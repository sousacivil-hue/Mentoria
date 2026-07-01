import asyncio
import json
import os
import re
import unicodedata

# ── Criptografia ──────────────────────────────────────────────────────────────
def _get_fernet():
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        return None
    try:
        from cryptography.fernet import Fernet
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception:
        return None

def _encrypt(valor: str) -> str:
    f = _get_fernet()
    if not f or not valor:
        return valor
    return f.encrypt(valor.encode()).decode()

def _decrypt(valor: str) -> str:
    f = _get_fernet()
    if not f or not valor:
        return valor
    try:
        return f.decrypt(valor.encode()).decode()
    except Exception:
        return valor  # já estava descriptografado (dados antigos)

# ── Supabase ──────────────────────────────────────────────────────────────────
def _get_supabase():
    url = os.environ.get("SUPABASE_URL", "https://niqgrzvaqfocpoemtwio.supabase.co")
    key = os.environ.get("SUPABASE_SECRET_KEY")
    if not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, Request, UploadFile, File


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.upper()) if unicodedata.category(c) != "Mn")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs: dict[str, list[str]] = {}

CONTEUDOS = {
    "6º": [
        "Critérios de divisibilidade - introdução", "Critérios de divisibilidade por 2 e 3",
        "Critérios de divisibilidade por 4, 5 e 6", "Critérios de divisibilidade por 9 e 10",
        "Revisão: critérios de divisibilidade - exercícios", "Números primos e compostos",
        "Decomposição em fatores primos", "MMC - conceito e cálculo",
        "MDC - conceito e cálculo", "Aplicações de MMC e MDC em situações-problema",
        "Frações: conceito e representação", "Frações equivalentes",
        "Simplificação de frações", "Adição e subtração de frações",
        "Multiplicação de frações", "Divisão de frações",
        "Operações mistas com frações", "Números decimais: leitura e escrita",
        "Adição e subtração de decimais", "Multiplicação de decimais",
        "Divisão de decimais", "Conversão entre frações e decimais",
        "Porcentagem: conceito e cálculo básico", "Resolução de problemas com porcentagem",
        "Revisão geral do bimestre",
    ],
    "7º": [
        "Porcentagem: revisão e aprofundamento", "Cálculo de porcentagem com calculadora",
        "Porcentagem: aumento e desconto", "Porcentagem: exercícios práticos",
        "Juros simples: introdução", "Juros simples: fórmula e cálculo",
        "Problemas com juros simples", "Razão: conceito e representação",
        "Proporção: conceito e propriedades", "Regra de três simples direta",
        "Regra de três simples inversa", "Regra de três composta",
        "Aplicações de proporção no cotidiano", "Números inteiros: conceito e representação",
        "Adição e subtração de inteiros", "Multiplicação e divisão de inteiros",
        "Expressões numéricas com inteiros", "Equações do 1º grau: introdução",
        "Equações do 1º grau: resolução", "Equações do 1º grau: problemas",
        "Inequações do 1º grau", "Plano cartesiano: introdução",
        "Localização no plano cartesiano", "Gráficos e tabelas: interpretação",
        "Revisão geral do bimestre",
    ],
    "1ª Série": [
        "Conjuntos: conceitos e notação", "Operações com conjuntos: união e interseção",
        "Funções: conceito e definição", "Função afim: definição e gráfico",
        "Função afim: crescimento e decrescimento", "Função afim: aplicações",
        "Função quadrática: introdução", "Função quadrática: vértice e gráfico",
        "Função quadrática: máximo e mínimo", "Função quadrática: aplicações",
        "Função exponencial: definição", "Função exponencial: gráfico e propriedades",
        "Progressão aritmética: conceito e razão", "PA: termo geral",
        "PA: soma dos termos", "Progressão geométrica: conceito e razão",
        "PG: termo geral", "PG: soma dos termos", "Trigonometria: seno, cosseno e tangente",
        "Trigonometria no triângulo retângulo", "Trigonometria: aplicações",
        "Logaritmos: definição e propriedades", "Logaritmos: cálculo",
        "Matrizes: introdução e operações", "Revisão geral do bimestre",
    ],
    "2ª Série": [
        "Trigonometria na circunferência: seno e cosseno", "Ciclo trigonométrico",
        "Equações trigonométricas", "Geometria plana: triângulos",
        "Geometria plana: quadriláteros", "Área de figuras planas",
        "Geometria espacial: prismas e pirâmides", "Volume de sólidos geométricos",
        "Probabilidade: espaço amostral", "Probabilidade clássica",
        "Probabilidade condicional", "Estatística: média, moda e mediana",
        "Estatística: variância e desvio padrão", "Análise combinatória: princípio multiplicativo",
        "Permutações", "Combinações", "Arranjos",
        "Binômio de Newton", "Números complexos: introdução",
        "Operações com complexos", "Geometria analítica: ponto e reta",
        "Equação da reta", "Distância entre ponto e reta",
        "Circunferência: equação geral", "Revisão geral do bimestre",
    ],
    "3ª Série": [
        "Razão e proporção: revisão e aprofundamento", "Regra de três: revisão",
        "Matemática Financeira: juros simples", "Matemática Financeira: juros compostos",
        "Matemática Financeira: descontos", "Matemática Financeira: financiamentos",
        "Matemática Financeira: investimentos e aplicações",
        "Matemática e o Mundo Digital: sistemas numéricos binário e decimal",
        "Matemática e o Mundo Digital: conversão de bases numéricas",
        "Matemática e o Mundo Digital: lógica booleana",
        "Matemática e o Mundo Digital: algoritmos e sequências lógicas",
        "Expressão Matemática: álgebra no cotidiano",
        "Expressão Matemática: modelagem matemática",
        "Expressão Matemática: equações e sistemas aplicados",
        "Geometria analítica: revisão de ponto e reta",
        "Geometria analítica: cônicas — circunferência",
        "Geometria analítica: cônicas — elipse e hipérbole",
        "Probabilidade e Estatística: revisão geral",
        "Estatística aplicada: leitura e interpretação de dados reais",
        "Análise combinatória aplicada a problemas do ENEM",
        "Revisão: funções para o ENEM", "Revisão: trigonometria para o ENEM",
        "Simulado e correção — parte 1", "Simulado e correção — parte 2",
        "Revisão geral do bimestre",
    ],
    "(EJA)": [
        "Operações básicas: adição e subtração", "Operações básicas: multiplicação e divisão",
        "Frações no cotidiano", "Números decimais e dinheiro",
        "Porcentagem na vida prática: descontos e acréscimos",
        "Juros simples: empréstimos e compras a prazo",
        "Medidas de comprimento: metro e seus múltiplos",
        "Medidas de massa: quilo e grama", "Medidas de capacidade: litro",
        "Medidas de tempo: horas, minutos e segundos",
        "Regra de três simples: receitas e proporções do dia a dia",
        "Geometria básica: figuras planas", "Perímetro e área de figuras simples",
        "Leitura e interpretação de gráficos e tabelas",
        "Média aritmética: notas e temperaturas",
        "Sistema monetário: troco e orçamento doméstico",
        "Razão e proporção no cotidiano", "Probabilidade básica: chances e eventos",
        "Números inteiros: positivos e negativos (temperatura, saldo bancário)",
        "Equações simples do 1º grau aplicadas ao dia a dia",
        "Expressões numéricas com operações básicas",
        "Matemática e consumo: comparação de preços",
        "Escalas e mapas: leitura e interpretação",
        "Revisão geral: operações e resolução de problemas",
        "Revisão final do bimestre",
    ],
}

_indices: dict[str, int] = {}


def _normalizar(texto: str) -> str:
    import unicodedata
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.replace("º", "").replace("ª", "")


def get_conteudo(serie: str, assuntos_proprios: list[str], assuntos_por_turma: dict[str, str] | None = None) -> str | None:
    # Retorna None se nenhum assunto configurado → aula será pulada
    # dict turma→assunto: aceita formas triviais — "6" (6º ano), "3b" (3ª série B),
    # "eja", "mat digital", "exp mat" (abreviações casam com início das palavras)
    if assuntos_por_turma:
        serie_norm = _normalizar(serie)
        # identificadores mais específicos (mais longos) primeiro
        for identificador in sorted(assuntos_por_turma, key=len, reverse=True):
            assunto = assuntos_por_turma[identificador]
            ident_norm = _normalizar(identificador.strip())
            if not ident_norm:
                continue
            # só número (ex: "6") → "6 ano" ou "6 serie"
            if ident_norm.isdigit() and len(ident_norm) <= 2:
                if re.search(rf"\b{ident_norm}\s*(ano|serie)", serie_norm):
                    return assunto
                continue
            # número+letra (ex: "3b") → "3 serie ... b"
            m = re.fullmatch(r"(\d{1,2})\s*([a-z])", ident_norm)
            if m:
                num, letra = m.group(1), m.group(2)
                if re.search(rf"\b{num}\s*(ano|serie)", serie_norm) and re.search(rf"(\s|-){letra}\b", serie_norm):
                    return assunto
                continue
            # texto: cada palavra casa com o início de alguma palavra ("exp mat" → Expressão Matemática)
            palavras = ident_norm.split()
            if all(re.search(rf"\b{re.escape(p)}", serie_norm) for p in palavras):
                return assunto
        # turma não tem assunto configurado → pula
        return None

    if assuntos_proprios:
        chave = serie[:6]
        idx = _indices.get(chave, 0)
        _indices[chave] = idx + 1
        return assuntos_proprios[idx % len(assuntos_proprios)]

    for chave, lista in CONTEUDOS.items():
        if chave in serie:
            idx = _indices.get(chave, 0)
            _indices[chave] = idx + 1
            return lista[idx % len(lista)]
    return "Conteúdo programático da disciplina"


class FormData(BaseModel):
    login: str
    senha: str
    opcoes: dict
    modo_conteudo: str = "pronto"
    assuntos: list[str] = []
    assuntos_por_turma: dict[str, str] = {}
    avaliacao: str = "AV2"
    nota: str = ""
    numero: str = ""


URL_LOGIN = "https://sso.seduc.se.gov.br/"
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
METODOLOGIA = "Aula expositiva dialogada com resolução de exercícios."


