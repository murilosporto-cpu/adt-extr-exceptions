import os
import sys
import time
import json
import re
from datetime import datetime
import pandas as pd
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'dados_all_stores')

CFG_PATH = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\pwr-automation\config.json'
with open(CFG_PATH, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

USERNAME = cfg['PWR_USER']
PASSWORD = '!!dominos@2026!!'
PWR_URL = cfg['PWR_URL']

def get_dynamic_sweep_dates(min_date="2026-08-24"):
    """
    Identifica dinamicamente quais datas do painel possuem lojas ativas sem vendas
    (pendências de subida tardia no PWR).
    Retorna as datas ordenadas da mais recente para a mais antiga.
    """
    try:
        from atualizar_painel import carregar_mapeamentos, carregar_dados_diarios, calcular_backfill
        fran_map, corp_map = carregar_mapeamentos()
        daily_data, _ = carregar_dados_diarios()
        bf_fran = calcular_backfill(daily_data, fran_map)
        bf_corp = calcular_backfill(daily_data, corp_map)
        
        from collections import Counter
        date_counts = Counter()
        for b in bf_fran + bf_corp:
            for d in b['missingDays']:
                if d >= min_date:
                    date_counts[d] += 1
                    
        # Sempre incluir os últimos 3 dias existentes na base, pois são os mais propensos a atraso
        all_existing_dates = sorted([d for d in daily_data.keys() if d >= min_date], reverse=True)
        recent_days = all_existing_dates[:3]

        # Verificar se dias recentes do calendário (até ontem) estão faltando na base e incluí-los
        from datetime import date, timedelta
        today = date.today()
        calendar_recent = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)]
        missing_calendar_days = [d for d in calendar_recent if d >= min_date and d not in daily_data]
        
        # Datas com pendência ordenadas da mais recente para a mais antiga
        dates_with_missing = [d for d, cnt in sorted(date_counts.items(), key=lambda x: x[0], reverse=True) if cnt > 0]
        
        final_dates = []
        for d in missing_calendar_days + recent_days + dates_with_missing:
            if d not in final_dates:
                final_dates.append(d)
                
        return final_dates
    except Exception as e:
        print(f"[AVISO] Não foi possível calcular datas dinamicamente ({e}). Usando datas padrão.")
        return [
            "2026-09-17", "2026-09-16", "2026-09-15", "2026-09-14", "2026-09-13",
            "2026-09-12", "2026-09-11", "2026-09-10", "2026-09-09", "2026-09-08"
        ]


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def select_scope(page, scope_name="All Stores (Stores)"):
    current = page.locator("#scope-selection").inner_text().strip()
    if current == scope_name:
        log(f"Escopo já ativo: {scope_name}")
        return

    log(f"Selecionando escopo '{scope_name}'...")
    page.click("#scope-selection")
    time.sleep(2)
    
    item = page.locator(f".dx-treeview-item:has-text('{scope_name}')").first
    if item.count() > 0:
        item.click()
    else:
        page.evaluate(f"""(name) => {{
            const el = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-item-content'))
                .find(el => el.innerText.trim() === name);
            if (el) el.click();
        }}""", scope_name)
    
    time.sleep(6)
    new_scope = page.locator("#scope-selection").inner_text().strip()
    log(f"Confirmado escopo ativo: {new_scope}")

