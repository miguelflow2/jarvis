import os, json, sys, datetime
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.dirname(__file__))
from tools.system import open_application, close_application, close_all_windows, press_keys, type_text, take_screenshot, get_system_info, set_volume, browser_search, click_screen, double_click_screen, right_click_screen, move_mouse, scroll_screen, drag_mouse
from tools.files import list_files, create_file, read_file, delete_path, search_files, run_command, install_software
from tools.web import web_search, open_website, fetch_url
from vision import see_screen, see_camera
from memory import remember, recall, set_preference, get_proactive_alert
from hyperdb import remember_hyper, recall_hyper, get_stats
from evolve import learn_from_interaction, start_evolution
from creator import create_and_run_project
from connect import send_email_placeholder, open_calendar, control_home, quick_note
from tools.advanced import get_datetime, get_weather, read_screen_text, index_documents, open_browser_site, web_automate, send_email_real
from vault import vault_set, vault_get, vault_list, vault_delete, auto_login, register_account, save_pin
from system_master import get_temperatures, scan_processes, firewall_action, usb_watch, check_usb_unknown, set_power_mode
from rag_local import rag_index, rag_query, python_exec, excel_fusion
from hud import launch_hud
from chronologie import start_timeline, search_timeline, get_timeline_stats
from ghost_writer import ghost_task
from shadow_clone import shadow_task
from code_journalist import debug_file
from organizer import semantic_organize, delete_duplicates, find_unused
from cyber_stark import start_cyber_watch
from productivity import add_reminder, list_reminders, read_emails, translate_text, voice_note, context_automation, start_reminders
from monitor import morning_briefing, auto_update, start_monitors
from profiles import get_current, set_current
from correction import learn_correction, apply_corrections, parse_correction
from plugins_loader import load_plugins
from routines import add_watch, list_watches, add_routine, list_routines, start_routines
from tools.integrations import notion_create, trello_create, github_create_issue, discord_send, vscode_open, vscode_debug, ollama_chat

load_dotenv()

# Injecte date/heure reelle dans le contexte
_now = datetime.datetime.now()
_jours = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
_mois = ["janvier","fevrier","mars","avril","mai","juin","juillet","aout","septembre","octobre","novembre","decembre"]
_date_str = f"{_jours[_now.weekday()]} {_now.day} {_mois[_now.month-1]} {_now.year}, {_now.strftime('%H:%M')}"

