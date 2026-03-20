import os
from app import create_app, db
from app.models import User, Course, Enrollment, Assignment, Submission, Material, RecordedClass, DiscussionPost, Comment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()

# Use the app context
with app.app_context():
    print("Clearing existing data...")
    # Clear tables in reverse dependency order to avoid foreign key constraints
    Submission.query.delete()
    Comment.query.delete()
    DiscussionPost.query.delete()
    Material.query.delete()
    RecordedClass.query.delete()
    Assignment.query.delete()
    Enrollment.query.delete()
    Course.query.delete()
    User.query.filter(User.role != 'admin').delete() # Keep existing admins, clear others
    
    db.session.commit()
    print("Data cleared.")

    # -----------------------------------
    # 1. CREATE USERS
    # -----------------------------------
    print("Creating Users...")
    
    # 2 Instructors
    instructors = []
    for i in range(1, 3):
        inst = User(
            student_id=f'INS00{i}',
            name=f'Dr. Instructor {i}',
            email=f'instructor{i}@unitech.ac.pg',
            role='instructor'
        )
        inst.set_password('password')
        instructors.append(inst)
        db.session.add(inst)

    # 5 Students
    students = []
    for i in range(1, 6):
        std = User(
            student_id=f'STU2024{i:03d}',
            name=f'Student Name {i}',
            email=f'student{i}@unitech.ac.pg',
            role='student'
        )
        std.set_password('password')
        students.append(std)
        db.session.add(std)
    
    db.session.commit()
    print(f"Created {len(instructors)} instructors and {len(students)} students.")

    # -----------------------------------
    # 2. CREATE COURSES (4 per semester, 2 years)
    # -----------------------------------
    print("Creating Courses...")
    
    courses = []
    course_code_counter = 100
    
    # Loop for Year 1 and Year 2
    for year in [1, 2]:
        # Loop for Semester 1 and 2
        for sem in [1, 2]:
            # Create 4 courses per semester
            for c in range(1, 5):
                code = f'CS{course_code_counter + c}'
                title = f'{["Intro to Programming", "Data Structures", "Calculus", "Physics", "Algorithms", "Databases", "Networking", "AI"][random.randint(0,7)]} (Y{year}S{sem})'
                
                course = Course(
                    code=code,
                    title=title,
                    description=f'Description for {title}. This is a core unit for Year {year}.',
                    year=year,
                    semester=sem,
                    credit_points=10,
                    school_name='School of Computing',
                    instructor_id=random.choice(instructors).id, # Assign random instructor
                    live_link='https://meet.google.com/demo'
                )
                courses.append(course)
                db.session.add(course)
            
            course_code_counter += 10
    
    db.session.commit()
    print(f"Created {len(courses)} courses.")

    # -----------------------------------
    # 3. ENROLLMENTS & COURSE CONTENT
    # -----------------------------------
    print("Creating Enrollments and Content...")
    
    # List to store assignments for later submission creation
    all_assignments = []

    for course in courses:
        # A. Enroll ALL 5 students in EVERY course (Status: Approved)
        for std in students:
            enrollment = Enrollment(
                student_id=std.id,
                course_id=course.id,
                status='approved'
            )
            db.session.add(enrollment)
        
        # B. Create Materials (Notes) - 2 per course
        for m in range(1, 3):
            mat = Material(
                title=f'Lecture Note {m} for {course.code}',
                file_url=f'/static/uploads/sample_note_{m}.pdf',
                course_id=course.id
            )
            db.session.add(mat)

        # C. Create Recorded Classes - 2 per course
        for r in range(1, 3):
            rec = RecordedClass(
                title=f'Week {r} Recording',
                video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', # Placeholder
                course_id=course.id
            )
            db.session.add(rec)

        # D. Create Assignments (1 to 3 per course)
        num_assignments = random.randint(1, 3)
        for a in range(1, num_assignments + 1):
            assign = Assignment(
                title=f'Assignment {a}',
                description=f'Please solve the problems in the attached PDF for {course.title}.',
                file_url=f'/static/uploads/assignment_{a}.pdf',
                due_date=datetime.utcnow() + timedelta(days=random.randint(7, 30)),
                course_id=course.id
            )
            db.session.add(assign)
            all_assignments.append(assign)
    
    db.session.commit()
    print("Enrollments and Content created.")

    # -----------------------------------
    # 4. SUBMISSIONS (Students submitting work)
    # -----------------------------------
    print("Creating Submissions...")
    
    # Let's have students submit to the first assignment of each course
    for assign in all_assignments:
        # Random students submit (not all students submit every assignment)
        submitting_students = random.sample(students, k=random.randint(2, len(students)))
        
        for std in submitting_students:
            sub = Submission(
                file_url=f'/static/uploads/sub_{std.student_id}_{assign.id}.pdf',
                student_id=std.id,
                assignment_id=assign.id,
                grade=random.uniform(50, 100) if random.random() > 0.3 else None # 70% chance graded
            )
            db.session.add(sub)

    # -----------------------------------
    # 5. DISCUSSIONS & COMMENTS
    # -----------------------------------
    print("Creating Discussions...")
    
    for course in courses:
        # Create 1 discussion post per course
        post = DiscussionPost(
            title=f'Help with {course.title}',
            content='Can someone explain the concept discussed in the last lecture?',
            student_id=random.choice(students).id,
            course_id=course.id,
            topic='General Discussion'
        )
        db.session.add(post)
        db.session.flush() # Get ID
        
        # Add 2 comments to the post
        for c in range(2):
            comment = Comment(
                content='I think the professor explained it well in the recording.',
                student_id=random.choice(students).id,
                post_id=post.id
            )
            db.session.add(comment)

    db.session.commit()
    print("\n=== DATABASE POPULATION COMPLETE ===")
    print("Summary:")
    print(f"- Instructors: 2")
    print(f"- Students: 5")
    print(f"- Courses: {len(courses)}")
    print(f"- Enrollments: {len(courses) * len(students)}")
    print("====================================")