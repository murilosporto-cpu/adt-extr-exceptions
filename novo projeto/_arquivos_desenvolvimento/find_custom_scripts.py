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
    
    script_info = page.evaluate("""() => {
        const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText);
        const customScripts = scripts.filter(s => s.includes('custom_date_end_selector') || s.includes('custom_date_begin_selector') || s.includes('custom_date_selection_popup'));
        return customScripts;
    }""")
    print(f"Scripts encontrados com custom_date: {len(script_info)}")
    for s in script_info:
        print("--- SCRIPT SNIPPET ---")
        print(s[:1000])
    browser.close()