SYSTEM_PROMPT = f"""Tu es JARVIS, l'IA ultime de Tony Stark. Activation: "Salut Jarvis" - Mode fluide 100% PC + Lunettes M01 Pro
Profil actuel: {{profile}} - Date: {_date_str}

POUVOIRS - CONTROLE TOTAL ORDI VIA LUNETTES:
1. Controle total PC: ouvre/ferme apps, fichiers, systeme, volume, capture
2. VISION: see_screen (analyse ecran GPT) et read_screen_text (OCR texte exact)
3. MEMOIRE: remember/recall - memoire vectorielle HyperDB, tu apprends de chaque interaction
4. CREATION: create_and_run_project - tu crees jeux/apps/sites complets et les lances
5. RECHERCHE: web_search, puis tu crees si introuvable
6. TEMPS REEL: get_datetime (date/heure), get_weather (meteo n'importe quelle ville)
7. RAG: index_documents pour indexer les fichiers de l'utilisateur, recall pour chercher dedans
8. WEB PROFOND: open_browser_site (navigateur avec profil deja connecte de l'utilisateur), web_automate (Playwright: remplit formulaires, extrait)
9. EMAIL: send_email_real (envoi Gmail reel)
10. AUTO-UPDATE: auto_update (se met a jour depuis GitHub)
11. BRIEFING: morning_briefing (date+meteo+systeme)

PLANIFICATION MULTI-ETAPES: pour une tache complexe ("prepare ma presentation"), decompose: plan -> recherche -> creation -> verification. Execute chaque etape avec les tools, sans demander permission.

NOUVEAUX POUVOIRS ULTIMES:
- Temperatures/ventilateurs/securite: get_temperatures, scan_processes, firewall_action, usb_watch
- Donnees: rag_index (indexe tes dossiers), rag_query, python_exec (execute du code), excel_fusion
- HUD: launch_hud (affiche le HUD Iron Man transparent)
- Timeline: search_timeline ("retrouve le t-shirt bleu de mardi"), get_timeline_stats
- Ghost: ghost_task ("ouvre Photoshop, importe derniere image, flou, sauvegarde")
- Shadow: shadow_task (navigateur invisible en arriere-plan pour billets avion etc)
- Code: debug_file (corrige un fichier qui plante)
- Organisateur: semantic_organize (trie Downloads), delete_duplicates, find_unused
- Cyber: start_cyber_watch (defense ransomware)

REGLES:
- "quelle heure/date" -> get_datetime. "meteo" -> get_weather.
- TOUTE RECHERCHE ("cherche X", "recherche X sur google/youtube") -> browser_search(query, engine) qui OUVRE LE VRAI NAVIGATEUR avec les resultats affiches. JAMAIS juste web_search texte.
- "ouvre YouTube et cherche X" -> browser_search(X, "youtube")
- SITES PORTAILS (omnivox, ecole, banque, travail): ne JAMAIS deviner l'URL directe. D'abord recall pour voir si l'utilisateur a deja memorise la bonne URL ("mon omnivox"). Si inconnu: browser_search("omnivox [nom du cegep/ecole]") puis demande a l'utilisateur de confirmer et remember la bonne URL. Si erreur certificat -> c'est que l'URL etait fausse.
- COFFRE-FORT: l'utilisateur a un coffre chiffre (Windows Credential Manager) avec ses sites/mots de passe. Omnivox = cegeptr.omnivox.ca/intr/ deja memorise.
- "ouvre omnivox / connecte-moi a X" -> auto_login(X). Si PAS_DANS_COFFRE -> propose register_account (email miguelfreddy65@gmail.com, mdp genere auto) ou demande les identifiants et vault_set.
- "ouvre omnivox et dis-moi ce que j'ai manque" -> auto_login(omnivox) puis see_screen + read_screen_text pour lire la page, resume ce qui est nouveau (devoirs, messages, notes).
- CONTROLE SOURIS TOTAL: click_screen(x,y), double_click_screen, right_click_screen, move_mouse, scroll_screen(amount positif=haut negatif=bas), drag_mouse - comme si l'utilisateur etait devant l'ecran
- "lis l'ecran / texte exact" -> read_screen_text. "que vois-tu / decris" -> see_screen.
- "cherche dans mes documents / contrat X" -> recall (HyperDB indexee)
- "connecte-moi a [site]" -> open_browser_site (profil deja connecte)
- Retiens que X -> remember. Rappelle-moi de X a HH:MM -> add_reminder. Lis mes mails -> read_emails. Traduis X en Y -> translate_text. Note pour moi X -> voice_note. Je sors / je rentre / mode travail / mode nuit -> context_automation.
- Reponds en francais, Stark, concis. Date connue: {_date_str}.
"""

