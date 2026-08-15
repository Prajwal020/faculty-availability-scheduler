import sys
from datetime import time, date
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.models.department import Department
from app.models.student import Student
from app.models.faculty import Faculty, MeetingMode
from app.models.availability import RegularAvailability
from app.models.appointment import Appointment, AppointmentStatus


def seed_database():
    db = SessionLocal()
    try:
        print("[INFO] Starting database seeding...")

        # 1. Seed Departments
        dept_cs = db.query(Department).filter(Department.code == "CS").first()
        if not dept_cs:
            dept_cs = Department(code="CS", name="Computer Science & Engineering", building="Turing Hall")
            db.add(dept_cs)

        dept_math = db.query(Department).filter(Department.code == "MATH").first()
        if not dept_math:
            dept_math = Department(code="MATH", name="Mathematics & Data Science", building="Euler Block")
            db.add(dept_math)

        dept_ee = db.query(Department).filter(Department.code == "EE").first()
        if not dept_ee:
            dept_ee = Department(code="EE", name="Electrical & Electronics Engineering", building="Tesla Complex")
            db.add(dept_ee)

        db.flush()
        print("[SUCCESS] Departments seeded.")

        # 2. Seed Admin User
        admin_user = db.query(User).filter(User.email == "admin@institution.edu").first()
        if not admin_user:
            admin_user = User(
                email="admin@institution.edu",
                password_hash=hash_password("AdminPassword123!"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
            )
            db.add(admin_user)
            print("[SUCCESS] Admin user seeded (admin@institution.edu / AdminPassword123!).")

        # 3. Seed Faculty Members
        fac_1_user = db.query(User).filter(User.email == "prof.sharma@institution.edu").first()
        if not fac_1_user:
            fac_1_user = User(
                email="prof.sharma@institution.edu",
                password_hash=hash_password("FacultyPassword123!"),
                full_name="Dr. Rajesh Sharma",
                role=UserRole.FACULTY,
                status=UserStatus.ACTIVE,
            )
            db.add(fac_1_user)
            db.flush()

            fac_1 = Faculty(
                user_id=fac_1_user.id,
                department_id=dept_cs.id,
                employee_id_number="FAC-1001",
                title="Professor & HOD",
                office_location="Turing Hall, Room 301",
                bio="Specializing in Distributed Systems, Cloud Architecture, and High-Performance Computing.",
                meeting_mode=MeetingMode.HYBRID,
            )
            db.add(fac_1)
            db.flush()
            print("[SUCCESS] Faculty Dr. Rajesh Sharma seeded.")
        else:
            fac_1 = db.query(Faculty).filter(Faculty.user_id == fac_1_user.id).first()

        fac_2_user = db.query(User).filter(User.email == "prof.menon@institution.edu").first()
        if not fac_2_user:
            fac_2_user = User(
                email="prof.menon@institution.edu",
                password_hash=hash_password("FacultyPassword123!"),
                full_name="Dr. Ananya Menon",
                role=UserRole.FACULTY,
                status=UserStatus.ACTIVE,
            )
            db.add(fac_2_user)
            db.flush()

            fac_2 = Faculty(
                user_id=fac_2_user.id,
                department_id=dept_math.id,
                employee_id_number="FAC-1002",
                title="Associate Professor",
                office_location="Euler Block, Room 204",
                bio="Research in Applied Statistics, Machine Learning, and Discrete Mathematics.",
                meeting_mode=MeetingMode.IN_PERSON,
            )
            db.add(fac_2)
            db.flush()
            print("[SUCCESS] Faculty Dr. Ananya Menon seeded.")
        else:
            fac_2 = db.query(Faculty).filter(Faculty.user_id == fac_2_user.id).first()

        # 4. Seed Regular Availability
        if fac_1:
            existing_reg = db.query(RegularAvailability).filter(RegularAvailability.faculty_id == fac_1.id).first()
            if not existing_reg:
                # Monday 09:00 - 12:00
                db.add(RegularAvailability(
                    faculty_id=fac_1.id,
                    day_of_week=0,
                    start_time=time(9, 0),
                    end_time=time(12, 0),
                    slot_duration_minutes=30,
                    is_active=True,
                ))
                # Monday 14:00 - 16:00
                db.add(RegularAvailability(
                    faculty_id=fac_1.id,
                    day_of_week=0,
                    start_time=time(14, 0),
                    end_time=time(16, 0),
                    slot_duration_minutes=30,
                    is_active=True,
                ))
                # Wednesday 10:00 - 13:00
                db.add(RegularAvailability(
                    faculty_id=fac_1.id,
                    day_of_week=2,
                    start_time=time(10, 0),
                    end_time=time(13, 0),
                    slot_duration_minutes=30,
                    is_active=True,
                ))
                # Friday 14:00 - 17:00
                db.add(RegularAvailability(
                    faculty_id=fac_1.id,
                    day_of_week=4,
                    start_time=time(14, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=30,
                    is_active=True,
                ))
                print("[SUCCESS] Regular weekly availability seeded for Dr. Rajesh Sharma.")

        if fac_2:
            existing_reg_2 = db.query(RegularAvailability).filter(RegularAvailability.faculty_id == fac_2.id).first()
            if not existing_reg_2:
                # Tuesday 09:30 - 12:30
                db.add(RegularAvailability(
                    faculty_id=fac_2.id,
                    day_of_week=1,
                    start_time=time(9, 30),
                    end_time=time(12, 30),
                    slot_duration_minutes=30,
                    is_active=True,
                ))
                # Thursday 14:00 - 17:00
                db.add(RegularAvailability(
                    faculty_id=fac_2.id,
                    day_of_week=3,
                    start_time=time(14, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=30,
                    is_active=True,
                ))
                print("[SUCCESS] Regular weekly availability seeded for Dr. Ananya Menon.")

        # 5. Seed Students
        stu_1_user = db.query(User).filter(User.email == "student.alex@institution.edu").first()
        if not stu_1_user:
            stu_1_user = User(
                email="student.alex@institution.edu",
                password_hash=hash_password("StudentPassword123!"),
                full_name="Alex Rivera",
                role=UserRole.STUDENT,
                status=UserStatus.ACTIVE,
            )
            db.add(stu_1_user)
            db.flush()

            stu_1 = Student(
                user_id=stu_1_user.id,
                student_id_number="STU-2026-001",
                major="Computer Science",
            )
            db.add(stu_1)
            print("[SUCCESS] Student Alex Rivera seeded.")
        else:
            stu_1 = db.query(Student).filter(Student.user_id == stu_1_user.id).first()

        stu_2_user = db.query(User).filter(User.email == "student.priya@institution.edu").first()
        if not stu_2_user:
            stu_2_user = User(
                email="student.priya@institution.edu",
                password_hash=hash_password("StudentPassword123!"),
                full_name="Priya Patel",
                role=UserRole.STUDENT,
                status=UserStatus.ACTIVE,
            )
            db.add(stu_2_user)
            db.flush()

            stu_2 = Student(
                user_id=stu_2_user.id,
                student_id_number="STU-2026-002",
                major="Mathematics & Data Science",
            )
            db.add(stu_2)
            print("[SUCCESS] Student Priya Patel seeded.")
        else:
            stu_2 = db.query(Student).filter(Student.user_id == stu_2_user.id).first()

        # 6. Seed Sample Appointments
        if fac_1 and stu_1 and stu_2:
            existing_appt = db.query(Appointment).first()
            if not existing_appt:
                # REQUESTED appointment: Alex Rivera with Dr. Rajesh Sharma
                db.add(Appointment(
                    student_id=stu_1.id,
                    faculty_id=fac_1.id,
                    date=date(2026, 8, 24),
                    start_time=time(9, 0),
                    end_time=time(9, 30),
                    duration_minutes=30,
                    status=AppointmentStatus.REQUESTED,
                    reason="Discussing capstone project roadmap and cloud architecture",
                ))

                # ACCEPTED appointment: Priya Patel with Dr. Rajesh Sharma
                db.add(Appointment(
                    student_id=stu_2.id,
                    faculty_id=fac_1.id,
                    date=date(2026, 8, 24),
                    start_time=time(10, 0),
                    end_time=time(10, 30),
                    duration_minutes=30,
                    status=AppointmentStatus.ACCEPTED,
                    reason="Distributed ML optimization discussion",
                    faculty_notes="Reviewed preliminary benchmarks. Please prepare distributed training slides.",
                ))

                # REJECTED appointment: Alex Rivera with Dr. Ananya Menon
                if fac_2:
                    db.add(Appointment(
                        student_id=stu_1.id,
                        faculty_id=fac_2.id,
                        date=date(2026, 8, 25),
                        start_time=time(10, 0),
                        end_time=time(10, 30),
                        duration_minutes=30,
                        status=AppointmentStatus.REJECTED,
                        reason="Statistical inference consultation",
                        cancellation_reason="Attending department curriculum committee meeting at that time.",
                    ))
                print("[SUCCESS] Sample appointments seeded (REQUESTED, ACCEPTED, REJECTED).")

        db.commit()
        print("[COMPLETE] Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error during database seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
