from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import anthropic
import os
load_dotenv()
app=FastAPI()

# class Response(BaseModel):
# class WebhookPayload(BaseModel):
#     event: str
#     message: str

# @app.post("/webhook")
# async def webhook(requests:Request, payload:WebhookPayload):
#     # print("Received:", requests.json())
#     x=await requests.json()
#     return {"status": "received", "data": x}
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

conversation_history={}

def ask_claude(userTxt:str,chat_id:int):
    history=conversation_history.setdefault(chat_id,[])
    history.append({"role":"user","content":userTxt})
    response=client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=history
    )
    reply=response.content[0].text
    history.append({"role":"assistant","content":reply})
    return reply

@app.get("/")
def home():
    return {"status": "Server is running"}

@app.post("/webhook")
async def webhook(update:dict):
    text = update.get("message", {}).get("text")
    chat_id = update.get("message", {}).get("chat", {}).get("id")
    print( text)
    
    if chat_id and text:
        reply=ask_claude(text,chat_id)

        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )
    return{"status": "ok"}