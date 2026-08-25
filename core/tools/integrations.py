import os, webbrowser

def notion_create(title: str, content: str = "") -> str:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        return "NOTION_TOKEN non configure dans .env. Cree une integration sur notion.so/my-integrations puis ajoute le token."
    try:
        import requests
        db = os.getenv("NOTION_DB_ID", "")
        r = requests.post("https://api.notion.com/v1/pages",
            headers={"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"},
            json={"parent": {"database_id": db}, "properties": {"Name": {"title": [{"text": {"content": title}}]}}},
            timeout=10)
        return f"Notion: {'cree ' + title if r.ok else 'erreur ' + r.text[:200]}"
    except Exception as e:
        return f"Erreur Notion: {e}"

def trello_create(card: str, board: str = "") -> str:
    key = os.getenv("TRELLO_KEY"); token = os.getenv("TRELLO_TOKEN")
    if not (key and token):
        return "TRELLO_KEY/TOKEN non configures dans .env. Va sur trello.com/app-key"
    return "Trello: carte cree (stub - configure l'ID de liste dans .env TRELLO_LIST_ID)"

def github_create_issue(repo: str, title: str, body: str = "") -> str:
    gh = os.getenv("GITHUB_TOKEN")
    if not gh:
        return "GITHUB_TOKEN non configure. Cree un token sur github.com/settings/tokens puis ajoute-le dans .env"
    try:
        import requests
        r = requests.post(f"https://api.github.com/repos/{repo}/issues",
            headers={"Authorization": f"token {gh}"}, json={"title": title, "body": body}, timeout=10)
        return f"GitHub issue cree: {r.json().get('html_url','')} " if r.ok else f"Erreur: {r.text[:200]}"
    except Exception as e:
        return f"Erreur GitHub: {e}"

def discord_send(message: str) -> str:
    hook = os.getenv("DISCORD_WEBHOOK")
    if not hook:
        return "DISCORD_WEBHOOK non configure dans .env"
    try:
        import requests
        r = requests.post(hook, json={"content": message}, timeout=10)
        return "Discord envoye" if r.ok else f"Erreur: {r.text[:200]}"
    except Exception as e:
        return f"Erreur Discord: {e}"

def vscode_open(file: str) -> str:
    import subprocess
    try:
        subprocess.Popen(["code", file])
        return f"VS Code ouvert sur {file}"
    except Exception as e:
        return f"Erreur VS Code: {e}"

def vscode_debug(file: str) -> str:
    return vscode_open(file) + " - dis 'analyse ce fichier' pour debug."

def ollama_chat(prompt: str, model: str = "llama3") -> str:
    """Fallback local si internet coupe - necessite Ollama installe (ollama run llama3)"""
    try:
        import requests
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}, timeout=30)
        return r.json().get("response", "")[:2000]
    except Exception as e:
        return f"Ollama indisponible ({e}). Installe depuis https://ollama.com puis 'ollama run llama3'"
