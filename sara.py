#!/usr/bin/env python3
# SARA - IA Ultime - Controle Total PC via Lunettes M01 Pro - Activation "Salut Sara"
import os, sys, json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.json")
with open(CONFIG_PATH, encoding="utf-8") as f:
    CONFIG = json.load(f)

SARA_CFG = CONFIG.get("sara", CONFIG.get("leo", {}))

from core.brain import JarvisBrain
from core.voice import speak, listen_once, listen_for_wake_word
from core.bluetooth import print_diagnostic

BANNER = r"""
  ███████╗ █████╗ ██████╗  █████╗
  ██╔════╝██╔══██╗██╔══██╗██╔══██╗ v2.0 SARA Edition
  ███████╗███████║██████╔╝███████║ Salut Sara - God Mode
  ╚════██║██╔══██║██╔══██╗██╔══██║ M01 Pro Bluetooth
  ███████║██║  ██║██║  ██║██║  ██║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
"""

WAKE_WORDS = ["salut sara", "salut sarah", "salut sarra", "salut sarra", "hey sara", "salut sera", "sarah", "sara"]

def contains_wake_word(text: str) -> bool:
    low = text.lower()
    for w in WAKE_WORDS:
        if w in low:
            return True
    return False

def strip_wake_word(text: str) -> str:
    low = text.lower()
    for w in sorted(WAKE_WORDS, key=len, reverse=True):
        if w in low:
            idx = low.find(w)
            return text[idx+len(w):].strip(" ,.:!-")
    return text

def main():
    print(BANNER)
    print(f"Modele: {SARA_CFG.get('model')} | Voix: {SARA_CFG.get('voice')} | Activation: 'Salut Sara'")
    print_diagnostic()
    mic_index = CONFIG["audio"].get("input_device_index", 2)
    print(f"\nMicro lunettes: [{mic_index}] M01 Pro_F444\n")
    try:
        brain = JarvisBrain(model=SARA_CFG.get("model","openai/gpt-4o-mini"), voice=SARA_CFG.get("voice","fr-FR-DeniseNeural"))
        # Override prompt name pour SARA
        brain.history[0]["content"] = brain.history[0]["content"].replace("LEO", "SARA").replace("Leo", "Sara")
    except RuntimeError as e:
        print(f"\n{e}")
        speak("Ma cle OpenRouter n'est pas configuree.")
        return
    speak("Sara en ligne. Salut ! Dis Salut Sara pour m'activer.")
    print("="*60)
    print("SARA en veille - dis 'Salut Sara' dans tes lunettes (MAINTIENS le bouton)")
    print("Ex: 'Salut Sara ouvre Chrome'")
    print("Ex: 'Salut Sara cree moi un jeu et lance le'")
    print("="*60 + "\n")
    while True:
        print("... en veille (en attente de 'Salut Sara') ...")
        wake_text = listen_for_wake_word(mic_index, timeout=None)
        if not wake_text:
            continue
        print(f"[WAKE] entendu: {wake_text}")
        if not contains_wake_word(wake_text):
            if len(wake_text.strip()) < 3:
                continue
            if "sara" not in wake_text.lower() and "sarah" not in wake_text.lower():
                if len(wake_text) < 8:
                    continue
        command = strip_wake_word(wake_text).strip()
        if command and len(command) > 2:
            text = command
            print(f">> Commande directe: {text}")
        else:
            speak("Oui ?", voice=SARA_CFG.get("voice","fr-FR-DeniseNeural"))
            print("-> J'ecoute ta demande (10s) - MAINTIENS le bouton et parle !")
            text = listen_once(device_index=mic_index, timeout=10, phrase_time=10)
            if not text:
                print("(rien entendu, retour en veille)")
                continue
            text = strip_wake_word(text) if contains_wake_word(text) else text
        if not text or len(text.strip()) < 2:
            continue
        print(f"\nToi: {text}")
        low = text.lower().strip()
        if any(x in low for x in ["quitte", "quitter", "stop sara", "au revoir sara", "eteins-toi"]):
            speak("Compris, je me mets en veille. A tout a l'heure !")
            break
        print("SARA reflechit...")
        try:
            answer = brain.ask(text)
        except Exception as e:
            answer = f"Erreur: {e}"
            print(answer)
        speak(answer, voice=SARA_CFG.get("voice","fr-FR-DeniseNeural"))
        print(f"\n[SARA]: {answer}\n")
        print("-"*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArret manuel.")
        try:
            from core.voice import speak as s
            s("Arret manuel. A bientot.")
        except: pass
