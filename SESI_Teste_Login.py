# SESI — Teste de login (Corpore.Net / FIES)
# Abre o Chrome na sua tela e tenta fazer login
# Dois cliques para rodar.

import sys, builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / "Desktop" / "diario_auto" / "sesi_login_log.txt"
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
LOGIN = "2002631"
SENHA = "250153@Si"
URL   = "https://portaleducacional.fies.org.br/Corpore.Net/Login.aspx"
# ─────────────────────────────────────────────────────────────

try:
    from playwright.sync_api import sync_playwright

    print("Iniciando Chrome...")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        print(f"Abrindo: {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        print(f"URL atual: {page.url}")
        print(f"Título: {page.title()}")

        # Diagnóstico dos campos
        campos_texto = page.locator("input[type='text'], input[type='email'], input:not([type])").count()
        campos_senha = page.locator("input[type='password']").count()
        print(f"Campos: texto={campos_texto}  senha={campos_senha}")

        # Tenta preencher
        if campos_texto > 0:
            page.locator("input[type='text']").first.fill(LOGIN)
            print("✅ Login preenchido")
        if campos_senha > 0:
            page.locator("input[type='password']").first.fill(SENHA)
            print("✅ Senha preenchida")

        # Clica no botão de entrar
        btn = page.locator("input[type='submit'], button[type='submit'], button:has-text('Entrar'), button:has-text('Login'), input[value='Entrar']").first
        if btn.count() > 0:
            btn.click()
            print("✅ Botão de login clicado")
        else:
            page.keyboard.press("Enter")
            print("✅ Enter pressionado")

        print("⏳ Aguardando login...")
        for i in range(20):
            page.wait_for_timeout(1000)
            url_atual = page.url
            print(f"  [{i+1}s] URL: {url_atual[:80]}")
            if "Login.aspx" not in url_atual:
                print("✅ LOGIN REALIZADO!")
                break

        print(f"\n🌐 URL final: {page.url}")
        print(f"📄 Título: {page.title()}")

        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
