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
            # /sistemas = tela de seleção de sistema = login OK
            if url_atual.rstrip("/").endswith("/sistemas"):
                logado = True
                break
            if "sso.seduc.se.gov.br" not in url_atual:
                logado = True
                break

        if logado:
            print(f"✅ LOGIN REALIZADO! URL final: {page.url}")
            print("⏳ Aguardando React carregar os cards...")
            page.wait_for_timeout(4000)
        else:
            print("❌ Login NÃO confirmado após 20 segundos.")
            print("Verifique o Chrome — pode ter aparecido erro ou CAPTCHA.")
            input("ENTER para fechar")
            browser.close()
            sys.exit()

        # Clicar no card DIÁRIO via JavaScript
        print("⏳ Procurando card DIÁRIO na página...")
        page.wait_for_timeout(2000)

        # Clica no DIÁRIO e captura nova aba ou navegação
        print("⏳ Clicando no card DIÁRIO...")
        loc = page.locator("a").filter(has_text="DIÁRIO").first
        print(f"  Encontrou <a>: {loc.count() > 0}")

        # captura se abrir nova aba
        with browser.expect_page() as new_page_info:
            try:
                loc.click(timeout=5000)
            except Exception:
                pass

        try:
            nova_aba = new_page_info.value
            nova_aba.wait_for_load_state("domcontentloaded", timeout=10000)
            print(f"✅ Abriu nova aba! URL: {nova_aba.url}")
            page = nova_aba  # continua na nova aba
        except Exception:
            # não abriu nova aba, verifica se a URL mudou
            page.wait_for_timeout(4000)
            print(f"🌐 URL após clique: {page.url}")

        # Navegar para a tela de aulas
        URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
        print(f"⏳ Acessando lista de aulas: {URL_AULAS}")
        page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        print(f"🌐 URL final: {page.url}")

        botoes = page.locator("button.btn-primary[onclick^='registrar']").count()
        print(f"✅ Botões de aula encontrados: {botoes}")

        print(f"\n✅ TUDO OK! URL final: {page.url}")
        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
