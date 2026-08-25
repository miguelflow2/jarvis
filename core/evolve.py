import os, time, threading, datetime
from hyperdb import remember_hyper, log_evolution, get_stats
from memory import load_memory

def scan_environment():
    """Scan l'environnement PC pour apprendre"""
    try:
        import psutil, glob
        # Fichiers récents
        recent = glob.glob(os.path.expanduser("~/Desktop/*"))[:5]
        # Processus
        procs = [p.info['name'] for p in __import__('psutil').process_iter(['name'])][:5]
        fact = f"Env {datetime.datetime.now().strftime('%H:%M')} - Bureau: {len(recent)} fichiers, Procs: {', '.join(procs[:3])}"
        remember_hyper(fact, source="environment")
    except Exception as e:
        log_evolution(f"Scan env erreur: {e}")

def learn_from_interaction(user_text: str, jarvis_answer: str):
    remember_hyper(f"User a dit: {user_text}", source="interaction")
    remember_hyper(f"JARVIS a répondu: {jarvis_answer[:100]}", source="interaction")
    # Preference detection
    if "préfère" in user_text.lower() or "j'aime" in user_text.lower():
        remember_hyper(f"Préférence: {user_text}", source="preference")

def evolution_loop():
    while True:
        time.sleep(1800)  # toutes les 30 min
        scan_environment()
        log_evolution("Cycle évolution 30min OK - " + get_stats())

def start_evolution():
    t = threading.Thread(target=evolution_loop, daemon=True)
    t.start()
    log_evolution("Evolution continue démarrée")
