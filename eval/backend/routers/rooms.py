from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend import models, schemas


def find_room(session: Session, room_id: int):
    statement = select(models.Room).where(models.Room.id == room_id)
    room = session.exec(statement).first()
    if room is None:
        raise HTTPException(status_code=400, detail="Room not found")
    return room

router = APIRouter()

@router.post("/", response_model=models.RoomRead)
def create_room(room: schemas.RoomCreate, session: Session = Depends(get_session)):
    statement = select(models.Room).where(models.Room.name == room.name)
    existing_room = session.exec(statement).first()
    if existing_room:
        raise HTTPException(status_code=400, detail="Room with this name already exists")
    
    room = models.Room(**room.dict())
    session.add(room)
    session.commit()
    session.refresh(room)
    return room

@router.delete("/{room_id}")
def delete_room(room_id: int, session: Session = Depends(get_session)):
    room = find_room(session, room_id)
    session.delete(room)
    session.commit()
    return {"message": "Room deleted"}

@router.get("/", response_model=List[models.RoomRead])
def list_rooms(session: Session = Depends(get_session)):
    statement = select(models.Room)
    rooms = session.exec(statement).all()
    return rooms

@router.get("/{room_id}/messages/", response_model=List[models.Message])
def list_messages(room_id: int, session: Session = Depends(get_session)):
    statement = select(models.Message).where(models.Message.room_id == room_id)
    messages = session.exec(statement).all()
    return messages

@router.get("/{room_id}/subscribers/", response_model=List[models.UserRead])
def list_subscribers(room_id: int, session: Session = Depends(get_session)):
    statement = statement = (
        select(models.User)
        .join(models.Subscription)
        .where(models.Subscription.room_id == room_id)
    )
    subscribers = session.exec(statement).all()
    return subscribers