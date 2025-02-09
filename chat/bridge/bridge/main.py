from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import re
from collections import defaultdict

clients = []
channels = defaultdict(set)

app = FastAPI()

@app.websocket("/ws/websocket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = data.strip()
            if data.startswith("SUBSCRIBE"):
                match = re.search(r"destination:\s*(\S+)", data)
                print(data)
                if match:
                    channel_id = match.group(1)
                    print("Topic to subscribe:", channel_id)
                    channels[channel_id].add(websocket)
                    await send_to_channel(channel_id, "{'type':'Message', 'message': {'content':'tst', 'username':'me', 'id':'1', 'timestamp':'01-01-1970'}}")
            else:
                print(data)
    except WebSocketDisconnect:
        clients.remove(websocket)


async def send_to_channel(channel_id: str, message: str):
    msg = f"SEND\ndestination:{channel_id}\n\n{message}\000"
    print(msg)
    for ws in channels[channel_id]:
        print(ws)
        await ws.send_text(msg)
