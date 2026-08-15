from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, NotFoundException
from app.models.department import Department
from app.repositories.department_repository import DepartmentRepository
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DepartmentRepository(db)

    def create_department(self, data: DepartmentCreate) -> Department:
        # Check code uniqueness
        if self.repo.get_by_code(data.code):
            raise ConflictException(
                code="DEPARTMENT_CODE_EXISTS",
                message=f"A department with code '{data.code}' already exists.",
            )

        # Check name uniqueness
        if self.repo.get_by_name(data.name):
            raise ConflictException(
                code="DEPARTMENT_NAME_EXISTS",
                message=f"A department with name '{data.name}' already exists.",
            )

        department = Department(
            code=data.code.upper().strip(),
            name=data.name.strip(),
            building=data.building.strip() if data.building else None,
        )
        created = self.repo.create(department)
        self.db.commit()
        self.db.refresh(created)
        return created

    def get_department(self, department_id: UUID) -> Department:
        dept = self.repo.get_by_id(department_id)
        if not dept:
            raise NotFoundException(
                code="DEPARTMENT_NOT_FOUND",
                message="Department not found.",
            )
        return dept

    def list_departments(self, skip: int = 0, limit: int = 100) -> List[Department]:
        return self.repo.list_all(skip=skip, limit=limit)

    def update_department(self, department_id: UUID, data: DepartmentUpdate) -> Department:
        dept = self.get_department(department_id)

        if data.name and data.name.strip().lower() != dept.name.lower():
            existing = self.repo.get_by_name(data.name)
            if existing and existing.id != department_id:
                raise ConflictException(
                    code="DEPARTMENT_NAME_EXISTS",
                    message=f"A department with name '{data.name}' already exists.",
                )
            dept.name = data.name.strip()

        if data.building is not None:
            dept.building = data.building.strip() if data.building else None

        updated = self.repo.update(dept)
        self.db.commit()
        self.db.refresh(updated)
        return updated
