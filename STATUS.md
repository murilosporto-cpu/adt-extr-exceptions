# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-16 13:40
- **O que foi feito**:
  - Executada extração de 2 novos dias e varredura profunda no portal PWR cobrindo os dias recentes (09/11 a 15/11/2026).
  - Extraídos e incorporados 2 novos dias:
    - **14/11 (Sábado)**: **19.541 pedidos**.
    - **15/11 (Domingo - ontem)**: **15.829 pedidos** (fechando a semana `09 a 15` com 7 dias completos).
    - Total de **35.370 novos pedidos** adicionados à base.
  - Fechamento da 4ª semana (`09 a 15`):
    - A semana `09 a 15` agora está 100% fechada com os 7 dias completos (09/11 a 15/11).
    - As 4 semanas do painel estão todas consolidadas com 7 dias fechados: **`19 a 25`**, **`26 a 01`**, **`02 a 08`** e **`09 a 15`**.
  - Executado backfill retroativo profundo de subidas tardias:
    - **39 lojas recuperadas** que haviam subido vendas tardiamente no PWR (destaque para 30 lojas recuperadas na sexta-feira 13/11, 4 lojas em 12/11, 3 lojas em 11/11 e 2 lojas em 10/11).
    - **2.950 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 89 para **91 dias consolidados** (17/08 a 15/11).
  - Loja Jardim Botânico (19693) com a semana `09 a 15` totalmente consolidada (eADT 38.21 min, Extremes 32.50%, 461 pedidos; Acumulado Nov: eADT 41.09 min, 1.008 pedidos).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 15/11/2026.
  - As 4 semanas vigentes estão 100% fechadas com 7 dias cada.
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
