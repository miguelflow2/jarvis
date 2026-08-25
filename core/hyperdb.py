import os, json, sqlite3, datetime, hashlib
from dotenv import load_dotenv
load_dotenv()
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "jarvis_hyper.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS memory (
        id TEXT PRIMARY KEY, fact TEXT, embedding BLOB, timestamp TEXT, source TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS evolution (
        id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT, timestamp TEXT
    )""")
    conn.commit(); conn.close()

def embed(text: str):
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        client = OpenAI(api_key=api_key, base_url=base_url)
        r = client.embeddings.create(model="openai/text-embedding-3-small", input=text)
        return r.data[0].embedding
    except:
        # fallback hash
        import numpy as np
        h = hashlib.md5(text.encode()).digest()
        return [float(b)/255 for b in h[:16]] + [0]*16

def remember_hyper(fact: str, source="user"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    eid = hashlib.md5((fact+str(datetime.datetime.now())).encode()).hexdigest()
    emb = json.dumps(embed(fact))
    conn.execute("INSERT INTO memory VALUES (?,?,?,?,?)", (eid, fact, emb, datetime.datetime.now().isoformat(), source))
    conn.commit(); conn.close()
    # Evolution log
    log_evolution(f"Appris: {fact[:60]}")
    return f"[HyperDB] Mémorisé: {fact}"

def recall_hyper(query: str, top_k=5):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT fact, embedding FROM memory")
    rows = cur.fetchall()
    if not rows:
        return "Aucun souvenir hyper."
    q_emb = embed(query)
    import math
    def cosine(a,b):
        dot=sum(x*y for x,y in zip(a,b))
        na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b))
        return dot/(na*nb+1e-9)
    scored=[]
    for fact, emb_json in rows:
        emb=json.loads(emb_json)
        scored.append((cosine(q_emb, emb), fact))
    scored.sort(reverse=True)
    conn.close()
    return "\n".join(f"- {f} (score {s:.2f})" for s,f in scored[:top_k])

def log_evolution(event: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO evolution (event, timestamp) VALUES (?,?)", (event, datetime.datetime.now().isoformat()))
    conn.commit(); conn.close()

def get_stats():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM memory"); mem = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM evolution"); evo = c.fetchone()[0]
    conn.close()
    return f"HyperDB: {mem} souvenirs, {evo} évolutions"
