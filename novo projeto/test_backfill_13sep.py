import os
import sys
import time
import json
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
            log(f"  -> Salvo com sucesso: {os.path.basename(dest_file)} ({os.path.getsize(dest_file):,} bytes)")
            page.keyboard.press("Escape")
            time.sleep(1)
            return True
        except Exception as e:
            log(f"  [Aviso] Falha na tentativa {attempt} de exportação: {e}")
            page.keyboard.press("Escape")
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

def main():
    test_date = "2026-09-13"
    log(f"Iniciando verificação de backfill para o dia {test_date} no PWR...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 950})

        log("Acessando PWR...")
        page.goto(PWR_URL, timeout=60000)
        time.sleep(2)

        if page.locator("#txtLogin").count() > 0:
            log("Realizando Login...")
            page.fill("#txtLogin", USERNAME)
            page.fill("#txtPassword", PASSWORD)
            page.click("#btnLogin")
            time.sleep(8)

        log("Login efetuado com sucesso.")
        select_scope(page, "All Stores (Stores)")

        # 1. Keys Summary
        go_to_keys_summary(page)
        log(f"Aplicando data {test_date} em Keys Summary...")
        apply_custom_date(page, test_date)
        
        sum_new_path = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({test_date}).new.xlsx")
        export_excel(page, sum_new_path)

        # 2. Service Exceptions
        go_to_service_exceptions(page)
        log(f"Aplicando data {test_date} em Service Exceptions...")
        apply_custom_date(page, test_date)
        
        exc_new_path = os.path.join(OUTPUT_DIR, f"KEYS Service Exceptions - All Stores (Stores) ({test_date}).new.xlsx")
        export_excel(page, exc_new_path)

        browser.close()
        log("Navegador fechado.")

    # 3. Comparar arquivo antigo vs novo
    old_sum_path = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({test_date}).xlsx")
    df_old = pd.read_excel(old_sum_path)
    df_new = pd.read_excel(sum_new_path)

    df_old['Store'] = df_old['Store'].astype(str).str.strip().str.zfill(5)
    df_new['Store'] = df_new['Store'].astype(str).str.strip().str.zfill(5)

    old_orders = df_old.set_index('Store')['Order Count'].fillna(0).to_dict()
    new_orders = df_new.set_index('Store')['Order Count'].fillna(0).to_dict()

    recovered = []
    for sid, n_ord in new_orders.items():
        o_ord = old_orders.get(sid, 0)
        if o_ord == 0 and n_ord > 0:
            recovered.append((sid, n_ord))

    log(f"=== RESULTADO DA VARREDURA PARA {test_date} ===")
    log(f"Lojas que subiram vendas agora (antes tinham 0 pedidos): {len(recovered)}")
    for sid, n_ord in recovered[:20]:
        log(f"  -> Loja {sid}: {int(n_ord)} pedidos recuperados!")

    if len(recovered) > 0:
        log("Substituindo arquivos antigos pelos novos atualizados...")
        os.replace(sum_new_path, old_sum_path)
        old_exc_path = os.path.join(OUTPUT_DIR, f"KEYS Service Exceptions - All Stores (Stores) ({test_date}).xlsx")
        os.replace(exc_new_path, old_exc_path)
        log("Arquivos do dia 13/09 atualizados com sucesso!")
    else:
        log("Nenhuma nova subida detectada para este dia.")
        if os.path.exists(sum_new_path): os.remove(sum_new_path)
        if os.path.exists(exc_new_path): os.remove(exc_new_path)

if __name__ == '__main__':
    main()
