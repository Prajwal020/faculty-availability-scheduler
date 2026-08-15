from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException, BadRequestException
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.models.student import Student
from app.models.faculty import Faculty
from app.repositories.user_repository import UserRepository
from app.repositories.department_repository import DepartmentRepository
from app.schemas.user import UserCreate, UserResponse, UserProfileResponse
from app.schemas.student import StudentUpdate, StudentResponse
from app.schemas.faculty import FacultyUpdate, FacultyResponse, FacultyPublicProfile


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.dept_repo = DepartmentRepository(db)

    # Student operations
    def get_student_profile(self, user_id: UUID) -> StudentResponse:
        student = self.user_repo.get_student_by_user_id(user_id)
        if not student:
            raise NotFoundException(
                code="STUDENT_PROFILE_NOT_FOUND",
                message="Student profile not found.",
            )
        return StudentResponse.model_validate(student)

    def update_student_profile(self, user_id: UUID, data: StudentUpdate) -> StudentResponse:
        student = self.user_repo.get_student_by_user_id(user_id)
        if not student:
            raise NotFoundException(
                code="STUDENT_PROFILE_NOT_FOUND",
                message="Student profile not found.",
            )

        if data.major:
            student.major = data.major.strip()

        self.db.commit()
        self.db.refresh(student)
        return StudentResponse.model_validate(student)

    # Faculty operations
    def get_faculty_profile(self, user_id: UUID) -> FacultyResponse:
        faculty = self.user_repo.get_faculty_by_user_id(user_id)
        if not faculty:
            raise NotFoundException(
                code="FACULTY_PROFILE_NOT_FOUND",
                message="Faculty profile not found.",
            )
        return FacultyResponse.model_validate(faculty)

    def get_faculty_public_profile(self, faculty_id: UUID) -> FacultyPublicProfile:
        faculty = self.user_repo.get_faculty_by_id(faculty_id)
        if not faculty or faculty.user.status != UserStatus.ACTIVE:
            raise NotFoundException(
                code="FACULTY_NOT_FOUND",
                message="Faculty member not found or inactive.",
            )

        return FacultyPublicProfile(
            id=faculty.id,
            user_id=faculty.user_id,
            full_name=faculty.user.full_name,
            email=faculty.user.email,
            title=faculty.title,
            office_location=faculty.office_location,
            bio=faculty.bio,
            meeting_mode=faculty.meeting_mode,
            department_id=faculty.department_id,
            department_name=faculty.department.name,
            department_code=faculty.department.code,
        )

    def list_faculty(
        self,
        name: Optional[str] = None,
        department_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[FacultyPublicProfile]:
        faculty_list = self.user_repo.list_faculty(
            name=name,
            department_id=department_id,
            status=UserStatus.ACTIVE,
            skip=skip,
            limit=limit,
        )

        return [
            FacultyPublicProfile(
                id=f.id,
                user_id=f.user_id,
                full_name=f.user.full_name,
                email=f.user.email,
                title=f.title,
                office_location=f.office_location,
                bio=f.bio,
                meeting_mode=f.meeting_mode,
                department_id=f.department_id,
                department_name=f.department.name,
                department_code=f.department.code,
            )
            for f in faculty_list
        ]

    def update_faculty_profile(self, user_id: UUID, data: FacultyUpdate) -> FacultyResponse:
        faculty = self.user_repo.get_faculty_by_user_id(user_id)
        if not faculty:
            raise NotFoundException(
                code="FACULTY_PROFILE_NOT_FOUND",
                message="Faculty profile not found.",
            )

        if data.title:
            faculty.title = data.title.strip()
        if data.office_location:
            faculty.office_location = data.office_location.strip()
        if data.bio is not None:
            faculty.bio = data.bio.strip() if data.bio else None
        if data.meeting_mode is not None:
            faculty.meeting_mode = data.meeting_mode
        if data.department_id is not None:
            dept = self.dept_repo.get_by_id(data.department_id)
            if not dept:
                raise NotFoundException(
                    code="DEPARTMENT_NOT_FOUND",
                    message="Specified department does not exist.",
                )
            faculty.department_id = data.department_id

        self.db.commit()
        self.db.refresh(faculty)
        return FacultyResponse.model_validate(faculty)

    # Admin operations
    def create_user_by_admin(self, data: UserCreate) -> UserResponse:
        if self.user_repo.get_by_email(data.email):
            raise ConflictException(
                code="EMAIL_ALREADY_REGISTERED",
                message="An account with this email already exists.",
            )

        user = User(
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            full_name=data.full_name.strip(),
            role=data.role,
            status=UserStatus.ACTIVE,
        )
        self.user_repo.create(user)
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)

    def update_user_status(self, user_id: UUID, status: UserStatus) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                code="USER_NOT_FOUND",
                message="User account not found.",
            )

        user.status = status
        self.db.commit()
        self.db.refresh(user)
        return UserResponse.model_validate(user)

    def list_all_users(self, skip: int = 0, limit: int = 50) -> List[UserProfileResponse]:
        users = self.user_repo.list_users(skip=skip, limit=limit)
        return [UserProfileResponse.model_validate(u) for u in users]
