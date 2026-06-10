"""
Preenchimento automático do Diário de Classe - TOTVS RM (Portal do Professor)
Uso: python preencher_diario.py

Requisitos:
    pip install playwright
    playwright install chromium
"""

import asyncio
from playwright.async_api import async_playwright

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────

# URL da página do plano de aula (cole a URL completa do portal)
URL_PORTAL = "https://portalprdsalesianos.rm.cloudtotvs.com.br/FrameHTML/web/app/edu/PortalDoProfessor/#/portal/class/lessonPlan/3/627237"

# Se quiser começar de uma aula específica (1 = primeira aula da tabela)
AULA_INICIO = 1

# Conteúdos por aula. Cada 2 aulas (dupla) usa o mesmo conteúdo.
# Índice 0 → aulas 1 e 2, Índice 1 → aulas 3 e 4, etc.
ASSUNTOS = [
    "Intro trigonometria: arcos, raio, diametro, grau e radiano. Conversao grau-radiano. Comprimento de arco.",
    "Matrizes: conceito, definicao, representacao aij. Linhas, colunas e tipos especiais (linha, coluna, quadrada, nula, diagonal, identidade).",
    "Ciclo Trigonometrico: construcao, orientacao, quadrantes. Arcos congruos e expressao geral.",
    "Operacoes com Matrizes: igualdade, adicao, subtracao. Multiplicacao por escalar. Intro multiplicacao entre matrizes.",
    "Seno e cosseno no ciclo. Variacao de sinal nos quadrantes. Valores notaveis (0,90,180,270,360). Reducao ao 1o quadrante.",
    "Multiplicacao de matrizes (linha x coluna). Transposta e inversa. Determinantes de ordem 2.",
    "Tangente no ciclo. Eixo das tangentes. Sinais por quadrante. Relacao fundamental da trigonometria.",
    "Determinantes ordem 3: Regra de Sarrus. Propriedades. Intro Sistemas Lineares: equacao linear, solucao e forma matricial.",
    "Classificacao de Sistemas (SPD, SPI, SI). Regra de Cramer para sistemas 2x2 e 3x3.",
    "Funcoes Trigonometricas. Funcao Seno: grafico (senoide), dominio, imagem, periodo. Parametros de amplitude e periodo.",
    "Escalonamento de Sistemas Lineares (Gauss). Matriz escalonada. Operacoes elementares. Resolucao e problemas contextualizados.",
    "Funcao Cosseno: grafico (cossenoide), dominio, imagem, periodo. Amplitude, deslocamento vertical/horizontal.",
    "Polinomios: conceito, monomio, grau, polinomio nulo. Operacoes: adicao, subtracao, multiplicacao.",
    "Funcao Tangente: tangentoide, dominio restrito, assintotas, periodicidade. Equacoes trigonometricas basicas.",
    "Divisao de Polinomios (chave). Teorema do Resto e D Alembert. Aplicacoes em divisibilidade.",
    "Divisao por (x-a): Briot-Ruffini. Equacoes polinomiais: raizes e Teorema Fundamental da Algebra.",
    "Adicao e subtracao de arcos: formulas de seno, cosseno e tangente. Arco duplo: sen(2x), cos(2x), tg(2x).",
    "Multiplicidade de raiz. Decomposicao em fatores de 1o grau. Relacoes de Girard para equacoes de 2a e 3a ordem.",
    "Inequacoes trigonometricas: resolucao geometrica no ciclo para sen x > k e cos x < k. Modelagem com funcoes trigonometricas.",
    "Revisao Frente B: arcos congruos, funcoes trigonometricas e equacoes/inequacoes trigonometricas.",
    "Pesquisa de raizes racionais. Teorema das raizes racionais e aplicacoes.",
    "Fechamento de trigonometria. Avaliacao e correcao de exercicios.",
    "Transicao: Intro geometria plana. Poligonos, classificacao, diagonais. Soma dos angulos internos.",
    "Calculo de areas de triangulos: formula de Heron e uso do seno. Relacoes metricas no triangulo retangulo.",
    "Plantao de duvidas pre-avaliacao. Revisao geral dos conteudos do bimestre.",
    "Area de figuras circulares: circulo, setor circular e coroa circular.",
    "Intro Geometria Espacial: ponto, reta e plano no espaco. Posicoes relativas.",
    "Poliedros: conceito, arestas, faces, vertices. Relacao de Euler (Frente C).",
    "Aplicacao de avaliacoes bimestrais.",
    "Poliedros. Prismas e piramides: definicao, classificacao e elementos.",
    "Equacoes trigonometricas no ciclo. Determinacao do conjunto solucao geral.",
    "Intro Prismas. Definicao, tipos (reto, obliquo), planificacao e area lateral/total.",
    "Aplicacoes da Trigonometria na Fisica: MHS, ondas sonoras e luz.",
    "Paralelepipedo retangulo: area total, diagonal e volume.",
    "Revisao geral Trigonometria e Geometria Espacial. Preparacao para avaliacao final.",
]

