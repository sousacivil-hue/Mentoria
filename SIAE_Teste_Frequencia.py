# SIAE — Teste de Frequência
# Roda no PC, abre o Chrome visível e testa o botão de frequência
# Coloque na pasta diario_auto na Área de Trabalho

import builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / "Desktop" / "diario_auto" / "siae_freq_log.txt"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
_log = open(LOG_FILE, "w", encoding="utf-8")

_print_orig = builtins.print
def print(*args, **kwargs):
    texto = " ".join(str(a) for a in args)
    _print_orig(texto, **kwargs)
    _log.write(f"[{datetime.now().strftime('%H:%M:%S')}] {texto}\n")
    _log.flush()
builtins.print = print

LOGIN = "789.626.335-15"
SENHA = "130224"
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"

try:
    from playwright.sync_api import sync_playwright

    print("=" * 55)
    print("SIAE — Teste do botão FREQUÊNCIA")
    print("=" * 55)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_context(viewport={"width": 1280, "height": 900}).new_page()

        print("\n🔐 Fazendo login...")
        page.goto("https://sso.seduc.se.gov.br/")
        page.wait_for_timeout(2000)
        page.fill("#user-login", LOGIN)
        page.fill("#user-password", SENHA)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)
        print(f"✅ URL após login: {page.url}")

        print("\n📋 Abrindo lista de aulas...")
        page.goto(URL_AULAS)
        page.wait_for_timeout(3000)

        # Pega o primeiro botão registrar disponível
        botoes = page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button.btn-primary[onclick^="registrar"]');
                for (const btn of btns) {
                    const tr = btn.closest('tr');
                    const tds = tr ? tr.querySelectorAll('td') : [];
                    const objeto = tds[2] ? tds[2].innerText.trim() : '';
                    if (objeto === '' || objeto === '-') {
                        return btn.getAttribute('onclick');
                    }
                }
                return null;
            }
        """)

        if not botoes:
            print("⚠️ Nenhuma aula pendente encontrada")
            input("ENTER para fechar")
            browser.close()
            exit()

        import re
        aula_id = re.search(r"\d+", botoes).group()
        print(f"\n⏳ Abrindo aula ID {aula_id}...")
        page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
        page.wait_for_timeout(3000)

        # Conta textareas
        n = page.locator("textarea").count()
        print(f"\n📋 Textareas na página: {n}")
        for i in range(n):
            t = page.locator("textarea").nth(i)
            print(f"  [{i}] placeholder='{t.get_attribute('placeholder') or ''}' visível={t.is_visible()}")

        # Verifica botão FREQUÊNCIA
        freq = page.locator("button:has-text('FREQUÊNCIA'), button:has-text('Frequência')")
        n_freq = freq.count()
        print(f"\n🔘 Botões FREQUÊNCIA encontrados: {n_freq}")
        for i in range(n_freq):
            btn = freq.nth(i)
            print(f"  [{i}] texto='{btn.inner_text()}' visível={btn.is_visible()} class='{btn.get_attribute('class')}'")

        if n_freq > 0:
            print("\n🖱️ Clicando em FREQUÊNCIA...")
            freq.first.click()
            page.wait_for_timeout(2000)

            # Verifica #btnConfirmar
            confirmar = page.locator("#btnConfirmar")
            n_conf = confirmar.count()
            print(f"\n✅ #btnConfirmar encontrados: {n_conf}")
            for i in range(n_conf):
                btn = confirmar.nth(i)
                print(f"  [{i}] texto='{btn.inner_text()}' visível={btn.is_visible()} class='{btn.get_attribute('class')}'")

        print(f"\n📄 Log salvo em: {LOG_FILE}")
        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
