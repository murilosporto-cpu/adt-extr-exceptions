import os
import glob
import json
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(BASE_DIR, 'dados_all_stores')
ROOT_DIR = os.path.dirname(BASE_DIR)

# Mapeamento oficial das 4 semanas e acumulado
WEEKS = {
    '17 a 23': pd.date_range('2026-08-17', '2026-08-23').strftime('%Y-%m-%d').tolist(),
    '24 a 30': pd.date_range('2026-08-24', '2026-08-30').strftime('%Y-%m-%d').tolist(),
    '31 a 06': pd.date_range('2026-08-31', '2026-09-06').strftime('%Y-%m-%d').tolist(),
    '07 a 13': pd.date_range('2026-09-07', '2026-09-13').strftime('%Y-%m-%d').tolist(),
}
ACUMULADO_DATES = pd.date_range('2026-09-01', '2026-09-13').strftime('%Y-%m-%d').tolist()

def load_stores_mapping():
    stores_info = {}
    
    # 1. Carrega mapping de franquias (195 lojas)
    f_path = os.path.join(ROOT_DIR, 'franquias', 'stores_mapping.json')
    if os.path.exists(f_path):
        with open(f_path, 'r', encoding='utf-8-sig') as f:
            for k, v in json.load(f).items():
                stores_info[str(k)] = {
                    'id': str(k),
                    'name': v.get('name', f'Loja {k}'),
                    'consultant': v.get('consultant', 'N/D'),
                    'franchisee': v.get('franchisee', 'N/D'),
                    'status': v.get('status', 'ATIVA'),
                    'type': 'F'
                }
                
    # 2. Carrega mapping de lojas próprias (22 lojas corporativas)
    p_path = os.path.join(ROOT_DIR, 'lojas-proprias', 'stores_mapping.json')
    if os.path.exists(p_path):
        with open(p_path, 'r', encoding='utf-8-sig') as f:
            for k, v in json.load(f).items():
                stores_info[str(k)] = {
                    'id': str(k),
                    'name': v.get('name', f'Loja {k}'),
                    'consultant': v.get('consultant', 'CORPORATIVO'),
                    'franchisee': v.get('franchisee', 'DOMINOS BRASIL'),
                    'status': v.get('status', 'ATIVA'),
                    'type': 'C'
                }
    return stores_info

