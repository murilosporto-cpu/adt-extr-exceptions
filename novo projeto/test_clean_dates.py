from playwright.sync_api import sync_playwright
import time
import os
import openpyxl

OUTPUT_DIR = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr\novo projeto'

def apply_custom_date(page, iso_date):
    print(f"[{iso_date}] 1. Abrindo seletor de data...", flush=True)
    page.keyboard.press("Escape")
    time.sleep(0.5)
    page.evaluate("document.querySelector('#date-selection').click()")
    time.sleep(1)

    print(f"[{iso_date}] 2. Clicando em Custom...", flush=True)
    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-menu-item'))
            .find(el => el.textContent.trim() === 'Custom');
        if (item) item.click();
    }""")
    time.sleep(1.5)

    print(f"[{iso_date}] 3. Definindo datas no dxDateBox...", flush=True)
    page.evaluate("""(dStr) => {
        const dParts = dStr.split('-');
        const dObj = new Date(parseInt(dParts[0]), parseInt(dParts[1]) - 1, parseInt(dParts[2]));
        $('#custom_date_begin_selector').dxDateBox('instance').option('value', dObj);
        $('#custom_date_end_selector').dxDateBox('instance').option('value', dObj);
    }""", iso_date)
    
    # NÃO CLICA NO #search_button!
    # Apenas fecha o popup de data pressionando Escape
    time.sleep(0.5)
    page.keyboard.press("Escape")
    
    print(f"[{iso_date}] 4. Aguardando recarregamento do grid...", flush=True)
    # Espera o loading desaparecer ou 8 segundos
    time.sleep(7)

def export_file(page, filename):
    page.evaluate("document.querySelector('.dx-icon-menu').click()")
    time.sleep(1.5)
    with page.expect_download(timeout=30000) as dl_info:
        page.click("text='Export to Excel (All Columns)'")
    dl = dl_info.value
    dest = os.path.join(OUTPUT_DIR, filename)
    dl.save_as(dest)
    print(f"Salvo: {filename} ({os.path.getsize(dest)} bytes)", flush=True)
    page.keyboard.press("Escape")
    time.sleep(1)
    return dest

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.goto('https://pwr.dominos.com')
    page.fill('#txtUsername', 'portom')
    page.fill('#txtPassword', '!!dominos@2026!!')
    with page.expect_navigation(timeout=45000):
        page.evaluate("""() => {
            const d = new Date();
            document.querySelector('#txtTZOffSet').value = d.getTimezoneOffset();
            __doPostBack('btnLogin', '');
        }""")
    time.sleep(4)
    print("Login OK!")

    # Seleciona All Stores (Stores)
    print("Selecionando All Stores (Stores)...")
    page.click("#scope-selection")
    time.sleep(2)
    page.locator(".dx-treeview-item:has-text('All Stores (Stores)')").first.click()
    time.sleep(6)
    print("Escopo All Stores selecionado!")

    # Dia 1: 2026-08-17
    apply_custom_date(page, "2026-08-17")
    dest17 = export_file(page, "test_clean_17.xlsx")

    # Dia 2: 2026-08-18
    apply_custom_date(page, "2026-08-18")
    dest18 = export_file(page, "test_clean_18.xlsx")

    browser.close()

# Compara os 2 arquivos
print("\n--- COMPARANDO ARQUIVOS 17 E 18 ---")
wb17 = openpyxl.load_workbook(dest17, data_only=True)
wb18 = openpyxl.load_workbook(dest18, data_only=True)
ws17 = wb17.active
ws18 = wb18.active
print("Linhas 17:", ws17.max_row, "| Linhas 18:", ws18.max_row)

headers17 = [c.value for c in ws17[1]]
headers18 = [c.value for c in ws18[1]]
cols = ['Store', 'Order Count', 'eADT', 'Royalty Sales (Tot)']
idxs17 = [headers17.index(c) for c in cols if c in headers17]

print("Dados Loja Linha 2 (17):", [ws17[2][i].value for i in idxs17])
print("Dados Loja Linha 2 (18):", [ws18[2][i].value for i in idxs17])
print("Dados Loja Linha 3 (17):", [ws17[3][i].value for i in idxs17])
print("Dados Loja Linha 3 (18):", [ws18[3][i].value for i in idxs17])
