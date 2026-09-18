@echo off
chcp 65001 >nul
title Atualizar Painel - Dominos Pizza
cd /d "%~dp0"

echo ============================================================
echo      ATUALIZANDO PAINEIS DOMINO'S (NOVO PROJETO)
echo ============================================================
echo.

python atualizar_painel.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Ocorreu uma falha ao atualizar os paineis!
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Abrindo o portal no navegador...
start "" index.html

echo.
echo Atualizacao concluida com sucesso!
echo Pressione qualquer tecla para fechar esta janela.
pause >nul
