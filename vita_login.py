import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://siga.activesoft.com.br/login/"
LOGIN = "seu_usuario"   # <-- coloque seu usuario/CPF/matricula
SENHA = "sua_senha"     # <-- coloque sua senha


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print("Abrindo pagina de login do Vita...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(3000)

        # Tenta preencher usuario
        try:
            usuario = page.locator(
                "input[name='usuario'], input[name='login'], input[name='username'], "
                "input[name='cpf'], input[id='usuario'], input[id='login'], "
                "input[id='username'], input[type='text']:visible"
            ).first
            await usuario.fill(LOGIN)
            print("  Usuario preenchido")
        except Exception as e:
            print(f"  ERRO usuario: {e}")

        # Tenta preencher senha
        try:
            senha = page.locator("input[type='password']").first
            await senha.fill(SENHA)
            print("  Senha preenchida")
        except Exception as e:
            print(f"  ERRO senha: {e}")

        # Tenta clicar em entrar
        try:
            entrar = page.locator(
                "button[type='submit'], input[type='submit'], "
                "button:has-text('Entrar'), button:has-text('Login'), "
                "button:has-text('Acessar')"
            ).first
            await entrar.click()
            print("  Botao de login clicado")
        except Exception as e:
            print(f"  ERRO botao: {e}")
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(4000)
        print(f"  URL atual: {page.url}")

        input("\nVerifique se fez login. ENTER para fechar...")
        await browser.close()


asyncio.run(main())
