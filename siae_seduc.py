import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://sso.seduc.se.gov.br/sistemas"
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
LOGIN = "789.626.335-15"
SENHA = "789.626.335-15"
METODOLOGIA = "Aula expositiva com resolucao de exercicios no quadro e atividade individual."

# Conteudo por turma (busca pelo texto da serie na tabela)
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

        print("\nAbrindo pagina de login...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)

        print("Fazendo login...")
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
            print("Navegando para a tela de aulas...")
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(3000)

        print("\nIniciando preenchimento...\n")
        aula_num = 0

        while True:
            await page.wait_for_timeout(1000)

            # Pega todos os botoes de registrar aula
            botoes = page.locator("a[href*='Registrar'], button:has-text('Registrar'), a.btn-primary, td a.btn")
            total_botoes = await botoes.count()

            # Busca linhas com status "para registrar"
            linhas = page.locator("tr:has-text('para registrar')")
            total_linhas = await linhas.count()

            if total_linhas == 0:
                print("Nenhuma aula pendente encontrada. Verificando botoes...")
                # Tenta achar qualquer botao azul na tabela
                botoes_azuis = page.locator("table a.btn, table button")
                total_botoes = await botoes_azuis.count()
                if total_botoes == 0:
                    print("Todas as aulas preenchidas!")
                    break
                btn = botoes_azuis.first
            else:
                # Pega a primeira linha pendente
                linha = linhas.first
                serie_texto = await linha.locator("td").nth(3).inner_text()
                conteudo = get_conteudo(serie_texto)
                print(f"Aula {aula_num + 1}: {serie_texto.strip()[:50]} -> {conteudo[:40]}...")
                btn = linha.locator("a, button").last

            await btn.scroll_into_view_if_needed()
            await btn.click()
            await page.wait_for_timeout(2000)

            # Preenche Objeto de Conhecimento
            try:
                serie_pagina = await page.locator("text=6 Ano, text=7 Ano, text=3").first.inner_text()
            except Exception:
                serie_pagina = ""

            # Tenta pegar a serie do titulo da pagina
            try:
                turma_texto = await page.locator("text=Ano, text=Serie, text=série").first.inner_text()
                conteudo = get_conteudo(turma_texto)
            except Exception:
                pass

            try:
                objeto = page.locator("textarea").first
                await objeto.wait_for(timeout=5000)
                await objeto.click()
                await objeto.fill(conteudo)
            except Exception as e:
                print(f"  ERRO no objeto de conhecimento: {e}")

            # Preenche Metodologia
            try:
                textareas = page.locator("textarea")
                count = await textareas.count()
                if count >= 2:
                    metodologia_field = textareas.nth(1)
                    await metodologia_field.click()
                    await metodologia_field.fill(METODOLOGIA)
            except Exception as e:
                print(f"  ERRO na metodologia: {e}")

            # Clica em Salvar
            try:
                salvar = page.locator("button:has-text('SALVAR'), input[value='SALVAR'], button:has-text('Salvar')").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(2000)
                aula_num += 1
                print(f"  OK")
            except Exception as e:
                print(f"  ERRO ao salvar: {e}")
                await page.go_back()
                await page.wait_for_timeout(2000)

            # Verifica se voltou para a lista
            if "Aulas" not in page.url and "aula" not in page.url.lower():
                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)

        print(f"\n{'=' * 55}")
        print(f"  CONCLUIDO! Total de aulas preenchidas: {aula_num}")
        print(f"{'=' * 55}")
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
