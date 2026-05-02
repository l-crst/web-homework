from typing import List

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlmodel import Session, select

from backend.database import get_session, create_db_and_tables
from backend import models, schemas


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
    user = models.User(**user_data.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

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
    room = models.Room(**room.dict())
    session.add(room)
    session.commit()
    session.refresh(room)
    return room

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
    subscription = models.Subscription(**subscription.dict())
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription

@app.post("/messages/", response_model=models.MessageRead)
def create_message(message: schemas.MessageCreate, session: Session = Depends(get_session)):
    message = models.Message(**message.dict())
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
