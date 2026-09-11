# MODELO DE RELATÓRIO PÓS-VISITA (E-MAIL DE CONSULTORIA)

Este documento padroniza o formato, o tom de voz e as métricas do e-mail de pós-visita enviado aos franqueados. O modelo foi extraído a partir da referência de campo (Loja Anápolis / Consultor Murilo Porto) e desenhado para ser preenchido de forma ágil com extrações do **PWR (Pulse Web Reporting)** e auditorias de loja.

---

## 1. CABEÇALHO & METADADOS DO E-MAIL

* **Assunto:** `Pós Visita ({{NOME_LOJA}}) e panorama da operação`
* **De:** `{{NOME_CONSULTOR}} <{{EMAIL_CONSULTOR}}>`
* **Para:** `{{NOME_FRANQUEADO}} <{{EMAIL_FRANQUEADO}}>`
* **Cc:** `{{SUPERVISOR_REGIONAL}} <{{EMAIL_SUPERVISOR}}>, {{DIRETORIA}} <{{EMAIL_DIRETORIA}}>`
* **Anexo Obrigatório:** `Exportable Ops Assessment Report - {{NUMERO_LOJA}} ({{DATA_VISITA_FORMATO_ISO}}).pdf`
* **Classificação da Informação:** `Público` / `Uso Interno`

---

## 2. ESTRUTURA E TOM DE ESCRITA DO E-MAIL

### Diretrizes de Tom e Postura:
1. **Acolhedor e Construtivo:** Inicia sempre reconhecendo pontos positivos reais (limpeza, organização, controle de desperdício, engajamento).
2. **Consultivo e Orientado a Fatos:** Apresenta números comparados a benchmarks (Brasil e Regional) sem tom punitivo.
3. **Plano de Ação Integrado:** Cada gargalo identificado (ex: ADT alto, CMV acima do ideal, cancelamentos TIGER) é imediatamente acompanhado do motivo ("Por quê") e da ação prática ("O que foi feito ou será feito").
4. **Alinhamento Humano e Estrutural:** Encerra abordando pessoas (liderança local, retenção) e iniciativas de médio prazo (totem, parcerias de RH, vendas locais).

---

## 3. TEMPLATE TEXTUAL DO E-MAIL (PRONTO PARA USO)

