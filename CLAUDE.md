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

## Status por Sistema
- **ActiveSoft/SIGA** ✅ — funciona pelo site (Render), diário completo validado
- **Salesiano (TOTVS RM)** ⚠️ — scripts .py locais funcionam; versão web com problema de navegação Angular (token perdido)
- **SIAE** ⚠️ — funcionou sábado 14/06 (commit `c6f5d2e`); parou após 15+ commits de debug em sequência na segunda 15/06; causa: código alterado incorretamente, não bloqueio de IP; precisa reverter para `c6f5d2e` e testar no PC pessoal com browser visível
- **SESI** 🚧 — em desenvolvimento

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
- [ ] SIAE: mostrar só as turmas do dia (segunda vs sexta são diferentes) — por enquanto todas aparecem, professor ignora as que não têm aula
- [ ] Cronômetro: recalibrar estimativa de tempo (está descalibrado) + mostrar tempo médio real de execução por sistema (SIAE, Active, etc.)

## Ritual Mensal — Exploração de Ferramentas
Todo mês reservar 30 min para explorar `github.com/hesreallyhim/awesome-claude-code` e avaliar o que vale instalar para o SóDigita. Categorias prioritárias: MCP (integrações), Hooks (segurança), Skills (produtividade).

## Ferramentas Instaladas
- **claude-mem** — instalado em 16/06/2026, testar por 15 dias. Relatório em 01/07/2026: ajudou a lembrar contexto? Reduziu erros?

## ⚠️ Regras de Segurança — Lição Aprendida em 15/06/2026

> O SIAE funcionava no sábado/domingo. Tentativas de debug em sequência quebraram o login e não conseguimos reverter corretamente. Isso não pode se repetir.

**ANTES de qualquer alteração em código que está funcionando em produção:**
1. Perguntar: "Isso pode quebrar algo que já funciona?" — se sim, avisar o usuário antes de mexer
2. Registrar o commit atual: `git log --oneline -1` — anotar o hash aqui no CLAUDE.md
3. Criar branch de experimento separada — NUNCA debugar direto na branch de dev
4. Só mergear para `main` após confirmar que funcionou

**Se o usuário pedir para voltar ao código anterior:**
- Usar `git revert <hash>` ou `git checkout <hash> -- arquivo` — NUNCA reescrever manualmente
- O commit que funcionava fica registrado no status do sistema (ver seção acima)

**Histórico de quebras:**
- 15/06/2026: SIAE login quebrou após 15+ commits de debug em sequência. Commit funcionando antes: `c6f5d2e`
- 17/06/2026: Causa raiz identificada — script local usava CPF com máscara `789.626.335-15`, site enviava sem máscara `78962633515`. Corrigido na v2026-06-17.46.

**Lições aprendidas:**
- Sempre comparar o script local que funciona com o código do servidor linha por linha antes de fazer qualquer mudança
- Quando algo funciona localmente mas não no servidor, a diferença está nos dados enviados (formato, máscara, encoding) — não no seletor
- NUNCA usar `replace_all=True` em edições sem verificar se o padrão existe em outros sistemas no mesmo arquivo
- Quando o usuário reporta falha, primeiro perguntar "o script local ainda funciona?" — se sim, a diferença está no servidor
- 17/06/2026: NUNCA assumir anti-bot sem evidência — o problema do SIAE era senha errada no autocomplete do navegador
- Seletores novos (ex: `#btnConfirmar`, `button[data-target]`) DEVEM ser testados localmente com um script `.py` antes de commitar — evita ciclos de deploy desnecessários

## Regras para Novos Scripts
1. Sempre incluir captura de erro com `try/except BaseException` + log em arquivo + `input("ENTER para fechar")`
2. Sempre incluir log em tempo real (arquivo `.txt` gravado a cada print)
3. Login automático embutido (não deixar o professor digitar no terminal)
4. Acentuação completa nos assuntos/tópicos (ç, ã, é, etc.)
5. Comentar no topo o que o script faz e como usar

## Histórico de Scripts por Turma (Salesiano)
- `Historia_Otavio_1ano.py` — 1º ano História, turma 627185, 40 aulas, duplas
- `preencher_diario.py` — mesmo conteúdo (cópia de trabalho)

## Registro de Horas e Valor Desenvolvido

> Atualizar a cada sessão de trabalho.

| Data | Descrição | Horas |
|------|-----------|-------|
| Antes de 2026-06-13 | ActiveSoft diário + notas + frequência; Salesiano scripts locais; SESI login; infraestrutura Render/Docker; frontend base | ~28h |
| 2026-06-13 | Infodat completo (login, turmas, diário); fix bugs de acento/AJAX; foto de notas Gemini; abas no Active; FAQ na home; loading animado; sábados letivos Infodat; resumo de aulas em tempo real; Salesiano → Totvs RM | ~17h |
| 2026-06-14/15 | Cache professor Infodat; code review fixes; debug SIAE login (não resolvido); instalação claude-mem | ~4h |
| **TOTAL** | | **~49h** |

### Valor de mercado estimado
| Perfil | Valor/hora | Total |
|--------|-----------|-------|
| Dev júnior | R$ 50/h | R$ 2.250 |
| Dev pleno | R$ 100/h | R$ 4.500 |
| Dev sênior | R$ 200/h | R$ 9.000 |
| Agência | R$ 300/h | R$ 13.500 |
