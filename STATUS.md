# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-26 13:20
- **O que foi feito**:
  - Extraído 1 novo dia do portal PWR:
    - **25/11 (Quarta-feira - ontem)**: **8.372 pedidos**.
  - Executada varredura retroativa profunda e direcionada cobrindo de **09/11 a 24/11**:
    - **Recuperação completa da Loja 19602**: Resgatadas todas as vendas que haviam subido com atraso pelo time da loja no PWR:
      - 09/11: 6 pedidos recuperados
      - 10/11: 3 pedidos recuperados
      - 11/11: 13 pedidos recuperados
      - 12/11: 4 pedidos recuperados
      - 13/11: 9 pedidos recuperados
      - 24/11: 5 pedidos recuperados
      - 25/11: 7 pedidos consolidados
      - Total da loja 19602 devidamente restaurado em todo o histórico de novembro.
    - **Total geral de lojas recuperadas na varredura retroativa**: **35 lojas** com subidas tardias resgatadas (24 lojas em 24/11 e 11 lojas no período de 09 a 14/11).
    - **1.455 pedidos adicionais resgatados e incorporados** à base de dados.
  - Janela móvel de 4 semanas atualizada:
    - **`02 a 08`** (7 dias fechados)
    - **`09 a 15`** (7 dias fechados)
    - **`16 a 22`** (7 dias fechados)
    - **`23 a 25`** (em andamento, Segunda a Quarta com 3 dias completos)
  - Base histórica total expandida de 100 para **101 dias consolidados** (17/08 a 25/11/2026).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 25/11/2026.
  - Loja 19602 totalmente atualizada e com histórico de novembro corrigido.
  - Janela móvel de 4 semanas atualizada (`02 a 08`, `09 a 15`, `16 a 22` e `23 a 25`).
  - Painéis sincronizados, com cache-busting renovado.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento dos próximos dias da semana (26/11 em diante) para a próxima varredura de rotina.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
