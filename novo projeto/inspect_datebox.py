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
    
    # Click date selection
    page.click('#date-selection')
    time.sleep(1)
    page.click('text=Custom')
    time.sleep(2)
    
    info = page.evaluate("""() => {
        const boxes = Array.from(document.querySelectorAll('.dx-datebox')).map(el => {
            const inst = typeof $ !== 'undefined' && $(el).dxDateBox ? $(el).dxDateBox('instance') : null;
            return inst ? String(inst.option('value')) : 'no-inst';
        });
        return {
            hasJQuery: typeof $ !== 'undefined',
            dateBoxes: boxes,
            inputs: Array.from(document.querySelectorAll('input.dx-texteditor-input')).map(i => i.value)
        };
    }""")
    print("DateBox info:", info)
    
    # Test setting date via typing vs via dxDateBox option
    inputs = page.locator('input.dx-texteditor-input').all()
    if len(inputs) >= 2:
        print("Testando digitação no Input 0...")
        inputs[0].click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type("18/08/2026")
        page.keyboard.press("Enter")
        
        inputs[1].click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.keyboard.type("18/08/2026")
        page.keyboard.press("Enter")
        time.sleep(1)
        
        # Check if there is an Apply / OK button or if Enter did it
        buttons = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.dx-button')).map(b => ({
                text: b.innerText.trim(),
                id: b.id,
                className: b.className
            })).filter(b => b.text.length > 0);
        }""")
        print("Botões visíveis na tela:", buttons)
        
    browser.close()
