import requests
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import webbrowser

def web_search(query: str, max_results: int = 5) -> str:
    """Recherche web si JARVIS ne sait pas."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"Aucun résultat pour: {query}"
        out = f"Résultats pour '{query}':\n"
        for i, r in enumerate(results, 1):
            out += f"{i}. {r['title']}\n   {r['href']}\n   {r['body'][:150]}...\n"
        return out
    except Exception as e:
        return f"Erreur recherche web: {e}"

def open_website(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"Site ouvert: {url}"

def fetch_url(url: str) -> str:
    try:
        if not url.startswith("http"):
            url = "https://" + url
        r = requests.get(url, timeout=10, headers={"User-Agent": "JARVIS/1.0"})
        text = r.text[:7000]
        return f"Contenu de {url} (extrait):\n{text}"
    except Exception as e:
        return f"Erreur fetch {url}: {e}"

def create_code_and_run(description: str, filename: str = "jarvis_created.py") -> str:
    """Si rien n'existe, JARVIS crée le code lui-même."""
    # Cette fonction est appelée par le LLM qui génère le code.
    # On l'exécute via l'outil files.create_file + run_command
    return f"Prêt à créer: {description} -> {filename}. Le cerveau va générer le code."
