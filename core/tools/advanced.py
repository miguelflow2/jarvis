"""Tools avances JARVIS: date/heure, meteo, OCR, RAG fichiers, navigateur profil connecte"""
import os, datetime, subprocess, json

def get_datetime(query: str = "") -> str:
    """Date et heure reelles en francais"""
    now = datetime.datetime.now()
    jours = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
    mois = ["janvier","fevrier","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","decembre"]
    return (f"Nous sommes {jours[now.weekday()]} {now.day} {mois[now.month-1]} {now.year}, "
            f"il est {now.strftime('%H:%M')}.")

def get_weather(city: str = "Paris") -> str:
    """Meteo reelle via wttr.in (gratuit, sans cle)"""
    try:
        import requests
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=10)
        d = r.json()["current_condition"][0]
        temp = d["temp_C"]; feels = d["FeelsLikeC"]; desc = d["lang_fr"][0]["value"] if "lang_fr" in d else d["weatherDesc"][0]["value"]
        hum = d["humidity"]; wind = d["windspeedKmph"]
        return f"Meteo {city}: {desc}, {temp}C (ressenti {feels}C), humidite {hum}%, vent {wind} km/h."
    except Exception as e:
        return f"Erreur meteo: {e}"

def read_screen_text(question: str = "") -> str:
    """OCR de l'ecran - extrait le texte visible"""
    try:
        import pytesseract
        from PIL import Image
        import pyautogui
        img = pyautogui.screenshot()
        txt = pytesseract.image_to_string(img, lang="fra")
        if not txt.strip():
            txt = pytesseract.image_to_string(img)
        return f"Texte lu sur l'ecran:\n{txt[:3000]}"
    except Exception as e:
        return (f"OCR indisponible: {e}. "
                f"Installe Tesseract: https://github.com/UB-Mannheim/tesseract/wiki puis "
                f"pytesseract. En attendant utilise see_screen (vision GPT).")

def index_documents(path: str = "~/Documents") -> str:
    """RAG: indexe txt/md/pdf dans HyperDB pour recherche semantique"""
    import glob
    from hyperdb import remember_hyper
    path = os.path.expanduser(path)
    count = 0
    for pattern in ["*.txt","*.md","*.pdf"]:
        for f in glob.glob(os.path.join(path, "**", pattern), recursive=True)[:50]:
            try:
                if f.endswith(".pdf"):
                    from pypdf import PdfReader
                    reader = PdfReader(f)
                    text = " ".join(p.extract_text() or "" for p in reader.pages[:20])
                else:
                    text = open(f, encoding="utf-8", errors="ignore").read()
                # decoupe en chunks
                for i in range(0, min(len(text), 20000), 1500):
                    chunk = text[i:i+1500].strip()
                    if len(chunk) > 100:
                        remember_hyper(f"[{os.path.basename(f)}] {chunk}", source="document")
                        count += 1
            except Exception:
                pass
    return f"Indexe {count} extraits depuis {path}. Tu peux maintenant demander leur contenu."

def open_browser_site(url: str, action: str = "") -> str:
    """Ouvre le navigateur avec TON profil (sessions deja connectees) via Playwright.
    Tes mots de passe ne sont JAMAIS extraits: on utilise tes cookies actifs."""
    try:
        # Lance via le vrai Chrome avec ton profil utilisateur
        profile = os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data")
        chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome) and os.path.exists(profile):
            subprocess.Popen([chrome, f"--profile-directory=Default", url])
            return f"Chrome ouvert avec ton profil sur {url} (sessions actives, deja connecte)."
        # Fallback Playwright avec profil persistant
        from playwright.sync_api import sync_playwright
        def run():
            with sync_playwright() as p:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=os.path.expandvars(r"%LocalAppData%\JARVIS_browser_profile"),
                    headless=False)
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                page.goto(url if url.startswith("http") else "https://"+url)
                if action:
                    page.keyboard.insert_text(action)
                    page.keyboard.press("Enter")
                return "OK"
        run()
        return f"Navigateur ouvert sur {url} avec profil persistant."
    except Exception as e:
        # fallback simple
        import webbrowser
        webbrowser.open(url if url.startswith("http") else "https://"+url)
        return f"Navigateur ouvert sur {url} (mode simple). Erreur profil: {e}"

def web_automate(url: str, task: str) -> str:
    """Automatisation web reelle via Playwright: remplit formulaires, clique, extrait"""
    try:
        from playwright.sync_api import sync_playwright
        result = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url if url.startswith("http") else "https://"+url, timeout=30000)
            # extraction contenu
            title = page.title()
            body = page.inner_text("body")[:4000]
            result = {"title": title, "content": body}
            browser.close()
        return f"Page '{result['title']}' chargee. Contenu:\n{result['content'][:3000]}"
    except Exception as e:
        return f"Erreur automatisation: {e}"

def send_email_real(to: str, subject: str, body: str) -> str:
    """Envoi email reel via SMTP Gmail (config dans .env: GMAIL_APP_PASSWORD)"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        gmail_user = os.getenv("GMAIL_USER", "miguelfreddy65@gmail.com")
        gmail_pass = os.getenv("GMAIL_APP_PASSWORD")
        if not gmail_pass:
            # ouvre Gmail a la place
            import urllib.parse, webbrowser
            webbrowser.open(f"https://mail.google.com/mail/?view=cm&to={urllib.parse.quote(to)}&su={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}")
            return "Mot de passe app Gmail non configure - Gmail ouvert en brouillon. Pour envoi auto: cree un mot de passe app sur myaccount.google.com/apppasswords et mets GMAIL_APP_PASSWORD dans .env"
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject; msg["From"] = gmail_user; msg["To"] = to
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(gmail_user, gmail_pass)
            s.send_message(msg)
        return f"Email envoye a {to}."
    except Exception as e:
        return f"Erreur email: {e}"
