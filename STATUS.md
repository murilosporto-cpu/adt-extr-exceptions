# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-19 15:15
- **O que foi feito**:
  - Executada extração de 3 novos dias e varredura profunda no portal PWR cobrindo os últimos 10 dias (09/11 a 18/11/2026).
  - Extraídos e incorporados 3 novos dias:
    - **16/11 (Segunda)**: **9.547 pedidos**.
    - **17/11 (Terça)**: **12.275 pedidos**.
    - **18/11 (Quarta - ontem)**: **7.863 pedidos**.
    - Total de **29.685 novos pedidos** adicionados à base.
  - Avanço da janela móvel de 4 semanas do painel:
    - A semana mais antiga (`19 a 25`) saiu do painel.
    - Nova semana em andamento adicionada: **`16 a 18`** (Segunda a Quarta).
    - As 4 semanas do painel agora são: **`26 a 01`** (7 dias), **`02 a 08`** (7 dias), **`09 a 15`** (7 dias) e **`16 a 18`** (em andamento, 3 dias).
  - Executado backfill retroativo profundo de subidas tardias (10 datas analisadas: 09/11 a 18/11):
    - **69 lojas recuperadas** que haviam subido dados tardiamente no PWR (destaque para 39 lojas em 15/11, 7 lojas em 14/11, 6 lojas em 13/11, 6 lojas em 12/11, 5 lojas em 11/11, 3 lojas em 10/11 e 3 lojas em 09/11).
    - **5.885 pedidos adicionais resgatados e incorporados** à base de dados.
    - Base total expandida de 91 para **94 dias consolidados** (17/08 a 18/11/2026).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 18/11/2026.
  - Janela móvel de 4 semanas atualizada (`26 a 01`, `02 a 08`, `09 a 15` e `16 a 18`).
  - Painéis sincronizados, com cache-busting renovado.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento dos próximos dias (19/11 em diante) para a próxima varredura de rotina.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
