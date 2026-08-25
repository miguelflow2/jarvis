import pyaudio
p = pyaudio.PyAudio()
print(f"Devices: {p.get_device_count()}")
print(f"Default input: {p.get_default_input_device_info()['name']}")
for i in range(min(p.get_device_count(), 5)):
    info = p.get_device_info_by_index(i)
    print(f"[{i}] {info['name']} - in:{info['maxInputChannels']} out:{info['maxOutputChannels']}")
print("\nTest open default...")
try:
    s = p.open(input=True, format=pyaudio.paInt16, channels=1, rate=16000, frames_per_buffer=1024)
    print("OPEN OK, reading...")
    data = s.read(1024, exception_on_overflow=False)
    print(f"READ OK {len(data)} bytes")
    s.close()
    print("CLOSE OK")
except Exception as e:
    print(f"OPEN ERREUR: {e}")
    import traceback; traceback.print_exc()
p.terminate()
