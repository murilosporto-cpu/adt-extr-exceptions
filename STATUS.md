# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-25 13:55
- **O que foi feito**:
  - Extraído 1 novo dia do portal PWR:
    - **24/11 (Terça-feira - ontem)**: **9.070 pedidos**.
  - Executada varredura retroativa profunda nos últimos 10 dias (15/11 a 24/11):
    - **49 lojas recuperadas** com subidas tardias resgatadas (destaque para 36 lojas em 23/11, 5 lojas em 22/11 e 2 lojas em 21/11).
    - **2.217 pedidos adicionais resgatados e incorporados** à base de dados.
  - Janela móvel de 4 semanas atualizada:
    - **`02 a 08`** (7 dias fechados)
    - **`09 a 15`** (7 dias fechados)
    - **`16 a 22`** (7 dias fechados)
    - **`23 a 24`** (em andamento, Segunda e Terça com 2 dias completos)
  - Base histórica atingiu o marco de **100 dias consolidados** (17/08 a 24/11/2026).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 24/11/2026.
  - Janela móvel de 4 semanas atualizada (`02 a 08`, `09 a 15`, `16 a 22` e `23 a 24`).
  - Painéis sincronizados, com cache-busting renovado.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento dos próximos dias da semana (25/11 em diante) para a próxima varredura de rotina.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
