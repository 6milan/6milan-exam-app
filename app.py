# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from config import Config
from models import db, User, Score
from forms import SignupForm, LoginForm, SelectCategoryForm
from questions import questions
from wtforms import RadioField
from flask_wtf import FlaskForm
from datetime import datetime, timezone
from wtforms import RadioField, SubmitField  # ← Added SubmitField
from wtforms.validators import DataRequired   # ← Added DataRequired
from  werkzeug.utils import secure_filename
import os

app = Flask(__name__)
# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create DB tables if not exist (run once locally)
with app.app_context():
    db.create_all()

# To create admin user locally: Run in Python shell
# from app import app, db
# from models import User
# with app.app_context():
#     admin = User(username='admin', email='admin@example.com', role='admin', approved=True)
#     admin.set_password('adminpass')
#     db.session.add(admin)
#     db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='student', approved=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful! Waiting for admin approval.')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.role == 'student' and not user.approved:
                flash('Your account is pending approval.')
                return redirect(url_for('login'))
            login_user(user)
            return redirect(url_for('profile'))
        flash('Invalid email or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student' and current_user.role != 'admin':
        return redirect(url_for('admin_dashboard'))

    form = SelectCategoryForm()
    upload_message = None

    if 'upload_pic' in request.files:
        file = request.files['upload_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add user ID to avoid conflicts
            filename = f"{current_user.id}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_pic = filename
            db.session.commit()
            upload_message = "Profile picture updated!"

    if form.validate_on_submit():
        return redirect(url_for('exam', category=form.category.data))

    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.date).all()
    chart_data = {
        'labels': [s.date.strftime('%b %d, %Y') for s in scores],
        'data': [s.score for s in scores]
    }

    return render_template('profile.html', form=form, chart_data=chart_data, upload_message=upload_message)

@app.route('/admin_profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('admin_dashboard'))

    upload_message = None

    if 'upload_pic' in request.files:
        file = request.files['upload_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Prefix with 'admin_' to separate from student uploads
            filename = f"admin_{current_user.id}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.profile_pic = filename
            db.session.commit()
            upload_message = "Admin profile picture updated successfully!"

    return render_template('admin_profile.html', upload_message=upload_message)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/exam/<category>', methods=['GET', 'POST'])
@login_required
def exam(category):
    if current_user.role != 'student' or not questions.get(category):
        flash('Invalid category or access denied.')
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
            if form.data[f'q{i}'] == ans:
                score += 1
        new_score = Score(user_id=current_user.id, category=category, score=score)
        db.session.add(new_score)
        db.session.commit()
        flash(f'You scored {score}/{len(q_list)}!')
        return redirect(url_for('profile'))
    
    return render_template('exam.html', form=form, category=category)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('profile'))
    
    # Handle approvals
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        user = User.query.get(user_id)
        if user and user.role == 'student':
            if action == 'approve':
                user.approved = True
                flash(f'{user.username} has been approved.')
            elif action == 'reject':
                db.session.delete(user)
                flash(f'{user.username} has been rejected and removed.')
            db.session.commit()
    
    pending_users = User.query.filter_by(approved=False, role='student').all()
    all_users = User.query.filter_by(role='student', approved=True).order_by(User.username).all()
    
    user_scores = {}
    for u in all_users:
        user_scores[u.id] = Score.query.filter_by(user_id=u.id).order_by(Score.date).all()
        date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    return render_template(
        'admin_dashboard.html',
        pending_users=pending_users,
        all_users=all_users,           # ← Required for template
        user_scores=user_scores
    )
    
if __name__ == '__main__':
    app.run(debug=True)