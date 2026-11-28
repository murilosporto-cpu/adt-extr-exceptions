# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-11-27 21:15
- **O que foi feito**:
  - Implementado o agendamento diário automático e autônomo para varredura e atualização do painel às **22h00**:
    - **`executar_agendamento_diario.py`**: Orquestrador autônomo em Python que:
      1. Faz sincronização preliminar via `git pull --rebase origin main`.
      2. Determina automaticamente o dia anterior (ontem) e uma janela móvel de segurança dos últimos 10 dias para varredura de subidas tardias.
      3. Aciona o robô Playwright `varredura_backfill_pwr.py` para extrair Keys Summary e Service Exceptions.
      4. Executa `atualizar_painel.py` recalculando métricas de eADT ponderado, extremos e dias faltantes.
      5. Aplica cache-busting nos arquivos HTML e sincroniza os dados para a pasta espelho `novo projeto/`.
      6. Atualiza o arquivo `STATUS.md` registrando a execução.
      7. Faz commit e push automático na branch `main` do GitHub para deploy contínuo no Cloudflare Pages.
      8. Registra logs completos e com timestamp em `logs/execucao_agendada.log`.
    - **`EXECUTAR_AGENDAMENTO_DIARIO.bat`**: Script executável silencioso (sem flags interativas ou comandos `pause`), com redirecionamento de logs.
    - **Registro no Agendador de Tarefas do Windows (Task Scheduler)**:
      - Tarefa: `Dominos_PWR_Varredura_Diaria`
      - Frequência: Diária (`/sc daily`)
      - Horário: **22:00:00**
      - Próxima execução: **27/11/2026 às 22:00:00**
      - Status: **Pronto / Habilitado**
  - **Suíte de Testes Automatizados**:
    - Criado runner `run_tests.py` na raiz (compatível com `python -m unittest` e `pytest`).
    - Criados testes unitários em `tests/test_atualizar_painel.py` e `tests/test_agendamento.py`.
    - Todos os 7 testes automatizados executados e aprovados com 100% de sucesso.
- **Estado atual do código**:
  - Agendador de Tarefas do Windows configurado e ativo para disparar diariamente às 22h00.
  - Scripts de orquestração autônoma e wrapper batch testados e operacionais.
  - Suíte de testes automatizados integrada e validada (7/7 testes aprovados).
  - Base de dados pronta para a execução automática de hoje às 22:00.
- **Qual é o próximo passo exato**:
  - O sistema executará automaticamente hoje às 22:00 a varredura até ontem (26/11) e publicará o resultado no Cloudflare Pages.

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
- tests/: Suíte de testes automatizados de regras de negócio, dados e agendamento.
- run_tests.py: Test runner executável para validação contínua da integridade do projeto.