from fastapi import FastAPI
from backend.transport.websocket import websocket_endpoint

app = FastAPI()

app.websocket("/ws")(websocket_endpoint)
