# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from models import db, User, Score
from forms import SignupForm, LoginForm, SelectCategoryForm
from questions import questions
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from supabase import create_client, Client
from datetime import datetime, timezone
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object(Config)

# ---------------------- Helper functions ---------------------- #

def get_total_score(user_id):
    scores = Score.query.filter_by(user_id=user_id).all()
    return sum(s.score for s in scores) if scores else 0

def get_performance_remark(total_score, total_exams):
    if total_exams == 0:
        return "No exams taken yet"
    average = total_score / total_exams
    if average >= 18:
        return "Outstanding! 🌟"
    elif average >= 16:
        return "Excellent! 👍"
    elif average >= 12:
        return "Very Good"
    elif average >= 8:
        return "Good"
    else:
        return "Keep Practicing! 💪"

# Supabase client
supabase: Client = create_client(
    app.config['SUPABASE_URL'],
    app.config['SUPABASE_SERVICE_ROLE_KEY']
)
SUPABASE_BUCKET = "6milan-exam-app"
SUPABASE_STORAGE_BASE_URL = f"{app.config['SUPABASE_URL'].rstrip('/')}/storage/v1/object/public/{SUPABASE_BUCKET}/"

def upload_to_supabase(file, user_supabase_uid):
    """Uploads a profile picture and returns public URL or None."""
    if not file or not file.filename.strip():
        return None

    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if '.' not in file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return None

    path = f"{user_supabase_uid}/profile.{ext}"
    try:
        file.stream.seek(0)
        file_bytes = file.stream.read()
        if not file_bytes:
            return None

        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": file.mimetype or f"image/{ext}", "upsert": True}
        )
        return f"{SUPABASE_STORAGE_BASE_URL}{path}"
    except Exception as e:
        print(f"Supabase upload error: {e}")
        return None

def handle_profile_upload():
    """Helper for profile picture upload and DB update."""
    upload_message = None
    if 'upload_pic' in request.files:
        file = request.files['upload_pic']
        new_url = upload_to_supabase(file, current_user.supabase_uid)
        if new_url:
            current_user.profile_pic = new_url
            db.session.commit()
            upload_message = "Profile picture updated successfully!"
        else:
            upload_message = "Upload failed. Please select a valid image file (JPG, PNG, GIF, WebP)."
    return upload_message

def get_resized_profile_url(profile_pic_url, width=None, height=None, quality=80):
    if not profile_pic_url:
        return None
    params = [f"width={width}" if width else "",
              f"height={height}" if height else "",
              f"quality={quality}",
              "resize=cover"]
    transform_str = "&".join(p for p in params if p)
    return f"{profile_pic_url}?{transform_str}"

@app.context_processor
def utility_processor():
    return dict(get_resized_profile_url=get_resized_profile_url)

