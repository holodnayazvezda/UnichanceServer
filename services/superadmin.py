from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from schemas.superadmin import ResultOfSearchUserId, ResulfOfOperations
from models.user import User


router = APIRouter(prefix="/superadmin", tags=["Superadmin"])


@router.get("/find_id_from_FIO/{user_email}", response_model=ResultOfSearchUserId)
def find_id_from_FIO(user_email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    user = db.query(User).filter(User.email == user_email).first()
    if current_user.status != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not SUPERADMIN"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not founded"
        )

    return {"id": user.id}

    
@router.delete("/del_user/{user_id}", response_model=ResulfOfOperations)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if current_user.status != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not SUPERADMIN"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not founded"
        )
        
    if user.status == 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't delete superadmin"
        )

    db.delete(user)
    db.commit()

    return {"result": "User secsessfully delete"}


@router.put("/change_to_teacher/{user_id}", response_model=ResulfOfOperations)
def set_status_teacher(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.status != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not SUPERADMIN"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not founded"
        )
        
    if user.status == 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="You can't move down from superadmin to teacher"
        )
        
    if user.status == 'teacher':
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already teacher"
        )

    user.status = "teacher"
    db.commit()
    db.refresh(user)

    return {"result": "User status is secsessfully change"}