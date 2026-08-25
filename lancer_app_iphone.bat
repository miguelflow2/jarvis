@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo Lancement API JARVIS pour iPhone...
echo Ton iPhone doit etre sur le meme WiFi que le PC
ipconfig | findstr "192.168"
echo.
echo Puis sur iPhone ouvre Safari a: http://192.168.2.30:8000
echo (Partager ^> Sur l'ecran d'accueil pour l'installer comme app)
echo.
python -m uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
pause
