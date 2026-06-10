import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://app12.activesoft.com.br/sistema/entrar.asp?p=FUTUROFELIZ"
LOGIN = "78962633515"
SENHA = "Luth1801@"

AULAS = [
    ("08/04/2026", "Funcao do 1 grau: conceito, coeficientes e dominio."),
    ("08/04/2026", "Grafico da funcao do 1 grau: construcao e interpretacao."),
    ("08/04/2026", "Funcao crescente e decrescente. Zeros da funcao."),
    ("10/04/2026", "Exercicios sobre funcao do 1 grau."),
    ("15/04/2026", "Aplicacoes da funcao do 1 grau em problemas contextualizados."),
    ("15/04/2026", "Revisao de funcao do 1 grau."),
    ("15/04/2026", "Funcao do 2 grau: conceito, coeficientes e dominio."),
    ("17/04/2026", "Raizes da funcao do 2 grau: formula de Bhaskara."),
    ("22/04/2026", "Vertice da parabola: calculo e interpretacao."),
    ("22/04/2026", "Grafico da funcao do 2 grau: parabola."),
    ("22/04/2026", "Concavidade e ponto de maximo e minimo."),
    ("24/04/2026", "Exercicios sobre funcao do 2 grau."),
    ("29/04/2026", "Aplicacoes da funcao do 2 grau em problemas contextualizados."),
    ("29/04/2026", "Revisao de funcoes do 1 e 2 grau."),
    ("29/04/2026", "Porcentagem: conceito e calculo basico."),
    ("06/05/2026", "Aumentos e descontos percentuais."),
    ("06/05/2026", "Juros simples: conceito e formula."),
    ("06/05/2026", "Juros compostos: conceito e aplicacao."),
    ("08/05/2026", "Exercicios sobre porcentagem e juros."),
    ("13/05/2026", "Escala: conceito e tipos (natural, reduzida, ampliada)."),
    ("13/05/2026", "Calculo com escalas em mapas e plantas."),
    ("13/05/2026", "Exercicios sobre escala."),
    ("15/05/2026", "Aplicacoes praticas de escala."),
    ("20/05/2026", "Prismas: definicao, classificacao e elementos."),
    ("20/05/2026", "Area lateral e total de prismas."),
    ("20/05/2026", "Volume de prismas."),
    ("22/05/2026", "Prismas especiais: cubo e paralelepipedo. Exercicios."),
    ("27/05/2026", "Aplicacoes de prismas em problemas contextualizados."),
    ("27/05/2026", "Piramides: definicao, classificacao e elementos."),
    ("27/05/2026", "Area lateral e total de piramides."),
    ("29/05/2026", "Volume de piramides."),
    ("05/06/2026", "Tronco de piramide: area e volume."),
    ("10/06/2026", "Exercicios sobre piramides."),
    ("10/06/2026", "Revisao geral do bimestre."),
    ("10/06/2026", "Exercicios de revisao para avaliacao."),
    ("12/06/2026", "Avaliacao bimestral e fechamento."),
]


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=400)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print("=" * 55)
        print("  PREENCHIMENTO AUTOMATICO DO DIARIO DE CLASSE")
        print("  Colegio Futuro Feliz - 3 ano EM - Matematica")
        print("  2 Bimestre 2026")
        print(f"  Total de aulas: {len(AULAS)}")
        print("=" * 55)

        print("\nFazendo login...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)
        await page.fill("input[name='login'], input[type='text']", LOGIN)
        await page.fill("input[name='senha'], input[type='password']", SENHA)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(3000)
        print("Login feito!")

        print("\n" + "=" * 55)
        print("Navegue ate: Diario > 2 Bimestre > Registro de aulas")
        print("Quando ver a tela com campos Data e Conteudo,")
        print("volte aqui e pressione ENTER.")
        print("=" * 55)
        input("\n>>> ENTER quando estiver na tela de registro: ")

        await page.wait_for_timeout(2000)

        print("\nProcurando campos...")
        frame_diario = None
        for frame in page.frames:
            try:
                if await frame.locator("td input[type='text']").count() > 0:
                    frame_diario = frame
                    print(f"  Encontrado: {frame.url}")
                    break
            except Exception:
                pass

        if not frame_diario:
            print("\nERRO: campos nao encontrados.")
            input("ENTER para fechar...")
            await browser.close()
            return

        print("\nIniciando preenchimento...\n")
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
