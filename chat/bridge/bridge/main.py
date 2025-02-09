from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect

clients = []

app = FastAPI()

@app.websocket("/ws/websocket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
    except WebSocketDisconnect:
        clients.remove(websocket)
