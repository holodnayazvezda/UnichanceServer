from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token, get_current_user
from models.user_status import UserStatus
from schemas.user import UserCreate, UserLogin, Token, UserOut
from models.user import User
from services.files import check_file_exists

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.avatar_uuid:
        if not check_file_exists(user.avatar_uuid, db):
            raise HTTPException(status_code=404, detail="Avatar file not found")

    hashed = hash_password(user.password)
    new_user = User(
        name=user.name,
        surname=user.surname,
        patronymic=user.patronymic,
        password_hash=hashed,
        status=UserStatus.GUEST,
        subject=user.subject,
        avatar_uuid=user.avatar_uuid,
        email=str(user.email)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login_user(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user