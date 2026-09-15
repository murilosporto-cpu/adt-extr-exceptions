from playwright.sync_api import sync_playwright
import os

HTML_PATH = os.path.abspath("novo projeto/index.html")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1600, 'height': 1200})
    page.goto(f"file:///{HTML_PATH.replace('\\', '/')}")
    page.wait_for_timeout(2000)

    # Scroll down to Service Exceptions
    page.locator("#section-exceptions").scroll_into_view_if_needed()
    page.wait_for_timeout(1000)
    page.screenshot(path="novo projeto/screenshot_exceptions.png")
    print("Screenshot Exceptions salvo.")

    # Clica na aba Análise de Risco
    page.click("#tab-risco")
    page.wait_for_timeout(1000)
    page.screenshot(path="novo projeto/screenshot_risco.png")
    print("Screenshot Risco salvo.")

    # Clica na aba Auditoria de Subida
    page.click("#tab-backfill")
    page.wait_for_timeout(1000)
    page.screenshot(path="novo projeto/screenshot_backfill.png")
    print("Screenshot Backfill salvo.")

    browser.close()
