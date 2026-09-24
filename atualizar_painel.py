# ==============================================================================
# ATUALIZAR PAINEL - Processamento e Consolidacao dos Relatorios PWR
# ==============================================================================
# Este script:
# 1. Le os relatorios diarios de Keys Summary e Service Exceptions em 'dados_all_stores'
# 2. Realiza a consolidacao das 4 semanas e do acumulado com a formula exata do PWR
#    (ponderacao de eADT e Extremos por pedidos de entrega / Delv Order Count)
# 3. Audita dias faltantes e gera a lista para a aba 'Auditoria de Subida'
# 4. Gera automaticamente data.json e data.js para Franquias e Lojas Proprias
# ==============================================================================

import os
import glob
import json
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(BASE_DIR, 'dados_all_stores')
FRAN_DIR = os.path.join(BASE_DIR, 'franquias')
CORP_DIR = os.path.join(BASE_DIR, 'lojas-proprias')

def obter_todos_os_dias():
    files = glob.glob(os.path.join(DADOS_DIR, 'Keys Summary - All Stores (Stores) (*).xlsx'))
    dias = []
    for f in files:
        d = f.split('(')[-1].split(')')[0]
        dias.append(d)
    return sorted(list(set(dias)))

ALL_DAYS = obter_todos_os_dias()

def calcular_periodos_e_semanas(all_days):
    from datetime import datetime, timedelta
    
    # Agrupar dias por semana ISO (segunda a domingo)
    weeks_dict = {}
    for d_str in all_days:
        dt = datetime.strptime(d_str, '%Y-%m-%d')
        mon = dt - timedelta(days=dt.weekday())
        sun = mon + timedelta(days=6)
        mon_str = mon.strftime('%Y-%m-%d')
        sun_str = sun.strftime('%Y-%m-%d')
        w_key = (mon_str, sun_str)
        weeks_dict.setdefault(w_key, []).append(d_str)
        
    sorted_week_keys = sorted(weeks_dict.keys())
    # Pegar as ultimas 4 semanas
    target_week_keys = sorted_week_keys[-4:]
    
    periods = {}
    weeks_list = []
    
    for i, (mon_str, sun_str) in enumerate(target_week_keys):
        days_in_week = sorted(weeks_dict[(mon_str, sun_str)])
        mon_day = mon_str.split('-')[-1]
        sun_day = sun_str.split('-')[-1]
        
        # Se for a ultima semana e ainda nao tiver 7 dias
        is_latest = (i == len(target_week_keys) - 1)
        if is_latest and len(days_in_week) < 7:
            last_day = days_in_week[-1].split('-')[-1]
            week_name = f"{mon_day} a {last_day}"
        else:
            week_name = f"{mon_day} a {sun_day}"
            
        periods[week_name] = days_in_week
        weeks_list.append(week_name)
        
    # Acumulado do mes atual (ou mes mais recente na base)
    latest_day = all_days[-1]
    latest_month_prefix = latest_day[:7] # ex: '2026-09'
    month_days = [d for d in all_days if d.startswith(latest_month_prefix)]
    periods['acumulado'] = month_days
    
    return periods, weeks_list

PERIODS, WEEKS_LIST = calcular_periodos_e_semanas(ALL_DAYS)

def carregar_mapeamentos():
    f_map_path = os.path.join(FRAN_DIR, 'stores_mapping.json')
    c_map_path = os.path.join(CORP_DIR, 'stores_mapping.json')
    
    with open(f_map_path, 'r', encoding='utf-8-sig') as f:
        fran_map = json.load(f)
    with open(c_map_path, 'r', encoding='utf-8-sig') as f:
        corp_map = json.load(f)
        
    return fran_map, corp_map

