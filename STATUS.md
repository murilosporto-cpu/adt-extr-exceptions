# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-03 11:50
- **O que foi feito**:
  - Executada extração de 3 novos dias e varredura profunda no portal PWR cobrindo 32 datas (01/10 a 01/11/2026).
  - Extraídos e incorporados 3 novos dias:
    - **30/10 (Sexta)**: **18.486 pedidos**.
    - **31/10 (Sábado)**: **17.037 pedidos** (fechando Outubro completo).
    - **01/11 (Domingo)**: **18.412 pedidos** (abrindo Novembro e fechando a 4ª semana).
    - Total de **53.935 novos pedidos** adicionados à base.
  - Fechamento da 4ª semana (`26 a 01`):
    - A semana `26 a 01` agora está 100% fechada com os 7 dias completos (26/10 a 01/11).
    - As 4 semanas do painel estão todas consolidadas com 7 dias: **`05 a 11`**, **`12 a 18`**, **`19 a 25`** e **`26 a 01`**.
  - Executado backfill retroativo de subidas tardias:
    - **44 lojas recuperadas** que haviam subido vendas tardiamente no PWR (destaque para 29/10 com 33 lojas recuperadas, 28/10 com 4 lojas, 27/10 com 3 lojas, 26/10 com 3 lojas e 20/10 com 1 loja).
    - **2.184 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 74 para **77 dias consolidados** (17/08 a 01/11).
  - Atualizado `atualizar_painel.py` para consolidar o mês de Novembro (`nov`) em `monthly_history.json`, mantendo Outubro (`out`) fechado com 31 dias.
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 01/11/2026 (fim de Outubro e encerramento da semana no domingo 01/11).
  - Commit e push concluídos com sucesso para o branch `main` (`5b16ae1`), com deploy automático no Cloudflare Pages acionado.
- **Qual é o próximo passo exato**:
  - Aguardar fechamento dos primeiros dias de Novembro (02/11 em diante) para a próxima varredura.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
