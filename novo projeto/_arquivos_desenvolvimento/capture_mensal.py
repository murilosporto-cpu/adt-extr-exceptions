from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1400, 'height': 900})
    file_path = os.path.abspath('novo projeto/franquias/index.html')
    page.goto('file:///' + file_path)
    page.wait_for_timeout(2000)
    page.click('.tab-btn[data-tab="mensal"]')
    page.wait_for_timeout(2000)
    page.screenshot(path='novo projeto/_arquivos_desenvolvimento/preview_aba_mensal_corrigida.png')
    browser.close()
print('Screenshot da aba Mensal capturado!')
