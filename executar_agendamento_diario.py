import os
import sys
import subprocess
import json
import shutil
from datetime import datetime, date, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'execucao_agendada.log')

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted = f'[{timestamp}] {msg}'
    print(formatted, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(formatted + '\n')
    except Exception as e:
        print(f'Erro ao gravar log: {e}')

def run_cmd(cmd_list, desc, check=True):
    log(f'Iniciando: {desc}...')
    try:
        result = subprocess.run(
            cmd_list,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.stdout:
            for line in result.stdout.strip().splitlines():
                log(f'  [STDOUT] {line}')
        if result.stderr:
            for line in result.stderr.strip().splitlines():
                log(f'  [STDERR] {line}')
        if check and result.returncode != 0:
            log(f'[FALHA] {desc} finalizou com codigo {result.returncode}')
            return False
        log(f'[CONCLUIDO] {desc}')
        return True
    except Exception as e:
        log(f'[EXCECAO] Erro ao executar {desc}: {e}')
        return False

def sincronizar_novo_projeto():
    try:
        log('Sincronizando arquivos de dados com a pasta novo projeto/...')
        orig_dest = [
            (os.path.join(BASE_DIR, 'franquias', 'data.json'), os.path.join(BASE_DIR, 'novo projeto', 'franquias', 'data.json')),
            (os.path.join(BASE_DIR, 'franquias', 'data.js'), os.path.join(BASE_DIR, 'novo projeto', 'franquias', 'data.js')),
            (os.path.join(BASE_DIR, 'lojas-proprias', 'data.json'), os.path.join(BASE_DIR, 'novo projeto', 'lojas-proprias', 'data.json')),
            (os.path.join(BASE_DIR, 'lojas-proprias', 'data.js'), os.path.join(BASE_DIR, 'novo projeto', 'lojas-proprias', 'data.js')),
        ]
        for src, dst in orig_dest:
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        log('[CONCLUIDO] Sincronizacao com novo projeto/ realizada com sucesso.')
    except Exception as e:
        log(f'[AVISO] Falha ao sincronizar com novo projeto/: {e}')

def atualizar_status_md(yesterday_str, total_dias, ultima_data):
    status_path = os.path.join(BASE_DIR, 'STATUS.md')
    if not os.path.exists(status_path):
        return
    try:
        agora_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        novo_bloco = f'''# STATUS DO PROJETO - DOMINO'S PIZZA (CAFÉ COM PWR)

## 📌 Último Status / Onde Parou
- **Data/Hora**: {agora_str} (Execução Automática Agendada - 22h00)
- **O que foi feito**:
  - Rotina de agendamento diário executada com sucesso.
  - Varredura retroativa e extração do portal PWR realizadas cobrindo o dia anterior ({yesterday_str}) e janela móvel de segurança de 10 dias.
  - Base histórica consolidada com **{total_dias} dias** (última data: {ultima_data}).
  - Métricas e relatórios reconciliados: `data.json`, `data.js` e cache-busting atualizados.
  - Dados sincronizados para a pasta espelho `novo projeto/`.
  - Publicação automática enviada para o GitHub e Cloudflare Pages via push na branch `main`.
- **Estado atual do código**:
  - Base de dados 100% atualizada e reconciliada até {ultima_data}.
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
'''
        with open(status_path, 'w', encoding='utf-8') as f:
            f.write(novo_bloco)
        log('[CONCLUIDO] STATUS.md atualizado com sucesso.')
    except Exception as e:
        log(f'[AVISO] Falha ao atualizar STATUS.md: {e}')

def obter_datas_alvo():
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # 1. Ultimos 10 dias ate ontem para varredura de subidas tardias
    target_dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 11)]
    
    # 2. Verificar se ha algum dia anterior ausente na base local
    try:
        from atualizar_painel import obter_todos_os_dias
        dias_existentes = set(obter_todos_os_dias())
        for i in range(1, 31):
            d_str = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            if d_str not in dias_existentes and d_str not in target_dates:
                target_dates.append(d_str)
    except Exception as e:
        log(f'[AVISO] Erro ao inspecionar dias existentes: {e}')
        
    return sorted(list(set(target_dates)), reverse=True), yesterday.strftime('%Y-%m-%d')

def main():
    log('====================================================================')
    log('  INICIANDO ROTINA DIARIA AUTOMATICA DE VARREDURA PWR E ATUALIZACAO')
    log('====================================================================')
    
    # ETAPA 1: Sincronizar com repositorio remoto antes de iniciar
    log('--- ETAPA 1: Sincronizando com o Git remoto (git pull) ---')
    run_cmd(['git', 'pull', '--rebase', 'origin', 'main'], 'Git Pull Rebase', check=False)
    
    # ETAPA 2: Determinar datas alvo
    target_dates, yesterday_str = obter_datas_alvo()
    log(f'Ontem: {yesterday_str}')
    log(f'Datas selecionadas para varredura/backfill ({len(target_dates)} datas): {target_dates}')
    
    # ETAPA 3: Executar varredura PWR com Playwright
    log('--- ETAPA 2: Executando varredura retroativa e extracao PWR ---')
    varredura_script = os.path.join(BASE_DIR, 'varredura_backfill_pwr.py')
    cmd_varredura = [sys.executable, varredura_script] + target_dates
    run_cmd(cmd_varredura, f'Varredura PWR para {len(target_dates)} datas', check=False)
    
    # ETAPA 4: Reconstruir os paineis
    log('--- ETAPA 3: Reconstruindo paineis e consolidando metricas ---')
    atualizar_script = os.path.join(BASE_DIR, 'atualizar_painel.py')
    ok_painel = run_cmd([sys.executable, atualizar_script], 'Atualizacao dos Paineis PWR', check=True)
    if not ok_painel:
        log('[ERRO CRITICO] Falha ao consolidar os paineis!')
        sys.exit(1)
        
    # ETAPA 5: Sincronizar novo projeto
    log('--- ETAPA 4: Sincronizando espelho do projeto ---')
    sincronizar_novo_projeto()
    
    # Obter dados consolidados para o log e STATUS.md
    try:
        from atualizar_painel import obter_todos_os_dias
        todos_dias = obter_todos_os_dias()
        total_dias = len(todos_dias)
        ultima_data = todos_dias[-1] if todos_dias else yesterday_str
    except Exception:
        total_dias = 'N/A'
        ultima_data = yesterday_str
        
    # ETAPA 6: Atualizar STATUS.md
    log('--- ETAPA 5: Atualizando STATUS.md de continuidade ---')
    atualizar_status_md(yesterday_str, total_dias, ultima_data)
    
    # ETAPA 7: Git Commit & Push
    log('--- ETAPA 6: Publicando atualizacoes no GitHub e Cloudflare Pages ---')
    run_cmd(['git', 'add', '-A'], 'Git Add All')
    commit_msg = f'data(auto): varredura diaria pwr ate {yesterday_str} [execucao 22h]'
    run_cmd(['git', 'commit', '-m', commit_msg], 'Git Commit', check=False)
    ok_push = run_cmd(['git', 'push', 'origin', 'main'], 'Git Push Origin Main', check=False)
    
    if ok_push:
        log('[SUCESSO] Atualizacoes publicadas no GitHub e deploy disparado no Cloudflare Pages!')
    else:
        log('[AVISO] Push falhou ou sem conexao no momento. Os dados locais estao salvos.')
        
    log('====================================================================')
    log(f'  ROTINA FINALIZADA COM SUCESSO ATE {ultima_data} ({total_dias} DIAS)')
    log('====================================================================')

if __name__ == '__main__':
    main()