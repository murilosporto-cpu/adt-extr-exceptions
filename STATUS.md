# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-21 20:30
- **O que foi feito**:
  - Executada varredura profunda no portal PWR em 20 datas de Outubro (01/10 a 20/10/2026).
  - Extraídos e consolidados 3 novos dias:
    - **18/10 (Domingo)**: **18.440 pedidos** (fechou oficialmente a semana `12 a 18`).
    - **19/10 (Segunda)**: **7.698 pedidos**.
    - **20/10 (Terça - ontem)**: **8.444 pedidos**.
    - Total de **34.582 novos pedidos** incorporados à base.
  - Realizada a rotação dinâmica das semanas do painel:
    - A semana mais antiga (`21 a 27`) deu espaço à nova semana em andamento (`19 a 20`).
    - As 4 semanas vigentes agora são: **`28 a 04`**, **`05 a 11`**, **`12 a 18`** (todas 100% fechadas com 7 dias) e **`19 a 20`** (em andamento, seg a ter).
  - Executado backfill retroativo de subidas tardias:
    - **67 lojas recuperadas** que haviam subido vendas com atraso no PWR (destaque para o sábado 17/10 com 28 lojas recuperadas, além de resgates históricos consistentes nas lojas 19693, 19579, 19687, etc.).
    - **5.276 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 62 para **65 dias** (17/08 a 20/10).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 20/10/2026.
  - Painéis de Franquias e Lojas Próprias atualizados e prontos para deploy.
- **Qual é o próximo passo exato**:
  - Realizar commit e push para o repositório GitHub (`main`) para acionar o deploy automático no Cloudflare Pages.
  - Apresentar o resumo da atualização ao usuário.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
