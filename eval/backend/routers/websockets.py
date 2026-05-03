from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from sqlmodel import Session

from backend.database import engine
from backend import models, schemas
from backend.routers.messages import create_message_in_db


router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        if room_id not in self.active_connections:
            return

        if websocket in self.active_connections[room_id]:
            self.active_connections[room_id].remove(websocket)

        if len(self.active_connections[room_id]) == 0:
            del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: int, data: dict):
        connections = self.active_connections.get(room_id, [])

        for connection in connections:
            await connection.send_json(data)


manager = ConnectionManager()


@router.websocket("/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: int,
    user_id: int,
):
    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content", "").strip()

            if content == "":
                await websocket.send_json({
                    "type": "error",
                    "detail": "Message vide",
                })
                continue

            message_data = schemas.MessageCreate(
                user_id=user_id,
                room_id=room_id,
                content=content,
            )

            try:
                with Session(engine) as session:
                    message = create_message_in_db(message_data, session)
                    user = session.get(models.User, user_id)

                    await manager.broadcast_to_room(room_id, {
                        "type": "message",
                        "id": message.id,
                        "user_id": message.user_id,
                        "username": user.name if user else "Utilisateur inconnu",
                        "room_id": message.room_id,
                        "content": message.content,
                        "created_at": str(message.created_at),
                    })

            except HTTPException as error:
                await websocket.send_json({
                    "type": "error",
                    "detail": error.detail,
                })

    except WebSocketDisconnect:
        manager.disconnect(room_id, websocket)