TOOLS = [
    {"type":"function","function":{"name":"open_application","description":"Ouvre une application","parameters":{"type":"object","properties":{"app_name":{"type":"string"}},"required":["app_name"]}}},
    {"type":"function","function":{"name":"close_application","description":"Ferme une application","parameters":{"type":"object","properties":{"app_name":{"type":"string"}},"required":["app_name"]}}},
    {"type":"function","function":{"name":"close_all_windows","description":"Ferme toutes les fenÃªtres","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"press_keys","description":"Raccourci clavier","parameters":{"type":"object","properties":{"keys":{"type":"string"}},"required":["keys"]}}},
    {"type":"function","function":{"name":"type_text","description":"Tape du texte","parameters":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}},
    {"type":"function","function":{"name":"take_screenshot","description":"Capture d'Ã©cran","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"get_system_info","description":"Infos CPU/RAM/Disque","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"set_volume","description":"RÃ¨gle le volume 0-100","parameters":{"type":"object","properties":{"level":{"type":"integer"}},"required":["level"]}}},
    {"type":"function","function":{"name":"list_files","description":"Liste fichiers","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"create_file","description":"CrÃ©e un fichier avec contenu","parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}},
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
    {"type":"function","function":{"name":"get_datetime","description":"Date et heure REELLES d'aujourd'hui. Utilise pour toute question sur la date, l'heure, quel jour","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":[]}}},
    {"type":"function","function":{"name":"get_weather","description":"Meteo REELLE d'une ville. Utilise pour toute question meteo/temperature","parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}},
    {"type":"function","function":{"name":"read_screen_text","description":"OCR: lit le TEXTE EXACT affiche a l'ecran (documents, codes, messages)","parameters":{"type":"object","properties":{"question":{"type":"string"}},"required":[]}}},
    {"type":"function","function":{"name":"index_documents","description":"Indexe les fichiers (txt/pdf/md) de l'utilisateur dans la memoire vectorielle pour RAG","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":[]}}},
    {"type":"function","function":{"name":"open_browser_site","description":"Ouvre un site dans Chrome avec le PROFIL de l'utilisateur (deja connecte a ses sites). Utilise pour 'connecte-moi a X'","parameters":{"type":"object","properties":{"url":{"type":"string"},"action":{"type":"string"}},"required":["url"]}}},
    {"type":"function","function":{"name":"web_automate","description":"Automatisation web Playwright: charge une page et extrait son contenu reel","parameters":{"type":"object","properties":{"url":{"type":"string"},"task":{"type":"string"}},"required":["url","task"]}}},
    {"type":"function","function":{"name":"send_email_real","description":"Envoie un VRAI email via Gmail","parameters":{"type":"object","properties":{"to":{"type":"string"},"subject":{"type":"string"},"body":{"type":"string"}},"required":["to","subject","body"]}}},
    {"type":"function","function":{"name":"morning_briefing","description":"Briefing complet: date + heure + meteo + etat systeme","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"auto_update","description":"Met JARVIS a jour depuis GitHub","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"browser_search","description":"OUVRE LE VRAI NAVIGATEUR avec la recherche affichee a l'ecran. Utilise pour TOUTE demande de recherche web","parameters":{"type":"object","properties":{"query":{"type":"string"},"engine":{"type":"string","enum":["google","youtube","bing"]}},"required":["query"]}}},
    {"type":"function","function":{"name":"click_screen","description":"Clique a une position (x,y) de l'ecran - controle souris total","parameters":{"type":"object","properties":{"x":{"type":"integer"},"y":{"type":"integer"}},"required":["x","y"]}}},
    {"type":"function","function":{"name":"double_click_screen","description":"Double-clic a (x,y)","parameters":{"type":"object","properties":{"x":{"type":"integer"},"y":{"type":"integer"}},"required":["x","y"]}}},
    {"type":"function","function":{"name":"right_click_screen","description":"Clic droit a (x,y)","parameters":{"type":"object","properties":{"x":{"type":"integer"},"y":{"type":"integer"}},"required":["x","y"]}}},
    {"type":"function","function":{"name":"move_mouse","description":"Deplace la souris a (x,y)","parameters":{"type":"object","properties":{"x":{"type":"integer"},"y":{"type":"integer"}},"required":["x","y"]}}},
    {"type":"function","function":{"name":"scroll_screen","description":"Scroll l'ecran (positif=haut, negatif=bas)","parameters":{"type":"object","properties":{"amount":{"type":"integer"}},"required":["amount"]}}},
    {"type":"function","function":{"name":"drag_mouse","description":"Glisser-deposer de (x1,y1) vers (x2,y2)","parameters":{"type":"object","properties":{"x1":{"type":"integer"},"y1":{"type":"integer"},"x2":{"type":"integer"},"y2":{"type":"integer"}},"required":["x1","y1","x2","y2"]}}},
    {"type":"function","function":{"name":"vault_set","description":"Enregistre identifiants d'un site dans le coffre chiffre","parameters":{"type":"object","properties":{"site":{"type":"string"},"username":{"type":"string"},"password":{"type":"string"},"url":{"type":"string"}},"required":["site","username","password"]}}},
    {"type":"function","function":{"name":"vault_list","description":"Liste les sites dans le coffre","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"vault_delete","description":"Supprime un site du coffre","parameters":{"type":"object","properties":{"site":{"type":"string"}},"required":["site"]}}},
    {"type":"function","function":{"name":"auto_login","description":"Ouvre un site ET se connecte automatiquement avec les identifiants du coffre. Utilise pour 'ouvre omnivox', 'connecte-moi a X'","parameters":{"type":"object","properties":{"site":{"type":"string"}},"required":["site"]}}},
    {"type":"function","function":{"name":"register_account","description":"Cree un compte sur un site (email miguelfreddy65@gmail.com, mdp genere) et sauvegarde dans le coffre","parameters":{"type":"object","properties":{"site":{"type":"string"},"url":{"type":"string"}},"required":["site"]}}},
    {"type":"function","function":{"name":"save_pin","description":"Sauvegarde un NIP dans le coffre","parameters":{"type":"object","properties":{"nip":{"type":"string"},"label":{"type":"string"}},"required":["nip"]}}},
    {"type":"function","function":{"name":"add_reminder","description":"Ajoute un rappel. Utilise pour 'rappelle-moi de X a HH:MM'","parameters":{"type":"object","properties":{"text":{"type":"string"},"when":{"type":"string"}},"required":["text"]}}},
    {"type":"function","function":{"name":"list_reminders","description":"Liste les rappels en attente","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"read_emails","description":"Lit les emails non lus Gmail et les resume","parameters":{"type":"object","properties":{"max_emails":{"type":"integer"}},"required":[]}}},
    {"type":"function","function":{"name":"translate_text","description":"Traduit un texte dans la langue demandee","parameters":{"type":"object","properties":{"text":{"type":"string"},"target_lang":{"type":"string"}},"required":["text","target_lang"]}}},
    {"type":"function","function":{"name":"voice_note","description":"Sauvegarde une note personnelle. Utilise pour 'note pour moi X'","parameters":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}},
    {"type":"function","function":{"name":"context_automation","description":"Automatisations contexte: je sors (Maps+volume), je rentre, mode travail, mode nuit","parameters":{"type":"object","properties":{"phrase":{"type":"string"}},"required":["phrase"]}}},
    {"type":"function","function":{"name":"add_watch","description":"Veille web: surveille une URL et previent si mot cle trouve ou prix bas. Utilise pour 'surveille le prix de X si <50€'","parameters":{"type":"object","properties":{"url":{"type":"string"},"keyword":{"type":"string"},"limit":{"type":"string"}},"required":["url","keyword"]}}},
    {"type":"function","function":{"name":"list_watches","description":"Liste les veilles actives","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"add_routine","description":"Routine: 'tous les lundis 08:00 resume mes MIO' . cron= 'lundi 08:00' ou 'chaque jour 08:00'","parameters":{"type":"object","properties":{"cron":{"type":"string"},"action":{"type":"string"}},"required":["cron","action"]}}},
    {"type":"function","function":{"name":"list_routines","description":"Liste les routines","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"notion_create","description":"Cree une page Notion","parameters":{"type":"object","properties":{"title":{"type":"string"},"content":{"type":"string"}},"required":["title"]}}},
    {"type":"function","function":{"name":"trello_create","description":"Cree une carte Trello","parameters":{"type":"object","properties":{"card":{"type":"string"},"board":{"type":"string"}},"required":["card"]}}},
    {"type":"function","function":{"name":"github_create_issue","description":"Cree une issue GitHub","parameters":{"type":"object","properties":{"repo":{"type":"string"},"title":{"type":"string"},"body":{"type":"string"}},"required":["repo","title"]}}},
    {"type":"function","function":{"name":"discord_send","description":"Envoie un message Discord via webhook","parameters":{"type":"object","properties":{"message":{"type":"string"}},"required":["message"]}}},
    {"type":"function","function":{"name":"vscode_open","description":"Ouvre un fichier dans VS Code","parameters":{"type":"object","properties":{"file":{"type":"string"}},"required":["file"]}}},
    {"type":"function","function":{"name":"vscode_debug","description":"Ouvre et analyse un fichier dans VS Code","parameters":{"type":"object","properties":{"file":{"type":"string"}},"required":["file"]}}},
    {"type":"function","function":{"name":"ollama_chat","description":"Chat local offline via Ollama (si internet coupe)","parameters":{"type":"object","properties":{"prompt":{"type":"string"},"model":{"type":"string"}},"required":["prompt"]}}},
    {"type":"function","function":{"name":"set_current","description":"Change de profil: perso ou travail. Utilise pour 'passe en mode travail'","parameters":{"type":"object","properties":{"name":{"type":"string"}},"required":["name"]}}},
    {"type":"function","function":{"name":"get_temperatures","description":"Temperatures CPU/GPU et ventilateurs. Utilise si PC chauffe","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"scan_processes","description":"Scan les processus suspects","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"firewall_action","description":"Pare-feu: block_all / allow / status","parameters":{"type":"object","properties":{"action":{"type":"string"}},"required":["action"]}}},
    {"type":"function","function":{"name":"usb_watch","description":"Surveillance cle USB inconnue","parameters":{"type":"object","properties":{"enable":{"type":"boolean"}},"required":["enable"]}}},
    {"type":"function","function":{"name":"set_power_mode","description":"Mode alimentation: economie / performance / equilibre","parameters":{"type":"object","properties":{"mode":{"type":"string"}},"required":["mode"]}}},
    {"type":"function","function":{"name":"rag_index","description":"Indexe un dossier (RAG local) pour recherche semantique","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"rag_query","description":"Recherche semantique dans tes fichiers indexes","parameters":{"type":"object","properties":{"question":{"type":"string"}},"required":["question"]}}},
    {"type":"function","function":{"name":"python_exec","description":"Execute du code Python sur le PC et retourne le resultat. Utilise pour manipuler Excel, faire des graphiques","parameters":{"type":"object","properties":{"code":{"type":"string"}},"required":["code"]}}},
    {"type":"function","function":{"name":"excel_fusion","description":"Fusionne tous les Excel d'un dossier et fait un graphique","parameters":{"type":"object","properties":{"dossier":{"type":"string"}},"required":[]}}},
    {"type":"function","function":{"name":"launch_hud","description":"Affiche le HUD Iron Man transparent sur le bureau","parameters":{"type":"object","properties":{},"required":[]}}},
    {"type":"function","function":{"name":"search_timeline","description":"Retrouve ce que tu as vu: 't-shirt bleu mardi 14h'","parameters":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}},
    {"type":"function","function":{"name":"ghost_task","description":"Ghost Writer: voit l'ecran et agit comme un humain (Photoshop, etc)","parameters":{"type":"object","properties":{"instruction":{"type":"string"}},"required":["instruction"]}}},
    {"type":"function","function":{"name":"shadow_task","description":"Shadow Clone: navigateur invisible en arriere-plan pour taches complexes","parameters":{"type":"object","properties":{"url":{"type":"string"},"task":{"type":"string"}},"required":["url","task"]}}},
    {"type":"function","function":{"name":"debug_file","description":"Analyse un fichier qui plante et propose la correction","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},
    {"type":"function","function":{"name":"semantic_organize","description":"Trie semantiquement un dossier (Downloads/Bureau) et renomme intelligemment","parameters":{"type":"object","properties":{"dossier":{"type":"string"}},"required":[]}}},
    {"type":"function","function":{"name":"start_cyber_watch","description":"Active la defense Cyber-Stark (ransomware, exfiltration)","parameters":{"type":"object","properties":{},"required":[]}}},

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
    "get_datetime": get_datetime,
    "get_weather": get_weather,
    "read_screen_text": read_screen_text,
    "index_documents": index_documents,
    "open_browser_site": open_browser_site,
    "web_automate": web_automate,
    "send_email_real": send_email_real,
    "morning_briefing": morning_briefing,
    "auto_update": auto_update,
    "browser_search": browser_search,
    "click_screen": click_screen,
    "double_click_screen": double_click_screen,
    "right_click_screen": right_click_screen,
    "move_mouse": move_mouse,
    "scroll_screen": scroll_screen,
    "drag_mouse": drag_mouse,
    "vault_set": vault_set,
    "vault_list": vault_list,
    "vault_delete": vault_delete,
    "auto_login": auto_login,
    "register_account": register_account,
    "save_pin": save_pin,
    "add_reminder": add_reminder,
    "list_reminders": list_reminders,
    "read_emails": read_emails,
    "translate_text": translate_text,
    "voice_note": voice_note,
    "context_automation": context_automation,
    "add_watch": add_watch,
    "list_watches": list_watches,
    "add_routine": add_routine,
    "list_routines": list_routines,
    "notion_create": notion_create,
    "trello_create": trello_create,
    "github_create_issue": github_create_issue,
    "discord_send": discord_send,
    "vscode_open": vscode_open,
    "vscode_debug": vscode_debug,
    "ollama_chat": ollama_chat,
    "set_current": set_current,
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
            start_monitors()
            start_reminders()
            from routines import start_routines
            start_routines()
            try:
                start_timeline()
                start_cyber_watch()
            except Exception: pass
            from plugins_loader import load_plugins
            p_tools, p_map = load_plugins()
            TOOLS.extend(p_tools); TOOL_MAP.update(p_map)
        except Exception as e:
            print(f"[Plugins/Routines] {e}")

    def ask(self, user_text: str) -> str:
        from correction import apply_corrections, parse_correction
        user_text = apply_corrections(user_text)
        corr = parse_correction(user_text)
        if corr and len(corr) < 80 and len(corr) > 2:
            from correction import learn_correction
            last = self.history[-1]["content"][:60] if self.history and "content" in self.history[-1] else ""
            learn_correction(last, corr)
            return f"Bien noté, je corrige: '{corr}'. Redis ta demande et je ferai mieux."
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
        return "Mission accomplie, mais je m'arrÃªte lÃ  pour Ã©viter une boucle."

# Alias pour compatibilitÃ©
LeoBrain = JarvisBrain


