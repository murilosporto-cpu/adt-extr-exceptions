@echo off
chcp 65001 >nul
title Robo de Varredura PWR - Dominos Pizza
cd /d "%~dp0"

echo ============================================================
echo      ROBO DE VARREDURA PWR - RECUPERAR VENDAS ATRASADAS
echo ============================================================
echo.
echo O robo ira conectar no PWR, consultar os dias pendentes
echo e re-extrair as lojas que subiram vendas com atraso.
echo.

python varredura_backfill_pwr.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Ocorreu uma falha durante a varredura do PWR!
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Reconstruindo paineis com os novos dados recuperados...
python atualizar_painel.py

echo.
echo Abrindo o portal no navegador...
start "" index.html

echo.
echo ============================================================
echo   Varredura e atualizacao local concluidas com sucesso!
echo   Para enviar os novos dados para o site na internet,
echo   basta executar o botao 'ATUALIZAR PAINEL.bat'.
echo ============================================================
echo.
pause
