from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from app.models import Enrollment

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def instructor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'instructor':
            flash('Instructor access required.')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def enrolled_required(f):
    """
    Checks if student is enrolled in the course (status='approved').
    Assumes the route has a 'course_id' argument.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        course_id = kwargs.get('course_id')
        if not course_id:
            abort(400) # Bad request
            
        # Check if user is admin or instructor of the course (bypass enrollment check)
        if current_user.role in ['admin', 'instructor']:
            return f(*args, **kwargs)

        # Check enrollment
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id, 
            course_id=course_id, 
            status='approved'
        ).first()
        
        if not enrollment:
            flash('You are not enrolled in this course.')
            return redirect(url_for('main.dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function