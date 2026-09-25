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
echo Sincronizando com a nuvem (git pull)...
git pull --rebase origin main
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
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao reconstruir os dados dos paineis!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Publicando atualizacoes no GitHub (o Cloudflare atualiza sozinho)...
git add -A
git commit -m "data: atualizacao automatica via varredura pwr"
timeout /t 3 /nobreak >nul
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] Nao foi possivel publicar no GitHub agora (verifique sua conexao).
    echo Os dados locais foram atualizados com sucesso.
    echo.
)

echo.
echo Abrindo o portal no navegador...
start "" index.html

echo.
echo ============================================================
echo   Varredura e publicacao concluidas com sucesso!
echo   O site na internet atualiza em 1-2 minutos:
echo   https://adt-extr-exceptions.pages.dev/
echo ============================================================
echo.
pause