def build_data():
    print("Iniciando processamento dos dados diários para o painel...")
    summary_files = sorted(glob.glob(os.path.join(DADOS_DIR, 'Keys Summary*.xlsx')))
    exc_files = sorted(glob.glob(os.path.join(DADOS_DIR, 'KEYS Service Exceptions*.xlsx')))

    if not summary_files or not exc_files:
        raise FileNotFoundError("Arquivos diários não encontrados em dados_all_stores.")

    print(f"Lendo {len(summary_files)} arquivos de Summary e {len(exc_files)} de Exceptions...")
    
    dfs_sum = []
    for f in summary_files:
        d_str = f.split('(')[-1].split(')')[0]
        df = pd.read_excel(f)
        df['Date'] = d_str
        dfs_sum.append(df)
    df_sum = pd.concat(dfs_sum, ignore_index=True)

    dfs_exc = []
    for f in exc_files:
        d_str = f.split('(')[-1].split(')')[0]
        df = pd.read_excel(f)
        df['Date'] = d_str
        dfs_exc.append(df)
    df_exc = pd.concat(dfs_exc, ignore_index=True)

    df_sum['Store'] = df_sum['Store'].astype(str)
    df_exc['Store'] = df_exc['Store'].astype(str)

    df_sum['Order Count'] = pd.to_numeric(df_sum['Order Count'], errors='coerce').fillna(0)
    df_sum['eADT'] = pd.to_numeric(df_sum['eADT'], errors='coerce').fillna(0)
    df_sum['% of Est Extreme Deliveries'] = pd.to_numeric(df_sum['% of Est Extreme Deliveries'], errors='coerce').fillna(0)
    df_sum['Royalty Sales (Tot)'] = pd.to_numeric(df_sum['Royalty Sales (Tot)'], errors='coerce').fillna(0)

    df_exc['Total Order Count'] = pd.to_numeric(df_exc['Total Order Count'], errors='coerce').fillna(0)
    df_exc['Delv Order Count'] = pd.to_numeric(df_exc['Delv Order Count'], errors='coerce').fillna(0)
    df_exc['Orders with 1+ Service Exceptions'] = pd.to_numeric(df_exc['Orders with 1+ Service Exceptions'], errors='coerce').fillna(0)

    merged = pd.merge(
        df_sum[['Store', 'Date', 'Corp/Fran Type', 'City', 'State', 'DCO / Fran', 'Order Count', 'eADT', '% of Est Extreme Deliveries', 'Royalty Sales (Tot)']],
        df_exc[['Store', 'Date', 'Total Order Count', 'Delv Order Count', 'Orders with 1+ Service Exceptions']],
        on=['Store', 'Date'],
        how='left'
    )
    merged['Delv Order Count'] = merged['Delv Order Count'].fillna(0)
    merged['Orders with 1+ Service Exceptions'] = merged['Orders with 1+ Service Exceptions'].fillna(0)

    merged['Extreme_Delv_Count'] = (merged['% of Est Extreme Deliveries'] / 100.0) * merged['Delv Order Count']
    merged['eADT_x_Delv'] = merged['eADT'] * merged['Delv Order Count']

    stores_mapping = load_stores_mapping()

    # Preenche novas lojas encontradas
    for _, row in merged.drop_duplicates(subset=['Store']).iterrows():
        sid = str(row['Store'])
        dco = str(row['DCO / Fran']).strip() if pd.notna(row['DCO / Fran']) else 'N/D'
        city = str(row['City']).strip() if pd.notna(row['City']) else ''
        
        if sid not in stores_mapping:
            stores_mapping[sid] = {
                'id': sid,
                'name': f"DOMINOS {city} ({sid})" if city else f"LOJA {sid}",
                'consultant': dco if dco != 'N/D' else 'CONSULTOR',
                'franchisee': dco,
                'status': 'ATIVA',
                'type': 'F' # Por padrão franquia, a menos que esteja no mapping de próprias
            }

    # Estruturas finais do data.json
    output_data = {
        'weeks': list(WEEKS.keys()),
        'acumuladoTitle': '01 a 13 (Set)',
        'stores': stores_mapping,
        'adt': {
            'weeks': {},
            'acumulado': []
        },
        'exceptions': {
            'weeks': {},
            'acumulado': []
        },
        'updatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # 1. Processar cada semana
    for w_name, dates in WEEKS.items():
        w_df = merged[merged['Date'].isin(dates)]
        w_agg = w_df.groupby('Store').agg({
            'Order Count': 'sum',
            'Delv Order Count': 'sum',
            'Extreme_Delv_Count': 'sum',
            'Orders with 1+ Service Exceptions': 'sum',
            'eADT_x_Delv': 'sum'
        }).reset_index()

        adt_week_list = []
        exc_week_list = []

        for _, r in w_agg.iterrows():
            sid = str(r['Store'])
            tot_orders = int(r['Order Count'])
            delv_orders = int(r['Delv Order Count'])
            ext_count = float(r['Extreme_Delv_Count'])
            exc_count = int(r['Orders with 1+ Service Exceptions'])
            eadt_prod = float(r['eADT_x_Delv'])

            adt_val = (eadt_prod / delv_orders) if delv_orders > 0 else 0.0
            ext_pct = (ext_count / delv_orders) if delv_orders > 0 else 0.0
            exc_pct = (exc_count / delv_orders) if delv_orders > 0 else 0.0

            if tot_orders > 0 or delv_orders > 0:
                adt_week_list.append({
                    'storeId': sid,
                    'orders': tot_orders,
                    'delvOrders': delv_orders,
                    'adt': round(adt_val, 2),
                    'extreme': round(ext_pct, 4)
                })

                exc_week_list.append({
                    'storeId': sid,
                    'totalOrders': tot_orders,
                    'delvOrders': delv_orders,
                    'exceptionsCount': exc_count,
                    'exceptions': round(exc_pct, 4)
                })

        output_data['adt']['weeks'][w_name] = adt_week_list
        output_data['exceptions']['weeks'][w_name] = exc_week_list

    # 2. Processar Acumulado de Setembro (01 a 13)
    ac_df = merged[merged['Date'].isin(ACUMULADO_DATES)]
    ac_agg = ac_df.groupby('Store').agg({
        'Order Count': 'sum',
        'Delv Order Count': 'sum',
        'Extreme_Delv_Count': 'sum',
        'Orders with 1+ Service Exceptions': 'sum',
        'eADT_x_Delv': 'sum'
    }).reset_index()

    adt_ac_list = []
    exc_ac_list = []

    for _, r in ac_agg.iterrows():
        sid = str(r['Store'])
        tot_orders = int(r['Order Count'])
        delv_orders = int(r['Delv Order Count'])
        ext_count = float(r['Extreme_Delv_Count'])
        exc_count = int(r['Orders with 1+ Service Exceptions'])
        eadt_prod = float(r['eADT_x_Delv'])

        adt_val = (eadt_prod / delv_orders) if delv_orders > 0 else 0.0
        ext_pct = (ext_count / delv_orders) if delv_orders > 0 else 0.0
        exc_pct = (exc_count / delv_orders) if delv_orders > 0 else 0.0

        if tot_orders > 0 or delv_orders > 0:
            adt_ac_list.append({
                'storeId': sid,
                'orders': tot_orders,
                'delvOrders': delv_orders,
                'adt': round(adt_val, 2),
                'extreme': round(ext_pct, 4)
            })

            exc_ac_list.append({
                'storeId': sid,
                'totalOrders': tot_orders,
                'delvOrders': delv_orders,
                'exceptionsCount': exc_count,
                'exceptions': round(exc_pct, 4)
            })

    output_data['adt']['acumulado'] = adt_ac_list
    output_data['exceptions']['acumulado'] = exc_ac_list

    out_json_path = os.path.join(BASE_DIR, 'data.json')
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"Salvo: {out_json_path} ({os.path.getsize(out_json_path):,} bytes)")

    out_js_path = os.path.join(BASE_DIR, 'data.js')
    with open(out_js_path, 'w', encoding='utf-8') as f:
        f.write("window.PWR_DATA = " + json.dumps(output_data, ensure_ascii=False) + ";\n")
    print(f"Salvo: {out_js_path} ({os.path.getsize(out_js_path):,} bytes)")

    # Resumo
    corp_count = sum(1 for s in stores_mapping.values() if s.get('type') == 'C')
    fran_count = sum(1 for s in stores_mapping.values() if s.get('type') == 'F')
    print(f"Total Lojas: {len(stores_mapping)} (Franquias: {fran_count} | Próprias: {corp_count})")

if __name__ == '__main__':
    build_data()
