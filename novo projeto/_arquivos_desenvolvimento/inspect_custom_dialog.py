from playwright.sync_api import sync_playwright
import time

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
    
    page.click('#date-selection')
    time.sleep(1)
    
    # Click Custom
    page.evaluate("""() => {
        const item = Array.from(document.querySelectorAll('.dx-menu-item'))
            .find(el => el.textContent.trim() === 'Custom');
        if (item) item.click();
    }""")
    time.sleep(2)
    
    # Take screenshot of the custom date dialog to see what it looks like!
    dialog_shot = r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\cafe-com-pwr\novo projeto\custom_dialog.png'
    page.screenshot(path=dialog_shot)
    print("Screenshot do diálogo de data customizada salvo:", dialog_shot)
    
    elements = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('input, .dx-button, .dx-datebox, .dx-popup-content *')).map(el => ({
            tag: el.tagName,
            id: el.id,
            className: el.className,
            value: el.value || '',
            text: el.innerText ? el.innerText.trim() : ''
        })).filter(e => e.id || e.text || e.value);
    }""")
    print("Elementos após clicar em Custom:")
    for el in elements[:40]:
        print(" >", el)
    browser.close()
