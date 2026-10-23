# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-23 13:15
- **O que foi feito**:
  - Executada varredura profunda no portal PWR cobrindo 22 datas de Outubro (01/10 a 22/10/2026).
  - Extraídos e consolidados os novos dias **21/10 (Quarta)** com **8.426 pedidos** e **22/10 (Quinta - ontem)** com **8.189 pedidos** (total de **16.615 novos pedidos** adicionados).
  - A semana atual em andamento avançou automaticamente para **`19 a 22`** (segunda a quinta-feira).
  - As 4 semanas vigentes do painel permanecem: **`28 a 04`**, **`05 a 11`**, **`12 a 18`** (todas fechadas com 7 dias) e **`19 a 22`** (em andamento).
  - Executado backfill retroativo de subidas tardias com resultado recorde:
    - **165 lojas recuperadas** que subiram vendas tardiamente ao longo das datas de Outubro (destaque para a terça-feira 20/10 com 37 lojas recuperadas, além de fortes resgates em 19507, 19602, 19821, 19855, 19859, 19877, etc.).
    - **8.978 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 65 para **67 dias** (17/08 a 22/10).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 22/10/2026.
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