```text
Classificação da Informação: Público

Bom dia, {{NOME_FRANQUEADO}},

{{PARAGRAFO_QUALITATIVO_VISITA}}
(Exemplo: Tive ontem uma grata surpresa ao visitar a loja {{NOME_LOJA}}, encontrei uma loja limpa, organizada e com insumos coerentes com a venda da loja, sinal que as sugestões de pedidos semanais e o controle de desperdício tem funcionado de forma brilhante.)

Este e-mail traz o panorama detalhado da unidade {{NOME_LOJA}}. Em anexo, envio o relatório de OSA realizado ontem. A seguir, compartilho os principais indicadores consolidados (SSS, SSO, ADT, Extremos, NPS e Exceptions):

1. Same Store Sales (SSS) & Panorama Regional

No comparativo com a média nacional, a loja apresenta {{RESUMO_TENDENCIA_SSS}} (ex: uma queda expressiva / um crescimento consistente):

• Brasil: {{SSS_BRASIL_PERIODO}} em faturamento | {{SSO_BRASIL_PERIODO}} em pedidos
• {{NOME_LOJA}}: {{SSS_LOJA_PERIODO}} em faturamento | {{SSO_LOJA_PERIODO}} em pedidos

Abertura por unidade:
• Q1 (1º Tri): {{NOME_LOJA}}: {{SSS_LOJA_Q1}}
• Q2 (2º Tri): {{NOME_LOJA}}: {{SSS_LOJA_Q2}}
• YTD ({{PERIODO_YTD_EXTENSO}}): {{NOME_LOJA}}: {{SSS_LOJA_YTD}}

2. Same Store Orders (SSO)

• Q1 (1º Tri): {{NOME_LOJA}}: {{SSO_LOJA_Q1}}
• Q2 (2º Tri): {{NOME_LOJA}}: {{SSO_LOJA_Q2}}
• YTD ({{PERIODO_YTD_EXTENSO}}): {{NOME_LOJA}}: {{SSO_LOJA_YTD}}

3. Average Delivery Time (ADT)

{{COMENTARIO_EVOLUCAO_ADT}}
(Exemplo: As lojas vêm apresentando uma evolução consistente nos tempos de entrega. Ajustamos quinzenalmente a escala dos especialistas e acompanhamos a eficiência semanalmente para alavancar a performance individual da equipe.)

• Q1 (1º Tri): {{NOME_LOJA}}: {{ADT_LOJA_Q1}} min
• Q2 (2º Tri): {{NOME_LOJA}}: {{ADT_LOJA_Q2}} min
• YTD ({{PERIODO_YTD_EXTENSO}}): {{NOME_LOJA}}: {{ADT_LOJA_YTD}} min

4. Pedidos Extremos (> 40 min)

• Q1 (1º Tri): {{NOME_LOJA}}: {{EXTREMES_LOJA_Q1}}%
• Q2 (2º Tri): {{NOME_LOJA}}: {{EXTREMES_LOJA_Q2}}%
• YTD ({{PERIODO_YTD_EXTENSO}}): {{NOME_LOJA}}: {{EXTREMES_LOJA_YTD}}%

{{DIRECIONAMENTO_TEMPOS_ENTREGA}}
(Exemplo: Com a melhoria dos tempos iremos colher frutos de crescimento em pedidos e faturamento, vamos seguir com esse acompanhamento diário.)

5. NPS (Net Promoter Score)

{{DIRECIONAMENTO_NPS}}
(Exemplo: Reforcei a gestão e execução do NPS com o supervisor e os gerentes. A correta mensuração do indicador nos fornecerá insights valiosos diretamente da experiência do cliente, orientando os planos de melhoria contínua.)

6. Operação & Exceptions

• Ajustes de Equipamentos / Processos: {{ACOES_EQUIPAMENTOS_FORNO}}
(Exemplo: Ajuste de Forno: Identificamos que o forno estava parametrizado para 8 minutos. Após testes práticos em loja, ajustamos o tempo de passagem para 6:30 min, adequando o equipamento à dinâmica operacional real. Seguiremos acompanhando o impacto nos tempos e na qualidade do produto.)

Obs: Como plano de ação para recuperar faturamento e volume de pedidos, {{ACOES_MARKETING_COMERCIAL}}
(Exemplo: ...o gestor tem realizado disparos de SMS direcionados tanto à base de clientes inativos quanto aos clientes fiéis (com mais de 3 compras), visando à recompra. Além disso, estamos utilizando a Marktech para ações geolocalizadas nas lojas.)

---
[INSERIR PRINTS / GRÁFICOS DO PWR DO BLOCO DE TEMPOS & VENDAS]
- Print 1: Benchmarking Vendas e Pedidos (Loja vs Brasil / Loja vs Regional CO)
- Print 2: Tabela de Evolução Mensal Vendas PCYA
- Print 3: Gráfico de ADT Mensal com meta e evolução mês a mês
- Print 4: Gráfico de Extremes % Mensal com meta e evolução mês a mês
- Print 5: Gráfico de Service Exceptions Mensal com meta e evolução mês a mês
---

7. Auditoria Operacional (TIGER)

Sobre o indicador TIGER, tivemos o seguinte cenário:
• Faturamento Total {{MES_REFERENCIA_TIGER}}: R$ {{FATURAMENTO_TOTAL_TIGER}}
• Cancelamentos Totais: R$ {{VALOR_CANCELAMENTOS_TIGER}} | {{PERC_CANCELAMENTOS_TIGER}}%
• Impacto TIGER: R$ {{VALOR_IMPACTO_TIGER}} (representando {{PERC_IMPACTO_TIGER}}% do faturamento total da loja).

Plano de Ação: {{PLANO_ACAO_TIGER}}
(Exemplo: Identificamos que grande parte dos cancelados foram devido aos erros de sistema, que nessa minha visita já conseguimos resolver boa parte.)

---
[INSERIR TABELA TIGER SUMMARY DO PULSE / PWR]
---

8. CMV Ideal Regional – {{MES_ANO_CMV}}

A loja registrou um CMV de {{CMV_REAL_LOJA}}%, ficando {{COMPARATIVO_REGIONAL}} da média da Regional {{NOME_REGIONAL}} ({{CMV_MEDIO_REGIONAL}}%). Para convergirmos com o resultado regional e otimizarmos a rentabilidade, precisamos focar nas seguintes frentes operacionais e de vendas:

• Alinhamento e direcionamento estratégico das campanhas vigentes;
• Redução de desperdícios e controle rigoroso no porcionamento/adicionais de insumos;
• Foco da equipe em venda sugestiva de acompanhamentos, sobremesas e upsell (upgrade no tamanho das pizzas).

---
[INSERIR TABELA DO PAINEL CMV DO PWR - VISÃO PRODUTOS, CANAIS E EVOLUÇÃO MENSAL]
---

9. Gestão de Equipe e Próximos Passos

Para finalizar, quero registrar a nossa atenção à {{DIAGNOSTICO_EQUIPE}}
(Exemplo: ...à dificuldade atual de contratação e retenção, que vem sobrecarregando a liderança local — que tem feito um trabalho essencial na condução da loja. Essa é uma dor que atinge várias regiões do país, mas não estamos parados diante dela.)

Frentes em andamento:
1. {{PROJETO_ESTRUTURANTE_1}} (Exemplo: Implantação do Totem: Seu pedido já foi encaminhado por e-mail e trará um ganho operacional direto no atendimento);
2. {{PROJETO_ESTRUTURANTE_2}} (Exemplo: Parceria com o SENAC: Iniciativa estratégica para abastecer o funil de recrutamento com perfis capacitados).

Contem com o nosso apoio para atravessar esse momento e equilibrar a rotina da loja.

At.te,

{{NOME_CONSULTOR}}
Franquias | Domino's Pizza
```

