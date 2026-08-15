import sys
from pathlib import Path

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password, create_access_token
from app.models.user import User, UserRole, UserStatus
from app.models.department import Department
from app.models.student import Student
from app.models.faculty import Faculty, MeetingMode

# In-memory test SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database schema for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_department(db_session: Session) -> Department:
    dept = Department(code="CS", name="Computer Science", building="Turing Hall")
    db_session.add(dept)
    db_session.commit()
    db_session.refresh(dept)
    return dept


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = User(
        email="admin@test.edu",
        password_hash=hash_password("AdminPass123!"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict:
    token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_user(db_session: Session) -> User:
    user = User(
        email="student@test.edu",
        password_hash=hash_password("StudentPass123!"),
        full_name="Student Bob",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.flush()

    student = Student(
        user_id=user.id,
        student_id_number="STU-TEST-001",
        major="Computer Science",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_auth_headers(student_user: User) -> dict:
    token = create_access_token({"sub": str(student_user.id), "role": student_user.role.value, "email": student_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def faculty_user(db_session: Session, sample_department: Department) -> User:
    user = User(
        email="faculty@test.edu",
        password_hash=hash_password("FacultyPass123!"),
        full_name="Dr. Alice Smith",
        role=UserRole.FACULTY,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.flush()

    faculty = Faculty(
        user_id=user.id,
        department_id=sample_department.id,
        employee_id_number="FAC-TEST-001",
        title="Associate Professor",
        office_location="Room 101",
        bio="Research in AI",
        meeting_mode=MeetingMode.IN_PERSON,
    )
    db_session.add(faculty)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def faculty_auth_headers(faculty_user: User) -> dict:
    token = create_access_token({"sub": str(faculty_user.id), "role": faculty_user.role.value, "email": faculty_user.email})
    return {"Authorization": f"Bearer {token}"}
