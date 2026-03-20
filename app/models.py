from app import db, login
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# -- User Model (Replaces Student for Scalability) --
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False) # Kept for backward compatibility
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # FIXED: Role Based Access
    role = db.Column(db.String(20), default='student') # Options: 'student', 'instructor', 'admin'
    
    # Relationships
    submissions = db.relationship('Submission', backref='author', lazy='dynamic')
    posts = db.relationship('DiscussionPost', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    courses_taught = db.relationship('Course', backref='instructor_user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.student_id}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# -- Enrollment Model (Handles Application/Approval) --
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Status: 'pending' (Applied), 'approved' (Registered), 'rejected'
    status = db.Column(db.String(20), default='pending') 
    
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a student can only enroll once per course
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id'),)

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
    
    # FIXED: Link course to an Instructor (User)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Note: 'instructor' string column in old model is replaced by relationship above
    
    materials = db.relationship('Material', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    discussions = db.relationship('DiscussionPost', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    recordings = db.relationship('RecordedClass', backref='course', lazy='dynamic', cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade="all, delete-orphan")

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
    
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('student_id', 'assignment_id'),)

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
    topic = db.Column(db.String(100), default='General Discussion')
    
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('discussion_post.id'), nullable=False)

# -- Flask-Login User Loader --
@login.user_loader
def load_user(id):
    return User.query.get(int(id))