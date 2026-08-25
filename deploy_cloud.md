# JARVIS Cloud - Tourne même PC éteint

Pour que JARVIS tourne 24/7 même PC fermé, déploie-le sur un VPS (5€/mois) ou Render gratuit.

## Option 1 - Render.com (gratuit, 2 min)
1. Push ce dossier sur GitHub
2. Va sur render.com -> New Web Service -> Connecte ton repo JARVIS
3. Build: `pip install -r requirements.txt` | Start: `uvicorn app.server:app --host 0.0.0.0 --port $PORT`
4. Ajoute env var: `OPENROUTER_API_KEY=sk-or-v1-...`
5. Ton JARVIS sera sur `https://jarvis-xxxx.onrender.com` - tes lunettes s'y connectent via l'app (change l'URL dans app/static/index.html)

## Option 2 - VPS (OVH/Hetzner)
```bash
docker build -t jarvis .
docker run -d -p 8000:8000 --env OPENROUTER_API_KEY=sk-or-... --restart always jarvis
```

PC éteint = JARVIS cloud continue, tu parles via l'app iPhone -> lunettes.
