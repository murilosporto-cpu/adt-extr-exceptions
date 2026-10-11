# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-11 12:05
- **O que foi feito**:
  - Varredura de subida tardia (backfill) executada cobrindo 10 datas (01/10 a 10/10).
  - 30 lojas que haviam subido vendas tardiamente foram recuperadas, somando 2.030 pedidos adicionais (destaque para a sexta-feira 09/10, onde 27 lojas recuperaram subidas, incluindo Cuiabá, Jaraguá BH e Taguatinga Norte de Murilo Porto).
  - Novo relatório oficial do dia 10/10 (sábado) baixado do portal PWR (13.346 pedidos).
  - Total da base ampliado para 55 dias analisados (17/08 a 10/10).
  - Semanas atualizadas para: 14 a 20, 21 a 27, 28 a 04 e 05 a 10 (segunda a sábado de Outubro).
  - Mês de Outubro consolidado com os primeiros 10 dias do mês.
  - Cache-busting automático atualizado para v=202610111201 em todos os arquivos HTML.
  - Arquivos sincronizados em franquias/, lojas-proprias/ e novo projeto/.
- **Estado atual do código**:
  - Base de dados 100% consistente e atualizada até 10/10/2026.
  - Painéis de Franquias e Lojas Próprias prontos e validados.
- **Qual é o próximo passo exato**:
  - Fazer commit e push para o repositório GitHub para publicação automática no Cloudflare Pages.
  - Na segunda-feira (12/10), rodar varredura para extrair o domingo (11/10) e fechar a semana completa 05 a 11.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
