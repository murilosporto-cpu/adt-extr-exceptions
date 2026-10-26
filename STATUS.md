# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-26 14:20
- **O que foi feito**:
  - Executada varredura profunda no portal PWR em 25 datas de Outubro (01/10 a 25/10/2026).
  - Extraídos e consolidados 3 novos dias do fim de semana:
    - **23/10 (Sexta)**: **18.810 pedidos**.
    - **24/10 (Sábado)**: **18.279 pedidos**.
    - **25/10 (Domingo - ontem)**: **14.694 pedidos**.
    - Total de **51.783 novos pedidos** adicionados à base.
  - Com o domingo 25/10, a semana **`19 a 25` foi oficialmente fechada** com os 7 dias completos.
  - As 4 semanas móveis do painel agora estão perfeitamente fechadas:
    - **`28 a 04`** (Set/Out - Fechada)
    - **`05 a 11`** (Outubro - Fechada)
    - **`12 a 18`** (Outubro - Fechada)
    - **`19 a 25`** (Outubro - Fechada)
  - Executado backfill retroativo de subidas tardias:
    - **45 lojas recuperadas** que haviam subido vendas com atraso no PWR (destaque para a quinta-feira 22/10 com 33 lojas recuperadas, além de resgates nos dias 13, 20 e 21/10).
    - **2.165 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 67 para **70 dias consolidados** (17/08 a 25/10).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 25/10/2026.
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