def carregar_dados_diarios():
    daily_data = {}
    dias_carregados = 0
    
    for dia in ALL_DAYS:
        sum_file = os.path.join(DADOS_DIR, f'Keys Summary - All Stores (Stores) ({dia}).xlsx')
        exc_file = os.path.join(DADOS_DIR, f'KEYS Service Exceptions - All Stores (Stores) ({dia}).xlsx')
        
        if not os.path.exists(sum_file) or not os.path.exists(exc_file):
            continue
            
        dias_carregados += 1
        df_sum = pd.read_excel(sum_file)
        df_exc = pd.read_excel(exc_file)
        
        df_sum['sid'] = df_sum['Store'].astype(str).str.strip().str.zfill(5)
        df_exc['sid'] = df_exc['Store'].astype(str).str.strip().str.zfill(5)
        
        def to_num(v):
            try:
                return float(v) if pd.notnull(v) else 0.0
            except:
                return 0.0
                
        df_sum['order_count'] = df_sum['Order Count'].apply(to_num)
        df_sum['adt_val'] = df_sum['eADT'].apply(to_num)
        df_sum['ext_pct'] = df_sum['% of Est Extreme Deliveries'].apply(to_num)
        
        df_exc['tot_orders'] = df_exc['Total Order Count'].apply(to_num)
        df_exc['delv_orders'] = df_exc['Delv Order Count'].apply(to_num)
        df_exc['exc_count'] = df_exc['Service Exceptions Count'].apply(to_num)
        
        sum_dict = df_sum.set_index('sid')[['order_count', 'adt_val', 'ext_pct']].to_dict('index')
        exc_dict = df_exc.set_index('sid')[['tot_orders', 'delv_orders', 'exc_count']].to_dict('index')
        
        all_sids = set(sum_dict.keys()) | set(exc_dict.keys())
        daily_data[dia] = {}
        
        for sid in all_sids:
            s = sum_dict.get(sid, {})
            e = exc_dict.get(sid, {})
            tot = int(e.get('tot_orders') or s.get('order_count', 0))
            delv = int(e.get('delv_orders', 0))
            
            daily_data[dia][sid] = {
                'orders': tot,
                'delv_orders': delv,
                'adt': s.get('adt_val', 0.0),
                'extreme': s.get('ext_pct', 0.0),
                'exceptions_count': int(e.get('exc_count', 0))
            }
            
    return daily_data, dias_carregados

def calcular_backfill(daily_data, mapping, is_corp=False):
    target_ids = set(mapping.keys())
    missing_list = []
    
    for sid in sorted(target_ids):
        info = mapping[sid]
        missing_days = []
        for dia in ALL_DAYS:
            day_orders = 0
            if dia in daily_data and sid in daily_data[dia]:
                day_orders = daily_data[dia][sid]['orders']
            if day_orders == 0:
                missing_days.append(dia)
                
        if 0 < len(missing_days) < len(ALL_DAYS):
            formatted_days = [d[8:10] + '/' + d[5:7] for d in missing_days]
            missing_list.append({
                'storeId': sid,
                'name': info.get('name', f'Loja {sid}'),
                'consultant': info.get('consultant', 'N/D'),
                'franchisee': info.get('franchisee', 'N/D'),
                'type': 'C' if is_corp else 'F',
                'missingCount': len(missing_days),
                'missingDays': missing_days,
                'formattedDays': formatted_days
            })
            
    missing_list.sort(key=lambda x: x['missingCount'], reverse=True)
    return missing_list

