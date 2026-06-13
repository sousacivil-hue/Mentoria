# Infodat — Preenchimento automático do Diário Online
# Login → Diário Online → preenche conteúdo + presença para cada turma
# Dois cliques para rodar.

import sys, builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / "Desktop" / "diario_auto" / "infodat_diario_log.txt"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
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

ESCOLA    = "arqui"                          # value do select de escola
PROFESSOR = "MARCOS ANTÔNIO PASSOS CHAGAS"  # texto do select de professor
SENHA     = "chagas"

BASE_URL  = "https://www.sigmawd.com.br/infodat/professor"

# Turmas a preencher:
# "value_do_select": {"conteudo": "...", "num_aulas": 2, "ativ_aula": "", "ativ_casa": ""}
# O value fica no select de Curso/Disciplina (ex: "017A031", "017B031")
# Turmas com o mesmo conteúdo podem ser listadas juntas

TURMAS = [
    {
        "values":    ["017A031", "017B031"],   # Terceira Série A e B — mesmo conteúdo
        "conteudo":  "Resolução de Exercícios",
        "num_aulas": 2,
        "ativ_aula": "",   # opcional
        "ativ_casa": "",   # opcional
    },
    # Adicione mais turmas abaixo se necessário:
    # {
    #     "values":    ["OUTRO_VALUE"],
    #     "conteudo":  "Outro conteúdo",
    #     "num_aulas": 2,
    #     "ativ_aula": "",
    #     "ativ_casa": "",
    # },
]

# ══════════════════════════════════════════════════════════

try:
    from playwright.sync_api import sync_playwright

    print("=" * 55)
    print("Infodat — Preenchimento do Diário Online")
    print("=" * 55)

    # Pergunta sobre faltas
    resp = input("\nHouve falta de algum aluno hoje? (s/n): ").strip().lower()
    ALUNOS_COM_FALTA = []
    if resp == "s":
        print("Digite os nomes (parte do nome) dos alunos com falta, um por linha.")
        print("Linha em branco para terminar.")
        while True:
            nome = input("  Aluno com falta: ").strip()
            if not nome:
                break
            ALUNOS_COM_FALTA.append(nome.upper())
        print(f"  → Faltas: {ALUNOS_COM_FALTA}")
    else:
        print("  → Todos presentes.")

    DATA_HOJE = datetime.now().strftime("%d/%m/%Y")
    print(f"\n📅 Data: {DATA_HOJE}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=150, channel="chrome")
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # ── LOGIN ────────────────────────────────────────────
        print("\n🔐 Fazendo login...")
        page.goto(f"{BASE_URL}/login.php", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)

        page.locator("select#escola").select_option(value=ESCOLA)
        print("✅ Escola selecionada")

        page.wait_for_function(
            "document.querySelector('select#professor').options.length > 1",
            timeout=10000
        )
        page.locator("select#professor").select_option(label=PROFESSOR)
        print("✅ Professor selecionado")

        page.locator("input[type='password']").first.fill(SENHA)
        page.locator("input[value='Entrar'], button:has-text('Entrar')").first.click()

        for i in range(20):
            page.wait_for_timeout(1000)
            if "login.php" not in page.url:
                break
        print(f"✅ Login realizado! URL: {page.url}")

        # ── DIÁRIO ONLINE ────────────────────────────────────
        print("\n📓 Abrindo Diário Online...")
        page.locator("a[href='diario.php']").click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        print(f"✅ Diário aberto: {page.url}")

        # ── PREENCHER CADA TURMA ─────────────────────────────
        gravadas = 0

        for grupo in TURMAS:
            conteudo  = grupo["conteudo"]
            num_aulas = str(grupo["num_aulas"])
            ativ_aula = grupo.get("ativ_aula", "")
            ativ_casa = grupo.get("ativ_casa", "")

            for value in grupo["values"]:
                url_form = (
                    f"{BASE_URL}/diario_add.php"
                    f"?c={value}&d={DATA_HOJE}&f={num_aulas}"
                )
                print(f"\n⏳ Turma {value} → {conteudo[:40]}")
                page.goto(url_form, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)

                # Preenche conteúdo
                campo_conteudo = page.locator("input[name='conteudo'], input#conteudo")
                if campo_conteudo.count() > 0:
                    campo_conteudo.first.fill(conteudo)

                # Atividade de aula (opcional)
                if ativ_aula:
                    page.locator("textarea#ativaula").fill(ativ_aula)

                # Atividade de casa (opcional)
                if ativ_casa:
                    page.locator("textarea#ativcasa").fill(ativ_casa)

                # Lista de presença — marca faltas
                if ALUNOS_COM_FALTA:
                    linhas = page.locator("tr").all()
                    for tr in linhas:
                        nome_cel = tr.locator("td").nth(1) if tr.locator("td").count() > 1 else None
                        if not nome_cel:
                            continue
                        try:
                            nome_aluno = nome_cel.inner_text().strip().upper()
                        except Exception:
                            continue
                        faltou = any(f in nome_aluno for f in ALUNOS_COM_FALTA)
                        if faltou:
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
        print(f"✅ CONCLUÍDO! Turmas gravadas: {gravadas}")
        print(f"{'='*55}")

        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
