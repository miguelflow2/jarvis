"""
Pont Bluetooth Lunettes <-> JARVIS
Tes lunettes en Bluetooth apparaissent comme un périphérique audio (micro + haut-parleur).
Ce module détecte et sélectionne automatiquement tes lunettes.
"""
import speech_recognition as sr

def detect_glasses():
    """Liste les périphériques audio et tente d'identifier les lunettes"""
    mics = sr.Microphone.list_microphone_names()
    candidates = []
    for i, name in enumerate(mics):
        low = name.lower()
        # mots clés courants lunettes / BT
        if any(k in low for k in ["bluetooth", "headset", "hands-free", "lunette", "glasses", "bt"]):
            candidates.append((i, name))
    return mics, candidates

def get_glasses_microphone_index(preferred_name: str = None):
    mics, candidates = detect_glasses()
    if preferred_name:
        for i, name in enumerate(mics):
            if preferred_name.lower() in name.lower():
                return i, name
    if candidates:
        return candidates[0]  # premier BT trouvé
    return None, None

def print_diagnostic():
    mics, candidates = detect_glasses()
    print("=== DIAGNOSTIC BLUETOOTH LUNETTES ===")
    for i, n in enumerate(mics):
        flag = " <-- CANDIDAT LUNETTES" if any(c[0]==i for c in candidates) else ""
        print(f"[{i}] {n}{flag}")
    if not candidates:
        print("\n[!] Aucune lunette Bluetooth detectee comme micro.")
        print("   -> Verifie que tes lunettes sont appairees en Bluetooth sur ce PC")
        print("   -> Dans Windows: Parametres > Bluetooth > Connecte")
        print("   -> Elles doivent apparaitre comme 'Casque' ou 'Headset'")
    else:
        print(f"\n[OK] Lunettes detectees: {candidates[0][1]} (index {candidates[0][0]})")
        print("   JARVIS utilisera ce micro automatiquement.")
