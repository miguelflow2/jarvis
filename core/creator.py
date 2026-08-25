import os, subprocess, webbrowser, json

def create_and_run_project(description: str, project_type: str = "auto") -> str:
    """
    Création autonome Stark: SARA génère le code complet via LLM puis l'exécute.
    project_type: python, web, game, app
    """
    from dotenv import load_dotenv
    from openai import OpenAI
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    client = OpenAI(api_key=api_key, base_url=base_url, default_headers={"HTTP-Referer":"https://sara.local","X-Title":"SARA Creator"})

    prompt = f"""Tu es SARA Stark. Crée un projet complet pour: "{description}"
Type: {project_type}
Règles:
- Génère UN fichier principal prêt à lancer (python ou html)
- Si python: code complet avec if __name__ == '__main__', interface simple, sans dépendances exotiques
- Si web: html+css+js en un seul fichier index.html autonome
- Réponds UNIQUEMENT en JSON: {{"filename": "chemin/relatif", "content": "code complet", "run_command": "commande pour lancer", "explication": "2 phrases"}}
Exemples filename: sara_creations/snake.py ou sara_creations/site_portfolio/index.html
"""

    try:
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role":"user","content": prompt}],
            response_format={"type":"json_object"}
        )
        data = json.loads(resp.choices[0].message.content)
        filename = data["filename"]
        content = data["content"]
        run_cmd = data.get("run_command", f"python {filename}")
        explication = data.get("explication","")

        # Sécurité chemin
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        os.makedirs(os.path.dirname(base), exist_ok=True)
        with open(base, "w", encoding="utf-8") as f:
            f.write(content)

        # Lancement
        try:
            if filename.endswith(".html"):
                webbrowser.open(f"file://{os.path.abspath(base)}")
                return f"Créé {filename}: {explication} | Ouvert dans Chrome."
            else:
                # python
                subprocess.Popen(run_cmd, shell=True, cwd=os.path.dirname(base))
                return f"Créé {filename}: {explication} | Lancé: {run_cmd}"
        except Exception as e:
            return f"Créé {filename} mais erreur lancement: {e} | {explication}"

    except Exception as e:
        return f"Erreur création: {e}"