---

## 4. MAPEAMENTO DAS VARIÁVEIS COM RELATÓRIOS DO PWR

| Variável no Template | Relatório de Origem no PWR / Pulse | Métrica / Coluna Específica |
| :--- | :--- | :--- |
| `{{SSS_LOJA_*}}` | PWR > Sales > Same Store Sales (SSS) | % Sales Growth vs PCYA |
| `{{SSO_LOJA_*}}` | PWR > Sales > Same Store Orders (SSO) | % Orders Growth vs PCYA |
| `{{ADT_LOJA_*}}` | PWR > Operations > Keys Summary (Stores) | Average Delivery Time (min) |
| `{{EXTREMES_LOJA_*}}` | PWR > Operations > Keys Summary (Stores) | % Orders > 40 min (Extremes) |
| `{{SERVICE_EXCEPTIONS}}`| PWR > Operations > Service Exceptions | % Service Exceptions Total |
| `{{FATURAMENTO_TOTAL_TIGER}}` | Pulse / PWR > TIGER Summary | Total Sales (Mês fechado / selecionado) |
| `{{VALOR_CANCELAMENTOS_TIGER}}` | Pulse / PWR > TIGER Summary | Canceled Orders Amount (R$) e % |
| `{{VALOR_IMPACTO_TIGER}}` | Pulse / PWR > TIGER Summary | Var This Edit / Tiger Impact |
| `{{CMV_REAL_LOJA}}` | PWR > Food Cost / CMV Ideal | % CMV Gên. Loja |
| `{{CMV_MEDIO_REGIONAL}}` | PWR > Food Cost / CMV Ideal | % CMV Médio Regional CO / Brasil |
| `{{TABELA_CAMPANHAS_CMV}}` | PWR > CMV Tabelas | Custo Adicional por Campanha e Canal |

---

## 5. GUIA RÁPIDO PARA O CONSULTOR (FLUXO DE PREENCHIMENTO)

1. **Antes da Visita:**
   - Extrair o histórico dos trimestres (Q1, Q2, etc.) e YTD da loja no PWR.
   - Puxar o fechamento de CMV e TIGER do mês anterior.

2. **Durante a Visita:**
   - Executar a lista de verificação operacional (OSA).
   - Observar na prática: parametrização do forno (tempo de esteira), porcionamento na bancada makeline, organização de estoque e escala da equipe.
   - Alinhar com a gerência sobre campanhas locais (SMS, Marktech, panfletagem).

3. **Após a Visita (Envio do E-mail):**
   - Gerar o PDF de OSA e anexar ao e-mail.
   - Tirar os prints padrões dos dashboards do PWR (conforme demarcado nos blocos visuais).
   - Preencher os números consolidados no modelo de texto e enviar com cópia aos líderes regionais.
