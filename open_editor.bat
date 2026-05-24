@echo off
setlocal

cd /d "%~dp0"
python -m xtable.app.main

GOTO :eof
