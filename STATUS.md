# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-22 13:45
- **O que foi feito**:
  - Extraídos 2 novos dias do portal PWR:
    - **20/11 (Sexta-feira)**: **17.839 pedidos**.
    - **21/11 (Sábado - ontem)**: **16.225 pedidos**.
    - Total de novos pedidos adicionados: **34.064 pedidos**.
  - Executada varredura retroativa profunda nos últimos 10 dias (12/11 a 21/11):
    - **50 lojas recuperadas** com subidas tardias resgatadas (40 lojas em 19/11, 7 lojas em 18/11 e 3 lojas em 17/11).
    - **3.016 pedidos adicionais resgatados e incorporados** à base de dados.
  - Janela móvel de 4 semanas atualizada:
    - **`26 a 01`** (7 dias fechados)
    - **`02 a 08`** (7 dias fechados)
    - **`09 a 15`** (7 dias fechados)
    - **`16 a 21`** (em andamento, Segunda a Sábado com 6 dias completos)
  - Base total expandida de 95 para **97 dias consolidados** (17/08 a 21/11/2026).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 21/11/2026.
  - Janela móvel de 4 semanas atualizada (`26 a 01`, `02 a 08`, `09 a 15` e `16 a 21`).
  - Painéis sincronizados, com cache-busting renovado.
  - Commit e push concluídos com sucesso para a branch `main` (`35e2c19`), com deploy automático no Cloudflare Pages em produção.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento do domingo 22/11 para fechar a semana `16 a 22` com 7 dias completos na próxima varredura de rotina.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
