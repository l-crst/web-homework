from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend import models, schemas

from backend.routers.users import find_user
from backend.routers.rooms import find_room

router = APIRouter()


@router.post("/", response_model=models.SubscriptionRead)
def create_subscription(subscription: schemas.SubscriptionCreate, session: Session = Depends(get_session)):
    find_user(session, subscription.user_id)
    find_room(session, subscription.room_id)
    statement = select(models.Subscription).where(models.Subscription.user_id == subscription.user_id, models.Subscription.room_id == subscription.room_id)
    find_subscription = session.exec(statement).first()
    if find_subscription:
        raise HTTPException(status_code=400, detail="User is already subscribed to the room")

    subscription = models.Subscription(**subscription.dict())
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription

@router.delete("/")
def delete_subscription(user_id: int, room_id: int, session: Session = Depends(get_session)):
    statement = select(models.Subscription).where(
        models.Subscription.user_id == user_id,
        models.Subscription.room_id == room_id
    )

    subscription = session.exec(statement).first()

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    session.delete(subscription)
    session.commit()

    return {
        "message": "Subscription deleted",
        "user_id": user_id,
        "room_id": room_id
    }
