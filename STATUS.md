# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-10 15:50
- **O que foi feito**:
  - Varredura de subida tardia (backfill) executada cobrindo 10 datas (30/09 a 09/10).
  - 50 lojas que haviam subido vendas tardiamente foram recuperadas, somando 2.800 pedidos adicionais.
  - Novos relatórios oficiais dos dias 08/10 (quinta) e 09/10 (sexta) baixados do PWR (9.224 e 15.041 pedidos).
  - Total da base ampliado para 54 dias analisados (17/08 a 09/10).
  - Semanas atualizadas para: 14 a 20, 21 a 27, 28 a 04 e 05 a 09 (segunda a sexta de Outubro).
  - Mês de Outubro consolidado com os primeiros 9 dias do mês.
  - Cache-busting automático renovado em todos os arquivos HTML.
  - Arquivos sincronizados em franquias/, lojas-proprias/ e novo projeto/.
- **Estado atual do código**:
  - Base de dados 100% atualizada e consistente até 09/10/2026.
  - Painéis de Franquias e Lojas Próprias prontos para visualização online.
- **Qual é o próximo passo exato**:
  - Fazer commit e push para o repositório GitHub para publicação automática no Cloudflare Pages.
  - Aguardar fechamento do final de semana (10 e 11/10) na próxima segunda-feira para fechar a semana 05 a 11.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