async def run_automacao(job_id: str, data: FormData):
    from playwright.async_api import async_playwright

    import time as _time
    log = jobs[job_id]
    _indices.clear()
    _inicio = _time.time()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR','pt','en-US','en']});
            window.chrome = {runtime: {}};
        """)

        log.append("🔐 Fazendo login no SIAE...")
        await page.goto(URL_LOGIN, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2000)

        logado = False
        try:
            cpf = re.sub(r'\D', '', data.login)
            login_fmt = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}" if len(cpf) == 11 else data.login
            await page.wait_for_selector("#user-login, input[type='text']", timeout=15000)
            await page.fill("#user-login", login_fmt)
            await page.wait_for_timeout(300)
            await page.fill("#user-password", data.senha)
            await page.wait_for_timeout(300)
            await page.keyboard.press("Enter")

            for _ in range(20):
                await page.wait_for_timeout(1000)
                url_atual = page.url
                if url_atual.rstrip("/").endswith("/sistemas"):
                    logado = True
                    break
                if "sso.seduc.se.gov.br" not in url_atual:
                    logado = True
                    break

            if logado:
                log.append("✅ Login realizado!")
            else:
                log.append(f"❌ Login falhou. URL: {page.url}")
                return
            # clica no card DIÁRIO
            loc = page.locator("a").filter(has_text="DIÁRIO").first
            try:
                await loc.click(timeout=5000)
            except Exception:
                pass
            await page.wait_for_timeout(4000)
            # pega aba do SIAE (pode ter aberto nova aba)
            paginas = context.pages
            siae_page = next((p for p in paginas if "siae.seduc" in p.url), None)
            if siae_page:
                page = siae_page
        except Exception as e:
            log.append(f"❌ Erro no login: {e}")
            return

        # ---- AULAS REGULARES ----
        if data.opcoes.get("aulas"):
            log.append("📋 Acessando aulas regulares...")
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(3000)

            aula_num = 0
            ja_visitados: set[str] = set()
            while True:
                await page.wait_for_timeout(1000)
                botoes = await page.evaluate("""
                    () => {
                        const result = [];
                        const btns = document.querySelectorAll('button.btn-primary[onclick^="registrar"]');
                        for (const btn of btns) {
                            const tr = btn.closest('tr');
                            if (!tr) continue;
                            const tds = tr.querySelectorAll('td');
                            const objeto = tds[2] ? tds[2].innerText.trim() : '';
                            const materia = tds[1] ? tds[1].innerText.trim() : '';
                            const serie = (tds[3] ? tds[3].innerText.trim() : '') + ' | ' + materia;
                            const onclick = btn.getAttribute('onclick') || '';
                            if (objeto === '' || objeto === '-') {
                                result.push({onclick, serie});
                            }
                        }
                        return result;
                    }
                """)
                if not botoes:
                    log.append("✅ Aulas regulares: todas preenchidas!")
                    break

                alvo = botoes[0]
                match = re.search(r"registrar\((\d+)\)", alvo["onclick"])
                if not match:
                    break
                aula_id = match.group(1)
                serie = alvo["serie"]
                conteudo = get_conteudo(serie, data.assuntos, data.assuntos_por_turma)

                if not conteudo:
                    log.append(f"⏭️ Pulando (sem assunto): {serie[:40]}")
                    await page.evaluate(f"""
                        () => {{
                            const btn = document.querySelector('button[onclick="registrar({aula_id})"]');
                            if (btn) btn.closest('tr').remove();
                        }}
                    """)
                    continue

                log.append(f"⏳ Aula {aula_num + 1}: {serie[:40]}")
                await page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
                await page.wait_for_timeout(3000)

                try:
                    await page.locator("#Ministrada_Conteudo").wait_for(timeout=6000)
                    await page.locator("#Ministrada_Conteudo").fill(conteudo)
                    await page.locator("#Ministrada_Metodologia").fill(METODOLOGIA)
                    # justificativa — só aparece em aulas com atraso
                    just = page.locator("input[name='Ministrada.Justificativa'], textarea[name='Ministrada.Justificativa']")
                    if await just.count() > 0 and await just.is_visible():
                        await just.fill("Instabilidade no sistema")
                    # frequência
                    try:
                        freq_btn = page.locator("button:has-text('FREQUÊNCIA')")
                        if await freq_btn.count() > 0:
                            await freq_btn.first.click(timeout=3000)
                            await page.wait_for_timeout(1500)
                            await page.locator("#btnConfirmar.btn-success").click(timeout=5000)
                            await page.wait_for_timeout(1500)
                            log.append("✅ Frequência registrada")
                    except Exception as ef:
                        log.append(f"⚠️ Frequência: {type(ef).__name__}")
                        await page.keyboard.press("Escape")
                        await page.wait_for_timeout(500)
                    await page.locator("button:has-text('SALVAR'), button:has-text('Salvar')").first.click()
                    await page.wait_for_timeout(3000)
                    aula_num += 1
                    log.append(f"✅ Salva: {conteudo[:50]}")
                except Exception as e:
                    log.append(f"⚠️ Erro: {e}")

                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)

        # ---- AULAS SOLICITADAS ----
        if data.opcoes.get("solicitadas"):
            log.append("📋 Acessando aulas solicitadas...")
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(3000)

            async def selecionar_solicitadas():
                try:
                    radio = page.locator("label:has-text('Solicitada') input[type=radio]")
                    if await radio.count() > 0:
                        await radio.first.click(force=True)
                        await page.wait_for_timeout(1500)
                        return
                    radios = page.locator("input[type=radio]")
                    if await radios.count() >= 2:
                        await radios.nth(1).click(force=True)
                        await page.wait_for_timeout(1500)
                except Exception:
                    pass

            await selecionar_solicitadas()
            aula_num = 0
            while True:
                await page.wait_for_timeout(1000)
                botoes = await page.evaluate("""
                    () => {
                        const result = [];
                        const btns = document.querySelectorAll('button.btn-primary[onclick^="registrar"]');
                        for (const btn of btns) {
                            const tr = btn.closest('tr');
                            if (!tr) continue;
                            const tds = tr.querySelectorAll('td');
                            const objeto = tds[2] ? tds[2].innerText.trim() : '';
                            const materia = tds[1] ? tds[1].innerText.trim() : '';
                            const serie = (tds[3] ? tds[3].innerText.trim() : '') + ' | ' + materia;
                            const onclick = btn.getAttribute('onclick') || '';
                            if (objeto === '' || objeto === '-') {
                                result.push({onclick, serie});
                            }
                        }
                        return result;
                    }
                """)
                if not botoes:
                    log.append("✅ Solicitadas: todas preenchidas!")
                    break

                alvo = botoes[0]
                match = re.search(r"registrar\((\d+)\)", alvo["onclick"])
                if not match:
                    break
                aula_id = match.group(1)
                serie = alvo["serie"]
                conteudo = get_conteudo(serie, data.assuntos, data.assuntos_por_turma) or (data.assuntos[0] if data.assuntos else "Conteúdo ministrado")

                log.append(f"⏳ Solicitada {aula_num + 1}: {serie[:40]}")
                await page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
                await page.wait_for_timeout(3000)

                try:
                    await page.locator("#Ministrada_Conteudo").wait_for(timeout=6000)
                    await page.locator("#Ministrada_Conteudo").fill(conteudo)
                    await page.locator("#Ministrada_Metodologia").fill(METODOLOGIA)
                    just = page.locator("input[name='Ministrada.Justificativa'], textarea[name='Ministrada.Justificativa']")
                    if await just.count() > 0:
                        await just.first.fill("Instabilidade no sistema")
                    try:
                        freq_btn = page.locator("button:has-text('FREQUÊNCIA')")
                        if await freq_btn.count() > 0:
                            await freq_btn.first.click(timeout=3000)
                            await page.wait_for_timeout(1500)
                            await page.locator("#btnConfirmar.btn-success").click(timeout=5000)
                            await page.wait_for_timeout(1500)
                            log.append("✅ Frequência registrada")
                    except Exception as ef:
                        log.append(f"⚠️ Frequência: {type(ef).__name__}")
                        await page.keyboard.press("Escape")
                        await page.wait_for_timeout(500)
                    await page.locator("button:has-text('SALVAR'), button:has-text('Salvar')").first.click()
                    await page.wait_for_timeout(3000)
                    aula_num += 1
                    log.append(f"✅ Salva: {conteudo[:50]}")
                except Exception as e:
                    log.append(f"⚠️ Erro: {e}")

                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)
                await selecionar_solicitadas()

        # ── CHAMADA AUTOMÁTICA (após aulas regulares e solicitadas) ──
        log.append("📋 Registrando presença em todas as aulas...")
        await page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        ja_feitos_chamada = set()
        chamada_num = 0
        while True:
            await page.wait_for_timeout(1000)
            botoes_chamada = await page.evaluate("""
                () => {
                    const result = [];
                    const btns = document.querySelectorAll('button[onclick^="carregarListaDePresenca"]');
                    for (const btn of btns) {
                        const onclick = btn.getAttribute('onclick') || '';
                        if (onclick) result.push({onclick});
                    }
                    return result;
                }
            """)
            pendentes = [b for b in botoes_chamada if b["onclick"] not in ja_feitos_chamada]
            if not pendentes:
                log.append("✅ Presenças: todas registradas!")
                break
            alvo = pendentes[0]
            onclick = alvo["onclick"]
            ja_feitos_chamada.add(onclick)
            chamada_num += 1
            try:
                onclick_esc = onclick.replace("'", "\\'")
                await page.evaluate(f"""
                    () => {{
                        const btn = document.querySelector("button[onclick='{onclick_esc}']");
                        if (btn) btn.click();
                    }}
                """)
                await page.wait_for_selector("#lista.in, #lista[style*='display: block'], #btnConfirmar", timeout=8000)
                await page.wait_for_timeout(1000)
                await page.locator("#btnConfirmar").click()
                await page.wait_for_timeout(2000)
                log.append(f"✅ Presença {chamada_num} confirmada!")
            except Exception as e:
                log.append(f"⚠️ Erro na presença {chamada_num}: {e}")
            await page.goto(URL_AULAS, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

        # ---- NOTAS ----
        if data.opcoes.get("notas") and data.nota:
            log.append(f"🔢 Lançando {data.avaliacao} = {data.nota}...")
            # O professor deve navegar até a tela de notas
            # Por ora registramos a intenção no log
            log.append("⚠️ Para notas: navegue até a tela de notas no SIAE e use o siae_notas.py")

        _elapsed = int(_time.time() - _inicio)
        _min, _seg = divmod(_elapsed, 60)
        log.append(f"🎉 Automação concluída em {_min}min {_seg}s!")
        log.append("__CONCLUIDO__")
        await browser.close()


class ActiveFormData(BaseModel):
    sistema: str = "activesoft"
    url_colegio: str = "https://siga.activesoft.com.br/login/"
    usuario: str
    senha: str
    bimestre: str = "2"  # 1, 2, 3 ou 4
    turma: str = ""  # vazio = todas as turmas
    inicio: str  # YYYY-MM-DD
    fim: str
    aulas_por_dia: dict  # {"1": 2, "2": 0, ...} 1=seg..5=sex
    eventos: list[dict] = []  # [{"data": "2025-04-21", "tipo": "Feriado"}]
    sabados_letivos: list[dict] = []  # [{"data": "2025-04-26", "segue_dia": 1}]
    emendas: bool = True  # feriado qui->sex e ter->seg imprensados
    topicos: list[str] = []


# Feriados nacionais + Sergipe (2026)
FERIADOS_FIXOS = [
    "2026-01-01",  # Confraternização Universal
    "2026-02-16", "2026-02-17",  # Carnaval
    "2026-02-18",  # Quarta de Cinzas (meio período, geralmente sem aula)
    "2026-04-03",  # Sexta-feira Santa
    "2026-04-21",  # Tiradentes
    "2026-05-01",  # Dia do Trabalho
    "2026-06-04",  # Corpus Christi
    "2026-06-24",  # São João
    "2026-07-08",  # Emancipação de Sergipe
    "2026-09-07",  # Independência
    "2026-10-12",  # N. Sra. Aparecida
    "2026-10-15",  # Dia do Professor
    "2026-11-02",  # Finados
    "2026-11-15",  # Proclamação da República
    "2026-11-20",  # Consciência Negra
    "2026-12-25",  # Natal
]


def montar_calendario(data: ActiveFormData) -> list[dict]:
    """Gera a lista de aulas: data, quantidade e conteúdo de cada uma."""
    from datetime import date, timedelta

    eventos_map = {e["data"]: e["tipo"] for e in data.eventos if e.get("data")}

    # Adiciona feriados nacionais/SE automaticamente
    feriados_auto = set(FERIADOS_FIXOS)
    for f in FERIADOS_FIXOS:
        try:
            df = date.fromisoformat(f)
        except ValueError:
            continue
        if data.emendas:
            # Feriado na quinta -> imprensa a sexta
            if df.isoweekday() == 4:
                feriados_auto.add((df + timedelta(days=1)).isoformat())
            # Feriado na terça -> imprensa a segunda
            if df.isoweekday() == 2:
                feriados_auto.add((df - timedelta(days=1)).isoformat())

    for f in feriados_auto:
        if f not in eventos_map:
            eventos_map[f] = "Feriado"
    # Sábados letivos: data -> dia da semana cujo horário ele segue
    sabados_map = {s["data"]: int(s["segue_dia"]) for s in data.sabados_letivos if s.get("data")}
    aulas = []
    idx_topico = 0

    d = date.fromisoformat(data.inicio)
    fim = date.fromisoformat(data.fim)

    while d <= fim:
        dow = d.isoweekday()  # 1=seg .. 7=dom
        iso = d.isoformat()

        if dow == 6 and iso in sabados_map:
            # Sábado letivo segue o horário de outro dia
            qtd = int(data.aulas_por_dia.get(str(sabados_map[iso]), 0) or 0)
        else:
            qtd = int(data.aulas_por_dia.get(str(dow), 0) or 0)
            if dow == 6:
                qtd = 0  # sábado comum não tem aula

        if 1 <= dow <= 6 and qtd > 0:
            tipo_especial = eventos_map.get(iso)
            if tipo_especial == "Feriado":
                pass  # pula o dia
            elif tipo_especial:
                for _ in range(qtd):
                    aulas.append({"data": iso, "conteudo": tipo_especial})
            else:
                for _ in range(qtd):
                    if data.topicos:
                        base = data.topicos[idx_topico % len(data.topicos)]
                        volta = idx_topico // len(data.topicos)
                        conteudo = base if volta == 0 else f"{base} — continuação e exercícios"
                        idx_topico += 1
                    else:
                        conteudo = "Conteúdo programático da disciplina"
                    aulas.append({"data": iso, "conteudo": conteudo})
        d += timedelta(days=1)

    return aulas


async def run_active(job_id: str, data: ActiveFormData):
    from playwright.async_api import async_playwright

    log = jobs[job_id]

    log.append("📅 Montando calendário de aulas...")
    aulas = montar_calendario(data)
    log.append(f"📊 Total de aulas a lançar: {len(aulas)}")

    log.append("=" * 40)
    log.append("📅 PROGRAMAÇÃO DAS AULAS:")
    for i, a in enumerate(aulas):
        # Converte 2026-04-06 -> 06/04/2026
        partes = a["data"].split("-")
        data_br = f"{partes[2]}/{partes[1]}/{partes[0]}"
        log.append(f"  {i + 1}. {data_br} — {a['conteudo'][:60]}")
    log.append("=" * 40)

    URL_ACTIVE = data.url_colegio or "https://siga.activesoft.com.br/login/"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote","--disable-extensions","--disable-images"])
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        log.append("🔐 Fazendo login no ActiveSoft...")
        try:
            await page.goto(URL_ACTIVE)
            await page.wait_for_timeout(1500)
            usuario_input = page.locator(
                "input[name='usuario'], input[name='login'], input[name='username'], input[type='text']"
            ).first
            await usuario_input.fill(data.usuario)
            await page.locator("input[type='password']").first.fill(data.senha)
            await page.locator(
                "button[type='submit'], input[type='submit'], button:has-text('Entrar'), button:has-text('Acessar')"
            ).first.click()

            # Aguarda sair da página de login (até 15s) — reage imediatamente quando a URL muda
            try:
                await page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
            except Exception:
                pass  # timeout — verificamos a URL logo abaixo

            if "/login" in page.url:
                # Login não avançou — captura a mensagem de erro do site
                msg_erro = ""
                try:
                    msg_erro = await page.evaluate(
                        "() => Array.from(document.querySelectorAll("
                        "'.alert, .error, .erro, [class*=alert], [class*=error], [role=alert], .toast, .swal2-content'"
                        ")).map(e => e.innerText.trim()).filter(t => t).join(' | ')"
                    )
                except Exception:
                    pass
                log.append("❌ ERRO: o login não foi aceito — a página continuou na tela de login.")
                if msg_erro:
                    log.append(f"📢 Mensagem do site: {msg_erro}")
                log.append("💡 Confira usuário e senha (teste entrar manualmente nesse mesmo link) e tente de novo.")
                log.append("__ERRO__")
                log.append("__CONCLUIDO__")
                await browser.close()
                return

            log.append(f"✅ Login realizado — {page.url}")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        async def achar(seletor, tentativas=10):
            """Procura um elemento na página e em todos os frames internos.
            Repete por até `tentativas` x 0,8s para aguardar a página carregar."""
            for _ in range(tentativas):
                for frame in page.frames:
                    try:
                        loc = frame.locator(seletor)
                        if await loc.count() > 0:
                            return frame, loc.first
                    except Exception:
                        continue
                await page.wait_for_timeout(800)
            return None, None

        # ---- 1. Clica em EXIBIR (obrigatório: é ele que mostra as turmas) ----
        frame_ex, exibir = await achar(
            "button:has-text('EXIBIR'), input[value*='EXIBIR' i], a:has-text('EXIBIR'), *[onclick]:has-text('EXIBIR')",
            tentativas=20,
        )
        if exibir:
            await exibir.click()
            await page.wait_for_timeout(800)
            log.append("✅ Período exibido")
        else:
            log.append("❌ ERRO: botão EXIBIR não apareceu (página demorou demais para carregar).")
            log.append("💡 Tente novamente — se repetir, me avise.")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        # ---- 2. Descobre as turmas disponíveis (procurando em frames) ----
        url_lista_turmas = page.url
        frame_diario, _ = await achar("a:has-text('Diário de classe')")
        if frame_diario is None:
            log.append("❌ ERRO: nenhum 'Diário de classe' encontrado na página")
            log.append("__ERRO__")
            await browser.close()
            return

        total_turmas = await frame_diario.locator("a:has-text('Diário de classe')").count()
        log.append(f"📚 Turmas encontradas: {total_turmas}")

        async def preencher_turma(indice_link: int):
            """Abre o diário de uma turma e preenche as aulas do bimestre."""
            fr, _ = await achar("a:has-text('Diário de classe')")
            links = fr.locator("a:has-text('Diário de classe')")
            await links.nth(indice_link).click()
            await page.wait_for_timeout(800)

            # Registro de aulas do bimestre (pode abrir em frame ou nova página)
            # Cada colégio nomeia diferente: "1º BIMESTRE", "1ª UNIDADE", "1ª ETAPA"...
            try:
                bim_num = int(str(data.bimestre).strip())
            except ValueError:
                bim_num = 1
            rotulos = [
                f"{bim_num}º BIMESTRE", f"{bim_num}ª UNIDADE",
                f"{bim_num}º BIM", f"{bim_num}ª ETAPA",
                f"{bim_num} UNIDADE", f"{bim_num} BIMESTRE",
            ]
            fr2 = None
            rotulo_achado = None
            for rotulo in rotulos:
                fr2, _ = await achar(f"tr:has-text('{rotulo}')", tentativas=4)
                if fr2 is not None:
                    rotulo_achado = rotulo
                    break
            if fr2 is not None:
                log.append(f"📑 Fase encontrada: {rotulo_achado}")
                # Tabelas aninhadas: várias <tr> podem conter o texto.
                # Escolhe a MENOR (a linha específica, não a tabela inteira).
                candidatas = fr2.locator(f"tr:has-text('{rotulo_achado}')")
                qtd_tr = await candidatas.count()
                linha_bim = None
                menor_tam = None
                for i in range(qtd_tr):
                    tr = candidatas.nth(i)
                    if await tr.locator("a:has-text('Registro de aulas')").count() == 0:
                        continue
                    tam = len((await tr.inner_text()) or "")
                    if menor_tam is None or tam < menor_tam:
                        menor_tam = tam
                        linha_bim = tr
                if linha_bim is None:
                    raise RuntimeError(f"Linha de '{rotulo_achado}' sem link de Registro de aulas")
                reg = linha_bim.locator("a:has-text('Registro de aulas')").first
                await reg.wait_for(timeout=8000)
                await reg.click()
            # sem wait fixo aqui — achar() já aguarda a tabela de aulas aparecer
            else:
                # Plano B: procura os links "Registro de aulas" diretamente
                # (alguns colégios mostram um link por bimestre, na ordem)
                fr2b, _ = await achar("a:has-text('Registro de aulas')", tentativas=5)
                if fr2b is not None:
                    links_reg = fr2b.locator("a:has-text('Registro de aulas')")
                    qtd = await links_reg.count()
                    if qtd >= bim_num:
                        log.append(f"ℹ️ Layout alternativo: {qtd} links de registro — abrindo o {bim_num}º")
                        await links_reg.nth(bim_num - 1).click()
                    else:
                        log.append(f"ℹ️ Apenas {qtd} link(s) de registro — abrindo o primeiro")
                        await links_reg.first.click()
                else:
                    # Plano C: alguns colégios caem direto na tabela de aulas,
                    # sem seleção de bimestre (o bimestre fica nas datas digitadas)
                    fr_direto, _ = await achar("table tr:has(textarea)", tentativas=3)
                    if fr_direto is not None:
                        log.append("ℹ️ Sem tabela de bimestres — registro de aulas direto (bimestre definido pelas datas)")
                    else:
                        # Diagnóstico: mostra o que existe na página para ajustarmos
                        for fi, frame in enumerate(page.frames):
                            try:
                                textos = await frame.evaluate(
                                    "() => Array.from(document.querySelectorAll('a, button, td, th'))"
                                    ".map(e => (e.innerText || '').trim()).filter(t => t && t.length < 60)"
                                    ".slice(0, 40)"
                                )
                                if textos:
                                    log.append(f"🔍 Frame {fi}: {textos}")
                            except Exception:
                                continue
                        raise RuntimeError("Tabela de bimestres não encontrada")
            log.append(f"✅ Registro de aulas aberto")

            # Localiza o frame onde está a tabela de aulas
            fr3, _ = await achar("table tr:has(textarea)")
            if fr3 is None:
                raise RuntimeError("Tabela de aulas não encontrada")

            # Conta quantas aulas JÁ existem (linhas com conteúdo preenchido)
            ja_existentes = 0
            linhas = fr3.locator("table tr:has(textarea)")
            total_linhas = await linhas.count()
            for i in range(total_linhas):
                txt = (await linhas.nth(i).locator("textarea").first.input_value()).strip()
                if txt:
                    ja_existentes += 1

            if ja_existentes > 0:
                log.append(f"📋 Já existem {ja_existentes} aulas — continuando da aula {ja_existentes + 1}")

            preenchidas = 0
            # Cria as aulas restantes, uma por vez: data + conteúdo + Gravar
            for idx_aula in range(ja_existentes, len(aulas)):
                aula = aulas[idx_aula]
                partes = aula["data"].split("-")
                data_br = f"{partes[2]}/{partes[1]}/{partes[0]}"

                # Reobtém o frame a cada aula (a página pode recarregar após Gravar)
                for tentativa in range(3):
                    fr3, _ = await achar("table tr:has(textarea)")
                    if fr3 is not None:
                        break
                    await page.wait_for_timeout(2000)
                if fr3 is None:
                    log.append("⚠️ Tabela de aulas sumiu após recarregar")
                    break

                # Acha a primeira linha em branco
                linha_vazia = None
                linhas = fr3.locator("table tr:has(textarea)")
                total_linhas = await linhas.count()
                for i in range(total_linhas):
                    linha = linhas.nth(i)
                    await linha.scroll_into_view_if_needed()
                    txt = (await linha.locator("textarea").first.input_value()).strip()
                    if not txt:
                        linha_vazia = linha
                        break

                if linha_vazia is None:
                    log.append("⚠️ Nenhuma linha em branco disponível — limite de aulas atingido?")
                    break

                # Preenche a data
                campo_data = linha_vazia.locator("input[type='text']").first
                await campo_data.click()
                await campo_data.fill(data_br)
                await campo_data.press("Tab")

                # Preenche o conteúdo
                conteudo_box = linha_vazia.locator("textarea").first
                await conteudo_box.click()
                await conteudo_box.fill(aula["conteudo"])

                # Grava
                gravar = linha_vazia.locator(
                    "button:has-text('Gravar'), input[value*='Gravar' i]"
                ).first
                await gravar.click()
                # espera a página estabilizar após o reload do portal
                try:
                    await page.wait_for_load_state("networkidle", timeout=12000)
                except Exception:
                    pass
                await page.wait_for_timeout(5000)

                preenchidas += 1
                log.append(f"✏️ {data_br} — {aula['conteudo'][:50]}")

            log.append(f"📊 {preenchidas} aulas gravadas nesta turma")

        # ---- 3. Processa turma(s), uma por vez ----
        turmas_feitas = 0
        teve_erro = False
        for idx in range(total_turmas):
            # Volta para a lista de turmas
            await page.goto(url_lista_turmas)
            await page.wait_for_timeout(800)
            fr_check, _ = await achar("a:has-text('Diário de classe')")
            if fr_check is None:
                _, exibir2 = await achar("button:has-text('EXIBIR'), input[value*='EXIBIR' i]")
                if exibir2:
                    await exibir2.click()
                    await page.wait_for_timeout(800)
                fr_check, _ = await achar("a:has-text('Diário de classe')")
            if fr_check is None:
                log.append(f"⚠️ Não consegui voltar à lista de turmas")
                teve_erro = True
                break

            # Identifica o nome da turma (para o log e para o filtro)
            bloco_texto = await fr_check.locator("a:has-text('Diário de classe')").nth(idx).evaluate(
                # Sobe do link até o primeiro bloco que tenha MAIS texto que o
                # próprio link (ou seja, que inclua o título da turma: "3ª série..."),
                # mas para antes de abraçar a página inteira (vários links de diário).
                "el => {"
                "  let q = el.parentElement;"
                "  for (let i = 0; i < 10 && q; i++) {"
                "    const t = (q.innerText || '').trim();"
                "    const qtdLinks = q.querySelectorAll ? q.querySelectorAll('a').length : 99;"
                "    const temMais = t.replace(/\\s+/g,' ').length > 30;"
                "    const soUmaTurma = (t.match(/Diário de classe/g) || []).length <= 1;"
                "    if (temMais && soUmaTurma) {"
                "      const proximo = q.parentElement;"
                "      const tProx = proximo ? (proximo.innerText || '') : '';"
                "      if ((tProx.match(/Diário de classe/g) || []).length > 1 || !proximo) {"
                "        return t.slice(0, 500);"
                "      }"
                "    }"
                "    q = q.parentElement;"
                "  }"
                "  return (el.closest('tr')?.innerText || el.innerText || '').slice(0, 500);"
                "}"
            )
            nome_turma = " ".join((bloco_texto or "").split())[:80] or f"Turma {idx + 1}"

            # Se o professor escolheu uma turma específica, pula as outras
            if data.turma:
                # Normaliza: minúsculas, sem º/°/ª, sem espaços, sem acentos
                def norm(s):
                    import unicodedata
                    s = s.lower().replace("º", "").replace("°", "").replace("ª", "").replace(" ", "").replace("/", "")
                    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii")
                if norm(data.turma) not in norm(bloco_texto or ""):
                    log.append(f"⏭️ '{nome_turma}' não é '{data.turma}' — pulando")
                    continue

            log.append(f"➡️ Turma {idx + 1} de {total_turmas}: {nome_turma}")
            try:
                await preencher_turma(idx)
                turmas_feitas += 1
            except Exception as e:
                log.append(f"⚠️ Erro na turma {idx + 1}: {e}")
                teve_erro = True

        if turmas_feitas > 0 and not teve_erro:
            log.append(f"🎉 Automação concluída! Turmas preenchidas: {turmas_feitas}")
            log.append("__CONCLUIDO__")
        elif turmas_feitas > 0:
            log.append(f"⚠️ Concluído com avisos. Turmas preenchidas: {turmas_feitas}")
            log.append("__CONCLUIDO__")
        else:
            log.append("❌ Nenhuma turma foi preenchida. Veja os erros acima.")
            log.append("__ERRO__")
        await browser.close()


# ---- Manchetes ao vivo (RSS do G1) para a tela de espera ----
_manchetes_cache: dict = {"quando": 0.0, "itens": []}

FEEDS_RSS = [
    ("📰", "https://g1.globo.com/rss/g1/"),
    ("⚽", "https://ge.globo.com/rss/ge/"),
    ("🏛️", "https://g1.globo.com/rss/g1/politica/"),
    ("🎓", "https://g1.globo.com/rss/g1/educacao/"),
]


def _buscar_manchetes() -> list[str]:
    import urllib.request
    import html as _html
    itens = []
    for emoji, url in FEEDS_RSS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml = resp.read().decode("utf-8", errors="ignore")
            # Pega só títulos de DENTRO dos <item> (notícias), nunca o nome do canal
            blocos = re.findall(r"<item>(.*?)</item>", xml, re.DOTALL)
            for bloco in blocos[:5]:
                m = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", bloco, re.DOTALL)
                if not m:
                    continue
                t = _html.unescape(m.group(1)).strip()
                if t and len(t) < 160:
                    itens.append(f"{emoji} {t}")
        except Exception:
            continue
    return itens


class ActiveNotasFormData(BaseModel):
    url_colegio: str = "https://siga.activesoft.com.br/login/"
    usuario: str
    senha: str
    turma: str = ""        # ex: "8A", "8B" — vazio = todas
    fase: str = ""         # ex: "AV3", "2ª Unidade" — vazio = não filtra
    media_minima: float = 7.0
    nota_alta: str = "5,0"
    nota_baixa: str = "4,0"
    nota_excecao: str = "3,0"
    excecoes: list[str] = []   # trechos do nome (minúsculo sem acento)
    pular_preenchidas: bool = True


async def run_active_notas(job_id: str, data: ActiveNotasFormData):
    import unicodedata
    from playwright.async_api import async_playwright

    log = jobs[job_id]

    def sem_acento(s: str) -> str:
        return "".join(
            c for c in unicodedata.normalize("NFD", s)
            if unicodedata.category(c) != "Mn"
        ).lower()

    def para_num(txt: str):
        try:
            return float((txt or "").strip().replace(",", "."))
        except ValueError:
            return None

    excecoes_norm = [sem_acento(e) for e in data.excecoes]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote","--disable-extensions","--disable-images"])
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        # ── LOGIN ──────────────────────────────────────────────────────────────
        log.append("🔐 Fazendo login no ActiveSoft...")
        try:
            await page.goto(data.url_colegio)
            await page.wait_for_timeout(3000)
            await page.locator(
                "input[name='login'], input[name='usuario'], input[type='text']"
            ).first.fill(data.usuario)
            await page.locator("input[type='password']").first.fill(data.senha)
            await page.locator(
                "button[type='submit'], input[type='submit'], "
                "button:has-text('Entrar'), button:has-text('Acessar')"
            ).first.click()
            await page.wait_for_timeout(4000)
            log.append(f"✅ Login realizado — {page.url}")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        async def achar(seletor, tentativas=10):
            for _ in range(tentativas):
                for frame in page.frames:
                    try:
                        loc = frame.locator(seletor)
                        if await loc.count() > 0:
                            return frame, loc.first
                    except Exception:
                        continue
                await page.wait_for_timeout(1500)
            return None, None

        # ── NAVEGA PARA DIGITAÇÃO DE NOTAS ─────────────────────────────────────
        log.append("🔢 Abrindo Digitação de notas...")
        frame_menu, link_notas = await achar(
            "a:has-text('Digitação de notas'), a:has-text('Notas')"
        )
        if link_notas is None:
            log.append("❌ Link 'Digitação de notas' não encontrado")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return
        await link_notas.click()
        await page.wait_for_timeout(3000)

        # ── CLICA EM EXIBIR (filtro de período) ────────────────────────────────
        _, exibir = await achar(
            "button:has-text('EXIBIR'), input[value*='EXIBIR' i]"
        )
        if exibir:
            await exibir.click()
            await page.wait_for_timeout(2000)

        # ── ENCONTRA AS TURMAS ─────────────────────────────────────────────────
        url_lista = page.url
        frame_lista, _ = await achar("a:has-text('Digitação de notas')")
        if frame_lista is None:
            log.append("❌ Lista de turmas não encontrada")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        links_turmas = frame_lista.locator("a:has-text('Digitação de notas')")
        total_turmas = await links_turmas.count()
        log.append(f"📚 Turmas encontradas: {total_turmas}")

        def norm(s):
            return sem_acento(s).replace("º", "").replace("ª", "").replace(" ", "").replace("/", "")

        for idx in range(total_turmas):
            await page.goto(url_lista)
            await page.wait_for_timeout(2000)

            fr, _ = await achar("a:has-text('Digitação de notas')")
            if fr is None:
                _, exibir2 = await achar("button:has-text('EXIBIR'), input[value*='EXIBIR' i]")
                if exibir2:
                    await exibir2.click()
                    await page.wait_for_timeout(2000)
                fr, _ = await achar("a:has-text('Digitação de notas')")
            if fr is None:
                log.append("⚠️ Não consegui voltar à lista de turmas")
                break

            # filtra por turma se informado
            if data.turma:
                bloco = await fr.locator(
                    "a:has-text('Digitação de notas')"
                ).nth(idx).evaluate(
                    "el => { let q=el, s=''; for(let i=0;i<10&&q;i++){"
                    "const t=q.innerText||''; if(t.length>s.length&&t.length<2000)s=t;"
                    "q=q.parentElement;} return s.slice(0,500); }"
                )
                if norm(data.turma) not in norm(bloco or ""):
                    log.append(f"⏭️ Turma {idx + 1} não é '{data.turma}' — pulando")
                    continue

            log.append(f"➡️ Turma {idx + 1} de {total_turmas}...")
            await fr.locator("a:has-text('Digitação de notas')").nth(idx).click()
            await page.wait_for_timeout(3000)

            # ── SELECIONA FASE/UNIDADE ─────────────────────────────────────────
            if data.fase:
                log.append(f"🗓️ Selecionando fase '{data.fase}'...")
                fr_fase, select_fase = await achar(
                    "select, select[name*='fase' i], select[name*='unidade' i], "
                    "select[name*='periodo' i]"
                )
                if select_fase is not None:
                    await select_fase.select_option(label=data.fase)
                    await page.wait_for_timeout(1500)
                else:
                    log.append("⚠️ Dropdown de fase não encontrado — continuando sem filtrar fase")

            # ── CLICA EM CONSULTAR ─────────────────────────────────────────────
            _, consultar = await achar(
                "input[value*='CONSULTAR' i], button:has-text('CONSULTAR'), "
                "input[value*='Consultar' i], button:has-text('Consultar')"
            )
            if consultar:
                await consultar.click()
                await page.wait_for_timeout(3000)
            else:
                log.append("⚠️ Botão CONSULTAR não encontrado — continuando mesmo assim")

            # ── PREENCHE AS NOTAS ──────────────────────────────────────────────
            SEL_INPUT = (
                "input:not([readonly]):not([disabled])"
                ":not([type='hidden']):not([type='checkbox'])"
                ":not([type='button']):not([type='submit'])"
                ":not([type='radio'])"
            )
            frame_notas = None
            for frame in page.frames:
                try:
                    if await frame.locator(f"tr:has({SEL_INPUT})").count() > 0:
                        frame_notas = frame
                        break
                except Exception:
                    continue

            if frame_notas is None:
                log.append("⚠️ Tabela de notas não encontrada nesta turma")
                continue

            linhas = frame_notas.locator(f"tr:has({SEL_INPUT})")
            total_alunos = await linhas.count()
            log.append(f"👥 Alunos encontrados: {total_alunos}")

            preenchidos = 0
            pulados = 0
            for i in range(total_alunos):
                linha = linhas.nth(i)
                try:
                    texto = sem_acento(await linha.inner_text())
                    inputs = linha.locator(SEL_INPUT)
                    n_inputs = await inputs.count()
                    if n_inputs == 0:
                        continue

                    valores = [(await inputs.nth(k).input_value()).strip() for k in range(n_inputs)]
                    vazios = [k for k, v in enumerate(valores) if not v]
                    preenchidos_idx = [k for k, v in enumerate(valores) if v]

                    if not vazios:
                        pulados += 1
                        continue

                    campo_av = inputs.nth(vazios[-1])

                    if any(e in texto for e in excecoes_norm):
                        nota = data.nota_excecao
                        motivo = "exceção"
                    else:
                        notas_existentes = [para_num(valores[k]) for k in preenchidos_idx]
                        notas_existentes = [n for n in notas_existentes if n is not None]
                        if len(notas_existentes) < 2:
                            nota = data.nota_baixa
                            motivo = "AV1/AV2 em branco"
                        else:
                            media = sum(notas_existentes[:2]) / 2
                            nota = data.nota_alta if media >= data.media_minima else data.nota_baixa
                            motivo = f"média {media:.1f}".replace(".", ",")

                    await campo_av.scroll_into_view_if_needed()
                    await campo_av.click()
                    await campo_av.fill(nota)
                    await campo_av.press("Tab")
                    await page.wait_for_timeout(600)
                    preenchidos += 1
                    nome = " ".join(texto.split()[1:4]).title()
                    log.append(f"  [{i + 1}/{total_alunos}] {nome}: {nota} ({motivo})")
                except Exception as e:
                    log.append(f"  [{i + 1}/{total_alunos}] ERRO: {e}")

            log.append(f"📊 Turma {idx + 1}: {preenchidos} notas lançadas"
                       + (f", {pulados} já tinham nota" if pulados else ""))

        log.append("🎉 Lançamento de notas concluído!")
        log.append("__CONCLUIDO__")
        await browser.close()


@app.get("/versao")
async def versao():
    return {"versao": "2026-06-17.62"}


@app.post("/ler-foto-notas")
async def ler_foto_notas(foto: UploadFile = File(...)):
    import base64, urllib.request, urllib.error

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        try:
            caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chave.txt")
            with open(caminho, encoding="utf-8") as f:
                api_key = f.read().strip()
        except FileNotFoundError:
            pass
    if not api_key:
        return {"erro": "Chave da API não configurada no servidor."}

    conteudo = await foto.read()
    mime = foto.content_type or "image/jpeg"
    b64 = base64.b64encode(conteudo).decode("utf-8")

    prompt = (
        "Esta imagem contém uma lista de notas de alunos. "
        "Leia TODOS os nomes e suas respectivas notas. "
        "Retorne APENAS no formato: NOME DO ALUNO: nota (uma por linha). "
        "Use o nome completo em maiúsculas. Exemplo:\n"
        "JOAO SILVA: 8,5\n"
        "MARIA SOUZA: 7,0\n"
        "Não adicione nenhum texto extra, só a lista."
    )

    MODELOS = ["gemini-2.0-flash", "gemini-2.5-flash-lite", "gemini-2.5-flash"]
    ultimo_erro = None
    for modelo in MODELOS:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{modelo}:generateContent?key={api_key}"
        )
        body = json.dumps({
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime, "data": b64}}
                ]
            }]
        }).encode("utf-8")
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resultado = json.loads(resp.read().decode("utf-8"))
            texto = resultado["candidates"][0]["content"]["parts"][0]["text"].strip()
            return {"texto": texto}
        except urllib.error.HTTPError as e:
            ultimo_erro = e.read().decode("utf-8", errors="ignore")
            if "429" in str(e.code):
                continue
            return {"erro": f"Erro da API: {ultimo_erro[:300]}"}
        except Exception as e:
            ultimo_erro = str(e)
            continue

    return {"erro": f"Falha ao chamar a IA: {ultimo_erro}"}


@app.get("/manchetes")
async def manchetes():
    import time as _t
    agora = _t.time()
    # cache de 10 minutos para não martelar os feeds
    if agora - _manchetes_cache["quando"] > 600 or not _manchetes_cache["itens"]:
        itens = await asyncio.to_thread(_buscar_manchetes)
        if itens:
            _manchetes_cache["itens"] = itens
            _manchetes_cache["quando"] = agora
    return {"manchetes": _manchetes_cache["itens"]}


class GerarTopicosRequest(BaseModel):
    disciplina: str
    serie: str
    assunto: str = ""
    quantidade: int = 30


# Controle simples de uso por IP (anti-abuso)
_geracoes_por_ip: dict[str, int] = {}
LIMITE_GERACOES = 5


@app.post("/gerar-topicos")
async def gerar_topicos(req: GerarTopicosRequest):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        # Tenta ler do arquivo chave.txt na mesma pasta
        try:
            caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chave.txt")
            with open(caminho, encoding="utf-8") as f:
                api_key = f.read().strip()
        except FileNotFoundError:
            pass
    if not api_key:
        return {
            "erro": "IA não configurada ainda. Cole sua lista de tópicos manualmente, "
                    "ou peça ao administrador para configurar a chave da API."
        }

    assunto_txt = f" sobre o assunto '{req.assunto}'" if req.assunto else ""
    prompt = (
        f"Crie exatamente {req.quantidade} tópicos de aula de {req.disciplina} "
        f"para a turma '{req.serie}'{assunto_txt}, em sequência didática lógica "
        f"(do mais básico ao mais avançado), adequados ao currículo brasileiro (BNCC). "
        f"Inclua aulas de exercícios e revisão distribuídas naturalmente. "
        f"Responda APENAS com a lista, um tópico por linha, sem numeração e sem texto extra."
    )

    try:
        import urllib.request
        import urllib.error

        if api_key.startswith("sk-ant"):
            # API do Claude (Anthropic)
            url = "https://api.anthropic.com/v1/messages"
            body = json.dumps({
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 3000,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }
        else:
            # API do Gemini (Google) — tenta vários modelos gratuitos
            # (cada um tem cota diária própria; se um esgotar, usa o próximo)
            body = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}]
            }).encode("utf-8")
            headers = {"Content-Type": "application/json"}
            url = None  # definido no loop de modelos abaixo

        def chamar(url_chamada):
            reqobj = urllib.request.Request(url_chamada, data=body, headers=headers)
            try:
                with urllib.request.urlopen(reqobj, timeout=60) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                detalhe = e.read().decode("utf-8", errors="ignore")
                raise RuntimeError(f"HTTP {e.code}: {detalhe[:600]}")

        if api_key.startswith("sk-ant"):
            resultado = await asyncio.to_thread(chamar, url)
        else:
            MODELOS_GEMINI = [
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.5-flash",
            ]
            resultado = None
            ultimo_erro = None
            for modelo in MODELOS_GEMINI:
                url_m = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{modelo}:generateContent?key={api_key}"
                )
                try:
                    resultado = await asyncio.to_thread(chamar, url_m)
                    break
                except RuntimeError as e:
                    ultimo_erro = e
                    if "429" in str(e):
                        continue  # cota esgotada nesse modelo — tenta o próximo
                    raise
            if resultado is None:
                raise RuntimeError(
                    "Cota diária gratuita do Gemini esgotada em todos os modelos. "
                    f"Tente novamente amanhã ou cole sua lista de tópicos manualmente. ({ultimo_erro})"
                )

        if api_key.startswith("sk-ant"):
            texto = resultado["content"][0]["text"]
        else:
            texto = resultado["candidates"][0]["content"]["parts"][0]["text"]

        topicos = [l.strip().lstrip("-•*").strip() for l in texto.split("\n") if l.strip()]
        return {"topicos": topicos}

    except Exception as e:
        return {"erro": f"Falha ao gerar tópicos: {e}"}


class SesiFormData(BaseModel):
    url_portal: str = ""
    usuario: str
    senha: str
    turma: str = ""
    bimestre: str = "1"
    licao_casa: str = ""
    # horários por dia da semana: {"1": [2,3]} = segunda, 2ª e 3ª aulas
    horarios: dict[str, list[int]] = {}
    topicos: list[str] = []


URL_SESI = "https://portaleducacional.fies.org.br/Corpore.Net/Login.aspx"


async def run_sesi(job_id: str, data: SesiFormData):
    from playwright.async_api import async_playwright

    log = jobs[job_id]
    topicos = [t for t in data.topicos if t.strip()]
    log.append(f"📊 Tópicos a lançar: {len(topicos)}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote","--disable-extensions","--disable-images"])
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        async def achar(seletor, tentativas=10):
            for _ in range(tentativas):
                for frame in page.frames:
                    try:
                        loc = frame.locator(seletor)
                        if await loc.count() > 0:
                            return frame, loc.first
                    except Exception:
                        continue
                await page.wait_for_timeout(800)
            return None, None

        def norm(s):
            import unicodedata
            s = (s or "").lower().replace("º", "").replace("°", "").replace("ª", "").replace(" ", "").replace("/", "")
            return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii")

        # ---- 1. Login ----
        log.append("🔐 Fazendo login no Portal Educacional (Totvs/Corpore.Net)...")
        try:
            await page.goto(data.url_portal or URL_SESI)
            await page.wait_for_timeout(1500)
            await page.locator("input[type='text']:visible").first.fill(data.usuario)
            await page.locator("input[type='password']:visible").first.fill(data.senha)
            await page.locator(
                "input[type='submit'], button[type='submit'], input[value*='Acessar' i], button:has-text('Acessar')"
            ).first.click()
            try:
                await page.wait_for_url(lambda url: "login" not in url.lower(), timeout=15000)
            except Exception:
                pass
            if "login" in page.url.lower():
                msg_erro = ""
                try:
                    msg_erro = await page.evaluate(
                        "() => Array.from(document.querySelectorAll('.alert, [class*=error], [id*=lblMsg], span[style*=red]'))"
                        ".map(e => e.innerText.trim()).filter(t => t).join(' | ')"
                    )
                except Exception:
                    pass
                log.append("❌ ERRO: o login não foi aceito.")
                if msg_erro:
                    log.append(f"📢 Mensagem do site: {msg_erro}")
                log.append("__ERRO__")
                log.append("__CONCLUIDO__")
                await browser.close()
                return
            log.append("✅ Login realizado")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        # ---- 2. Diário de classe ----
        fr_d, diario = await achar("a:has-text('Diário de classe')", tentativas=15)
        if not diario:
            log.append("❌ ERRO: link 'Diário de classe' não encontrado após o login")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return
        await diario.click()
        log.append("📋 Abrindo Diário de classe...")

        # ---- 3. Seleciona a turma (radio) ----
        # Os grupos podem precisar ser expandidos antes de mostrar as turmas
        fr_t, _ = await achar("input[type='radio']", tentativas=15)
        if fr_t is None:
            log.append("❌ ERRO: lista de turmas não apareceu")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        async def selecionar_turma():
            """Procura o radio cuja linha contenha o texto da turma."""
            for frame in page.frames:
                try:
                    radios = frame.locator("input[type='radio']")
                    qtd = await radios.count()
                    for i in range(qtd):
                        r = radios.nth(i)
                        texto = await r.evaluate(
                            "el => (el.closest('tr')?.innerText || el.parentElement?.innerText || '')"
                        )
                        if norm(data.turma) in norm(texto):
                            await r.click()
                            return texto.strip()[:80]
                except Exception:
                    continue
            return None

        achou = await selecionar_turma()
        if not achou and data.turma:
            # Tenta expandir os grupos (cabeçalhos com o ano letivo) e procurar de novo
            log.append("🔍 Expandindo grupos de turmas...")
            for frame in page.frames:
                try:
                    grupos = frame.locator("tr:has-text('2026'), div:has-text('2026'), td:has-text('ENSINO')")
                    qtd = min(await grupos.count(), 10)
                    for i in range(qtd):
                        try:
                            await grupos.nth(i).click()
                            await page.wait_for_timeout(500)
                        except Exception:
                            continue
                except Exception:
                    continue
            achou = await selecionar_turma()

        if not achou:
            if data.turma:
                log.append(f"❌ ERRO: turma '{data.turma}' não encontrada na lista")
            else:
                log.append("❌ ERRO: informe a turma (ex: 6C) — o SESI exige escolher uma")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return
        log.append(f"✅ Turma selecionada: {achou}")
        await page.wait_for_timeout(800)

        # ---- 4. Plano de aula ----
        _, plano = await achar(
            "input[value*='Plano de aula' i], button:has-text('Plano de aula'), a:has-text('Plano de aula')",
            tentativas=10,
        )
        if not plano:
            log.append("❌ ERRO: botão 'Plano de aula' não encontrado")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return
        await plano.click()
        log.append("📑 Abrindo Plano de aula...")
        await page.wait_for_timeout(1500)

        # ---- 5. Seleciona a etapa (bimestre) ----
        try:
            bim_num = int(str(data.bimestre).strip())
        except ValueError:
            bim_num = 1

        etapa_ok = False
        # Tenta primeiro um <select> nativo com as etapas
        for frame in page.frames:
            try:
                selects = frame.locator("select")
                qtd = await selects.count()
                for i in range(qtd):
                    sel = selects.nth(i)
                    opcoes = await sel.evaluate(
                        "el => Array.from(el.options).map(o => o.text)"
                    )
                    if not any("bimestre" in (o or "").lower() for o in opcoes):
                        continue
                    # Acha a opção do bimestre pedido (1º Bimestre, ou a 2ª da lista...)
                    alvo = None
                    for o in opcoes:
                        if f"{bim_num}º" in o or f"{bim_num}°" in o:
                            alvo = o
                            break
                    if alvo is None:
                        # rótulos sem número (ex: "Faltas do Bimestre" = 2º): usa a posição
                        bims = [o for o in opcoes if "bimestre" in (o or "").lower()]
                        if len(bims) >= bim_num:
                            alvo = bims[bim_num - 1]
                    if alvo:
                        await sel.select_option(label=alvo)
                        log.append(f"📑 Etapa selecionada: {alvo}")
                        etapa_ok = True
                        break
                if etapa_ok:
                    break
            except Exception:
                continue

        if not etapa_ok:
            # Combo da Totvs que abre uma gradezinha: clica e escolhe a linha
            fr_c, combo = await achar("input[id*='Etapa' i], select[id*='Etapa' i], [id*='etapa' i]", tentativas=5)
            if combo:
                try:
                    await combo.click()
                    await page.wait_for_timeout(800)
                    fr_l, linha = await achar(f"tr:has-text('{bim_num}º Bimestre')", tentativas=3)
                    if linha is None and bim_num == 2:
                        fr_l, linha = await achar("tr:has-text('Faltas do Bimestre')", tentativas=3)
                    if linha:
                        await linha.click()
                        log.append(f"📑 Etapa do {bim_num}º bimestre selecionada")
                        etapa_ok = True
                except Exception:
                    pass
        if not etapa_ok:
            log.append("⚠️ Não consegui selecionar a etapa — tentando seguir com a etapa padrão")

        # ---- 6. Botão Selecionar ----
        _, btn_sel = await achar(
            "input[value='Selecionar'], button:has-text('Selecionar')", tentativas=8
        )
        if btn_sel:
            await btn_sel.click()
            log.append("✅ Lista de aulas carregada")
            await page.wait_for_timeout(1500)

        # ---- 7. Preenche as aulas vazias ----
        from datetime import datetime as _dt

        def periodo_da_aula(data_br: str, ja_usadas_na_data: int):
            """Retorna o nº da aula (1-6) que o professor dá nesse dia da semana.
            Se ele tem 2 aulas no dia, a 1ª linha vazia usa a primeira, a 2ª usa a segunda."""
            try:
                dt = _dt.strptime(data_br.strip()[:10], "%d/%m/%Y")
            except ValueError:
                return None
            dia_semana = str(dt.isoweekday())  # 1=segunda ... 5=sexta
            lista = data.horarios.get(dia_semana) or []
            if not lista:
                return None
            return lista[min(ja_usadas_na_data, len(lista) - 1)]

        usos_por_data: dict[str, int] = {}
        preenchidas = 0
        idx_topico = 0
        while idx_topico < len(topicos):
            # Localiza o frame da tabela de aulas e a primeira linha sem conteúdo realizado
            alvo_info = None
            fr_tab = None
            for frame in page.frames:
                try:
                    info = await frame.evaluate(
                        """() => {
                            const tabelas = document.querySelectorAll('table');
                            for (const t of tabelas) {
                                const ths = Array.from(t.querySelectorAll('th, td'))
                                    .map(c => (c.innerText || '').trim());
                                if (!ths.some(x => x.includes('Conteúdo realizado'))) continue;
                                // achou a tabela de aulas
                                const linhas = Array.from(t.querySelectorAll('tr'));
                                // identifica o índice da coluna pelo cabeçalho
                                let header = null;
                                for (const tr of linhas) {
                                    const cels = Array.from(tr.children).map(c => (c.innerText || '').trim());
                                    if (cels.some(x => x === 'Conteúdo realizado')) { header = cels; break; }
                                }
                                if (!header) continue;
                                const colReal = header.indexOf('Conteúdo realizado');
                                const colData = header.indexOf('Data');
                                const colIni = header.indexOf('Início');
                                let i = -1;
                                for (const tr of linhas) {
                                    i++;
                                    const btn = tr.querySelector("input[value='Editar'], button");
                                    if (!btn) continue;
                                    const cels = Array.from(tr.children).map(c => (c.innerText || '').trim());
                                    if (cels.length <= colReal) continue;
                                    if ((cels[colReal] || '').trim() === '') {
                                        return {
                                            linha: i,
                                            data: colData >= 0 ? cels[colData] : '',
                                            inicio: colIni >= 0 ? cels[colIni] : ''
                                        };
                                    }
                                }
                                return { linha: -1 };
                            }
                            return null;
                        }"""
                    )
                    if info is not None:
                        fr_tab = frame
                        alvo_info = info
                        break
                except Exception:
                    continue

            if fr_tab is None:
                log.append("❌ ERRO: tabela de aulas não encontrada")
                break
            if alvo_info["linha"] < 0:
                log.append("✅ Nenhuma aula em branco restante — tudo preenchido!")
                break

            # Clica no Editar da linha vazia
            try:
                linha_loc = fr_tab.locator("table tr").nth(alvo_info["linha"])
                await linha_loc.locator("input[value='Editar'], button:has-text('Editar')").first.click()
            except Exception as e:
                log.append(f"⚠️ Erro ao abrir a aula: {e}")
                break

            # Popup Incluir/Editar registro: Conteúdo (3º textarea) + Lição de Casa (4º)
            fr_pop, _ = await achar("textarea", tentativas=10)
            if fr_pop is None:
                log.append("⚠️ Popup de edição não abriu")
                break
            await page.wait_for_timeout(500)
            try:
                areas = fr_pop.locator("textarea")
                qtd_areas = await areas.count()
                # Ordem observada: Conteúdo Previsto, Aula Online, Conteúdo, Lição de Casa, Observação
                idx_conteudo = 2 if qtd_areas >= 4 else max(qtd_areas - 2, 0)
                await areas.nth(idx_conteudo).fill(topicos[idx_topico])

                # Seleciona o horário da aula:
                # 1º tenta o horário que o professor informou para esse dia da semana;
                # 2º (fallback) usa o horário de início da própria linha, se existir
                data_linha = (alvo_info.get("data") or "").strip()
                periodo = periodo_da_aula(data_linha, usos_por_data.get(data_linha, 0))
                hora_ini = (alvo_info.get("inicio") or "").strip()
                horario_ok = False
                try:
                    sels = fr_pop.locator("select")
                    for i_s in range(await sels.count()):
                        s = sels.nth(i_s)
                        opcoes = await s.evaluate("el => Array.from(el.options).map(o => o.text)")
                        if not opcoes or len(opcoes) < 2:
                            continue
                        alvo_op = None
                        if periodo is not None:
                            # opções no formato "VESPERTINO - 2 - 13:50/14:40"
                            alvo_op = next(
                                (o for o in opcoes if f"- {periodo} -" in (o or "") or f"-{periodo}-" in (o or "").replace(" ", "")),
                                None,
                            )
                        if alvo_op is None and hora_ini:
                            alvo_op = next((o for o in opcoes if hora_ini in (o or "")), None)
                        if alvo_op:
                            await s.select_option(label=alvo_op)
                            horario_ok = True
                            break
                except Exception:
                    pass
                if not horario_ok and (periodo is not None or hora_ini):
                    # Combo em grade da Totvs: abre e clica na linha correspondente
                    try:
                        _, combo_h = await achar("input[id*='Horario' i], [id*='horario' i]", tentativas=2)
                        if combo_h:
                            await combo_h.click()
                            await page.wait_for_timeout(600)
                            linha_h = None
                            if hora_ini:
                                _, linha_h = await achar(f"tr:has-text('{hora_ini}')", tentativas=2)
                            if linha_h is None and periodo is not None:
                                # coluna "Dia"/posição: clica na linha cujo nº da aula bate
                                fr_g, grade = await achar("tr:has(td)", tentativas=2)
                                if fr_g:
                                    linhas_g = fr_g.locator("tr:has(td)")
                                    if await linhas_g.count() >= periodo:
                                        linha_h = linhas_g.nth(periodo - 1)
                            if linha_h:
                                await linha_h.click()
                                horario_ok = True
                    except Exception:
                        pass
                if not horario_ok:
                    log.append("⚠️ Horário não selecionado automaticamente — confira essa aula depois")
                if data_linha:
                    usos_por_data[data_linha] = usos_por_data.get(data_linha, 0) + 1
                if data.licao_casa and qtd_areas > idx_conteudo + 1:
                    await areas.nth(idx_conteudo + 1).fill(data.licao_casa)
                _, salvar = await achar("input[value='Salvar'], button:has-text('Salvar')", tentativas=5)
                if salvar:
                    await salvar.click()
                else:
                    raise RuntimeError("botão Salvar não encontrado no popup")
                await page.wait_for_timeout(1200)
                preenchidas += 1
                log.append(f"✏️ {alvo_info.get('data', '')} — {topicos[idx_topico][:50]}")
                idx_topico += 1
            except Exception as e:
                log.append(f"⚠️ Erro ao preencher: {e}")
                break

        log.append(f"📊 {preenchidas} aulas gravadas")
        log.append("🏁 Automação SESI finalizada!")
        log.append("__CONCLUIDO__")
        await browser.close()


class SalesianoFormData(BaseModel):
    url_portal: str = "https://portalprdsalesianos.rm.cloudtotvs.com.br/FrameHTML/web/app/edu/PortalDoProfessor/#/login"
    url_plano: str  # URL direta do plano de aula da turma (com #/portal/class/lessonPlan/...)
    usuario: str
    senha: str
    aula_inicio: int = 1
    duplas: bool = False
    topicos: list[str] = []


async def run_salesiano(job_id: str, data: SalesianoFormData):  # noqa: C901
    from playwright.async_api import async_playwright

    log = jobs[job_id]
    topicos = [t for t in data.topicos if t.strip()]
    log.append(f"📊 Tópicos a lançar: {len(topicos)}")

    def topico_da_aula(n: int) -> str | None:
        idx = n // 2 if data.duplas else n
        return topicos[idx] if idx < len(topicos) else None

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote","--disable-extensions","--disable-images"])
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        # ── LOGIN ──────────────────────────────────────────────────────────────
        log.append("🔐 Fazendo login no Portal do Professor...")
        try:
            await page.goto(data.url_portal)
            try:
                await page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                pass
            await page.wait_for_timeout(2000)

            senha_input = page.locator("input[type='password']").first
            if await senha_input.count() > 0 and await senha_input.is_visible():
                user_input = page.locator(
                    "input[name='login'], input[name='user' i], "
                    "input[name='username' i], input[type='text']"
                ).first
                # preenche via JS para o Angular registrar o valor
                await page.evaluate("""([sel_u, sel_p, u, p]) => {
                    const set = (sel, val) => {
                        const el = document.querySelector(sel);
                        if (!el) return;
                        Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value'
                        ).set.call(el, val);
                        el.dispatchEvent(new Event('input',  {bubbles:true}));
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                    };
                    set(sel_u, u); set(sel_p, p);
                }""", ["input[type='text']", "input[type='password']",
                       data.usuario, data.senha])
                # digita também para acionar validadores Angular
                await user_input.click()
                await user_input.type(data.usuario, delay=60)
                await senha_input.click()
                await senha_input.type(data.senha, delay=60)
                await page.wait_for_timeout(600)

                botao = page.locator(
                    "button:has-text('Entrar'), button[type='submit'], "
                    "button:has-text('Acessar'), input[type='submit']"
                ).first
                if await botao.count() > 0:
                    await botao.click()
                else:
                    await senha_input.press("Enter")

                # aguarda menu aparecer E URL sair do login (até 40s)
                logado = False
                for _ in range(40):
                    await page.wait_for_timeout(1000)
                    tem_menu = await page.locator(".po-menu-item, po-menu").count() > 0
                    if tem_menu and "login" not in page.url.lower():
                        logado = True
                        break

                if not logado:
                    avisos = await page.evaluate(
                        """() => Array.from(document.querySelectorAll(
                            'po-toaster,.po-toaster,[class*=error i],[role=alert]'
                        )).map(e=>e.innerText.trim()).filter(t=>t).slice(0,5)"""
                    )
                    for a in avisos:
                        log.append("🧭 aviso: " + a)
                    log.append("🧭 URL: " + page.url)
                    log.append("🧭 página: " + await page.evaluate(
                        "() => document.body.innerText.trim().slice(0,300)"
                    ))
                    raise RuntimeError("portal não abriu após login — veja linhas 🧭 acima")

            log.append("✅ Login realizado — " + page.url)
            await page.wait_for_timeout(1500)

            # ── NAVEGA AO PLANO VIA HASH (não recarrega o app Angular) ─────────
            hash_part = data.url_plano.split('#')[-1] if '#' in data.url_plano else ''
            if hash_part:
                log.append("🔀 Navegando ao plano de aula via hash...")
                await page.evaluate(f"() => {{ window.location.hash = '{hash_part}'; }}")
            else:
                await page.goto(data.url_plano)

        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        # ── AGUARDA TABELA ──────────────────────────────────────────────────────
        log.append("⏳ Aguardando tabela de aulas carregar...")
        total = 0
        for _ in range(60):
            await page.wait_for_timeout(1000)
            total = await page.evaluate(
                "() => document.querySelectorAll('table tbody tr, po-table tbody tr').length"
            )
            if total > 0:
                break

        log.append(f"🧭 URL atual: {page.url}")
        if total == 0:
            log.append("🧭 página: " + await page.evaluate(
                "() => document.body.innerText.trim().slice(0,300)"
            ))
            log.append("❌ Tabela de aulas não carregou. Confira o link do plano de aula.")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        log.append(f"📚 {total} aulas encontradas na tabela")

        # ── PREENCHE CADA AULA ─────────────────────────────────────────────────
        preenchidas = 0
        for i in range(total):
            numero_aula = i + 1
            if numero_aula < data.aula_inicio:
                continue
            conteudo = topico_da_aula(preenchidas)
            if conteudo is None:
                log.append("✅ Todos os tópicos foram usados")
                break
            try:
                # fecha qualquer modal aberto antes de clicar na linha
                overlay = page.locator(".po-modal-overlay")
                if await overlay.count() > 0:
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(800)

                btn = page.locator("table tbody tr").nth(i).locator("text=Editar")
                if await btn.count() == 0:
                    log.append(f"⏭️ Aula {numero_aula} sem botão Editar — pulando")
                    continue
                await btn.scroll_into_view_if_needed()
                await btn.click()
                await page.wait_for_timeout(1500)

                # clica em Editar dentro do modal para habilitar o textarea
                editar_modal = page.locator(
                    "po-modal button:has-text('Editar'), "
                    "[role='dialog'] button:has-text('Editar')"
                ).first
                for _ in range(3):
                    try:
                        if await editar_modal.count() > 0 and await editar_modal.is_visible():
                            await editar_modal.click()
                        await page.wait_for_timeout(1000)
                        alvo = page.locator(
                            "po-modal textarea:not([disabled]), "
                            "[role='dialog'] textarea:not([disabled])"
                        ).first
                        await alvo.wait_for(timeout=6000)
                        break
                    except Exception:
                        await page.wait_for_timeout(1500)

                await alvo.click()
                await alvo.fill(conteudo)
                await alvo.dispatch_event("input")
                await alvo.dispatch_event("change")
                await page.wait_for_timeout(400)

                salvar = page.locator(
                    "po-modal button:has-text('Salvar'), "
                    "[role='dialog'] button:has-text('Salvar')"
                ).first
                await salvar.wait_for(timeout=5000)
                await salvar.click()

                # espera o modal fechar
                for _ in range(15):
                    await page.wait_for_timeout(1000)
                    if await overlay.count() == 0:
                        break

                preenchidas += 1
                log.append(f"✏️ Aula {numero_aula} — {conteudo[:50]}")
            except Exception as e:
                log.append(f"⚠️ Erro na aula {numero_aula}: {e}")
                try:
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(800)
                except Exception:
                    pass

        log.append(f"📊 {preenchidas} aulas gravadas")
        log.append("🏁 Automação Salesiano finalizada!")
        if preenchidas == 0 and total > 0:
            log.append("__ERRO__")
        log.append("__CONCLUIDO__")
        await browser.close()


@app.post("/executar-salesiano")
async def executar_salesiano(data: SalesianoFormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_salesiano(job_id, data))
    return {"job_id": job_id}


@app.post("/executar-sesi")
async def executar_sesi(data: SesiFormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_sesi(job_id, data))
    return {"job_id": job_id}


class ActiveFaltasFormData(BaseModel):
    url_colegio: str = "https://siga.activesoft.com.br/login/"
    usuario: str
    senha: str
    turma: str = ""   # vazio = todas as turmas
    bimestre: str = "2"


async def run_active_faltas(job_id: str, data: ActiveFaltasFormData):
    from playwright.async_api import async_playwright

    log = jobs[job_id]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote","--disable-extensions","--disable-images"])
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        # ── LOGIN ──────────────────────────────────────────────────────────────
        log.append("🔐 Fazendo login no ActiveSoft...")
        try:
            await page.goto(data.url_colegio)
            await page.wait_for_timeout(3000)
            await page.locator(
                "input[name='login'], input[name='usuario'], input[type='text']"
            ).first.fill(data.usuario)
            await page.locator("input[type='password']").first.fill(data.senha)
            await page.locator(
                "button[type='submit'], input[type='submit'], "
                "button:has-text('Entrar'), button:has-text('Acessar')"
            ).first.click()
            await page.wait_for_timeout(4000)
            log.append(f"✅ Login realizado — {page.url}")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        async def achar(seletor, tentativas=10):
            for _ in range(tentativas):
                for frame in page.frames:
                    try:
                        loc = frame.locator(seletor)
                        if await loc.count() > 0:
                            return frame, loc.first
                    except Exception:
                        continue
                await page.wait_for_timeout(1500)
            return None, None

        # ── CLICA EM EXIBIR ────────────────────────────────────────────────────
        _, exibir = await achar("button:has-text('EXIBIR'), input[value*='EXIBIR' i]")
        if exibir:
            await exibir.click()
            await page.wait_for_timeout(2000)

        url_lista = page.url
        frame_lista, _ = await achar("a:has-text('Diário de classe')")
        if frame_lista is None:
            log.append("❌ Lista de turmas (Diário de classe) não encontrada")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        total_turmas = await frame_lista.locator("a:has-text('Diário de classe')").count()
        log.append(f"📚 Turmas encontradas: {total_turmas}")

        def norm(s):
            import unicodedata
            s = "".join(c for c in unicodedata.normalize("NFD", s)
                        if unicodedata.category(c) != "Mn").lower()
            return s.replace("º", "").replace("ª", "").replace(" ", "").replace("/", "")

        turmas_feitas = 0
        for idx in range(total_turmas):
            await page.goto(url_lista)
            await page.wait_for_timeout(2500)
            fr, _ = await achar("a:has-text('Diário de classe')")
            if fr is None:
                _, exibir2 = await achar("button:has-text('EXIBIR'), input[value*='EXIBIR' i]")
                if exibir2:
                    await exibir2.click()
                    await page.wait_for_timeout(2000)
                fr, _ = await achar("a:has-text('Diário de classe')")
            if fr is None:
                log.append("⚠️ Não consegui voltar à lista")
                break

            if data.turma:
                bloco = await fr.locator(
                    "a:has-text('Diário de classe')"
                ).nth(idx).evaluate(
                    "el => { let q=el, s=''; for(let i=0;i<10&&q;i++){"
                    "const t=q.innerText||''; if(t.length>s.length&&t.length<2000)s=t;"
                    "q=q.parentElement;} return s.slice(0,500); }"
                )
                if norm(data.turma) not in norm(bloco or ""):
                    log.append(f"⏭️ Turma {idx + 1} não é '{data.turma}' — pulando")
                    continue

            log.append(f"➡️ Turma {idx + 1} de {total_turmas}...")
            await fr.locator("a:has-text('Diário de classe')").nth(idx).click()
            await page.wait_for_timeout(3000)

            # ── ABRE REGISTRO DE AULAS DO BIMESTRE ────────────────────────────
            fr2, _ = await achar(f"tr:has-text('{data.bimestre}º BIMESTRE')")
            if fr2 is None:
                log.append(f"⚠️ Tabela de bimestres não encontrada — pulando turma")
                continue
            linha_bim = fr2.locator(f"tr:has-text('{data.bimestre}º BIMESTRE')").first
            reg = linha_bim.locator("a:has-text('Registro de aulas')").first
            await reg.wait_for(timeout=8000)
            await reg.click()
            await page.wait_for_timeout(3000)

            # ── CLICA NA ABA FREQUÊNCIA ────────────────────────────────────────
            log.append("📋 Abrindo aba Frequência...")
            _, aba_freq = await achar(
                "a:has-text('Frequência'), a:has-text('Frequencia'), "
                "li:has-text('Frequência') a, tab:has-text('Frequência')"
            )
            if aba_freq is None:
                log.append("⚠️ Aba Frequência não encontrada — pulando turma")
                continue
            await aba_freq.click()
            await page.wait_for_timeout(3000)

            # ── CLICA EM P (Presente) EM TODAS AS COLUNAS ─────────────────────
            log.append("✅ Marcando presença em todas as colunas...")
            fr_freq = None
            for frame in page.frames:
                try:
                    if await frame.locator("table th:has-text('P')").count() > 0:
                        fr_freq = frame
                        break
                except Exception:
                    continue

            if fr_freq is None:
                log.append("⚠️ Tabela de frequência não encontrada — pulando turma")
                continue

            colunas_p = fr_freq.locator("table th:has-text('P'), table th input[value='P']")
            total_colunas = await colunas_p.count()
            log.append(f"📊 Colunas de presença: {total_colunas}")

            for col in range(total_colunas):
                try:
                    await colunas_p.nth(col).click()
                    await page.wait_for_timeout(400)
                except Exception as e:
                    log.append(f"⚠️ Erro na coluna {col + 1}: {e}")

            # ── GRAVAR ─────────────────────────────────────────────────────────
            log.append("💾 Gravando frequência...")
            _, gravar = await achar(
                "button:has-text('Gravar'), input[value*='Gravar' i]"
            )
            if gravar:
                await gravar.click()
                await page.wait_for_timeout(4000)
                log.append("✅ Frequência gravada")
            else:
                log.append("⚠️ Botão Gravar não encontrado")
                continue

            # ── PRÓXIMO ────────────────────────────────────────────────────────
            _, proximo = await achar(
                "button:has-text('Próximo'), input[value*='Próximo' i], "
                "button:has-text('Proximo'), a:has-text('Próximo')"
            )
            if proximo:
                await proximo.click()
                await page.wait_for_timeout(3000)
                log.append("➡️ Próximo clicado")

            turmas_feitas += 1

        log.append(f"🎉 Frequência concluída! Turmas processadas: {turmas_feitas}")
        log.append("__CONCLUIDO__")
        await browser.close()


@app.post("/executar-active-faltas")
async def executar_active_faltas(data: ActiveFaltasFormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_active_faltas(job_id, data))
    return {"job_id": job_id}


# ════════════════════════════════════════════════════════════
# INFODAT
# ════════════════════════════════════════════════════════════

class InfodatEntrada(BaseModel):
    data: str           # DD/MM/AAAA
    turma_value: str    # value do <option> no select de curso/disciplina
    num_aulas: str = "2"
    conteudo: str
    ativ_aula: str = ""
    ativ_casa: str = ""


class InfodatFormData(BaseModel):
    escola: str         # value do <option> no select de escola
    professor: str      # texto exato do <option> no select de professor
    senha: str
    entradas: list[InfodatEntrada]
    alunos_falta: list[str] = []  # partes do nome em maiúsculo
    numero: str = ""    # WhatsApp do professor para notificação


INFODAT_BASE = "https://www.sigmawd.com.br/infodat/professor"


async def run_infodat(job_id: str, data: InfodatFormData):
    from playwright.async_api import async_playwright

    log = jobs[job_id]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote","--disable-extensions","--disable-images"])
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()

        # ── LOGIN ────────────────────────────────────────────────────────────
        log.append("🔐 Fazendo login no Infodat...")
        for tentativa_login in range(3):
            try:
                await page.goto(f"{INFODAT_BASE}/login.php", wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(500)
                await page.locator("select#escola").select_option(value=data.escola)
                await page.evaluate(
                    "document.querySelector('select#escola').dispatchEvent(new Event('change'))"
                )
                await page.wait_for_function(
                    "document.querySelector('select#professor').options.length > 1",
                    timeout=20000,
                )
                opcoes = await page.evaluate("""
                    () => Array.from(document.querySelector('select#professor').options)
                        .filter(o => o.value)
                        .map(o => ({value: o.value, text: o.text.trim()}))
                """)
                palavras = _sem_acento(data.professor).split()
                valor_prof = None
                for opt in opcoes:
                    texto = _sem_acento(opt["text"])
                    if all(p in texto for p in palavras):
                        valor_prof = opt["value"]
                        log.append(f"✅ Professor encontrado: {opt['text']}")
                        break
                if valor_prof:
                    await page.locator("select#professor").select_option(value=valor_prof)
                else:
                    log.append(f"⚠️ Professor não encontrado. Opções: {[o['text'] for o in opcoes[:5]]}")
                    await page.locator("select#professor").select_option(index=1)
                await page.evaluate(
                    "document.querySelector('select#professor').dispatchEvent(new Event('change'))"
                )
                await page.wait_for_timeout(1000)
                await page.locator("input[type='password']").first.fill(data.senha)
                await page.wait_for_timeout(500)
                await page.evaluate("document.querySelector('form').submit()")

                for _ in range(120):
                    await page.wait_for_timeout(500)
                    if "login.php" not in page.url:
                        break

                if "login.php" in page.url:
                    if tentativa_login < 2:
                        log.append(f"⚠️ Login falhou, tentando novamente ({tentativa_login + 2}/3)...")
                        await asyncio.sleep(5)
                        continue
                    log.append("❌ Login não aceito após 3 tentativas.")
                    if data.numero:
                        notificacoes.setdefault(data.numero, []).append("❌ Não consegui registrar suas aulas — login falhou 3 vezes. Tente novamente mais tarde.")
                    log.append("__ERRO__")
                    log.append("__CONCLUIDO__")
                    await browser.close()
                    return

                log.append("✅ Login realizado!")
                break
            except Exception as e:
                log.append(f"❌ ERRO no login: {e}")
                if tentativa_login < 2:
                    log.append(f"⚠️ Tentando novamente ({tentativa_login + 2}/3)...")
                    await asyncio.sleep(5)
                    continue
                log.append("__ERRO__")
                log.append("__CONCLUIDO__")
                await browser.close()
                return

        # ── ABRE DIÁRIO ONLINE ────────────────────────────────────────────────
        log.append("📓 Abrindo Diário Online...")
        try:
            await page.locator("a.btn[href='diario.php']").click()
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)
        except Exception as e:
            log.append(f"❌ ERRO ao abrir diário: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        # ── PREENCHE CADA ENTRADA ─────────────────────────────────────────────
        gravadas = 0
        for i, entrada in enumerate(data.entradas, 1):
            url_form = (
                f"{INFODAT_BASE}/diario_add.php"
                f"?c={entrada.turma_value}&d={entrada.data}&f={entrada.num_aulas}"
            )
            log.append(f"⏳ [{i}/{len(data.entradas)}] {entrada.turma_value} | {entrada.data} → {entrada.conteudo[:40]}")
            try:
                await page.goto(url_form, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                campo = page.locator("input[name='conteudo'], input#conteudo")
                if await campo.count() > 0:
                    await campo.first.fill(entrada.conteudo)

                if entrada.ativ_aula:
                    await page.locator("textarea#ativaula").fill(entrada.ativ_aula)

                if entrada.ativ_casa:
                    await page.locator("textarea#ativcasa").fill(entrada.ativ_casa)

                if data.alunos_falta:
                    linhas = page.locator("tr")
                    total = await linhas.count()
                    for j in range(total):
                        tr = linhas.nth(j)
                        tds = tr.locator("td")
                        if await tds.count() < 2:
                            continue
                        try:
                            nome = (await tds.nth(1).inner_text()).strip().upper()
                        except Exception:
                            continue
                        if any(f in nome for f in data.alunos_falta):
                            cb = tr.locator("input[type='checkbox']")
                            if await cb.count() > 0 and not await cb.first.is_checked():
                                await cb.first.check()
                                log.append(f"   ❌ Falta: {nome}")

                await page.locator("button[type='submit'].btn-success").click()
                await page.wait_for_timeout(3000)
                gravadas += 1
                log.append(f"   ✅ Gravado!")
                # Screenshot da confirmação logo após salvar
                try:
                    import os as _os
                    _os.makedirs("/tmp/screenshots", exist_ok=True)
                    shot_path = f"/tmp/screenshots/{job_id}_{i}.png"
                    await page.screenshot(path=shot_path, clip={"x": 0, "y": 0, "width": 1000, "height": 300})
                    log.append(f"   📸 SCREENSHOT:{job_id}_{i}.png")
                except Exception:
                    pass
            except Exception as e:
                log.append(f"   ⚠️ Erro: {e}")

        log.append(f"\n✅ CONCLUÍDO! Aulas gravadas: {gravadas}/{len(data.entradas)}")
        # Screenshot final de confirmação
        try:
            import os as _os
            _os.makedirs("/tmp/screenshots", exist_ok=True)
            shot_final = f"/tmp/screenshots/{job_id}_final.png"
            await page.screenshot(path=shot_final)
            log.append(f"📸 SCREENSHOT:{job_id}_final.png")
            if data.numero:
                notificacoes.setdefault(data.numero, []).append(f"📸 SCREENSHOT:{job_id}_final.png")
        except Exception:
            pass
        if data.numero:
            if gravadas == len(data.entradas):
                notificacoes.setdefault(data.numero, []).append(f"✅ {gravadas} aula(s) registrada(s) com sucesso!")
            else:
                notificacoes.setdefault(data.numero, []).append(f"⚠️ {gravadas} de {len(data.entradas)} aulas registradas. Verifique o sistema.")
        # Salva métrica no Supabase
        try:
            sb = _get_supabase()
            if sb:
                sb.table("metricas_automacoes").insert({
                    "sistema": "infodat",
                    "professor": data.professor,
                    "total": len(data.entradas),
                    "gravadas": gravadas,
                    "sucesso": gravadas == len(data.entradas),
                }).execute()
        except Exception:
            pass
        log.append("__CONCLUIDO__")
        await browser.close()


class InfodatLoginData(BaseModel):
    escola: str
    professor: str
    senha: str
    valor_prof: str | None = None


async def _descobrir_turmas_infodat(escola: str, professor: str, senha: str, valor_prof: str | None = None) -> dict:
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote","--disable-extensions","--disable-images"])
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        try:
            for _ in range(3):
                try:
                    await page.goto(f"{INFODAT_BASE}/login.php",
                                    wait_until="domcontentloaded", timeout=60000)
                    break
                except Exception:
                    await page.wait_for_timeout(5000)

            await page.wait_for_timeout(500)
            await page.locator("select#escola").select_option(value=escola)
            await page.evaluate(
                "document.querySelector('select#escola').dispatchEvent(new Event('change'))"
            )
            await page.wait_for_function(
                "document.querySelector('select#professor').options.length > 1",
                timeout=20000,
            )
            opcoes = await page.evaluate("""
                () => Array.from(document.querySelector('select#professor').options)
                    .filter(o => o.value && o.text.trim())
                    .map(o => ({value: o.value, text: o.text.trim()}))
            """)
            valores_validos = {o["value"] for o in opcoes}
            if valor_prof and valor_prof in valores_validos:
                vp = valor_prof
            else:
                palavras = _sem_acento(professor).split()
                vp = None
                for opt in opcoes:
                    texto = _sem_acento(opt["text"])
                    if all(p in texto for p in palavras):
                        vp = opt["value"]
                        break
                if not vp:
                    nomes = [o["text"] for o in opcoes[:5]]
                    return {"erro": f"Professor não encontrado. Exemplos: {nomes}"}
            await page.locator("select#professor").select_option(value=vp)
            await page.evaluate(
                "document.querySelector('select#professor').dispatchEvent(new Event('change'))"
            )
            await page.wait_for_timeout(1000)
            await page.locator("input[type='password']").first.fill(senha)
            await page.wait_for_timeout(500)
            await page.evaluate("document.querySelector('form').submit()")
            for _ in range(120):
                await page.wait_for_timeout(500)
                if "login.php" not in page.url:
                    break
            if "login.php" in page.url:
                return {"erro": "Login não aceito — verifique professor e senha."}

            await page.goto(f"{INFODAT_BASE}/diario_add.php",
                            wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            turmas = await page.evaluate("""
                () => {
                    const sel = document.querySelector('select#cursoturmadisc');
                    if (!sel) return [];
                    return Array.from(sel.options)
                        .filter(o => o.value)
                        .map(o => ({ value: o.value, label: o.text.trim() }));
                }
            """)
            return {"turmas": turmas, "valor_prof": vp}
        except Exception as e:
            return {"erro": str(e)}
        finally:
            await browser.close()


@app.post("/turmas-infodat")
async def turmas_infodat(data: InfodatLoginData):
    return await _descobrir_turmas_infodat(data.escola, data.professor, data.senha, data.valor_prof)


@app.post("/executar-infodat")
async def executar_infodat(data: InfodatFormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_infodat(job_id, data))
    return {"job_id": job_id}


@app.post("/executar-active-notas")
async def executar_active_notas(data: ActiveNotasFormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_active_notas(job_id, data))
    return {"job_id": job_id}


@app.post("/executar-active")
async def executar_active(data: ActiveFormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_active(job_id, data))
    return {"job_id": job_id}


@app.post("/executar")
async def executar(data: FormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_automacao(job_id, data))
    return {"job_id": job_id}


@app.get("/progresso/{job_id}")
async def progresso(job_id: str, request: Request):
    # Se o navegador reconectar, continua de onde parou (Last-Event-ID)
    try:
        inicio = int(request.headers.get("last-event-id", "0"))
    except ValueError:
        inicio = 0

    async def stream() -> AsyncGenerator[str, None]:
        enviado = inicio
        silencio = 0.0
        while True:
            logs = jobs.get(job_id, [])
            while enviado < len(logs):
                msg = logs[enviado]
                enviado += 1
                yield f"id: {enviado}\ndata: {msg}\n\n"
                silencio = 0.0
                if msg == "__CONCLUIDO__":
                    return
            await asyncio.sleep(0.5)
            silencio += 0.5
            # keepalive: comentário SSE invisível para o navegador,
            # impede que proxies derrubem a conexão por inatividade
            if silencio >= 10:
                yield ": ping\n\n"
                silencio = 0.0

    return StreamingResponse(stream(), media_type="text/event-stream")


# ---- Robô conversacional (Claude) ----

PROFESSORES = {
    "5579998746693": {
        "nome": "Luth",
        "login": "789.626.335-15",
        "senha": "130224",
        "turmas": ["6", "7", "3b", "financeira", "mat digital b", "mat digital a", "exp mat", "etapa"],
    },
    "5579998746694": {
        "nome": "Marcos",
        "sistema": "infodat",
        "escola": "arqui",
        "professor": "MARCOS ANTÔNIO PASSOS CHAGAS",
        "senha": "Chagas",
        "turmas": [
            {"value": "017A031", "label": "Terceira Série/Ensino Médio - TURMA A - Física"},
            {"value": "017B031", "label": "Terceira Série/Ensino Médio - TURMA B - Física"},
        ],
    },
}

SYSTEM_PROMPT = """Você é o assistente do SóDigita. Registra aulas no sistema escolar do professor. Seja humano, natural, direto — como um colega que ajuda via WhatsApp.

