from datetime import datetime
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    name: str
    is_active: bool = True

class UserRead(SQLModel):
    id: int
    name: str
    is_active: bool




class RoomCreate(SQLModel):
    name: str

class RoomRead(SQLModel):
    id: int
    name: str




class SubscriptionCreate(SQLModel):
    user_id: int
    room_id: int

class SubscriptionRead(SQLModel):
    user_id: int
    room_id: int



class MessageCreate(SQLModel):
    user_id: int
    room_id: int
    content: str

class MessageRead(SQLModel):
    id: int
    user_id: int
    room_id: int
    content: str
    created_at: datetime