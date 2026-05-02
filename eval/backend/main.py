from typing import List

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlmodel import Session, select

from backend.database import get_session, create_db_and_tables
from backend import models, schemas
from backend.routers import users, rooms, subscriptions, messages






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