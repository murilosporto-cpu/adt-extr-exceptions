import os
import glob
import pandas as pd
import json
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
dados_dir = os.path.join(BASE_DIR, 'dados_all_stores')

import re
days = sorted(list(set(re.findall(r'\d{4}-\d{2}-\d{2}', f)[0] for f in glob.glob(os.path.join(dados_dir, 'Keys Summary*.xlsx')) if re.findall(r'\d{4}-\d{2}-\d{2}', f))))
print(f"Total dias analisados: {len(days)} ({days[0]} ate {days[-1]})")

store_days = defaultdict(dict)

for d in days:
    filepath = os.path.join(dados_dir, f"Keys Summary - All Stores (Stores) ({d}).xlsx")
    df = pd.read_excel(filepath)
    df['Store'] = df['Store'].astype(str).str.strip().str.zfill(5)
    for _, r in df.iterrows():
        sid = r['Store']
        orders = r['Order Count'] if pd.notnull(r['Order Count']) else 0
        store_days[sid][d] = int(orders)

with open(os.path.join(ROOT_DIR, 'franquias', 'stores_mapping.json'), 'r', encoding='utf-8-sig') as f:
    fran_map = json.load(f)
with open(os.path.join(ROOT_DIR, 'lojas-proprias', 'stores_mapping.json'), 'r', encoding='utf-8-sig') as f:
    corp_map = json.load(f)

excluded_ids = {'19680', '19707', '19733', '19792', '19964', '19967', '19736'}

def get_missing_for_panel(mapping, is_corp=False):
    report = []
    for sid, st in mapping.items():
        if sid in excluded_ids:
            continue
        day_dict = store_days.get(sid, {})
        tot_orders = sum(day_dict.values())
        if tot_orders == 0:
            continue  # Loja inativa no período
        missing_days = [d for d in days if day_dict.get(d, 0) == 0]
        if missing_days:
            clean_name = st.get('name', f"Loja {sid}").replace("DOMINOS ", "").replace("DOMINO'S ", "").strip()
            formatted = [f"{d.split('-')[2]}/{d.split('-')[1]}" for d in missing_days]
            report.append({
                'storeId': sid,
                'name': clean_name,
                'consultant': st.get('consultant', 'N/D'),
                'franchisee': st.get('franchisee', 'N/D'),
                'type': 'C' if is_corp else 'F',
                'missingCount': len(missing_days),
                'missingDays': missing_days,
                'formattedDays': formatted
            })
    report.sort(key=lambda x: x['missingCount'], reverse=True)
    return report

fran_report = get_missing_for_panel(fran_map, is_corp=False)
corp_report = get_missing_for_panel(corp_map, is_corp=True)

print(f"\n--- FRANQUIAS COM DIAS FALTANTES ({len(fran_report)} lojas) ---")
for item in fran_report:
    print(f"{item['storeId']} - {item['name']} | Consultor: {item['consultant']} | {item['missingCount']} dias: {', '.join(item['formattedDays'])}")

print(f"\n--- LOJAS PRÓPRIAS COM DIAS FALTANTES ({len(corp_report)} lojas) ---")
for item in corp_report:
    print(f"{item['storeId']} - {item['name']} | Coordenador: {item['consultant']} | {item['missingCount']} dias: {', '.join(item['formattedDays'])}")