REGRAS DE OURO:
- Respostas CURTAS. 1 ou 2 frases no máximo. Nunca instrucional.
- Se a mensagem parecer incompleta (termina com "de", "com", "sobre", "e", "para" etc.), pergunte o que faltou: "Terminou a frase? 😊" ou "Pode completar?"
- Quando tiver turma + conteúdo, registre SEM perguntar confirmação
- NUNCA pergunte "tem mais aulas?" na mesma mensagem que confirmar o lançamento — deixe o professor mandar quando quiser
- Quando tiver UMA turma, use um REGISTRAR. Quando tiver VÁRIAS turmas na mesma mensagem, use UM REGISTRAR POR TURMA, um embaixo do outro.
- No campo "turma" do REGISTRAR, use SEMPRE o label EXATO da lista de turmas do professor (ex: "6ºA", "1ª Etapa", "3ªB"). Se o professor disser "6 ano", coloque "6ºA". Se disser "1 etapa", coloque "1ª Etapa". Use o label da lista, não o que o professor escreveu.
  REGISTRAR:{"turma": "6ºA", "conteudo": "Critérios de divisibilidade", "solicitadas": false}
  REGISTRAR:{"turma": "7ºA", "conteudo": "Operações com números inteiros", "solicitadas": false}
- Se o professor mencionar "solicitadas", "reposição" ou "aula solicitada", use "solicitadas": true
- NUNCA diga "registrado com sucesso" — você não sabe o resultado ainda
- Nunca invente conteúdo — use exatamente o que o professor escreveu
- Se der instabilidade: "Tive uma queda aqui, tenta de novo em 1 minuto 😊"
- Fora do tema de aulas: redirecione gentilmente, sem repetir sempre a mesma frase
- Português informal, sem formalidade, sem emojis em excesso

