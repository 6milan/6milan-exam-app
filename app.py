# app.py
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from models import db, User, Score
from forms import SignupForm, LoginForm, SelectCategoryForm
from questions import questions
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf import FlaskForm
from supabase import create_client, Client
from datetime import datetime, timezone
import uuid
import os

app = Flask(__name__)
app.config.from_object(Config)

# Supabase client (using service role key for server-side operations)
supabase: Client = create_client(
    app.config['SUPABASE_URL'],
    app.config['SUPABASE_SERVICE_ROLE_KEY']
)

# Supabase Storage bucket
SUPABASE_BUCKET = "6milan-exam-app"

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# Helper functions
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

# Supabase Storage upload function
def upload_to_supabase(file, user_id, role):
    if not file or file.filename == '':
        return None
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"{role}_{user_id}_{uuid.uuid4().hex}.{ext}"
    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=file.read(),
            file_options={"content-type": file.content_type or "image/jpeg", "upsert": True}
        )
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        return public_url
    except Exception as e:
        print(f"Supabase upload error: {e}")
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

# === SIGNUP (Traditional Password) ===
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))

    form = SignupForm()
    if form.validate_on_submit():
        try:
            # Create user in Supabase Auth with password
            response = supabase.auth.sign_up({
                "email": form.email.data,
                "password": form.password.data,
                "options": {
                    "data": {"username": form.username.data}
                }
            })

            if response.user:
                # Create local User record
                user = User(
                    username=form.username.data,
                    email=form.email.data.lower(),
                    role='student',
                    approved=False  # Waiting for admin approval
                )
                # Note: Password is stored in Supabase Auth, not locally
                db.session.add(user)
                db.session.commit()
                flash('Signup successful! Please wait for admin approval.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Signup failed. Please try again.', 'danger')
        except Exception as e:
            print(e)
            flash('Email already exists or invalid.', 'danger')

    return render_template('signup.html', form=form)

# === LOGIN (Traditional Password with Supabase Auth) ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if response.user:
                user = User.query.filter_by(email=email).first()
                if not user:
                    # Rare case: create local record if missing
                    user = User(
                        email=email,
                        username=email.split('@')[0],
                        role='student',
                        approved=True
                    )
                    db.session.add(user)
                    db.session.commit()

                if user.role == 'student' and not user.approved:
                    flash('Your account is pending admin approval.', 'warning')
                    return redirect(url_for('login'))

                login_user(user)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('profile' if user.role == 'student' else 'admin_dashboard'))
        except Exception as e:
            print(e)
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# === PROFILE, EXAM, ADMIN, LEADERBOARD (unchanged logic, minor cleanup) ===
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student':
        return redirect(url_for('admin_dashboard' if current_user.role == 'admin' else 'login'))

    form = SelectCategoryForm()
    upload_message = None
    if 'upload_pic' in request.files:
        file = request.files['upload_pic']
        if file.filename:
            new_url = upload_to_supabase(file, current_user.id, 'student')
            if new_url:
                current_user.profile_pic = new_url
                db.session.commit()
                upload_message = "Profile picture updated!"

    if form.validate_on_submit():
        return redirect(url_for('exam', category=form.category.data))

    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date).all()
    total_exams = len(scores)
    total_score = get_total_score(current_user.id)
    remark = get_performance_remark(total_score, total_exams)

    chart_data = {
        'labels': [s.date.strftime('%b %d, %Y') for s in scores],
        'scores': [s.score for s in scores]  # renamed for JS consistency
    }

    # Category averages
    category_scores = {}
    category_counts = {}
    for s in scores:
        cat = s.category
        category_scores[cat] = category_scores.get(cat, 0) + s.score
        category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_category_data = {
        cat: round(category_scores[cat] / category_counts[cat], 1)
        for cat in category_scores if category_counts[cat] > 0
    }

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

@app.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    upload_message = None
    if 'upload_pic' in request.files:
        file = request.files['upload_pic']
        if file.filename:
            new_url = upload_to_supabase(file, current_user.id, 'admin')
            if new_url:
                current_user.profile_pic = new_url
                db.session.commit()
                upload_message = "Profile picture updated!"

    return render_template('admin_profile.html', upload_message=upload_message)

