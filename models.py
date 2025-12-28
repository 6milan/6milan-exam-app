# models.py (Add the missing methods to User class)

from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash  # <-- ADD THIS

db = SQLAlchemy()

# models.py - Recommended version for Supabase Auth

from datetime import datetime, timezone
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    supabase_uid = db.Column(db.String(255), unique=True, index=True, nullable=False)  # Required for linking
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    role = db.Column(db.String(50), default='student')
    approved = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.Text, nullable=True)  # nullable=True → use default image if None

    # NO password_hash column! Supabase handles passwords

    scores = db.relationship('Score', backref='user', lazy=True, cascade="all, delete-orphan")

    def get_id(self):
        return str(self.id)

    def set_email(self, email):
        self.email = email.lower().strip()

    @property
    def total_score(self):
        return sum(score.score for score in self.scores)

    @property
    def total_exams(self):
        return len(self.scores)

    @property
    def average_score(self):
        if self.total_exams == 0:
            return 0
        return round(self.total_score / self.total_exams, 1)

    def __repr__(self):
        return f'<User {self.username} ({self.email}) role={self.role} approved={self.approved}>'
        
class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    date = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        index=True
    )

    def __repr__(self):
        return f'<Score {self.score} in {self.category} on {self.date.strftime("%Y-%m-%d")}>'