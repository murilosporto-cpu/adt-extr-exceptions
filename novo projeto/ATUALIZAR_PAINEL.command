#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "     ATUALIZAR PAINEL PWR (Mac) - Dominos Pizza"
echo "============================================================"
echo ""
echo "Sincronizando com a nuvem (git pull)..."
git pull --rebase origin main

echo ""
echo "[1 de 2] Consolidando metricas e gerando dados dos paineis..."
python3 atualizar_painel.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERRO] Falha ao processar os dados dos paineis!"
    read -p "Pressione Enter para sair..."
    exit 1
fi

echo ""
echo "[2 de 2] Publicando no GitHub (o Cloudflare atualiza sozinho)..."
git add -A
git commit -m "data: atualizacao do painel (mac)"
git push origin main
if [ $? -ne 0 ]; then
    echo ""
    echo "[AVISO] Nao foi possivel publicar no GitHub agora (verifique sua conexao)."
else
    echo ""
    echo "============================================================"
    echo "   PRONTO! O link atualiza no ar em 1-2 minutos:"
    echo "   https://adt-extr-exceptions.pages.dev/"
    echo "============================================================"
fi

echo ""
read -p "Pressione Enter para fechar esta janela..."
