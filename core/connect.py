import os, json, webbrowser

def send_email_placeholder(to: str, subject: str, body: str) -> str:
    # Placeholder - ouvre Gmail compose
    try:
        url = f"https://mail.google.com/mail/?view=cm&to={to}&su={subject}&body={body}"
        webbrowser.open(url)
        return f"Gmail ouvert pour envoyer à {to}: {subject}. (Connecte ton SMTP pour envoi auto)"
    except Exception as e:
        return f"Erreur email: {e}"

def open_calendar() -> str:
    webbrowser.open("https://calendar.google.com")
    return "Calendrier ouvert."

def control_home(action: str) -> str:
    # Placeholder domotique - à connecter à Philips Hue / Tuya / Home Assistant
    actions = {
        "lumiere on": "Lumières allumées (simulé - connecte Home Assistant)",
        "lumiere off": "Lumières éteintes (simulé)",
        "musique": "Musique lancée"
    }
    return actions.get(action.lower(), f"Action domotique '{action}' simulée. Dis-moi ton système (Hue, Tuya, Home Assistant) pour brancher en vrai.")

def quick_note(text: str) -> str:
    path = os.path.join(os.path.expanduser("~/Desktop"), "SARA_notes.txt")
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    return f"Note ajoutée sur le Bureau: {text}"

def control_iphone(action: str, param: str = "") -> str:
    import json, os, datetime
    schemes = {
        "spotify": "spotify://",
        "youtube": "youtube://",
        "maps": f"maps://?q={param}" if param else "maps://",
        "phone": f"tel://{param}" if param else "tel://",
        "messages": f"sms://{param}" if param else "sms://",
        "settings": "App-prefs://",
        "camera": "camera://",
        "photos": "photos-redirect://",
        "music": "music://",
        "mail": "message://",
        "safari": f"https://{param}" if param else "https://www.google.com",
    }
    url = schemes.get(action.lower(), f"{action}://{param}")
    # Queue pour iPhone app (polling)
    try:
        qpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "iphone_queue.json")
        queue = []
        if os.path.exists(qpath):
            with open(qpath, encoding="utf-8") as f:
                queue = json.load(f)
        queue.append({"url": url, "action": action, "timestamp": datetime.datetime.now().isoformat()})
        queue = queue[-10:]
        with open(qpath, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
    except Exception as e:
        print(f"queue error {e}")
    return f"IPHONE_OPEN:{url}"
