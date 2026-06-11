import asyncio
import json
import os
import re
import uuid
from typing import AsyncGenerator

from fastapi import FastAPI, Request
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

                # Acha a primeira linha em branco (reavalia após cada gravação)
                linha_vazia = None
                # scroll para o topo da tabela para garantir visibilidade
                await fr3.locator("table").first.evaluate("el => el.scrollIntoView()")
                await page.wait_for_timeout(300)
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
                # espera a tabela atualizar (até 8s)
                for _ in range(8):
                    await page.wait_for_timeout(1000)
                    # considera gravado quando o textarea da linha sumiu ou virou texto fixo
                    ainda_editando = await linha_vazia.locator("textarea").count()
                    if ainda_editando == 0:
                        break

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
    url_plano: str  # URL direta do plano de aula da turma
    usuario: str
    senha: str
    aula_inicio: int = 1
    duplas: bool = False
    topicos: list[str] = []


async def run_salesiano(job_id: str, data: SalesianoFormData):
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

        # ---- Login + ir direto para o plano de aula ----
        log.append("🔐 Fazendo login no Portal do Professor...")
        try:
            await page.goto(data.url_plano)
            await page.wait_for_timeout(3000)
            senha_input = page.locator("input[type='password']").first
            if await senha_input.count() > 0 and await senha_input.is_visible():
                user_input = page.locator("input[type='text'], input[name='login']").first
                await user_input.fill(data.usuario)
                await senha_input.fill(data.senha)
                await page.wait_for_timeout(500)
                botao = page.locator("button:has-text('Entrar'), button[type='submit']").first
                if await botao.count() > 0:
                    await botao.click()
                else:
                    await senha_input.press("Enter")
                # aguarda o Angular processar o login e montar o menu (até 30s)
                for _ in range(30):
                    await page.wait_for_timeout(1000)
                    if await page.locator("po-menu, .po-menu-item").count() > 0:
                        break
                await page.wait_for_timeout(2000)
                # agora navega para o plano — o token já está salvo no Angular
                await page.goto(data.url_plano)
            log.append("✅ Login realizado")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        log.append("📋 Abrindo o plano de aula...")
        try:
            # espera o Angular montar a tabela (tenta a cada segundo por até 60s)
            log.append("⏳ Aguardando tabela carregar...")
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
                corpo = await page.evaluate("() => document.body.innerText.trim().slice(0, 300)")
                log.append(f"🧭 Conteúdo da página: {corpo}")
                raise RuntimeError("a tabela de aulas não carregou — confira o link do plano de aula.")
            log.append(f"📚 {total} aulas encontradas")
        except Exception as e:
            log.append(f"❌ ERRO ao abrir o plano de aula: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        # ---- Preenche cada aula vazia ----
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
                btn = page.locator("table tbody tr").nth(i).locator("text=Editar")
                if await btn.count() == 0:
                    log.append(f"⏭️ Aula {numero_aula} sem botão Editar — pulando")
                    continue
                await btn.scroll_into_view_if_needed()
                await btn.click()
                await page.wait_for_timeout(1200)

                alvo = page.locator("po-modal textarea, [role='dialog'] textarea, dialog textarea").first
                await alvo.wait_for(timeout=8000)
                await alvo.click()
                await alvo.fill(conteudo)
                await alvo.dispatch_event("input")
                await alvo.dispatch_event("change")
                await page.wait_for_timeout(400)

                salvar = page.locator(
                    "po-modal button:has-text('Salvar'), [role='dialog'] button:has-text('Salvar')"
                ).first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(1500)

                preenchidas += 1
                log.append(f"✏️ Aula {numero_aula} — {conteudo[:50]}")
            except Exception as e:
                log.append(f"⚠️ Erro na aula {numero_aula}: {e}")
                break

        log.append(f"📊 {preenchidas} aulas gravadas")
        log.append("🏁 Automação Salesiano finalizada!")
        log.append("__CONCLUIDO__")
        await browser.close()

        log.append("🔐 Fazendo login no Portal do Professor (Totvs RM)...")
        try:
            await page.goto(data.url_portal)
            try:
                await page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                pass
            await page.wait_for_timeout(2000)

            senha_input = page.locator("input[type='password'], input[name='password']").first
            if await senha_input.count() > 0 and await senha_input.is_visible():
                # usuário: campo de login do po-page-login (Totvs) ou genérico
                user_input = page.locator(
                    "input[name='login'], po-login input, "
                    "input[name='user' i], input[name='username' i], "
                    "form:has(input[type='password']) input[type='text'], "
                    "input[id*='user' i], input[type='text']"
                ).first
                # preenche via JS para garantir que o Angular registra o valor
                await page.evaluate("""([sel_user, sel_pass, usuario, senha]) => {
                    const setVal = (sel, val) => {
                        const el = document.querySelector(sel);
                        if (!el) return;
                        const nativeSet = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeSet.call(el, val);
                        el.dispatchEvent(new Event('input', {bubbles: true}));
                        el.dispatchEvent(new Event('change', {bubbles: true}));
                    };
                    setVal(sel_user, usuario);
                    setVal(sel_pass, senha);
                }""", [
                    await user_input.evaluate("el => el.tagName.toLowerCase() + (el.name ? '[name=' + el.name + ']' : '') || 'input'"),
                    "input[type='password']",
                    data.usuario,
                    data.senha
                ])
                await user_input.click()
                await user_input.type(data.usuario, delay=80)
                await senha_input.click()
                await senha_input.type(data.senha, delay=80)
                await page.wait_for_timeout(800)

                botao = page.locator(
                    "button:has-text('Entrar'), button[type='submit'], button:has-text('Acessar'), "
                    "button:has-text('Login'), input[type='submit']"
                ).first
                if await botao.count() > 0:
                    await botao.click()
                else:
                    await senha_input.press("Enter")

                # sucesso = menu lateral apareceu E URL saiu do login (até 40s)
                logado = False
                for _ in range(40):
                    await page.wait_for_timeout(1000)
                    url_atual = page.url
                    tem_menu = await page.locator(".po-menu-item, po-menu").count() > 0
                    if tem_menu and "login" not in url_atual.lower():
                        logado = True
                        break
                if not logado:
                    avisos = await page.evaluate(
                        """() => Array.from(document.querySelectorAll('po-toaster, .po-toaster, [class*=error i], [class*=invalid i], [role=alert], .po-field-container-bottom-text-error'))
                            .map(e => e.innerText.trim()).filter(t => t).slice(0, 5)"""
                    )
                    for a in avisos:
                        log.append("🧭 aviso do portal: " + a)
                    corpo = await page.evaluate("() => document.body.innerText.trim().slice(0, 300)")
                    log.append("🧭 texto da página: " + corpo)
                    raise RuntimeError("o portal não abriu após o login — veja as linhas 🧭 acima.")
                await page.wait_for_timeout(2000)
            log.append("✅ Login realizado")
        except Exception as e:
            log.append(f"❌ ERRO no login: {e}")
            log.append("__ERRO__")
            log.append("__CONCLUIDO__")
            await browser.close()
            return

        async def abrir_diario():
            log.append("📒 Abrindo o Diário de Classe...")
            try:
                await page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            candidatos = [
                "div.po-menu-item[aria-label='Diário de classe']",
                ".po-menu-item:has(.an-book-bookmark)",
                "a:has-text('Diário de classe')",
                "[aria-label*='Diário' i]",
                "[title*='Diário' i]",
                "a[href*='diary' i]",
                "a[href*='diario' i]",
                "a[href*='classdiary' i]",
                "a[href*='teacherdiary' i]",
            ]
            # o app Angular pode demorar para montar a tela após o login: espera até 30s
            for espera in range(30):
                for sel in candidatos:
                    loc = page.locator(sel).first
                    if await loc.count() > 0:
                        try:
                            await loc.click(timeout=5000)
                            await page.wait_for_timeout(3000)
                            return
                        except Exception:
                            continue
                await page.wait_for_timeout(1000)

            # fallback: 2º ícone do menu lateral (home é o 1º)
            for sel in ["po-menu a", ".po-menu-item", "nav a", "aside a"]:
                icones = page.locator(sel)
                if await icones.count() >= 2:
                    try:
                        await icones.nth(1).click(timeout=5000)
                        await page.wait_for_timeout(3000)
                        return
                    except Exception:
                        continue

            # diagnóstico: mostra o que existe na página para calibrar o seletor
            log.append("🧭 Página atual: " + page.url)
            itens = await page.evaluate(
                """() => Array.from(document.querySelectorAll('a, [aria-label], .po-menu-item, button')).slice(0, 30).map(e =>
                    e.tagName + ' | ' + (e.getAttribute('aria-label') || e.title || e.innerText || '').trim().slice(0, 40)
                ).filter(t => t.split('|')[1].trim())"""
            )
            for l in itens:
                log.append("🧭 item: " + l)
            corpo = await page.evaluate("() => document.body.innerText.trim().slice(0, 300)")
            log.append("🧭 texto da página: " + corpo)
            raise RuntimeError("não encontrei o menu 'Diário de classe' — me envie as linhas 🧭 do log")

        async def abrir_plano_da_turma(turma: str):
            log.append(f"🔎 Procurando a turma {turma}...")

            # Aceita "GE09EM1A", "1A", "1º A", "1ª A", "primeiro a"...
            t = turma.upper().strip()
            ordinais = {"PRIMEIRO": "1", "SEGUNDO": "2", "TERCEIRO": "3",
                        "PRIMEIRA": "1", "SEGUNDA": "2", "TERCEIRA": "3"}
            for nome, num in ordinais.items():
                t = t.replace(nome, num)
            m = re.match(r"^(\d)\s*[ºª°]?\s*(?:ANO|SERIE|SÉRIE)?\s*([A-Z])$", t)
            serie_num, letra = (m.group(1), m.group(2)) if m else (None, None)

            async def achar_linha():
                # 1) busca pelo código exato
                linha = page.locator("table tbody tr", has_text=turma).first
                if await linha.count() > 0:
                    return linha
                # 2) busca por série + letra final do código (ex.: "2ª SÉRIE" + código terminando em A)
                if serie_num:
                    todas = page.locator("table tbody tr")
                    for j in range(await todas.count()):
                        cand = todas.nth(j)
                        texto = (await cand.inner_text()).upper()
                        if f"{serie_num}ª SÉRIE" in texto or f"{serie_num}º ANO" in texto:
                            cod = re.search(r"\b[A-Z]{2}\d{2}[A-Z]+\d[A-Z]\b", texto)
                            if cod and cod.group(0).endswith(letra):
                                return cand
                return None

            linha_turma = None
            for tentativa in range(10):
                linha_turma = await achar_linha()
                if linha_turma is not None:
                    break
                # tenta carregar mais resultados, se existir
                mais = page.locator("text=Carregar mais resultados").first
                if await mais.count() > 0 and await mais.is_visible():
                    await mais.click()
                await page.wait_for_timeout(1500)
            if linha_turma is None:
                raise RuntimeError(
                    f"Turma {turma} não encontrada no Diário de Classe. "
                    "Use o código da coluna 'Cód. Turma' (ex.: GE09EM2A) ou o formato '2A' / '2ª A'."
                )

            # clica nos "..." da linha
            mais_acoes = linha_turma.locator(
                "i.an-dots-three, .po-icon-more, [class*='more'], po-icon, span:has-text('...')"
            ).last
            await mais_acoes.scroll_into_view_if_needed()
            await mais_acoes.click()
            await page.wait_for_timeout(800)

            plano = page.locator(
                ".po-item-list-label:has-text('Plano de aula'), text=Plano de aula"
            ).first
            await plano.wait_for(timeout=8000)
            await plano.click()
            await page.wait_for_timeout(3000)
            log.append("✅ Plano de aula aberto")

        async def filtrar_e_pesquisar():
            log.append(f"🗓️ Selecionando a etapa '{data.etapa}'...")
            # abre os filtros se estiverem recolhidos
            filtros = page.locator("text=Filtros").first
            if await filtros.count() > 0:
                combo_visivel = await page.locator("po-combo input, po-select select").first.is_visible()
                if not combo_visivel:
                    await filtros.click()
                    await page.wait_for_timeout(800)

            combo = page.locator("input[name='stepCode'], po-combo input, po-select select, po-lookup input").first
            await combo.wait_for(timeout=8000)
            await combo.click()
            await combo.fill(data.etapa)
            await page.wait_for_timeout(1200)
            opcao = page.locator(f"po-combo li:has-text('{data.etapa}'), .po-combo-item:has-text('{data.etapa}'), li:has-text('{data.etapa}')").first
            await opcao.wait_for(timeout=6000)
            await opcao.click()
            await page.wait_for_timeout(800)

            # preenche o intervalo de datas (Material date range picker)
            log.append(f"📅 Definindo o período {data.data_inicio} a {data.data_fim}...")
            inicio = page.locator("input.mat-start-date, mat-date-range-input input >> nth=0").first
            fim = page.locator("input.mat-end-date, mat-date-range-input input >> nth=1").first
            if await inicio.count() > 0:
                await inicio.click()
                await page.keyboard.press("Control+a")
                await page.keyboard.type(data.data_inicio, delay=50)
                await fim.click()
                await page.keyboard.press("Control+a")
                await page.keyboard.type(data.data_fim, delay=50)
            else:
                campo_data = page.locator("po-datepicker-range input, input[name*='date' i]").first
                await campo_data.wait_for(timeout=8000)
                await campo_data.click()
                await page.keyboard.press("Control+a")
                digitos = re.sub(r"\D", "", data.data_inicio) + re.sub(r"\D", "", data.data_fim)
                await page.keyboard.type(digitos, delay=60)
            await page.keyboard.press("Escape")
            await page.keyboard.press("Tab")
            await page.wait_for_timeout(600)

            await page.locator(
                "button.po-button:has(.po-button-label:has-text('Pesquisar')), "
                "button:has-text('Pesquisar'), po-button:has-text('Pesquisar')"
            ).first.click()
            await page.wait_for_timeout(3000)

        async def preencher_aulas() -> int:
            total_linhas = 0
            for _ in range(20):
                total_linhas = await page.evaluate(
                    "() => document.querySelectorAll('table tbody tr, po-table tbody tr').length"
                )
                if total_linhas > 0:
                    break
                await page.wait_for_timeout(1000)

            if total_linhas == 0:
                raise RuntimeError("a tabela de aulas não carregou.")

            log.append(f"📚 Aulas encontradas na tabela: {total_linhas}")

            # Mapeia quais linhas já têm conteúdo realizado (linha vazia tem só o link 'Editar')
            info_linhas = await page.evaluate(
                """() => Array.from(document.querySelectorAll('table tbody tr')).map(tr => ({
                    links: tr.querySelectorAll('a').length,
                    texto: tr.innerText.trim().slice(0, 60)
                }))"""
            )

            preenchidas = 0
            for i in range(total_linhas):
                numero_aula = i + 1
                if numero_aula < data.aula_inicio:
                    continue
                if info_linhas[i]["links"] >= 2:
                    log.append(f"⏭️ Aula {numero_aula} já tem conteúdo — pulando")
                    continue
                conteudo = topico_da_aula(preenchidas)
                if conteudo is None:
                    log.append("✅ Todos os tópicos foram usados")
                    break
                try:
                    btn = page.locator("table tbody tr").nth(i).locator("text=Editar")
                    await btn.wait_for(timeout=10000)
                    await btn.scroll_into_view_if_needed()
                    await btn.click()
                    await page.wait_for_timeout(1200)

                    textarea = page.locator(
                        "label:has-text('Conteúdo realizado') + textarea, "
                        "label:has-text('Conteudo realizado') + textarea, "
                        "label:has-text('Conteúdo') ~ textarea"
                    ).first
                    fallback = page.locator(
                        "po-modal textarea, dialog textarea, [role='dialog'] textarea"
                    ).first
                    try:
                        await textarea.wait_for(timeout=5000)
                        alvo = textarea
                    except Exception:
                        await fallback.wait_for(timeout=5000)
                        alvo = fallback

                    await alvo.click()
                    await alvo.fill(conteudo)
                    await alvo.dispatch_event("input")
                    await alvo.dispatch_event("change")
                    await page.wait_for_timeout(400)

                    salvar = page.locator(
                        "po-modal button:has-text('Salvar'), dialog button:has-text('Salvar'), "
                        "[role='dialog'] button:has-text('Salvar')"
                    ).first
                    await salvar.wait_for(timeout=5000)
                    await salvar.click()
                    await page.wait_for_timeout(1500)

                    preenchidas += 1
                    log.append(f"✏️ Aula {numero_aula} — {conteudo[:50]}")
                except Exception as e:
                    log.append(f"⚠️ Erro na aula {numero_aula}: {e}")
                    break
            return preenchidas

        # ---- Processa cada turma informada (mesmos tópicos para todas) ----
        turmas = [t.strip().upper() for t in re.split(r"[,;]+", data.turma) if t.strip()]
        total_geral = 0
        turmas_ok = 0
        for turma in turmas:
            log.append(f"━━━ Turma {turma} ━━━")
            try:
                await abrir_diario()
                await abrir_plano_da_turma(turma)
                await filtrar_e_pesquisar()
                gravadas = await preencher_aulas()
                total_geral += gravadas
                turmas_ok += 1
                log.append(f"📊 Turma {turma}: {gravadas} aulas gravadas")
            except Exception as e:
                log.append(f"❌ ERRO na turma {turma}: {e}")

        log.append(f"📊 Total: {total_geral} aulas gravadas em {turmas_ok} de {len(turmas)} turma(s)")
        log.append("🏁 Automação Salesiano finalizada!")
        if turmas_ok == 0:
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
