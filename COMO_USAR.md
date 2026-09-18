# 🍕 Guia de Uso - Novo Projeto Cafe com PWR

Este projeto contem o painel oficial de performance Domino's com automacao completa de extracao, consolidacao diaria e auditoria de subida de vendas.

---

## 🚀 1. Como Visualizar os Paineis

- **Portal Geral**: De duplo clique no arquivo [index.html](index.html). Ele exibira a tela inicial com as opcoes **Franquias** e **Lojas Proprias**.
- **Acesso Direto Franquias**: Abra [ranquias/index.html](franquias/index.html).
- **Acesso Direto Lojas Proprias**: Abra [lojas-proprias/index.html](lojas-proprias/index.html).

> [!TIP]
> Os paineis funcionam 100% offline e sem erro de CORS ao abrir direto pelo Windows Explorer!

---

## ⚡ 2. Como Atualizar as Informacoes

Voce tem duas formas super faceis de atualizar:

### 🟢 Opcao A: Atualizacao Rapida em 1 Clique (Recomendada)
Quando voce adicionar novas planilhas ou quiser reprocessar os dados locais:
1. De duplo clique no executavel **[ATUALIZAR_PAINEL.bat](ATUALIZAR_PAINEL.bat)**.
2. O script ira em 5 segundos:
   - Ler todas as planilhas da pasta dados_all_stores/.
   - Aplicar a ponderacao exata de delivery do PWR para eADT e Extremos.
   - Auditar as lojas com dias pendentes de subida de vendas.
   - Regerar os arquivos data.json e data.js de Franquias e Lojas Proprias.
   - Abrir o portal automaticamente no seu navegador padrao.

### 🤖 Opcao B: Robô de Varredura PWR (Backfill / Buscar Novas Vendas)
Quando quiser que o robo conecte no portal PWR e faca uma varredura automatica nas lojas pendentes:
1. De duplo clique em **[ROBO_VARREDURA_PWR.bat](ROBO_VARREDURA_PWR.bat)**.
2. O robo do Playwright ira:
   - Fazer login automatico no PWR.
   - Verificar os dias pendentes de cada loja.
   - Baixar as planilhas atualizadas para dados_all_stores/.
   - Regerar os paineis e abrir a tela no navegador com os novos dados resgatados.

---

## 📁 3. Estrutura das Pastas e Arquivos

- **ATUALIZAR PAINEL.bat**: Executavel de 1 clique para consolidar, gerar paineis e publicar no Cloudflare Pages.
- **ROBO_VARREDURA_PWR.bat**: Executavel para rodar a varredura e download automatico de vendas atrasadas no PWR.
- **index.html**: Portal inicial com selecao entre Franquias e Lojas Proprias.
- **franquias/**: Painel completo de Franquias (HTML, CSS, JS e dados).
- **lojas-proprias/**: Painel completo de Lojas Proprias (HTML, CSS, JS e dados).
- **dados_all_stores/**: Contem os relatorios diarios de *Keys Summary* e *Service Exceptions*.
- **atualizar_painel.py**: Motor Python que executa o processamento matematico oficial.
- **varredura_backfill_pwr.py**: Motor do robo de navegacao e download do PWR.
- **_arquivos_desenvolvimento/**: Pasta de backup contendo scripts de testes, analises intermediarias e screenshots.

---

## 📊 4. Abas Disponiveis nos Paineis

1. **📈 Semanal**: Visao das 4 semanas com eADT, % Extremos, graficos de tendencia e filtros por consultor e franqueado.
2. **📅 Mensal**: Visao consolidada mensal.
3. **⚠️ Analise de Risco**: Destaque para lojas que necessitam de atencao operacional.
4. **🔄 Auditoria de Subida (Dias Faltantes)**: Relacao em tempo real de lojas que nao transmitiram vendas em algum dia do periodo e as datas exatas faltantes.
