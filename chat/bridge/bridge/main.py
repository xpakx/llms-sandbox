from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import re
from collections import defaultdict
from typing import Any, Dict
import json
from bridge.ai import get_client, ask_deepseek
from datetime import datetime
from openai import OpenAI
import asyncio


def load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as file:
        return json.load(file)


clients = []
channels = defaultdict(set)

app = FastAPI()
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )
config = load_config("config.json")
client = get_client(config["apiKey"])
history = [{"role": "system", "content": config["systemPrompt"], "date": datetime.now()}]


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
                    await send_messages_on_subscription(channel_id, websocket)
            else:
                print(data)
    except WebSocketDisconnect:
        clients.remove(websocket)
        for channel in channels.values():
            if websocket in channel:
                channel.remove(websocket)


@app.post("/send/{channel_id}")
async def send_message_to_channel(channel_id: str, message: Dict[str, Any]):
    channel = f"/topic/{channel_id}"
    if channel not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    query = message['content'].strip()
    time = datetime.now()
    msg = {"role": "user", "content": query, "date": time}
    history.append(msg)
    response = to_response(msg)
    await send_to_channel(channel, [response])
    asyncio.create_task(process_response_fib(client, config, channel))
    return {"status": "Message sent to channel", "channel_id": channel}


async def send_to_channel(channel_id: str, message: Any):
    message_json = json.dumps(message)
    msg = f"SEND\ndestination:{channel_id}\n\n{message_json}\000"
    print(msg)
    for ws in channels[channel_id]:
        await ws.send_text(msg)


async def send_message(channel_id: str, ws: WebSocket, message: Any):
    message_json = json.dumps(message)
    msg = f"SEND\ndestination:{channel_id}\n\n{message_json}\000"
    print(msg)
    await ws.send_text(msg)


def get_history():
    return list(map(lambda x: {"role": x["role"], "content": x["content"]}, history))


def chat(client: OpenAI, config):
    response = ""
    try:
        response = ask_deepseek(client, get_history())
    except Exception as e:
        print(e)
        return {"type": f"Error, {e}"}
    time = datetime.now()
    msg = {"role": "assistant", "content": response, "date": time}
    history.append(msg)
    return to_response(msg)


async def process_response(client: OpenAI, config, message, channel):
    query = message['content']
    history.append({"role": "user", "content": query})
    response = chat(client, config)
    await send_to_channel(channel, [response])


# with fibonacci backoff
async def process_response_fib(client: OpenAI, config, channel):
    base = 10
    max_retries = 5
    fib_prev, fib_curr = 0, 1

    for attempt in range(max_retries + 1):
        response = chat(client, config)
        error = response.get('type') == 'Error'
        content = response.get('message', {}).get('content')
        empty = (content is None or content == '')
        print(f"Response: {response}")
        if not (error or empty):
            await send_to_channel(channel, [response])
            return
        if attempt < max_retries:
            print("Retrying…")
            await asyncio.sleep(fib_curr * base)
            fib_prev, fib_curr = fib_curr, fib_prev + fib_curr

    print("Max retries reached. Failed to process response.")


@app.get("/{channel_id}/{index}")
async def get_message_from_channel(channel_id: str, index: int):
    channel = f"/topic/{channel_id}"
    if channel not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    i = len(history) - index - 1
    if i < 0:
        raise HTTPException(status_code=400, detail="Bad index")
    return to_response(history[i])


async def send_messages_on_subscription(channel_id: str, ws: WebSocket):
    hist = get_detailed_history()
    await send_message(channel_id, ws, hist)


def get_detailed_history():
    return [to_response(msg) for msg in history if msg["role"] != "system"]


def to_response(msg):
    time = msg["date"].strftime("%Y-%m-%d %H:%M:%S")
    return {
                "type": "Message",
                "message": {
                    "content": msg["content"],
                    "username": "ai" if msg["role"] == "assistant" else msg["role"],
                    "id": "1",
                    "timestamp": time
                    }
                }


@app.delete("/{channel_id}")
async def reset_channel(channel_id: str):
    channel = f"/topic/{channel_id}"
    if channel not in channels:
        raise HTTPException(status_code=404, detail="Channel not found")
    system_msg = history[0]
    history.clear()
    history.append(system_msg)
    await send_to_channel(channel, [{"type": "Clear"}])
