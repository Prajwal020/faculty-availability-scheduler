from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.user import User, UserStatus
from app.models.student import Student
from app.models.faculty import Faculty


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return (
            self.db.query(User)
            .options(
                joinedload(User.student_profile),
                joinedload(User.faculty_profile).joinedload(Faculty.department),
            )
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .options(
                joinedload(User.student_profile),
                joinedload(User.faculty_profile).joinedload(Faculty.department),
            )
            .filter(User.email == email.lower().strip())
            .first()
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def update(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def list_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        return (
            self.db.query(User)
            .options(
                joinedload(User.student_profile),
                joinedload(User.faculty_profile).joinedload(Faculty.department),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    # Student specific
    def get_student_by_id_number(self, student_id_number: str) -> Optional[Student]:
        return self.db.query(Student).filter(Student.student_id_number == student_id_number.strip()).first()

    def get_student_by_user_id(self, user_id: UUID) -> Optional[Student]:
        return self.db.query(Student).filter(Student.user_id == user_id).first()

    def create_student(self, student: Student) -> Student:
        self.db.add(student)
        self.db.flush()
        return student

    # Faculty specific
    def get_faculty_by_employee_id(self, employee_id_number: str) -> Optional[Faculty]:
        return self.db.query(Faculty).filter(Faculty.employee_id_number == employee_id_number.strip()).first()

    def get_faculty_by_id(self, faculty_id: UUID) -> Optional[Faculty]:
        return (
            self.db.query(Faculty)
            .options(joinedload(Faculty.user), joinedload(Faculty.department))
            .filter(Faculty.id == faculty_id)
            .first()
        )

    def get_faculty_by_user_id(self, user_id: UUID) -> Optional[Faculty]:
        return (
            self.db.query(Faculty)
            .options(joinedload(Faculty.user), joinedload(Faculty.department))
            .filter(Faculty.user_id == user_id)
            .first()
        )

    def create_faculty(self, faculty: Faculty) -> Faculty:
        self.db.add(faculty)
        self.db.flush()
        return faculty

    def list_faculty(
        self,
        name: Optional[str] = None,
        department_id: Optional[UUID] = None,
        status: Optional[UserStatus] = UserStatus.ACTIVE,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Faculty]:
        query = (
            self.db.query(Faculty)
            .join(Faculty.user)
            .options(joinedload(Faculty.user), joinedload(Faculty.department))
        )

        if status:
            query = query.filter(User.status == status)

        if department_id:
            query = query.filter(Faculty.department_id == department_id)

        if name:
            search = f"%{name.strip()}%"
            query = query.filter(User.full_name.ilike(search))

        return query.offset(skip).limit(limit).all()
