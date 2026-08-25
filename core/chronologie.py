"""Conscience contextuelle - screenshots toutes les 5s + OCR + indexation"""
import os, time, threading, datetime, glob

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "timeline")
INTERVAL = 5  # secondes

def _capture_once():
    try:
        import pyautogui, pytesseract
        from PIL import Image
        os.makedirs(CAPTURE_DIR, exist_ok=True)
        ts = datetime.datetime.now()
        img = pyautogui.screenshot()
        # miniature
        small = img.resize((640, 360))
        path = os.path.join(CAPTURE_DIR, ts.strftime("%Y%m%d_%H%M%S.png"))
        small.save(path, "PNG", optimize=True)
        # OCR
        try:
            txt = pytesseract.image_to_string(small, lang="fra")
            if not txt.strip():
                txt = pytesseract.image_to_string(small)
        except Exception:
            txt = ""
        # indexe dans HyperDB
        if txt.strip() and len(txt.strip()) > 20:
            try:
                from hyperdb import remember_hyper
                remember_hyper(f"[Timeline {ts.strftime('%Y-%m-%d %H:%M:%S')}] {txt[:600]}", source="timeline")
            except Exception:
                pass
        # garde seulement 3 jours
        for f in glob.glob(os.path.join(CAPTURE_DIR, "*.png")):
            if os.path.getmtime(f) < time.time() - 3*24*3600:
                try: os.remove(f)
                except Exception: pass
    except Exception as e:
        print(f"[Timeline] {e}")

def timeline_loop():
    while True:
        _capture_once()
        time.sleep(INTERVAL)

def start_timeline():
    t = threading.Thread(target=timeline_loop, daemon=True)
    t.start()
    return f"Timeline active: capture toutes les {INTERVAL}s dans config/timeline/"

def search_timeline(query: str) -> str:
    """Recherche dans la timeline: 't-shirt bleu mardi 14h'"""
    from hyperdb import recall_hyper
    return recall_hyper(f"[Timeline] {query}", top_k=8)

def get_timeline_stats() -> str:
    count = len(glob.glob(os.path.join(CAPTURE_DIR, "*.png")))
    return f"Timeline: {count} captures (3 jours), intervalle {INTERVAL}s"
