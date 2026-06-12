# SóDigita — Contexto do Projeto

## O Produto
**SóDigita** (`sodigita.com.br`) — automação de tarefas repetitivas para professores brasileiros.
- Automatiza: preenchimento de diário, lançamento de notas e registro de frequência
- Cliente: professor individual (não escola)
- Tecnologia: Python + Playwright (headless Chromium) + FastAPI + SSE

## Planos e Preços
| Plano | Inclui | Preço |
|-------|--------|-------|
| Diário | Preenchimento do diário de classe | R$ 19,90/mês |
| Notas | Lançamento de notas | R$ 19,90/mês |
| Faltas | Registro de frequência | R$ 19,90/mês |
| Completo | Diário + Notas + Faltas | R$ 39,90/mês |

## Sistemas Suportados
- **ActiveSoft/SIGA** — usado pelo Colégio Vita e CEFF
- **Salesiano (TOTVS RM)** — Portal do Professor Angular (hash routing)
- **SIAE** — Seduc Sergipe
- **SESI** — em desenvolvimento

## Infraestrutura
- **Render.com** (free plan) — hospeda o backend FastAPI + Playwright
- **Domínio:** sodigita.com.br apontado para o Render
- **Branch de desenvolvimento:** `claude/quirky-hamilton-4pm1s`
- **Branch principal:** `main`
- Deploy automático a cada push (Docker + Playwright/Chromium, ~5 min)

## Arquivos Principais
- `backend/main.py` — toda a lógica de automação (SIAE, Active, Salesiano)
- `frontend/active.html` — tela do ActiveSoft
- `frontend/salesiano.html` — tela do Salesiano
- `frontend/index.html` — landing page / home
- `Notas_Active.py` — script standalone de notas (ActiveSoft, roda local)
- `Historia_Otavio_1ano.py` / `preencher_diario.py` — script standalone do Salesiano (roda local)

## Scripts Standalone (rodam no PC do professor)
Ficam na pasta `diario_auto` na Área de Trabalho do professor.
- Dois cliques para rodar (não precisa de terminal)
- Sempre incluir: captura de erro com log (`notas_log.txt`, `erro_notas.log`) e `input()` no final para janela não fechar
- Login automático já embutido

## Credenciais Conhecidas (apenas para scripts locais)
- **Vita (ActiveSoft):** `Luth5824` / `Luth1801@` — URL: `https://siga01.activesoft.com.br/login/?instituicao=COLEGIOVITA`
- **Salesiano:** URL base: `https://portalprdsalesianos.rm.cloudtotvs.com.br/FrameHTML/web/app/edu/PortalDoProfessor/#/login`

## Decisões Técnicas Importantes
- Angular (Salesiano) usa hash routing — NUNCA usar `page.goto()` após login, usar `window.location.hash`
- ActiveSoft recarrega iframe após cada "Gravar" — re-adquirir frame a cada aula
- Após Gravar no Active: esperar `networkidle` (12s timeout) + 5s extra
- Campos de login: IDs únicos por sistema para evitar colisão (`active_usuario`, `active_senha`)
- SSE timeout: 60s no frontend para recuperar conexões caídas
- Form persistence: localStorage para todos os campos (exceto senha)

## Pendências Técnicas
- [ ] Salesiano: navegação automática login → plano de aula (Angular token perdido com goto)
- [ ] Active: "Execution context destroyed" após Gravar (ainda ocorre ocasionalmente)
- [ ] Active: automatizar navegação completa (Digitação de notas → turma → fase → Consultar)
- [ ] Frequência (Active): clicar nas colunas P → Gravar → Próximo
- [ ] UptimeRobot: configurar ping a cada 5 min para evitar hibernação do Render
- [ ] Cronômetro: recalibrar estimativa de tempo (está descalibrado)

## Regras para Novos Scripts
1. Sempre incluir captura de erro com `try/except BaseException` + log em arquivo + `input("ENTER para fechar")`
2. Sempre incluir log em tempo real (arquivo `.txt` gravado a cada print)
3. Login automático embutido (não deixar o professor digitar no terminal)
4. Acentuação completa nos assuntos/tópicos (ç, ã, é, etc.)
5. Comentar no topo o que o script faz e como usar

## Histórico de Scripts por Turma (Salesiano)
- `Historia_Otavio_1ano.py` — 1º ano História, turma 627185, 40 aulas, duplas
- `preencher_diario.py` — mesmo conteúdo (cópia de trabalho)
