"""Coffre-fort JARVIS - mots de passes chiffres via Windows Credential Manager (keyring).
Tout reste LOCAL et chiffre par l'OS."""
import os, json, secrets, string

SERVICE = "jarvis-vault"
INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "vault_index.json")

def _load_index():
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_index(idx):
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)

def vault_set(site: str, username: str, password: str, url: str = "") -> str:
    import keyring
    key = site.lower().strip()
    keyring.set_password(SERVICE, key, json.dumps({"username": username, "password": password, "url": url}))
    idx = _load_index()
    idx[key] = {"site": site, "username": username, "url": url}
    _save_index(idx)
    return f"[Coffre] {site} enregistre (utilisateur: {username})."

def vault_get(site: str) -> str:
    import keyring
    key = site.lower().strip()
    raw = keyring.get_password(SERVICE, key)
    if not raw:
        return f"NOT_FOUND:{site}"
    return json.dumps(json.loads(raw))

def vault_list() -> str:
    idx = _load_index()
    if not idx:
        return "Coffre vide."
    return "\n".join(f"- {v['site']} ({v['username']})" for v in idx.values())

def vault_delete(site: str) -> str:
    import keyring
    key = site.lower().strip()
    try:
        keyring.delete_password(SERVICE, key)
    except Exception:
        pass
    idx = _load_index()
    idx.pop(key, None)
    _save_index(idx)
    return f"[Coffre] {site} supprime."

def _gen_password(length=16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(length))

def auto_login(site: str) -> str:
    """Ouvre le site et se connecte avec les identifiants du coffre - version robuste"""
    d = vault_get(site)
    if d.startswith("NOT_FOUND"):
        return f"PAS_DANS_COFFRE:{site}"
    creds = json.loads(d)
    url = creds.get("url") or f"https://{site}"
    user = creds.get("username") or ""
    pwd = creds.get("password") or ""
    if not pwd:
        import subprocess
        for bp in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]:
            if os.path.exists(bp):
                subprocess.Popen([bp, url]); break
        return f"{site} ouvert avec ton profil."

    # Cas special Omnivox Cegpetr - page avec No de matricule + Mot de passe
    is_omnivox = "omnivox" in site.lower() or "omnivox" in url.lower()
    try:
        from playwright.sync_api import sync_playwright
        import time
        # Utilise le VRAI profil Chrome si possible, sinon profil JARVIS
        real_profile = os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data")
        jarvis_profile = os.path.expandvars(r"%LocalAppData%\JARVIS_browser_profile")
        # Si Chrome tourne deja, on ne peut pas locker le profil reel -> utilise JARVIS profil + remplit
        profile_to_use = jarvis_profile
        # Tente d'abord avec le navigateur deja ouvert via pyautogui si omnivox
        if is_omnivox:
            # Ouvre avec le vrai Chrome (nouvel onglet)
            import subprocess
            for bp in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                       r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]:
                if os.path.exists(bp):
                    try:
                        subprocess.Popen([bp, url])
                    except Exception:
                        pass
                    break
            time.sleep(4)
            # Remplit via pyautogui sur la fenetre active (plus fiable pour Omnivox)
            try:
                import pyautogui
                # Attend que la page charge, puis tab jusqu'au champ matricule
                time.sleep(2)
                # Methode 1: Playwright sur le profil JARVIS en parallele pour remplir proprement
                with sync_playwright() as p:
                    ctx = p.chromium.launch_persistent_context(jarvis_profile, headless=False)
                    page = ctx.pages[0] if ctx.pages else ctx.new_page()
                    page.goto(url, timeout=30000)
                    page.wait_for_timeout(3000)
                    # Omnivox: le premier input texte est No de matricule
                    # On essaie plusieurs selecteurs specifiques
                    filled_user = False
                    for sel in ["input[placeholder*='0000000']", "input[name*='Matricule' i]", "input[name*='matricule' i]", "input[type='text']"]:
                        try:
                            loc = page.locator(sel).first
                            if loc.count() > 0 and loc.is_visible():
                                loc.click(timeout=2000)
                                loc.fill("", timeout=2000)
                                loc.fill(user, timeout=3000)
                                filled_user = True
                                break
                        except Exception:
                            continue
                    if not filled_user:
                        page.locator("input[type='text']").first.fill(user)
                    # Mot de passe
                    page.locator("input[type='password']").first.fill(pwd)
                    page.wait_for_timeout(1000)
                    # Clique Connexion
                    for sel in ["button:has-text('Connexion')", "button[type='submit']", "input[type='submit']"]:
                        try:
                            page.locator(sel).first.click(timeout=3000)
                            break
                        except Exception:
                            continue
                    else:
                        page.keyboard.press("Enter")
                    page.wait_for_timeout(5000)
                    # Verifie si connecte (plus de champ matricule)
                    try:
                        still_login = page.locator("input[placeholder*='0000000']").count() > 0 and page.locator("input[placeholder*='0000000']").first.is_visible()
                        if still_login:
                            return f"Omnivox: champs remplis mais toujours sur login - verifie DA/mdp dans le coffre ({user}). Page restee ouverte pour verification."
                    except Exception:
                        pass
                    return f"Connecte a Omnivox ({user}). Page chargee, pret pour recap MIO. Dis 'lis l ecran' si besoin."
            except Exception as e:
                return f"Omnivox ouvert sur {url} - remplissage Playwright echoue ({e}). Essaie de remplir manuellement: DA {user}."
        # Cas general non-Omnivox
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(profile_to_use, headless=False)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(url if url.startswith("http") else "https://" + url, timeout=30000)
            page.wait_for_timeout(2000)
            page.locator("input[type='text'], input[type='email']").first.fill(user)
            page.locator("input[type='password']").first.fill(pwd)
            try:
                page.locator("button:has-text('Connexion'), button:has-text('Se connecter'), button[type='submit']").first.click(timeout=3000)
            except Exception:
                page.keyboard.press("Enter")
            page.wait_for_timeout(3000)
            return f"Connecte a {site}. Navigateur ouvert."
    except Exception as e:
        import subprocess
        for bp in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]:
            if os.path.exists(bp):
                subprocess.Popen([bp, url]); break
        return f"Site ouvert: {url}. Auto-login echoue ({e})."

