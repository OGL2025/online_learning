from app import db
from app.models import User
# 1. Create an Instructor
instructor = User(
    student_id='INS001', 
    name='Dr. Smith', 
    email='smith@unitech.ac.pg', 
    role='instructor'
)


instructor.set_password('password123')
# 2. Create an Admin
admin = User(
    student_id='ADM001', 
    name='Admin User', 
    email='admin@unitech.ac.pg', 
    role='admin'
)


admin.set_password('admin123')
# 3. Add to DB
db.session.add(instructor)
db.session.add(admin)
db.session.commit()
print("Instructor and Admin created successfully!")


exit()