# ---------------------- Flask setup ---------------------- #
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# ---------------------- Routes ---------------------- #

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        username = form.username.data.strip()
        password = form.password.data

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"username": username}}
            })
            if response.user:
                supabase_uid = response.user.id
                if User.query.filter_by(supabase_uid=supabase_uid).first():
                    flash('You have already signed up. Please log in.', 'info')
                    return redirect(url_for('login'))

                new_user = User(
                    supabase_uid=supabase_uid,
                    username=username,
                    email=email,
                    role='student',
                    approved=False,
                    profile_pic=None
                )
                db.session.add(new_user)
                db.session.commit()
                flash('Signup successful! Your account is pending admin approval.', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            print("Signup error:", e)
            flash('Signup failed. Please try again.', 'danger')

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data

        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if not response.user:
                flash('Invalid email or password.', 'danger')
                return render_template('login.html', form=form)

            supabase_uid = response.user.id
            user = User.query.filter_by(supabase_uid=supabase_uid).first()
            if not user:
                # If user doesn't exist locally, create with pending approval
                user = User(
                    supabase_uid=supabase_uid,
                    email=email,
                    username=email.split('@')[0],
                    role='student',
                    approved=False,
                    profile_pic=None
                )
                db.session.add(user)
                db.session.commit()
                flash('Account created! Please wait for admin approval.', 'info')

            if user.role == 'student' and not user.approved:
                supabase.auth.sign_out()
                flash('Your account is pending admin approval.', 'warning')
                return render_template('login.html', form=form)

            login_user(user)
            session['supabase_access_token'] = response.session.access_token
            session['supabase_refresh_token'] = response.session.refresh_token
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile' if user.role == 'student' else 'admin_dashboard'))
        except Exception as e:
            print("Login error:", e)
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ---------------------- Student Profile ---------------------- #
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student':
        return redirect(url_for('admin_dashboard' if current_user.role == 'admin' else 'login'))

    upload_message = handle_profile_upload()
    form = SelectCategoryForm()
    if form.validate_on_submit():
        return redirect(url_for('exam', category=form.category.data))

    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date).all()
    total_exams = len(scores)
    total_score = get_total_score(current_user.id)
    remark = get_performance_remark(total_score, total_exams)

    chart_data = {
        'labels': [s.date.strftime('%b %d, %Y') for s in scores],
        'scores': [s.score for s in scores]
    }

    category_scores = {}
    category_counts = {}
    for s in scores:
        cat = s.category
        category_scores[cat] = category_scores.get(cat, 0) + s.score
        category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_category_data = {cat: round(category_scores[cat] / category_counts[cat], 1)
                         for cat in category_scores if category_counts[cat] > 0}

    return render_template(
        'profile.html',
        form=form,
        chart_data=chart_data,
        upload_message=upload_message,
        total_score=total_score,
        total_exams=total_exams,
        remark=remark,
        avg_category_data=avg_category_data
    )

# ---------------------- Student Profile Update ---------------------- #
@app.route('/student_profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    upload_message = handle_profile_upload()

    if request.method == "POST" and 'update_profile' in request.form:
        new_username = request.form.get("username", "").strip()
        new_email = request.form.get("email", "").strip().lower()
        if new_username:
            current_user.username = new_username
        if new_email:
            current_user.email = new_email
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("student_profile"))

    return render_template("student_profile.html", upload_message=upload_message)

# ---------------------- Admin Profile ---------------------- #
@app.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))
    upload_message = handle_profile_upload()
    return render_template('admin_profile.html', upload_message=upload_message)

# ---------------------- Exam Route ---------------------- #
@app.route('/exam/<category>', methods=['GET', 'POST'])
@login_required
def exam(category):
    if current_user.role != 'student' or category not in questions:
        flash('Invalid category or access denied.', 'danger')
        return redirect(url_for('profile'))

    q_list = questions[category]
    fields = {f'q{i+1}': RadioField(q, choices=opts, validators=[DataRequired()]) 
              for i, (q, opts, _) in enumerate(q_list)}
    ExamForm = type('ExamForm', (FlaskForm,), {**fields, 'submit': SubmitField('Submit Exam')})
    form = ExamForm()

    if form.validate_on_submit():
        score = sum(getattr(form, f'q{i+1}').data == ans for i, (_, _, ans) in enumerate(q_list))
        db.session.add(Score(user_id=current_user.id, category=category, score=score,
                             date=datetime.now(timezone.utc)))
        db.session.commit()
        flash(f'You scored {score}/{len(q_list)}!', 'success')
        return redirect(url_for('profile'))

    return render_template('exam.html', form=form, category=category,
                           num_questions=len(q_list), total_time_seconds=len(q_list) * 60)

