import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 1200})
        file_path = os.path.abspath('franquias/index.html')
        await page.goto(f'file:///{file_path}')
        await page.evaluate("
            document.body.classList.remove('gate-locked');
            const g = document.getElementById('password-gate');
            if (g) g.style.display = 'none';
        ")
        await page.wait_for_timeout(1000)
        await page.screenshot(path='novo projeto/franquias_preview.png', full_page=False)
        await browser.close()
        print('Franquias preview captured!')

if __name__ == '__main__':
    asyncio.run(main())
