"""Surveillance proactive + briefing matinal + auto-update"""
import os, time, threading, datetime

def _notify(title: str, msg: str):
    """Notification Windows native"""
    try:
        from win10toast import ToastNotifier
        ToastNotifier().show_toast(title, msg, duration=5, threaded=True)
    except:
        try:
            subprocess = __import__('subprocess')
            subprocess.Popen(['powershell','-Command',
                f'[windows.ui.notifications.toastnotificationmanager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null'], shell=True)
        except:
            print(f"[JARVIS notif] {title}: {msg}")

def watch_screen_changes():
    """Surveille: nouveaux fichiers Bureau/Downloads, RAM haute -> alerte vocale"""
    from core.voice import speak
    from core.memory import get_proactive_alert
    last_downloads = set()
    dl_path = os.path.expanduser("~/Downloads")
    if os.path.exists(dl_path):
        last_downloads = set(os.listdir(dl_path))
    while True:
        time.sleep(60)
        try:
            # Nouveau download
            if os.path.exists(dl_path):
                current = set(os.listdir(dl_path))
                new = current - last_downloads
                if new and not any(f.startswith("~") or f.endswith((".tmp",".crdownload",".part")) for f in new):
                    speak(f"Telechargement termine: {', '.join(list(new)[:2])}")
                last_downloads = current
            # RAM critique
            import psutil
            ram = psutil.virtual_memory().percent
            if ram > 92:
                speak(f"Attention, RAM a {ram} pourcent. Je peux fermer des applications si tu veux.")
                time.sleep(600)
        except Exception:
            pass

def morning_briefing() -> str:
    """Briefing complet: date + heure + meteo + systeme"""
    from tools.advanced import get_datetime, get_weather
    from core.memory import get_proactive_alert
    parts = [get_datetime(), get_weather("Paris"), get_proactive_alert()]
    return "Briefing du matin. " + " ".join(parts)

def briefing_loop():
    """Briefing automatique a 8h si le PC est allume"""
    from core.voice import speak
    from core.memory import load_memory
    said_today = None
    while True:
        now = datetime.datetime.now()
        if now.hour == 8 and now.minute < 5 and said_today != now.date():
            mem = load_memory()
            speak(morning_briefing())
            said_today = now.date()
        time.sleep(240)

def start_monitors():
    threading.Thread(target=watch_screen_changes, daemon=True).start()
    threading.Thread(target=briefing_loop, daemon=True).start()

def auto_update() -> str:
    """Se met a jour depuis GitHub"""
    try:
        import subprocess
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pull = subprocess.run(["git","pull"], cwd=base, capture_output=True, text=True, timeout=60)
        if "Already up to date" in pull.stdout or "deja a jour" in pull.stdout:
            return "Deja a la derniere version."
        return f"Mise a jour appliquee: {pull.stdout[:200]}. Redemarrage conseille."
    except Exception as e:
        return f"Erreur update: {e}"

def update_loop():
    while True:
        time.sleep(21600)  # 6h
        auto_update()
