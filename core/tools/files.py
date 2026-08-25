import os
import shutil
import glob
import subprocess

def list_files(path: str = ".") -> str:
    try:
        path = os.path.expanduser(path)
        items = os.listdir(path)
        if not items: return f"Dossier vide: {path}"
        return f"Contenu de {path}:\n" + "\n".join(f"- {x}" for x in items[:50])
    except Exception as e:
        return f"Erreur list {path}: {e}"

def create_file(path: str, content: str = "") -> str:
    try:
        path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Fichier créé: {path}"
    except Exception as e:
        return f"Erreur création {path}: {e}"

def read_file(path: str) -> str:
    try:
        path = os.path.expanduser(path)
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            data = f.read()
        return data[:8000] if len(data) > 8000 else data
    except Exception as e:
        return f"Erreur lecture {path}: {e}"

def delete_path(path: str) -> str:
    try:
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return f"Supprimé: {path}"
    except Exception as e:
        return f"Erreur suppression {path}: {e}"

def search_files(query: str, root: str = "C:/Users") -> str:
    try:
        pattern = os.path.join(os.path.expanduser(root), "**", f"*{query}*")
        results = glob.glob(pattern, recursive=True)[:20]
        if not results: return f"Aucun fichier trouvé pour '{query}' dans {root}"
        return "\n".join(results)
    except Exception as e:
        return f"Erreur recherche: {e}"

def run_command(command: str) -> str:
    """Exécute n'importe quelle commande shell. Autonomie totale."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        out = (result.stdout or "") + ("\nERR: " + result.stderr if result.stderr else "")
        return out[:6000] if out else f"Commande exécutée (code {result.returncode})"
    except Exception as e:
        return f"Erreur commande: {e}"

def install_software(query: str) -> str:
    """Installe automatiquement un logiciel via winget / pip / npm"""
    q = query.lower()
    # 1. Python package
    if any(x in q for x in ["python", "pip install"]):
        pkg = query.split()[-1]
        return run_command(f"pip install {pkg}")
    # 2. Windows app via winget
    result = run_command(f'winget search "{query}"')
    # On tente install direct
    install = run_command(f'winget install --accept-package-agreements --accept-source-agreements "{query}"')
    if "aucun" in install.lower() or "no package" in install.lower():
        return f"Recherche winget:\n{result}\n\nTentative install:\n{install}\n\nSi introuvable, je peux le créer ou le télécharger depuis le web."
    return install[:6000]
