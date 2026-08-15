from typing import List
from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_access_token
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository

# HTTP Bearer token extractor
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Validate the incoming JWT Bearer token and retrieve the active user entity.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedException(
            code="NOT_AUTHENTICATED",
            message="Missing or invalid Bearer authentication token.",
        )

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise UnauthorizedException(
            code="INVALID_TOKEN",
            message="Invalid, expired, or malformed authentication token.",
        )

    user_id_str = payload.get("sub")
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise UnauthorizedException(
            code="INVALID_TOKEN_SUBJECT",
            message="Token contains invalid subject identity.",
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException(
            code="USER_NOT_FOUND",
            message="The user associated with this token no longer exists.",
        )

    if user.status != UserStatus.ACTIVE:
        raise UnauthorizedException(
            code="ACCOUNT_INACTIVE",
            message=f"User account is {user.status.value.lower()}.",
        )

    return user


class RoleChecker:
    """Dependency for enforcing Role-Based Access Control (RBAC)."""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise ForbiddenException(
                code="INSUFFICIENT_PERMISSIONS",
                message=f"Action requires one of the following roles: {[r.value for r in self.allowed_roles]}.",
            )
        return current_user


# Convenience dependencies
require_student = RoleChecker([UserRole.STUDENT])
require_faculty = RoleChecker([UserRole.FACULTY])
require_admin = RoleChecker([UserRole.ADMIN])
require_faculty_or_admin = RoleChecker([UserRole.FACULTY, UserRole.ADMIN])
