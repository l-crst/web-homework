from typing import List

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

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


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request, session: Session = Depends(get_session)):
    users = session.exec(select(models.User)).all()

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"users": users}
    )


@app.post("/select-user/")
def select_user(user_id: int = Form(...)):
    print(f"User selected: {user_id}")
    print("")
    return RedirectResponse(
        url=f"/rooms?user_id={user_id}",
        status_code=303
    )

@app.get("/rooms", response_class=HTMLResponse)
def rooms_page(request: Request, user_id: int, session: Session = Depends(get_session)):
    user = session.get(models.User, user_id)

    all_rooms = session.exec(select(models.Room)).all()

    subscribed_rooms = session.exec(select(models.Room).join(models.Subscription).where(models.Subscription.user_id == user_id)).all()

    subscribed_room_ids = {room.id for room in subscribed_rooms}

    return templates.TemplateResponse(
        request=request,
        name="rooms.html",
        context={
            "user": user,
            "rooms": all_rooms,
            "subscribed_room_ids": subscribed_room_ids,
        }
    )


@app.get("/{user_id}/room/{room_id}/", response_class=HTMLResponse)
def room_page(request: Request, user_id: int, room_id: int, session: Session = Depends(get_session)):
    user = session.get(models.User, user_id)
    room = session.get(models.Room, room_id)

    messages = session.exec(select(models.Message).where(models.Message.room_id == room_id)).all()
    users = session.exec(select(models.User)).all()
    user_by_id = {user.id: user for user in users}

    return templates.TemplateResponse(
        request=request,
        name="room.html",
        context={
            "user": user,
            "room": room,
            "messages": messages,
            "user_by_id": user_by_id,
        }
    )

@app.post("/rooms/{room_id}/send-messages/")
def send_message(room_id:int, user_id:str = Form(...), content:str = Form(...), session: Session = Depends(get_session)):
    message_data = schemas.MessageCreate(content=content, user_id=user_id, room_id=room_id)
    messages.create_message_in_db(message_data, session)

    return RedirectResponse(
        url=f"/{user_id}/room/{room_id}/",
        status_code=303
    )


