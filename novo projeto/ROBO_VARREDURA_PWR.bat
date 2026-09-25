@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
call "ROBO_VARREDURA_PWR.bat"
exit /b %ERRORLEVEL%
