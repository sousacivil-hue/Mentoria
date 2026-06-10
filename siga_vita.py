import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://siga01.activesoft.com.br/login/?instituicao=COLEGIOVITA"
LOGIN = "Luth5824"
SENHA = "Luth1801@"

# CSS do link "Registro de aulas" do 2 Bimestre
CSS_LINK_DIARIO = "body > div > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(2) > td:nth-child(8) > a"

AULAS = [
    ("06/04/2026", "Introducao a algebra. Variaveis e constantes. Expressoes algebricas."),
    ("06/04/2026", "Valor numerico de expressoes algebricas. Exercicios de substituicao."),
    ("08/04/2026", "Monomios: conceito, coeficiente e parte literal."),
    ("10/04/2026", "Monomios semelhantes. Adicao e subtracao de monomios."),
    ("10/04/2026", "Multiplicacao de monomios."),
    ("13/04/2026", "Divisao de monomios."),
    ("13/04/2026", "Potenciacao e radicacao de monomios."),
    ("15/04/2026", "Revisao e exercicios sobre monomios e expressoes algebricas."),
    ("17/04/2026", "Polinomios: conceito, termos e grau."),
    ("17/04/2026", "Valor numerico de polinomios. Polinomio nulo e identico."),
    ("22/04/2026", "Adicao e subtracao de polinomios."),
    ("24/04/2026", "Multiplicacao de polinomio por monomio."),
    ("24/04/2026", "Multiplicacao de polinomio por polinomio."),
    ("27/04/2026", "Divisao de polinomio por monomio."),
    ("27/04/2026", "Divisao de polinomio por polinomio (chave)."),
    ("29/04/2026", "Revisao e exercicios sobre polinomios."),
    ("04/05/2026", "Produtos notaveis: quadrado da soma."),
    ("04/05/2026", "Quadrado da diferenca."),
    ("06/05/2026", "Produto da soma pela diferenca."),
    ("08/05/2026", "Cubo da soma e cubo da diferenca."),
    ("08/05/2026", "Fatoracao: fator comum em evidencia."),
    ("11/05/2026", "Fatoracao por agrupamento."),
    ("11/05/2026", "Fatoracao de trinomio quadrado perfeito."),
    ("13/05/2026", "Fatoracao de diferenca de quadrados."),
    ("15/05/2026", "Fatoracao: casos combinados."),
    ("15/05/2026", "Revisao e exercicios sobre operacoes com polinomios."),
    ("18/05/2026", "Equacoes com duas incognitas: conceito e solucoes."),
    ("18/05/2026", "Representacao grafica de equacoes com duas incognitas."),
    ("20/05/2026", "Par ordenado e verificacao de solucoes."),
    ("22/05/2026", "Equacoes lineares: forma padrao ax + by = c."),
    ("22/05/2026", "Construcao de tabela de valores e grafico."),
    ("25/05/2026", "Interpretacao grafica de equacoes."),
    ("25/05/2026", "Aplicacoes praticas de equacoes com duas incognitas."),
    ("27/05/2026", "Revisao e exercicios sobre equacoes com duas incognitas."),
    ("29/05/2026", "Sistemas lineares: conceito e classificacao (SPD, SPI, SI)."),
    ("29/05/2026", "Metodo da substituicao."),
    ("01/06/2026", "Metodo da substituicao: exercicios."),
    ("01/06/2026", "Metodo da adicao (eliminacao)."),
    ("05/06/2026", "Metodo da adicao: exercicios."),
    ("05/06/2026", "Metodo da comparacao."),
    ("08/06/2026", "Classificacao de sistemas pelo numero de solucoes."),
    ("08/06/2026", "Interpretacao grafica de sistemas lineares."),
    ("10/06/2026", "Problemas contextualizados com sistemas lineares."),
    ("12/06/2026", "Problemas contextualizados: exercicios."),
    ("12/06/2026", "Revisao final do bimestre. Preparacao para avaliacao."),
]


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=600)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print("Fazendo login...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)

        await page.fill("input[name='login'], input[type='text']", LOGIN)
        await page.fill("input[name='senha'], input[type='password']", SENHA)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(4000)

        print("Aguardando pagina do portal carregar...")
        print("Pressione ENTER aqui depois que a tela de bimestres aparecer.")
        input(">>> ENTER para continuar: ")

        print("Clicando em Registro de aulas do 2 Bimestre...")
        link = page.locator(CSS_LINK_DIARIO)
        await link.wait_for(timeout=15000)
        await link.click()
        await page.wait_for_timeout(3000)

        print("Pagina do diario aberta. Iniciando preenchimento...")

        total = len(AULAS)
        for i, (data, conteudo) in enumerate(AULAS, 1):
            print(f"\n[Aula {i}/{total}] {data} - {conteudo[:50]}...")
            try:
                campo_data = page.locator("td input[type='text']").last
                await campo_data.wait_for(timeout=8000)
                await campo_data.click(triple_click=True)
                await campo_data.fill(data)

                campo_conteudo = page.locator("td textarea").first
                await campo_conteudo.wait_for(timeout=5000)
                await campo_conteudo.click()
                await campo_conteudo.fill(conteudo)

                await page.click("input[value='Gravar'], button:has-text('Gravar')")
                await page.wait_for_timeout(2000)
                print(f"  OK")
            except Exception as e:
                print(f"  ERRO: {e}")
                await page.wait_for_timeout(1000)

        print("\nConcluido!")
        input("Pressione ENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
