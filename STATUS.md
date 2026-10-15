# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-15 17:20
- **O que foi feito**:
  - Realizada a rotação semanal das 4 semanas no painel:
    - Retirada com sucesso a primeira semana (**`14 a 20`**).
    - Adicionada a semana atual em andamento: **`12 a 14`** (segunda a quarta-feira).
    - As 4 semanas ativas agora são: **`21 a 27`**, **`28 a 04`**, **`05 a 11`** (fechada) e **`12 a 14`** (em andamento).
  - Executada varredura profunda no portal PWR em 17 datas:
    - Baixados 3 novos dias: **12/10** (18.049 pedidos), **13/10** (8.856 pedidos) e **14/10** (7.234 pedidos). Total de **34.139 pedidos** incorporados da semana atual.
    - Executado backfill retroativo em 14 datas de Outubro/Setembro: **54 lojas recuperadas** e **4.075 pedidos adicionais resgatados**.
    - Total de dias carregados na base subiu de 56 para **59 dias** (17/08 a 14/10).
  - Reconstruídos `data.json` e `data.js` para Franquias e Lojas Próprias com atualização de cache-busting nos arquivos HTML.
  - Sincronização completa realizada para `novo projeto/`.
- **Estado atual do código**:
  - Rotação concluída sem qualquer inconsistência ou quebra de layout.
  - Painéis de Franquias e Lojas Próprias atualizados e prontos para deploy.
- **Qual é o próximo passo exato**:
  - Realizar commit e push para o repositório GitHub (`main`) para acionar o deploy automático no Cloudflare Pages.
  - Apresentar o resumo das semanas e dados resgatados ao usuário.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
