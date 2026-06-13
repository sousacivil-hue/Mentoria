# SIAE — Teste de login
# Abre o Chrome na sua tela e tenta fazer login no SIAE
# Dois cliques para rodar. Deixa a janela aberta para ver o que acontece.

import sys, builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / "Desktop" / "diario_auto" / "siae_login_log.txt"
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
LOGIN = ""     # coloque seu CPF aqui
SENHA = ""     # coloque sua senha aqui
URL   = "https://sso.seduc.se.gov.br/"
# ─────────────────────────────────────────────────────────────

try:
    from playwright.sync_api import sync_playwright

    if not LOGIN or not SENHA:
        print("ATENÇÃO: preencha LOGIN e SENHA no topo do arquivo antes de rodar!")
        input("ENTER para fechar")
        sys.exit()

    print("Iniciando Chrome...")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1200, "height": 800})

        print(f"Abrindo: {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        print(f"URL atual: {page.url}")

        campos_texto = page.locator("input[type='text'], input[type='email']").count()
        campos_senha = page.locator("input[type='password']").count()
        print(f"Campos na tela: texto={campos_texto}  senha={campos_senha}")

        if campos_texto == 0 and campos_senha == 0:
            print("PROBLEMA: nenhum campo de login encontrado na página!")
            print("Título da página:", page.title())
            input("Verifique o Chrome e pressione ENTER para fechar")
            sys.exit()

        # Preenche login
        if campos_texto > 0:
            page.locator("input[type='text'], input[type='email']").first.fill(LOGIN)
            print("✅ CPF preenchido")
        if campos_senha > 0:
            page.locator("input[type='password']").first.fill(SENHA)
            print("✅ Senha preenchida")

        page.keyboard.press("Enter")
        print("⏳ Aguardando login...")

        logado = False
        for i in range(20):
            page.wait_for_timeout(1000)
            url_atual = page.url
            tem_senha = page.locator("input[type='password']").count() > 0
            print(f"  [{i+1}s] URL: {url_atual[:70]}  | campo_senha_visível: {tem_senha}")
            if "sso.seduc.se.gov.br" not in url_atual:
                logado = True
                break
            if not tem_senha:
                logado = True
                break

        if logado:
            print(f"✅ LOGIN REALIZADO! URL final: {page.url}")
        else:
            print("❌ Login NÃO confirmado após 20 segundos.")
            print("Verifique o Chrome — pode ter aparecido erro ou CAPTCHA.")
            input("ENTER para fechar")
            browser.close()
            sys.exit()

        # Clicar no card DIÁRIO
        print("⏳ Procurando card DIÁRIO...")
        page.wait_for_timeout(3000)

        # tenta vários seletores
        diario = None
        for sel in [
            "p.chakra-text:has-text('DIÁRIO')",
            ".chakra-text:has-text('DIÁRIO')",
            "p:text-is('DIÁRIO')",
            "p:has-text('DIÁRIO')",
            "div.css-dwrep4:has-text('DIÁRIO')",
            "text=DIÁRIO",
        ]:
            loc = page.locator(sel)
            if loc.count() > 0:
                print(f"✅ Encontrado com seletor: {sel}")
                loc.first.click()
                diario = sel
                break

        if diario:
            print("✅ Card DIÁRIO clicado!")
            page.wait_for_timeout(3000)
            print(f"🌐 URL após DIÁRIO: {page.url}")
        else:
            # diagnóstico: lista todos os textos de p na página
            textos = page.evaluate("() => Array.from(document.querySelectorAll('p')).map(p => p.innerText.trim()).filter(t => t)")
            print(f"⚠️ Card DIÁRIO não encontrado. Textos de <p> na página: {textos[:20]}")
            print("Verifique o Chrome")

        print(f"\n✅ TUDO OK! URL final: {page.url}")
        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
