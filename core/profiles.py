import os, json
PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "profiles")
CURRENT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "current_profile.json")

def list_profiles():
    os.makedirs(PROFILES_DIR, exist_ok=True)
    profs = [d for d in os.listdir(PROFILES_DIR) if os.path.isdir(os.path.join(PROFILES_DIR, d))]
    if not profs:
        # cree defaut
        for p in ["perso","travail"]:
            os.makedirs(os.path.join(PROFILES_DIR, p), exist_ok=True)
            with open(os.path.join(PROFILES_DIR, p, "config.json"), "w", encoding="utf-8") as f:
                json.dump({"name":p, "voice":"fr-FR-DeniseNeural" if p=="perso" else "fr-FR-HenriNeural"}, f, indent=2)
        profs = ["perso","travail"]
    return profs

def get_current():
    if os.path.exists(CURRENT_PATH):
        with open(CURRENT_PATH, encoding="utf-8") as f:
            return json.load(f).get("profile","perso")
    return "perso"

def set_current(name: str) -> str:
    name = name.lower().strip()
    if name not in list_profiles():
        return f"Profil {name} inexistant. Dispo: {', '.join(list_profiles())}"
    with open(CURRENT_PATH, "w", encoding="utf-8") as f:
        json.dump({"profile": name}, f)
    return f"Profil bascule sur '{name}'. Memoire et voix adaptees."

def get_profile_db(profile: str) -> str:
    return os.path.join(PROFILES_DIR, profile, "hyper.db")

def get_profile_memory(profile: str) -> str:
    return os.path.join(PROFILES_DIR, profile, "memory.json")
