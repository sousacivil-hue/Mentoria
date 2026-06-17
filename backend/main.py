import asyncio
import json
import os
import re
import unicodedata
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


def get_conteudo(serie: str, assuntos_proprios: list[str], assuntos_por_turma: dict[str, str] | None = None) -> str:
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
            # CPF precisa de máscara: 78962633515 → 789.626.335-15
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
                log.append(f"❌ Login falhou — verifique CPF e senha. URL: {page.url}")
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
                log.append(f"📓 SIAE aberto: {page.url}")
        except Exception as e:
            log.append(f"❌ Erro no login: {e}")
            return

        # ---- AULAS REGULARES ----
        if data.opcoes.get("aulas"):
            log.append("📋 Acessando aulas regulares...")
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(3000)

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
                    log.append("✅ Aulas regulares: todas preenchidas!")
                    break

                alvo = botoes[0]
                match = re.search(r"registrar\((\d+)\)", alvo["onclick"])
                if not match:
                    break
                aula_id = match.group(1)
                serie = alvo["serie"]
                conteudo = get_conteudo(serie, data.assuntos, data.assuntos_por_turma)

                log.append(f"⏳ Aula {aula_num + 1}: {serie[:40]}")
                await page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
                await page.wait_for_timeout(3000)

                try:
                    obj = page.locator("textarea").nth(0)
                    await obj.wait_for(timeout=6000)
                    await obj.fill(conteudo)
                    met = page.locator("textarea").nth(1)
                    if await met.count() > 0:
                        await met.fill(METODOLOGIA)
                    try:
                        await page.locator("button[data-target='#lista']").click(timeout=3000)
                        await page.wait_for_timeout(1500)
                        await page.locator("button#btnConfirmar, button:has-text('CONFIRMAR'), button:has-text('Confirmar')").first.click(timeout=5000)
                        await page.wait_for_timeout(1500)
                        log.append("✅ Frequência registrada")
                    except Exception as ef:
                        log.append(f"⚠️ Frequência: {ef}")
                    salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar')").first
                    await salvar.click()
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
                conteudo = get_conteudo(serie, data.assuntos, data.assuntos_por_turma)

                log.append(f"⏳ Solicitada {aula_num + 1}: {serie[:40]}")
                await page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
                await page.wait_for_timeout(3000)

                try:
                    obj = page.locator("textarea").nth(0)
                    await obj.wait_for(timeout=6000)
                    await obj.fill(conteudo)
                    met = page.locator("textarea").nth(1)
                    if await met.count() > 0:
                        await met.fill(METODOLOGIA)
                    try:
                        await page.locator("button[data-target='#lista']").click(timeout=3000)
                        await page.wait_for_timeout(1500)
                        await page.locator("button#btnConfirmar, button:has-text('CONFIRMAR'), button:has-text('Confirmar')").first.click(timeout=5000)
                        await page.wait_for_timeout(1500)
                        log.append("✅ Frequência registrada")
                    except Exception as ef:
                        log.append(f"⚠️ Frequência: {ef}")
                    salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar')").first
                    await salvar.click()
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

        # ---- SÓ CHAMADA ----
        if data.opcoes.get("chamada"):
            log.append("✅ Iniciando chamadas...")
            await page.goto(URL_AULAS)
            await page.wait_for_timeout(3000)

            async def selecionar_solicitadas():
                try:
                    radio = page.locator("label:has-text('Solicitada') input[type=radio]")
                    if await radio.count() > 0:
                        await radio.first.click(force=True)
                        await page.wait_for_timeout(1500)
                except Exception:
                    pass

            await selecionar_solicitadas()
            ja_feitos = set()
            chamada_num = 0
            while True:
                await page.wait_for_timeout(1000)
                botoes = await page.evaluate("""
                    () => {
                        const result = [];
                        const btns = document.querySelectorAll('button[onclick*="carregarListaDePresenca"]');
                        for (const btn of btns) {
                            const tr = btn.closest('tr');
                            if (!tr) continue;
                            const tds = tr.querySelectorAll('td');
                            const objeto = tds[2] ? tds[2].innerText.trim() : '';
                            const onclick = btn.getAttribute('onclick') || '';
                            if (objeto && objeto !== '-') {
                                result.push({onclick});
                            }
                        }
                        return result;
                    }
                """)
                pendentes = [b for b in botoes if b["onclick"] not in ja_feitos]
                if not pendentes:
                    log.append("✅ Chamadas: todas confirmadas!")
                    break
                alvo = pendentes[0]
                onclick = alvo["onclick"]
                ja_feitos.add(onclick)
                try:
                    btn = page.locator(f"button[onclick='{onclick}']").first
                    await btn.click()
                    await page.wait_for_selector("#lista.in, #lista[style*='display: block']", timeout=8000)
                    await page.wait_for_timeout(1000)
                    await page.locator("#btnConfirmar").click()
                    await page.wait_for_timeout(2000)
                    chamada_num += 1
                    log.append(f"✅ Chamada {chamada_num} confirmada!")
                    await page.goto(URL_AULAS)
                    await page.wait_for_timeout(2000)
                    await selecionar_solicitadas()
                except Exception as e:
                    log.append(f"⚠️ Erro na chamada: {e}")
                    break

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
        browser = await pw.chromium.launch(headless=True)
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
        browser = await pw.chromium.launch(headless=True)
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
    return {"versao": "2026-06-17.54"}


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
        browser = await pw.chromium.launch(headless=True)
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
        browser = await pw.chromium.launch(headless=True)
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
        browser = await pw.chromium.launch(headless=True)
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


