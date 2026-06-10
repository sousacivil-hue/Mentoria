import asyncio
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

        while True:
            await page.wait_for_timeout(1000)

            linhas = page.locator("tr:has-text('para registrar')")
            total_linhas = await linhas.count()

            # Pega a primeira linha com coluna Objeto vazia
            linha_alvo = None
            serie_texto = ""
            for i in range(total_linhas):
                ln = linhas.nth(i)
                try:
                    obj_texto = await ln.locator("td").nth(2).inner_text()
                    if obj_texto.strip() == "":
                        linha_alvo = ln
                        serie_texto = await ln.locator("td").nth(3).inner_text()
                        break
                except Exception:
                    pass

            if linha_alvo is None:
                log("Todas as aulas preenchidas!")
                break

            conteudo = get_conteudo(serie_texto)
            log(f"Aula {aula_num + 1}: {serie_texto.strip()[:50]} -> {conteudo[:40]}...")

            # Clica no botao azul
            # Loga todos os links da linha para debug
            todos = linha_alvo.locator("a, button")
            qtd = await todos.count()
            log(f"  Links na linha: {qtd}")
            for idx in range(qtd):
                el = todos.nth(idx)
                try:
                    href = await el.get_attribute("href") or ""
                    cls = await el.get_attribute("class") or ""
                    txt = (await el.inner_text()).strip()
                    log(f"    [{idx}] class='{cls}' href='{href[:60]}' txt='{txt[:30]}'")
                except Exception:
                    pass

            # Clica no botao btn-primary (usa JS, href pode ser vazio)
            try:
                btn = linha_alvo.locator("a.btn-primary").first
                await btn.click(force=True)
                await page.wait_for_timeout(3000)
                log("  Botao clicado")
            except Exception as e:
                log(f"  ERRO ao clicar: {e}")
                break

            log(f"  URL: {page.url}")

            # Preenche Objeto de Conhecimento (textarea 0)
            try:
                objeto = page.locator("textarea").nth(0)
                await objeto.wait_for(timeout=6000)
                await objeto.triple_click()
                await objeto.fill(conteudo)
                log("  Objeto preenchido")
            except Exception as e:
                log(f"  ERRO objeto: {e}")

            # Preenche Metodologia (textarea 1)
            try:
                met = page.locator("textarea").nth(1)
                await met.wait_for(timeout=3000)
                await met.click()
                await met.fill(METODOLOGIA)
                log("  Metodologia preenchida")
            except Exception as e:
                log(f"  ERRO metodologia: {e}")

            # Salva
            try:
                salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar'), input[value='SALVAR'], input[value='Salvar']").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(3000)
                log(f"  URL pos salvar: {page.url}")
            except Exception as e:
                log(f"  ERRO ao salvar: {e}")
                await page.go_back()
                await page.wait_for_timeout(2000)
                continue

            # Confirma chamada se abrir
            try:
                confirmar = page.locator("button:has-text('Confirmar'), button:has-text('CONFIRMAR'), input[value='Confirmar'], input[value='CONFIRMAR']").first
                await confirmar.wait_for(timeout=5000)
                await confirmar.click()
                await page.wait_for_timeout(3000)
                log("  Chamada confirmada")
            except Exception:
                pass

            aula_num += 1
            log(f"  OK")

            if "Aulas" not in page.url:
                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)

        log(f"\n{'=' * 55}")
        log(f"  CONCLUIDO! Total de aulas preenchidas: {aula_num}")
        log(f"{'=' * 55}")
        LOG_FILE.close()
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
