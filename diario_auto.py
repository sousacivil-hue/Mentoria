import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://siga01.activesoft.com.br/login/?instituicao=COLEGIOVITA"
LOGIN = "Luth5824"
SENHA = "Luth1801@"

AULAS = [
    ("06/04/2026", "Introducao a algebra. Variaveis e constantes. Expressoes algebricas."),
    ("06/04/2026", "Valor numerico de expressoes algebricas. Exercicios de substituicao."),
    ("08/04/2026", "Monomios: conceito, coeficiente e parte literal."),
    ("10/04/2026", "Monomios semelhantes. Adicao e subtracao de monomios."),
    ("10/04/2026", "Multiplicacao de monomios."),
]


def cabecalho():
    print("=" * 55)
    print("  PREENCHIMENTO AUTOMATICO DO DIARIO DE CLASSE")
    print("  Colegio Vita - 8 ano A - Matematica")
    print("  2 Bimestre 2026")
    print("=" * 55)
    print(f"  Total de aulas a preencher: {len(AULAS)}")
    print("=" * 55)


async def main():
    cabecalho()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=400)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print("\nFazendo login automaticamente...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)
        await page.fill("input[name='login'], input[type='text']", LOGIN)
        await page.fill("input[name='senha'], input[type='password']", SENHA)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)
        print("Login feito!")

        print("\n" + "=" * 55)
        print("PROXIMOS PASSOS:")
        print("1. No navegador que abriu, va em:")
        print("   Diario > 2 Bimestre > Registro de aulas")
        print("2. Quando ver a tela com campos Data e Conteudo,")
        print("   volte aqui e pressione ENTER.")
        print("=" * 55)
        input("\n>>> ENTER quando estiver na tela de registro: ")

        await page.wait_for_timeout(2000)

        print("\nProcurando campos...")
        frame_diario = None
        for frame in page.frames:
            try:
                if await frame.locator("td input[type='text']").count() > 0:
                    frame_diario = frame
                    break
            except Exception:
                pass

        if not frame_diario:
            print("\nERRO: campos nao encontrados.")
            print("Verifique se navegou ate a tela correta.")
            input("ENTER para fechar...")
            await browser.close()
            return

        print("Iniciando preenchimento automatico...\n")
        total = len(AULAS)
        erros = 0
        for i, (data, conteudo) in enumerate(AULAS, 1):
            print(f"[{i}/{total}] {data} - {conteudo[:50]}...")
            try:
                campo_data = frame_diario.locator("td input[type='text']:not([readonly])").last
                await campo_data.wait_for(timeout=8000)
                await campo_data.click(click_count=3)
                await campo_data.fill(data)

                campo_conteudo = frame_diario.locator("textarea[name^='ConteudoMinistrado']:not([readonly])").last
                await campo_conteudo.wait_for(timeout=5000)
                await campo_conteudo.click()
                await campo_conteudo.fill(conteudo)

                await frame_diario.locator("input[value='Gravar']").last.click()
                await page.wait_for_timeout(3000)
                print(f"  OK")
            except Exception as e:
                print(f"  ERRO: {e}")
                erros += 1
                await page.wait_for_timeout(1000)

        print("\n" + "=" * 55)
        print(f"  CONCLUIDO!")
        print(f"  Aulas salvas: {total - erros}/{total}")
        if erros > 0:
            print(f"  Erros: {erros} (verifique manualmente)")
        print("=" * 55)
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
