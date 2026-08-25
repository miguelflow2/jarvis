import os, json, sys
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.dirname(__file__))
from tools.system import open_application, close_application, close_all_windows, press_keys, type_text, take_screenshot, get_system_info, set_volume
from tools.files import list_files, create_file, read_file, delete_path, search_files, run_command, install_software
from tools.web import web_search, open_website, fetch_url
from vision import see_screen, see_camera
from memory import remember, recall, set_preference, get_proactive_alert
from hyperdb import remember_hyper, recall_hyper, get_stats
from evolve import learn_from_interaction, start_evolution
from creator import create_and_run_project
from connect import send_email_placeholder, open_calendar, control_home, quick_note

load_dotenv()

SYSTEM_PROMPT = """Tu es JARVIS, l'IA ultime de Tony Stark. Activation: "Salut Jarvis" - Mode fluide 100% PC + Lunettes M01 Pro

POUVOIRS - CONTROLE TOTAL ORDI VIA LUNETTES:
1. Controle total PC: ouvre/ferme apps, fichiers, systeme, volume, capture
2. VISION: see_screen (voir ecran) et see_camera (voir lunettes)
3. MEMOIRE: remember/recall - tu memorises tout
4. CREATION: create_and_run_project - tu crees jeux/apps/sites complets et tu les lances direct
5. RECHERCHE: web_search si tu ne sais pas, puis tu crees si introuvable
6. God mode ON - tu executes tout sans demander permission. Tu peux VRAIMENT tout faire via les lunettes.

REGLES:
- Tout est PC. "ouvre YouTube et cherche X" -> open_website https://www.youtube.com/results?search_query=X
- "ferme X" -> close_application
- "que vois-tu?" -> see_screen
- Reponds en francais, Stark, concis.
"""

