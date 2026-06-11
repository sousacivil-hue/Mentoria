"""
Lançamento automático de NOTAS (AV3) - ActiveSoft (SIGA)
Uso: dois cliques ou `python Notas_Active.py`

Regra aplicada:
- Média de AV1 e AV2 >= MEDIA_MINIMA  -> AV3 = NOTA_ALTA
- Média abaixo                        -> AV3 = NOTA_BAIXA
- Aluno cujo nome contém um dos EXCECOES -> AV3 = NOTA_EXCECAO

Como usar:
1. Abre o Chrome no site do colégio
2. Você faz login e navega até: Digitação de notas → turma/fase →
   Consultar (a lista de alunos com AV1, AV2 e AV3 deve estar na tela)
3. Volta ao terminal e aperta ENTER
"""

import asyncio
from playwright.async_api import async_playwright

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────

URL_LOGIN = "https://siga01.activesoft.com.br/login/?instituicao=COLEGIOVITA"

# Login automático (deixe em branco "" para logar manualmente)
LOGIN = "Luth5824"
SENHA = "Luth1801@"

MEDIA_MINIMA = 7.0   # média de AV1+AV2 para ganhar a nota alta
NOTA_ALTA = "5,0"
NOTA_BAIXA = "4,0"
NOTA_EXCECAO = "3,0"

# Alunos (trecho do nome, sem acento, minúsculo) que recebem NOTA_EXCECAO
EXCECOES = ["davi", "icaro", "vinicius oliveira", "murilo"]

# Coluna a preencher: 3 = AV3 (1=AV1, 2=AV2)
COLUNA_AV = 3

# Se True, não mexe em quem já tem AV3 digitada
PULAR_PREENCHIDAS = True

# ─────────────────────────────────────────────────────────────


def sem_acento(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


def para_num(txt: str):
    txt = (txt or "").strip().replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return None


async def lancar_notas():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        print("=" * 60)
        print("LANÇAMENTO AUTOMÁTICO DE AV3 - ACTIVESOFT")
        print(f"Regra: média >= {MEDIA_MINIMA} -> {NOTA_ALTA} | abaixo -> {NOTA_BAIXA}")
        print(f"Exceções ({NOTA_EXCECAO}): {', '.join(EXCECOES)}")
        print("=" * 60)
        print("1. Faça o LOGIN no navegador")
        print("2. Vá em Digitação de notas → turma/fase → Consultar")
        print("3. Com a lista de alunos na tela, aperte ENTER aqui")
        print("=" * 60)

        # Internet lenta: até 2 min para abrir, sem esperar carregar 100%
        page.set_default_timeout(60000)
        try:
            await page.goto(URL_LOGIN, timeout=120000, wait_until="domcontentloaded")
        except Exception as e:
            print(f"\n⚠️ A página demorou para abrir ({e})")
            print("Se o site apareceu no Chrome, siga normalmente.")
        if LOGIN:
            try:
                await page.wait_for_timeout(2000)
                await page.fill("input[name='login'], input[type='text']", LOGIN)
                await page.fill("input[name='senha'], input[type='password']", SENHA)
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(3000)
                print("\n✅ Login feito automaticamente!")
            except Exception as e:
                print(f"\n⚠️ Login automático falhou ({e}) — faça o login manualmente.")
        input("\n>>> ENTER quando a lista de alunos estiver na tela: ")
        await page.wait_for_timeout(2000)

        # Acha o frame com a tabela de alunos (linhas com inputs editáveis)
        frame_notas = None
        for frame in page.frames:
            try:
                if await frame.locator(
                    "table tr:has(input[type='text']:not([readonly]):not([disabled]))"
                ).count() > 0:
                    frame_notas = frame
                    break
            except Exception:
                continue

        if frame_notas is None:
            print("\nERRO: tabela de notas não encontrada. A lista está na tela?")
            input("ENTER para fechar...")
            await browser.close()
            return

        linhas = frame_notas.locator(
            "table tr:has(input[type='text']:not([readonly]):not([disabled]))"
        )
        total = await linhas.count()
        print(f"\nAlunos encontrados: {total}\n")

        preenchidos = 0
        pulados = 0
        for i in range(total):
            linha = linhas.nth(i)
            try:
                texto = sem_acento(await linha.inner_text())
                inputs = linha.locator(
                    "input[type='text']:not([readonly]):not([disabled])"
                )
                n_inputs = await inputs.count()
                if n_inputs < COLUNA_AV:
                    continue  # linha sem a coluna AV3 (cabeçalho etc.)

                campo_av3 = inputs.nth(COLUNA_AV - 1)
                atual = (await campo_av3.input_value()).strip()
                if PULAR_PREENCHIDAS and atual:
                    pulados += 1
                    continue

                # Decide a nota
                if any(exc in texto for exc in EXCECOES):
                    nota = NOTA_EXCECAO
                    motivo = "exceção"
                else:
                    av1 = para_num(await inputs.nth(0).input_value())
                    av2 = para_num(await inputs.nth(1).input_value())
                    if av1 is None or av2 is None:
                        nota = NOTA_BAIXA
                        motivo = "AV1/AV2 em branco -> nota baixa"
                    else:
                        media = (av1 + av2) / 2
                        if media >= MEDIA_MINIMA:
                            nota = NOTA_ALTA
                        else:
                            nota = NOTA_BAIXA
                        motivo = f"média {media:.2f}".replace(".", ",")

                await campo_av3.scroll_into_view_if_needed()
                await campo_av3.click()
                await campo_av3.fill(nota)
                await campo_av3.press("Tab")  # dispara o salvamento automático
                await page.wait_for_timeout(800)
                preenchidos += 1
                nome = " ".join(texto.split()[1:4]).title()
                print(f"  [{i + 1}/{total}] {nome}: AV3 = {nota} ({motivo})")
            except Exception as e:
                print(f"  [{i + 1}/{total}] ERRO: {e}")

        print("\n" + "=" * 60)
        print(f"✅ CONCLUÍDO! Notas lançadas: {preenchidos}")
        if pulados:
            print(f"   Já tinham AV3 (pulados): {pulados}")
        print("   Confira na tela antes de fechar.")
        print("=" * 60)
        input("\nENTER para fechar o navegador...")
        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(lancar_notas())
    except Exception:
        import traceback
        erro = traceback.format_exc()
        print("\n" + "=" * 60)
        print("ERRO INESPERADO:")
        print(erro)
        try:
            with open("erro_notas.log", "w", encoding="utf-8") as f:
                f.write(erro)
            print("(erro salvo em erro_notas.log)")
        except Exception:
            pass
        input("\nENTER para fechar...")
