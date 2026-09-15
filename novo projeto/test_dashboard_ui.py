from playwright.sync_api import sync_playwright
import os

HTML_PATH = os.path.abspath("novo projeto/index.html")
SCREENSHOT_PATH = os.path.abspath("novo projeto/dashboard_preview.png")

print(f"Testando carregamento de: {HTML_PATH}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1600, 'height': 1200})
    
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))

    page.goto(f"file:///{HTML_PATH.replace('\\', '/')}")
    page.wait_for_timeout(3000)

    # Verifica se os KPIs foram preenchidos
    kpi_adt = page.locator("#kpi-adt-num").inner_text()
    kpi_ext = page.locator("#kpi-extremes-num").inner_text()
    kpi_exc = page.locator("#kpi-exceptions-num").inner_text()

    # Conta linhas da tabela
    rows_adt = page.locator("#table-adt tbody tr").count()
    rows_exc = page.locator("#table-exceptions tbody tr").count()

    print("\n--- RESULTADO DO TESTE DE RENDERIZAÇÃO ---")
    print(f"KPI eADT: {kpi_adt}")
    print(f"KPI Extremes: {kpi_ext}")
    print(f"KPI Exceptions: {kpi_exc}")
    print(f"Linhas Tabela eADT: {rows_adt}")
    print(f"Linhas Tabela Exceptions: {rows_exc}")
    print(f"Erros de JS: {len(errors)}")
    if errors:
        for e in errors:
            print("  ERRO:", e)

    page.screenshot(path=SCREENSHOT_PATH, full_page=False)
    print(f"Screenshot salvo em: {SCREENSHOT_PATH}")
    browser.close()
