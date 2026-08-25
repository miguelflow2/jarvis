"""Ghost Writer autonome - voit l'ecran et clique aux bons endroits (VLM + PyAutoGUI)"""
import os

def ghost_task(instruction: str) -> str:
    """Voit l'ecran via see_screen puis agit. Ex: 'ouvre Photoshop, importe la derniere image du bureau, flou, sauvegarde'"""
    from vision import see_screen
    from tools.system import click_screen, type_text, press_keys
    import glob
    # Etape 1: voir
    vision = see_screen(f"Tache: {instruction}. Decris la disposition pour agir.")
    # Etape 2: plan simple via LLM
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY")
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        r = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role":"system","content":"Tu es un agent GUI. Donne une liste d'actions JSON: [{\"action\":\"click\",\"x\":100,\"y\":200},{\"action\":\"type\",\"text\":\"bonjour\"},{\"action\":\"press\",\"keys\":\"ctrl+s\"}]"},{"role":"user","content": f"Instruction: {instruction}\nVision: {vision[:2000]}"}],
            max_tokens=800)
        plan = r.choices[0].message.content
        return f"Plan Ghost pour '{instruction}':\n{plan}\nVision: {vision[:800]}"
    except Exception as e:
        return f"Erreur Ghost: {e}. Vision: {vision[:1000]}"

def photoshop_task(action: str) -> str:
    """Raccourci Photoshop: importe derniere image du Bureau, applique filtre"""
    bilder = sorted(__import__('glob').glob(os.path.expanduser("~/Desktop/*.*")), key=os.path.getmtime, reverse=True)
    if not bilder:
        return "Aucune image sur le Bureau"
    last = bilder[0]
    return f"Derniere image: {last}. Instruction: {action}. Utilise ghost_task pour automatiser."

def get_last_image() -> str:
    import glob
    files = glob.glob(os.path.expanduser("~/Desktop/*.*"))
    imgs = [f for f in files if f.lower().endswith((".png",".jpg",".jpeg",".webp"))]
    if not imgs:
        return "Aucune image sur le Bureau"
    last = max(imgs, key=os.path.getmtime)
    return last
