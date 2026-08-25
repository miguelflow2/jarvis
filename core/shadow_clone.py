"""Shadow Clone - navigateurs invisibles (headless) en arriere-plan"""
import os, threading

def shadow_task(url: str, task: str) -> str:
    """Lance un navigateur headless qui fait une tache en arriere-plan sans perturber l'utilisateur"""
    def run():
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url if url.startswith("http") else "https://"+url, timeout=30000)
                # Laisse l'IA decrire la tache
                from openai import OpenAI
                api_key = os.getenv("OPENROUTER_API_KEY")
                client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
                html = page.content()[:8000]
                r = client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[{"role":"user","content": f"Tache: {task}\nURL: {url}\nHTML:\n{html[:4000]}\nQue faire ensuite? Resume."}],
                    max_tokens=500)
                print(f"[Shadow] {r.choices[0].message.content}")
                browser.close()
        except Exception as e:
            print(f"[Shadow erreur] {e}")
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return f"Shadow Clone lance en arriere-plan sur {url} pour: {task}. Tu peux continuer a jouer/travailler."

def shadow_flight_search(origin: str, dest: str, date: str) -> str:
    return shadow_task(f"https://www.google.com/travel/flights?q=vols+{origin}+{dest}+{date}", f"trouve les 5 meilleurs billets {origin} -> {dest} le {date}, extrait prix et horaires")
