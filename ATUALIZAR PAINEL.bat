@echo off
chcp 65001 >nul
set GIT_ASK_YESNO=false
title Atualizar Painel PWR - Dominos Pizza
cd /d "%~dp0"

echo ============================================================
echo      ATUALIZAR PAINEL PWR (Franquias e Lojas Proprias)
echo ============================================================
echo.
echo [1 de 2] Consolidando metricas e gerando dados dos paineis...
python atualizar_painel.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao processar os dados dos paineis!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2 de 2] Publicando no GitHub (o Cloudflare atualiza sozinho)...
git add -A
git commit -m "data: atualizacao do painel (novo motor)"
timeout /t 3 /nobreak >nul
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo *** Nao foi possivel publicar. Pode ser que nao havia nada novo para enviar,
    echo *** ou falhou a conexao/login do GitHub. Veja a mensagem acima.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo    PRONTO! O link atualiza no ar em 1-2 minutos:
echo    https://adt-extr-exceptions.pages.dev/
echo ============================================================
echo.
pause
exit /b 0