# ─────────────────────────────────────────────────────────────


def assunto_da_aula(numero_aula: int) -> str:
    """Retorna o conteúdo para a aula. Duplas de aulas compartilham o mesmo conteúdo."""
    idx = (numero_aula - 1) // 2
    if idx < len(ASSUNTOS):
        return ASSUNTOS[idx]
    return "Conteudo nao definido"


async def preencher_diario():
    async with async_playwright() as pw:
        # Abre o Chrome visível para você poder fazer login
        browser = await pw.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("=" * 60)
        print("Abrindo o portal TOTVS...")
        print("Faça o LOGIN normalmente no navegador.")
        print("Depois que a página de plano de aula carregar,")
        print("pressione ENTER aqui para continuar.")
        print("=" * 60)

        await page.goto(URL_PORTAL)
        input("\n>>> Pressione ENTER após fazer login e a tabela de aulas aparecer: ")

        # Descobre quantas linhas de aula existem na tabela
        await page.wait_for_timeout(2000)

        # Conta as linhas da tabela (tr dentro do tbody)
        total_linhas = await page.evaluate("""
            () => {
                const rows = document.querySelectorAll('table tbody tr, po-table tbody tr');
                return rows.length;
            }
        """)
        print(f"\nLinhas encontradas na tabela: {total_linhas}")

        if total_linhas == 0:
            print("ERRO: Nenhuma linha encontrada. Verifique se a tabela carregou.")
            print("Tente inspecionar a página e identificar o seletor correto.")
            await browser.close()
            return

        # Itera sobre cada aula
        for numero_aula in range(AULA_INICIO, total_linhas + 1):
            conteudo = assunto_da_aula(numero_aula)
            print(f"\n[Aula {numero_aula}/{total_linhas}] → {conteudo[:60]}...")

            try:
                await _preencher_aula(page, numero_aula, conteudo)
                print(f"  ✓ Aula {numero_aula} salva.")
            except Exception as e:
                print(f"  ✗ ERRO na aula {numero_aula}: {e}")
                resposta = input("  Continuar mesmo assim? (s/n): ").strip().lower()
                if resposta != "s":
                    break

        print("\n✅ Preenchimento concluído!")
        input("Pressione ENTER para fechar o navegador...")
        await browser.close()


async def _preencher_aula(page, numero_aula: int, conteudo: str):
    """Clica em Editar da aula N, preenche o conteúdo e salva."""

    # ── PASSO 1: Acha o botão/link Editar da linha correta ──
    # Estratégia: pega todos os elementos clicáveis de "Editar" e clica no N-ésimo
    btn = page.locator("text=Editar").nth(numero_aula - 1)

    # Alternativa: busca dentro da linha que contenha o número da aula
    # Se a linha tiver o número da aula numa célula, tente:
    # btn = page.locator(f"tr:has(td:text-is('{numero_aula}')) >> text=Editar")

    await btn.wait_for(timeout=10000)
    await btn.scroll_into_view_if_needed()
    await btn.click()

    # ── PASSO 2: Aguarda o modal abrir ──
    await page.wait_for_timeout(1500)

    # ── PASSO 3: Localiza o textarea de "Conteúdo realizado" ──
    # Tenta pelo label primeiro
    textarea = page.locator("label:has-text('Conteúdo realizado') + textarea, "
                            "label:has-text('Conteudo realizado') + textarea, "
                            "label:has-text('Conteúdo') ~ textarea").first

    fallback = page.locator("po-modal textarea, dialog textarea, [role='dialog'] textarea").first

    try:
        await textarea.wait_for(timeout=5000)
        alvo = textarea
    except Exception:
        await fallback.wait_for(timeout=5000)
        alvo = fallback

    # ── PASSO 4: Limpa e preenche ──
    await alvo.click()
    await alvo.select_all()
    await alvo.fill(conteudo)

    # Dispara evento input/change para o Angular detectar a mudança
    await alvo.dispatch_event("input")
    await alvo.dispatch_event("change")

    await page.wait_for_timeout(500)

    # ── PASSO 5: Clica em Salvar ──
    salvar = page.locator("po-modal button:has-text('Salvar'), "
                          "dialog button:has-text('Salvar'), "
                          "[role='dialog'] button:has-text('Salvar')").first
    await salvar.wait_for(timeout=5000)
    await salvar.click()

    # Aguarda modal fechar
    await page.wait_for_timeout(2000)


if __name__ == "__main__":
    asyncio.run(preencher_diario())
