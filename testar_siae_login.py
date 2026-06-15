"""
Teste de login SIAE - roda com browser VISÍVEL para ver o que acontece.
Execute: python testar_siae_login.py
"""
import asyncio
from playwright.async_api import async_playwright

CPF   = input("Digite seu CPF (só números): ").strip()
SENHA = input("Digite sua senha: ").strip()

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        print("Abrindo SSO...")
        await page.goto("https://sso.seduc.se.gov.br/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        print(f"URL atual: {page.url}")
        print("Preenchendo CPF...")
        await page.locator("input[type='text'], input[type='email']").first.fill(CPF)
        await page.wait_for_timeout(500)

        print("Preenchendo senha...")
        await page.locator("input[type='password']").first.fill(SENHA)
        await page.wait_for_timeout(500)

        print("Pressionando Enter...")
        await page.locator("input[type='password']").first.press("Enter")

        await page.wait_for_timeout(5000)
        print(f"URL após login: {page.url}")

        input("\nObserve a tela e pressione ENTER aqui para fechar...")
        await browser.close()

asyncio.run(main())
