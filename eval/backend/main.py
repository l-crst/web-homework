from typing import List

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlmodel import Session, select

from backend.database import get_session, create_db_and_tables
from backend import models


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


@app.post("/users/", response_model=models.User)
def create_user(user: models.User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/", response_model=List[models.User])
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


@app.post("/rooms/", response_model=models.Room)
def create_room(room: models.Room, session: Session = Depends(get_session)):
    session.add(room)
    session.commit()
    session.refresh(room)
    return room

@app.get("/rooms/", response_model=List[models.Room])
def list_rooms(session: Session = Depends(get_session)):
    statement = select(models.Room)
    rooms = session.exec(statement).all()
    return rooms

@app.get("/rooms/{room_id}/messages/", response_model=List[models.Message])
def list_messages(room_id: int, session: Session = Depends(get_session)):
    statement = select(models.Message).where(models.Message.room_id == room_id)
    messages = session.exec(statement).all()
    return messages

@app.get("/rooms/{room_id}/subscribers/", response_model=List[models.User])
def list_subscribers(room_id: int, session: Session = Depends(get_session)):
    statement = statement = (
        select(models.User)
        .join(models.Subscription)
        .where(models.Subscription.room_id == room_id)
    )
    subscribers = session.exec(statement).all()
    return subscribers


@app.post("/subscriptions/", response_model=models.Subscription)
def create_subscription(subscription: models.Subscription, session: Session = Depends(get_session)):
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    return subscription

@app.post("/messages/", response_model=models.Message)
def create_message(message: models.Message, session: Session = Depends(get_session)):
    session.add(message)
    session.commit()
    session.refresh(message)
    return message
