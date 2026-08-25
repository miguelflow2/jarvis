"""JARVIS Cloud - version serveur sans écran (PC tools désactivés)"""
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os, json, asyncio, tempfile
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

SYSTEM_PROMPT = """Tu es JARVIS, IA ultime style Tony Stark, en version CLOUD.
Tu tournes sur un serveur 24/7 - tu n'as PAS accès à un PC physique ici.
Tu peux: répondre, chercher sur le web, mémoriser, créer du code/texte, conseiller.
Tu parles français, concis, classe, Stark. Activation "Salut Jarvis"."""

app = FastAPI(title="JARVIS Cloud")

class ChatReq(BaseModel):
    message: str

client = None
def get_client():
    global client
    if client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1",
                        default_headers={"HTTP-Referer":"https://jarvis.cloud","X-Title":"JARVIS"})
    return client

@app.post("/api/chat")
async def chat(req: ChatReq):
    c = get_client()
    r = c.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":req.message}],
        max_tokens=800, temperature=0.7
    )
    answer = r.choices[0].message.content
    return {"answer": answer, "mode": "cloud"}

@app.get("/api/status")
def status():
    return {"status":"online", "mode":"cloud 24/7", "pc_control": False}

@app.get("/")
def index():
    return {"app":"JARVIS Cloud", "status":"online", "endpoints":["/api/chat","/api/status"]}
