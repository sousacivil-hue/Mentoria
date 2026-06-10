import asyncio
from playwright.async_api import async_playwright

LOG_FILE = open("erro_siae_notas.txt", "w", encoding="utf-8")


def log(msg):
    print(msg)
    LOG_FILE.write(msg + "\n")
    LOG_FILE.flush()


URL_LOGIN = "https://sso.seduc.se.gov.br/sistemas"
LOGIN = "789.626.335-15"
SENHA = "130224"

# =============================================
# CONFIGURACAO - altere aqui antes de rodar
# =============================================
NOTA_AV2 = "8,0"   # Nota a colocar em TODOS os alunos na AV2
# Se quiser notas diferentes por aluno, deixe NOTA_AV2 = ""
# e preencha o dicionario abaixo com {matricula: nota}
NOTAS_INDIVIDUAIS = {
    # "20240141": "9,0",
    # "20240297": "7,0",
}
# =============================================


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=300)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        log("=" * 55)
        log("  LANCAMENTO DE NOTAS AV2 - SIAE SEDUC-SE")
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
        log("Depois navegue ate a tela de NOTAS da turma desejada.")
        log("Certifique-se de que a lista de alunos esta visivel.")
        log("=" * 55)
        input("\n>>> ENTER quando estiver na tela de notas da turma: ")

        await page.wait_for_timeout(1500)

        # Coleta todos os campos AV2 da tabela
        # A estrategia: encontra inputs na coluna AV2
        # O cabecalho tem: AV1, AV2, AV3(SIM) - pegamos o indice da coluna AV2
        resultado = await page.evaluate("""
            () => {
                const headers = document.querySelectorAll('table thead th, table thead td');
                let av2Index = -1;
                let matriculaIndex = -1;
                let nomeIndex = -1;

                headers.forEach((th, i) => {
                    const txt = th.innerText.trim().toUpperCase();
                    if (txt === 'AV2') av2Index = i;
                    if (txt === 'MATRÍCULA' || txt === 'MATRICULA') matriculaIndex = i;
                    if (txt === 'ALUNO') nomeIndex = i;
                });

                return { av2Index, matriculaIndex, nomeIndex, totalHeaders: headers.length };
            }
        """)

        log(f"\nEstrutura da tabela detectada: {resultado}")
        av2_index = resultado["av2Index"]
        matricula_index = resultado["matriculaIndex"]
        nome_index = resultado["nomeIndex"]

        if av2_index == -1:
            log("ERRO: Coluna AV2 nao encontrada! Verifique se esta na tela correta.")
            input("\nENTER para fechar...")
            await browser.close()
            return

        log(f"Coluna AV2 encontrada na posicao {av2_index}")

        # Pega todas as linhas da tabela
        linhas = await page.evaluate(f"""
            () => {{
                const rows = document.querySelectorAll('table tbody tr');
                const result = [];
                rows.forEach((tr, rowIdx) => {{
                    const tds = tr.querySelectorAll('td');
                    const matricula = tds[{matricula_index}] ? tds[{matricula_index}].innerText.trim() : '';
                    const nome = tds[{nome_index}] ? tds[{nome_index}].innerText.trim() : '';
                    const av2td = tds[{av2_index}];
                    const hasInput = av2td && av2td.querySelector('input');
                    result.push({{ rowIdx, matricula, nome, hasInput: !!hasInput }});
                }});
                return result;
            }}
        """)

        alunos_para_preencher = [l for l in linhas if l["hasInput"]]
        log(f"\nAlunos com campo AV2 disponivel: {len(alunos_para_preencher)}")

        preenchidos = 0
        erros = 0

        for aluno in alunos_para_preencher:
            row_idx = aluno["rowIdx"]
            matricula = aluno["matricula"]
            nome = aluno["nome"]

            # Determina a nota para este aluno
            if matricula in NOTAS_INDIVIDUAIS:
                nota = NOTAS_INDIVIDUAIS[matricula]
            elif NOTA_AV2:
                nota = NOTA_AV2
            else:
                log(f"  PULANDO {nome} ({matricula}) - sem nota configurada")
                continue

            try:
                # Seleciona o input AV2 da linha especifica
                input_av2 = page.locator(
                    f"table tbody tr:nth-child({row_idx + 1}) td:nth-child({av2_index + 1}) input"
                )

                count = await input_av2.count()
                if count == 0:
                    log(f"  PULANDO {nome} - campo AV2 nao encontrado na linha {row_idx + 1}")
                    continue

                await input_av2.first.click()
                await input_av2.first.triple_click()
                await input_av2.first.fill(nota)
                await page.keyboard.press("Tab")
                await page.wait_for_timeout(200)

                log(f"  OK: {nome[:40]} ({matricula}) -> AV2 = {nota}")
                preenchidos += 1

            except Exception as e:
                log(f"  ERRO em {nome} ({matricula}): {e}")
                erros += 1

        log(f"\n{'=' * 55}")
        log(f"  Preenchidos: {preenchidos} | Erros: {erros}")
        log(f"{'=' * 55}")

        if preenchidos > 0:
            log("\nTentando salvar...")
            try:
                # Tenta clicar em botao de salvar
                salvar = page.locator(
                    "button:has-text('Salvar'), button:has-text('SALVAR'), "
                    "input[type='submit'][value*='alvar'], "
                    "button[onclick*='salvar'], button[onclick*='Salvar']"
                )
                if await salvar.count() > 0:
                    await salvar.first.click()
                    await page.wait_for_timeout(3000)
                    log("  Salvo com sucesso!")
                else:
                    log("  ATENCAO: Botao salvar nao encontrado automaticamente.")
                    log("  Por favor, clique em SALVAR manualmente na pagina.")
            except Exception as e:
                log(f"  ERRO ao salvar: {e}")
                log("  Por favor, salve manualmente.")

        input("\nENTER para fechar o navegador...")
        LOG_FILE.close()
        await browser.close()


asyncio.run(main())
