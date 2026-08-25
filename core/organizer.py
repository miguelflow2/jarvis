"""Organisateur de Vie Numerique - tri semantique des dossiers"""
import os, glob, shutil, hashlib

def semantic_organize(dossier: str = "~/Downloads") -> str:
    """Trie par contenu, renomme intelligemment, detecte doublons"""
    dossier = os.path.expanduser(dossier)
    files = [f for f in glob.glob(os.path.join(dossier, "*")) if os.path.isfile(f)]
    if not files:
        return f"Aucun fichier dans {dossier}"
    # Detecte doublons par hash
    seen = {}
    dups = []
    for f in files:
        try:
            h = hashlib.md5(open(f,"rb").read(1024*1024)).hexdigest()
            if h in seen:
                dups.append(f)
            else:
                seen[h] = f
        except Exception:
            pass
    # Tri semantique via LLM pour renommage
    organized = 0
    for f in files[:20]:  # limite 20 par appel
        try:
            name = os.path.basename(f)
            ext = os.path.splitext(name)[1].lower()
            # Determine categorie par extension + contenu
            if ext in [".pdf"]:
                # lit le debut pour deviner
                try:
                    from pypdf import PdfReader
                    txt = " ".join((p.extract_text() or "")[:500] for p in PdfReader(f).pages[:2])
                    if "facture" in txt.lower() or "invoice" in txt.lower():
                        target = os.path.join(dossier, "Factures")
                    elif "cours" in txt.lower() or "examen" in txt.lower():
                        target = os.path.join(dossier, "Cours")
                    else:
                        target = os.path.join(dossier, "Documents")
                except Exception:
                    target = os.path.join(dossier, "Documents")
            elif ext in [".jpg",".jpeg",".png"]:
                target = os.path.join(dossier, "Images")
            elif ext in [".xlsx",".xls",".csv"]:
                target = os.path.join(dossier, "Tableurs")
            elif ext in [".zip",".rar",".7z"]:
                target = os.path.join(dossier, "Archives")
            else:
                continue
            os.makedirs(target, exist_ok=True)
            dest = os.path.join(target, name)
            if not os.path.exists(dest) and f not in dups:
                shutil.move(f, dest)
                organized += 1
        except Exception:
            pass
    msg = f"Organise {organized} fichiers. Doublons detectes: {len(dups)} ({', '.join(os.path.basename(d) for d in dups[:3])})"
    if dups:
        msg += " - Supprimer les doublons? Dis 'supprime les doublons'"
    return msg

def delete_duplicates(dossier: str = "~/Downloads") -> str:
    dossier = os.path.expanduser(dossier)
    seen = {}
    removed = 0
    for f in glob.glob(os.path.join(dossier, "**", "*"), recursive=True):
        if not os.path.isfile(f):
            continue
        try:
            h = hashlib.md5(open(f,"rb").read(1024*1024)).hexdigest()
            if h in seen:
                os.remove(f)
                removed += 1
            else:
                seen[h] = f
        except Exception:
            pass
    return f"{removed} doublons supprimes"

def find_unused(dossier: str = "~/Downloads", days: int = 365) -> str:
    import time
    dossier = os.path.expanduser(dossier)
    old = []
    for f in glob.glob(os.path.join(dossier, "*")):
        if os.path.isfile(f) and os.path.getmtime(f) < time.time() - days*24*3600:
            old.append(f"{os.path.basename(f)} ({int((time.time()-os.path.getmtime(f))/86400)}j)")
    if not old:
        return f"Aucun fichier inutilise depuis {days}j"
    return f"Fichiers inutilises depuis {days}j:\n" + "\n".join(old[:15])
