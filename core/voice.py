import asyncio
import tempfile
import os

# TTS Français naturel via edge-tts (gratuit, voix DeniseNeural excellente)
# Fallback pyttsx3 si offline

async def speak_edge(text: str, voice: str = "fr-FR-DeniseNeural"):
    try:
        import edge_tts
        import pygame
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tmp = f.name
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp)
        pygame.mixer.init()
        pygame.mixer.music.load(tmp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.quit()
        try: os.remove(tmp)
        except: pass
    except Exception as e:
        print(f"[TTS Edge error] {e} -> fallback pyttsx3")
        speak_pyttsx3(text)

def speak_pyttsx3(text: str):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        # Tentative voix FR
        for v in engine.getProperty('voices'):
            if 'french' in v.name.lower() or 'fr-' in v.id.lower():
                engine.setProperty('voice', v.id)
                break
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS pyttsx3 error] {e}: {text}")

def speak(text: str, voice="fr-FR-DeniseNeural"):
    """Fonction synchrone à appeler depuis JARVIS"""
    print(f"[JARVIS]: {text}")
    try:
        asyncio.run(speak_edge(text, voice))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(speak_edge(text, voice))

def listen_fast(timeout=4, phrase_time=6, device_index=None) -> str:
    """Version ultra-rapide pour mode fluide - latence <1s"""
    import speech_recognition as sr
    r = sr.Recognizer()
    r.energy_threshold = 200
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.5
    if device_index is None:
        try:
            import json
            cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            device_index = cfg.get("audio", {}).get("input_device_index", 2)
        except:
            device_index = 2
    try:
        with sr.Microphone(device_index=device_index) as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time)
        try:
            text = r.recognize_google(audio, language="fr-FR")
            corrections = {"take": "Tayc", "taik": "Tayc", "tayk": "Tayc", "tay c": "Tayc", "le chanteur ta": "Tayc", "chanteur ta": "Tayc"}
            low = text.lower()
            for k, v in corrections.items():
                if k in low:
                    text = text.replace(k, v).replace(k.capitalize(), v)
            return text.strip()
        except sr.UnknownValueError:
            return ""
        except:
            return ""
    except sr.WaitTimeoutError:
        return ""
    except Exception as e:
        return ""

def listen_once(timeout=6, phrase_time=8, device_index=None) -> str:
    """Ecoute une commande via micro M01 Pro"""
    import speech_recognition as sr
    r = sr.Recognizer()
    r.energy_threshold = 250
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    # Force le bon micro si non specifie
    if device_index is None:
        try:
            import json, os
            cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            device_index = cfg.get("audio", {}).get("input_device_index", 2)
        except:
            device_index = 2
    print(f"[JARVIS ecoute sur micro {device_index}... parle dans tes lunettes - appuie et MAINTIENS le bouton si besoin]")
    try:
        with sr.Microphone(device_index=device_index) as source:
            print(f"  (micro {device_index} actif, bruit ambiant...)")
            r.adjust_for_ambient_noise(source, duration=0.8)
            print("  -> Parle maintenant !")
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time)
        print("   -> Transcription Google FR...")
        try:
            text = r.recognize_google(audio, language="fr-FR")
            print(f"   -> Google: {text}")
            corrections = {"take": "Tayc", "taik": "Tayc", "tayk": "Tayc", "tay c": "Tayc", "take sur youtube": "Tayc sur YouTube", "le chanteur ta": "Tayc", "chanteur ta": "Tayc"}
            low = text.lower()
            for k, v in corrections.items():
                if k in low:
                    text = text.replace(k, v).replace(k.capitalize(), v)
                    print(f"   -> Corrige: {k} -> {v}")
            return text.strip()
        except sr.UnknownValueError:
            print("   -> Google n'a rien compris (silence/bruit)")
            return ""
        except sr.RequestError as e:
            print(f"   -> Erreur Google: {e}")
            return ""
        except Exception as e:
            print(f"   -> Erreur STT: {e} ({type(e).__name__})")
            import traceback; traceback.print_exc()
            return ""
    except sr.WaitTimeoutError:
        print("   -> Timeout: rien entendu")
        return ""
    except Exception as e:
        print(f"[STT error] {e}")
        import traceback; traceback.print_exc()
        return ""

def listen_for_wake_word(device_index=None, timeout=None) -> str:
    """Ecoute en continu jusqu'a entendre 'Hey Jarvis' - ultra sensible"""
    import speech_recognition as sr
    r = sr.Recognizer()
    r.energy_threshold = 250
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.7
    if device_index is None:
        try:
            import json, os
            cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            device_index = cfg.get("audio", {}).get("input_device_index", 2)
        except:
            device_index = 2
    try:
        with sr.Microphone(device_index=device_index) as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=4)
        # Transcription legere via Google FR (rapide pour wake word)
        try:
            text = r.recognize_google(audio, language="fr-FR")
            return text.strip()
        except sr.UnknownValueError:
            return ""
        except Exception:
            # fallback whisper si google echoue
            try:
                from openai import OpenAI
                from dotenv import load_dotenv
                load_dotenv()
                import tempfile
                api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    wav_path = f.name
                with open(wav_path, "wb") as wf:
                    wf.write(audio.get_wav_data())
                client = OpenAI(api_key=api_key)
                with open(wav_path, "rb") as af:
                    tr = client.audio.transcriptions.create(model="whisper-1", file=af, language="fr")
                os.remove(wav_path)
                return tr.text.strip()
            except:
                return ""
    except sr.WaitTimeoutError:
        return ""
    except Exception as e:
        print(f"[Wake error] {e}")
        return ""

def list_microphones():
    import speech_recognition as sr
    print("Microphones disponibles (tes lunettes Bluetooth doivent apparaitre ici):")
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  [{i}] {name}")
