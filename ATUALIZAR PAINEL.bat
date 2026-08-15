@echo off
cd /d "%~dp0"
echo ==========================================
echo    ATUALIZAR PAINEL PWR (franquias e lojas)
echo ==========================================
echo.
echo [1 de 3] Conferindo os arquivos baixados (trava)...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0validar_extracao.ps1"
if errorlevel 1 goto erro_validacao
echo.
echo [2 de 3] Gerando os dados do painel...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0gera_dados.ps1"
echo.
echo [3 de 3] Publicando no GitHub (a Vercel atualiza sozinha)...
git add -A
git commit -m "data: atualizacao do painel (via botao)"
timeout /t 3 /nobreak >nul
git push origin main
if errorlevel 1 goto erro_push
echo.
echo ==========================================
echo    PRONTO! O link atualiza em 1-2 minutos:
echo    https://adt-extr-exceptions-v1ok.vercel.app/
echo ==========================================
echo.
pause
exit /b 0

:erro_validacao
echo.
echo *** PAROU: ha arquivo com conteudo errado (veja acima em vermelho).
echo *** Baixe de novo o relatorio CERTO no PWR e clique neste botao outra vez.
echo.
pause
exit /b 1

:erro_push
echo.
echo *** Nao consegui publicar. Pode ser que nao havia nada novo para enviar,
echo *** ou falhou a conexao/login do GitHub. Veja a mensagem acima.
echo.
pause
exit /b 1
