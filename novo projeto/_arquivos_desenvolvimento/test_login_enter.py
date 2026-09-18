import json
import time
from playwright.sync_api import sync_playwright

cfg = json.load(open(r'c:\Users\muril\OneDrive\FRANQUIAS\master mind\pwr-automation\config.json', encoding='utf-8'))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1400, 'height': 900})
    
    print("1. Acessando PWR...", flush=True)
    page.goto(cfg['PWR_URL'])
    
    print("2. Preenchendo credenciais...", flush=True)
    page.fill('#txtUsername', cfg['PWR_USER'])
    page.fill('#txtPassword', cfg['PWR_PASSWORD'])
    
    print("3. Clicando em Login...", flush=True)
    # Pressionar Enter no campo de senha ou clicar no botão
    with page.expect_navigation(timeout=30000) as nav:
        page.keyboard.press("Enter")
        
    print("4. Navegacao concluida!", flush=True)
    print("URL pós-login:", page.url, flush=True)
    time.sleep(5)
    
    print("5. Verificando escopo atual...", flush=True)
    scope = page.locator("#scope-selection").inner_text()
    print("Escopo ativo:", scope, flush=True)
    
    browser.close()
