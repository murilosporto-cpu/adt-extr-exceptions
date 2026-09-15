import os
import re
import json
import shutil
import pandas as pd
from datetime import datetime

ROOT_DIR = os.path.abspath('.')
NOVO_DIR = os.path.join(ROOT_DIR, 'novo projeto')
DADOS_DIR = os.path.join(NOVO_DIR, 'dados_all_stores')

FRAN_DIR = os.path.join(NOVO_DIR, 'franquias')
CORP_DIR = os.path.join(NOVO_DIR, 'lojas-proprias')

os.makedirs(FRAN_DIR, exist_ok=True)
os.makedirs(CORP_DIR, exist_ok=True)

print('1. Carregando mapeamento de lojas...')
with open(os.path.join(ROOT_DIR, 'franquias', 'stores_mapping.json'), 'r', encoding='utf-8-sig') as f:
    fran_mapping = json.load(f)

with open(os.path.join(ROOT_DIR, 'lojas-proprias', 'stores_mapping.json'), 'r', encoding='utf-8-sig') as f:
    corp_mapping = json.load(f)

corp_ids = set(corp_mapping.keys())
print(f'Total Franquias mapeadas: {len(fran_mapping)}, Lojas Proprias: {len(corp_ids)}')

print('2. Lendo arquivos diarios de 17/08 a 13/09...')
dias_w1 = [f'2026-08-{d:02d}' for d in range(17, 24)]
dias_w2 = [f'2026-08-{d:02d}' for d in range(24, 31)]
dias_w3 = ['2026-08-31'] + [f'2026-09-{d:02d}' for d in range(1, 7)]
dias_w4 = [f'2026-09-{d:02d}' for d in range(7, 14)]
dias_acum = [f'2026-09-{d:02d}' for d in range(1, 14)]

periodos = {
    '17 a 23': dias_w1,
    '24 a 30': dias_w2,
    '31 a 06': dias_w3,
    '07 a 13': dias_w4,
    'acumulado': dias_acum
}

daily_store_data = {}
all_days = sorted(list(set(dias_w1 + dias_w2 + dias_w3 + dias_w4 + dias_acum)))

for dia in all_days:
    sum_file = os.path.join(DADOS_DIR, f'Keys Summary - All Stores (Stores) ({dia}).xlsx')
    exc_file = os.path.join(DADOS_DIR, f'KEYS Service Exceptions - All Stores (Stores) ({dia}).xlsx')
    
    if not os.path.exists(sum_file) or not os.path.exists(exc_file):
        print(f'AVISO: Arquivo faltando para o dia {dia}')
        continue
    
    df_sum = pd.read_excel(sum_file)
    df_exc = pd.read_excel(exc_file)
    
    df_sum['store_id'] = df_sum['Store'].astype(str).str.strip().str.zfill(5)
    df_exc['store_id'] = df_exc['Store'].astype(str).str.strip().str.zfill(5)
    
    def to_float(val):
        try:
            return float(val) if pd.notnull(val) else 0.0
        except:
            return 0.0
            
    df_sum['delv_orders'] = df_sum['Order Count'].apply(to_float)
    df_sum['adt_val'] = df_sum['eADT'].apply(to_float)
    df_sum['ext_pct'] = df_sum['% of Est Extreme Deliveries'].apply(to_float)
    
    df_exc['tot_orders'] = df_exc['Total Order Count'].apply(to_float)
    df_exc['delv_orders_exc'] = df_exc['Delv Order Count'].apply(to_float)
    df_exc['exc_count'] = df_exc['Service Exceptions Count'].apply(to_float)
    
    sum_dict = df_sum.set_index('store_id')[['delv_orders', 'adt_val', 'ext_pct']].to_dict(orient='index')
    exc_dict = df_exc.set_index('store_id')[['tot_orders', 'delv_orders_exc', 'exc_count']].to_dict(orient='index')
    
    all_sids = set(sum_dict.keys()) | set(exc_dict.keys())
    daily_store_data[dia] = {}
    
    for sid in all_sids:
        s = sum_dict.get(sid, {})
        e = exc_dict.get(sid, {})
        delv = s.get('delv_orders', 0.0)
        daily_store_data[dia][sid] = {
            'orders': int(delv),
            'adt': s.get('adt_val', 0.0),
            'extreme': s.get('ext_pct', 0.0),
            'total_orders': int(e.get('tot_orders', 0.0)),
            'delv_orders': int(e.get('delv_orders_exc', delv)),
            'exceptions_count': int(e.get('exc_count', 0.0))
        }

