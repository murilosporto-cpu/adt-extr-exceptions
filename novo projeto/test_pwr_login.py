import json
import time
from playwright.sync_api import sync_playwright

cfg = json.load(open(r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\pwr-automation\config.json', encoding='utf-8'))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1400, 'height': 900})
    print("Acessando PWR...", flush=True)
    page.goto(cfg['PWR_URL'], timeout=60000)
    print("Preenchendo credenciais...", flush=True)
    page.fill('#txtUsername', cfg['PWR_USER'])
    page.fill('#txtPassword', cfg['PWR_PASSWORD'])
    print("Clicando no botão de login...", flush=True)
    page.click('#dxLoginButton', no_wait_after=True)
    
    print("Aguardando carregamento pós-login...", flush=True)
    page.wait_for_selector('#scope-selection', timeout=45000)
    time.sleep(3)
    
    print("URL atual:", page.url, flush=True)
    print("Titulo:", page.title(), flush=True)

    
    scope_el = page.locator('#scope-selection')
    if scope_el.count() > 0:
        print("Escopo atual na tela:", scope_el.inner_text(), flush=True)
        page.click('#scope-selection')
        time.sleep(2)
        scopes = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.dx-treeview-item, .dx-item-content')).map(el => el.innerText.trim()).filter(t => t.length > 0);
        }""")
        print("Opções de escopo encontradas:", flush=True)
        for s in set(scopes):
            print("  -", s, flush=True)
    else:
        print("Elemento #scope-selection não encontrado!", flush=True)
        
    browser.close()
    print("Teste finalizado com sucesso!", flush=True)
