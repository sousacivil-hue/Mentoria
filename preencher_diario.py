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
URL_PORTAL = "https://portalprdsalesianos.rm.cloudtotvs.com.br/FrameHTML/web/app/edu/PortalDoProfessor/#/portal/class/lessonPlan/3/627185?classDate=2026%2F06%2F11"

# Se quiser começar de uma aula específica (1 = primeira aula da tabela)
AULA_INICIO = 1

# Conteúdos por aula. Cada 2 aulas (dupla) usa o mesmo conteúdo.
# Índice 0 → aulas 1 e 2, Índice 1 → aulas 3 e 4, etc.
ASSUNTOS = [
    "Introducao aos estudos historicos: o que e Historia, fontes historicas e o trabalho do historiador.",
    "Tempo e periodizacao: cronologia, calendarios e divisao da Historia em periodos.",
    "Pre-Historia: origem e evolucao do ser humano. Paleolitico e Neolitico.",
    "Revolucao Neolitica: agricultura, sedentarizacao e primeiras aldeias.",
    "Povoamento da America: teorias sobre a chegada do homem ao continente americano.",
    "Primeiras civilizacoes: Mesopotamia - cidades-Estado, escrita cuneiforme e Codigo de Hamurabi.",
    "Egito Antigo: sociedade, religiao, faraos e as contribuicoes culturais.",
    "Hebreus, fenicios e persas: caracteristicas e legados dessas civilizacoes.",
    "Civilizacoes africanas antigas: Reino de Kush, Axum e a importancia da Africa na Antiguidade.",
    "Grecia Antiga: formacao das polis. Esparta e Atenas - sociedade e politica.",
    "Democracia ateniense: funcionamento, cidadania e limites da participacao.",
    "Cultura grega: filosofia, mitologia, teatro e jogos olimpicos.",
    "Periodo Helenistico: conquistas de Alexandre e difusao da cultura grega.",
    "Roma Antiga: da Monarquia a Republica - sociedade, patricios e plebeus.",
    "Expansao romana e crise da Republica: guerras punicas e reformas dos Gracos.",
    "Imperio Romano: principais imperadores, Pax Romana e cultura romana.",
    "Cristianismo: origem, perseguicao e oficializacao no Imperio Romano.",
    "Crise do Imperio Romano e invasoes germanicas: a queda de Roma.",
    "Revisao dos conteudos: da Pre-Historia a Roma Antiga. Exercicios.",
    "Avaliacao bimestral e correcao comentada.",
    "Idade Media: formacao dos reinos germanicos e o Imperio Carolingio.",
    "Feudalismo: estrutura social, economica e politica do mundo feudal.",
    "Igreja Catolica na Idade Media: poder, cultura e vida monastica.",
    "Mundo arabe e o Isla: origem, expansao e contribuicoes culturais.",
    "Imperio Bizantino: Constantinopla, Justiniano e o cisma do Oriente.",
    "Africa medieval: reinos de Gana, Mali e Songai. Comercio transaariano.",
    "Baixa Idade Media: renascimento comercial e urbano. Cruzadas.",
    "Crise do seculo XIV: peste negra, fome e revoltas camponesas.",
    "Revisao geral do bimestre e plantao de duvidas.",
    "Fechamento do bimestre: atividade avaliativa e correcao.",
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
