@echo off
cd /d "%~dp0"
python -m streamlit run "%~dp0stocks.py"
pause
