import os
import sys
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'dados_all_stores')

CFG_PATH = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\pwr-automation\config.json'
with open(CFG_PATH, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

USERNAME = cfg['PWR_USER']
PASSWORD = '!!dominos@2026!!'
PWR_URL = cfg['PWR_URL']

TARGET_DATES = ['2026-09-15', '2026-09-16', '2026-09-17']

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def select_scope(page, scope_name='All Stores (Stores)'):
    current = page.locator('#scope-selection').inner_text().strip()
    if current == scope_name:
        log(f'Escopo já ativo: {scope_name}')
        return

    log(f"Selecionando escopo '{scope_name}'...")
    page.click('#scope-selection')
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
    new_scope = page.locator('#scope-selection').inner_text().strip()
    log(f'Confirmado escopo ativo: {new_scope}')

def apply_custom_date(page, iso_date):
    page.keyboard.press('Escape')
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

    page.keyboard.press('Escape')
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
            page.keyboard.press('Escape')
            time.sleep(1)
            return True
        except Exception as e:
            log(f"  [Aviso] Falha na tentativa {attempt} de exportação: {e}")
            try: page.keyboard.press('Escape')
            except: pass
            time.sleep(2)
    return False

def go_to_keys_summary(page):
    log('Navegando para Keys Summary...')
    page.click("//*[contains(text(), 'KEYS')]")
    time.sleep(2)
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-menu-item'));
        const it = items.find(el => el.textContent.trim() === 'Keys Summary');
        if (it) it.click();
    }""")
    time.sleep(6)

def go_to_service_exceptions(page):
    log('Navegando para Service Exceptions...')
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
    log('=== BAIXANDO DIAS 14 E 15 DE SETEMBRO DO PWR ===')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_viewport_size({'width': 1400, 'height': 900})

        log('1. Acessando portal PWR e autenticando...')
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
        log('Login realizado com sucesso!')

        select_scope(page, 'All Stores (Stores)')

        # FASE 1: KEYS SUMMARY
        log('\n--- BAIXANDO KEYS SUMMARY ---')
        go_to_keys_summary(page)
        for dt_str in TARGET_DATES:
            log(f'Baixando Keys Summary de {dt_str}...')
            apply_custom_date(page, dt_str)
            target_file = os.path.join(OUTPUT_DIR, f'Keys Summary - All Stores (Stores) ({dt_str}).xlsx')
            export_excel(page, target_file)

        # FASE 2: SERVICE EXCEPTIONS
        log('\n--- BAIXANDO SERVICE EXCEPTIONS ---')
        go_to_service_exceptions(page)
        for dt_str in TARGET_DATES:
            log(f'Baixando Service Exceptions de {dt_str}...')
            apply_custom_date(page, dt_str)
            target_file = os.path.join(OUTPUT_DIR, f'KEYS Service Exceptions - All Stores (Stores) ({dt_str}).xlsx')
            export_excel(page, target_file)

        browser.close()
        log('Navegador finalizado com sucesso!')

if __name__ == '__main__':
    main()