EXEMPLOS DE CONFIRMAÇÃO (varie, nunca repita):
  "Lançando pra turma 7A..."
  "Ok, acessando o sistema..."
  "Mandei pro sistema, aguarda..."
  "Certo, registrando agora..."""


class ChatMsg(BaseModel):
    numero: str
    mensagem: str
    historico: list[dict] = []


# Notificações pendentes por professor {numero: [msg, ...]}
notificacoes: dict[str, list[str]] = {}


@app.get("/notificacoes/{numero}")
async def get_notificacoes(numero: str):
    msgs = notificacoes.pop(numero, [])
    return {"mensagens": msgs}


# ---- Gerente de Projetos IA ----

class ManagerMsg(BaseModel):
    mensagem: str
    historico: list[dict] = []

try:
    _CLAUDE_MD = open(os.path.join(os.path.dirname(__file__), "../CLAUDE.md")).read()
except Exception:
    _CLAUDE_MD = "Documento de contexto não encontrado."

MANAGER_PROMPT = f"""Você é o gerente de projetos do SóDigita, um SaaS que automatiza o preenchimento de diários escolares para professores brasileiros via WhatsApp e web.

Você conhece profundamente o projeto pelo documento abaixo. Sua função é ajudar o fundador (Luth) a tomar decisões, priorizar tarefas, identificar riscos e planejar o desenvolvimento.

Quando perguntado "o que faço hoje?" ou "por onde começo?", responda com no máximo 3 tarefas priorizadas por impacto no negócio. Seja direto e prático.

=== CONTEXTO DO PROJETO ===
{_CLAUDE_MD}
=== FIM DO CONTEXTO ===

Responda sempre em português brasileiro, de forma concisa e objetiva."""

