import asyncio
import json
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


class TurmaData(BaseModel):
    serie: str
    disciplina: str
    dias: list[str]
    conteudos: list[str]
    metodologia: str


class FormData(BaseModel):
    login: str
    senha: str
    turmas: list[TurmaData]


def build_conteudo_map(turmas: list[TurmaData]) -> dict[str, list[str]]:
    mapa = {}
    for t in turmas:
        chave = t.serie[:3]
        mapa[chave] = t.conteudos
    return mapa


async def run_siae(job_id: str, data: FormData):
    from playwright.async_api import async_playwright

    log = jobs[job_id]

    URL_LOGIN = "https://sso.seduc.se.gov.br/sistemas"
    URL_AULAS = "https://siae.seduc.se.gov.br/siae.diario/Aula/Aulas"

    conteudo_map = build_conteudo_map(data.turmas)
    metodologia_map = {t.serie[:3]: t.metodologia for t in data.turmas}

    def get_conteudo(serie: str, indice: int) -> str:
        for chave, lista in conteudo_map.items():
            if chave in serie:
                if lista:
                    return lista[indice % len(lista)]
        return "Conteudo nao definido"

    def get_metodologia(serie: str) -> str:
        for chave, met in metodologia_map.items():
            if chave in serie:
                return met
        return "Aula expositiva dialogada."

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

        log.append("📋 Acessando lista de aulas...")
        await page.goto(URL_AULAS)
        await page.wait_for_timeout(3000)

        aula_num = 0
        indices_por_serie: dict[str, int] = {}

        while True:
            await page.wait_for_timeout(1000)

            botoes_info = await page.evaluate("""
                () => {
                    const result = [];
                    const btns = document.querySelectorAll('button.btn-primary[onclick^="registrar"]');
                    for (const btn of btns) {
                        const tr = btn.closest('tr');
                        if (!tr) continue;
                        const tds = tr.querySelectorAll('td');
                        const situacao = tds[7] ? tds[7].innerText.trim() : '';
                        const objeto = tds[2] ? tds[2].innerText.trim() : '';
                        const serie = tds[3] ? tds[3].innerText.trim() : '';
                        const onclick = btn.getAttribute('onclick') || '';
                        if (situacao.includes('para registrar') && (objeto === '' || objeto === '-')) {
                            result.push({onclick, serie, situacao});
                        }
                    }
                    return result;
                }
            """)

            if not botoes_info:
                log.append("✅ Todas as aulas preenchidas!")
                break

            alvo = botoes_info[0]
            onclick = alvo["onclick"]
            serie_texto = alvo["serie"]

            match = re.search(r"registrar\((\d+)\)", onclick)
            if not match:
                log.append("❌ ID da aula não encontrado.")
                break
            aula_id = match.group(1)

            chave_serie = serie_texto[:3]
            indice = indices_por_serie.get(chave_serie, 0)
            conteudo = get_conteudo(serie_texto, indice)
            metodologia = get_metodologia(serie_texto)
            indices_por_serie[chave_serie] = indice + 1

            log.append(f"⏳ Aula {aula_num + 1}: {serie_texto[:50]}")

            url_reg = f"https://siae.seduc.se.gov.br/siae.diario/Aula/Registrar/{aula_id}"
            await page.goto(url_reg)
            await page.wait_for_timeout(3000)

            try:
                objeto = page.locator("textarea").nth(0)
                await objeto.wait_for(timeout=6000)
                await objeto.click(click_count=3)
                await objeto.fill(conteudo)
            except Exception as e:
                log.append(f"  ⚠️ Erro ao preencher conteúdo: {e}")

            for sel in ["textarea:nth-of-type(2)", "input[type='text']:not([readonly])"]:
                try:
                    locs = page.locator(sel)
                    if await locs.count() > 0:
                        await locs.first.click()
                        await locs.first.fill(metodologia)
                        break
                except Exception:
                    pass

            try:
                salvar = page.locator("button:has-text('SALVAR'), button:has-text('Salvar'), input[value='SALVAR']").first
                await salvar.wait_for(timeout=5000)
                await salvar.click()
                await page.wait_for_timeout(3000)
            except Exception as e:
                log.append(f"  ⚠️ Erro ao salvar: {e}")
                await page.goto(URL_AULAS)
                await page.wait_for_timeout(2000)
                continue

            aula_num += 1
            log.append(f"✅ Aula {aula_num} salva — {conteudo[:40]}...")

            await page.goto(URL_AULAS)
            await page.wait_for_timeout(2000)

        log.append(f"🎉 Concluído! Total: {aula_num} aulas preenchidas.")
        log.append("__DONE__")
        await browser.close()


@app.post("/executar")
async def executar(data: FormData):
    job_id = str(uuid.uuid4())
    jobs[job_id] = []
    asyncio.create_task(run_siae(job_id, data))
    return {"job_id": job_id}


@app.get("/progresso/{job_id}")
async def progresso(job_id: str):
    async def stream() -> AsyncGenerator[str, None]:
        enviado = 0
        while True:
            logs = jobs.get(job_id, [])
            while enviado < len(logs):
                msg = logs[enviado]
                yield f"data: {json.dumps({'msg': msg})}\n\n"
                enviado += 1
                if msg == "__DONE__":
                    return
            await asyncio.sleep(0.5)

    return StreamingResponse(stream(), media_type="text/event-stream")
