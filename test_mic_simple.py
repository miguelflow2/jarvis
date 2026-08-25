import speech_recognition as sr
r = sr.Recognizer()
print("Test sans adjust (direct listen)...")
for idx in [None, 2, 9]:
    try:
        print(f"\n--- Micro {idx} ---")
        with sr.Microphone(device_index=idx) as m:
            print(f"Ouvert {idx}, ecoute 3s (parle!)...")
            # Pas de adjust, direct listen
            try:
                audio = r.listen(m, timeout=3, phrase_time_limit=3)
                print(f"  {idx} audio capture OK, taille {len(audio.get_wav_data())}")
                try:
                    txt = r.recognize_google(audio, language="fr-FR")
                    print(f"  Google: {txt}")
                except Exception as e:
                    print(f"  Google erreur: {e}")
            except sr.WaitTimeoutError:
                print(f"  {idx} timeout (silence)")
    except Exception as e:
        print(f"  {idx} ERREUR: {e}")
        import traceback; traceback.print_exc()
