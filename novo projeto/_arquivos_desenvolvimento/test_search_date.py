from playwright.sync_api import sync_playwright
import time
import pandas as pd

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
    
    # 1. Abrir seletor de data e clicar em Custom
    page.click('#date-selection')
    time.sleep(1)
    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-menu-item'))
            .find(el => el.textContent.trim() === 'Custom');
        if (item) item.click();
    }""")
    time.sleep(2)
    
    # 2. Definir as datas via dxDateBox no custom_date_begin_selector e end_selector
    test_date_iso = "2026-08-17" # ou Date object
    page.evaluate("""(dStr) => {
        const dParts = dStr.split('-');
        const dObj = new Date(parseInt(dParts[0]), parseInt(dParts[1]) - 1, parseInt(dParts[2]));
        $('#custom_date_begin_selector').dxDateBox('instance').option('value', dObj);
        $('#custom_date_end_selector').dxDateBox('instance').option('value', dObj);
    }""", test_date_iso)
    time.sleep(1)
    
    # 3. Clicar no search_button!
    print("Clicando no #search_button...", flush=True)
    page.click('#search_button')
    time.sleep(8) # Aguarda grid recarregar
    
    # Verifica texto atual no #date-selection
    date_text = page.locator('#date-selection').inner_text().strip()
    print("Texto do date-selection após search:", date_text, flush=True)
    
    # Exporta para testar
    page.evaluate("document.querySelector('.dx-icon-menu').click()")
    time.sleep(2)
    with page.expect_download(timeout=25000) as dl_info:
        page.click("text='Export to Excel (All Columns)'")
    dl = dl_info.value
    dest = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr\novo projeto\test_search_17ago.xlsx'
    dl.save_as(dest)
    print("Download teste concluído:", dest, flush=True)
    
    df = pd.read_excel(dest)
    print("Total de lojas baixadas:", len(df))
    # Check store 19506
    sub = df[df['Store'].astype(str) == '19506']
    if len(sub) > 0:
        print("Loja 19506 Orders:", sub.iloc[0]['Order Count'], "eADT:", sub.iloc[0]['eADT'])
    browser.close()