@app.route('/exam/<category>', methods=['GET', 'POST'])
@login_required
def exam(category):
    if current_user.role != 'student' or category not in questions:
        flash('Invalid category or access denied.', 'danger')
        return redirect(url_for('profile'))

    q_list = questions[category]
    class ExamForm(FlaskForm):
        pass

    for i, (q, opts, _) in enumerate(q_list, 1):
        setattr(ExamForm, f'q{i}', RadioField(q, choices=opts, validators=[DataRequired()]))

    ExamForm.submit = SubmitField('Submit Exam')
    form = ExamForm()

    if form.validate_on_submit():
        score = 0
        for i, (_, _, ans) in enumerate(q_list, 1):
            if getattr(form, f'q{i}').data == ans:
                score += 1

        new_score = Score(user_id=current_user.id, category=category, score=score, date=datetime.now(timezone.utc))
        db.session.add(new_score)
        db.session.commit()
        flash(f'You scored {score}/{len(q_list)}!', 'success')
        return redirect(url_for('profile'))

    return render_template(
        'exam.html',
        form=form,
        category=category,
        num_questions=len(q_list),
        total_time_seconds=len(q_list) * 60
    )

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        user = User.query.get(user_id)
        if user and user.role == 'student':
            if action == 'approve':
                user.approved = True
                flash(f'{user.username} approved.', 'success')
            elif action == 'reject':
                db.session.delete(user)
                flash(f'{user.username} rejected.', 'info')
            db.session.commit()

    pending_users = User.query.filter_by(approved=False, role='student').all()
    approved_users = User.query.filter_by(approved=True, role='student').order_by(User.username).all()
    user_scores = {u.id: Score.query.filter_by(user_id=u.id).order_by(Score.date).all() for u in approved_users}

    # Category averages
    category_scores = {}
    category_counts = {}
    for scores in user_scores.values():
        for s in scores:
            cat = s.category
            category_scores[cat] = category_scores.get(cat, 0) + s.score
            category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_category_data = {
        cat: round(category_scores[cat] / category_counts[cat], 1)
        for cat in category_scores if category_counts[cat] > 0
    }

    all_scores = Score.query.join(User).filter(User.role == 'student', User.approved == True).order_by(Score.date).all()
    trend_data = {
        'labels': [s.date.strftime('%b %d') for s in all_scores],
        'data': [s.score for s in all_scores]
    }

    return render_template(
        'admin_dashboard.html',
        pending_users=pending_users,
        all_users=approved_users,
        user_scores=user_scores,
        avg_category_data=avg_category_data,
        trend_data=trend_data
    )

@app.route('/leaderboard')
def leaderboard():
    students = User.query.filter_by(role='student', approved=True).all()
    leaderboard_data = []

    for student in students:
        scores = Score.query.filter_by(user_id=student.id).all()
        if not scores:
            continue
        total_exams = len(scores)
        total_score = sum(s.score for s in scores)
        average = round(total_score / total_exams, 1)

        leaderboard_data.append({
            'username': student.username,
            'email': student.email,
            'profile_pic': student.profile_pic or '/static/images/default.jpg',
            'total_exams': total_exams,
            'total_score': total_score,
            'average': average
        })

    leaderboard_data.sort(key=lambda x: (-x['average'], -x['total_exams']))
    top_performers = leaderboard_data[:10]

    active_students = len(leaderboard_data)
    all_avg = round(sum(item['average'] for item in leaderboard_data) / len(leaderboard_data), 1) if leaderboard_data else 0

    return render_template(
        'leaderboard.html',
        top_performers=top_performers,
        total_students=active_students,
        all_avg=all_avg
    )

# === PASSWORD RESET (Local + Flask-Mail) ===
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        user = User.query.filter_by(email=email).first()
        if user:
            from flask_mail import Message
            from app import mail
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message("Password Reset - 6Milan Academy",
                          sender=("6Milan Academy", "admin@6milancoding.academy"),
                          recipients=[email])
            msg.body = f'''
Hello {user.username},

You requested a password reset for your 6Milan Academy account.

Click this link to reset your password (expires in 30 minutes):
{reset_url}

If you didn't request this, please ignore this email.

Best regards,
6Milan Coding Academy Team
'''
            try:
                mail.send(msg)
                flash('Password reset link sent! Check your email.', 'success')
            except Exception as e:
                print(e)
                flash('Failed to send email. Try again later.', 'danger')
        else:
            flash('If that email is registered, a reset link has been sent.', 'info')

        return redirect(url_for('login'))

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=1800)
    except:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('reset_password.html', token=token)

        user = User.query.filter_by(email=email).first()
        if user:
            # Update password in Supabase Auth
            try:
                supabase.auth.admin.update_user(
                    user_id=user.supabase_uid or supabase.auth.get_user()['user']['id'],
                    attributes={"password": password}
                )
            except:
                pass  # fallback to local if needed

            # Also update local hash if you store it
            user.set_password(password)
            db.session.commit()
            flash('Password reset successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    app.run(debug=True)