# ---------------------- Admin Dashboard ---------------------- #
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied: Admin privileges required.', 'danger')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        if user_id and action:
            try:
                user_id = int(user_id)
                user = User.query.get(user_id)
                if user and user.role == 'student':
                    if action == 'approve':
                        user.approved = True
                        db.session.commit()
                        flash(f'{user.username} has been approved.', 'success')
                    elif action == 'reject':
                        Score.query.filter_by(user_id=user.id).delete()
                        db.session.delete(user)
                        db.session.commit()
                        flash(f'{user.username} has been rejected and removed.', 'info')
            except Exception as e:
                print("Admin action error:", e)
                flash('Invalid action.', 'danger')

    pending_users = User.query.filter_by(approved=False, role='student').order_by(User.username).all()
    approved_users = User.query.filter_by(approved=True, role='student').order_by(User.username).all()

    approved_user_ids = [u.id for u in approved_users]
    all_scores = Score.query.filter(Score.user_id.in_(approved_user_ids)).order_by(Score.date).all() if approved_user_ids else []

    user_scores = {}
    for score in all_scores:
        user_scores.setdefault(score.user_id, []).append(score)

    category_scores, category_counts = {}, {}
    for score in all_scores:
        cat = score.category
        category_scores[cat] = category_scores.get(cat, 0) + score.score
        category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_category_data = {cat: round(category_scores[cat]/category_counts[cat], 1)
                         for cat in category_scores if category_counts[cat] > 0}

    trend_data = {'labels': [s.date.strftime('%b %d') for s in all_scores],
                  'data': [s.score for s in all_scores]} if all_scores else {'labels': [], 'data': []}

    return render_template('admin_dashboard.html',
                           pending_users=pending_users,
                           approved_users=approved_users,
                           user_scores=user_scores,
                           avg_category_data=avg_category_data,
                           trend_data=trend_data)

# ---------------------- Leaderboard ---------------------- #
@app.route('/leaderboard')
def leaderboard():
    sort = request.args.get('sort', 'average_desc')
    students_with_scores = (
        db.session.query(User.id, User.username, User.email, User.profile_pic)
        .outerjoin(Score, User.id == Score.user_id)
        .filter(User.role == 'student', User.approved == True)
        .group_by(User.id)
        .having(func.count(Score.id) > 0)
        .all()
    )

    current_date = datetime.now().strftime("%B %d, %Y")
    if not students_with_scores:
        return render_template('leaderboard.html', top_performers=[], total_students=0,
                               all_avg=0, current_date=current_date, current_sort=sort)

    student_ids = [s.id for s in students_with_scores]
    all_scores = Score.query.filter(Score.user_id.in_(student_ids)).order_by(Score.user_id, Score.date).all()

    leaderboard_data, student_scores = [], {sid: [] for sid in student_ids}
    for score in all_scores:
        student_scores[score.user_id].append(score)

    for student in students_with_scores:
        scores = student_scores[student.id]
        total_exams = len(scores)
        total_score = sum(s.score for s in scores)
        average = round(total_score / total_exams, 1) if total_exams else 0
        leaderboard_data.append({'id': student.id, 'username': student.username, 'email': student.email,
                                 'profile_pic': student.profile_pic, 'total_exams': total_exams,
                                 'total_score': total_score, 'average': average})

    sort_keys = {
        'average_desc': lambda x: (-x['average'], -x['total_exams']),
        'average_asc': lambda x: (x['average'], -x['total_exams']),
        'exams_desc': lambda x: (-x['total_exams'], -x['average']),
        'score_desc': lambda x: (-x['total_score'], -x['average'])
    }
    leaderboard_data.sort(key=sort_keys.get(sort, sort_keys['average_desc']))
    for i, item in enumerate(leaderboard_data, 1):
        item['rank'] = i

    top_performers = leaderboard_data[:10]
    total_students = len(leaderboard_data)
    all_avg = round(sum(x['average'] for x in leaderboard_data) / total_students, 1) if total_students else 0

    return render_template('leaderboard.html', top_performers=top_performers,
                           total_students=total_students, all_avg=all_avg,
                           current_user=current_user, current_date=current_date,
                           current_sort=sort)

# ---------------------- Run ---------------------- #
if __name__ == '__main__':
    app.run(debug=True)
