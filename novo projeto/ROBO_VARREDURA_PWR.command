#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "     ROBO DE VARREDURA PWR (Mac) - RECUPERAR VENDAS ATRASADAS"
echo "============================================================"
echo ""
echo "Sincronizando com a nuvem (git pull)..."
git pull --rebase origin main

echo ""
python3 varredura_backfill_pwr.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERRO] Ocorreu uma falha durante a varredura do PWR!"
    read -p "Pressione Enter para sair..."
    exit 1
fi

echo ""
echo "Reconstruindo paineis com os novos dados recuperados..."
python3 atualizar_painel.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERRO] Falha ao reconstruir os dados dos paineis!"
    read -p "Pressione Enter para sair..."
    exit 1
fi

echo ""
echo "Publicando atualizacoes no GitHub..."
git add -A
git commit -m "data: atualizacao automatica via varredura pwr (mac)"
git push origin main
if [ $? -ne 0 ]; then
    echo ""
    echo "[AVISO] Nao foi possivel publicar no GitHub agora."
else
    echo ""
    echo "============================================================"
    echo "   Varredura e publicacao concluidas com sucesso!"
    echo "   https://adt-extr-exceptions.pages.dev/"
    echo "============================================================"
fi

echo ""
read -p "Pressione Enter para fechar esta janela..."
