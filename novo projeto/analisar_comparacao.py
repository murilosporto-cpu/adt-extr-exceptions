import pandas as pd
import os
import glob
import numpy as np

folder = os.path.dirname(os.path.abspath(__file__))
daily_files = sorted([
    os.path.join(folder, f) for f in os.listdir(folder)
    if f.startswith('Keys Summary - Franquias (Stores) (2026-')
])
consolidated_file = os.path.join(folder, 'Keys Summary - Franquias (Stores)(2026-08-31 - 2026-09-06).xlsx')

df_cons = pd.read_excel(consolidated_file, sheet_name='KEYS Keys Summary')
dfs_daily = []
for f in daily_files:
    d = pd.read_excel(f, sheet_name='KEYS Keys Summary')
    d['__file_date'] = os.path.basename(f)
    dfs_daily.append(d)

df_daily = pd.concat(dfs_daily, ignore_index=True)

print(f"Consolidated records: {len(df_cons)}")
print(f"Total daily records: {len(df_daily)}")

stores_cons = set(df_cons['Store'])
stores_daily = set(df_daily['Store'])

print(f"Distinct stores in consolidated: {len(stores_cons)}")
print(f"Distinct stores in daily: {len(stores_daily)}")

diff_daily_only = stores_daily - stores_cons
diff_cons_only = stores_cons - stores_daily

print("\n--- DIFERENÇA DE LOJAS ---")
print("Lojas que aparecem nos diários mas NÃO estão no consolidado:", diff_daily_only)
print("Lojas que estão no consolidado mas NÃO estão nos diários:", diff_cons_only)

for s in diff_daily_only:
    sub = df_daily[df_daily['Store'] == s]
    print(f"\nDetalhe Loja {s}:")
    print(sub[['Store', 'City', '__file_date', 'Royalty Sales (Tot)', 'Order Count']])

# Let's check additive columns for common stores
common_stores = sorted(list(stores_cons.intersection(stores_daily)))
print(f"\nLojas em comum analisadas: {len(common_stores)}")

# Compare Sales and Order Count
daily_agg = df_daily.groupby('Store').agg({
    'Royalty Sales (Tot)': 'sum',
    'Order Count': 'sum',
    'Cash Over / Short': 'sum'
}).reset_index()

merged = pd.merge(df_cons, daily_agg, on='Store', suffixes=('_cons', '_daily_sum'))

merged['sales_diff'] = merged['Royalty Sales (Tot)_cons'] - merged['Royalty Sales (Tot)_daily_sum']
merged['orders_diff'] = merged['Order Count_cons'] - merged['Order Count_daily_sum']
merged['cash_diff'] = merged['Cash Over / Short_cons'] - merged['Cash Over / Short_daily_sum']

print("\n--- COMPARAÇÃO DE VENDAS TOTAIS (Royalty Sales (Tot)) ---")
sales_mismatch = merged[merged['sales_diff'].abs() > 0.05]
print(f"Lojas com diferença em Vendas: {len(sales_mismatch)} de {len(merged)}")
if len(sales_mismatch) > 0:
    print(sales_mismatch[['Store', 'Royalty Sales (Tot)_cons', 'Royalty Sales (Tot)_daily_sum', 'sales_diff']].head(10))
else:
    print("-> Vendas batem perfeitamente (100% iguais) para todas as lojas em comum!")

print("\n--- COMPARAÇÃO DE QUANTIDADE DE PEDIDOS (Order Count) ---")
orders_mismatch = merged[merged['orders_diff'].abs() > 0.001]
print(f"Lojas com diferença em Pedidos: {len(orders_mismatch)} de {len(merged)}")
if len(orders_mismatch) > 0:
    print(orders_mismatch[['Store', 'Order Count_cons', 'Order Count_daily_sum', 'orders_diff']].head(10))
else:
    print("-> Quantidade de pedidos bate perfeitamente (100% igual) para todas as lojas em comum!")

print("\n--- COMPARAÇÃO DE QUEBRA DE CAIXA (Cash Over / Short) ---")
cash_mismatch = merged[merged['cash_diff'].abs() > 0.05]
print(f"Lojas com diferença em Cash Over/Short: {len(cash_mismatch)} de {len(merged)}")
if len(cash_mismatch) > 0:
    print(cash_mismatch[['Store', 'Cash Over / Short_cons', 'Cash Over / Short_daily_sum', 'cash_diff']].head(10))
