# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from models import db, User, Score
from forms import SignupForm, LoginForm, SelectCategoryForm
from questions import questions
from wtforms import RadioField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from supabase import create_client, Client
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import uuid
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta
import os

app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)

# For generating reset tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Supabase client initialization
supabase: Client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_SERVICE_ROLE_KEY'])

# Supabase Storage bucket
SUPABASE_BUCKET = "6mila-exam-app"

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
    if not file:
        return None

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"{role}_{user_id}_{uuid.uuid4().hex}.{ext}"

    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=filename,
            file=file,
            file_options={"content-type": file.content_type}
        )
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        return public_url
    except Exception as e:
        print(f"Supabase upload error: {e}")
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='student', approved=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful! Waiting for admin approval.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.role == 'student' and not user.approved:
                flash('Your account is pending admin approval.', 'warning')
                return redirect(url_for('login'))
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('profile'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    if current_user.role != 'student':
        flash('Access denied.', 'danger')
        return redirect(url_for('login'))

    form = SelectCategoryForm()
    upload_message = None

    if 'upload_pic' in request.files:
        file = request.files['upload_pic']
        new_url = upload_to_supabase(file, current_user.id, 'student')
        if new_url:
            current_user.profile_pic = new_url
            db.session.commit()
            upload_message = "Profile picture updated!"

    if form.validate_on_submit():
        return redirect(url_for('exam', category=form.category.data))

    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date).all()
    total_exams = len(scores)
    total_score = sum(s.score for s in scores)
    remark = get_performance_remark(total_score, total_exams)

    chart_data = {
        'labels': [s.date.strftime('%b %d, %Y') for s in scores],
        'data': [s.score for s in scores]
    }

    category_scores = {}
    category_counts = {}
    for score in scores:
        cat = score.category
        category_scores[cat] = category_scores.get(cat, 0) + score.score
        category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_category_data = {
        cat: round(category_scores[cat] / category_counts[cat], 1) if category_counts[cat] > 0 else 0
        for cat in category_scores
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
        flash('Access denied.')
        return redirect(url_for('admin_dashboard'))

    upload_message = None

    if 'upload_pic' in request.files:
        file = request.files['upload_pic']
        new_url = upload_to_supabase(file, current_user.id, 'admin')
        if new_url:
            current_user.profile_pic = new_url
            db.session.commit()
            upload_message = "Admin profile picture updated!"

    return render_template('admin_profile.html', upload_message=upload_message)

@app.route('/exam/<category>', methods=['GET', 'POST'])
@login_required
def exam(category):
    if current_user.role != 'student' or not questions.get(category):
        flash('Invalid category or access denied.')
        return redirect(url_for('profile'))

    q_list = questions[category]
    num_questions = len(q_list)
    time_per_question = 60  # 1 minute per question
    total_time_seconds = num_questions * time_per_question

    class ExamForm(FlaskForm):
        pass

    for i, (q, opts, _) in enumerate(q_list, 1):
        setattr(ExamForm, f'q{i}', RadioField(q, choices=opts, validators=[DataRequired()]))

    ExamForm.submit = SubmitField('Submit Exam')

    form = ExamForm()
    if form.validate_on_submit():
        score = 0
        for i, (_, _, ans) in enumerate(q_list, 1):
            if form.data[f'q{i}'] == ans:
                score += 1
        new_score = Score(user_id=current_user.id, category=category, score=score)
        db.session.add(new_score)
        db.session.commit()
        flash(f'You scored {score}/{len(q_list)}!', 'success')
        return redirect(url_for('profile'))

    return render_template(
        'exam.html',
        form=form,
        category=category,
        num_questions=num_questions,
        total_time_seconds=total_time_seconds
    )

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('profile'))

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
    all_users = User.query.filter_by(role='student', approved=True).order_by(User.username).all()

    user_scores = {}
    for u in all_users:
        user_scores[u.id] = Score.query.filter_by(user_id=u.id).order_by(Score.date).all()

    # Admin charts
    category_scores = {}
    category_counts = {}
    for u in all_users:
        for score in user_scores.get(u.id, []):
            cat = score.category
            category_scores[cat] = category_scores.get(cat, 0) + score.score
            category_counts[cat] = category_counts.get(cat, 0) + 1

    avg_category_data = {
        cat: round(category_scores[cat] / category_counts[cat], 1) if category_counts[cat] > 0 else 0
        for cat in category_scores
    }

    all_scores = Score.query.join(User).filter(User.role == 'student', User.approved == True)\
                    .order_by(Score.date).all()
    trend_data = {
        'labels': [s.date.strftime('%b %d') for s in all_scores],
        'data': [s.score for s in all_scores]
    }

    return render_template(
        'admin_dashboard.html',
        pending_users=pending_users,
        all_users=all_users,
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
            'profile_pic': student.profile_pic or 'default.jpg',
            'total_exams': total_exams,
            'total_score': total_score,
            'average': average
        })
    
    leaderboard_data.sort(key=lambda x: (-x['average'], -x['total_exams']))
    top_performers = leaderboard_data[:10]
    
    total_students = len([s for s in students if Score.query.filter_by(user_id=s.id).first()])
    all_avg = round(sum(p['average'] for p in leaderboard_data) / len(leaderboard_data), 1) if leaderboard_data else 0

    return render_template(
        'leaderboard.html',
        top_performers=top_performers,
        total_students=total_students,
        all_avg=all_avg
    )

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('profile' if current_user.role == 'student' else 'admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate token valid for 30 minutes
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)

            msg = Message("Password Reset Request - 6Milan Academy",
                          recipients=[email])
            msg.body = f'''
Hello {user.username},

You requested a password reset.

Click the link below to reset your password (valid for 30 minutes):

{reset_url}

If you didn't request this, ignore this email.

Best regards,
6Milan Coding Academy Team
'''
            try:
                mail.send(msg)
                flash('Password reset link sent to your email!', 'success')
            except Exception as e:
                flash('Failed to send email. Contact admin.', 'danger')
        else:
            flash('If the email exists, a reset link has been sent.', 'info')
        return redirect(url_for('login'))

    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=1800)  # 30 minutes
    except:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)

        user = User.query.filter_by(email=email).first()
        user.set_password(password)
        db.session.commit()
        flash('Your password has been reset! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    app.run(debug=True)