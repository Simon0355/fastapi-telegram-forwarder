from fastapi import FastAPI
from pydantic import BaseModel
from telethon.sync import TelegramClient
import asyncio

app = FastAPI()

class Message(BaseModel):
    chat_id: int
    text: str

# Telegram API credentials
api_id = "YOUR_API_ID"  # Erstat med din API ID
api_hash = "YOUR_API_HASH"  # Erstat med din API Hash
phone_number = "YOUR_PHONE_NUMBER"  # Erstat med dit telefonnummer

client = TelegramClient('session_name', api_id, api_hash)

@app.on_event("startup")
async def startup_event():
    await client.start()

@app.on_event("shutdown")
async def shutdown_event():
    await client.disconnect()

@app.post("/forward/")
async def forward_message(message: Message):
    # Her tilføjer du logikken til at forwarde beskeder
    try:
        await client.send_message(message.chat_id, message.text)
        return {"status": "Message forwarded", "chat_id": message.chat_id, "text": message.text}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

# Tilføj en route for at liste chat-id'er (valgfrit)
@app.get("/chats/")
async def list_chats():
    dialogs = await client.get_dialogs()
    chat_list = [{"id": dialog.id, "title": dialog.title} for dialog in dialogs]
    return chat_list
