from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import FamilyProfile, User
from typing import List

router = APIRouter()

def verify_admin(current_user: User = Depends()):
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this endpoint"
        )
    return current_user

@router.get("/", response_model=List[dict])
def get_all_families(
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    families = db.query(FamilyProfile).all()
    result = []
    for family in families:
        user = db.query(User).filter(User.id == family.user_id).first()
        result.append({
            "id": family.id,
            "user_id": family.user_id,
            "full_name": user.full_name if user else "Unknown",
            "email": user.email if user else "Unknown",
            "family_size": family.family_size,
            "monthly_income": family.monthly_income,
            "location": family.location,
            "created_at": family.created_at
        })
    return result

@router.get("/stats")
def get_family_stats(
    current_user: User = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    total_families = db.query(FamilyProfile).count()
    return {"total_families": total_families}
