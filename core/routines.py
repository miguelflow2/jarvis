import os, json, threading, time, datetime

WATCHES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "watches.json")
ROUTINES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "routines.json")

def load_watches():
    if os.path.exists(WATCHES_PATH):
        with open(WATCHES_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []

def add_watch(url: str, keyword: str, limit: str = "") -> str:
    watches = load_watches()
    watches.append({"url": url, "keyword": keyword, "limit": limit, "last": ""})
    os.makedirs(os.path.dirname(WATCHES_PATH), exist_ok=True)
    with open(WATCHES_PATH, "w", encoding="utf-8") as f:
        json.dump(watches, f, indent=2)
    return f"Veille ajoutee: {url} si contient '{keyword}' {limit}"

def list_watches() -> str:
    w = load_watches()
    if not w: return "Aucune veille"
    return "\n".join(f"- {x['url']} ({x['keyword']})" for x in w)

def load_routines():
    if os.path.exists(ROUTINES_PATH):
        with open(ROUTINES_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []

def add_routine(cron: str, action: str) -> str:
    """cron = 'lundi 08:00' ou 'chaque jour 08:00' """
    routines = load_routines()
    routines.append({"cron": cron, "action": action})
    os.makedirs(os.path.dirname(ROUTINES_PATH), exist_ok=True)
    with open(ROUTINES_PATH, "w", encoding="utf-8") as f:
        json.dump(routines, f, indent=2)
    return f"Routine ajoutee: {cron} -> {action}"

def list_routines() -> str:
    r = load_routines()
    if not r: return "Aucune routine"
    return "\n".join(f"- {x['cron']}: {x['action']}" for x in r)

def _watch_loop():
    from core.voice import speak
    from hyperdb import remember_hyper
    while True:
        time.sleep(600)  # 10 min
        for w in load_watches():
            try:
                import requests
                r = requests.get(w["url"], timeout=15, headers={"User-Agent":"JARVIS"})
                txt = r.text.lower()
                if w["keyword"].lower() in txt:
                    # check prix si limite
                    if w["limit"] and "€" in w["limit"]:
                        try:
                            import re
                            prices = re.findall(r"(\d+[.,]\d+)\s*€", r.text)
                            if prices:
                                p = float(prices[0].replace(",","."))
                                lim = float(w["limit"].replace("€","").replace(",",".").strip())
                                if p < lim:
                                    speak(f"Veille prix: {w['url']} est a {p} euros, sous {lim} !")
                                    remember_hyper(f"Veille declenchee {w['url']} prix {p}", source="watch")
                                    continue
                        except Exception: pass
                    speak(f"Veille: {w['keyword']} trouve sur {w['url']}")
                w["last"] = datetime.datetime.now().isoformat()
            except Exception:
                pass

def _routine_loop():
    from core.brain import JarvisBrain
    while True:
        now = datetime.datetime.now()
        jours = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
        cur = f"{jours[now.weekday()]} {now.strftime('%H:%M')}"
        chaque = f"chaque jour {now.strftime('%H:%M')}"
        for r in load_routines():
            if r["cron"].lower() in [cur.lower(), chaque.lower()]:
                try:
                    brain = JarvisBrain()
                    ans = brain.ask(r["action"])
                    from core.voice import speak
                    speak(ans)
                except Exception:
                    pass
        time.sleep(60)

def start_routines():
    threading.Thread(target=_watch_loop, daemon=True).start()
    threading.Thread(target=_routine_loop, daemon=True).start()
