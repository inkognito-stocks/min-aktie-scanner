@echo off
chcp 65001 >nul
title AktieApp - Streamlit
color 0A
echo ========================================
echo   AktieApp - Streamlit Server
echo ========================================
echo.
cd /d "%~dp0"
echo Startar Streamlit server...
echo.
python -m streamlit run "%~dp0stocks.py"
echo.
echo Server stoppad.
pause
