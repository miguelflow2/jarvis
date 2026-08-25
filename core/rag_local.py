"""RAG local + Interpreteur Python (Open Interpreter style)"""
import os, glob, subprocess, json

def rag_index(path: str = "~/Documents") -> str:
    """Indexe fichiers locaux (txt, pdf, md, py, docx, xlsx) dans HyperDB"""
    from hyperdb import remember_hyper
    path = os.path.expanduser(path)
    exts = ["*.txt","*.md","*.pdf","*.py","*.docx","*.xlsx","*.csv"]
    count = 0
    for ext in exts:
        for f in glob.glob(os.path.join(path, "**", ext), recursive=True)[:100]:
            try:
                text = ""
                if f.endswith(".pdf"):
                    from pypdf import PdfReader
                    reader = PdfReader(f)
                    text = " ".join((p.extract_text() or "") for p in reader.pages[:30])
                elif f.endswith(".xlsx"):
                    import openpyxl
                    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
                    for ws in wb.worksheets[:2]:
                        for row in ws.iter_rows(values_only=True, max_row=30):
                            text += " ".join(str(v) for v in row if v) + "\n"
                elif f.endswith(".docx"):
                    import docx
                    doc = docx.Document(f)
                    text = "\n".join(p.text for p in doc.paragraphs[:200])
                else:
                    text = open(f, encoding="utf-8", errors="ignore").read()
                if not text.strip():
                    continue
                # chunk 1200 chars
                for i in range(0, min(len(text), 40000), 1200):
                    chunk = text[i:i+1200].strip()
                    if len(chunk) > 80:
                        remember_hyper(f"[{os.path.basename(f)}] {chunk}", source="rag_local")
                        count += 1
            except Exception as e:
                continue
    return f"RAG local: {count} extraits indexes depuis {path}. Demande 'Jarvis, resume mon PDF impots'"

def rag_query(question: str) -> str:
    """Recherche semantique dans le RAG local"""
    from hyperdb import recall_hyper
    return recall_hyper(question, top_k=5)

def python_exec(code: str) -> str:
    """Execute du code Python sur la machine (interpreteur) et retourne le resultat"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(code)
        tf_path = tf.name
    try:
        r = subprocess.run(["python", tf_path], capture_output=True, text=True, timeout=30)
        out = r.stdout + ("\nERR:\n" + r.stderr if r.stderr else "")
        return out[:6000] if out else "Code execute sans sortie"
    except Exception as e:
        return f"Erreur exec: {e}"
    finally:
        try: os.remove(tf_path)
        except Exception: pass

def excel_fusion(dossier: str = "~/Downloads") -> str:
    """Fusionne tous les Excel d'un dossier et fait un graphique depenses"""
    code = f"""
import glob, os, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
dossier = os.path.expanduser("{dossier}")
files = glob.glob(os.path.join(dossier, "*.xlsx")) + glob.glob(os.path.join(dossier, "*.xls"))
if not files:
    print("Aucun Excel trouve dans " + dossier)
    exit()
dfs = []
for f in files:
    try:
        dfs.append(pd.read_excel(f))
    except Exception as e:
        print(f"Erreur {{f}}: {{e}}")
df = __import__('pandas').concat(dfs, ignore_index=True)
print(f"Fusion: {{len(df)}} lignes, {{len(df.columns)}} colonnes")
print(df.head().to_string())
print("\\nColonnes:", list(df.columns))
# tente un graphique si colonne montant/date
try:
    for col in df.columns:
        if any(k in str(col).lower() for k in ["montant","prix","total","depense","amount"]):
            df[col] = __import__('pandas').to_numeric(df[col], errors='coerce')
            df.groupby(list(df.columns)[0])[col].sum().plot(kind='bar')
            plt.savefig(os.path.expanduser("~/Desktop/graph_depenses.png"))
            print("Graphique sauvegarde sur Bureau/graph_depenses.png")
            break
except Exception as e:
    print(f"Graph erreur: {{e}}")
"""
    return python_exec(code)
