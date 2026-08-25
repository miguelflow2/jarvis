from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os, sys, json, asyncio, tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))
from core.brain import JarvisBrain
from core.vision import see_screen
from core.memory import recall
from core.profiles import get_current, set_current, list_profiles
from core.correction import load_corr
from core.plugins_loader import list_plugins
from core.routines import list_watches
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="JARVIS iPhone API")
brain = JarvisBrain()

class ChatReq(BaseModel):
    message: str

class ConfigReq(BaseModel):
    voice: str = None
    model: str = None
    wake_word: str = None

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")

@app.get("/api/config")
def get_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

@app.post("/api/config")
def set_config(req: ConfigReq):
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    if req.voice: cfg["jarvis"]["voice"] = req.voice
    if req.model: cfg["jarvis"]["model"] = req.model
    if req.wake_word: cfg["jarvis"]["wake_word"] = req.wake_word
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return cfg

@app.post("/api/chat")
async def chat(req: ChatReq):
    answer = brain.ask(req.message)
    # Si controle iPhone, on le laisse passer tel quel pour que l'app l'execute
    if "IPHONE_OPEN:" not in answer:
        try:
            import edge_tts, tempfile, pygame, json
            cfg_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
            with open(cfg_path, encoding="utf-8") as f:
                voice = json.load(f)["jarvis"]["voice"]
            # Nettoie le prefix IPHONE_OPEN si present pour TTS
            tts_text = answer.split("IPHONE_OPEN:")[0].strip() or answer
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tmp = f.name
            communicate = edge_tts.Communicate(tts_text, voice)
            await communicate.save(tmp)
            pygame.mixer.init()
            pygame.mixer.music.load(tmp)
            pygame.mixer.music.play()
            import threading
            def cleanup():
                import time
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.quit()
                try: os.remove(tmp)
                except: pass
            threading.Thread(target=cleanup, daemon=True).start()
        except Exception as e:
            print(f"[TTS lunettes error] {e}")
    return {"answer": answer, "routed_to": "lunettes M01 Pro_F444"}

@app.get("/api/tts")
async def tts(text: str, voice: str = "fr-FR-DeniseNeural"):
    try:
        import edge_tts
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tmp = f.name
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp)
        def iterfile():
            with open(tmp, "rb") as f:
                yield from f
            try: os.remove(tmp)
            except: pass
        return StreamingResponse(iterfile(), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/vision")
def vision(q: str = "Que vois-tu sur l'ecran ?"):
    return {"result": see_screen(q)}

@app.get("/api/memory")
def memory(q: str = ""):
    return {"result": recall(q)}

@app.get("/api/iphone/queue")
def iphone_queue():
    qpath = os.path.join(os.path.dirname(__file__), "..", "config", "iphone_queue.json")
    try:
        with open(qpath, encoding="utf-8") as f:
            q = json.load(f)
        # vide après lecture
        with open(qpath, "w", encoding="utf-8") as f:
            json.dump([], f)
        return {"commands": q}
    except:
        return {"commands": []}

@app.get("/api/profile")
def profile(set: str = None):
    if set:
        return {"result": set_current(set), "profile": get_current()}
    return {"profile": get_current(), "available": list_profiles(), "corrections": len(load_corr()), "reminders": 0}

@app.get("/api/plugins")
def plugins():
    return {"plugins": list_plugins()}

@app.get("/api/watches")
def watches():
    return {"watches": list_watches().split("\n") if list_watches()!="Aucune veille" else []}

@app.get("/api/logs")
def logs():
    import os
    p = os.path.join(os.path.dirname(__file__), "..", "config", "sara_memory.json")
    if os.path.exists(p):
        return open(p, encoding="utf-8").read()[-8000:]
    return "Pas de logs"

@app.get("/api/status")
def status():
    try:
        import psutil
        return {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "disk": psutil.disk_usage("/").percent, "glasses": "M01 Pro_F444 connecte (index 2)"}
    except Exception as e:
        return {"error": str(e)}

# Serve PWA
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
app.mount("/dashboard", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="dashboard")

@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))

@app.get("/dashboard")
def dashboard():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "dashboard.html"))
