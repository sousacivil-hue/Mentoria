import asyncio
import re
from playwright.async_api import async_playwright

LOG_FILE = open("erro_siae.txt", "w", encoding="utf-8")


def log(msg):
    print(msg)
    LOG_FILE.write(msg + "\n")
    LOG_FILE.flush()


URL_LOGIN = "https://sso.seduc.se.gov.br/sistemas"
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
LOGIN = "789.626.335-15"
SENHA = "130224"
METODOLOGIA = "Aula expositiva dialogada com apresentacao do conteudo no quadro, resolucao de exercicios e participacao ativa dos alunos."

CONTEUDOS = {
    # 6 ANO — Criterios de divisibilidade e temas relacionados
    "6º": [
        "Criterios de divisibilidade por 2: numeros pares e impares.",
        "Criterios de divisibilidade por 3: soma dos algarismos.",
        "Criterios de divisibilidade por 4: analise dos dois ultimos algarismos.",
        "Criterios de divisibilidade por 5: algarismo das unidades.",
        "Criterios de divisibilidade por 6: combinacao dos criterios de 2 e 3.",
        "Criterios de divisibilidade por 9: soma dos algarismos.",
        "Criterios de divisibilidade por 10: algarismo das unidades.",
        "Revisao dos criterios de divisibilidade: exercicios de fixacao.",
        "Numeros primos: conceito e identificacao.",
        "Numeros compostos: decomposicao em fatores primos.",
        "Maximo divisor comum (MDC): conceito e calculo.",
        "Minimo multiplo comum (MMC): conceito e calculo.",
        "Aplicacoes de MDC e MMC em problemas do cotidiano.",
        "Multiplos e divisores: revisao e exercicios.",
        "Exercicios de aplicacao: divisibilidade em situacoes praticas.",
        "Resolucao de problemas com criterios de divisibilidade.",
        "Atividade avaliativa: criterios de divisibilidade e fatoracao.",
        "Correcao da atividade e revisao dos conteudos.",
        "Exercicios diversificados: MDC, MMC e divisibilidade.",
        "Problemas desafio envolvendo divisibilidade e numeros primos.",
        "Revisao geral: numeros naturais e criterios de divisibilidade.",
        "Exercicios de preparacao para avaliacao.",
        "Avaliacao bimestral.",
        "Correcao da avaliacao e discussao dos erros.",
        "Atividade de recuperacao e reforco.",
    ],

    # 7 ANO — Porcentagem com variacao de topicos
    "7º": [
        "Porcentagem: conceito e representacao.",
        "Calculo de porcentagem: metodo da regra de tres.",
        "Calculo de porcentagem: metodo do valor unitario.",
        "Exercicios de fixacao: calculo de porcentagem.",
        "Aumento percentual: conceito e calculo.",
        "Desconto percentual: conceito e calculo.",
        "Problemas com aumento e desconto percentual.",
        "Porcentagem em situacoes do cotidiano: salarios e precos.",
        "Exercicios de aplicacao: porcentagem no dia a dia.",
        "Calculo do valor original apos aumento ou desconto.",
        "Porcentagem acumulada: aumentos e descontos sucessivos.",
        "Exercicios desafio: porcentagem em situacoes reais.",
        "Revisao de porcentagem: resolucao de problemas variados.",
        "Proporcionalidade e porcentagem: conexoes.",
        "Exercicios de fixacao: porcentagem e proporcao.",
        "Porcentagem aplicada a graficos e tabelas.",
        "Leitura e interpretacao de dados percentuais.",
        "Atividade pratica: pesquisa e calculo de porcentagens reais.",
        "Revisao geral de porcentagem.",
        "Exercicios de preparacao para avaliacao.",
        "Avaliacao bimestral.",
        "Correcao da avaliacao e revisao dos erros.",
        "Atividade de reforco: porcentagem e proporcionalidade.",
        "Exercicios complementares de porcentagem.",
        "Atividade de recuperacao.",
    ],

    # 1 SERIE EM — Funcoes, geometria analitica e trigonometria
    "1ª Série": [
        "Conjuntos: conceito, representacao e operacoes.",
        "Relacoes e funcoes: conceito e notacao.",
        "Funcao do 1 grau: definicao e grafico.",
        "Funcao do 1 grau: coeficientes e interpretacao.",
        "Exercicios: funcao do 1 grau em situacoes praticas.",
        "Funcao do 2 grau: definicao e representacao grafica.",
        "Funcao do 2 grau: vertice, zeros e concavidade.",
        "Problemas com funcao do 2 grau.",
        "Funcao modular: conceito e grafico.",
        "Exercicios de fixacao: funcoes.",
        "Progressao aritmetica: definicao e razao.",
        "Progressao aritmetica: termo geral e soma.",
        "Progressao geometrica: definicao e razao.",
        "Progressao geometrica: termo geral e soma.",
        "Exercicios: PA e PG aplicadas.",
        "Trigonometria: seno, cosseno e tangente no triangulo retangulo.",
        "Relacoes trigonometricas: exercicios de aplicacao.",
        "Trigonometria: angulos notaveis 30, 45 e 60 graus.",
        "Lei dos senos e lei dos cossenos.",
        "Exercicios de trigonometria.",
        "Revisao de funcoes e progressoes.",
        "Revisao de trigonometria.",
        "Exercicios de preparacao para avaliacao.",
        "Avaliacao bimestral.",
        "Atividade de recuperacao e reforco.",
    ],

    # 2 SERIE EM — Logaritmos, geometria e probabilidade
    "2ª Série": [
        "Funcao exponencial: definicao e grafico.",
        "Equacoes exponenciais: resolucao.",
        "Logaritmo: definicao e propriedades basicas.",
        "Propriedades dos logaritmos: produto, quociente e potencia.",
        "Equacoes logaritmicas: resolucao.",
        "Funcao logaritmica: grafico e aplicacoes.",
        "Exercicios: funcao exponencial e logaritmica.",
        "Geometria plana: revisao de areas e perimetros.",
        "Circunferencia e circulo: arcos, cordas e angulos.",
        "Geometria espacial: prismas e piramides.",
        "Geometria espacial: cilindro, cone e esfera.",
        "Volume e area de solidos geometricos.",
        "Exercicios de geometria espacial.",
        "Analise combinatoria: principio fundamental da contagem.",
        "Arranjos e permutacoes.",
        "Combinacoes: conceito e calculo.",
        "Exercicios de analise combinatoria.",
        "Probabilidade: conceito e calculo.",
        "Probabilidade de eventos compostos.",
        "Exercicios de probabilidade em situacoes reais.",
        "Estatistica: media, moda e mediana.",
        "Estatistica: desvio padrao e variancia.",
        "Revisao geral de logaritmos e geometria.",
        "Exercicios de preparacao para avaliacao.",
        "Atividade de recuperacao e reforco.",
    ],

    # 3 SERIE — Razao, proporcao, mat financeira e outros topicos do EM
    "3ª": [
        "Razao e proporcao: revisao e conceitos fundamentais.",
        "Proporcao: propriedade fundamental e aplicacoes.",
        "Grandezas diretamente proporcionais: identificacao e calculo.",
        "Grandezas inversamente proporcionais: identificacao e calculo.",
        "Regra de tres simples: direta e inversa.",
        "Regra de tres composta: problemas com multiplas variaveis.",
        "Exercicios de aplicacao: razao e proporcao no cotidiano.",
        "Matematica Financeira: porcentagem e juros no contexto economico.",
        "Matematica Financeira: juros simples — formula e aplicacao.",
        "Matematica Financeira: juros compostos — conceito e formula.",
        "Matematica Financeira: comparacao entre juros simples e compostos.",
        "Matematica Financeira: montante, capital e taxa.",
        "Educacao Financeira: planejamento e orcamento pessoal.",
        "Educacao Financeira: credito, dividas e consumo consciente.",
        "Educacao Financeira: investimentos basicos — poupanca e fundos.",
        "Educacao Financeira: impostos e tributos na vida do cidadao.",
        "Matematica e o Mundo Digital: sistemas de numeracao binario e decimal.",
        "Matematica e o Mundo Digital: logica booleana e operacoes digitais.",
        "Matematica e o Mundo Digital: algoritmos e raciocinio logico.",
        "Matematica e o Mundo Digital: graficos, dados e interpretacao digital.",
        "Expressao Matematica: variaveis, constantes e expressoes algebricas.",
        "Expressao Matematica: valor numerico de expressoes algebricas.",
        "Expressao Matematica: operacoes com polinomios.",
        "Revisao geral e exercicios de preparacao para o ENEM.",
        "Atividade de recuperacao e reforco final.",
    ],

    # EJA — Matematica basica para jovens e adultos
    "(EJA)": [
        "Numeros naturais: leitura, escrita e comparacao.",
        "Operacoes basicas: adicao e subtracao.",
        "Operacoes basicas: multiplicacao e divisao.",
        "Resolucao de problemas com as quatro operacoes.",
        "Frações: conceito e representacao no dia a dia.",
        "Frações equivalentes e simplificacao.",
        "Operacoes com fracoes: adicao e subtracao.",
        "Numeros decimais: leitura e escrita.",
        "Operacoes com decimais: adicao e subtracao.",
        "Porcentagem: conceito e calculo basico.",
        "Porcentagem aplicada: descontos, salarios e precos.",
        "Medicoes: comprimento, massa e capacidade.",
        "Conversao de unidades de medida.",
        "Geometria basica: figuras planas e seus elementos.",
        "Perimetro e area de figuras simples.",
        "Resolucao de problemas do cotidiano com matematica.",
        "Proporcionalidade: razao e proporcao basica.",
        "Regra de tres simples em situacoes praticas.",
        "Leitura de graficos e tabelas.",
        "Matematica Financeira basica: juros e compras a prazo.",
        "Educacao Financeira: controle de gastos e renda.",
        "Revisao geral: operacoes e frações.",
        "Revisao geral: medidas e geometria.",
        "Exercicios de preparacao para avaliacao.",
        "Atividade de recuperacao e reforco.",
    ],
}

