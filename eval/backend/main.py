from typing import List

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlmodel import Session, select

from backend.database import get_session, create_db_and_tables
from backend import models, schemas


def find_user(session: Session, user_id: int):
    statement = select(models.User).where(models.User.id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user

def find_room(session: Session, room_id: int):
    statement = select(models.Room).where(models.Room.id == room_id)
    room = session.exec(statement).first()
    if room is None:
        raise HTTPException(status_code=400, detail="Room not found")
    return room



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initialisation de la base...")
    create_db_and_tables()
    print("Base initialisée.")
    yield


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="backend/templates")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")



@app.get("/login/{name}", response_class=HTMLResponse)
def login_page(request: Request, name: str):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"name": name}
    )


@app.post("/users/", response_model=models.UserRead)
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

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = find_user(session, user_id)
    session.delete(user)
    session.commit()
    return {"message": "User deleted"}

@app.get("/users/", response_model=List[models.UserRead])
def list_users(session: Session = Depends(get_session)):
    statement = select(models.User)
    users = session.exec(statement).all()
    return users

@app.get("/users/{user_id}/rooms/", response_model=List[models.Room])
def list_subscriptions(user_id: int, session: Session = Depends(get_session)):
    statement = (
        select(models.Room)
        .join(models.Subscription)
        .where(models.Subscription.user_id == user_id)
    )
    rooms = session.exec(statement).all()
    return rooms


@app.post("/rooms/", response_model=models.RoomRead)
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

@app.delete("/rooms/{room_id}")
def delete_room(room_id: int, session: Session = Depends(get_session)):
    room = find_room(session, room_id)
    session.delete(room)
    session.commit()
    return {"message": "Room deleted"}

@app.get("/rooms/", response_model=List[models.RoomRead])
def list_rooms(session: Session = Depends(get_session)):
    statement = select(models.Room)
    rooms = session.exec(statement).all()
    return rooms

@app.get("/rooms/{room_id}/messages/", response_model=List[models.Message])
def list_messages(room_id: int, session: Session = Depends(get_session)):
    statement = select(models.Message).where(models.Message.room_id == room_id)
    messages = session.exec(statement).all()
    return messages

@app.get("/rooms/{room_id}/subscribers/", response_model=List[models.UserRead])
def list_subscribers(room_id: int, session: Session = Depends(get_session)):
    statement = statement = (
        select(models.User)
        .join(models.Subscription)
        .where(models.Subscription.room_id == room_id)
    )
    subscribers = session.exec(statement).all()
    return subscribers



@app.post("/subscriptions/", response_model=models.SubscriptionRead)
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

@app.delete("/subscriptions/")
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


@app.post("/messages/", response_model=models.MessageRead)
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
