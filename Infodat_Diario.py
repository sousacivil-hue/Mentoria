# Infodat — Preenchimento automático do Diário Online
# Coleta todas as aulas antes de abrir o Chrome e preenche tudo de uma vez
# Dois cliques para rodar.

import sys, builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent / "infodat_diario_log.txt"
_log = open(LOG_FILE, "w", encoding="utf-8")

_print_orig = builtins.print
def print(*args, **kwargs):
    texto = " ".join(str(a) for a in args)
    _print_orig(texto, **kwargs)
    _log.write(f"[{datetime.now().strftime('%H:%M:%S')}] {texto}\n")
    _log.flush()
builtins.print = print

# ══════════════════════════════════════════════════════════
# CONFIGURAÇÃO — edite aqui antes de rodar
# ══════════════════════════════════════════════════════════

ESCOLA    = "arqui"
PROFESSOR = "MARCOS ANTÔNIO PASSOS CHAGAS"
SENHA     = "chagas"
BASE_URL  = "https://www.sigmawd.com.br/infodat/professor"

# Turmas disponíveis — identificador curto → value do select
TURMAS_DISPONIVEIS = {
    "3a": "017A031",   # Terceira Série/Ensino Médio - TURMA A - Física
    "3b": "017B031",   # Terceira Série/Ensino Médio - TURMA B - Física
    # Adicione mais turmas conforme necessário
}

# ══════════════════════════════════════════════════════════

try:
    from playwright.sync_api import sync_playwright

    print("=" * 55)
    print("Infodat — Preenchimento do Diário Online")
    print("=" * 55)
    print()
    print("Turmas disponíveis:")
    for ident, val in TURMAS_DISPONIVEIS.items():
        print(f"  {ident} → {val}")
    print()

    # ── COLETA DE AULAS ──────────────────────────────────
    aulas = []
    print("Digite as aulas a registrar. Linha em branco para terminar.")
    print()

    while True:
        data = input("Data (DD/MM/AAAA) [Enter para hoje]: ").strip()
        if not data:
            data = datetime.now().strftime("%d/%m/%Y")
        if not data:
            break

        turmas_input = input(f"  Turmas (ex: 3a 3b ou só 3a): ").strip().lower()
        if not turmas_input:
            break
        idents = turmas_input.split()
        values = []
        for i in idents:
            if i in TURMAS_DISPONIVEIS:
                values.append(TURMAS_DISPONIVEIS[i])
            else:
                print(f"  ⚠️ Turma '{i}' não encontrada — ignorada")
        if not values:
            continue

        conteudo = input("  Conteúdo: ").strip()
        if not conteudo:
            break

        num_aulas = input("  Número de aulas: ").strip()
        if not num_aulas:
            num_aulas = "2"

        ativ_aula = input("  Atividade de aula (Enter para pular): ").strip()
        ativ_casa = input("  Atividade de casa (Enter para pular): ").strip()

        for v in values:
            aulas.append({
                "data": data,
                "value": v,
                "conteudo": conteudo,
                "num_aulas": num_aulas,
                "ativ_aula": ativ_aula,
                "ativ_casa": ativ_casa,
            })

        print(f"  ✅ {len(values)} turma(s) adicionada(s)\n")
        continuar = input("Adicionar mais aulas? (s/Enter para não): ").strip().lower()
        if continuar != "s":
            break

    if not aulas:
        print("Nenhuma aula para registrar. Encerrando.")
        input("ENTER para fechar")
        sys.exit()

    print(f"\n📋 Total: {len(aulas)} aula(s) para gravar")

    # ── FALTAS ───────────────────────────────────────────
    resp = input("\nHouve falta de algum aluno hoje? (s/n): ").strip().lower()
    ALUNOS_COM_FALTA = []
    if resp == "s":
        print("Digite parte do nome do aluno com falta (um por linha). Linha em branco para terminar.")
        while True:
            nome = input("  Aluno com falta: ").strip()
            if not nome:
                break
            ALUNOS_COM_FALTA.append(nome.upper())
        print(f"  → Faltas: {ALUNOS_COM_FALTA}")
    else:
        print("  → Todos presentes.")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=150, channel="chrome")
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # ── LOGIN ────────────────────────────────────────
        print("\n🔐 Fazendo login...")
        for tentativa in range(3):
            try:
                page.goto(f"{BASE_URL}/login.php", wait_until="domcontentloaded", timeout=60000)
                break
            except Exception as e:
                print(f"  ⚠️ Tentativa {tentativa+1} falhou: {e.__class__.__name__} — aguardando...")
                page.wait_for_timeout(5000)
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
        print(f"✅ Login realizado!")

        # ── DIÁRIO ONLINE ────────────────────────────────
        print("📓 Abrindo Diário Online...")
        page.locator("a.btn[href='diario.php']").click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── PREENCHER AULAS ──────────────────────────────
        gravadas = 0

        for i, aula in enumerate(aulas, 1):
            url_form = (
                f"{BASE_URL}/diario_add.php"
                f"?c={aula['value']}&d={aula['data']}&f={aula['num_aulas']}"
            )
            print(f"\n⏳ [{i}/{len(aulas)}] {aula['value']} | {aula['data']} → {aula['conteudo'][:40]}")
            page.goto(url_form, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            # Conteúdo
            campo = page.locator("input[name='conteudo'], input#conteudo")
            if campo.count() > 0:
                campo.first.fill(aula["conteudo"])

            # Atividade de aula
            if aula["ativ_aula"]:
                page.locator("textarea#ativaula").fill(aula["ativ_aula"])

            # Atividade de casa
            if aula["ativ_casa"]:
                page.locator("textarea#ativcasa").fill(aula["ativ_casa"])

            # Faltas
            if ALUNOS_COM_FALTA:
                linhas = page.locator("tr").all()
                for tr in linhas:
                    tds = tr.locator("td")
                    if tds.count() < 2:
                        continue
                    try:
                        nome_aluno = tds.nth(1).inner_text().strip().upper()
                    except Exception:
                        continue
                    if any(f in nome_aluno for f in ALUNOS_COM_FALTA):
                        cb = tr.locator("input[type='checkbox']")
                        if cb.count() > 0 and not cb.first.is_checked():
                            cb.first.check()
                            print(f"   ❌ Falta: {nome_aluno}")

            # Grava
            page.locator("button[type='submit'].btn-success").click()
            page.wait_for_timeout(3000)
            gravadas += 1
            print(f"   ✅ Gravado!")

        print(f"\n{'='*55}")
        print(f"✅ CONCLUÍDO! Aulas gravadas: {gravadas}")
        print(f"{'='*55}")

        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
