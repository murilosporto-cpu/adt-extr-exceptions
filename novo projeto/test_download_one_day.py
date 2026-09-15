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

# Ensure correct password
cfg['PWR_PASSWORD'] = '!!dominos@2026!!'

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def select_scope(page, scope_name):
    current = page.locator("#scope-selection").inner_text().strip()
    if current == scope_name:
        log(f"Escopo já está em: {scope_name}")
        return

    log(f"Selecionando escopo '{scope_name}'...")
    page.click("#scope-selection")
    time.sleep(2)
    
    # Try finding item in treeview
    item = page.locator(f".dx-treeview-item:has-text('{scope_name}')").first
    if item.count() > 0:
        item.click()
    else:
        page.evaluate(f"""(name) => {{
            const el = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-item-content'))
                .find(el => el.innerText.trim() === name);
            if (el) el.click();
        }}""", scope_name)
    
    time.sleep(5)
    new_scope = page.locator("#scope-selection").inner_text().strip()
    log(f"Novo escopo ativo: {new_scope}")

def fill_custom_dates(page, date_br):
    """Preenche início e fim com o mesmo dia (dd/mm/aaaa)."""
    page.click("#date-selection")
    time.sleep(1)
    
    # Clica no Custom
    page.evaluate("""() => {
        const customEl = Array.from(document.querySelectorAll('.dx-menu-item, span, div, a'))
            .find(el => el.textContent.trim() === 'Custom');
        if (customEl) customEl.click();
    }""")
    time.sleep(1.5)

    # Preenche ambos os inputs com date_br
    page.evaluate(f"""(d) => {{
        const inputs = document.querySelectorAll('input.dx-texteditor-input');
        if (inputs.length >= 2) {{
            inputs[0].value = d;
            inputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
            inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
            inputs[1].value = d;
            inputs[1].dispatchEvent(new Event('change', {{ bubbles: true }}));
            inputs[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}
    }}""", date_br)
    time.sleep(1)
    page.keyboard.press("Escape")
    time.sleep(6) # Aguarda recarregamento dos dados no PWR

def go_to_keys_summary(page):
    log("Navegando para Keys Summary...")
    page.evaluate("""() => {
        const btn = document.querySelector('.dx-icon-menu');
        if (btn && !document.querySelector('.dx-treeview-node')) btn.click();
    }""")
    time.sleep(2)
    page.evaluate("""() => {
        const node = Array.from(document.querySelectorAll('.dx-treeview-node, .dx-treeview-item'))
            .find(el => el.textContent.trim().includes('KEYS'));
        if (node) node.click();
    }""")
    time.sleep(2)
    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-menu-item'))
            .find(el => el.textContent.trim() === 'Keys Summary');
        if (item) item.click();
    }""")
    time.sleep(5)

def go_to_service_exceptions(page):
    log("Navegando para Service Exceptions...")
    page.evaluate("""() => {
        const btn = document.querySelector('.dx-icon-menu');
        if (btn && !document.querySelector('.dx-treeview-node')) btn.click();
    }""")
    time.sleep(2)
    page.evaluate("""() => {
        const node = Array.from(document.querySelectorAll('.dx-treeview-node, .dx-treeview-item'))
            .find(el => el.textContent.trim().includes('KEYS'));
        if (node) node.click();
    }""")
    time.sleep(2)
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('.dx-treeview-item'));
        const svc = items.filter(el => el.textContent.trim() === 'Service');
        if (svc.length >= 2) svc[1].click();
        else if (svc.length === 1) svc[0].click();
    }""")
    time.sleep(2.5)
    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-menu-item'))
            .find(el => el.textContent.trim() === 'Service Exceptions');
        if (item) item.click();
    }""")
    time.sleep(5)

def export_excel(page, dest_file, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            log(f"  Exportando Excel (tentativa {attempt}/{max_retries})...")
            page.evaluate("document.querySelector('.dx-icon-menu').click()")
            time.sleep(2)
            page.wait_for_selector("text='Export to Excel (All Columns)'", timeout=15000)
            with page.expect_download(timeout=120000) as dl_info:
                page.click("text='Export to Excel (All Columns)'")
            dl = dl_info.value
            if os.path.exists(dest_file):
                os.remove(dest_file)
            dl.save_as(dest_file)
            log(f"  [OK] Salvo: {os.path.basename(dest_file)} ({os.path.getsize(dest_file)} bytes)")
            return True
        except Exception as e:
            log(f"  [ERRO] Falha no export: {e}")
            try:
                page.keyboard.press("Escape")
            except:
                pass
            time.sleep(4)
    return False

def test_single_day():
    date_test = "2026-08-17"
    date_br = "17/08/2026"
    log(f"=== TESTE DE DOWNLOAD DE 1 DIA ({date_test}) ===")
    
    summary_file = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({date_test}).xlsx")
    exceptions_file = os.path.join(OUTPUT_DIR, f"KEYS Service Exceptions - All Stores (Stores) ({date_test}).xlsx")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_viewport_size({'width': 1400, 'height': 900})
        
        log("1. Acessando PWR...")
        page.goto(cfg['PWR_URL'])
        page.fill('#txtUsername', cfg['PWR_USER'])
        page.fill('#txtPassword', cfg['PWR_PASSWORD'])
        with page.expect_navigation(timeout=45000) as nav:
            page.evaluate("""() => {
                const d = new Date();
                document.querySelector('#txtTZOffSet').value = d.getTimezoneOffset();
                __doPostBack('btnLogin', '');
            }""")
        time.sleep(5)
        log("Login OK!")
        
        # 2. Selecionar Escopo All Stores (Stores)
        select_scope(page, "All Stores (Stores)")
        
        # 3. Baixar Keys Summary
        go_to_keys_summary(page)
        fill_custom_dates(page, date_br)
        export_excel(page, summary_file)
        
        # 4. Baixar Service Exceptions
        go_to_service_exceptions(page)
        fill_custom_dates(page, date_br)
        export_excel(page, exceptions_file)
        
        browser.close()
        log("Teste de 1 dia concluído com sucesso!")

if __name__ == '__main__':
    test_single_day()
