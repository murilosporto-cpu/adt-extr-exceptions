import os
import glob
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DADOS_DIR = os.path.join(BASE_DIR, 'dados_all_stores')
ROOT_DIR = os.path.dirname(BASE_DIR)

WEEKS = {
    'Semana 1 (17/08 a 23/08)': pd.date_range('2026-08-17', '2026-08-23').strftime('%Y-%m-%d').tolist(),
    'Semana 2 (24/08 a 30/08)': pd.date_range('2026-08-24', '2026-08-30').strftime('%Y-%m-%d').tolist(),
    'Semana 3 (31/08 a 06/09)': pd.date_range('2026-08-31', '2026-09-06').strftime('%Y-%m-%d').tolist(),
    'Semana 4 (07/09 a 13/09)': pd.date_range('2026-09-07', '2026-09-13').strftime('%Y-%m-%d').tolist(),
    'Acumulado Setembro (01/09 a 13/09)': pd.date_range('2026-09-01', '2026-09-13').strftime('%Y-%m-%d').tolist(),
}

def main():
    print("=================================================================")
    print("    AUDITORIA E CONSOLIDAÇÃO DOS 28 DIAS (PROVA DE FOGO)")
    print("=================================================================\n")

    summary_files = sorted(glob.glob(os.path.join(DADOS_DIR, 'Keys Summary*.xlsx')))
    exc_files = sorted(glob.glob(os.path.join(DADOS_DIR, 'KEYS Service Exceptions*.xlsx')))

    print(f"[OK] Total de arquivos carregados: {len(summary_files)} Keys Summary | {len(exc_files)} Service Exceptions")
    
    dfs_sum = []
    for f in summary_files:
        dt_str = f.split('(')[-1].split(')')[0]
        df = pd.read_excel(f)
        df['Date'] = dt_str
        dfs_sum.append(df)
    all_sum = pd.concat(dfs_sum, ignore_index=True)

    dfs_exc = []
    for f in exc_files:
        dt_str = f.split('(')[-1].split(')')[0]
        df = pd.read_excel(f)
        df['Date'] = dt_str
        dfs_exc.append(df)
    all_exc = pd.concat(dfs_exc, ignore_index=True)

    num_cols_sum = ['Order Count', 'Royalty Sales (Tot)', 'eADT', '% of Est Extreme Deliveries', '% of Orders in Singles', 'Cash Over / Short']
    for col in num_cols_sum:
        if col in all_sum.columns:
            all_sum[col] = pd.to_numeric(all_sum[col], errors='coerce').fillna(0)

    num_cols_exc = ['Total Order Count', 'Delv Order Count', 'Service Exceptions Count', 'Orders with 1+ Service Exceptions']
    for col in num_cols_exc:
        if col in all_exc.columns:
            all_exc[col] = pd.to_numeric(all_exc[col], errors='coerce').fillna(0)

    merged = pd.merge(
        all_sum, 
        all_exc[['Store', 'Date', 'Delv Order Count', 'Service Exceptions Count', 'Orders with 1+ Service Exceptions']], 
        on=['Store', 'Date'], 
        how='left'
    )
    merged['Delv Order Count'] = merged['Delv Order Count'].fillna(0)
    merged['Service Exceptions Count'] = merged['Service Exceptions Count'].fillna(0)
    merged['Orders with 1+ Service Exceptions'] = merged['Orders with 1+ Service Exceptions'].fillna(0)
    
    merged['Extreme_Delv_Count'] = (merged['% of Est Extreme Deliveries'] / 100.0) * merged['Delv Order Count']
    merged['Singles_Count'] = (merged['% of Orders in Singles'] / 100.0) * merged['Delv Order Count']
    merged['eADT_x_Delv'] = merged['eADT'] * merged['Delv Order Count']

    # 1. RESUMO GERAL DAS 4 SEMANAS E ACUMULADO
    print("\n" + "="*105)
    print(f"{'PERÍODO':<33} | {'DIAS':<4} | {'LOJAS':<5} | {'PEDIDOS':<9} | {'DELIVERY':<9} | {'VENDAS (R$)':<15} | {'eADT':<6} | {'% EXTR':<6} | {'EXCEPT':<7}")
    print("="*105)

    for p_name, dates in WEEKS.items():
        sub = merged[merged['Date'].isin(dates)]
        dias_cnt = sub['Date'].nunique()
        lojas_ativas = sub[sub['Order Count'] > 0]['Store'].nunique()
        total_pedidos = int(sub['Order Count'].sum())
        total_delv = int(sub['Delv Order Count'].sum())
        total_vendas = sub['Royalty Sales (Tot)'].sum()
        total_except = int(sub['Orders with 1+ Service Exceptions'].sum())
        
        eadt_medio = sub['eADT_x_Delv'].sum() / total_delv if total_delv > 0 else 0
        pct_extremos = (sub['Extreme_Delv_Count'].sum() / total_delv * 100) if total_delv > 0 else 0
        
        print(f"{p_name:<33} | {dias_cnt:<4} | {lojas_ativas:<5} | {total_pedidos:>9,d} | {total_delv:>9,d} | R$ {total_vendas:>12,.2f} | {eadt_medio:>6.2f} | {pct_extremos:>5.1f}% | {total_except:>7,d}")
    print("="*105)

    # 2. COMPARATIVO DA SEMANA 3 CONTRA O OFICIAL CONSOLIDADO DO PWR
    print("\n\n" + "="*95)
    print("    COMPARAÇÃO MATEMÁTICA: SEMANA 3 DIÁRIA (31/08 a 06/09) vs CONSOLIDADO OFICIAL PWR")
    print("="*95)
    
    oficial_path = os.path.join(ROOT_DIR, 'franquias', 'pwr_reports', 'Keys Summary - Franquias (Stores)(2026-08-31 - 2026-09-06).xlsx')
    if os.path.exists(oficial_path):
        df_oficial = pd.read_excel(oficial_path)
        for c in ['Order Count', 'Royalty Sales (Tot)', 'eADT', '% of Est Extreme Deliveries', 'Cash Over / Short']:
            if c in df_oficial.columns:
                df_oficial[c] = pd.to_numeric(df_oficial[c], errors='coerce').fillna(0)
        
        w3_fran = merged[(merged['Date'].isin(WEEKS['Semana 3 (31/08 a 06/09)'])) & (merged['Corp/Fran Type'] == 'F')]
        
        w3_agg = w3_fran.groupby('Store').agg({
            'Order Count': 'sum',
            'Royalty Sales (Tot)': 'sum',
            'Cash Over / Short': 'sum',
            'Delv Order Count': 'sum',
            'Extreme_Delv_Count': 'sum',
            'eADT_x_Delv': 'sum'
        }).reset_index()
        w3_agg['eADT_calc'] = w3_agg.apply(lambda r: r['eADT_x_Delv'] / r['Delv Order Count'] if r['Delv Order Count'] > 0 else 0, axis=1)
        w3_agg['Pct_Extr_calc'] = w3_agg.apply(lambda r: (r['Extreme_Delv_Count'] / r['Delv Order Count'] * 100) if r['Delv Order Count'] > 0 else 0, axis=1)

        comp = pd.merge(w3_agg, df_oficial[['Store', 'Order Count', 'Royalty Sales (Tot)', 'eADT', '% of Est Extreme Deliveries', 'Cash Over / Short']], on='Store', suffixes=('_soma_diaria', '_oficial_pwr'))
        
        total_oficial_orders = int(comp['Order Count_oficial_pwr'].sum())
        total_diaria_orders = int(comp['Order Count_soma_diaria'].sum())
        diff_orders = total_diaria_orders - total_oficial_orders
        
        total_oficial_sales = comp['Royalty Sales (Tot)_oficial_pwr'].sum()
        total_diaria_sales = comp['Royalty Sales (Tot)_soma_diaria'].sum()
        diff_sales = total_diaria_sales - total_oficial_sales

        total_oficial_cash = comp['Cash Over / Short_oficial_pwr'].sum()
        total_diaria_cash = comp['Cash Over / Short_soma_diaria'].sum()

        print(f"Lojas franqueadas comparadas: {len(comp)}")
        print(f"Total Pedidos Oficial PWR:  {total_oficial_orders:>10,d}")
        print(f"Total Pedidos Soma Diária:  {total_diaria_orders:>10,d} | Diferença: {diff_orders:d} ({(diff_orders/total_oficial_orders*100):.4f}%)")
        print(f"Total Vendas Oficial PWR:   R$ {total_oficial_sales:>12,.2f}")
        print(f"Total Vendas Soma Diária:   R$ {total_diaria_sales:>12,.2f} | Diferença: R$ {diff_sales:,.2f} ({(diff_sales/total_oficial_sales*100):.4f}%)")
        print(f"Total Caixa Sobre/Falta Of: R$ {total_oficial_cash:>12,.2f}")
        print(f"Total Caixa Sobre/Falta Di: R$ {total_diaria_cash:>12,.2f} | Diferença: R$ {(total_diaria_cash - total_oficial_cash):,.2f}")
        
        comp['diff_eadt'] = (comp['eADT_calc'] - comp['eADT']).round(2)
        comp_with_delv = comp[comp['Delv Order Count'] > 0]
        max_diff_eadt = comp_with_delv['diff_eadt'].abs().max()
        print(f"Diferença máxima de eADT loja a loja: {max_diff_eadt:.2f} minutos")
        print(f"Diferença média de eADT loja a loja:  {comp_with_delv['diff_eadt'].abs().mean():.4f} minutos")

    print("\n\n" + "="*95)
    print("    ANÁLISE DE DIAS FALTANTES / SEM MOVIMENTO (PARÂMETRO DE AUTO-RECUPERAÇÃO)")
    print("="*95)
    
    pivot_orders = merged.pivot_table(index='Store', columns='Date', values='Order Count', aggfunc='sum', fill_value=0)
    lojas_com_falha = []
    for store, row in pivot_orders.iterrows():
        dias_zerados = row[row == 0].index.tolist()
        if len(dias_zerados) > 0 and len(dias_zerados) < 28:
            tipo = merged[merged['Store'] == store]['Corp/Fran Type'].iloc[0]
            lojas_com_falha.append({
                'Store': store,
                'Type': tipo,
                'Dias_Zerados': len(dias_zerados),
                'Exemplo_Dias': dias_zerados[:3]
            })

    print(f"Total de lojas na base: {len(pivot_orders)}")
    print(f"Lojas com operação normal em todos os 28 dias: {len(pivot_orders) - len(lojas_com_falha)}")
    print(f"Lojas com dias faltantes/zerados detectadas pelo robô: {len(lojas_com_falha)}")
    if lojas_com_falha:
        print("\nExemplos de lojas identificadas para auto-recuperação/backfill:")
        for l in lojas_com_falha[:5]:
            print(f"  - Loja {l['Store']} ({'Franquia' if l['Type'] == 'F' else 'Corporativa'}): {l['Dias_Zerados']} dias sem dados. Ex: {l['Exemplo_Dias']}")

if __name__ == '__main__':
    main()
