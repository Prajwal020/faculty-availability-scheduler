from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.department import Department


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, department_id: UUID) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == department_id).first()

    def get_by_code(self, code: str) -> Optional[Department]:
        return self.db.query(Department).filter(Department.code == code.upper().strip()).first()

    def get_by_name(self, name: str) -> Optional[Department]:
        return self.db.query(Department).filter(Department.name.ilike(name.strip())).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Department]:
        return (
            self.db.query(Department)
            .order_by(Department.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, department: Department) -> Department:
        self.db.add(department)
        self.db.flush()
        return department

    def update(self, department: Department) -> Department:
        self.db.add(department)
        self.db.flush()
        return department
