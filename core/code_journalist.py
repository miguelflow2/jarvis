"""Journaliste de Code & Debugger temps reel - surveille logs et VS Code"""
import os, time, threading, subprocess, glob

WATCHED_LOGS = [os.path.expanduser("~/AppData/Roaming/Code/logs"), ".", os.path.join(os.path.dirname(os.path.dirname(__file__)), "app")]

def watch_logs():
    """Surveille les logs systeme et previent des erreurs"""
    # Implementation simple: surveille les fichiers .log recents
    while True:
        time.sleep(10)
        for pattern in ["*.log","*.err"]:
            for f in glob.glob(pattern):
                try:
                    if os.path.getmtime(f) > time.time() - 10:
                        txt = open(f, encoding="utf-8", errors="ignore").read()[-2000:]
                        if any(k in txt.lower() for k in ["error","exception","failed","traceback"]):
                            from core.voice import speak
                            speak(f"Erreur detectee dans {f}")
                except Exception:
                    pass

def debug_file(path: str) -> str:
    """Analyse un fichier et propose une correction"""
    try:
        content = open(os.path.expanduser(path), encoding="utf-8", errors="ignore").read()
        from openai import OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY")
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        r = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role":"system","content":"Tu es un expert debug. Analyse le code, trouve l'erreur et propose la correction exacte."},
                      {"role":"user","content": f"Fichier {path}:\n{content[:6000]}"}],
            max_tokens=1000)
        suggestion = r.choices[0].message.content
        # Ecrit la correction en .fix
        fix_path = path + ".jarvis_fix.py"
        open(os.path.expanduser(fix_path), "w", encoding="utf-8").write(suggestion)
        return f"Analyse de {path}: {suggestion[:1500]}"
    except Exception as e:
        return f"Erreur debug: {e}"

def start_code_watch():
    t = threading.Thread(target=watch_logs, daemon=True)
    t.start()
    return "Journaliste Code actif"

def intercept_terminal_error(log_path: str = "") -> str:
    """Lit le dernier log et explique l'erreur"""
    return debug_file(log_path or "app/server.py")
