"""Authentication endpoints"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db.database import get_db
from app.models import User
from app.core.security import verify_password, create_access_token
from app.core.logging import bind_user_context, logger

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: str
    role: str
    department_id: str | None = None
    title: str | None = None
    manager_id: str | None = None
    employee_no: str | None = None
    status: str


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint

    Returns JWT access token on successful authentication
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        logger.warning("login failed: unknown user", email=str(request.email))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        logger.warning("login failed: invalid password", email=str(request.email))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value}
    )
    bind_user_context(user.id, user.email)
    logger.info("login succeeded", role=user.role.value)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            department_id=user.department_id,
            title=user.title,
            manager_id=user.manager_id,
            employee_no=user.employee_no,
            status=user.status,
        ),
    )


@router.post("/logout")
async def logout():
    """User logout endpoint"""
    logger.info("logout requested")
    return {"message": "Logged out successfully"}
