from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    is_active: bool = True

class Room(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


class Subscription(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    room_id: int = Field(foreign_key="room.id", primary_key=True)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    room_id: int = Field(foreign_key="room.id")
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

