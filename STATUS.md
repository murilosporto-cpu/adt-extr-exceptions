# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-20 15:47
- **O que foi feito**:
  - Extraído o novo dia **19/11 (Quinta - ontem)** com **12.162 pedidos**.
  - Executada varredura retroativa profunda nos últimos 10 dias (10/11 a 19/11):
    - **33 lojas recuperadas** com subidas tardias resgatadas (30 lojas em 18/11 e 3 lojas em 17/11).
    - **1.743 pedidos adicionais resgatados e incorporados** à base de dados.
  - Janela móvel de 4 semanas atualizada:
    - **`26 a 01`** (7 dias fechados)
    - **`02 a 08`** (7 dias fechados)
    - **`09 a 15`** (7 dias fechados)
    - **`16 a 19`** (em andamento, Segunda a Quinta com 4 dias)
  - Base total expandida de 94 para **95 dias consolidados** (17/08 a 19/11/2026).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 19/11/2026.
  - Janela móvel de 4 semanas atualizada (`26 a 01`, `02 a 08`, `09 a 15` e `16 a 19`).
  - Painéis sincronizados, com cache-busting renovado.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento da sexta-feira 20/11 e fim de semana para a próxima varredura de rotina.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
