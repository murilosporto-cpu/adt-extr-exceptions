# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-05 12:15
- **O que foi feito**:
  - Executada extração de 3 novos dias e varredura profunda no portal PWR cobrindo os dias recentes (25/10 a 04/11/2026).
  - Extraídos e incorporados 3 novos dias:
    - **02/11 (Segunda)**: **16.449 pedidos**.
    - **03/11 (Terça)**: **8.582 pedidos**.
    - **04/11 (Quarta - ontem)**: **6.697 pedidos**.
    - Total de **31.728 novos pedidos** adicionados à base.
  - Realizada a rotação dinâmica das 4 semanas do painel:
    - A semana mais antiga (`05 a 11`) deu espaço para a nova semana em andamento (`02 a 04`).
    - As 4 semanas vigentes agora são: **`12 a 18`**, **`19 a 25`**, **`26 a 01`** (todas 100% fechadas com 7 dias) e **`02 a 04`** (em andamento, seg a qua).
  - Executado backfill retroativo profundo de subidas tardias:
    - **53 lojas recuperadas** que haviam subido vendas tardiamente no PWR (10 lojas no domingo 01/11, 7 lojas em 31/10, 7 lojas em 30/10, 6 lojas em 29/10, 6 lojas em 28/10, 6 lojas em 27/10, 6 lojas em 26/10 e 5 lojas em 25/10).
    - **3.575 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 77 para **80 dias consolidados** (17/08 a 04/11).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 04/11/2026.
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
