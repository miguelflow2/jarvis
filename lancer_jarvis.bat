@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title JARVIS - Controle Total PC
echo Lancement JARVIS...
python "%~dp0jarvis.py"
pause
