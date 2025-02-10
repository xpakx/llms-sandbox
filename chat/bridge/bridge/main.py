from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.websockets import WebSocketDisconnect
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
config = load_config("config.json")
client = get_client(config["apiKey"])
history = [{"role": "system", "content": config["systemPrompt"]}]


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
                    await send_message(channel_id, websocket, [{"type":"Message", "message": {"content":"tst", "username":"me", "id":"1", "timestamp":"01-01-1970"}}])
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
    await send_to_channel(channel, [message])
    asyncio.create_task(process_response_fib(client, config, message, channel))
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


def chat(client: OpenAI, config, query: str):
    response = ""
    history.append({"role": "user", "content": query})
    try:
        response = ask_deepseek(client, history)
    except Exception as e:
        return {"type": "Error"}
    history.append({"role": "assistant", "content": response})
    return { 
            "type": "Message",
            "message": {
                "content": response,
                "username": "ai",
                "id": "1",
                "timestamp": str(datetime.now())
                }
            }
    

async def process_response(client: OpenAI, config, message, channel):
    response = chat(client, config, message['message']['content'])
    await send_to_channel(channel, [response])


# with fibonacci backoff
async def process_response_fib(client: OpenAI, config, message, channel):
    max_retries = 5
    fib_prev, fib_curr = 0, 1

    for attempt in range(max_retries):
        response = chat(client, config, message['message']['content'])
        if response.get('type') != 'Error':
            await send_to_channel(channel, [response])
            return

        await asyncio.sleep(fib_curr)
        fib_prev, fib_curr = fib_curr, fib_prev + fib_curr

    print("Max retries reached. Failed to process response.")
