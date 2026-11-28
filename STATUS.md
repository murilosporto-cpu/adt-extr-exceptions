# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-27 22:05 (Execução Automática Agendada - 22h00)
- **O que foi feito**:
  - Rotina de agendamento diário executada com sucesso.
  - Varredura retroativa e extração do portal PWR realizadas cobrindo o dia anterior (2026-11-26) e janela móvel de segurança de 10 dias.
  - Base histórica consolidada com **102 dias** (última data: 2026-11-26).
  - Métricas e relatórios reconciliados: `data.json`, `data.js` e cache-busting atualizados.
  - Dados sincronizados para a pasta espelho `novo projeto/`.
  - Publicação automática enviada para o GitHub e Cloudflare Pages via push na branch `main`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até 2026-11-26.
  - Rotina diária das 22h00 ativa e operando de forma autônoma.
  - Site em produção atualizado: https://adt-extr-exceptions.pages.dev/
- **Qual é o próximo passo exato**:
  - Próxima execução automática agendada para amanhã às 22h00 via Agendador de Tarefas do Windows (Tarefa: `Dominos_PWR_Varredura_Diaria`).

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
- executar_agendamento_diario.py: Orquestrador autônomo da rotina diária (extração, cálculo, status, commit e push).
- EXECUTAR_AGENDAMENTO_DIARIO.bat: Script acionado pelo Agendador de Tarefas do Windows (Task Scheduler).
- logs/execucao_agendada.log: Histórico e logs de todas as execuções diárias automáticas.
