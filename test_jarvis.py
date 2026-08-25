"""Test rapide JARVIS sans voix - vérifie que le cerveau et les tools fonctionnent"""
import os
from dotenv import load_dotenv
load_dotenv()

from core.brain import JarvisBrain

# Vérifie clé
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Pas de OPENAI_API_KEY dans .env")
    print("-> Copie .env.example vers .env et mets ta clé")
    exit(1)

brain = JarvisBrain()

tests = [
    "Ouvre le bloc-notes et écris Bonjour depuis Jarvis",
    "Quelle est la charge CPU et RAM actuelle?",
    "Cherche sur le web: meilleur logiciel montage vidéo gratuit 2026",
]

for t in tests:
    print(f"\n{'='*60}\n👤 TEST: {t}\n{'='*60}")
    ans = brain.ask(t)
    print(f"🤖 JARVIS: {ans}\n")