def gerar_painel(mapping, daily_data, backfill_list, is_corp=False):
    target_ids = set(mapping.keys())
    weeks_list = WEEKS_LIST
    
    adt_weeks = {w: [] for w in weeks_list}
    adt_acum = []
    exc_weeks = {w: [] for w in weeks_list}
    exc_acum = []
    
    for p_name, p_days in PERIODS.items():
        for sid in target_ids:
            tot_total_orders = 0
            tot_delv_orders = 0
            sum_adt_weight = 0.0
            sum_ext_weight = 0.0
            tot_exc_count = 0
            
            has_data = False
            for d in p_days:
                if d in daily_data and sid in daily_data[d]:
                    row = daily_data[d][sid]
                    tot_ord = row['orders']
                    delv_ord = row['delv_orders']
                    
                    if tot_ord > 0 or delv_ord > 0:
                        has_data = True
                        
                    tot_total_orders += tot_ord
                    tot_delv_orders += delv_ord
                    sum_adt_weight += row['adt'] * delv_ord
                    sum_ext_weight += row['extreme'] * delv_ord
                    tot_exc_count += row['exceptions_count']
                    
            if not has_data:
                continue
                
            adt_avg = (sum_adt_weight / tot_delv_orders) if tot_delv_orders > 0 else 0.0
            ext_avg = (sum_ext_weight / tot_delv_orders) if tot_delv_orders > 0 else 0.0
            exc_pct = (tot_exc_count / tot_delv_orders) if tot_delv_orders > 0 else 0.0
            
            adt_entry = {
                'storeId': sid,
                'adt': round(adt_avg, 2),
                'extreme': round(ext_avg, 4),
                'orders': tot_total_orders
            }
            exc_entry = {
                'storeId': sid,
                'exceptions': round(exc_pct, 4),
                'exceptionsCount': tot_exc_count,
                'delvOrders': tot_delv_orders,
                'totalOrders': tot_total_orders
            }
            
            if p_name == 'acumulado':
                adt_acum.append(adt_entry)
                exc_acum.append(exc_entry)
            else:
                adt_weeks[p_name].append(adt_entry)
                exc_weeks[p_name].append(exc_entry)
                
    # Carregar historico mensal existente (jan a ago) e atualizar com o acumulado de setembro
    p_dir = CORP_DIR if is_corp else FRAN_DIR
    hist_file = os.path.join(p_dir, 'monthly_history.json')
    monthly_data = {}
    if os.path.exists(hist_file):
        with open(hist_file, 'r', encoding='utf-8') as f:
            monthly_data = json.load(f)
            
    if not monthly_data or 'months' not in monthly_data:
        monthly_data = {
            'months': ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set'],
            'adt': {},
            'exceptions': {}
        }
        
    if 'adt' not in monthly_data: monthly_data['adt'] = {}
    if 'exceptions' not in monthly_data: monthly_data['exceptions'] = {}
    monthly_data['adt']['set'] = adt_acum
    monthly_data['exceptions']['set'] = exc_acum
    if 'set' not in monthly_data.get('months', []):
        monthly_data['months'].append('set')
    
    payload = {
        'stores': mapping,
        'weeks': weeks_list,
        'adt': {
            'acumulado': adt_acum,
            'weeks': adt_weeks
        },
        'exceptions': {
            'acumulado': exc_acum,
            'weeks': exc_weeks
        },
        'monthly': monthly_data,
        'updatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'backfill': backfill_list
    }
    return payload

def main():
    print('===========================================================')
    print('       ATUALIZACAO DE PAINEIS PWR - DOMINOS PIZZA')
    print('===========================================================')
    
    print('1. Carregando mapeamentos de lojas...')
    fran_map, corp_map = carregar_mapeamentos()
    print('   -> Franquias: %d lojas | Lojas Proprias: %d lojas' % (len(fran_map), len(corp_map)))
    
    print('2. Lendo planilhas de relatorios diarios em dados_all_stores/...')
    daily_data, dias_cnt = carregar_dados_diarios()
    print('   -> Carregados %d dias com sucesso.' % dias_cnt)
    
    print('3. Auditando lojas com dias faltantes (Backfill)...')
    bf_fran = calcular_backfill(daily_data, fran_map, is_corp=False)
    bf_corp = calcular_backfill(daily_data, corp_map, is_corp=True)
    print('   -> Pendencias: %d Franquias | %d Lojas Proprias' % (len(bf_fran), len(bf_corp)))
    
    print('4. Consolidando metricas e gerando data.json / data.js...')
    payload_fran = gerar_painel(fran_map, daily_data, bf_fran, is_corp=False)
    payload_corp = gerar_painel(corp_map, daily_data, bf_corp, is_corp=True)
    
    # Salvar Franquias
    with open(os.path.join(FRAN_DIR, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(payload_fran, f, ensure_ascii=False, indent=2)
    with open(os.path.join(FRAN_DIR, 'data.js'), 'w', encoding='utf-8') as f:
        f.write('window.PWR_DATA = ' + json.dumps(payload_fran, ensure_ascii=False) + ';')
        
    # Salvar Lojas Proprias
    with open(os.path.join(CORP_DIR, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(payload_corp, f, ensure_ascii=False, indent=2)
    with open(os.path.join(CORP_DIR, 'data.js'), 'w', encoding='utf-8') as f:
        f.write('window.PWR_DATA = ' + json.dumps(payload_corp, ensure_ascii=False) + ';')
        
    print('')
    print('===========================================================')
    print('  [SUCESSO] PAINEIS ATUALIZADOS COM SUCESSO!')
    print('  - Franquias:      franquias/index.html')
    print('  - Lojas Proprias: lojas-proprias/index.html')
    print('  - Portal Geral:   index.html')
    print('===========================================================')

if __name__ == '__main__':
    main()
