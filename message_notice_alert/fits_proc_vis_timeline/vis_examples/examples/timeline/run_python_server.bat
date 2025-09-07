@echo off
cd /d "%~dp0"
echo "%~dp0"
python -m http.server 18080 --directory "%~dp0"