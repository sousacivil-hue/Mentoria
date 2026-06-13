# Infodat — Lê as turmas disponíveis após login
# Dois cliques para rodar. Mostra os nomes e values do select de turmas.

import builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent / "infodat_turmas_log.txt"
_log = open(LOG_FILE, "w", encoding="utf-8")

_print_orig = builtins.print
def print(*args, **kwargs):
    texto = " ".join(str(a) for a in args)
    _print_orig(texto, **kwargs)
    _log.write(f"[{datetime.now().strftime('%H:%M:%S')}] {texto}\n")
    _log.flush()
builtins.print = print

# ── CONFIGURAÇÃO ──────────────────────────────────────────────
ESCOLA    = "arqui"
PROFESSOR = "MARCOS ANTÔNIO PASSOS CHAGAS"
SENHA     = "chagas"
BASE_URL  = "https://www.sigmawd.com.br/infodat/professor"
# ─────────────────────────────────────────────────────────────

try:
    from playwright.sync_api import sync_playwright

    print("Iniciando...")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=100, channel="chrome")
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # Login
        print("Fazendo login...")
        page.goto(f"{BASE_URL}/login.php", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)
        page.locator("select#escola").select_option(value=ESCOLA)
        page.wait_for_function(
            "document.querySelector('select#professor').options.length > 1",
            timeout=10000
        )
        page.locator("select#professor").select_option(label=PROFESSOR)
        page.locator("input[type='password']").first.fill(SENHA)
        page.locator("input[value='Entrar'], button:has-text('Entrar')").first.click()
        for _ in range(20):
            page.wait_for_timeout(1000)
            if "login.php" not in page.url:
                break
        print(f"✅ Login OK — {page.url}")

        # Abre diário
        page.locator("a.btn[href='diario.php']").click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # Abre formulário de adicionar
        page.goto(f"{BASE_URL}/diario_add.php", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # Lê o select de turmas
        turmas = page.evaluate("""
            () => {
                const sel = document.querySelector('select#cursoturmadisc');
                if (!sel) return [];
                return Array.from(sel.options)
                    .filter(o => o.value)
                    .map(o => ({ value: o.value, label: o.text.trim() }));
            }
        """)

        print(f"\n📋 Turmas disponíveis ({len(turmas)}):")
        for t in turmas:
            print(f"  value={t['value']!r:20}  →  {t['label']}")

        input("\nENTER para fechar...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
