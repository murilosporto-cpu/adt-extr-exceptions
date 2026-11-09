# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-08 22:15
- **O que foi feito**:
  - Executada extração de 3 novos dias e varredura profunda no portal PWR cobrindo os dias recentes (28/10 a 07/11/2026).
  - Extraídos e incorporados 3 novos dias:
    - **05/11 (Quinta)**: **9.220 pedidos**.
    - **06/11 (Sexta)**: **17.289 pedidos**.
    - **07/11 (Sábado - ontem)**: **16.829 pedidos**.
    - Total de **43.338 novos pedidos** adicionados à base.
  - Atualização da 4ª semana (`02 a 07`):
    - A semana em andamento avançou para 6 dias consolidados (`02 a 07`), cobrindo de segunda a sábado.
    - As 4 semanas vigentes agora são: **`12 a 18`**, **`19 a 25`**, **`26 a 01`** (todas 100% fechadas com 7 dias) e **`02 a 07`** (em andamento, seg a sab).
  - Executado backfill retroativo profundo de subidas tardias:
    - **36 lojas recuperadas** que haviam subido vendas tardiamente no PWR (destaque para 33 lojas recuperadas na quarta-feira 04/11 e 3 lojas na terça-feira 03/11).
    - **1.627 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 80 para **83 dias consolidados** (17/08 a 07/11).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 07/11/2026.
  - Commit e push concluídos com sucesso para o branch `main` (`c5ba752`), com deploy automático no Cloudflare Pages acionado.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento do domingo (08/11) para concluir a semana `02 a 08` na próxima varredura.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
