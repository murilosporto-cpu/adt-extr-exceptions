import json
import time
from playwright.sync_api import sync_playwright

cfg = json.load(open(r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\pwr-automation\config.json', encoding='utf-8'))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://pwr.dominos.com')
    page.fill('#txtUsername', cfg['PWR_USER'])
    page.fill('#txtPassword', cfg['PWR_PASSWORD'])
    
    # Trigger postback directly
    with page.expect_navigation(timeout=45000) as nav:
        page.evaluate("""() => {
            const d = new Date();
            document.querySelector('#txtTZOffSet').value = d.getTimezoneOffset();
            __doPostBack('btnLogin', '');
        }""")
        
    print("URL após postback:", page.url)
    
    # Check if login succeeded or if there is an error message
    err = page.evaluate("""() => {
        const lbl = document.querySelector('#lblError, .error-message, #errorMessage, .dx-error-message');
        return lbl ? lbl.innerText : null;
    }""")
    print("Mensagem de erro na tela:", err)
    
    body = page.inner_text('body')
    print("Primeiras linhas do body:")
    for l in body.splitlines()[:10]:
        if l.strip():
            print("  >", l.strip())
            
    browser.close()
