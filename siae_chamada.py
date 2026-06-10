import asyncio
import re
from playwright.async_api import async_playwright

LOG_FILE = open("erro_siae_chamada.txt", "w", encoding="utf-8")


def log(msg):
    print(msg)
    LOG_FILE.write(msg + "\n")
    LOG_FILE.flush()


URL_LOGIN = "https://sso.seduc.se.gov.br/sistemas"
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
LOGIN = "789.626.335-15"
SENHA = "130224"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        log("=" * 55)
        log("  CHAMADA AUTOMATICA - SIAE SEDUC-SE")
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

        async def selecionar_solicitadas():
            try:
                radio = page.locator("label:has-text('Solicitada') input[type=radio], input[type=radio][value*='olicita']")
                if await radio.count() > 0:
                    await radio.first.click(force=True)
                    await page.wait_for_timeout(1500)
                    log("  Aba Solicitadas selecionada")
                    return
                radios = page.locator("input[type=radio]")
                if await radios.count() >= 2:
                    await radios.nth(1).click(force=True)
                    await page.wait_for_timeout(1500)
                    log("  Aba Solicitadas selecionada (fallback)")
            except Exception as e:
                log(f"  AVISO: nao selecionou Solicitadas: {e}")

        await selecionar_solicitadas()

        log("\nIniciando chamadas...\n")
        chamada_num = 0

        while True:
            await page.wait_for_timeout(1000)

            # Busca botoes verdes de chamada de aulas que ja tem conteudo
            botoes = await page.evaluate("""
                () => {
                    const result = [];
                    const btns = document.querySelectorAll('button[onclick*="carregarListaDePresenca"]');
                    for (const btn of btns) {
                        const tr = btn.closest('tr');
                        if (!tr) continue;
                        const tds = tr.querySelectorAll('td');
                        const objeto = tds[2] ? tds[2].innerText.trim() : '';
                        const serie = tds[3] ? tds[3].innerText.trim() : '';
                        const situacao = tds[7] ? tds[7].innerText.trim() : '';
                        const onclick = btn.getAttribute('onclick') || '';
                        // Apenas aulas com conteudo preenchido
                        if (objeto && objeto !== '-' && objeto !== '') {
                            result.push({onclick, serie, objeto, situacao});
                        }
                    }
                    return result;
                }
            """)

            if not botoes:
                log("Todas as chamadas confirmadas!")
                break

            alvo = botoes[0]
            onclick = alvo["onclick"]
            serie = alvo["serie"]
            objeto = alvo["objeto"]

            log(f"Chamada {chamada_num + 1}: {serie[:50]}")
            log(f"  Conteudo: {objeto[:50]}")
            log(f"  onclick: {onclick}")

            try:
                await page.evaluate(f"{onclick.rstrip(';')}")
                await page.wait_for_timeout(2000)

                confirmar = page.locator("button.btn-success:has-text('CONFIRMAR'), button.btn-success:has-text('Confirmar')")
                await confirmar.wait_for(timeout=5000)
                await confirmar.click()
                await page.wait_for_timeout(2000)
                log("  Chamada confirmada!")
                chamada_num += 1

            except Exception as e:
                log(f"  ERRO: {e}")
                break

            await page.wait_for_timeout(1000)

        log(f"\n{'=' * 55}")
        log(f"  CONCLUIDO! Total de chamadas: {chamada_num}")
        log(f"{'=' * 55}")
        LOG_FILE.close()
        input("\nENTER para fechar o navegador...")
        await browser.close()


asyncio.run(main())
