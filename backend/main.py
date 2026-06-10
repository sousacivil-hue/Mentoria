import asyncio
import json
import os
import re
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI
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


def get_conteudo(serie: str, assuntos_proprios: list[str]) -> str:
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
    avaliacao: str = "AV2"
    nota: str = ""


URL_LOGIN = "https://sso.seduc.se.gov.br/sistemas"
URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"
METODOLOGIA = "Aula expositiva dialogada com resolução de exercícios."


async def run_automacao(job_id: str, data: FormData):
    from playwright.async_api import async_playwright

    log = jobs[job_id]
    _indices.clear()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        log.append("🔐 Fazendo login no SIAE...")
        await page.goto(URL_LOGIN)
        await page.wait_for_timeout(2000)
        try:
            await page.fill("input[name='username'], input[type='text']", data.login)
            await page.fill("input[name='password'], input[type='password']", data.senha)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(4000)
        except Exception as e:
            log.append(f"⚠️ Erro no login: {e}")

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
                            const serie = tds[3] ? tds[3].innerText.trim() : '';
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
                conteudo = get_conteudo(serie, data.assuntos)

                log.append(f"⏳ Aula {aula_num + 1}: {serie[:40]}")
                await page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
                await page.wait_for_timeout(3000)

                try:
                    obj = page.locator("textarea").nth(0)
                    await obj.wait_for(timeout=6000)
                    await obj.triple_click()
                    await obj.fill(conteudo)
                    met = page.locator("textarea").nth(1)
                    if await met.count() > 0:
                        await met.triple_click()
                        await met.fill(METODOLOGIA)
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
                            const serie = tds[3] ? tds[3].innerText.trim() : '';
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
                conteudo = get_conteudo(serie, data.assuntos)

                log.append(f"⏳ Solicitada {aula_num + 1}: {serie[:40]}")
                await page.goto(f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}")
                await page.wait_for_timeout(3000)

                try:
                    obj = page.locator("textarea").nth(0)
                    await obj.wait_for(timeout=6000)
                    await obj.triple_click()
                    await obj.fill(conteudo)
                    met = page.locator("textarea").nth(1)
                    if await met.count() > 0:
                        await met.triple_click()
                        await met.fill(METODOLOGIA)
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

        log.append(f"🎉 Automação concluída!")
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
            await page.wait_for_timeout(3000)
            usuario_input = page.locator(
                "input[name='usuario'], input[name='login'], input[name='username'], input[type='text']"
            ).first
            await usuario_input.fill(data.usuario)
            await page.locator("input[type='password']").first.fill(data.senha)
            await page.locator(
                "button[type='submit'], input[type='submit'], button:has-text('Entrar'), button:has-text('Acessar')"
            ).first.click()
            await page.wait_for_timeout(4000)
            log.append(f"✅ Login realizado — {page.url}")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        async def achar(seletor, tentativas=10):
            """Procura um elemento na página e em todos os frames internos.
            Repete por até `tentativas` x 1,5s para aguardar a página carregar."""
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

        # ---- DIAGNÓSTICO: o que o robô enxerga na página ----
        await page.wait_for_timeout(4000)
        log.append(f"🔍 URL atual: {page.url}")
        log.append(f"🔍 Frames na página: {len(page.frames)}")
        for fi, frame in enumerate(page.frames):
            try:
                textos = await frame.evaluate(
                    "() => Array.from(document.querySelectorAll('button, input[type=button], "
                    "input[type=submit], a')).map(e => (e.innerText || e.value || '').trim())"
                    ".filter(t => t).slice(0, 25)"
                )
                if textos:
                    log.append(f"🔍 Frame {fi}: {textos}")
            except Exception:
                continue

        # ---- 1. Clica em EXIBIR (filtro de período) ----
        frame_ex, exibir = await achar("button:has-text('EXIBIR'), input[value*='EXIBIR' i], a:has-text('EXIBIR'), *[onclick]:has-text('EXIBIR')")
        if exibir:
            await exibir.click()
            await page.wait_for_timeout(3000)
            log.append("✅ Período exibido")
        else:
            log.append("⚠️ Botão EXIBIR não encontrado — tentando seguir mesmo assim")

        # ---- 2. Descobre as turmas disponíveis (procurando em frames) ----
        url_lista_turmas = page.url
        await page.wait_for_timeout(2000)
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
            await page.wait_for_timeout(3000)

            # Registro de aulas do bimestre (pode abrir em frame ou nova página)
            fr2, _ = await achar(f"tr:has-text('{data.bimestre}º BIMESTRE')")
            if fr2 is None:
                raise RuntimeError(f"Tabela de bimestres não encontrada")
            linha_bim = fr2.locator(f"tr:has-text('{data.bimestre}º BIMESTRE')").first
            reg = linha_bim.locator("a:has-text('Registro de aulas')").first
            await reg.wait_for(timeout=8000)
            await reg.click()
            await page.wait_for_timeout(3000)
            log.append(f"✅ Registro de aulas do {data.bimestre}º bimestre aberto")

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

                # Acha a linha em branco (textarea de conteúdo vazio)
                linha_vazia = None
                linhas = fr3.locator("table tr:has(textarea)")
                total_linhas = await linhas.count()
                for i in range(total_linhas):
                    linha = linhas.nth(i)
                    txt = (await linha.locator("textarea").first.input_value()).strip()
                    if not txt:
                        linha_vazia = linha
                        break

                if linha_vazia is None:
                    log.append("⚠️ Nenhuma linha em branco disponível — limite de aulas atingido?")
                    break

                # Preenche a data (input de texto, não a checkbox)
                campo_data = linha_vazia.locator("input[type='text']").first
                await campo_data.click()
                await campo_data.fill(data_br)
                # Dispara eventos de máscara de data, se houver
                await campo_data.press("Tab")

                # Preenche o conteúdo (primeiro textarea; Tarefas fica em branco)
                conteudo_box = linha_vazia.locator("textarea").first
                await conteudo_box.click()
                await conteudo_box.fill(aula["conteudo"])

                # Grava esta aula
                gravar = linha_vazia.locator(
                    "button:has-text('Gravar'), input[value*='Gravar' i]"
                ).first
                await gravar.click()
                await page.wait_for_timeout(2500)

                preenchidas += 1
                log.append(f"✏️ {data_br} — {aula['conteudo'][:50]}")

            log.append(f"📊 {preenchidas} aulas gravadas nesta turma")

        # ---- 3. Processa turma(s), uma por vez ----
        turmas_feitas = 0
        teve_erro = False
        for idx in range(total_turmas):
            # Volta para a lista de turmas
            await page.goto(url_lista_turmas)
            await page.wait_for_timeout(2500)
            fr_check, _ = await achar("a:has-text('Diário de classe')")
            if fr_check is None:
                _, exibir2 = await achar("button:has-text('EXIBIR'), input[value*='EXIBIR' i]")
                if exibir2:
                    await exibir2.click()
                    await page.wait_for_timeout(3000)
                fr_check, _ = await achar("a:has-text('Diário de classe')")
            if fr_check is None:
                log.append(f"⚠️ Não consegui voltar à lista de turmas")
                teve_erro = True
                break

            # Se o professor escolheu uma turma específica, pula as outras
            if data.turma:
                bloco_texto = await fr_check.locator("a:has-text('Diário de classe')").nth(idx).evaluate(
                    "el => { let q = el, melhor = ''; "
                    "for (let i = 0; i < 10 && q; i++) { "
                    "const t = q.innerText || ''; "
                    "if (t.length > melhor.length && t.length < 2000) melhor = t; "
                    "q = q.parentElement; } return melhor.slice(0, 500); }"
                )
                # Normaliza: minúsculas, sem º/°/ª, sem espaços
                def norm(s):
                    return (s.lower().replace("º", "").replace("°", "").replace("ª", "")
                            .replace(" ", "").replace("/", ""))
                if norm(data.turma) not in norm(bloco_texto or ""):
                    log.append(f"⏭️ Turma {idx + 1} não é '{data.turma}' — pulando")
                    continue

            log.append(f"➡️ Turma {idx + 1} de {total_turmas}...")
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
            # API do Gemini (Google)
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.5-flash-lite:generateContent?key={api_key}"
            )
            body = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}]
            }).encode("utf-8")
            headers = {"Content-Type": "application/json"}

        def chamar():
            reqobj = urllib.request.Request(url, data=body, headers=headers)
            try:
                with urllib.request.urlopen(reqobj, timeout=60) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                detalhe = e.read().decode("utf-8", errors="ignore")
                raise RuntimeError(f"HTTP {e.code}: {detalhe[:600]}")

        resultado = await asyncio.to_thread(chamar)

        if api_key.startswith("sk-ant"):
            texto = resultado["content"][0]["text"]
        else:
            texto = resultado["candidates"][0]["content"]["parts"][0]["text"]

        topicos = [l.strip().lstrip("-•*").strip() for l in texto.split("\n") if l.strip()]
        return {"topicos": topicos}

    except Exception as e:
        return {"erro": f"Falha ao gerar tópicos: {e}"}


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
async def progresso(job_id: str):
    async def stream() -> AsyncGenerator[str, None]:
        enviado = 0
        while True:
            logs = jobs.get(job_id, [])
            while enviado < len(logs):
                msg = logs[enviado]
                yield f"data: {msg}\n\n"
                enviado += 1
                if msg == "__CONCLUIDO__":
                    return
            await asyncio.sleep(0.5)

    return StreamingResponse(stream(), media_type="text/event-stream")


# ---- Servir o site (frontend) pelo mesmo servidor ----
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
