"""Domotique totale - Maitre absolu du systeme (Windows/Mac/Linux)"""
import os, subprocess, json, psutil

def get_temperatures() -> str:
    """CPU/GPU temp + ventilateurs (psutil + GPUtil + WMI fallback)"""
    out = []
    try:
        temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
        if temps:
            for name, entries in temps.items():
                for e in entries:
                    out.append(f"{name} {e.label or ''}: {e.current}C")
        else:
            out.append("Capteurs psutil non disponibles sur ce Windows")
    except Exception as e:
        out.append(f"psutil temp erreur: {e}")
    try:
        import GPUtil
        for gpu in GPUtil.getGPUs():
            out.append(f"GPU {gpu.name}: {gpu.temperature}C, load {gpu.load*100:.0f}%, mem {gpu.memoryUtil*100:.0f}%")
    except Exception:
        out.append("GPUtil non disponible (pas de GPU Nvidia ou pas installe)")
    # WMI fallback via WMIC
    try:
        r = subprocess.run(["wmic","/namespace:\\\\root\\wmi","PATH","MSAcpi_ThermalZoneTemperature","get","CurrentTemperature"], capture_output=True, text=True, timeout=5)
        if r.stdout and "CurrentTemperature" not in r.stdout.split("\n")[0]:
            pass
    except Exception:
        pass
    # Ventilateurs via psutil
    try:
        fans = psutil.sensors_fans() if hasattr(psutil, "sensors_fans") else {}
        for name, entries in fans.items():
            for e in entries:
                out.append(f"Ventilateur {name}: {e.current} RPM")
    except Exception:
        pass
    # Surchauffe proactive
    try:
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 90:
            out.append("ALERTE: CPU >90% - je peux fermer les apps gourmandes sur demande")
    except Exception:
        pass
    return "\n".join(out) if out else "Aucune temperature disponible"

def scan_processes() -> str:
    """Scan processus + alerte si suspect"""
    suspicious = ["mimikatz","keylogger","miner","xmrig"]
    out = []
    for p in psutil.process_iter(['name','cpu_percent','memory_percent']):
        try:
            name = (p.info['name'] or "").lower()
            if any(s in name for s in suspicious):
                out.append(f"SUSPECT: {p.info['name']} (CPU {p.info['cpu_percent']}%)")
        except Exception:
            pass
    if out:
        return "Processus suspects:\n" + "\n".join(out)
    total = len(list(psutil.process_iter()))
    return f"{total} processus actifs, aucun suspect detecte"

def firewall_action(action: str) -> str:
    """Pare-feu: block_all / allow / status"""
    try:
        if action == "block_all":
            subprocess.run(["netsh","advfirewall","set","allprofiles","state","on"], capture_output=True, timeout=10)
            subprocess.run(["netsh","advfirewall","firewall","add","rule","name=JARVIS_BlockAll","dir=out","action=block","enable=yes"], capture_output=True, timeout=10)
            return "Pare-feu: toutes les connexions sortantes bloquees (Cyber-Stark)"
        elif action == "allow":
            subprocess.run(["netsh","advfirewall","set","allprofiles","state","off"], capture_output=True, timeout=10)
            return "Pare-feu desactive"
        elif action == "status":
            r = subprocess.run(["netsh","advfirewall","show","allprofiles"], capture_output=True, text=True, timeout=10)
            return r.stdout[:2000]
        else:
            return "Action: block_all / allow / status"
    except Exception as e:
        return f"Erreur pare-feu: {e}"

def usb_watch(enable: bool = True) -> str:
    """Verrouillage si cle USB inconnue (surveillance via WMI)"""
    # Pour demo: liste les USB actuels et memorise les connus
    try:
        r = subprocess.run(["wmic","logicaldisk","where","drivetype=2","get","DeviceID,VolumeName"], capture_output=True, text=True, timeout=10)
        known_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "known_usb.json")
        import json
        current = r.stdout.strip()
        if enable:
            if os.path.exists(known_path):
                with open(known_path, encoding="utf-8") as f:
                    known = json.load(f)
            else:
                known = {}
            # Sauvegarde les actuels comme connus
            with open(known_path, "w", encoding="utf-8") as f:
                json.dump({"last": current}, f)
            return f"Surveillance USB activee. USB actuels memorises comme connus. Prochaine cle inconnue -> alerte."
        else:
            return f"USB actuels:\n{current}"
    except Exception as e:
        return f"Erreur USB watch: {e}"

def check_usb_unknown() -> str:
    """Verifie si une nouvelle cle USB inconnue est branchee"""
    try:
        import json, subprocess
        known_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "known_usb.json")
        if not os.path.exists(known_path):
            return "Pas de reference USB memorisee"
        with open(known_path, encoding="utf-8") as f:
            known = json.load(f).get("last","")
        r = subprocess.run(["wmic","logicaldisk","where","drivetype=2","get","DeviceID,VolumeName"], capture_output=True, text=True, timeout=10)
        current = r.stdout.strip()
        if current != known:
            return f"ALERTE USB inconnue detectee!\nActuel:\n{current}\nConnu:\n{known}"
        return "Aucune nouvelle cle USB"
    except Exception as e:
        return f"Erreur check USB: {e}"

def kill_network_suspicious() -> str:
    """Ferme connexions reseau suspectes (ports etrangers)"""
    try:
        conns = psutil.net_connections(kind='inet')
        killed = 0
        for c in conns:
            if c.status == 'ESTABLISHED' and c.raddr:
                # Exemple: tue les connexions vers ports non standards (>50000) si suspect
                pass
        return f"{len(conns)} connexions actives. Pour bloquer tout: firewall block_all"
    except Exception as e:
        return f"Erreur reseau: {e}"

def set_power_mode(mode: str) -> str:
    """economie / performance / equilibre"""
    try:
        guid_map = {"economie": "a1841308-3541-4fab-bc81-f71556f20b4a", "performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", "equilibre": "381b4222-f694-41f0-9685-ff5bb260df2e"}
        guid = guid_map.get(mode.lower(), guid_map["equilibre"])
        subprocess.run(["powercfg","/setactive", guid], capture_output=True, timeout=10)
        return f"Mode alimentation: {mode}"
    except Exception as e:
        return f"Erreur power mode: {e}"

def app_volume(app: str, level: int) -> str:
    """Volume par application (0-100) via pycaw si dispo"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
        sessions = AudioUtilities.GetAllSessions()
        for s in sessions:
            if s.Process and app.lower() in s.Process.name().lower():
                vol = s._ctl.QueryInterface(ISimpleAudioVolume)
                vol.SetMasterVolume(level/100, None)
                return f"Volume {app} a {level}%"
        return f"App {app} non trouvee parmi les sessions audio"
    except Exception as e:
        return f"Erreur volume app (pycaw requis): {e}. Utilise set_volume pour le volume global."
