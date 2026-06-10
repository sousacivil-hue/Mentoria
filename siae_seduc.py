import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://sso.seduc.se.gov.br/sistemas"
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
LOGIN = "789.626.335-15"
SENHA = "130224"
METODOLOGIA = "Aula expositiva dialogada com apresentacao do conteudo no quadro, resolucao de exercicios e participacao ativa dos alunos."

CONTEUDOS = {
    "6": "Criterios de divisibilidade por 4 e por 5.",
    "7": "Problemas envolvendo porcentagem.",
    "3": "Problemas envolvendo razao e proporcao.",
}


def get_conteudo(serie: str) -> str:
    for chave, conteudo in CONTEUDOS.items():
        if chave in serie:
            return conteudo
    return "Conteudo nao definido"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print("=" * 55)
        print("  PREENCHIMENTO AUTOMATICO - SIAE SEDUC-SE")
        print("=" * 55)

        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)
        try:
            await page.fill("input[name='username'], input[type='text'], input[name='login']", LOGIN)
            await page.fill("input[name='password'], input[type='password'], input[name='senha']", SENHA)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(4000)
        except Exception:
            pass

        print("\n" + "=" * 55)
        print("Se nao fez login automaticamente, faca manualmente.")
        print("Depois navegue ate a tela de AULAS do SIAE.")
        print("Quando ver a lista de aulas, pressione ENTER aqui.")
        print("=" * 55)
        input("\n>>> ENTER quando estiver na tela de aulas: ")

        await page.wait_for_timeout(2000)

        if "Aula" not in page.url:
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(3000)

        print("\nIniciando preenchimento...\n")
        aula_num = 0

        while True:
            await page.wait_for_timeout(1000)

            linhas = page.locator("tr:has-text('para registrar')")
            total_linhas = await linhas.count()

            if total_linhas == 0:
                print("Todas as aulas preenchidas!")
                break

            linha = linhas.first
            serie_texto = await linha.locator("td").nth(3).inner_text()
            conteudo = get_conteudo(serie_texto)
            print(f"Aula {aula_num + 1}: {serie_texto.strip()[:50]} -> {conteudo[:40]}...")

            btn_azul = linha.locator("a.btn-primary, a.btn-info, a.btn[class*='primary']").first
            await btn_azul.scroll_into_view_if_needed()
            await btn_azul.click()
            await page.wait_for_timeout(2000)

            try:
                objeto = page.locator("textarea").nth(0)
                await objeto.wait_for(timeout=5000)
                await objeto.click()
                await objeto.fill(conteudo)
            except Exception as e:
                print(f"  ERRO objeto: {e}")

            try:
                metodologia = page.locator("textarea").nth(1)
                await metodologia.wait_for(timeout=5000)
                await metodologia.click()
                await metodologia.fill(METODOLOGIA)
            except Exception as e:
                print(f"  ERRO metodologia: {e}")

            try:
                salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar')").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(2500)
            except Exception as e:
                print(f"  ERRO ao salvar: {e}")
                await page.go_back()
                await page.wait_for_timeout(2000)
                continue

            try:
                btn_verde = page.locator("a.btn-success, button.btn-success").last
                await btn_verde.wait_for(timeout=5000)
                await btn_verde.click()
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  ERRO frequencia: {e}")

            try:
                confirmar = page.locator("button:has-text('CONFIRMAR'), button:has-text('Confirmar')").first
                await confirmar.wait_for(timeout=5000)
                await confirmar.click()
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"  ERRO confirmar: {e}")

            aula_num += 1
            print(f"  OK")

            if "Aulas" not in page.url:
                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)

        print(f"\n{'=' * 55}")
        print(f"  CONCLUIDO! Total de aulas preenchidas: {aula_num}")
        print(f"{'=' * 55}")
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
