from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User
from database.schemas import UserLogin, UserCreate, TokenResponse
from database import schemas,models
from auth.config import verify_password, hash_password
from auth.jwt import create_access_token, create_refresh_token, decode_token
from auth.validate_users import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserCreateResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


    return schemas.UserCreateResponse(
        status_code=201,
        message='User created successfully',
        data={
            "id": db_user.id,
            "email": db_user.email,
            'first_name': db_user.first_name,
            'last_name': db_user.last_name,
            'is_active': db_user.is_active,
            'is_verified': db_user.is_verified,
            'created_at': db_user.created_at,
        }
    )

#user login
@router.post("/login", response_model=schemas.UserLoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate tokens
    access_token = create_access_token({"sub": db_user.email})
    refresh_token = create_refresh_token({"sub": db_user.email})

    # Build user response
    user_data = schemas.UserResponse(
        id=db_user.id,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        is_active=db_user.is_active,
        is_verified=db_user.is_verified,
        created_at=db_user.created_at
    )

    token_data = schemas.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60  # 30 minutes in seconds
    )

    return schemas.UserLoginResponse(
        success=True,
        status_code=200,
        message="Login successful",
        data={
            "user": user_data,
            "tokens": token_data
        }
    )


# ------------------ /me ENDPOINT ------------------ #
@router.get("/me", response_model=schemas.SuccessResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently logged-in user"""
    return {
        "success": True,
        "status_code": 200,
        "message": "User profile fetched successfully",
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at,
        },
    }


# ------------------ REFRESH ENDPOINT ------------------ #
@router.post("/refresh", response_model=schemas.UserLoginResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Exchange a refresh token for a new access token"""
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create new access token
    new_access_token = create_access_token(data={"sub": user.email})

    return {
        "success": True,
        "status_code": 200,
        "message": "Access token refreshed successfully",
        "data": {
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "access_token": new_access_token,
        },
    }