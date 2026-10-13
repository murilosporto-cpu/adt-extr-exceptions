# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-13 12:20
- **O que foi feito**:
  - Atendendo à solicitação do usuário, não foi incluído o dia 12/10 para não queimar prematuramente a semana `14 a 20` por apenas 1 dia isolado. O ciclo semanal continuou mantendo as 4 semanas consolidadas: `14 a 20`, `21 a 27`, `28 a 04` e `05 a 11` (fechada).
  - Executada varredura profunda de subida tardia (backfill) no portal PWR em 14 datas retroativas (`28/09` a `11/10/2026`).
  - **Resultados expressivos da varredura**:
    - **52 lojas recuperadas** que subiram vendas tardiamente (destaque para o domingo 11/10 com 39 lojas que haviam subido tarde no PWR, além de subidas resgatadas nos dias 05, 06, 07, 08, 09 e 10/10).
    - **4.287 pedidos adicionais resgatados e incorporados** à base de dados.
    - As pendências de backfill em Franquias caíram para 32 lojas.
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados totalmente reconciliada e robusta até 11/10/2026.
  - Painéis de Franquias e Lojas Próprias prontos e alinhados para deploy.
- **Qual é o próximo passo exato**:
  - Realizar commit e push para o repositório GitHub (`main`) para acionar o deploy automático no Cloudflare Pages.
  - Na quarta-feira (amanhã ou pós-fechamento), avançar a nova semana (`12 a 18`) removendo a primeira semana (`14 a 20`) conforme combinado.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
