import speech_recognition as sr
r = sr.Recognizer()
for idx in [2, 9]:
    try:
        print(f'Test micro {idx}...')
        with sr.Microphone(device_index=idx) as m:
            print(f'  {idx} OK - {m.SAMPLE_RATE}Hz')
            r.adjust_for_ambient_noise(m, duration=0.5)
            print(f'  {idx} bruit OK')
    except Exception as e:
        print(f'  {idx} ERREUR: {e}')
