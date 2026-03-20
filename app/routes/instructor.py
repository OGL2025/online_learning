from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Course, Enrollment, Material, Assignment, RecordedClass
from app.utils.decorators import instructor_required
# Note: We are removing the missing form imports for now, using request.form directly
import os
import uuid

instructor = Blueprint('instructor', __name__)

# Helper to check if instructor owns the course
def check_course_ownership(course_id):
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to manage this course.')
        return None
    return course

# -- Instructor Dashboard (Manage Enrollments) --
@instructor.route('/my-courses')
@login_required
@instructor_required
def my_courses():
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    return render_template('instructor/my_courses.html', courses=courses)

# -- Manage Enrollments (Accept/Reject) --
@instructor.route('/course/<int:course_id>/enrollments')
@login_required
@instructor_required
def manage_enrollments(course_id):
    course = check_course_ownership(course_id)
    if not course: return redirect(url_for('instructor.my_courses'))
    
    # Get pending and approved students
    pending = Enrollment.query.filter_by(course_id=course_id, status='pending').all()
    approved = Enrollment.query.filter_by(course_id=course_id, status='approved').all()
    
    return render_template('instructor/manage_enrollments.html', course=course, pending=pending, approved=approved)

@instructor.route('/enrollment/<int:enrollment_id>/approve')
@login_required
@instructor_required
def approve_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    course = check_course_ownership(enrollment.course_id)
    if not course: return redirect(url_for('instructor.my_courses'))
    
    enrollment.status = 'approved'
    db.session.commit()
    flash('Student approved.')
    return redirect(url_for('instructor.manage_enrollments', course_id=enrollment.course_id))

@instructor.route('/enrollment/<int:enrollment_id>/reject')
@login_required
@instructor_required
def reject_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    course = check_course_ownership(enrollment.course_id)
    if not course: return redirect(url_for('instructor.my_courses'))
    
    enrollment.status = 'rejected'
    # Or db.session.delete(enrollment) to remove record
    db.session.commit()
    flash('Student rejected.')
    return redirect(url_for('instructor.manage_enrollments', course_id=enrollment.course_id))

# -- Upload Material (Example) --
@instructor.route('/course/<int:course_id>/upload_material', methods=['GET', 'POST'])
@login_required
@instructor_required
def upload_material(course_id):
    course = check_course_ownership(course_id)
    if not course: return redirect(url_for('instructor.my_courses'))
    
    # Simplified logic using request.form instead of separate Form class
    if request.method == 'POST':
        title = request.form.get('title')
        file = request.files.get('file')
        if file and title:
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
            upload_path = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_path): os.makedirs(upload_path)
            file.save(os.path.join(upload_path, unique_filename))
            
            material = Material(title=title, file_url=f'/static/uploads/{unique_filename}', course_id=course.id)
            db.session.add(material)
            db.session.commit()
            flash('Material uploaded.')
            return redirect(url_for('main.view_course', course_id=course.id))
            
    return render_template('instructor/upload_material.html', course=course)