NEGOCIOS_PROMPT = """Você é o gerente de negócios e estratégia do SóDigita, um SaaS que automatiza o preenchimento de diários escolares para professores brasileiros via WhatsApp.

Seu foco é ajudar o fundador a escalar o negócio até 2027, pensando em modelo financeiro, crescimento, estrutura e riscos.

Contexto do produto:
- Professor manda mensagem no WhatsApp com a aula → sistema registra automaticamente no SIAE, Infodat, ActiveSoft, SESI
- Planos: R$19,90/mês por função ou R$39,90/mês completo
- Mercado estimado: 43.500 professores em sistemas compatíveis
- Infraestrutura atual: Render free tier, 1 desenvolvedor (o fundador), sem funcionários
- Receita atual: R$0 (fase de testes com primeiros professores)

Quando perguntado, ajude com:
- Metas de receita por trimestre até 2027
- Quantos clientes precisam para cada meta
- Quando contratar primeiro funcionário ou suporte
- Quando migrar infraestrutura para plano pago
- Modelo B2C (professor individual) vs B2B (escola paga por todos)
- Estratégia de precificação
- Riscos críticos e como mitigar
- Plano de negócios resumido

Seja direto, use números reais, não seja genérico. Responda em português brasileiro."""


class NegociosMsg(BaseModel):
    mensagem: str
    historico: list[dict] = []


