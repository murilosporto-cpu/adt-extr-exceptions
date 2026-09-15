import time
from playwright.sync_api import sync_playwright

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
    print("1. URL inicial:", page.url, flush=True)
    
    # Click KEYS
    page.click("//*[contains(text(), 'KEYS')]")
    time.sleep(2)
    print("2. Clicou em KEYS", flush=True)
    
    # Click second Service item
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('.dx-treeview-item'));
        const serviceItems = items.filter(el => el.textContent.trim() === 'Service');
        if (serviceItems.length >= 2) {
            serviceItems[1].click();
        } else if (serviceItems.length === 1) {
            serviceItems[0].click();
        }
    }""")
    time.sleep(4)
    print("3. Clicou em Service", flush=True)
    
    # Click Service Exceptions
    page.click("text='Service Exceptions'")
    time.sleep(5)
    print("4. URL pós-Service Exceptions:", page.url, flush=True)
    
    # Open hamburger menu for export
    page.evaluate("document.querySelector('.dx-icon-menu').click()")
    time.sleep(2)
    
    with page.expect_download(timeout=20000) as download_info:
        page.click("text='Export to Excel (All Columns)'")
    dl = download_info.value
    print("5. Suggested filename:", dl.suggested_filename, flush=True)
    
    dest = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr\novo projeto\test_exc_sample.xlsx'
    dl.save_as(dest)
    print(f"Salvo em: {dest}", flush=True)
    browser.close()