else:
    print("-> Quebra de caixa bate perfeitamente para todas as lojas em comum!")

print("\n" + "="*50)
print("INVESTIGAÇÃO PROFUNDA DE VENDAS E DIAS")
print("="*50)

# Check Store 19506 day by day
c_19506 = df_cons[df_cons['Store'] == 19506].iloc[0]
print(f"Consolidado Loja 19506: Vendas = {c_19506['Royalty Sales (Tot)']} | Pedidos = {c_19506['Order Count']}")

daily_19506 = []
for f in daily_files:
    d = pd.read_excel(f, sheet_name='KEYS Keys Summary')
    r = d[d['Store'] == 19506]
    dt = os.path.basename(f).split('(')[-1].replace(').xlsx', '').strip()
    if len(r) > 0:
        s = r.iloc[0]['Royalty Sales (Tot)']
        o = r.iloc[0]['Order Count']
        daily_19506.append({'date': dt, 'sales': s, 'orders': o})
        print(f"  Dia {dt}: Vendas = {s:.2f}, Pedidos = {o}")

df_19506 = pd.DataFrame(daily_19506)
print(f"Soma dos 7 dias Vendas: {df_19506['sales'].sum():.2f}")
print(f"Soma dos 7 dias Pedidos: {df_19506['orders'].sum():.2f}")
print(f"Diferença Vendas: {df_19506['sales'].sum() - c_19506['Royalty Sales (Tot)']:.2f}")

# Check if one of the days has sales equal to the difference
diff = df_19506['sales'].sum() - c_19506['Royalty Sales (Tot)']
print(f"\nValor da diferença: {diff:.2f}")
for idx, row in df_19506.iterrows():
    print(f"  Vendas no dia {row['date']}: {row['sales']:.2f} (diferença vs dia: {diff - row['sales']:.2f})")

# Filter out zero sales and calculate ratio
merged_clean = merged[merged['Store'].apply(lambda x: str(x).isdigit())].copy()
merged_clean['Store'] = merged_clean['Store'].astype(int)

# Filter non-zero
active = merged_clean[merged_clean['Royalty Sales (Tot)_daily_sum'] > 0].copy()
active['ratio_sales'] = active['Royalty Sales (Tot)_cons'] / active['Royalty Sales (Tot)_daily_sum']
active['pct_diff'] = ((active['Royalty Sales (Tot)_cons'] - active['Royalty Sales (Tot)_daily_sum']) / active['Royalty Sales (Tot)_daily_sum']) * 100

print("\nEstatísticas da Razão Consolidado / Soma Diária de Vendas (Lojas com venda > 0):")
print(active['pct_diff'].describe())

print("\nExemplos de diferenças percentuais:")
print(active[['Store', 'Royalty Sales (Tot)_cons', 'Royalty Sales (Tot)_daily_sum', 'pct_diff']].head(15))

# Check stores where daily sum is 0
zero_stores = merged_clean[merged_clean['Royalty Sales (Tot)_daily_sum'] == 0]
if len(zero_stores) > 0:
    print("\nLojas com venda diária zerada:")
    print(zero_stores[['Store', 'Royalty Sales (Tot)_cons', 'Royalty Sales (Tot)_daily_sum']])

# Check the 3 stores with order count mismatch
print("\nINVESTIGANDO AS 3 LOJAS COM PEDIDOS DIFERENTES:")
for s in [19536, 19618, 19863]:
    cons_r = df_cons[df_cons['Store'] == s].iloc[0]
    print(f"\nLoja {s} no Consolidado: Pedidos = {cons_r['Order Count']}, Vendas = {cons_r['Royalty Sales (Tot)']}")
    for f in daily_files:
        dt = os.path.basename(f).split('(')[-1].replace(').xlsx', '').strip()
        d = pd.read_excel(f, sheet_name='KEYS Keys Summary')
        r = d[d['Store'] == s]
        if len(r) > 0:
            print(f"  Dia {dt}: Pedidos = {r.iloc[0]['Order Count']}, Vendas = {r.iloc[0]['Royalty Sales (Tot)']}")
        else:
            print(f"  Dia {dt}: NÃO CONSTA NO ARQUIVO")