def register_account(site: str, url: str = "") -> str:
    """Cree un compte avec miguelfreddy65@gmail.com, mot de passe genere, sauvegarde coffre"""
    email = "miguelfreddy65@gmail.com"
    password = _gen_password()
    target = url or f"https://{site}"
    vault_set(site, email, password, target)
    try:
        from playwright.sync_api import sync_playwright
        profile_dir = os.path.expandvars(r"%LocalAppData%\JARVIS_browser_profile")
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(profile_dir, headless=False)
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(target if target.startswith("http") else "https://" + target, timeout=30000)
            page.wait_for_timeout(2000)
            for sel in ["a:has-text('Inscription')", "a:has-text('inscrire')", "a:has-text('Sign up')", "a:has-text('Créer un compte')", "a:has-text('Register')"]:
                try:
                    page.locator(sel).first.click(timeout=2000)
                    page.wait_for_timeout(2000)
                    break
                except Exception:
                    continue
            try:
                page.locator("input[type=email], input[name*=mail]").first.fill(email, timeout=3000)
            except Exception: pass
            pw_fields = page.locator("input[type=password]")
            n = pw_fields.count()
            for i in range(min(n, 2)):
                pw_fields.nth(i).fill(password)
            try:
                page.locator("input[name*=nom i], input[name*=name i], input[placeholder*=om i]").first.fill("Miguel", timeout=1500)
            except Exception: pass
            return (f"Formulaire {site} pre-rempli (email {email}, mdp genere + SAUVEGARDE coffre). "
                    f"Confirme l'inscription (CAPTCHA/CGU souvent requis) puis dis 'enregistre {site}'.")
    except Exception as e:
        return f"Inscription auto impossible ({e}). Identifiants deja dans le coffre: {site} / {email} / mdp genere."

def save_pin(nip: str, label: str = "nip-personnel") -> str:
    return vault_set(label, "nip", nip)

def init_default_vault():
    vault_set("gmail", "miguelfreddy65@gmail.com", "", "https://mail.google.com")
    vault_set("omnivox", "miguelfreddy65@gmail.com", "", "https://cegeptr.omnivox.ca/intr/")
