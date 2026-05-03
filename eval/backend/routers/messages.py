from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend import models, schemas


router = APIRouter()


def create_message_in_db(message_data: schemas.MessageCreate,session: Session):
    statement = select(models.Subscription).where(models.Subscription.user_id == message_data.user_id, models.Subscription.room_id == message_data.room_id)
    subscription = session.exec(statement).first()
    if subscription is None:
        raise HTTPException(status_code=400, detail="User is not subscribed to the room")

    message = models.Message(**message_data.model_dump())

    session.add(message)
    session.commit()
    session.refresh(message)

    return message

@router.post("/", response_model=schemas.MessageRead)
def create_message(message: schemas.MessageCreate, session: Session = Depends(get_session)):
    return create_message_in_db(message, session)
