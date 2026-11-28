@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "logs" mkdir "logs"
echo ============================================================ >> logs\execucao_agendada.log
echo [INICIO_WRAPPER] %DATE% %TIME% >> logs\execucao_agendada.log
python "%~dp0executar_agendamento_diario.py" >> logs\execucao_agendada.log 2>&1
set EXIT_CODE=%ERRORLEVEL%
echo [FIM_WRAPPER] Codigo de saida: %EXIT_CODE% - %DATE% %TIME% >> logs\execucao_agendada.log
exit /b %EXIT_CODE%