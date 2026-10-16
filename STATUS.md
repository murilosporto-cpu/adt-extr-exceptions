# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-16 16:05
- **O que foi feito**:
  - Executada varredura no portal PWR em 18 datas (28/09 a 15/10/2026).
  - Extraído e consolidado o novo dia **15/10/2026 (Quinta-feira)** com **8.524 pedidos** incorporados à base.
  - A semana atual em andamento avançou automaticamente para **`12 a 15`** (segunda a quinta-feira).
  - As 4 semanas vigentes do painel permanecem: **`21 a 27`**, **`28 a 04`**, **`05 a 11`** (fechada) e **`12 a 15`** (em andamento).
  - Executado backfill retroativo de subidas tardias:
    - **47 lojas recuperadas** que haviam subido vendas com atraso no PWR (destaque para a quarta-feira 14/10 com 27 lojas recuperadas e resgates também nos dias 05, 06, 07, 08, 10, 11, 12 e 13/10).
    - **2.267 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu para **60 dias** (17/08 a 15/10).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 15/10/2026.
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
