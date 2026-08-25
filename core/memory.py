import os, json, datetime

MEM_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "sara_memory.json")

def load_memory():
    if not os.path.exists(MEM_PATH):
        return {"user": {}, "history": [], "preferences": {}, "projects": []}
    try:
        with open(MEM_PATH, encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"history": []}

def save_memory(mem):
    os.makedirs(os.path.dirname(MEM_PATH), exist_ok=True)
    with open(MEM_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2, ensure_ascii=False)

def remember(fact: str) -> str:
    mem = load_memory()
    mem["history"].append({"date": datetime.datetime.now().isoformat(), "fact": fact})
    # garde 200 derniers
    mem["history"] = mem["history"][-200:]
    save_memory(mem)
    return f"Mémorisé: {fact}"

def recall(query: str = "") -> str:
    mem = load_memory()
    if not mem["history"]:
        return "Aucun souvenir encore."
    if not query:
        last = mem["history"][-5:]
        return "Derniers souvenirs:\n" + "\n".join(f"- {h['fact']} ({h['date'][:10]})" for h in last)
    # recherche simple
    res = [h for h in mem["history"] if query.lower() in h["fact"].lower()]
    if not res:
        return f"Aucun souvenir pour '{query}'"
    return "\n".join(f"- {h['fact']}" for h in res[-10:])

def set_preference(key: str, value: str) -> str:
    mem = load_memory()
    mem["preferences"][key] = value
    save_memory(mem)
    return f"Préférence {key} = {value}"

def get_proactive_alert() -> str:
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        alerts = []
        if cpu > 85: alerts.append(f"CPU à {cpu}% - je peux fermer des apps")
        if ram > 90: alerts.append(f"RAM à {ram}% - besoin de libérer ?")
        if disk > 90: alerts.append(f"Disque à {disk}% - nettoyage conseillé")
        if alerts:
            return " | ".join(alerts)
        return "Système OK"
    except Exception as e:
        return f"Erreur check: {e}"
