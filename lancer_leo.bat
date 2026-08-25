@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
title LEO - Stark Edition
echo Lancement LEO...
python "%~dp0leo.py"
pause
