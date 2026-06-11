"""
Lançamento automático de NOTAS - ActiveSoft (SIGA)
Uso: dois cliques ou `python Notas_Active.py`

Como funciona:
1. Abre o Chrome no site do colégio
2. Você faz o login e navega até: Digitação de notas → escolhe a
   turma/fase/unidade → clica em Consultar (a lista de alunos com o
   campo NOTA deve estar visível na tela)
3. Volta aqui no terminal e aperta ENTER
4. Ele preenche a nota de todos os alunos (salvamento é automático)
"""

import asyncio
from playwright.async_api import async_playwright

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────

# URL de login do colégio (ActiveSoft)
URL_LOGIN = "https://siga.activesoft.com.br/login/"

# Nota a lançar para TODOS os alunos (use ponto ou vírgula conforme o site)
NOTA = "10"

# Se True, pula alunos que já têm nota digitada (não sobrescreve)
PULAR_PREENCHIDAS = True

# ─────────────────────────────────────────────────────────────


async def lancar_notas():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("=" * 60)
        print("LANÇAMENTO AUTOMÁTICO DE NOTAS - ACTIVESOFT")
        print("=" * 60)
        print("1. Faça o LOGIN no navegador que abriu")
        print("2. Vá em: Digitação de notas")
        print("3. Selecione a turma, a fase/unidade e clique em CONSULTAR")
        print("4. Quando a lista de alunos com o campo NOTA aparecer,")
        print("   volte aqui e pressione ENTER")
        print("=" * 60)

        await page.goto(URL_LOGIN)
        input("\n>>> Pressione ENTER quando a lista de alunos estiver na tela: ")
        await page.wait_for_timeout(2000)

        # Procura os campos de nota na página e em todos os frames
        frame_notas = None
        campos = None
        for frame in page.frames:
            try:
                loc = frame.locator(
                    "table input[type='text']:not([readonly]):not([disabled]), "
                    "table input[type='number']:not([readonly]):not([disabled])"
                )
                if await loc.count() > 0:
                    frame_notas = frame
                    campos = loc
                    break
            except Exception:
                continue

        if frame_notas is None:
            print("\nERRO: nenhum campo de nota encontrado.")
            print("Verifique se a lista de alunos está visível na tela.")
            input("ENTER para fechar...")
            await browser.close()
            return

        total = await campos.count()
        print(f"\nCampos de nota encontrados: {total}")
        print(f"Lançando nota {NOTA} para todos...\n")

        preenchidos = 0
        pulados = 0
        for i in range(total):
            campo = campos.nth(i)
            try:
                atual = (await campo.input_value()).strip()
                if PULAR_PREENCHIDAS and atual:
                    pulados += 1
                    continue
                await campo.scroll_into_view_if_needed()
                await campo.click()
                await campo.fill(NOTA)
                # Tab dispara o salvamento automático do ActiveSoft
                await campo.press("Tab")
                await page.wait_for_timeout(800)
                preenchidos += 1
                print(f"  [{i + 1}/{total}] nota {NOTA} lançada")
            except Exception as e:
                print(f"  [{i + 1}/{total}] ERRO: {e}")

        print("\n" + "=" * 60)
        print(f"✅ CONCLUÍDO! Notas lançadas: {preenchidos}")
        if pulados:
            print(f"   Alunos já com nota (pulados): {pulados}")
        print("   Confira na tela antes de fechar.")
        print("=" * 60)
        input("\nENTER para fechar o navegador...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(lancar_notas())
