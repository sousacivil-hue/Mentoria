import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://sso.seduc.se.gov.br/"
CPF   = "78962633515"
SENHA = "130224"

async def main():
    print("=" * 55)
    print("  TESTE DE LOGIN SIAE")
    print("=" * 55)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        print("\nAbrindo SSO...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)

        print("Preenchendo CPF...")
        await page.fill("input[type='text'], input[type='email']", CPF)
        await page.wait_for_timeout(500)

        print("Preenchendo senha...")
        await page.fill("input[type='password']", SENHA)
        await page.wait_for_timeout(500)

        print("Clicando em Acessar...")
        await page.locator("button#submit-form").click()
        await page.wait_for_timeout(5000)

        print(f"\nURL apos login: {page.url}")
        if "sso.seduc.se.gov.br" not in page.url:
            print("LOGIN OK!")
        else:
            print("LOGIN FALHOU - ainda na pagina de login")

        input("\nObserve a tela e pressione ENTER para fechar...")
        await browser.close()

asyncio.run(main())
