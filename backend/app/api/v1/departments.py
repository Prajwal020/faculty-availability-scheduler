from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import require_admin
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get(
    "",
    response_model=List[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all academic departments",
)
def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[DepartmentResponse]:
    service = DepartmentService(db)
    return service.list_departments(skip=skip, limit=limit)


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get department details by ID",
)
def get_department(
    department_id: UUID,
    db: Session = Depends(get_db),
) -> DepartmentResponse:
    service = DepartmentService(db)
    return service.get_department(department_id)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new department (Admin only)",
)
def create_department(
    data: DepartmentCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DepartmentResponse:
    service = DepartmentService(db)
    return service.create_department(data)


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing department (Admin only)",
)
def update_department(
    department_id: UUID,
    data: DepartmentUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DepartmentResponse:
    service = DepartmentService(db)
    return service.update_department(department_id, data)
