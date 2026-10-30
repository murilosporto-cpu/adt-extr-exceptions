# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-30 12:35
- **O que foi feito**:
  - Executada varredura profunda no portal PWR cobrindo 29 datas de Outubro (01/10 a 29/10/2026).
  - Extraídos e consolidados 4 novos dias:
    - **26/10 (Segunda)**: **6.657 pedidos**.
    - **27/10 (Terça)**: **9.478 pedidos**.
    - **28/10 (Quarta)**: **8.531 pedidos**.
    - **29/10 (Quinta - ontem)**: **8.557 pedidos**.
    - Total de **33.223 novos pedidos** adicionados à base.
  - Realizada a rotação dinâmica das semanas do painel:
    - A semana mais antiga (`28 a 04`) deu espaço à nova semana em andamento (`26 a 29`).
    - As 4 semanas vigentes agora são: **`05 a 11`**, **`12 a 18`**, **`19 a 25`** (todas 100% fechadas com 7 dias) e **`26 a 29`** (em andamento, seg a qui).
  - Executado backfill retroativo de subidas tardias:
    - **102 lojas recuperadas** que haviam subido vendas tardiamente no PWR (destaque para o domingo 25/10 com 43 lojas recuperadas, além de resgates ao longo de todo o mês, incluindo histórico completo da loja 19742).
    - **7.605 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 70 para **74 dias consolidados** (17/08 a 29/10).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 29/10/2026.
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
