# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-12 10:30
- **O que foi feito**:
  - Executada varredura de subida tardia (backfill) no portal PWR cobrindo 15 datas (27/09 a 11/10/2026).
  - Extraídos e consolidados os dados do dia **11/10/2026 (Domingo)**, completando e fechando oficialmente a semana **`05 a 11`** (7 dias completos).
  - Resgatadas **43 lojas** que subiram vendas tardiamente e **3.897 pedidos adicionais** incorporados na base de dados (destaque para sábado 10/10 com 34 lojas recuperadas, incluindo as lojas do escopo de Murilo Porto: 19551, 19553, 19730 e 19759).
  - A base agora possui 56 dias consolidados (17/08 a 11/10) com as 4 semanas móveis perfeitamente fechadas: `14 a 20`, `21 a 27`, `28 a 04` e `05 a 11`.
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 11/10/2026.
  - Painéis de Franquias e Lojas Próprias prontos para deploy.
- **Qual é o próximo passo exato**:
  - Realizar commit e push para o repositório GitHub (`main`) para acionar o deploy automático no Cloudflare Pages.
  - Informar ao usuário os resultados da varredura e o fechamento da semana.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
