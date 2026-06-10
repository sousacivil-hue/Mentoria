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

        # Descobre o que a funcao registrar() faz
        js_registrar = await page.evaluate("""
            () => {
                if (typeof registrar === 'function') {
                    return registrar.toString().substring(0, 500);
                }
                return 'funcao nao encontrada';
            }
        """)
        log(f"  Funcao registrar: {js_registrar}")

        log("\nIniciando preenchimento...\n")
        aula_num = 0

        while True:
            await page.wait_for_timeout(1000)

            # Pega todos os botoes de registrar com seus IDs
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
                        if (situacao.includes('para registrar') && objeto === '') {
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
            log(f"Aula {aula_num + 1}: {serie_texto[:50]} | onclick: {onclick}")

            # Extrai o ID do onclick: registrar(165565786)
            match = re.search(r"registrar\((\d+)\)", onclick)
            if not match:
                log("  ERRO: ID nao encontrado no onclick")
                break
            aula_id = match.group(1)

            conteudo = get_conteudo(serie_texto)
            log(f"  ID: {aula_id} | conteudo: {conteudo[:40]}")

            # Chama a funcao registrar() via JS e captura o popup
            context = page.context
            try:
                async with context.expect_page(timeout=8000) as popup_info:
                    await page.evaluate(f"registrar({aula_id})")
                popup = await popup_info.value
                await popup.wait_for_load_state("domcontentloaded")
                await popup.wait_for_timeout(2000)
                log(f"  Popup URL: {popup.url}")
            except Exception as e:
                log(f"  ERRO popup: {e}")
                # Tenta navegar direto para a URL de registro
                url_reg = f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}"
                log(f"  Tentando URL direta: {url_reg}")
                await page.goto(url_reg)
                await page.wait_for_timeout(3000)
                popup = page

            # Preenche Objeto de Conhecimento
            try:
                objeto = popup.locator("textarea").nth(0)
                await objeto.wait_for(timeout=6000)
                await objeto.click(click_count=3)
                await objeto.fill(conteudo)
                log("  Objeto preenchido")
            except Exception as e:
                log(f"  ERRO objeto: {e}")

            # Preenche Metodologia (tenta textarea e input)
            met_preenchida = False
            for sel in ["textarea", "input[type='text']"]:
                try:
                    locs = popup.locator(sel)
                    count = await locs.count()
                    log(f"  {sel} count: {count}")
                    if count >= 2:
                        met = locs.nth(1)
                        await met.click()
                        await met.fill(METODOLOGIA)
                        log("  Metodologia preenchida")
                        met_preenchida = True
                        break
                except Exception as e:
                    log(f"  ERRO metodologia ({sel}): {e}")
            if not met_preenchida:
                log("  Metodologia nao preenchida")

            # Salva
            try:
                salvar = popup.locator("button:has-text('SALVAR'), button:has-text('Salvar'), input[value='SALVAR'], input[value='Salvar']").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await popup.wait_for_timeout(3000)
                log("  Salvo!")
            except Exception as e:
                log(f"  ERRO ao salvar: {e}")
                try:
                    await popup.close()
                except Exception:
                    pass
                continue

            # Confirma chamada
            try:
                confirmar = popup.locator("button:has-text('Confirmar'), button:has-text('CONFIRMAR'), input[value='Confirmar']").first
                await confirmar.wait_for(timeout=4000)
                await confirmar.click()
                await popup.wait_for_timeout(2000)
                log("  Chamada confirmada")
            except Exception:
                pass

            # Fecha popup
            try:
                if popup != page and not popup.is_closed():
                    await popup.close()
            except Exception:
                pass

            aula_num += 1
            log(f"  OK")
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(2000)

        log(f"\n{'=' * 55}")
        log(f"  CONCLUIDO! Total de aulas preenchidas: {aula_num}")
        log(f"{'=' * 55}")
        LOG_FILE.close()
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
