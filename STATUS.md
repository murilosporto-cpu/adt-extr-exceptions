# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-24 13:35
- **O que foi feito**:
  - Extraídos 2 novos dias do portal PWR:
    - **22/11 (Domingo)**: **17.540 pedidos** (fechando a semana `16 a 22` com 7 dias completos).
    - **23/11 (Segunda-feira - ontem)**: **5.405 pedidos** (início da nova semana).
    - Total de novos pedidos adicionados: **22.945 pedidos**.
  - Executada varredura retroativa profunda nos últimos 10 dias (14/11 a 23/11):
    - **62 lojas recuperadas** com subidas tardias resgatadas (33 em 21/11, 7 em 20/11, 4 em 19/11, 4 em 18/11, 4 em 17/11, 4 em 16/11, 3 em 15/11 e 3 em 14/11).
    - **4.835 pedidos adicionais resgatados e incorporados** à base de dados.
  - Janela móvel de 4 semanas atualizada (semana `26 a 01` rodou para fora e entrou `23 a 23`):
    - **`02 a 08`** (7 dias fechados)
    - **`09 a 15`** (7 dias fechados)
    - **`16 a 22`** (7 dias fechados - semana consolidada)
    - **`23 a 23`** (em andamento, Segunda-feira com 1 dia)
  - Base total expandida de 97 para **99 dias consolidados** (17/08 a 23/11/2026).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 23/11/2026.
  - Janela móvel de 4 semanas atualizada (`02 a 08`, `09 a 15`, `16 a 22` e `23 a 23`).
  - Painéis sincronizados, com cache-busting renovado.
  - Commit e push concluídos com sucesso para a branch `main` (`a242f73`), com deploy automático no Cloudflare Pages em produção.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento dos próximos dias da semana (24/11 em diante) para a próxima varredura de rotina.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
