import os
import sys
import time
import json
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'dados_all_stores')
os.makedirs(OUTPUT_DIR, exist_ok=True)

CFG_PATH = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\pwr-automation\config.json'
with open(CFG_PATH, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

USERNAME = cfg['PWR_USER']
PASSWORD = '!!dominos@2026!!'
PWR_URL = cfg['PWR_URL']

START_DATE = datetime(2026, 8, 17)
END_DATE = datetime(2026, 9, 13)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_days_list():
    days = []
    curr = START_DATE
    while curr <= END_DATE:
        days.append(curr)
        curr += timedelta(days=1)
    return days

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
    """Define data de início e fim no DevExtreme e dispara atualização forçada do grid."""
    page.keyboard.press("Escape")
    time.sleep(0.3)

    # 1. Abre o menu de seleção de data
    page.evaluate("document.querySelector('#date-selection').click()")
    time.sleep(1)

    # 2. Clica na opção 'Custom'
    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-menu-item'))
            .find(el => el.textContent.trim() === 'Custom');
        if (item) item.click();
    }""")
    time.sleep(1.2)

    # 3. Define as instâncias dxDateBox e força o refresh
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

    # 4. Aguarda término do callback da DevExpress Grid
    page.wait_for_function("""() => {
        const inCb = typeof ASPxGridViewMainReport !== 'undefined' && ASPxGridViewMainReport.InCallback && ASPxGridViewMainReport.InCallback();
        const loadVisible = $('.dx-loadpanel:visible').length > 0;
        return !inCb && !loadVisible;
    }""", timeout=35000)
    time.sleep(1.5)

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

def export_excel(page, dest_file, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            page.evaluate("document.querySelector('.dx-icon-menu').click()")
            time.sleep(1.5)
            page.wait_for_selector("text='Export to Excel (All Columns)'", timeout=15000)
            with page.expect_download(timeout=60000) as dl_info:
                page.click("text='Export to Excel (All Columns)'")
            dl = dl_info.value
            temp_dest = dest_file + ".tmp"
            if os.path.exists(temp_dest):
                os.remove(temp_dest)
            dl.save_as(temp_dest)
            if os.path.exists(dest_file):
                os.remove(dest_file)
            os.rename(temp_dest, dest_file)
            log(f"  -> Salvo: {os.path.basename(dest_file)} ({os.path.getsize(dest_file):,} bytes)")
            page.keyboard.press("Escape")
            time.sleep(1)
            return True
        except Exception as e:
            log(f"  [AVISO] Tentativa {attempt} falhou ({e}), tentando novamente...")
            try:
                page.keyboard.press("Escape")
            except:
                pass
            time.sleep(3)
    return False

def run_extraction():
    days = get_days_list()
    log(f"=== INICIANDO EXTRAÇÃO DE {len(days)} DIAS (17/08/2026 a 13/09/2026) ===")
    log(f"Escopo: All Stores (Stores) | Pasta destino: {OUTPUT_DIR}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_viewport_size({'width': 1400, 'height': 900})
        
        log("1. Acessando portal PWR e autenticando...")
        page.goto(PWR_URL)
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
        
        # -------------------------------------------------------------
        # FASE 1: KEYS SUMMARY DIA A DIA (28 DIAS)
        # -------------------------------------------------------------
        log("\n--- FASE 1: EXTRAINDO KEYS SUMMARY (28 DIAS) ---")
        go_to_keys_summary(page)
        
        for idx, dt in enumerate(days, 1):
            iso_date = dt.strftime("%Y-%m-%d")
            dest_file = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({iso_date}).xlsx")
            log(f"[{idx}/{len(days)}] Keys Summary ({iso_date})...")
            try:
                apply_custom_date(page, iso_date)
                ok = export_excel(page, dest_file)
                if not ok:
                    log(f"  [ERRO] Falha ao exportar Keys Summary de {iso_date}")
            except Exception as e:
                log(f"  [ERRO] Exceção em {iso_date}: {e}")
                
        # -------------------------------------------------------------
        # FASE 2: KEYS SERVICE EXCEPTIONS DIA A DIA (28 DIAS)
        # -------------------------------------------------------------
        log("\n--- FASE 2: EXTRAINDO KEYS SERVICE EXCEPTIONS (28 DIAS) ---")
        go_to_service_exceptions(page)
        
        for idx, dt in enumerate(days, 1):
            iso_date = dt.strftime("%Y-%m-%d")
            dest_file = os.path.join(OUTPUT_DIR, f"KEYS Service Exceptions - All Stores (Stores) ({iso_date}).xlsx")
            log(f"[{idx}/{len(days)}] Service Exceptions ({iso_date})...")
            try:
                apply_custom_date(page, iso_date)
                ok = export_excel(page, dest_file)
                if not ok:
                    log(f"  [ERRO] Falha ao exportar Service Exceptions de {iso_date}")
            except Exception as e:
                log(f"  [ERRO] Exceção em {iso_date}: {e}")
                
        browser.close()
        log("\n=== EXTRAÇÃO COMPLETA DE 28 DIAS FINALIZADA COM SUCESSO! ===")

if __name__ == '__main__':
    run_extraction()
