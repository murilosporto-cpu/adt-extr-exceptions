from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1400, 'height': 900})
    
    # Intercept network responses to see PWR report API calls
    def on_response(response):
        if 'pwr' in response.url.lower() and ('get' in response.url.lower() or 'report' in response.url.lower() or 'data' in response.url.lower() or 'grid' in response.url.lower() or 'api' in response.url.lower() or 'ashx' in response.url.lower() or 'asmx' in response.url.lower()):
            print(f"[NET] {response.status} {response.url[:100]}")
    page.on('response', on_response)

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

    page.click("//*[contains(text(), 'KEYS')]")
    time.sleep(2)
    page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('.dx-treeview-item, .dx-menu-item'));
        const it = items.find(el => el.textContent.trim() === 'Keys Summary');
        if (it) it.click();
    }""")
    time.sleep(6)

    # Let's inspect the active report parameters in PwrJSSpa
    spa_state = page.evaluate("""() => {
        return {
            selectedReport: PwrJSSpa._selectedReport ? {
                ReportName: PwrJSSpa._selectedReport.ReportName,
                ReportID: PwrJSSpa._selectedReport.ReportID,
                RptDateFilterName: PwrJSSpa._selectedReport.RptDateFilterName,
                RptScopeFilterName: PwrJSSpa._selectedReport.RptScopeFilterName
            } : null,
            selectedDateFilterOption: PwrJSDateFilters._selectedDateFilterOption,
            currentDateFilter: PwrJSDateFilters._currentDateFilter
        };
    }""")
    print("SPA State:", json.dumps(spa_state, indent=2))

    browser.close()
