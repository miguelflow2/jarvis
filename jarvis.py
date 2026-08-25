#!/usr/bin/env python3
# JARVIS Stark - Mode Conversation Fluide - M01 Pro Bluetooth
import os, sys, json, time

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "config.json")
with open(CONFIG_PATH, encoding="utf-8") as f:
    CONFIG = json.load(f)

JARVIS_CFG = CONFIG.get("jarvis", {})

from core.brain import JarvisBrain
from core.voice import speak, listen_once, listen_fast, listen_for_wake_word
from core.bluetooth import print_diagnostic

BANNER = r"""
  JARVIS v4.0 FLUIDE - Conversation continue
  Plus besoin de repeter "Salut Jarvis"
  M01 Pro Bluetooth - God Mode
"""

WAKE_WORDS = ["salut jarvis", "salut jarvisse", "salut djaviss", "salut jarviss", "salut jer", "salut ger", "salut jervis", "hey jarvis", "salut jarvi", "salut", "jarvis"]

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
    print(f"Modele: {JARVIS_CFG.get('model')} | Mode: CONVERSATION FLUIDE")
    print_diagnostic()
    mic_index = CONFIG["audio"].get("input_device_index", 2)
    print(f"\nMicro: [{mic_index}] M01 Pro_F444\n")
    try:
        brain = JarvisBrain(model=JARVIS_CFG.get("model","openai/gpt-4o-mini"), voice=JARVIS_CFG.get("voice","fr-FR-DeniseNeural"))
    except RuntimeError as e:
        print(f"\n{e}")
        return
    # Verrou anti-double instance (evite 2 JARVIS qui se battent pour le micro)
    import tempfile, psutil
    lock_path = os.path.join(tempfile.gettempdir(), "jarvis.lock")
    try:
        if os.path.exists(lock_path):
            with open(lock_path) as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                print(f"[!] JARVIS deja en cours (PID {pid}) - fermeture de cette instance")
                return
        with open(lock_path, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

    speak("Jarvis en ligne. Dis Salut Jarvis une fois, ensuite on discute fluide.")
    print("="*60)
    print("MODE FLUIDE: Dis 'Salut Jarvis' UNE FOIS, puis parle normalement")
    print("Plus besoin de repeter le wake word pendant 45s")
    print("Dis 'merci' ou 'pause' pour repasser en veille")
    print("="*60 + "\n")

    in_conversation = False
    last_active = 0

    while True:
        # Si pas en conversation -> attend wake word
        if not in_conversation:
            print("... en veille (dis 'Salut Jarvis' une fois) ...")
            wake_text = listen_for_wake_word(mic_index, timeout=None)
            if not wake_text or not contains_wake_word(wake_text):
                if wake_text and len(wake_text.strip()) >= 4 and contains_wake_word(wake_text):
                    pass
                elif not wake_text or len(wake_text.strip()) < 4:
                    continue
                else:
                    continue
            command = strip_wake_word(wake_text).strip()
            if command.lower() in ["jer", "ger", "vis", "jervis", "jar"]:
                command = ""
            if command and len(command) > 2:
                text = command
                print(f"[WAKE] + commande: {text}")
                in_conversation = True
                last_active = time.time()
            else:
                speak("Oui, je t'écoute", voice=JARVIS_CFG.get("voice","fr-FR-DeniseNeural"))
                print("-> Mode fluide active (45s) - parle normalement (maintiens bouton)")
                in_conversation = True
                last_active = time.time()
                # Ecoute la première vraie demande sans wake
                text = listen_fast(device_index=mic_index, timeout=6, phrase_time=7)
                if not text:
                    print("(rien, reste en fluide)")
                    continue
                text = strip_wake_word(text) if contains_wake_word(text) else text
        else:
            # Mode fluide: ecoute direct sans wake word
            if time.time() - last_active > 45:
                print("... fin du mode fluide (45s sans parler) -> retour veille ...")
                speak("Je repasse en veille, dis Salut Jarvis quand tu veux", voice=JARVIS_CFG.get("voice","fr-FR-DeniseNeural"))
                in_conversation = False
                continue
            print("... fluide (parle, maintiens bouton) ...")
            text = listen_fast(device_index=mic_index, timeout=5, phrase_time=6)
            if not text:
                continue
            # Si l'utilisateur dit un wake pendant fluide, on le nettoie juste
            text = strip_wake_word(text) if contains_wake_word(text) else text
            last_active = time.time()

        if not text or len(text.strip()) < 2:
            continue
        print(f"\nToi: {text}")
        low = text.lower().strip()
        # STOP PAROLE immediate
        if low.strip() in ["arrete", "arrête", "arrête-toi", "arrete-toi", "chut", "tais-toi", "silence", "stop"] :
            speak("J'arrête.", voice=JARVIS_CFG.get("voice","fr-FR-DeniseNeural"))
            continue
        # Sortie fluide
        if any(x in low for x in ["merci jarvis", "pause jarvis", "en veille jarvis", "au revoir jarvis"]):
            speak("Parfait, je reste en veille. Appelle-moi quand tu veux.")
            in_conversation = False
            continue
        if low in ["merci", "pause"]:
            speak("Je repasse en veille.")
            in_conversation = False
            continue
        if any(x in low for x in ["quitte", "eteins-toi"]):
            speak("A tes ordres. En veille.")
            break
        print("JARVIS reflechit...")
        try:
            answer = brain.ask(text)
        except Exception as e:
            answer = f"Erreur: {e}"
        speak(answer, voice=JARVIS_CFG.get("voice","fr-FR-DeniseNeural"))
        print(f"\n[JARVIS]: {answer}\n")
        print("-"*60)
        last_active = time.time()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArret manuel.")
