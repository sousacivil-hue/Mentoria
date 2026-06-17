# SIAE — Teste completo: preencher + frequência + salvar
# Roda no PC com Chrome visível para diagnosticar problemas

import builtins, traceback, re
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
CONTEUDO_TESTE = "TESTE AUTOMATICO — pode apagar"
METODOLOGIA_TESTE = "Aula expositiva dialogada com resolução de exercícios."
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"

try:
    from playwright.sync_api import sync_playwright

    print("=" * 55)
    print("SIAE — Teste completo: preencher + frequência + salvar")
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

        aula_id = re.search(r"\d+", botoes).group()
        print(f"\n⏳ Abrindo aula ID {aula_id}...")
        page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
        page.wait_for_timeout(3000)
        print(f"✅ URL: {page.url}")

        # ── PREENCHER CONTEUDO ────────────────────────────
        print("\n✍️ Preenchendo Objeto de Conhecimento...")
        campo = page.locator("#Ministrada_Conteudo")
        if campo.count() > 0:
            campo.fill(CONTEUDO_TESTE)
            print(f"  ✅ Preenchido: '{campo.input_value()}'")
        else:
            print("  ❌ #Ministrada_Conteudo NÃO encontrado!")

        # ── PREENCHER METODOLOGIA ─────────────────────────
        print("\n✍️ Preenchendo Metodologia...")
        met = page.locator("#Ministrada_Metodologia")
        if met.count() > 0:
            met.fill(METODOLOGIA_TESTE)
            print(f"  ✅ Preenchido: '{met.input_value()}'")
        else:
            print("  ❌ #Ministrada_Metodologia NÃO encontrado!")

        # ── FREQUÊNCIA ───────────────────────────────────
        print("\n🖱️ Clicando em FREQUÊNCIA...")
        freq = page.locator("button:has-text('FREQUÊNCIA')")
        if freq.count() > 0:
            freq.first.click()
            page.wait_for_timeout(2000)
            confirmar = page.locator("#btnConfirmar.btn-success")
            if confirmar.count() > 0:
                confirmar.click()
                page.wait_for_timeout(1500)
                print("  ✅ Frequência confirmada!")
            else:
                print("  ❌ #btnConfirmar.btn-success não encontrado após abrir modal")
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
        else:
            print("  ⚠️ Botão FREQUÊNCIA não encontrado")

        # ── SALVAR ───────────────────────────────────────
        print("\n💾 Procurando botão SALVAR...")
        salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar')")
        n_salvar = salvar.count()
        print(f"  Botões salvar encontrados: {n_salvar}")
        for i in range(n_salvar):
            btn = salvar.nth(i)
            print(f"  [{i}] texto='{btn.inner_text().strip()}' visível={btn.is_visible()} enabled={btn.is_enabled()}")

        if n_salvar > 0:
            print("  🖱️ Clicando em SALVAR...")
            salvar.first.click()
            page.wait_for_timeout(3000)
            print(f"  URL após salvar: {page.url}")

            # Verifica se voltou para listagem ou se há erro
            if "Aulas" in page.url or "Home" in page.url:
                print("  ✅ Redirecionou — provavelmente salvou!")
            else:
                print("  ⚠️ Não redirecionou — verificar se há erro na tela")
                # Captura mensagens de erro
                erros = page.evaluate("""
                    () => Array.from(document.querySelectorAll('.alert, .validation-summary-errors, .field-validation-error'))
                         .map(e => e.innerText.trim()).filter(t => t)
                """)
                if erros:
                    print(f"  ❌ Erros na página: {erros}")

        print(f"\n📄 Log salvo em: {LOG_FILE}")
        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
