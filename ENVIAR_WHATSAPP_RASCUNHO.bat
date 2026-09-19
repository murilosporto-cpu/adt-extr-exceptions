@echo off
chcp 65001 >nul
title Enviar Rascunho WhatsApp - Dominos PWR
cd /d "%~dp0"

echo ============================================================
echo   GERAR TABELAS MURILO E ENVIAR PARA RASCUNHO NO WHATSAPP
echo ============================================================
echo.
echo Executando exportacao e preparando rascunhos nos grupos...
python enviar_rascunho_whatsapp.py

echo.
pause
exit /b %ERRORLEVEL%
