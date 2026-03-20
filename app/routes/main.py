from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.forms import SubmissionForm, DiscussionForm, CommentForm
from app.models import Course, Assignment, Submission, DiscussionPost, Comment, Material, RecordedClass, Enrollment, User
from app import db
from app.utils.decorators import enrolled_required
import os
import uuid
from datetime import datetime

main = Blueprint('main', __name__)

def save_file(file):
    if file:
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
        upload_path = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        filepath = os.path.join(upload_path, unique_filename)
        file.save(filepath)
        return f'/static/uploads/{unique_filename}'
    return None

# -- Home (Redirect) --
@main.route('/')
@main.route('/index')
def index():
    # If user is already logged in, send them to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Otherwise show the public landing page
    return render_template('index.html')

@main.route('/legal')
def legal():
    return render_template('legal.html', title='Legal & Privacy')

# -- Dashboard (Student) --
@main.route('/dashboard')
@login_required
def dashboard():
    # Logic: If Student, show only their enrolled courses.
    # If Instructor, show courses they teach.
    
    if current_user.role == 'instructor':
        courses = Course.query.filter_by(instructor_id=current_user.id).all()
        return render_template('dashboard/home.html', courses=courses, role='instructor')
    
    # For Students: Show courses they are APPROVED in
    approved_enrollments = Enrollment.query.filter_by(student_id=current_user.id, status='approved').all()
    courses = [e.course for e in approved_enrollments]
    
    return render_template('dashboard/home.html', courses=courses, role='student')

# -- Course Catalog (For Students to Apply) --
@main.route('/courses')
@login_required
def course_catalog():
    if current_user.role != 'student':
        flash('Only students can browse the catalog.')
        return redirect(url_for('main.dashboard'))

    all_courses = Course.query.all()
    # Get list of courses student has already applied to
    applied_ids = [e.course_id for e in Enrollment.query.filter_by(student_id=current_user.id).all()]
    
    return render_template('dashboard/course_catalog.html', courses=all_courses, applied_ids=applied_ids)

# -- Apply for Course --
@main.route('/course/<int:course_id>/apply')
@login_required
def apply_course(course_id):
    if current_user.role != 'student':
        flash('Only students can apply.')
        return redirect(url_for('main.dashboard'))

    # Check if already applied
    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if existing:
        flash('You have already applied or are enrolled.')
        return redirect(url_for('main.course_catalog'))

    enrollment = Enrollment(student_id=current_user.id, course_id=course_id, status='pending')
    db.session.add(enrollment)
    db.session.commit()
    flash('Application submitted. Awaiting instructor approval.')
    return redirect(url_for('main.dashboard'))

# -- View Course Details (Protected by Enrollment) --
@main.route('/course/<int:course_id>')
@login_required
@enrolled_required # Uses decorator to check approval
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    materials = course.materials.order_by(Material.uploaded_at.desc()).all()
    assignments = course.assignments.all()
    recordings = RecordedClass.query.filter_by(course_id=course.id).order_by(RecordedClass.id.desc()).all()
    return render_template('dashboard/course_detail.html', course=course, materials=materials, assignments=assignments, recordings=recordings)

# -- Download Notes --
@main.route('/material/<int:material_id>')
@login_required
def download_material(material_id):
    material = Material.query.get_or_404(material_id)
    return redirect(material.file_url)

# -- Submit Assignment --
@main.route('/assignment/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    # Check Enrollment manually for submission (extra security)
    if current_user.role == 'student':
        is_enrolled = Enrollment.query.filter_by(student_id=current_user.id, course_id=assignment.course_id, status='approved').first()
        if not is_enrolled:
            flash('Must be enrolled to submit.')
            return redirect(url_for('main.dashboard'))

    form = SubmissionForm()
    
    if form.validate_on_submit():
        file_url = save_file(form.file.data)
        if file_url:
            existing_submission = Submission.query.filter_by(
                student_id=current_user.id, 
                assignment_id=assignment.id
            ).first()

            if existing_submission:
                existing_submission.file_url = file_url
                existing_submission.submitted_at = datetime.utcnow()
                flash('Assignment updated successfully!')
            else:
                submission = Submission(
                    file_url=file_url,
                    student_id=current_user.id,
                    assignment_id=assignment.id
                )
                db.session.add(submission)
                flash('Assignment submitted successfully!')
            
            db.session.commit()
            return redirect(url_for('main.view_course', course_id=assignment.course_id))
        else:
            flash('Error uploading file.')
            
    return render_template('dashboard/submit_assignment.html', form=form, assignment=assignment)

# -- Discussion Forum (List) --
@main.route('/course/<int:course_id>/discussions')
@login_required
@enrolled_required
def discussions(course_id):
    course = Course.query.get_or_404(course_id)    
    topic = request.args.get('topic', 'General Discussion')
    posts = DiscussionPost.query.filter_by(course_id=course.id, topic=topic).order_by(DiscussionPost.created_at.desc()).all()
    return render_template('dashboard/discussions.html', course=course, posts=posts, topic=topic)

# -- Create Discussion Post --
@main.route('/course/<int:course_id>/discussions/new', methods=['GET', 'POST'])
@login_required
@enrolled_required
def create_discussion(course_id):
    course = Course.query.get_or_404(course_id)
    topic = request.args.get('topic', 'General Discussion')
    
    form = DiscussionForm()
    if form.validate_on_submit():
        post = DiscussionPost(
            title=form.title.data,
            content=form.content.data,
            student_id=current_user.id,
            course_id=course.id,
            topic=topic
        )
        db.session.add(post)
        db.session.commit()
        flash('Discussion posted.')
        return redirect(url_for('main.discussions', course_id=course.id, topic=topic))
        
    return render_template('dashboard/create_discussion.html', form=form, course=course, topic=topic)

# -- View Single Discussion & Comments --
@main.route('/discussion/<int:post_id>', methods=['GET', 'POST'])
@login_required
def view_discussion(post_id):
    post = DiscussionPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            student_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.')
        return redirect(url_for('main.view_discussion', post_id=post.id))
    
    comments = post.comments.order_by(Comment.created_at.asc()).all()
    return render_template('dashboard/view_discussion.html', post=post, form=form, comments=comments)