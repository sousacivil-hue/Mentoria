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
- **SIAE** ✅ — funcionando via chat (robô WhatsApp). Login OK, aulas registradas, presença registrada
- **Infodat** ✅ — funcionando via chat. Login com retry 3x, turmas hardcoded (017A031/017B031 Colégio Arqui), screenshot de confirmação após cada registro
- **SESI** 🚧 — em desenvolvimento

## Infraestrutura
- **Render.com** (free plan) — hospeda o backend FastAPI + Playwright
- **Domínio:** sodigita.com.br apontado para o Render
- **Branch de desenvolvimento:** `claude/quirky-hamilton-4pm1s`
- **Branch principal:** `main`
- Deploy automático a cada push (Docker + Playwright/Chromium, ~5 min)

## Arquivos Principais
- `backend/main.py` — toda a lógica de automação (SIAE, Active, Salesiano, Infodat, SESI) + endpoints de chat/CEO/gerentes
- `frontend/active.html` — tela do ActiveSoft
- `frontend/salesiano.html` — tela do Salesiano
- `frontend/index.html` — landing page / home
- `frontend/chat.html` — chat WhatsApp simulado para professores registrarem aulas
- `frontend/ceo.html` — Cláudia, CEO IA que coordena os 3 gerentes
- `frontend/manager.html` — Gerente de Projetos IA
- `frontend/marketing.html` — Gerente de Marketing IA
- `frontend/negocios.html` — Gerente de Negócios IA
- `Notas_Active.py` — script standalone de notas (ActiveSoft, roda local)
- `Historia_Otavio_1ano.py` / `preencher_diario.py` — script standalone do Salesiano (roda local)

## Decisões de Negócio (18/06/2026)
- Foco atual: SIAE + Infodat via chat/WhatsApp
- Mercado estimado: ~43.500 professores em sistemas compatíveis
- Preço: R$19,90/mês por sistema ou R$39,90/mês completo
- Primeiros clientes: R$9,90/mês (desconto 50%) para os 50 primeiros
- Canal de aquisição: grupos WhatsApp de professores + Instagram + indicação
- Meta curto prazo: 50 clientes pagantes antes de contratar funcionário
- B2C direto (professor individual) como foco principal por ora
- Cláudia (CEO IA) é o ponto central de gestão — coordena projetos, marketing e negócios

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
- [ ] SIAE: mostrar só as turmas do dia (segunda vs sexta são diferentes)
- [ ] Cronômetro: recalibrar estimativa de tempo
- [ ] Supabase: memória persistente da Cláudia + métricas de automações
- [ ] WhatsApp API: conectar robô ao WhatsApp real (Evolution API ou Z-API)
- [ ] Professor com múltiplas escolas: suportar perfil com SIAE em uma escola e Infodat em outra
- [ ] Registro de múltiplos dias: professor esqueceu 3 dias → robô pede datas e registra todos
- [ ] Screenshot: substituir por texto formatado em produção (imagem é cara com muitos usuários)

## Ritual Mensal — Exploração de Ferramentas
Todo mês reservar 30 min para explorar `github.com/hesreallyhim/awesome-claude-code` e avaliar o que vale instalar para o SóDigita. Categorias prioritárias: MCP (integrações), Hooks (segurança), Skills (produtividade).

## Ferramentas Instaladas
- **claude-mem** — instalado em 16/06/2026, testar por 15 dias. Relatório em 01/07/2026: ajudou a lembrar contexto? Reduziu erros?
- **Supabase** — a instalar. Vai servir para: memória entre sessões da Cláudia (CEO IA), métricas das automações (quantas rodaram, taxa de sucesso), histórico de professores e conversas.

## Próximas Integrações Planejadas
- [ ] Supabase: criar projeto, configurar tabelas (sessoes_claudia, metricas_automacoes, professores)
- [ ] Cláudia: memória persistente entre conversas usando Supabase
- [ ] Dashboard: métricas reais das automações (total rodadas, taxa de sucesso, por sistema)
- [ ] WhatsApp API (Evolution API ou Z-API): conectar robô do chat ao WhatsApp real

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
- **REGRA INEGOCIÁVEL: NUNCA commitar seletor ou lógica de automação sem o usuário rodar o script .py local e confirmar o output primeiro. Sem exceção. Quebrar essa regra = ciclos desnecessários de deploy que desperdiçam tempo.**

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
| 2026-06-18 | Robô conversacional Claude Haiku via chat.html; integração SIAE+Infodat pelo chat; retry login; screenshot de confirmação; notificações assíncronas; normalização de conteúdo (maiúscula+ponto); Cláudia CEO + 3 gerentes IA (projetos/marketing/negócios); plano de negócios e análise de mercado | ~8h |
| **TOTAL** | | **~57h** |

### Valor de mercado estimado
| Perfil | Valor/hora | Total |
|--------|-----------|-------|
| Dev júnior | R$ 50/h | R$ 2.250 |
| Dev pleno | R$ 100/h | R$ 4.500 |
| Dev sênior | R$ 200/h | R$ 9.000 |
| Agência | R$ 300/h | R$ 13.500 |
