import pandas as pd
import os

folder_all = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr\novo projeto\dados_all_stores'
f_cons = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr\franquias\pwr_reports\Keys Summary - Franquias (Stores)(2026-08-31 - 2026-09-06).xlsx'

df_cons = pd.read_excel(f_cons)
df_cons = df_cons[df_cons['Store'].astype(str).str.isnumeric()].copy()
df_cons['Store'] = df_cons['Store'].astype(int)

week_dates = ['2026-08-31', '2026-09-01', '2026-09-02', '2026-09-03', '2026-09-04', '2026-09-05', '2026-09-06']

daily_sum_list = []
daily_exc_list = []

for d in week_dates:
    fs = os.path.join(folder_all, f'Keys Summary - All Stores (Stores) ({d}).xlsx')
    fe = os.path.join(folder_all, f'KEYS Service Exceptions - All Stores (Stores) ({d}).xlsx')
    
    ds = pd.read_excel(fs)
    de = pd.read_excel(fe)
    
    ds = ds[ds['Store'].astype(str).str.isnumeric()].copy()
    de = de[de['Store'].astype(str).str.isnumeric()].copy()
    ds['Store'] = ds['Store'].astype(int)
    de['Store'] = de['Store'].astype(int)
    
    ds['Date'] = d
    de['Date'] = d
    
    daily_sum_list.append(ds)
    daily_exc_list.append(de)

df_all_sum = pd.concat(daily_sum_list, ignore_index=True)
df_all_exc = pd.concat(daily_exc_list, ignore_index=True)

# Merge summary and exceptions day by day to get Delv Order Count and eADT
merged_daily = pd.merge(
    df_all_sum[['Store', 'Date', 'eADT', '% of Est Extreme Deliveries', 'Order Count']],
    df_all_exc[['Store', 'Date', 'Delv Order Count', 'Total Order Count', 'Service Exceptions Count']],
    on=['Store', 'Date']
)

consolidated_calc = []
for s, grp in merged_daily.groupby('Store'):
    tot_delv = grp['Delv Order Count'].sum()
    tot_orders = grp['Order Count'].sum()
    tot_exc_cnt = grp['Service Exceptions Count'].sum()
    
    if tot_delv > 0:
        eadt_calc = (grp['eADT'] * grp['Delv Order Count']).sum() / tot_delv
        extreme_calc = (grp['% of Est Extreme Deliveries'] * grp['Delv Order Count']).sum() / tot_delv
    else:
        eadt_calc = grp['eADT'].mean()
        extreme_calc = grp['% of Est Extreme Deliveries'].mean()
        
    consolidated_calc.append({
        'Store': s,
        'eADT_calc': eadt_calc,
        'Extreme_calc': extreme_calc,
        'Orders_calc': tot_orders,
        'Delv_calc': tot_delv,
        'Exc_Count_calc': tot_exc_cnt
    })

df_calc = pd.DataFrame(consolidated_calc)
comp = pd.merge(df_cons[['Store', 'City', 'eADT', '% of Est Extreme Deliveries', 'Order Count']], df_calc, on='Store')

comp['diff_eADT_seconds'] = (comp['eADT'] - comp['eADT_calc']) * 60
comp['diff_Extreme_pct'] = (comp['% of Est Extreme Deliveries'] - comp['Extreme_calc']) * 100

print("="*65)
print("=== RESULTADO DA PROVA DE FOGO: OFICIAL PWR vs CÁLCULO DIÁRIO ===")
print("="*65)
print(f"Total de lojas comparadas: {len(comp)}")

print("\n--- DIFERENÇA NO eADT (em SEGUNDOS) ---")
print(f"Média de diferença: {comp['diff_eADT_seconds'].mean():.2f} segundos")
print(f"Mediana: {comp['diff_eADT_seconds'].median():.2f} segundos")
print(f"Desvio Padrão: {comp['diff_eADT_seconds'].std():.2f} segundos")

print("\n--- DIFERENÇA EM % DE EXTREMOS (pontos percentuais) ---")
print(f"Média de diferença: {comp['diff_Extreme_pct'].mean():.4f}%")
print(f"Mediana: {comp['diff_Extreme_pct'].median():.4f}%")

print("\n--- AMOSTRA REAL DE 10 LOJAS ---")
for idx, r in comp.head(10).iterrows():
    s_id = int(r['Store'])
    city = r['City']
    eadt_pwr = r['eADT']
    eadt_c = r['eADT_calc']
    diff_sec = r['diff_eADT_seconds']
    ext_pwr = r['% of Est Extreme Deliveries'] * 100
    ext_c = r['Extreme_calc'] * 100
    print(f"Loja {s_id:5d} ({city[:12]:12}): eADT PWR={eadt_pwr:5.2f}m | Calc={eadt_c:5.2f}m (diff: {diff_sec:+4.1f}s) | Extremos PWR={ext_pwr:4.1f}% | Calc={ext_c:4.1f}%")
