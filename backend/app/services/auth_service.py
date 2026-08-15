from uuid import UUID
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException, BadRequestException
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserRole, UserStatus
from app.models.student import Student
from app.models.faculty import Faculty
from app.repositories.user_repository import UserRepository
from app.repositories.department_repository import DepartmentRepository
from app.schemas.auth import LoginRequest, TokenResponse, RegisterStudentRequest, RegisterFacultyRequest
from app.schemas.user import UserProfileResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.dept_repo = DepartmentRepository(db)

    def register_student(self, data: RegisterStudentRequest) -> TokenResponse:
        # Check email uniqueness
        if self.user_repo.get_by_email(data.email):
            raise ConflictException(
                code="EMAIL_ALREADY_REGISTERED",
                message="An account with this email already exists.",
            )

        # Check student ID uniqueness
        if self.user_repo.get_student_by_id_number(data.student_id_number):
            raise ConflictException(
                code="STUDENT_ID_EXISTS",
                message="A student profile with this ID number already exists.",
            )

        # Create user and student
        user = User(
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            full_name=data.full_name.strip(),
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
        )
        self.user_repo.create(user)

        student = Student(
            user_id=user.id,
            student_id_number=data.student_id_number.strip(),
            major=data.major.strip(),
        )
        self.user_repo.create_student(student)

        self.db.commit()
        self.db.refresh(user)

        # Generate JWT
        token = create_access_token(data={"sub": str(user.id), "role": user.role.value, "email": user.email})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserProfileResponse.model_validate(user),
        )

    def register_faculty(self, data: RegisterFacultyRequest) -> TokenResponse:
        # Check email uniqueness
        if self.user_repo.get_by_email(data.email):
            raise ConflictException(
                code="EMAIL_ALREADY_REGISTERED",
                message="An account with this email already exists.",
            )

        # Check employee ID uniqueness
        if self.user_repo.get_faculty_by_employee_id(data.employee_id_number):
            raise ConflictException(
                code="EMPLOYEE_ID_EXISTS",
                message="A faculty profile with this Employee ID number already exists.",
            )

        # Verify department exists
        department = self.dept_repo.get_by_id(data.department_id)
        if not department:
            raise NotFoundException(
                code="DEPARTMENT_NOT_FOUND",
                message="The specified department does not exist.",
            )

        # Create user and faculty
        user = User(
            email=data.email.lower().strip(),
            password_hash=hash_password(data.password),
            full_name=data.full_name.strip(),
            role=UserRole.FACULTY,
            status=UserStatus.ACTIVE,
        )
        self.user_repo.create(user)

        faculty = Faculty(
            user_id=user.id,
            department_id=department.id,
            employee_id_number=data.employee_id_number.strip(),
            title=data.title.strip(),
            office_location=data.office_location.strip(),
            bio=data.bio.strip() if data.bio else None,
            meeting_mode=data.meeting_mode,
        )
        self.user_repo.create_faculty(faculty)

        self.db.commit()
        self.db.refresh(user)

        # Generate JWT
        token = create_access_token(data={"sub": str(user.id), "role": user.role.value, "email": user.email})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserProfileResponse.model_validate(user),
        )

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException(
                code="INVALID_CREDENTIALS",
                message="Invalid email or password.",
            )

        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException(
                code="ACCOUNT_INACTIVE",
                message=f"Your account is currently {user.status.value.lower()}. Please contact an administrator.",
            )

        token = create_access_token(data={"sub": str(user.id), "role": user.role.value, "email": user.email})
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserProfileResponse.model_validate(user),
        )

    def get_user_profile(self, user_id: UUID) -> UserProfileResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                code="USER_NOT_FOUND",
                message="User account not found.",
            )
        return UserProfileResponse.model_validate(user)
