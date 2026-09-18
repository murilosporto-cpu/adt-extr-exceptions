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
    
    srcs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
    }""")
    print("Scripts externos carregados:")
    for s in srcs:
        if 'dominos' in s or 'PWR' in s or 'mobile' in s.lower():
            print(" -", s)
    browser.close()