_indices: dict = {}


def get_conteudo(serie: str) -> str:
    for chave, lista in CONTEUDOS.items():
        if chave in serie:
            i = _indices.get(chave, 0)
            conteudo = lista[i % len(lista)]
            _indices[chave] = i + 1
            return conteudo
    return "Conteudo nao definido"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        log("=" * 55)
        log("  PREENCHIMENTO AUTOMATICO - SIAE SEDUC-SE")
        log("=" * 55)

        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)
        try:
            await page.fill("input[name='username'], input[type='text'], input[name='login']", LOGIN)
            await page.fill("input[name='password'], input[type='password'], input[name='senha']", SENHA)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(4000)
        except Exception:
            pass

        log("\n" + "=" * 55)
        log("Se nao fez login automaticamente, faca manualmente.")
        log("Depois navegue ate a tela de AULAS do SIAE.")
        log("Quando ver a lista de aulas, pressione ENTER aqui.")
        log("=" * 55)
        input("\n>>> ENTER quando estiver na tela de aulas: ")

        await page.wait_for_timeout(2000)

        if "Aula" not in page.url:
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(3000)

        log("\nIniciando preenchimento...\n")
        aula_num = 0

        async def selecionar_solicitadas():
            try:
                # Tenta clicar pelo texto do label
                radio = page.locator("label:has-text('Solicitada') input[type=radio], input[type=radio][value*='olicita']")
                if await radio.count() > 0:
                    await radio.first.click(force=True)
                    await page.wait_for_timeout(1500)
                    log("  Aba Solicitadas selecionada")
                    return
                # Fallback: clica em qualquer radio que nao seja o primeiro (Regulares)
                radios = page.locator("input[type=radio]")
                count = await radios.count()
                if count >= 2:
                    await radios.nth(1).click(force=True)
                    await page.wait_for_timeout(1500)
                    log("  Aba Solicitadas selecionada (fallback)")
            except Exception as e:
                log(f"  AVISO: nao selecionou Solicitadas: {e}")

        await selecionar_solicitadas()

        while True:
            await page.wait_for_timeout(1000)

            botoes_info = await page.evaluate("""
                () => {
                    const result = [];
                    const btns = document.querySelectorAll('button.btn-primary[onclick^="registrar"]');
                    for (const btn of btns) {
                        const tr = btn.closest('tr');
                        if (!tr) continue;
                        const tds = tr.querySelectorAll('td');
                        const situacao = tds[7] ? tds[7].innerText.trim() : '';
                        const objeto = tds[2] ? tds[2].innerText.trim() : '';
                        const serie = tds[3] ? tds[3].innerText.trim() : '';
                        const onclick = btn.getAttribute('onclick') || '';
                        if (situacao.includes('para registrar') && (objeto === '' || objeto === '-')) {
                            result.push({onclick, serie, situacao});
                        }
                    }
                    return result;
                }
            """)

            if not botoes_info:
                log("Todas as aulas preenchidas!")
                break

            alvo = botoes_info[0]
            onclick = alvo["onclick"]
            serie_texto = alvo["serie"]

            match = re.search(r"registrar\((\d+)\)", onclick)
            if not match:
                log("  ERRO: ID nao encontrado")
                break
            aula_id = match.group(1)

            conteudo = get_conteudo(serie_texto)
            log(f"Aula {aula_num + 1}: {serie_texto[:50]}")
            log(f"  ID: {aula_id} | conteudo: {conteudo[:50]}")

            # Navega para a pagina de registro (registrar() faz location.href)
            url_reg = f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}"
            await page.goto(url_reg)
            await page.wait_for_timeout(3000)
            log(f"  URL: {page.url}")

            # Preenche Objeto de Conhecimento
            try:
                objeto = page.locator("textarea").nth(0)
                await objeto.wait_for(timeout=6000)
                await objeto.click(click_count=3)
                await objeto.fill(conteudo)
                log("  Objeto preenchido")
            except Exception as e:
                log(f"  ERRO objeto: {e}")

            # Preenche Metodologia
            # Metodologia: tenta textarea, depois input text
            met_ok = False
            for sel in ["textarea:nth-of-type(2)", "input[type='text']", "input[type='text']:not([readonly])"]:
                try:
                    locs = page.locator(sel)
                    c = await locs.count()
                    if c > 0:
                        await locs.first.click()
                        await locs.first.fill(METODOLOGIA)
                        log(f"  Metodologia preenchida ({sel})")
                        met_ok = True
                        break
                except Exception:
                    pass
            if not met_ok:
                log("  Metodologia nao preenchida (campo nao encontrado)")

            # Salva
            try:
                salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar'), input[value='SALVAR'], input[value='Salvar']").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(3000)
                log(f"  Salvo! URL pos salvar: {page.url}")
            except Exception as e:
                log(f"  ERRO ao salvar: {e}")
                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)
                continue

            aula_num += 1
            log(f"  OK")

            # Volta para lista e seleciona aba Solicitadas
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(2000)
            await selecionar_solicitadas()
            try:
                btn_verde = await page.evaluate(f"""
                    () => {{
                        const btns = document.querySelectorAll('button.btn-success[onclick], a.btn-success[onclick]');
                        for (const btn of btns) {{
                            const tr = btn.closest('tr');
                            if (tr) {{
                                const onclick = btn.getAttribute('onclick') || '';
                                if (onclick.includes('{aula_id}')) return onclick;
                            }}
                        }}
                        return null;
                    }}
                """)
                if btn_verde:
                    log(f"  Botao verde onclick: {btn_verde}")
                    match_verde = re.search(r"\((\d+)\)", btn_verde)
                    if match_verde:
                        freq_id = match_verde.group(1)
                        await page.evaluate(f"({btn_verde.split('(')[0]})({freq_id})")
                        await page.wait_for_timeout(3000)
                        confirmar = page.locator("button:has-text('Confirmar'), button:has-text('CONFIRMAR'), input[value='Confirmar']").first
                        await confirmar.wait_for(timeout=5000)
                        await confirmar.click()
                        await page.wait_for_timeout(2000)
                        log("  Frequencia confirmada")
                        await page.goto(URL_AULAS)
                        await page.wait_for_timeout(2000)
                        await selecionar_solicitadas()
            except Exception as e:
                log(f"  ERRO frequencia: {e}")

        log(f"\n{'=' * 55}")
        log(f"  CONCLUIDO! Total de aulas preenchidas: {aula_num}")
        log(f"{'=' * 55}")
        LOG_FILE.close()
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