@app.post("/negocios")
async def negocios_agent(data: NegociosMsg):
    import anthropic as _anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"resposta": "❌ API do Claude não configurada.", "historico": data.historico}
    historico = data.historico + [{"role": "user", "content": data.mensagem}]
    try:
        client = _anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=NEGOCIOS_PROMPT,
            messages=historico,
        )
        resposta = response.content[0].text
    except Exception as e:
        return {"resposta": f"❌ Erro: {str(e)[:100]}", "historico": data.historico}
    return {
        "resposta": resposta,
        "historico": historico + [{"role": "assistant", "content": resposta}],
    }


# ---- CEO IA — coordena os três gerentes ----

class CEOMsg(BaseModel):
    mensagem: str
    historico: list[dict] = []


async def _consultar_especialista(prompt_sistema: str, pergunta: str, api_key: str) -> str:
    import anthropic as _anthropic
    client = _anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=prompt_sistema,
        messages=[{"role": "user", "content": pergunta}],
    )
    return response.content[0].text


CEO_PROMPT = """Você é a Cláudia, CEO do SóDigita, um SaaS que automatiza o preenchimento de diários escolares para professores brasileiros via WhatsApp.

Você coordena três gerentes especializados:
- PROJETOS: responsável pelo desenvolvimento técnico e priorização de tarefas
- MARKETING: responsável por posts, conteúdo e prospecção de professores
- NEGÓCIOS: responsável por estratégia, metas financeiras e escala até 2027

Quando o fundador (Luth) fizer uma pergunta:
1. Decida quais gerentes precisam ser consultados (pode ser 1, 2 ou todos os 3)
2. Você receberá as respostas de cada um
3. Consolide numa resposta única, coesa e acionável

Responda sempre em português brasileiro, de forma direta e prática.
Indique claramente quando uma decisão envolve trade-offs entre áreas."""


