@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
call "ATUALIZAR PAINEL.bat"
exit /b %ERRORLEVEL%
