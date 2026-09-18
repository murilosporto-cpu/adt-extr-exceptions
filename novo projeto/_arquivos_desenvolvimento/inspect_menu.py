import time
from playwright.sync_api import sync_playwright

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
    
    # Open hamburger menu
    page.evaluate("document.querySelector('.dx-icon-menu').click()")
    time.sleep(2)
    
    # Click on KEYS to expand
    page.evaluate("""() => {
        const n = Array.from(document.querySelectorAll('.dx-treeview-node, .dx-treeview-item'))
            .find(el => el.innerText.trim().includes('KEYS'));
        if (n) n.click();
    }""")
    time.sleep(2)
    
    # Check tree items
    items = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.dx-treeview-item')).map(el => el.innerText.trim());
    }""")
    print("Itens encontrados no menu após expandir KEYS:")
    for it in items:
        if it:
            print("  -", it)
            
    # Check if there is Service or Service Exceptions
    svc_items = [it for it in items if 'service' in it.lower() or 'exception' in it.lower()]
    print("\nItens relacionados a Service/Exceptions:", svc_items)
    
    browser.close()