@app.post("/ceo")
async def ceo_agent(data: CEOMsg):
    import anthropic as _anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"resposta": "❌ API do Claude não configurada.", "historico": data.historico}

    historico = data.historico + [{"role": "user", "content": data.mensagem}]

    try:
        client = _anthropic.Anthropic(api_key=api_key)

        # Passo 1: CEO decide quais especialistas consultar
        roteamento = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system="Você decide quais especialistas consultar para responder a pergunta. Responda APENAS com uma lista separada por vírgula com os especialistas necessários: PROJETOS, MARKETING, NEGOCIOS. Exemplo: PROJETOS,NEGOCIOS",
            messages=[{"role": "user", "content": data.mensagem}],
        ).content[0].text.upper()

        # Passo 2: Consulta os especialistas em paralelo
        tarefas = []
        nomes = []
        if "PROJETOS" in roteamento:
            tarefas.append(_consultar_especialista(MANAGER_PROMPT, data.mensagem, api_key))
            nomes.append("PROJETOS")
        if "MARKETING" in roteamento:
            tarefas.append(_consultar_especialista(MARKETING_PROMPT, data.mensagem, api_key))
            nomes.append("MARKETING")
        if "NEGOCIOS" in roteamento:
            tarefas.append(_consultar_especialista(NEGOCIOS_PROMPT, data.mensagem, api_key))
            nomes.append("NEGÓCIOS")

        if not tarefas:
            tarefas.append(_consultar_especialista(MANAGER_PROMPT, data.mensagem, api_key))
            nomes.append("PROJETOS")

        respostas = await asyncio.gather(*tarefas)

        # Passo 3: CEO consolida
        contexto_especialistas = "\n\n".join(
            f"=== {nome} ===\n{resp}" for nome, resp in zip(nomes, respostas)
        )
        consolidado = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            system=CEO_PROMPT,
            messages=[
                {"role": "user", "content": data.mensagem},
                {"role": "assistant", "content": f"Consultei meus gerentes. Aqui estão as visões deles:\n\n{contexto_especialistas}"},
                {"role": "user", "content": "Agora consolide numa resposta única e acionável para o fundador."},
            ],
        ).content[0].text

        especialistas_usados = ", ".join(nomes)
        resposta_final = f"*Consultei: {especialistas_usados}*\n\n{consolidado}"

        # Salva memória no Supabase
        try:
            sb = _get_supabase()
            if sb:
                sb.table("sessoes_claudia").insert({
                    "pergunta": data.mensagem,
                    "resposta": resposta_final,
                    "especialistas": especialistas_usados,
                }).execute()
        except Exception:
            pass

    except Exception as e:
        return {"resposta": f"❌ Erro: {str(e)[:100]}", "historico": data.historico}

    return {
        "resposta": resposta_final,
        "historico": historico + [{"role": "assistant", "content": resposta_final}],
    }


MARKETING_PROMPT = """Você é o gerente de marketing digital do SóDigita, um serviço que automatiza o preenchimento de diários escolares para professores brasileiros via WhatsApp.

Seu foco é ajudar o fundador a vender o serviço online para professores, principalmente via Instagram, Facebook e grupos de WhatsApp.

Contexto do produto:
- Professor manda mensagem no WhatsApp dizendo a aula → sistema registra automaticamente no SIAE, Infodat, ActiveSoft, SESI
- Planos: R$19,90/mês por função ou R$39,90/mês completo
- Dor do professor: perde 30-60 min por semana preenchendo diário manualmente
- Diferencial: mais simples que qualquer concorrente — só manda mensagem no WhatsApp

Quando pedido, crie:
- Posts prontos para Instagram/Facebook (legenda completa + sugestão de imagem)
- Scripts de stories (curto, direto, com CTA)
- Mensagens para grupos de WhatsApp de professores (sem spam, com valor)
- Respostas para objeções comuns ("será que funciona?", "é seguro?", "é caro?")
- Calendário semanal de conteúdo
- Estratégias de indicação (professor indica professor)

Escreva sempre na linguagem do professor brasileiro: informal, próximo, sem jargão de marketing.
Foque em dor real: fim de semana preenchendo diário, estresse com prazo da coordenação.
Responda em português brasileiro."""


class MarketingMsg(BaseModel):
    mensagem: str
    historico: list[dict] = []


@app.post("/marketing")
async def marketing_agent(data: MarketingMsg):
    import anthropic as _anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"resposta": "❌ API do Claude não configurada.", "historico": data.historico}
    historico = data.historico + [{"role": "user", "content": data.mensagem}]
    try:
        client = _anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=MARKETING_PROMPT,
            messages=historico,
        )
        resposta = response.content[0].text
    except Exception as e:
        return {"resposta": f"❌ Erro: {str(e)[:100]}", "historico": data.historico}
    return {
        "resposta": resposta,
        "historico": historico + [{"role": "assistant", "content": resposta}],
    }


@app.post("/manager")
async def manager(data: ManagerMsg):
    import anthropic as _anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"resposta": "❌ API do Claude não configurada.", "historico": data.historico}
    historico = data.historico + [{"role": "user", "content": data.mensagem}]
    try:
        client = _anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            system=MANAGER_PROMPT,
            messages=historico,
        )
        resposta = response.content[0].text
    except Exception as e:
        return {"resposta": f"❌ Erro: {str(e)[:100]}", "historico": data.historico}
    return {
        "resposta": resposta,
        "historico": historico + [{"role": "assistant", "content": resposta}],
    }

CADASTRO_PROMPT = """Você é a Rebeca, consultora do SóDigita — um serviço que preenche o diário escolar automaticamente pelo WhatsApp, sem o professor precisar entrar no sistema.

Você é humana, calorosa, sergipana. Fale de forma natural, como uma pessoa real — não como um robô. Use o nome do professor sempre que possível.

FASE 1 — VENDAS (sempre começa aqui para números desconhecidos):
Apresente-se e o produto de forma calorosa. Se a mensagem do professor já trouxer nome e sistema (vindo do formulário do site), use essas informações imediatamente — não pergunte de novo.

Use este roteiro como base, adaptando ao contexto:

"Boa tarde, [nome]! 😊 Me chamo Rebeca, sou consultora do *SóDigita*.

Vi que você tem interesse em automatizar o diário da sua escola. Deixa eu te mostrar como funciona em 30 segundos.

Você manda o conteúdo da aula aqui no WhatsApp e a gente registra tudo no sistema automaticamente — sem você precisar entrar no SIAE, Infodat, ActiveSoft ou qualquer outro sistema.

Funciona com qualquer sistema escolar. E o melhor: você testa gratuitamente.

Posso te cadastrar agora para começar o teste?"

Se não souber o nome, adapte: "Olá! 👋 Me chamo Rebeca..."

IDENTIFICAÇÃO DE PERFIL — OBRIGATÓRIO na conversa:
Durante a conversa, identifique o perfil do professor e ofereça o plano adequado:

- Professor jovem, fala de tecnologia, quer autonomia → **Plano Self-service** (R$9,90/mês — ele mesmo manda as aulas pelo chat)
- Professor mais velho, diz que "não entende de tecnologia", quer simplicidade → **Plano Gerenciado** (R$49,90/mês — a equipe faz tudo por ele)
- Sinais de perfil gerenciado: "não sei mexer", "é complicado?", "tenho que digitar tudo?", "não tenho tempo pra isso", "pode fazer por mim?"

Quando detectar perfil gerenciado, diga:
"[nome], temos também o plano Gerenciado — você manda as informações por aqui (pode ser áudio, foto, texto) e nossa equipe registra tudo no sistema por você. Nem precisa saber como funciona o sistema. Quer conhecer?"

Se o professor confirmar interesse no gerenciado, colete os dados normalmente (FASE 3) e marque no JSON: "plano":"gerenciado".

FASE 2 — QUALIFICAÇÃO DO SISTEMA:
- Se o professor mencionar SIAE, Infodat, ActiveSoft/SIGA ou Totvs RM → diga "Ótimo! A gente já automatiza esse sistema. Posso te cadastrar agora e você testa gratuitamente?" → vá para FASE 3.
- Se o sistema não for nenhum desses → responda EXATAMENTE:
  "Ainda não temos automação para esse sistema, mas podemos providenciar. Caso tenha interesse, podemos ajudar você e seus colegas também. Pode deixar seu nome e o nome do sistema? Nossa equipe entra em contato. 🙏"
  Depois de coletar nome e sistema, encerre com agradecimento e NÃO gere JSON de cadastro.

FASE 3 — CADASTRO (só entra aqui após confirmação do professor):
Vá direto ao ponto — sem repetir o parágrafo de vendas. Colete uma informação por vez:
1. Nome do professor
2. Quantas escolas ele dá aula
3. Para cada escola:
   a. Nome da escola — é o nome da instituição. NÃO confunda com o sistema.
      - Para ActiveSoft: diga "O ActiveSoft funciona pelo link da escola. Você sabe o nome completo da escola ou tem o endereço do sistema deles? (ex: vita.activesoft.com.br)"
   b. Sistema — já foi informado na fase anterior, não pergunte de novo se já sabe.
      - SIAE = rede estadual de Sergipe
      - ActiveSoft/SIGA = Vita, Jardins, COESI, Futuro Feliz e similares
      - Totvs RM = Salesiano e escolas privadas
      - Infodat = sigmawd.com.br
   c. Login:
      - SIAE: CPF sem máscara (só números)
      - ActiveSoft: nome de usuário da escola (NÃO é CPF)
      - Totvs RM: CPF com máscara (xxx.xxx.xxx-xx)
      - Infodat: nome de usuário
   d. Senha — Este é o momento mais importante da conversa. O professor vai hesitar. Você precisa transmitir confiança ANTES de pedir. Use este texto:

"[nome], agora preciso do seu login e senha do sistema. Sei que pode parecer um passo delicado — e faz sentido você hesitar.

O SóDigita é uma empresa 100% sergipana, criada por professores, para professores. Nossa missão é desburocratizar e automatizar o trabalho do professor — viemos pra facilitar, pra ajudar. Em nenhum momento pra atrapalhar.

Estamos do mesmo lado — somos daqui, conhecemos a realidade da rede, e queremos que sua vida seja mais fácil, não mais complicada.

Sua senha é usada exclusivamente para acessar o sistema e preencher seu diário. Nada além disso. Ela fica guardada com criptografia — nem nós conseguimos ver o que você digitou.

Após cada registro, você recebe um print de confirmação com o que foi salvo no sistema. Nossa automação faz uma verificação antes de encerrar — garantindo que cada campo foi preenchido corretamente.

Você ensina. A gente cuida do resto. 🙏

Pode me passar seu login e senha?"

A próxima mensagem JÁ É a senha — aceite qualquer coisa, NUNCA peça confirmação ou repita a pergunta.
   e. Dias da semana nessa escola
   f. Turmas (ex: 1A, 2B)
4. Quando tiver TUDO de TODAS as escolas, gere EXATAMENTE:
CADASTRO:{"nome":"...","plano":"self-service","escolas":[{"nome":"...","sistema":"...","login":"...","senha":"...","dias":["segunda","terça"],"turmas":[{"label":"3A","value":"3A"}]}]}
O campo "plano" deve ser "gerenciado" se o professor escolheu o plano gerenciado, ou "self-service" para os demais.

OBJEÇÃO — "Isso é permitido? Não vou ter problema?":
Se o professor demonstrar receio sobre automação ser proibida ou ter medo de punição, responda:

"[nome], entendo a preocupação — e ela faz sentido.

Mas veja: o que a gente faz é exatamente o que você já faz hoje, só que mais rápido. Entramos no sistema com seu login, preenchemos os campos, clicamos em salvar. É o mesmo processo — só que a gente aperta os botões por você.

Automação é usada em todo lugar: banco, hospital, cartório, RH. Ninguém vai ao banco digitar cada transação manualmente — o sistema faz. Com o diário escolar é a mesma coisa.

O conteúdo é seu. A decisão pedagógica é sua. A gente só executa o trabalho burocrático que você já teria que fazer de qualquer jeito.

E o SóDigita é uma empresa 100% sergipana — nascemos aqui, conhecemos a rede estadual, sabemos o que é ser professor em Sergipe. Nossa missão é desburocratizar, facilitar. Em nenhum momento atrapalhar.

Não existe nenhuma regra nos sistemas escolares que proíba isso — eles só exigem que o diário seja preenchido. Como é preenchido não é problema deles." 😊

REGRAS:
- Linguagem informal, próxima, de professor brasileiro
- Uma pergunta por vez — nunca sobrecarregue
- Se o professor já deu uma informação, não pergunte de novo
- Nunca fale de preço a menos que o professor pergunte — se perguntar, diga: "R$9,90/mês para os primeiros 50 professores. Depois sobe para R$19,90."
- NUNCA diga "CPF e senha" — diga sempre "login e senha". Cada sistema tem seu tipo de login.
- NUNCA presuma SIAE como sistema padrão — o SóDigita funciona com SIAE, Infodat, ActiveSoft, Totvs RM e outros igualmente. Pergunte sempre qual sistema o professor usa.
- Fora do assunto de registro de aulas ou cadastro, não responda — redirecione gentilmente
- Se o professor perguntar se você é um robô, IA ou chatbot — NUNCA confirme nem negue. Responda como consultora humana. Exemplo: "Sou a Rebeca, consultora do SóDigita 😊 Estou aqui para te ajudar!" Se insistir muito, diga: "Posso te passar pro nosso gerente de operações, o Cledson, que pode te dar mais detalhes. Ele entra em contato o mais breve possível. Quer que eu avise ele?" — e encerre a conversa com cordialidade."""


def _buscar_professor_supabase(numero: str):
    sb = _get_supabase()
    if not sb:
        return None
    try:
        res = sb.table("professores").select("*").eq("numero_whatsapp", numero).execute()
        if res.data:
            prof = res.data[0]
            escolas = prof.get("escolas", [])
            prof["escolas"] = [
                {**e, "login": _decrypt(e.get("login", "")), "senha": _decrypt(e.get("senha", ""))}
                for e in escolas
            ]
            return prof
        return None
    except Exception:
        return None


def _classificar_conversa(historico: list, api_key: str) -> dict:
    """Usa Claude para classificar o status da conversa e gerar resumo."""
    try:
        import anthropic as _anthropic
        client = _anthropic.Anthropic(api_key=api_key)
        conversa_texto = "\n".join(
            f"{'Professor' if m['role']=='user' else 'Robô'}: {m['content']}"
            for m in historico[-10:]
        )
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system="""Classifique esta conversa de vendas do SóDigita. Retorne EXATAMENTE este JSON:
{"status":"cadastrado","nome":"Nome do professor","sistema":"SIAE","resumo":"Uma frase resumindo o que aconteceu"}

Status possíveis:
- "cadastrado": professor completou o cadastro
- "lead_quente": interessado, sistema suportado, mas não finalizou
- "sistema_novo": quer o serviço mas usa sistema não suportado
- "abandonou": iniciou conversa mas não avançou
- "fora_escopo": pergunta sem relação com o produto

Retorne APENAS o JSON, sem explicação.""",
            messages=[{"role": "user", "content": conversa_texto}],
        )
        return json.loads(response.content[0].text.strip())
    except Exception:
        return {"status": "abandonou", "nome": "", "sistema": "", "resumo": "Erro ao classificar"}


def _salvar_conversa_supabase(numero: str, classificacao: dict):
    sb = _get_supabase()
    if not sb:
        return
    try:
        sb.table("conversas").upsert({
            "numero_whatsapp": numero,
            "nome": classificacao.get("nome", ""),
            "status": classificacao.get("status", "abandonou"),
            "sistema": classificacao.get("sistema", ""),
            "resumo": classificacao.get("resumo", ""),
        }, on_conflict="numero_whatsapp").execute()
    except Exception:
        pass