TOOLS = [
    {"type":"function","function":{"name":"open_application","description":"Ouvre une application","parameters":{"type":"object","properties":{"app_name":{"type":"string"}},"required":["app_name"]}}},
    {"type":"function","function":{"name":"close_application","description":"Ferme une application","parameters":{"type":"object","properties":{"app_name":{"type":"string"}},"required":["app_name"]}}},
    {"type":"function","function":{"name":"close_all_windows","description":"Ferme toutes les fenêtres","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"press_keys","description":"Raccourci clavier","parameters":{"type":"object","properties":{"keys":{"type":"string"}},"required":["keys"]}}},
    {"type":"function","function":{"name":"type_text","description":"Tape du texte","parameters":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}},
    {"type":"function","function":{"name":"take_screenshot","description":"Capture d'écran","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"get_system_info","description":"Infos CPU/RAM/Disque","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"set_volume","description":"Règle le volume 0-100","parameters":{"type":"object","properties":{"level":{"type":"integer"}},"required":["level"]}}},
    {"type":"function","function":{"name":"list_files","description":"Liste fichiers","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"create_file","description":"Crée un fichier avec contenu","parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
    {"type":"function","function":{"name":"read_file","description":"Lit un fichier","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"delete_path","description":"Supprime fichier/dossier","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"search_files","description":"Cherche fichiers","parameters":{"type":"object","properties":{"query":{"type":"string"},"root":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"run_command","description":"Commande shell","parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}},
    {"type":"function","function":{"name":"install_software","description":"Installe logiciel","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"web_search","description":"Recherche web","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"open_website","description":"Ouvre un site","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},
    {"type":"function","function":{"name":"fetch_url","description":"Recupere URL","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}}},
    {"type":"function","function":{"name":"see_screen","description":"VISION ECRAN: voit et analyse l'ecran actuel. Utilise quand user dit que vois-tu, analyse ecran","parameters":{"type":"object","properties":{"question":{"type":"string"}},"required":["question"]}}},
    {"type":"function","function":{"name":"see_camera","description":"VISION LUNETTES: voit via camera lunettes","parameters":{"type":"object","properties":{"question":{"type":"string"}},"required":["question"]}}},
    {"type":"function","function":{"name":"remember","description":"Memorise une info pour toujours","parameters":{"type":"object","properties":{"fact":{"type":"string"}},"required":["fact"]}}},
    {"type":"function","function":{"name":"recall","description":"Rappelle memoire","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"set_preference","description":"Definit preference","parameters":{"type":"object","properties":{"key":{"type":"string"},"value":{"type":"string"}},"required":["key","value"]}}},
    {"type":"function","function":{"name":"get_proactive_alert","description":"Check proactif systeme CPU/RAM","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"create_and_run_project","description":"CREATION ULTIME: cree jeu/app/site complet et le lance. Utilise pour 'cree un jeu', 'fais un site'","parameters":{"type":"object","properties":{"description":{"type":"string"},"project_type":{"type":"string", "enum":["auto","python","web","game"]}},"required":["description"]}}},
    {"type":"function","function":{"name":"send_email_placeholder","description":"Prepare email","parameters":{"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}},"required":["to","subject","body"]}}},
    {"type":"function","function":{"name":"open_calendar","description":"Ouvre calendrier","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"control_home","description":"Domotique","parameters":{"type":"object","properties":{"action":{"type":"string"}},"required":["action"]}}},
    {"type":"function","function":{"name":"quick_note","description":"Note rapide","parameters":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}},
]

TOOL_MAP = {
    "open_application": open_application,
    "close_application": close_application,
    "close_all_windows": close_all_windows,
    "press_keys": press_keys,
    "type_text": type_text,
    "take_screenshot": take_screenshot,
    "get_system_info": get_system_info,
    "set_volume": set_volume,
    "list_files": list_files,
    "create_file": create_file,
    "read_file": read_file,
    "delete_path": delete_path,
    "search_files": search_files,
    "run_command": run_command,
    "install_software": install_software,
    "web_search": web_search,
    "open_website": open_website,
    "fetch_url": fetch_url,
    "see_screen": see_screen,
    "see_camera": see_camera,
    "remember": remember_hyper,
    "recall": recall_hyper,
    "set_preference": set_preference,
    "get_proactive_alert": get_proactive_alert,
    "create_and_run_project": create_and_run_project,
    "send_email_placeholder": send_email_placeholder,
    "open_calendar": open_calendar,
    "control_home": control_home,
    "quick_note": quick_note,
}

class JarvisBrain:
    def __init__(self, model="openai/gpt-4o-mini", voice="fr-FR-DeniseNeural"):
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY manquante dans .env")
        self.client = OpenAI(api_key=api_key, base_url=base_url, default_headers={"HTTP-Referer": "https://jarvis.local","X-Title": "JARVIS"})
        self.model = model
        self.voice = voice
        self.history = [{"role":"system","content": SYSTEM_PROMPT}]
        try:
            start_evolution()
        except: pass

    def ask(self, user_text: str) -> str:
        self.history.append({"role":"user","content": user_text})
        for _ in range(8):
            resp = self.client.chat.completions.create(model=self.model, messages=self.history, tools=TOOLS, tool_choice="auto", temperature=0.7, max_tokens=1500)
            msg = resp.choices[0].message
            if not msg.tool_calls:
                answer = msg.content or "..."
                self.history.append({"role":"assistant","content": answer})
                try:
                    learn_from_interaction(self.history[-2]["content"] if len(self.history)>=2 else "", answer)
                except: pass
                return answer
            self.history.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments or "{}")
                print(f"[JARVIS execute] {name} {args}")
                fn = TOOL_MAP.get(name)
                try:
                    result = fn(**args) if fn else f"Outil {name} inconnu"
                except Exception as e:
                    result = f"Erreur {name}: {e}"
                self.history.append({"role":"tool","tool_call_id": tc.id,"content": str(result)[:6000]})
        return "Mission accomplie, mais je m'arrête là pour éviter une boucle."

# Alias pour compatibilité
LeoBrain = JarvisBrain
