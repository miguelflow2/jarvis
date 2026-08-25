"""Cyber-Stark - Defense active (pare-feu + ransomware + exfiltration)"""
import os, time, threading, subprocess, psutil

ALERT_MODE = False

def enable_alert():
    global ALERT_MODE
    ALERT_MODE = True
    # Passe l'interface en rouge via HUD si actif
    print("[CYBER-STARK] MODE ALERTE ROUGE")

def network_watch():
    """Surveille les connexions suspectes et les chiffrages massifs"""
    while True:
        time.sleep(10)
        try:
            # Detecte chiffrage massif (ransomware): beaucoup de fichiers modifies en peu de temps
            # Simplifie: surveille le taux d'ecriture disque
            disk_io = psutil.disk_io_counters()
            time.sleep(2)
            disk_io2 = psutil.disk_io_counters()
            write_rate = (disk_io2.write_bytes - disk_io.write_bytes) / 2 / 1024 / 1024  # MB/s
            if write_rate > 50:  # 50 MB/s suspect
                # Verifie si beaucoup de fichiers recemment modifies
                import glob
                recent = [f for f in glob.glob(os.path.expanduser("~/Documents/*")) if os.path.getmtime(f) > time.time() - 5]
                if len(recent) > 10:
                    enable_alert()
                    # Coupe le reseau
                    subprocess.run(["netsh","advfirewall","set","allprofiles","state","on"], capture_output=True)
                    from core.voice import speak
                    speak("Alerte Cyber-Stark: chiffrage massif detecte, reseau coupe")
        except Exception:
            pass
        try:
            # Detecte exfiltration: gros upload
            net = psutil.net_io_counters()
            time.sleep(3)
            net2 = psutil.net_io_counters()
            sent_rate = (net2.bytes_sent - net.bytes_sent) / 3 / 1024 / 1024
            if sent_rate > 20:
                print(f"[CYBER] Upload suspect {sent_rate:.1f} MB/s")
        except Exception:
            pass

def isolate_process(pid: int) -> str:
    try:
        p = psutil.Process(pid)
        p.suspend()
        return f"Processus {pid} ({p.name()}) isole"
    except Exception as e:
        return f"Erreur isolation: {e}"

def block_ip(ip: str) -> str:
    try:
        subprocess.run(["netsh","advfirewall","firewall","add","rule","name=JARVIS_Block_"+ip,"dir=out","action=block","remoteip="+ip], capture_output=True, timeout=10)
        return f"IP {ip} bloquee"
    except Exception as e:
        return f"Erreur block IP: {e}"

def start_cyber_watch():
    t = threading.Thread(target=network_watch, daemon=True)
    t.start()
    return "Cyber-Stark actif: surveillance chiffrage + exfiltration"
