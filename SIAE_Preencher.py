# SIAE — Preenchimento automático do diário
# Faz login, abre o DIÁRIO e preenche todas as aulas pendentes do dia
# Dois cliques para rodar.

import sys, re, builtins, traceback
from pathlib import Path
from datetime import datetime

LOG_FILE = Path.home() / "Desktop" / "diario_auto" / "siae_log.txt"
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

LOGIN = ""
SENHA = ""

# Assunto por turma — use parte do nome como aparece no SIAE
# Exemplos: "6" (6º Ano), "7" (7º Ano), "3" (3ª Série), "eja", "mat digital", "exp mat", "financeira"
ASSUNTOS = {
    "6":           "Critérios de divisibilidade",
    "7":           "Números inteiros: potenciação",
    "3":           "Razão e proporção",
    "mat digital": "Exercícios no livro",
    "eja":         "Revisão de matemática básica",
    "exp mat":     "Razão e proporção",
    "financeira":  "Juros compostos",
}

METODOLOGIA = "Aula expositiva dialogada com resolução de exercícios."

# ══════════════════════════════════════════════════════════

import unicodedata

def normalizar(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t.replace("º", "").replace("ª", "")

def get_assunto(serie):
    serie_norm = normalizar(serie)
    for ident in sorted(ASSUNTOS, key=len, reverse=True):
        i = normalizar(ident.strip())
        if not i:
            continue
        # só número → "X ano" ou "X serie"
        if i.isdigit() and len(i) <= 2:
            if re.search(rf"\b{i}\s*(ano|serie)", serie_norm):
                return ASSUNTOS[ident]
            continue
        # número+letra (ex: "3b")
        m = re.fullmatch(r"(\d{1,2})\s*([a-z])", i)
        if m:
            num, letra = m.groups()
            if re.search(rf"\b{num}\s*(ano|serie)", serie_norm) and re.search(rf"(\s|-){letra}\b", serie_norm):
                return ASSUNTOS[ident]
            continue
        # texto livre
        palavras = i.split()
        if all(re.search(rf"\b{re.escape(p)}", serie_norm) for p in palavras):
            return ASSUNTOS[ident]
    return None

try:
    from playwright.sync_api import sync_playwright

    print("=" * 50)
    print("SIAE — Preenchimento automático do diário")
    print("=" * 50)

    # ── PERGUNTAS INICIAIS ────────────────────────────────
    resp = input("\nHouve falta de algum aluno hoje? (s/n): ").strip().lower()
    ALUNOS_COM_FALTA = []
    if resp == "s":
        print("Digite os nomes dos alunos com falta (um por linha).")
        print("Quando terminar, deixe a linha em branco e pressione ENTER.")
        while True:
            nome = input("  Aluno com falta: ").strip()
            if not nome:
                break
            ALUNOS_COM_FALTA.append(nome.lower())
        print(f"  → Faltas registradas para: {ALUNOS_COM_FALTA}")
    else:
        print("  → Todos presentes.")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        # ── LOGIN ────────────────────────────────────────
        print("\n🔐 Fazendo login...")
        page.goto("https://sso.seduc.se.gov.br/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2000)

        page.locator("input[type='text'], input[type='email']").first.fill(LOGIN)
        page.locator("input[type='password']").first.fill(SENHA)
        page.keyboard.press("Enter")

        logado = False
        for i in range(20):
            page.wait_for_timeout(1000)
            if page.url.rstrip("/").endswith("/sistemas"):
                logado = True
                break

        if not logado:
            print("❌ Login falhou. Verifique o Chrome.")
            input("ENTER para fechar")
            sys.exit()

        print("✅ Login realizado!")

        # ── ABRIR DIÁRIO ──────────────────────────────────
        print("⏳ Aguardando React carregar cards...")
        page.wait_for_timeout(4000)

        loc = page.locator("a").filter(has_text="DIÁRIO").first
        try:
            loc.click(timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(4000)

        # Pega aba do SIAE
        siae_page = next((p for p in context.pages if "siae.seduc" in p.url), None)
        if siae_page:
            page = siae_page
        print(f"✅ SIAE aberto: {page.url}")

        # ── LISTA DE AULAS ────────────────────────────────
        URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
        page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        print(f"✅ Lista de aulas carregada: {page.url}")

        # ── PREENCHER AULAS ───────────────────────────────
        salvas = 0
        sem_assunto = []
        aula_num = 0

        while True:
            page.wait_for_timeout(1000)

            botoes = page.evaluate("""
                () => {
                    const result = [];
                    const btns = document.querySelectorAll('button.btn-primary[onclick^="registrar"]');
                    for (const btn of btns) {
                        const tr = btn.closest('tr');
                        if (!tr) continue;
                        const tds = tr.querySelectorAll('td');
                        const objeto  = tds[2] ? tds[2].innerText.trim() : '';
                        const materia = tds[1] ? tds[1].innerText.trim() : '';
                        const serie   = tds[3] ? tds[3].innerText.trim() : '';
                        const onclick = btn.getAttribute('onclick') || '';
                        if (objeto === '' || objeto === '-') {
                            result.push({onclick, serie, materia});
                        }
                    }
                    return result;
                }
            """)

            if not botoes:
                print("\n✅ Todas as aulas preenchidas!")
                break

            alvo = botoes[0]
            match = re.search(r"registrar\((\d+)\)", alvo["onclick"])
            if not match:
                break

            aula_id   = match.group(1)
            serie     = alvo["serie"]
            materia   = alvo["materia"]
            texto_ref = f"{serie} | {materia}"
            aula_num += 1

            assunto = get_assunto(texto_ref)
            if not assunto:
                print(f"⚠️  [{aula_num}] SEM ASSUNTO: {serie} / {materia}")
                sem_assunto.append(f"{serie} / {materia}")
                # pula essa aula clicando em registrar e voltando
                page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
                # remove do DOM para não ficar em loop — marca como visitada
                page.evaluate(f"""
                    () => {{
                        const btns = document.querySelectorAll('button[onclick="registrar({aula_id})"]');
                        btns.forEach(b => b.closest('tr').remove());
                    }}
                """)
                continue

            print(f"⏳ [{aula_num}] {serie[:35]} → {assunto[:40]}")

            page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            try:
                obj = page.locator("textarea").nth(0)
                obj.wait_for(timeout=8000)
                obj.fill(assunto)

                met = page.locator("textarea").nth(1)
                if met.count() > 0:
                    met.fill(METODOLOGIA)

                salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar')").first
                salvar.click()
                page.wait_for_timeout(3000)
                salvas += 1
                print(f"   ✅ Salva!")
            except Exception as e:
                print(f"   ⚠️ Erro ao preencher: {e}")

            page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

        print(f"\n{'='*50}")
        print(f"✅ Aulas preenchidas: {salvas}")
        if sem_assunto:
            print(f"⚠️  Sem assunto ({len(sem_assunto)} turmas): {sem_assunto}")

        # ── CHAMADA (presença) ────────────────────────────
        print("\n📋 Iniciando registro de presença...")
        page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        chamadas = 0
        chamada_num = 0
        while True:
            page.wait_for_timeout(1000)

            botoes_verdes = page.evaluate("""
                () => {
                    const result = [];
                    const btns = document.querySelectorAll('button.btn-success, button[onclick*="carregarListaDePresenca"], button[onclick*="presenca"], a.btn-success');
                    for (const btn of btns) {
                        const onclick = btn.getAttribute('onclick') || btn.getAttribute('href') || '';
                        if (onclick) result.push({onclick});
                    }
                    return result;
                }
            """)

            if not botoes_verdes:
                print("✅ Chamadas: todas registradas!")
                break

            chamada_num += 1
            alvo = botoes_verdes[0]
            print(f"⏳ Chamada [{chamada_num}]...")

            # clica no 1º botão de chamada (abre modal com lista de alunos)
            clicou = page.evaluate("""
                () => {
                    const btns = document.querySelectorAll('button[onclick^="carregarListaDePresenca"]');
                    if (btns.length > 0) { btns[0].click(); return true; }
                    return false;
                }
            """)

            if not clicou:
                break

            page.wait_for_timeout(3000)

            # desmarca alunos com falta (se houver)
            if ALUNOS_COM_FALTA:
                try:
                    page.evaluate(f"""
                        (faltas) => {{
                            const linhas = document.querySelectorAll('tr');
                            for (const tr of linhas) {{
                                const nome = tr.innerText.toLowerCase();
                                const faltou = faltas.some(f => nome.includes(f));
                                if (faltou) {{
                                    const cb = tr.querySelector('input[type="checkbox"]');
                                    if (cb && cb.checked) cb.click();
                                }}
                            }}
                        }}
                    """, ALUNOS_COM_FALTA)
                except Exception:
                    pass

            # confirma na modal — botão verde de confirmar
            try:
                confirmar = page.locator("button.btn-success, button:has-text('Confirmar'), button:has-text('CONFIRMAR'), button:has-text('Salvar')").first
                if confirmar.count() > 0:
                    confirmar.click()
                    page.wait_for_timeout(2000)
                    chamadas += 1
                    print(f"   ✅ Presença registrada!")
                else:
                    print(f"   ⚠️ Botão confirmar não encontrado")
            except Exception as e:
                print(f"   ⚠️ Erro na chamada: {e}")

            page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

        print(f"\n{'='*50}")
        print(f"✅ CONCLUÍDO!")
        print(f"   Aulas preenchidas: {salvas}")
        print(f"   Presenças registradas: {chamadas}")
        print(f"{'='*50}")

        input("\nENTER para fechar o Chrome...")
        browser.close()

except BaseException:
    print("\n=== ERRO ===")
    print(traceback.format_exc())
    input("ENTER para fechar")
