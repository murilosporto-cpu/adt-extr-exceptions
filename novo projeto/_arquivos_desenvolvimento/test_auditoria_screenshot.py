import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 1200})
        
        page.on('console', lambda msg: print('PAGE LOG:', msg.text))
        page.on('pageerror', lambda err: print('PAGE ERROR:', err))
        
        fran_path = os.path.abspath('novo projeto/franquias/index.html')
        await page.goto(f'file:///{fran_path}')
        await page.screenshot(path='novo projeto/preview_franquias_pos_backfill.png', full_page=False)
        print('Captured preview_franquias_pos_backfill.png')
        
        # Click button
        print('Clicking tab-backfill...')
        await page.evaluate("document.getElementById('tab-backfill').click()")
        await page.wait_for_timeout(1000)
        
        await page.screenshot(path='novo projeto/preview_auditoria_pos_backfill.png', full_page=False)
        print('Captured preview_auditoria_pos_backfill.png successfully!')
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
