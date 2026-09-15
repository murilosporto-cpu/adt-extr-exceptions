from playwright.sync_api import sync_playwright
import time
import os

OUTPUT_DIR = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr\novo projeto\dados_all_stores'

def apply_custom_date(page, iso_date):
    # Garante que nenhum popup anterior ficou aberto
    page.keyboard.press("Escape")
    time.sleep(0.5)
    
    # Abre seletor de data via JS para não ser interceptado por overlays
    page.evaluate("document.querySelector('#date-selection').click()")
    time.sleep(1)
    
    # Clica em Custom
    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-menu-item'))
            .find(el => el.textContent.trim() === 'Custom');
        if (item) item.click();
    }""")
    time.sleep(1.5)

    # Preenche as datas
    page.evaluate("""(dStr) => {
        const dParts = dStr.split('-');
        const dObj = new Date(parseInt(dParts[0]), parseInt(dParts[1]) - 1, parseInt(dParts[2]));
        $('#custom_date_begin_selector').dxDateBox('instance').option('value', dObj);
        $('#custom_date_end_selector').dxDateBox('instance').option('value', dObj);
    }""", iso_date)
    time.sleep(0.8)

    # Clica no search_button para disparar a busca
    page.click('#search_button')
    time.sleep(2)
    
    # Fecha o popover de data pressionando Escape
    page.keyboard.press("Escape")
    time.sleep(6) # Aguarda recarregamento do grid

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
    page.click("#scope-selection")
    time.sleep(2)
    page.locator(".dx-treeview-item:has-text('All Stores (Stores)')").first.click()
    time.sleep(5)
    print("Escopo All Stores selecionado!")
    
    # Testar 2 dias consecutivos
    test_days = ["2026-08-17", "2026-08-18"]
    for d in test_days:
        print(f"Aplicando data {d}...")
        apply_custom_date(page, d)
        print(f"Data {d} aplicada! Exportando...")
        page.evaluate("document.querySelector('.dx-icon-menu').click()")
        time.sleep(2)
        with page.expect_download(timeout=25000) as dl_info:
            page.click("text='Export to Excel (All Columns)'")
        dl = dl_info.value
        dest = os.path.join(OUTPUT_DIR, f"Keys Summary - All Stores (Stores) ({d}).xlsx")
        dl.save_as(dest)
        print(f"Salvo {d}: {os.path.getsize(dest)} bytes")
        page.keyboard.press("Escape")
        time.sleep(1)
        
    browser.close()
    print("Teste de 2 dias consecutivos concluído com sucesso!")
