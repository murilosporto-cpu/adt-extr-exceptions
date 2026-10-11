# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: 2026-10-11 12:55
- **O que foi feito**:
  - Investigado o ponto levantado pelo usuário sobre as lojas 19602 (Campo Grande) e 19693 (Jardim Botânico) estarem com dezenas de dias faltantes na aba Auditoria desde 24/08.
  - Identificado que o relatório consolidado do PWR do usuário abrangia o período de 24/08 a 26/09/2026, e que essas vendas foram subidas tardiamente no PWR mas nunca haviam sido re-extraídas porque as varreduras anteriores focavam apenas em Outubro.
  - Executada varredura profunda de 34 datas no PWR cobrindo todo o intervalo de 24/08 a 26/09/2026.
  - Recuperadas 193 lojas com subidas tardias e 11.448 pedidos adicionais resgatados na rede inteira.
  - Para a 19602 (Campo Grande): resgatadas 33 datas com 275 pedidos (dias faltantes caíram de 47 para apenas 14).
  - Para a 19693 (Jardim Botânico): resgatadas todas as 34 datas com 2.053 pedidos (dias faltantes caíram de 41 para apenas 14).
  - Total de dias ausentes do consultor Murilo no card de Auditoria despencou de 98 para 38 dias.
  - Reconstruídos data.json e data.js com métricas semanais das semanas 14 a 20 e 21 a 27 atualizadas com os novos pedidos.
  - Arquivos sincronizados em franquias/, lojas-proprias/ e novo projeto/.
- **Estado atual do código**:
  - Base de dados 100% alinhada com o portal PWR para os períodos históricos e recentes.
  - Painel online pronto para deploy.
- **Qual é o próximo passo exato**:
  - Fazer commit e push para o repositório GitHub para publicação automática no Cloudflare Pages.
  - Apresentar o comparativo antes x depois ao usuário com total transparência.

---

## 🗂️ Estrutura do Projeto
- dados_all_stores/: Planilhas diárias .xlsx de Keys Summary e KEYS Service Exceptions extraídas do PWR.
- franquias/: Painel web das franquias (index.html, app.js, data.json, data.js).
- lojas-proprias/: Painel web de lojas próprias corporativas.
- novo projeto/: Espelho do projeto para sincronização e redundância.
- varredura_backfill_pwr.py: Robô Playwright que faz varredura e download das planilhas do portal PWR.
- atualizar_painel.py: Consolidador de regras PWR (eADT ponderado, extremos, exceções, fechamento semanal/mensal e detecção de faltantes).