def apply_custom_date(page, iso_date):
    page.keyboard.press("Escape")
    time.sleep(0.3)

    page.evaluate("document.querySelector('#date-selection').click()")
    time.sleep(1)

    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-menu-item'))
            .find(el => el.textContent.trim() === 'Custom');
        if (item) item.click();
    }""")
    time.sleep(1.2)

    page.evaluate("""(dStr) => {
        const parts = dStr.split('-');
        const dObj = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        
        $('#custom_date_begin_selector').dxDateBox('instance').option('value', dObj);
        $('#custom_date_end_selector').dxDateBox('instance').option('value', dObj);
        
        if (PwrJSDateFilters._selectedDateFilterOption) {
            PwrJSDateFilters._selectedDateFilterOption.BeginDate = dObj;
            PwrJSDateFilters._selectedDateFilterOption.EndDate = dObj;
        }
        
        PwrJSSpa.RefreshPWRReport();
    }""", iso_date)

    page.keyboard.press("Escape")
    time.sleep(1.5)

    page.wait_for_function("""() => {
        const inCb = typeof ASPxGridViewMainReport !== 'undefined' && ASPxGridViewMainReport.InCallback && ASPxGridViewMainReport.InCallback();
        const loadVisible = $('.dx-loadpanel:visible').length > 0;
        return !inCb && !loadVisible;
    }""", timeout=35000)
    time.sleep(1.5)

def export_excel(page, dest_file, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            page.evaluate("document.querySelector('.dx-icon-menu').click()")
            time.sleep(1.5)
            page.wait_for_selector("text='Export to Excel (All Columns)'", timeout=15000)
            with page.expect_download(timeout=60000) as dl_info:
                page.click("text='Export to Excel (All Columns)'")
            dl = dl_info.value
            if os.path.exists(dest_file):
                os.remove(dest_file)
            dl.save_as(dest_file)
            log(f"  -> Salvo: {os.path.basename(dest_file)} ({os.path.getsize(dest_file):,} bytes)")
            page.keyboard.press("Escape")
            time.sleep(1)
            return True
        except Exception as e:
            log(f"  [Aviso] Falha na tentativa {attempt} de exportação: {e}")
            try:
                page.keyboard.press("Escape")
            except:
                pass
            time.sleep(2)
    return False

def go_to_keys_summary(page):
    log("Navegando para Keys Summary...")
    page.click("//*[contains(text(), 'KEYS')]")
    time.sleep(2)
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-menu-item'));
        const it = items.find(el => el.textContent.trim() === 'Keys Summary');
        if (it) it.click();
    }""")
    time.sleep(6)

