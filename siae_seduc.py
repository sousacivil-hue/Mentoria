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

            try:
                btn_azul = linha.locator("a.btn-primary, a.btn-info, a.btn[class*='primary']").first
                await btn_azul.wait_for(timeout=3000)
            except Exception:
                btn_azul = linha.locator("a, button").last
            await btn_azul.scroll_into_view_if_needed()
            await btn_azul.click()
            await page.wait_for_timeout(3000)

            print(f"  URL: {page.url}")

            # Passo 1: se caiu na chamada, marcar todos presentes e confirmar
            try:
                btn_todos = page.locator("button:has-text('Todos Presentes'), a:has-text('Todos Presentes'), button:has-text('TODOS'), input[value*='Presentes']").first
                await btn_todos.wait_for(timeout=3000)
                await btn_todos.click()
                await page.wait_for_timeout(2000)
                print("  Chamada: marcou todos presentes")
            except Exception:
                pass

            # Confirma chamada se houver botao de confirmacao
            try:
                confirmar_chamada = page.locator("button:has-text('Confirmar'), button:has-text('CONFIRMAR'), input[value='Confirmar']").first
                await confirmar_chamada.wait_for(timeout=3000)
                await confirmar_chamada.click()
                await page.wait_for_timeout(3000)
                print("  Chamada confirmada")
            except Exception:
                pass

            print(f"  URL apos chamada: {page.url}")

            # Passo 2: preencher conteudo (objeto de conhecimento)
            campo_obj = None
            for sel in ["textarea", "input[type='text']:not([readonly])"]:
                try:
                    loc = page.locator(sel).first
                    await loc.wait_for(timeout=4000)
                    campo_obj = loc
                    print(f"  Campo conteudo: {sel}")
                    break
                except Exception:
                    pass

            if campo_obj:
                await campo_obj.click()
                await campo_obj.fill(conteudo)
            else:
                print("  ERRO: campo de conteudo nao encontrado")

            # Passo 3: preencher metodologia (segundo campo)
            try:
                textareas = page.locator("textarea")
                count = await textareas.count()
                if count >= 2:
                    await textareas.nth(1).click()
                    await textareas.nth(1).fill(METODOLOGIA)
                    print("  Metodologia preenchida")
            except Exception as e:
                print(f"  ERRO metodologia: {e}")

            # Passo 4: salvar
            try:
                salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar'), input[value='SALVAR'], input[value='Salvar']").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(3000)
                aula_num += 1
                print(f"  OK")
            except Exception as e:
                print(f"  ERRO ao salvar: {e}")
                await page.go_back()
                await page.wait_for_timeout(2000)
                continue

            if "Aulas" not in page.url:
                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)

        print(f"\n{'=' * 55}")
        print(f"  CONCLUIDO! Total de aulas preenchidas: {aula_num}")
        print(f"{'=' * 55}")
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
