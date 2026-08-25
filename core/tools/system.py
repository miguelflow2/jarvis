import subprocess
import psutil
import os
import pyautogui
import pygetwindow as gw
import webbrowser
from typing import Optional

pyautogui.FAILSAFE = False

def open_application(app_name: str) -> str:
    """Ouvre n'importe quelle application par son nom."""
    import webbrowser as wb
    low = app_name.lower().strip()
    # CAS CHROME - robuste Windows
    if low in ["chrome", "google chrome", "navigateur", "google"]:
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for p in paths:
            if os.path.exists(p):
                try:
                    subprocess.Popen([p, "https://www.google.com"])
                    return "Chrome ouvert."
                except: pass
        try:
            os.system('start "" "chrome" https://www.google.com')
            return "Chrome ouvert (via start)."
        except: pass
        try:
            wb.open("https://www.google.com")
            return "Chrome ouvert (via webbrowser)."
        except Exception as e:
            return f"Erreur Chrome: {e}"
    aliases = {
        "notepad": "notepad",
        "bloc-notes": "notepad",
        "bloc notes": "notepad",
        "spotify": 'start "" spotify',
        "vscode": "code",
        "code": "code",
    }
    cmd = aliases.get(low, app_name)
    try:
        subprocess.Popen(cmd, shell=True)
        return f"J'ouvre {app_name}."
    except Exception as e:
        try:
            os.system(f'start "" "{cmd}"')
            return f"J'ouvre {app_name} (via start)."
        except Exception as e2:
            return f"Erreur ouverture {app_name}: {e2}"

def close_application(app_name: str) -> str:
    """Ferme une application par son nom."""
    closed = 0
    for proc in psutil.process_iter(['name']):
        if app_name.lower() in proc.info['name'].lower():
            try:
                proc.terminate()
                closed += 1
            except: pass
    if closed > 0:
        return f"{app_name} fermé ({closed} processus)."
    # fallback fenêtre
    try:
        wins = gw.getWindowsWithTitle(app_name)
        for w in wins:
            w.close()
        if wins: return f"Fenêtre {app_name} fermée."
    except: pass
    return f"Aucun processus {app_name} trouvé."

def close_all_windows() -> str:
    try:
        wins = gw.getAllWindows()
        for w in wins:
            if w.title.strip() and w.visible:
                try: w.close()
                except: pass
        return "Toutes les fenêtres fermées."
    except Exception as e:
        return f"Erreur: {e}"

def press_keys(keys: str) -> str:
    """Simule des touches: ex 'win+r', 'alt+f4', 'ctrl+c'"""
    try:
        pyautogui.hotkey(*[k.strip() for k in keys.split('+')])
        return f"Raccourci {keys} exécuté."
    except Exception as e:
        return f"Erreur touche {keys}: {e}"

def type_text(text: str) -> str:
    pyautogui.write(text, interval=0.02)
    return f"Texte saisi."

def take_screenshot() -> str:
    path = os.path.expanduser("~/Desktop/jarvis_screenshot.png")
    pyautogui.screenshot(path)
    return f"Capture enregistrée: {path}"

def get_system_info() -> str:
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return f"CPU {cpu}% | RAM {ram}% | Disque {disk}%"

def set_volume(level: int) -> str:
    """level 0-100"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level/100, None)
        return f"Volume à {level}%."
    except:
        # fallback nircmd / touches
        for _ in range(5): pyautogui.press("volumedown")
        for _ in range(int(level/10)): pyautogui.press("volumeup")
        return f"Volume ajusté vers {level}% (fallback)."
