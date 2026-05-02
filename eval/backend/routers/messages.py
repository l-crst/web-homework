from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend import models, schemas


router = APIRouter()

@router.post("/", response_model=models.MessageRead)
def create_message(message: schemas.MessageCreate, session: Session = Depends(get_session)):
    statement = select(models.Subscription).where(models.Subscription.user_id == message.user_id, models.Subscription.room_id == message.room_id)
    subscription = session.exec(statement).first()
    if subscription is None:
        raise HTTPException(status_code=400, detail="User is not subscribed to the room")
    
    message = models.Message(**message.dict())
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
