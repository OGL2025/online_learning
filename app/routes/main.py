from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.forms import SubmissionForm, DiscussionForm, CommentForm
from app.models import Course, Assignment, Submission, DiscussionPost, Comment, Material, RecordedClass
from app import db
import os

main = Blueprint('main', __name__)

# -- Helper Function for File Upload --
def save_file(file):
    if file:
        filename = secure_filename(file.filename)
        upload_path = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        return f'/static/uploads/{filename}'
    return None

# -- Home --
@main.route('/')
@main.route('/index')
def index():
    return redirect(url_for('auth.login'))

# -- Dashboard --
@main.route('/dashboard')
@login_required
def dashboard():
    courses = Course.query.order_by(Course.year.asc(), Course.semester.asc()).all()
    return render_template('dashboard/home.html', courses=courses)

# -- View Course Details --
@main.route('/course/<int:course_id>')
@login_required
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
    form = SubmissionForm()
    
    if form.validate_on_submit():
        file_url = save_file(form.file.data)
        if file_url:
            submission = Submission(
                file_url=file_url,
                student_id=current_user.id,
                assignment_id=assignment.id
            )
            db.session.add(submission)
            db.session.commit()
            flash('Assignment submitted successfully!')
            return redirect(url_for('main.view_course', course_id=assignment.course_id))
        else:
            flash('Error uploading file.')
            
    return render_template('dashboard/submit_assignment.html', form=form, assignment=assignment)

# -- Discussion Forum (List) --
@main.route('/course/<int:course_id>/discussions')
@login_required
def discussions(course_id):
    course = Course.query.get_or_404(course_id)    
    topic = request.args.get('topic', 'General Discussion')
    
    # UPDATED: Filter posts by BOTH course_id AND topic
    posts = DiscussionPost.query.filter_by(course_id=course.id, topic=topic).order_by(DiscussionPost.created_at.desc()).all()
    
    return render_template('dashboard/discussions.html', course=course, posts=posts, topic=topic)

# -- Create Discussion Post --
@main.route('/course/<int:course_id>/discussions/new', methods=['GET', 'POST'])
@login_required
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
            topic=topic  # UPDATED: Save the topic
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