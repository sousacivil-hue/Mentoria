import asyncio
from playwright.async_api import async_playwright

URL_LOGIN = "https://app12.activesoft.com.br/sistema/entrar.asp?p=FUTUROFELIZ"
LOGIN = "78962633515"
SENHA = "Luth1801@"

AULAS = [
    ("07/04/2026", "Introducao a estatistica. Conceitos basicos: populacao, amostra e dados."),
    ("07/04/2026", "Coleta e organizacao de dados. Tabelas de frequencia."),
    ("10/04/2026", "Graficos estatisticos: barras, setores e histograma."),
    ("10/04/2026", "Media aritmetica simples: conceito e calculo."),
    ("14/04/2026", "Media aritmetica ponderada: conceito e calculo."),
    ("14/04/2026", "Moda: conceito, calculo e interpretacao."),
    ("17/04/2026", "Mediana: conceito e calculo em rol de dados."),
    ("17/04/2026", "Mediana em tabelas de frequencia."),
    ("21/04/2026", "Comparacao entre media, moda e mediana."),
    ("21/04/2026", "Exercicios sobre medidas de tendencia central."),
    ("24/04/2026", "Medidas de dispersao: amplitude e variancia."),
    ("24/04/2026", "Desvio padrao: conceito e calculo."),
    ("28/04/2026", "Interpretacao do desvio padrao. Coeficiente de variacao."),
    ("28/04/2026", "Exercicios sobre desvio padrao e dispersao."),
    ("05/05/2026", "Revisao de estatistica. Exercicios contextualizados."),
    ("05/05/2026", "Avaliacao de estatistica."),
    ("08/05/2026", "Correcao e retomada de estatistica."),
    ("08/05/2026", "Introducao a trigonometria: revisao de seno e cosseno no triangulo retangulo."),
    ("12/05/2026", "Ciclo trigonometrico: construcao e orientacao."),
    ("12/05/2026", "Funcao seno: definicao, dominio e imagem."),
    ("15/05/2026", "Grafico da funcao seno (senoide). Periodo e amplitude."),
    ("15/05/2026", "Parametros da funcao seno: y = a sen(bx + c) + d."),
    ("19/05/2026", "Funcao cosseno: definicao, dominio e imagem."),
    ("19/05/2026", "Grafico da funcao cosseno. Periodo e amplitude."),
    ("22/05/2026", "Parametros da funcao cosseno: y = a cos(bx + c) + d."),
    ("22/05/2026", "Comparacao entre funcao seno e cosseno."),
    ("26/05/2026", "Equacoes trigonometricas basicas com seno e cosseno."),
    ("26/05/2026", "Resolucao de equacoes trigonometricas no ciclo."),
    ("29/05/2026", "Aplicacoes de funcoes trigonometricas: modelagem."),
    ("29/05/2026", "Aplicacoes em fisica: MHS e ondas."),
    ("02/06/2026", "Exercicios sobre funcoes trigonometricas."),
    ("02/06/2026", "Revisao geral: estatistica e trigonometria."),
    ("05/06/2026", "Exercicios de revisao para avaliacao."),
    ("05/06/2026", "Avaliacao bimestral."),
    ("09/06/2026", "Correcao da avaliacao."),
    ("09/06/2026", "Plantao de duvidas e recuperacao."),
    ("12/06/2026", "Atividade complementar: problemas contextualizados."),
    ("12/06/2026", "Fechamento do bimestre."),
]


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=400)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print("=" * 55)
        print("  PREENCHIMENTO AUTOMATICO DO DIARIO DE CLASSE")
        print("  Colegio Futuro Feliz - 2 ano EM - Matematica")
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
