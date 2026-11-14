# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-14 15:40
- **O que foi feito**:
  - Executada extração de 2 novos dias e varredura profunda no portal PWR cobrindo os dias recentes (01/11 a 13/11/2026).
  - Extraídos e incorporados 2 novos dias:
    - **12/11 (Quinta)**: **9.446 pedidos**.
    - **13/11 (Sexta - ontem)**: **16.455 pedidos**.
    - Total de **25.901 novos pedidos** adicionados à base.
  - Atualização da 4ª semana (`09 a 13`):
    - A semana em andamento avançou para 5 dias consolidados (`09 a 13`), cobrindo de segunda a sexta-feira.
    - As 4 semanas vigentes agora são: **`19 a 25`**, **`26 a 01`**, **`02 a 08`** (todas 100% fechadas com 7 dias) e **`09 a 13`** (em andamento, seg a sex).
  - Executado backfill retroativo profundo de subidas tardias:
    - **44 lojas recuperadas** que haviam subido vendas tardiamente no PWR (destaque para 33 lojas recuperadas na quarta-feira 11/11, 8 lojas em 10/11 e 3 lojas em 09/11).
    - **1.749 pedidos adicionais resgatados e incorporados** à base de dados.
    - Total de dias carregados na base subiu de 87 para **89 dias consolidados** (17/08 a 13/11).
  - **Correção da loja Jardim Botânico (19693)**:
    - Identificado que no relatório PWR do tipo *Service Exceptions*, a loja 19693 (e algumas outras) vinha com o campo `Delv Order Count` como NaN/vazio pelo sistema da Domino's, apesar de possuir eADT, % de Extremos e contagem de pedidos normalmente registrados no *Keys Summary*.
    - Como o cálculo ponderava pelo total de entregas, o divisor zerado resultava em ADT/Extremos 0.00 no painel.
    - Foi aprimorado o script `atualizar_painel.py` para utilizar fallback inteligente nos pedidos da loja caso o PWR reporte entregas vazias, restaurando com perfeição o ADT e Extremes históricos e semanais da loja Jardim Botânico (ex: Sem. 09 a 13: ADT 34.25 min, Extremes 27.08%; Acumulado Nov: ADT 40.49 min).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 13/11/2026.
  - Loja Jardim Botânico (19693) com dados históricos e semanais totalmente exibidos.
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
