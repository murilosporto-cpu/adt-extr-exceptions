from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
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

    page.click("//*[contains(text(), 'KEYS')]")
    time.sleep(2)
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-menu-item'));
        const it = items.find(el => el.textContent.trim() === 'Keys Summary');
        if (it) it.click();
    }""")
    time.sleep(6)
    print("Keys Summary carregado.")

    def set_date(d_str):
        print(f"\n--- APLICANDO DATA {d_str} ---")
        # Abre Custom
        page.click("#date-selection")
        time.sleep(1)
        page.evaluate("""() => {
            const item = Array.from(document.querySelectorAll('.dx-menu-item'))
                .find(el => el.textContent.trim() === 'Custom');
            if (item) item.click();
        }""")
        time.sleep(1.5)

        # Define as datas
        page.evaluate(f"""() => {{
            const parts = '{d_str}'.split('-');
            const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
            const beginInst = $('#custom_date_begin_selector').dxDateBox('instance');
            const endInst = $('#custom_date_end_selector').dxDateBox('instance');
            
            beginInst.option('value', d);
            if (endInst && $('#custom_date_end').is(':visible')) {{
                endInst.option('value', d);
            }}
            // Oculta o popup customizado com jQuery .hide()
            $('#custom_date_selection_popup').hide();
        }}""")
        time.sleep(6) # Aguarda recarregamento do grid

        status = page.evaluate("""() => {
            const grid = $('.dx-datagrid').dxDataGrid('instance');
            const ds = grid ? grid.getDataSource() : null;
            const items = ds ? ds.items() : [];
            const dateText = $('#date-selection').text().trim();
            // Pega uma loja que sabemos que tem movimento, ex loja index 1
            const item1 = items.length > 1 ? items[1] : (items.length > 0 ? items[0] : null);
            return {
                dateText: dateText,
                totalItems: items.length,
                storeData: item1 ? {
                    Store: item1.Store,
                    Orders: item1.Order_Count,
                    Sales: item1.Total_Sales,
                    eADT: item1.eADT
                } : null
            };
        }""")
        print(f"Resultado {d_str}:", status)

    set_date("2026-08-17")
    set_date("2026-08-18")
    set_date("2026-08-19")

    browser.close()
