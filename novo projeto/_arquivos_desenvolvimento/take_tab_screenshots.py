import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1600, 'height': 1000})
        await page.goto('https://adt-extr-exceptions-v1ok.vercel.app/franquias/')
        await page.wait_for_timeout(2000)
        # Check password gate
        # Let's see if password gate is present
        gate = await page.$('#password-gate')
        if gate:
            await page.fill('#gate-password', 'dominos2024') # or let's see what password is in app.js
            await page.click('#btn-enter')
            await page.wait_for_timeout(1500)
        await page.screenshot(path='novo projeto/live_vercel_preview.png', full_page=False)
        await browser.close()
        print('Live vercel preview captured!')

if __name__ == '__main__':
    asyncio.run(main())
