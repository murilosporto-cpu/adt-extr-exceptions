# INSTRUÇÕES PARA O ANTIGRAVITY — Automação de extração PWR

> Leia com atenção. A lógica de "quais planilhas manter nas pastas" MUDOU.
> Antes, o robô decidia sozinho o que adicionar/remover a cada dia — isso causava
> looping e bagunça nas viradas de semana/mês. Agora essa decisão é de UM script
> determinístico. **Não reimplemente essa lógica. Apenas execute o plano.**

---

## ⭐ REGRA DE OURO (leia antes de tudo)

**Uma extração NÃO está concluída até a TRAVA confirmar.**

Depois de baixar QUALQUER coisa do PWR, rode `validar_extracao.ps1`. Só considere o
trabalho terminado quando ele disser **"OK! ... todos com o conteudo certo"**.

Baixar um arquivo NÃO é garantia de que veio o relatório certo — o PWR tem relatórios
parecidos (Summary vs Service Exceptions) e é fácil pegar o errado. **Só a trava garante.**
Nunca gere o `data.json` nem dê `git push` antes do "OK" da trava. Se a trava acusar erro,
o trabalho ainda não acabou: corrija (rebaixe o relatório certo) e rode a trava de novo.

---

## 1. Estrutura do projeto

Raiz: `cafe-com-pwr` (é um repo git → GitHub `adt-extr-exceptions`). Contém:

- `index.html` — portal (2 painéis)
- `franquias/` — painel das franquias (scope no PWR = **"Franquias"**)
- `lojas-proprias/` — painel das lojas próprias (scope no PWR = **"Lojas Corporativas"**)
- `plano_extracao.ps1` — **o cérebro** (na raiz; cuida dos dois painéis)

Cada painel tem suas próprias pastas: `pwr_reports/`, `pwr_reports_mensal/`,
seu `watch_pwr.ps1` e seu `data.json`.

---

## 2. Fluxo diário CORRETO (rodar às 13h)

**Passo 1 — Planejar e limpar:** na raiz, rode:
```
powershell -ExecutionPolicy Bypass -File .\plano_extracao.ps1 -Apply
```
Isso: (a) move arquivos errados/velhos para `_lixeira_pwr` (NÃO apague essa lixeira),
e (b) gera `downloads_pendentes.json` com a lista EXATA do que baixar.

**Passo 2 — Baixar do PWR:** abra `downloads_pendentes.json`. Para CADA item, baixe no PWR:
- painel = campo `scope` ("Franquias" ou "Lojas Corporativas")
- relatório = campo `relatorio` ("summary" ou "exceptions")
- período = de `data_inicio` até `data_fim`
- salve em `pasta` com o nome EXATO de `nome_arquivo`

> 🚨 **ERRO JÁ COMETIDO — NÃO REPETIR (02/08/2026):** ao baixar os itens de `exceptions`,
> o robô baixou por engano o relatório **Summary** e salvou com o nome de Exceptions.
> Resultado: a coluna Service Exceptions ficou vazia e o ADT dobrou.
> **Quando `relatorio` = "exceptions", selecione no PWR o relatório de SERVICE EXCEPTIONS,
> não o Summary.** Como conferir: abrir o .xlsx baixado e olhar o nome da aba —
> Exceptions correto tem a aba **"KEYS Service Exceptions"**. Se a aba for
> "KEYS Keys Summary", VOCÊ BAIXOU O RELATÓRIO ERRADO — refaça.

**Passo 2.5 — VALIDAR (obrigatório):** rode na raiz:
```
powershell -ExecutionPolicy Bypass -File .\validar_extracao.ps1
```
Ele confere o CONTEÚDO de cada arquivo baixado. Se algum Exceptions vier com dado de
Summary (erro do dia 02/08), ele move pra lixeira e acusa. Se acusar erro (sai com "ATENCAO"),
volte ao Passo 1 e rebaixe SÓ os itens acusados — com o relatório CERTO. Só siga para o
Passo 3 quando o validador disser "OK! ... todos com o conteudo certo".

**Passo 3 — Gerar os dados:** rode o `watch_pwr.ps1` de CADA painel para gerar o `data.json`.
⚠️ Atenção: o `watch_pwr.ps1` gera o `data.json` e DEPOIS sobe um servidor local (fica travado).
Encerre o processo assim que aparecer "data.json gerado com sucesso".

**Passo 4 — Publicar:** `git add -A` → `git commit` → `git push`.

---

## 3. Regras que o `plano_extracao.ps1` já aplica (NÃO refaça isso na mão)

- **Dado fecha só até ONTEM** (o PWR trabalha com D-1).
- **Pasta semanal (`pwr_reports`)**: sempre **4 semanas + 1 acumulado**.
  - Semana = segunda a domingo.
  - A semana atual "estica" até ontem. Por causa do D-1, a semana nova só aparece na TERÇA.
  - Quando entra semana nova, a mais antiga sai.
  - Acumulado = do dia 01 do mês (de ontem) até ontem.
- **Pasta mensal (`pwr_reports_mensal`)**: 1 arquivo por mês, de janeiro até o mês de ontem.
  Mês fechado = mês inteiro; mês corrente = 01 até ontem. Guarda o ano todo.
- **Arquivos VOLÁTEIS** (semana atual, acumulado, mês corrente): são SEMPRE re-baixados
  e a versão antiga vai pra lixeira. **Isso é essencial** — se sobrar um arquivo velho
  com o mesmo nome (ex.: um Summary acumulado sem o par Exceptions), tudo bagunça de novo.
- Vale para os **dois relatórios** (Summary + Exceptions) e os **dois painéis**.

Formato dos nomes:
- `Keys Summary - <scope> (Stores)(AAAA-MM-DD - AAAA-MM-DD).xlsx`
- `KEYS Service Main Service Exceptions - <scope> (Stores)(AAAA-MM-DD - AAAA-MM-DD).xlsx`
- acumulado do semanal leva ` acumulado` antes do `.xlsx`.

---

## 4. O que NÃO fazer (pra não bagunçar de novo)

- ❌ NÃO recalcule "o que tira/põe" comparando com ontem. Use SEMPRE o `plano_extracao.ps1`.
- ❌ NÃO baixe nada fora do `downloads_pendentes.json`.
- ❌ NÃO deixe mais de 4 semanas, nem 2 acumulados na pasta semanal.
- ❌ NÃO coloque " acumulado" no nome dos arquivos mensais.
- ❌ NÃO renomeie/mova os arquivos corretos, nem mexa em `_lixeira_pwr`.

---

## 5. TAREFA DE HOJE (o robô não rodou às 13h)

As pastas já foram limpas e o `downloads_pendentes.json` já está gerado com as
pendências de hoje (dados até ONTEM). Rode o **Passo 2 em diante** agora:
baixe todos os itens do `downloads_pendentes.json`, gere os `data.json` e dê push.

São, em resumo:
- **Franquias** — semanal: semana atual + acumulado; mensal: fechar julho + criar agosto.
- **Lojas próprias** — semanal: semana atual + acumulado; mensal: criar agosto.
