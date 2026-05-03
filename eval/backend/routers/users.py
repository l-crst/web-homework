from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend import models, schemas


def find_user(session: Session, user_id: int):
    statement = select(models.User).where(models.User.id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


router = APIRouter()


@router.post("/", response_model=schemas.UserRead)
def create_user(user_data: schemas.UserCreate, session: Session = Depends(get_session)):
    statement = select(models.User).where(models.User.name == user_data.name)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this name already exists")

    user = models.User(**user_data.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = find_user(session, user_id)
    session.delete(user)
    session.commit()
    return {"message": "User deleted"}

@router.get("/", response_model=List[schemas.UserRead])
def list_users(session: Session = Depends(get_session)):
    statement = select(models.User)
    users = session.exec(statement).all()
    return users

@router.get("/{user_id}/rooms/", response_model=List[models.Room])
def list_subscriptions(user_id: int, session: Session = Depends(get_session)):
    statement = (
        select(models.Room)
        .join(models.Subscription)
        .where(models.Subscription.user_id == user_id)
    )
    rooms = session.exec(statement).all()
    return rooms

