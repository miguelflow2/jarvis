import os, json
CORR_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "corrections.json")

def load_corr():
    if os.path.exists(CORR_PATH):
        with open(CORR_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_corr(d):
    with open(CORR_PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

def learn_correction(bad: str, good: str):
    """Apprend qu'on a mal compris bad -> good"""
    d = load_corr()
    d[bad.lower().strip()] = good.strip()
    save_corr(d)
    # aussi dans HyperDB
    try:
        from hyperdb import remember_hyper
        remember_hyper(f"Correction: ne plus comprendre '{bad}' comme avant, mais comme '{good}'", source="correction")
    except Exception:
        pass
    return f"Bien noté, je corrige '{bad}' -> '{good}' pour toujours."

def apply_corrections(text: str) -> str:
    d = load_corr()
    low = text.lower()
    for k, v in d.items():
        if k in low:
            text = text.replace(k, v)
    return text

def parse_correction(phrase: str):
    """Detecte 'non je voulais dire X' ou 'je voulais dire X' """
    low = phrase.lower()
    triggers = ["non je voulais dire", "je voulais dire", "non c'est", "je voulais que tu"]
    for t in triggers:
        if t in low:
            idx = low.find(t) + len(t)
            correction = phrase[idx:].strip(" :,-")
            # Essaie de retrouver ce qui etait mal compris (dernier echange)
            try:
                from hyperdb import recall_hyper
                # on ne peut pas savoir l'ancien, on stocke juste la correction comme alias
                return correction
            except Exception:
                return correction
    return None
