# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-12 17:08
- **O que foi feito**:
  - Executada extração de 4 novos dias e varredura profunda no portal PWR cobrindo os dias recentes (01/11 a 11/11/2026).
  - Extraídos e incorporados 4 novos dias:
    - **08/11 (Domingo)**: **21.381 pedidos** (fechando a semana `02 a 08` com 7 dias completos).
    - **09/11 (Segunda)**: **7.261 pedidos**.
    - **10/11 (Terça)**: **10.413 pedidos**.
    - **11/11 (Quarta - ontem)**: **7.860 pedidos**.
    - Total de **46.915 novos pedidos** adicionados à base.
  - Realizada a rotação dinâmica das 4 semanas do painel:
    - A semana mais antiga (`12 a 18`) deu espaço para a nova semana em andamento (`09 a 11`).
    - A semana anterior (`02 a 08`) foi 100% fechada com 7 dias.
    - As 4 semanas vigentes agora são: **`19 a 25`**, **`26 a 01`**, **`02 a 08`** (todas 100% fechadas com 7 dias) e **`09 a 11`** (em andamento, seg a qua).
  - Executado backfill retroativo profundo de subidas tardias:
    - **125 lojas recuperadas** que haviam subido vendas tardiamente no PWR (destaque para 46 lojas recuperadas no sábado 07/11, 16 lojas em 06/11, 15 lojas em 05/11, 15 lojas em 04/11, 14 lojas em 03/11 e 19 lojas em 02/11).
    - **8.849 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 83 para **87 dias consolidados** (17/08 a 11/11).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 11/11/2026.
  - Commit e push concluídos com sucesso para o branch `main` (`9c6a66f`), com deploy automático no Cloudflare Pages acionado.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento dos próximos dias da semana (12/11 em diante) para a próxima varredura.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
