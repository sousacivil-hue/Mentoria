# Infodat — Teste de login (sigmawd.com.br)
# Abre o Chrome na sua tela, seleciona escola e professor, digita a senha e entra
# Dois cliques para rodar.

import sys, builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / "Desktop" / "diario_auto" / "infodat_login_log.txt"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
_log = open(LOG_FILE, "w", encoding="utf-8")

_print_orig = builtins.print
def print(*args, **kwargs):
    texto = " ".join(str(a) for a in args)
    _print_orig(texto, **kwargs)
    _log.write(f"[{datetime.now().strftime('%H:%M:%S')}] {texto}\n")
    _log.flush()
builtins.print = print

# ── CONFIGURAÇÃO ──────────────────────────────────────────────
ESCOLA    = "Colégio Arqui"               # texto do option no select de escola
PROFESSOR = "MARCOS ANTÔNIO PASSOS CHAGAS"  # texto do option no select de professor
SENHA     = "chagas"
URL       = "https://www.sigmawd.com.br/infodat/professor/login.php"
# ─────────────────────────────────────────────────────────────

try:
    from playwright.sync_api import sync_playwright

    print("Iniciando Chrome...")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=150)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        print(f"Abrindo: {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        print(f"URL atual: {page.url}")
        print(f"Título: {page.title()}")

        # Diagnóstico dos selects
        selects = page.locator("select").count()
        print(f"Selects encontrados: {selects}")
        for i in range(selects):
            sel = page.locator("select").nth(i)
            opts = sel.locator("option").all_text_contents()
            print(f"  Select [{i}]: {opts[:5]}{'...' if len(opts) > 5 else ''}")

        # Seleciona escola (primeiro select)
        print(f"Selecionando escola: {ESCOLA}")
        page.locator("select").nth(0).select_option(label=ESCOLA)
        page.wait_for_timeout(1500)
        print("✅ Escola selecionada")

        # Aguarda o select de professor carregar (pode ser dinâmico)
        page.wait_for_timeout(1000)
        selects_apos = page.locator("select").count()
        print(f"Selects após escolher escola: {selects_apos}")
        for i in range(selects_apos):
            sel = page.locator("select").nth(i)
            opts = sel.locator("option").all_text_contents()
            print(f"  Select [{i}]: {opts[:5]}{'...' if len(opts) > 5 else ''}")

        # Seleciona professor (segundo select)
        print(f"Selecionando professor: {PROFESSOR}")
        page.locator("select").nth(1).select_option(label=PROFESSOR)
        page.wait_for_timeout(1000)
        print("✅ Professor selecionado")

        # Preenche a senha
        print("Preenchendo senha...")
        page.locator("input[type='password']").first.fill(SENHA)
        print("✅ Senha preenchida")

        # Clica em Entrar
        page.locator("input[value='Entrar'], button:has-text('Entrar')").first.click()
        print("✅ Botão Entrar clicado")

        # Aguarda navegação
        print("⏳ Aguardando login...")
        for i in range(20):
            page.wait_for_timeout(1000)
            url_atual = page.url
            print(f"  [{i+1}s] URL: {url_atual[:80]}")
            if "login.php" not in url_atual:
                print("✅ LOGIN REALIZADO!")
                break

        print(f"\n🌐 URL final: {page.url}")
        print(f"📄 Título: {page.title()}")

        # Diagnóstico da tela após login
        links = page.locator("a").all_text_contents()
        print(f"\nLinks na tela: {links[:10]}")

        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