print(f'Carregados {len(daily_store_data)} dias de dados com sucesso.')

def build_panel_data(target_corp=False):
    if target_corp:
        mapping = corp_mapping
        target_ids = corp_ids
        source_data_json = os.path.join(ROOT_DIR, 'lojas-proprias', 'data.json')
    else:
        mapping = fran_mapping
        target_ids = set(fran_mapping.keys())
        source_data_json = os.path.join(ROOT_DIR, 'franquias', 'data.json')
        
    with open(source_data_json, 'r', encoding='utf-8-sig') as f:
        orig_json = json.load(f)
        
    weeks_list = ['17 a 23', '24 a 30', '31 a 06', '07 a 13']
    
    adt_weeks = {w: [] for w in weeks_list}
    adt_acum = []
    
    exc_weeks = {w: [] for w in weeks_list}
    exc_acum = []
    
    for p_name, p_days in periodos.items():
        for sid in target_ids:
            tot_delv = 0
            sum_adt_weight = 0.0
            sum_ext_weight = 0.0
            tot_exc_count = 0
            tot_all_orders = 0
            tot_delv_exc = 0
            
            has_data = False
            for d in p_days:
                if d in daily_store_data and sid in daily_store_data[d]:
                    row = daily_store_data[d][sid]
                    o = row['orders']
                    if o > 0 or row['total_orders'] > 0:
                        has_data = True
                    tot_delv += o
                    sum_adt_weight += row['adt'] * o
                    sum_ext_weight += row['extreme'] * o
                    tot_exc_count += row['exceptions_count']
                    tot_all_orders += row['total_orders']
                    tot_delv_exc += row['delv_orders']
                    
            if not has_data:
                continue
                
            adt_avg = (sum_adt_weight / tot_delv) if tot_delv > 0 else 0.0
            ext_avg = (sum_ext_weight / tot_delv) if tot_delv > 0 else 0.0
            
            exc_base = tot_delv_exc if tot_delv_exc > 0 else tot_delv
            exc_pct = (tot_exc_count / exc_base) if exc_base > 0 else 0.0
            
            adt_entry = {
                'storeId': sid,
                'adt': round(adt_avg, 2),
                'extreme': round(ext_avg, 4),
                'orders': tot_delv
            }
            
            exc_entry = {
                'storeId': sid,
                'exceptions': round(exc_pct, 4),
                'exceptionsCount': tot_exc_count,
                'delvOrders': exc_base,
                'totalOrders': tot_all_orders
            }
            
            if p_name == 'acumulado':
                adt_acum.append(adt_entry)
                exc_acum.append(exc_entry)
            else:
                adt_weeks[p_name].append(adt_entry)
                exc_weeks[p_name].append(exc_entry)
                
    monthly_data = orig_json.get('monthly', {})
    if isinstance(monthly_data, dict):
        if 'adt' in monthly_data:
            monthly_data['adt']['set'] = adt_acum
        if 'exceptions' in monthly_data:
            monthly_data['exceptions']['set'] = exc_acum
            
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
        'updatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return payload

print('3. Gerando payloads Franquias e Lojas Proprias...')
payload_fran = build_panel_data(target_corp=False)
payload_corp = build_panel_data(target_corp=True)

for p_dir, p_data in [(FRAN_DIR, payload_fran), (CORP_DIR, payload_corp)]:
    json_path = os.path.join(p_dir, 'data.json')
    js_path = os.path.join(p_dir, 'data.js')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(p_data, f, ensure_ascii=False, indent=2)
        
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write('window.PWR_DATA = ' + json.dumps(p_data, ensure_ascii=False) + ';\n')
        
print('data.json e data.js gerados com sucesso para Franquias e Lojas Proprias!')