INFODAT_BASE = "https://www.sigmawd.com.br/infodat/professor"


async def run_infodat(job_id: str, data: InfodatFormData):
    from playwright.async_api import async_playwright

    log = jobs[job_id]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
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
        for tentativa in range(3):
            try:
                await page.goto(f"{INFODAT_BASE}/login.php",
                                wait_until="domcontentloaded", timeout=60000)
                break
            except Exception as e:
                log.append(f"  ⚠️ Tentativa {tentativa + 1} falhou: {e.__class__.__name__}")
                await page.wait_for_timeout(5000)

        await page.wait_for_timeout(500)

        try:
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
                log.append(f"⚠️ Professor não encontrado na lista. Opções: {[o['text'] for o in opcoes[:5]]}")
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
                log.append("❌ ERRO: login não aceito — verifique professor e senha.")
                log.append("__ERRO__")
                log.append("__CONCLUIDO__")
                await browser.close()
                return

            log.append("✅ Login realizado!")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
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
            except Exception as e:
                log.append(f"   ⚠️ Erro: {e}")

        log.append(f"\n✅ CONCLUÍDO! Aulas gravadas: {gravadas}/{len(data.entradas)}")
        log.append("__CONCLUIDO__")
        await browser.close()


class InfodatLoginData(BaseModel):
    escola: str
    professor: str
    senha: str
    valor_prof: str | None = None


@app.post("/turmas-infodat")
async def turmas_infodat(data: InfodatLoginData):
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
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
                    .filter(o => o.value && o.text.trim())
                    .map(o => ({value: o.value, text: o.text.trim()}))
            """)
            valores_validos = {o["value"] for o in opcoes}
            if data.valor_prof and data.valor_prof in valores_validos:
                valor_prof = data.valor_prof
            else:
                palavras = _sem_acento(data.professor).split()
                valor_prof = None
                for opt in opcoes:
                    texto = _sem_acento(opt["text"])
                    if all(p in texto for p in palavras):
                        valor_prof = opt["value"]
                        break
                if not valor_prof:
                    nomes = [o["text"] for o in opcoes[:5]]
                    return {"erro": f"Professor não encontrado. Tente com outro trecho do nome. Exemplos da lista: {nomes}"}
            await page.locator("select#professor").select_option(value=valor_prof)
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
            return {"turmas": turmas, "valor_prof": valor_prof}
        except Exception as e:
            return {"erro": str(e)}
        finally:
            await browser.close()


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


# ---- Servir o site (frontend) pelo mesmo servidor ----
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
