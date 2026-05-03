from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from backend.database import get_session
from backend import models, schemas

from backend.routers.users import find_user
from backend.routers.rooms import find_room

router = APIRouter()


@router.post("/{user_id}/{room_id}/", response_model=schemas.SubscriptionRead)
def create_subscription(user_id: int, room_id: int, session: Session = Depends(get_session)):
    find_user(session, user_id)
    find_room(session, room_id)
    statement = select(models.Subscription).where(models.Subscription.user_id == user_id, models.Subscription.room_id == room_id)
    find_subscription = session.exec(statement).first()
    if find_subscription:
        raise HTTPException(status_code=400, detail="User is already subscribed to the room")

    subscription = models.Subscription(user_id=user_id, room_id=room_id)
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return RedirectResponse(
        url=f"/rooms?user_id={user_id}",
        status_code=303
    )

@router.post("/delete/{user_id}/{room_id}/")
def delete_subscription(user_id: int, room_id: int, session: Session = Depends(get_session)):
    statement = select(models.Subscription).where(
        models.Subscription.user_id == user_id,
        models.Subscription.room_id == room_id
    )

    subscription = session.exec(statement).first()

    if subscription:
        session.delete(subscription)
        session.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )


    return RedirectResponse(
        url=f"/rooms?user_id={user_id}",
        status_code=303
    )
