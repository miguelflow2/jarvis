#!/usr/bin/env python3
# LEO - IA Ultime Tony Stark - Controle Total PC via Lunettes M01 Pro - Activation "Hey Leo"
import os, sys, json, time

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.json")
with open(CONFIG_PATH, encoding="utf-8") as f:
    CONFIG = json.load(f)

LEO_CFG = CONFIG.get("leo", CONFIG.get("jarvis", {}))

from core.brain import JarvisBrain
from core.voice import speak, listen_once, listen_for_wake_word
from core.bluetooth import print_diagnostic, get_glasses_microphone_index

BANNER = r"""
 ██╗     ███████╗  ██████╗
 ██║     ██╔════╝ ██╔═══██╗
 ██║     █████╗   ██║   ██║  v2.0 STARK EDITION - Hey Leo
 ██║     ██╔══╝   ██║   ██║  Controle Total + God Mode
 ███████╗███████╗ ╚██████╔╝  Lunettes M01 Pro Bluetooth
 ╚══════╝╚══════╝  ╚═════╝
"""

WAKE_WORDS = ["hey leo", "hé leo", "eh leo", "hey léo", "hey leon", "ok leo", "hey léo", "hello leo", "hey google", "hey jarvis"]

def contains_wake_word(text: str) -> bool:
    low = text.lower()
    for w in WAKE_WORDS:
        if w in low:
            return True
    if "leo" in low:
        return True
    return False

def strip_wake_word(text: str) -> str:
    low = text.lower()
    for w in sorted(WAKE_WORDS, key=len, reverse=True):
        if w in low:
            idx = low.find(w)
            return text[idx+len(w):].strip(" ,.:!-")
    for w in ["leo", "Leo", "LEO"]:
        if w.lower() in low:
            idx = low.find(w.lower())
            return (text[:idx] + text[idx+len(w):]).strip(" ,.:!-")
    return text

def main():
    print(BANNER)
    print(f"Modele: {LEO_CFG.get('model')} | Voix: {LEO_CFG.get('voice')} | Activation: 'Hey Leo' | God Mode: ON")
    print_diagnostic()
    mic_index = CONFIG["audio"].get("input_device_index", 2)
    mic_name = f"M01 Pro_F444 (index {mic_index})"
    print(f"\nMicro lunettes selectionne: [{mic_index}] {mic_name}\n")
    try:
        brain = JarvisBrain(model=LEO_CFG.get("model","openai/gpt-4o-mini"), voice=LEO_CFG.get("voice","fr-FR-DeniseNeural"))
    except RuntimeError as e:
        print(f"\n{e}")
        speak("Ma cle OpenRouter n'est pas configuree.")
        return
    speak("Leo en ligne. Systeme Stark operationnel. Dis Hey Leo pour m'activer.")
    print("="*60)
    print("LEO en veille - dis 'Hey Leo' dans tes lunettes M01 Pro")
    print("Ex: 'Hey Leo ouvre Chrome'")
    print("Ex: 'Hey Leo cree moi un jeu Snake en Python et lance le'")
    print("Ex: 'Hey Leo installe Photoshop et ouvre le'")
    print("Ex: 'Hey Leo quel est le meilleur film 2026 ? cherche et dis moi'")
    print("="*60 + "\n")
    while True:
        print("... en veille (en attente de 'Hey Leo') ...")
        wake_text = listen_for_wake_word(mic_index, timeout=None)
        if not wake_text:
            continue
        print(f"[WAKE] entendu: {wake_text}")
        if not contains_wake_word(wake_text):
            # Petit bruit parasite
            if len(wake_text.strip()) < 3:
                continue
            # Si pas de wake mais phrase longue, on tente quand meme
            if "leo" not in wake_text.lower() and len(wake_text) < 8:
                continue
        command = strip_wake_word(wake_text).strip()
        if command and len(command) > 2:
            text = command
            print(f">> Commande directe: {text}")
        else:
            speak("Oui ?", voice=LEO_CFG.get("voice","fr-FR-DeniseNeural"))
            print("-> J'ecoute ta demande (10s)...")
            text = listen_once(device_index=mic_index, timeout=10, phrase_time=10)
            if not text:
                print("(rien entendu, retour en veille)")
                continue
            text = strip_wake_word(text) if contains_wake_word(text) else text
        if not text or len(text.strip()) < 2:
            continue
        print(f"\nToi (lunettes): {text}")
        low = text.lower().strip()
        if any(x in low for x in ["quitte", "quitter", "stop leo", "au revoir leo", "eteins-toi", "arrete-toi"]):
            speak("Compris. Je passe en veille. A tes ordres.")
            break
        print("LEO reflechit...")
        try:
            answer = brain.ask(text)
        except Exception as e:
            answer = f"Erreur: {e}"
            print(answer)
        speak(answer, voice=LEO_CFG.get("voice","fr-FR-DeniseNeural"))
        print(f"\n[LEO]: {answer}\n")
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
