"""Productivite JARVIS: rappels, emails, traduction, notes, automatisations contexte"""
import os, json, datetime, threading, time

REMINDERS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "reminders.json")

def _load_reminders():
    if os.path.exists(REMINDERS_PATH):
        with open(REMINDERS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_reminders(r):
    os.makedirs(os.path.dirname(REMINDERS_PATH), exist_ok=True)
    with open(REMINDERS_PATH, "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)

def add_reminder(text: str, when: str = "") -> str:
    """Ajoute un rappel. when = 'HH:MM' ou '2026-08-25 14:30' ou vide = dans 1h"""
    reminders = _load_reminders()
    now = datetime.datetime.now()
    if when:
        try:
            if len(when) == 5:  # HH:MM
                h, m = map(int, when.split(":"))
                dt = now.replace(hour=h, minute=m, second=0)
                if dt < now: dt += datetime.timedelta(days=1)
            else:
                dt = datetime.datetime.fromisoformat(when)
        except Exception:
            dt = now + datetime.timedelta(hours=1)
    else:
        dt = now + datetime.timedelta(hours=1)
    reminders.append({"text": text, "when": dt.isoformat(), "said": False})
    _save_reminders(reminders)
    return f"Rappel enregistre: '{text}' a {dt.strftime('%H:%M')}."

def list_reminders() -> str:
    reminders = [r for r in _load_reminders() if not r["said"]]
    if not reminders:
        return "Aucun rappel en attente."
    return "Rappels en attente:\n" + "\n".join(
        f"- {r['text']} ({datetime.datetime.fromisoformat(r['when']).strftime('%d/%m %H:%M')})" for r in reminders)

def _reminder_loop():
    from core.voice import speak
    while True:
        now = datetime.datetime.now()
        reminders = _load_reminders()
        changed = False
        for r in reminders:
            if not r["said"] and datetime.datetime.fromisoformat(r["when"]) <= now:
                speak(f"Rappel: {r['text']}")
                r["said"] = True
                changed = True
        if changed:
            _save_reminders(reminders)
        time.sleep(30)

def start_reminders():
    threading.Thread(target=_reminder_loop, daemon=True).start()

def read_emails(max_emails: int = 5) -> str:
    """Lit les emails non lus Gmail (IMAP, necessite GMAIL_APP_PASSWORD dans .env)"""
    pwd = os.getenv("GMAIL_APP_PASSWORD")
    user = os.getenv("GMAIL_USER", "miguelfreddy65@gmail.com")
    if not pwd:
        import webbrowser
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
        return "Mot de passe app Gmail non configure - boite ouverte dans Chrome. Pour lecture auto: cree un mot de passe app sur myaccount.google.com/apppasswords puis ajoute GMAIL_APP_PASSWORD dans .env"
    try:
        import imaplib, email
        from email.header import decode_header
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pwd)
        mail.select("inbox")
        _, data = mail.search(None, "UNSEEN")
        ids = data[0].split()[-max_emails:]
        if not ids:
            return "Aucun email non lu. Boite a jour."
        out = []
        for i in ids:
            _, msg_data = mail.fetch(i, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            subj = decode_header(msg["Subject"] or "")[0][0]
            if isinstance(subj, bytes): subj = subj.decode(errors="ignore")
            frm = decode_header(msg["From"])[0][0]
            if isinstance(frm, bytes): frm = frm.decode(errors="ignore")
            out.append(f"- De {frm}: {subj}")
        mail.logout()
        return f"{len(out)} emails non lus:\n" + "\n".join(out)
    except Exception as e:
        return f"Erreur lecture emails: {e}"

def translate_text(text: str, target_lang: str = "anglais") -> str:
    """Traduction via le cerveau LLM"""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY")
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        r = client.chat.completions.create(
            model="openai/gpt-4o-mini", max_tokens=1000,
            messages=[{"role":"user","content":f"Traduis en {target_lang}, reponds UNIQUEMENT avec la traduction: {text}"}])
        return r.choices[0].message.content
    except Exception as e:
        return f"Erreur traduction: {e}"

def voice_note(text: str) -> str:
    """Note vocale transcree -> fichier + memoire"""
    from hyperdb import remember_hyper
    path = os.path.expanduser("~/Desktop/SARA_notes.txt")
    ts = datetime.datetime.now().strftime("%d/%m %H:%M")
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {text}\n")
    remember_hyper(f"Note vocale: {text}", source="note")
    return f"Note sauvegardee sur le Bureau et en memoire: {text}"

def context_automation(phrase: str) -> str:
    """Automatisations declenchees par contexte"""
    low = phrase.lower()
    if any(x in low for x in ["je sors", "je pars", "j'y vais"]):
        from tools.system import open_application
        open_application("chrome")
        from tools.web import open_website
        open_website("https://www.google.com/maps")
        from tools.system import set_volume
        set_volume(70)
        return "Mode sortie active: Maps ouvert, volume 70%. Bonne route !"
    if any(x in low for x in ["je rentre", "je suis rentre", "je suis la"]):
        from tools.system import set_volume
        set_volume(40)
        return "Mode maison active. Bienvenue !"
    if any(x in low for x in ["mode travail", "au travail", "je bosse"]):
        from tools.system import close_all_windows
        close_all_windows()
        from tools.system import open_application
        open_application("code")
        return "Mode travail: bureau nettoye, VS Code ouvert."
    if any(x in low for x in ["mode nuit", "bonne nuit", "je vais dormir"]):
        from tools.system import set_volume
        set_volume(10)
        return "Mode nuit: volume au minimum. Bonne nuit !"
    return ""

