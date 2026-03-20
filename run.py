from app import create_app, db
from app.models import User, Course, Material, Assignment, Submission, DiscussionPost, Comment, Enrollment # Updated

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, # Changed from Student
        'Course': Course,
        'Material': Material,
        'Assignment': Assignment,
        'Submission': Submission,
        'DiscussionPost': DiscussionPost,
        'Comment': Comment,
        'Enrollment': Enrollment # New
    }

if __name__ == '__main__':
    app.run(debug=True)