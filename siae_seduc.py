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

            if total_linhas == 0:
                log("Todas as aulas preenchidas!")
                break

            linha = linhas.first
            serie_texto = await linha.locator("td").nth(3).inner_text()
            conteudo = get_conteudo(serie_texto)
            log(f"Aula {aula_num + 1}: {serie_texto.strip()[:50]} -> {conteudo[:40]}...")

            # Descobre todos os links/botoes na linha
            todos_links = linha.locator("a, button")
            qtd = await todos_links.count()
            log(f"  Botoes na linha: {qtd}")
            for idx in range(qtd):
                el = todos_links.nth(idx)
                try:
                    href = await el.get_attribute("href") or ""
                    txt = await el.inner_text() or ""
                    cls = await el.get_attribute("class") or ""
                    log(f"    [{idx}] txt='{txt.strip()}' href='{href[:60]}' class='{cls}'")
                except Exception:
                    pass

            # Clica no primeiro link que vai para Registrar
            btn_azul = None
            for idx in range(qtd):
                el = todos_links.nth(idx)
                try:
                    href = await el.get_attribute("href") or ""
                    cls = await el.get_attribute("class") or ""
                    if "Registrar" in href or "registrar" in href:
                        btn_azul = el
                        log(f"  Clicando botao Registrar [{idx}]")
                        break
                except Exception:
                    pass

            if not btn_azul:
                try:
                    btn_azul = linha.locator("a.btn-primary, a.btn-info").first
                    await btn_azul.wait_for(timeout=2000)
                    log("  Clicando btn-primary")
                except Exception:
                    btn_azul = todos_links.first
                    log("  Clicando primeiro link da linha")

            await btn_azul.scroll_into_view_if_needed()
            await btn_azul.click()
            await page.wait_for_timeout(3000)

            log(f"  URL: {page.url}")

            # Passo 1: se caiu na chamada, marcar todos presentes e confirmar
            try:
                btn_todos = page.locator("button:has-text('Todos Presentes'), a:has-text('Todos Presentes'), button:has-text('TODOS'), input[value*='Presentes']").first
                await btn_todos.wait_for(timeout=3000)
                await btn_todos.click()
                await page.wait_for_timeout(2000)
                log("  Chamada: marcou todos presentes")
            except Exception:
                pass

            try:
                confirmar_chamada = page.locator("button:has-text('Confirmar'), button:has-text('CONFIRMAR'), input[value='Confirmar']").first
                await confirmar_chamada.wait_for(timeout=3000)
                await confirmar_chamada.click()
                await page.wait_for_timeout(3000)
                log("  Chamada confirmada")
            except Exception:
                pass

            log(f"  URL apos chamada: {page.url}")

            # Passo 2: preencher conteudo
            campo_obj = None
            for sel in ["textarea", "input[type='text']:not([readonly])"]:
                try:
                    loc = page.locator(sel).first
                    await loc.wait_for(timeout=4000)
                    campo_obj = loc
                    log(f"  Campo conteudo: {sel}")
                    break
                except Exception:
                    pass

            if campo_obj:
                await campo_obj.click()
                await campo_obj.fill(conteudo)
            else:
                log("  ERRO: campo de conteudo nao encontrado")

            # Passo 3: metodologia
            try:
                textareas = page.locator("textarea")
                count = await textareas.count()
                if count >= 2:
                    await textareas.nth(1).click()
                    await textareas.nth(1).fill(METODOLOGIA)
                    log("  Metodologia preenchida")
            except Exception as e:
                log(f"  ERRO metodologia: {e}")

            # Passo 4: salvar
            try:
                salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar'), input[value='SALVAR'], input[value='Salvar']").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(3000)
                aula_num += 1
                log(f"  OK")
            except Exception as e:
                log(f"  ERRO ao salvar: {e}")
                await page.go_back()
                await page.wait_for_timeout(2000)
                continue

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
