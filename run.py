from app import create_app, db
from app.models import User, Course, Material, Assignment, Submission, DiscussionPost, Comment, Enrollment

app = create_app()

# Shell context for flask shell command
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Course': Course,
        'Material': Material,
        'Assignment': Assignment,
        'Submission': Submission,
        'DiscussionPost': DiscussionPost,
        'Comment': Comment,
        'Enrollment': Enrollment
    }

if __name__ == '__main__':
    app.run(debug=True)