def _salvar_professor_supabase(numero: str, dados: dict):
    sb = _get_supabase()
    if not sb:
        return False
    try:
        escolas = dados.get("escolas", [])
        escolas_cript = []
        for e in escolas:
            escolas_cript.append({
                **e,
                "login": _encrypt(e.get("login", "")),
                "senha": _encrypt(e.get("senha", "")),
            })
        sb.table("professores").insert({
            "numero_whatsapp": numero,
            "nome": dados.get("nome", ""),
            "escolas": escolas_cript,
            "ativo": True,
        }).execute()
        return True
    except Exception:
        return False


@app.post("/chat")
async def chat(data: ChatMsg):
    import anthropic as _anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"resposta": "❌ API do Claude não configurada.", "historico": data.historico}

    # Busca professor no dict local ou no Supabase
    professor = PROFESSORES.get(data.numero)
    if not professor:
        professor_sb = _buscar_professor_supabase(data.numero)
        if professor_sb:
            escolas = professor_sb.get("escolas", [])
            if escolas:
                # Detecta escola pelo dia da semana
                import datetime
                dias_semana = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
                dia_hoje = dias_semana[datetime.date.today().weekday()]

                # Filtra escolas do dia de hoje
                escolas_hoje = []
                for e in escolas:
                    dias_escola = [d.lower().replace("ç","c").replace("á","a").replace("ã","a").replace("é","e").replace("ê","e") for d in e.get("dias", [])]
                    if dia_hoje in dias_escola:
                        escolas_hoje.append(e)

                if not escolas_hoje:
                    escolas_hoje = [escolas[0]]

                # Monta mapa turma → escola para detecção automática
                turma_para_escola = {}
                for e in escolas_hoje:
                    for t in e.get("turmas", []):
                        turma_para_escola[t["value"].upper()] = e
                        turma_para_escola[t["label"].upper()] = e

                # Usa primeira escola do dia como padrão
                escola = escolas_hoje[0]

                professor = {
                    "nome": professor_sb["nome"],
                    "sistema": escola.get("sistema", "siae"),
                    "login": escola.get("login", ""),
                    "senha": escola.get("senha", ""),
                    "turmas": escola.get("turmas", []),
                    "escola": escola.get("nome", ""),
                    "professor": escola.get("login", ""),
                    "escolas": escolas,
                    "escolas_hoje": escolas_hoje,
                    "turma_para_escola": turma_para_escola,
                    "escola_hoje": escola.get("nome", ""),
                }

    # Professor não cadastrado — inicia fluxo de vendas + cadastro
    if not professor:
        historico = data.historico + [{"role": "user", "content": data.mensagem}]

        # Limite de 30 trocas no cadastro (precisa de mais espaço que vendas)
        # Só encerra se já tiver muitas mensagens E não houver progresso
        if len(historico) > 60:
            encerramento = "Foi um prazer conversar! 😊 Quando quiser começar a usar o SóDigita, é só chamar. Até logo!"
            return {
                "resposta": encerramento,
                "historico": [],
                "job_id": None,
                "cadastrando": False,
            }

        client = _anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=CADASTRO_PROMPT,
            messages=historico,
        )
        resposta = response.content[0].text

        # Verifica se o cadastro foi concluído
        cadastro_match = re.search(r"CADASTRO:(\{.*\})", resposta, re.DOTALL)
        if cadastro_match:
            try:
                dados_cadastro = json.loads(cadastro_match.group(1))
                _salvar_professor_supabase(data.numero, dados_cadastro)
                resposta = resposta.replace(cadastro_match.group(0), "").strip()
                resposta += "\n\n✅ Cadastro concluído! Agora é só me mandar a turma e o conteúdo da aula que eu registro pra você. 🚀"
                _salvar_conversa_supabase(data.numero, {
                    "status": "cadastrado",
                    "nome": dados_cadastro.get("nome", ""),
                    "sistema": dados_cadastro.get("escolas", [{}])[0].get("sistema", ""),
                    "resumo": f"Professor cadastrou {len(dados_cadastro.get('escolas', []))} escola(s).",
                })
            except Exception:
                pass
        else:
            # Classifica conversa em background se tiver pelo menos 4 trocas
            hist_completo = historico + [{"role": "assistant", "content": resposta}]
            if len(hist_completo) >= 4:
                try:
                    classificacao = _classificar_conversa(hist_completo, api_key)
                    _salvar_conversa_supabase(data.numero, classificacao)
                except Exception:
                    pass

        return {
            "resposta": resposta,
            "historico": historico + [{"role": "assistant", "content": resposta}],
            "job_id": None,
            "cadastrando": True,
        }

    professor = professor or {"nome": "Professor", "sistema": "siae"}
    historico = data.historico + [{"role": "user", "content": data.mensagem}]

    try:
        client = _anthropic.Anthropic(api_key=api_key)
        import datetime
        dias_semana_pt = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
        dia_hoje_pt = dias_semana_pt[datetime.date.today().weekday()]
        escola_hoje = professor.get("escola_hoje", professor.get("escola", ""))
        sistema_hoje = professor.get("sistema", "SIAE")

        # Monta lista de turmas do dia de hoje
        turmas_hoje = professor.get("turmas_hoje", [])
        turmas_str = ""
        if turmas_hoje:
            labels = [t.get("label", t.get("value", "")) for t in turmas_hoje]
            turmas_str = f"\n\nTURMAS DO PROFESSOR HOJE ({dia_hoje_pt}): {', '.join(labels)}. Quando o professor disser 'todas as turmas' ou 'todas da {dia_hoje_pt.split('-')[0]}', use EXATAMENTE essas turmas — NÃO peça para ele listar. Gere um REGISTRAR para cada turma."

        system = SYSTEM_PROMPT.replace("Professor", professor["nome"])
        system += f"\n\nCONTEXTO DE HOJE ({dia_hoje_pt}): O professor está na escola '{escola_hoje}' usando o sistema {sistema_hoje}. Quando confirmar o registro, mencione a escola se relevante."
        system += turmas_str

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=system,
            messages=historico,
        )
        resposta = response.content[0].text
    except Exception as e:
        return {"resposta": f"❌ Erro: {str(e)[:100]}", "historico": data.historico}

    # Verifica se tem aulas para registrar (suporta múltiplos REGISTRAR na mesma resposta)
    registrar_matches = re.findall(r"REGISTRAR:(\{.*?\})", resposta)
    resposta = re.sub(r"REGISTRAR:\{.*?\}", "", resposta).strip()
    job_id = None

    if registrar_matches:
        try:
            turma_para_escola = professor.get("turma_para_escola", {})

            def _resolver_credenciais(turma):
                escola_det = turma_para_escola.get(turma.upper())
                if escola_det:
                    sis = escola_det.get("sistema", professor.get("sistema", "siae")).lower().replace("/", "").replace(" ", "")
                    return sis, escola_det.get("login", professor.get("login", "")), escola_det.get("senha", professor.get("senha", "")), escola_det.get("nome", professor.get("escola", "")), escola_det.get("turmas", professor.get("turmas", []))
                sis = professor.get("sistema", "siae").lower().replace("/", "").replace(" ", "")
                return sis, professor.get("login", ""), professor.get("senha", ""), professor.get("escola", ""), professor.get("turmas", [])

            def _normalizar_sistema(sis):
                if "activesoft" in sis or "siga" in sis:
                    return "active"
                if "totvs" in sis or "salesiano" in sis:
                    return "salesiano"
                if "infodat" in sis:
                    return "infodat"
                return "siae"

            # Agrupa entradas por sistema
            siae_assuntos = {}  # turma_label → conteudo
            siae_solicitadas = False
            siae_creds = None
            infodat_entradas = []
            infodat_creds = None

            for raw in registrar_matches:
                try:
                    dados_aula = json.loads(raw)
                except Exception:
                    continue
                turma = dados_aula.get("turma", "")
                conteudo = dados_aula.get("conteudo", "").strip()
                if not conteudo:
                    continue
                conteudo = conteudo[0].upper() + conteudo[1:]
                if not conteudo.endswith("."):
                    conteudo += "."
                solicitadas = dados_aula.get("solicitadas", False)

                sis_raw, login_uso, senha_uso, escola_uso, turmas_uso = _resolver_credenciais(turma)
                sis = _normalizar_sistema(sis_raw)

                if sis == "siae":
                    if siae_creds is None:
                        siae_creds = (login_uso, senha_uso, solicitadas)
                    if solicitadas:
                        siae_solicitadas = True
                    # Mapeia turma → conteudo usando label das turmas do professor
                    # Matching tolerante: "sexto ano"→"6", "6 ano"/"6°A" casa com "6ºA"
                    _EXTENSO = {"primeiro":1,"segunda":2,"segundo":2,"terceiro":3,"terceira":3,"quarto":4,"quarta":4,"quinto":5,"quinta":5,"sexto":6,"setimo":7,"sétimo":7,"oitavo":8,"nono":9,"decimo":10}
                    def _normalizar_turma(s):
                        s = s.lower()
                        for palavra, num in _EXTENSO.items():
                            s = s.replace(palavra, str(num))
                        return re.sub(r'[°ºª\.\s\-]', '', s)
                    def _turma_match(turma_json, label):
                        t = _normalizar_turma(turma_json)
                        l = _normalizar_turma(label)
                        return t in l or l.startswith(t)
                    turmas_match = [t for t in turmas_uso if _turma_match(turma, t)]
                    if not turmas_match:
                        turmas_match = turmas_uso
                    for t in turmas_match:
                        siae_assuntos[t] = conteudo

                elif sis == "infodat":
                    if infodat_creds is None:
                        infodat_creds = (login_uso, senha_uso, escola_uso)
                    turmas_match = [t for t in turmas_uso if turma.upper() in t["label"].upper()]
                    if not turmas_match:
                        turmas_match = turmas_uso
                    hoje = __import__("datetime").date.today().strftime("%d/%m/%Y")
                    for t in turmas_match:
                        infodat_entradas.append({"data": hoje, "turma_value": t["value"], "num_aulas": "2", "conteudo": conteudo})

                else:
                    resposta += f"\n⚠️ Sistema '{sis}' para turma {turma} — use sodigita.com.br"

            # Dispara job SIAE com todas as turmas de uma vez
            if siae_assuntos and siae_creds:
                login_uso, senha_uso, _ = siae_creds
                form = FormData(
                    login=login_uso,
                    senha=senha_uso,
                    opcoes={"aulas": not siae_solicitadas, "solicitadas": siae_solicitadas, "notas": False},
                    modo_conteudo="proprio",
                    assuntos_por_turma=siae_assuntos,
                    numero=data.numero,
                )
                job_id = str(uuid.uuid4())
                jobs[job_id] = []
                asyncio.create_task(run_automacao(job_id, form))

            # Dispara job Infodat
            if infodat_entradas and infodat_creds:
                login_uso, senha_uso, escola_uso = infodat_creds
                form_inf = InfodatFormData(
                    escola=escola_uso,
                    professor=login_uso,
                    senha=senha_uso,
                    entradas=infodat_entradas,
                    numero=data.numero,
                )
                job_id = str(uuid.uuid4())
                jobs[job_id] = []
                asyncio.create_task(run_infodat(job_id, form_inf))

        except Exception as ex:
            resposta += f"\n⚠️ Erro ao iniciar registro: {str(ex)[:80]}"

    return {
        "resposta": resposta,
        "historico": historico + [{"role": "assistant", "content": resposta}],
        "job_id": job_id,
    }


# ---- Servir o site (frontend) pelo mesmo servidor ----
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.post("/cadastro")
async def cadastro_web(data: dict):
    """Endpoint para cadastro via formulário web."""
    numero = data.get("numero", "")
    nome = data.get("nome", "")
    escolas = data.get("escolas", [])

    if not numero or not nome or not escolas:
        return {"ok": False, "erro": "Dados incompletos"}

    sucesso = _salvar_professor_supabase(numero, {"nome": nome, "escolas": escolas})
    if sucesso:
        return {"ok": True}
    return {"ok": False, "erro": "Erro ao salvar no banco de dados"}


@app.post("/lead")
async def salvar_lead(data: dict):
    """Salva lead do formulário da landing page."""
    nome = data.get("nome", "")
    whatsapp = data.get("whatsapp", "")
    sistema = data.get("sistema", "")
    sb = _get_supabase()
    if sb:
        try:
            sb.table("leads").upsert({
                "numero_whatsapp": whatsapp,
                "nome": nome,
                "sistema": sistema,
                "criado_em": datetime.datetime.now().isoformat()
            }).execute()
        except Exception:
            pass
    return {"ok": True}


@app.post("/admin/professor/turmas")
async def atualizar_turmas(data: dict):
    """Atualiza turmas de uma escola do professor."""
    sb = _get_supabase()
    if not sb:
        return {"erro": "Supabase não configurado"}
    try:
        numero = data.get("numero")
        escola_index = data.get("escola_index", 0)
        turmas = data.get("turmas", [])
        dias = data.get("dias", None)

        res = sb.table("professores").select("*").eq("numero_whatsapp", numero).execute()
        if not res.data:
            return {"erro": "Professor não encontrado"}

        prof = res.data[0]
        escolas = prof.get("escolas", [])
        if escola_index >= len(escolas):
            return {"erro": "Escola não encontrada"}

        escolas[escola_index]["turmas"] = turmas
        if dias:
            escolas[escola_index]["dias"] = dias

        sb.table("professores").update({"escolas": escolas}).eq("numero_whatsapp", numero).execute()
        return {"ok": True, "mensagem": f"{len(turmas)} turmas salvas com sucesso"}
    except Exception as e:
        return {"erro": str(e)}


@app.post("/admin/briefing")
async def gerar_briefing():
    """Gera briefing diário com IA baseado nas conversas do Supabase."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    sb = _get_supabase()
    conversas = []
    if sb:
        try:
            res = sb.table("conversas").select("*").order("atualizado_em", desc=True).limit(50).execute()
            conversas = res.data or []
        except Exception:
            pass
    if not conversas:
        return {"briefing": "Nenhuma conversa encontrada ainda."}
    resumo = "\n".join([f"- {c.get('nome','?')} ({c.get('status','?')}): {c.get('resumo','sem resumo')}" for c in conversas])
    hoje = datetime.date.today().strftime("%d/%m/%Y")
    prompt = f"""Você é assistente de vendas do SóDigita. Gere um briefing executivo para hoje ({hoje}) baseado nas conversas abaixo.

Conversas:
{resumo}

O briefing deve ter:
1. Resumo do pipeline (quantos em cada status)
2. Top 3 leads para priorizar hoje e por quê
3. Alertas (leads esfriando, sistemas não suportados com interesse)
4. Sugestão de ação do dia

Seja direto e prático. Máximo 300 palavras."""
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(model="claude-haiku-4-5", max_tokens=600, messages=[{"role": "user", "content": prompt}])
    return {"briefing": resp.content[0].text}


@app.get("/admin/conversas")
async def admin_conversas():
    sb = _get_supabase()
    if not sb:
        return {"erro": "Supabase não configurado"}
    try:
        res = sb.table("conversas").select("*").order("atualizado_em", desc=True).limit(100).execute()
        return {"conversas": res.data}
    except Exception as e:
        return {"erro": str(e)}


@app.post("/admin/conversas/{numero}/visto")
async def marcar_visto(numero: str):
    sb = _get_supabase()
    if not sb:
        return {"ok": False}
    try:
        sb.table("conversas").update({"visto": True}).eq("numero_whatsapp", numero).execute()
        return {"ok": True}
    except Exception:
        return {"ok": False}


@app.get("/screenshot/{nome}")
async def ver_screenshot(nome: str):
    path = f"/tmp/screenshots/{nome}"
    if not os.path.exists(path):
        return {"erro": "Screenshot não encontrado"}
    return FileResponse(path, media_type="image/png")


class DesignMsg(BaseModel):
    descricao: str

@app.post("/design")
async def design_agent(data: DesignMsg):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        return {"erro": "GEMINI_API_KEY não configurada"}
    try:
        import httpx, base64
        prompt = f"""Crie uma imagem para post de Instagram do SóDigita, um app que automatiza o preenchimento de diário escolar para professores brasileiros.
Estilo: minimalista, fundo roxo (#7C5CFF) ou branco, tipografia moderna e limpa.
Cores: roxo #7C5CFF, verde-água #00D4AA, branco.
Formato: quadrado 1080x1080px.
Descrição do post: {data.descricao}"""

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
                }
            )
        result = resp.json()
        parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                img_b64 = part["inlineData"]["data"]
                mime = part["inlineData"]["mimeType"]
                img_path = f"/tmp/screenshots/design_{uuid.uuid4().hex[:8]}.png"
                os.makedirs("/tmp/screenshots", exist_ok=True)
                with open(img_path, "wb") as f:
                    f.write(base64.b64decode(img_b64))
                nome = os.path.basename(img_path)
                return {"imagem": f"/screenshot/{nome}", "mime": mime}
        return {"aviso": "Imagem não gerada", "resposta": result}
    except Exception as e:
        return {"erro": str(e)}


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
