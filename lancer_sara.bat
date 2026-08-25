@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title SARA - Salut Sara
echo Lancement SARA...
python "%~dp0sara.py"
pause
