from app import db, login
from flask_login import UserMixin
from datetime import datetime

# -- User Model --
class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    submissions = db.relationship('Submission', backref='author', lazy='dynamic')
    posts = db.relationship('DiscussionPost', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __repr__(self):
        return f'<Student {self.student_id}>'

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

# -- Course Model --
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)    
    live_link = db.Column(db.String(500))
    recorded_link = db.Column(db.String(500))    
    
    year = db.Column(db.Integer, nullable=True)
    semester = db.Column(db.Integer, nullable=True)
    school_name = db.Column(db.String(100), nullable=True)
    credit_points = db.Column(db.Integer, nullable=True)
    instructor = db.Column(db.String(100), nullable=True)
    
    materials = db.relationship('Material', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    discussions = db.relationship('DiscussionPost', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    recordings = db.relationship('RecordedClass', backref='course', lazy='dynamic', cascade="all, delete-orphan")

# -- Material Model (Notes) --
class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20))
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# -- Assignment Model --
class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(500))
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic')

# -- Submission Model (Student Work) --
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_url = db.Column(db.String(500), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float)
    feedback = db.Column(db.Text)
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)

# -- Recorded Class Model --
class RecordedClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

# -- Discussion Forum Models --
class DiscussionPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ADDED: Topic column to link discussion to specific item (e.g., "Assignment 1")
    topic = db.Column(db.String(100), default='General Discussion')
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('discussion_post.id'), nullable=False)

# -- Flask-Login User Loader --
@login.user_loader
def load_user(id):
    return Student.query.get(int(id))