def go_to_service_exceptions(page):
    log("Navegando para Service Exceptions...")
    page.click("//*[contains(text(), 'KEYS')]")
    time.sleep(2)
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('.dx-treeview-item'));
        const serviceItems = items.filter(el => el.textContent.trim() === 'Service');
        if (serviceItems.length >= 2) {
            serviceItems[1].click();
        } else if (serviceItems.length === 1) {
            serviceItems[0].click();
        }
    }""")
    time.sleep(3.5)
    page.click("text='Service Exceptions'")
    time.sleep(6)

def run_backfill(target_dates=None):
    if not target_dates:
        target_dates = get_dynamic_sweep_dates()
        
    log("=== INICIANDO VARREDURA DE SUBIDA TARDIA NO PWR ===")
    log(f"Datas alvo: {len(target_dates)} datas ({', '.join(target_dates)})")

    all_recovered_overall = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_viewport_size({'width': 1400, 'height': 900})

        log("1. Acessando portal PWR e autenticando...")
        page.goto(PWR_URL, timeout=60000)
        page.fill('#txtUsername', USERNAME)
        page.fill('#txtPassword', PASSWORD)
        with page.expect_navigation(timeout=45000):
            page.evaluate("""() => {
                const d = new Date();
                document.querySelector('#txtTZOffSet').value = d.getTimezoneOffset();
                __doPostBack('btnLogin', '');
            }""")
        time.sleep(4)
        log("Login realizado com sucesso!")

        select_scope(page, "All Stores (Stores)")

        # ---------------------------------------------------------
        # FASE 1: KEYS SUMMARY DAS DATAS ALVO
        # ---------------------------------------------------------
        log("\n--- VERIFICANDO KEYS SUMMARY ---")
        go_to_keys_summary(page)

        for idx, dt_str in enumerate(target_dates, 1):
            log(f"[{idx}/{len(target_dates)}] Verificando Keys Summary para {dt_str}...")
            apply_custom_date(page, dt_str)
            new_file = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({dt_str}).new.xlsx")
            ok = export_excel(page, new_file)
            if not ok:
                log(f"  [ERRO] Falha ao exportar Keys Summary de {dt_str}")

        # ---------------------------------------------------------
        # FASE 2: KEYS SERVICE EXCEPTIONS DAS DATAS ALVO
        # ---------------------------------------------------------
        log("\n--- VERIFICANDO KEYS SERVICE EXCEPTIONS ---")
        go_to_service_exceptions(page)

        for idx, dt_str in enumerate(target_dates, 1):
            log(f"[{idx}/{len(target_dates)}] Verificando Service Exceptions para {dt_str}...")
            apply_custom_date(page, dt_str)
            new_file = os.path.join(OUTPUT_DIR, f"KEYS Service Exceptions - All Stores (Stores) ({dt_str}).new.xlsx")
            ok = export_excel(page, new_file)
            if not ok:
                log(f"  [ERRO] Falha ao exportar Service Exceptions de {dt_str}")

        browser.close()
        log("Navegador finalizado com sucesso.")

    # ---------------------------------------------------------
    # FASE 3: COMPARAÇÃO E ATUALIZAÇÃO DOS ARQUIVOS
    # ---------------------------------------------------------
    log("\n--- COMPARANDO DADOS E ATUALIZANDO HISTÓRICO ---")
    
    total_recovered_stores_count = 0
    total_recovered_orders_count = 0

    for dt_str in target_dates:
        old_sum_path = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({dt_str}).xlsx")
        new_sum_path = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({dt_str}).new.xlsx")
        old_exc_path = os.path.join(OUTPUT_DIR, f"KEYS Service Exceptions - All Stores (Stores) ({dt_str}).xlsx")
        new_exc_path = os.path.join(OUTPUT_DIR, f"KEYS Service Exceptions - All Stores (Stores) ({dt_str}).new.xlsx")

        if not os.path.exists(new_sum_path):
            continue

        df_old = pd.read_excel(old_sum_path)
        df_new = pd.read_excel(new_sum_path)

        df_old['Store'] = df_old['Store'].astype(str).str.strip().str.zfill(5)
        df_new['Store'] = df_new['Store'].astype(str).str.strip().str.zfill(5)

        old_orders = df_old.set_index('Store')['Order Count'].fillna(0).to_dict()
        new_orders = df_new.set_index('Store')['Order Count'].fillna(0).to_dict()

        date_recovered = []
        for sid, n_ord in new_orders.items():
            if sid == '19499': continue
            o_ord = old_orders.get(sid, 0)
            if o_ord == 0 and n_ord > 0:
                date_recovered.append((sid, int(n_ord)))

        if len(date_recovered) > 0:
            log(f"[{dt_str}] RECUPERADAS {len(date_recovered)} LOJAS que subiram vendas:")
            for sid, n_ord in date_recovered:
                log(f"   -> Loja {sid}: {n_ord} pedidos recuperados!")
                total_recovered_orders_count += n_ord
            total_recovered_stores_count += len(date_recovered)
            all_recovered_overall[dt_str] = date_recovered

            # Substitui arquivo antigo pelo novo
            os.replace(new_sum_path, old_sum_path)
            if os.path.exists(new_exc_path):
                os.replace(new_exc_path, old_exc_path)
            log(f"  -> Arquivos de {dt_str} atualizados na base!")
        else:
            log(f"[{dt_str}] Nenhuma alteração (mesmos dados de vendas).")
            if os.path.exists(new_sum_path): os.remove(new_sum_path)
            if os.path.exists(new_exc_path): os.remove(new_exc_path)

    log("\n=== RESUMO GERAL DA VARREDURA ===")
    log(f"Total de lojas que subiram vendas tardiamente: {total_recovered_stores_count}")
    log(f"Total de pedidos adicionais recuperados: {total_recovered_orders_count}")

    # ---------------------------------------------------------
    # FASE 4: RECONSTRUÇÃO DOS PAINÉIS
    # ---------------------------------------------------------
    if total_recovered_stores_count > 0:
        log("\nReconstruindo data.json e data.js com os novos dados...")
        import subprocess
        subprocess.run(["python", os.path.join(BASE_DIR, "atualizar_painel.py")], check=True)
        log("Painéis Franquias e Lojas Próprias atualizados com sucesso!")
    else:
        log("Histórico já estava atualizado com os últimos dados disponíveis.")

if __name__ == '__main__':
    # Permite passar datas específicas como argumento: python varredura_backfill_pwr.py 2026-09-15 2026-09-16
    args = sys.argv[1:]
    target = args if len(args) > 0 else None
    run_backfill(target)
