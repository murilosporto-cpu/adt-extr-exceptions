# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-18 13:00
- **O que foi feito**:
  - Executada varredura no portal PWR em 20 datas (28/09 a 17/10/2026).
  - Extraídos e consolidados os novos dias **16/10 (Sexta)** com **17.288 pedidos** e **17/10 (Sábado - ontem)** com **15.487 pedidos** (total de **32.775 novos pedidos** adicionados).
  - A semana atual em andamento avançou automaticamente para **`12 a 17`** (segunda a sábado).
  - As 4 semanas vigentes do painel permanecem: **`21 a 27`**, **`28 a 04`**, **`05 a 11`** (fechada) e **`12 a 17`** (em andamento).
  - Executado backfill retroativo de subidas tardias:
    - **46 lojas recuperadas** que subiram vendas tardiamente no PWR (destaque para a quinta-feira 15/10 com 35 lojas recuperadas, além de resgates nos dias 09, 12, 13 e 14/10).
    - **2.345 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 60 para **62 dias** (17/08 a 17/10).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 17/10/2026.
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
