# SóDigita — Contexto do Projeto

## O Produto
**SóDigita** (`sodigita.com.br`) — automação de tarefas repetitivas para professores brasileiros.
- Automatiza: preenchimento de diário, lançamento de notas e registro de frequência
- Cliente: professor individual (não escola)
- Tecnologia: Python + Playwright (headless Chromium) + FastAPI + SSE
- Canal principal: WhatsApp ou site

## Planos e Preços
| Plano | Inclui | Preço |
|-------|--------|-------|
| Diário | Preenchimento do diário de classe | R$ 9,90/mês |
| Completo | Diário + Frequência + Notas | R$ 19,90/mês |

**Decisões de precificação (01/07/2026):**
- Sempre mês a mês — sem anual. Projeto depende de sistemas de terceiros que podem mudar.
- Professor começa pelo Diário e faz upgrade quando vê valor
- Sazonalidade: uso pausa nov–jan (diários fecham). Professor cancela naturalmente, retorna em fev.
- Meta: 100 prof. Diário (R$990) + 30 upgrade Completo (R$298) = ~R$1.290/mês
- Sem plano fundador permanente — era incentivo de entrada, não modelo sustentável

**Comunicação honesta com o professor:**
> "Cobramos mês a mês porque somos honestos: trabalhamos com sistemas de terceiros que não controlamos. Se algo mudar, você não perde nada."

## Status por Sistema
- **ActiveSoft/SIGA** ✅ — funciona pelo site (Render), diário completo validado
- **Salesiano (TOTVS RM)** ⚠️ — scripts .py locais funcionam; versão web com problema de navegação Angular (token perdido)
- **SIAE** ✅ — funcionando via chat (robô WhatsApp). Login OK, aulas registradas, presença registrada
- **Infodat** ✅ — funcionando via chat. Login com retry 3x, turmas hardcoded (017A031/017B031 Colégio Arqui), screenshot de confirmação após cada registro
- **SESI** 🚧 — em desenvolvimento

## Infraestrutura
- **Render.com** (free plan) — hospeda o backend FastAPI + Playwright
- **Domínio:** sodigita.com.br apontado para o Render
- **UptimeRobot** ✅ — configurado, ping a cada 5 min para evitar hibernação
- **Supabase** ✅ — projeto "Sodigita" criado, tabelas criadas, chave configurada no Render
- **Branch de desenvolvimento:** `claude/quirky-hamilton-4pm1s`
- **Branch principal:** `main`
- Deploy automático a cada push (Docker + Playwright/Chromium, ~5 min)

## Arquivos Principais
- `backend/main.py` — toda a lógica de automação (SIAE, Active, Salesiano, Infodat, SESI) + endpoints de chat/CEO/gerentes/design
- `frontend/index.html` — landing page redesenhada (minimalista, fundo branco)
- `frontend/logo.png` — logo oficial com fundo branco
- `frontend/active.html` — tela do ActiveSoft
- `frontend/salesiano.html` — tela do Salesiano
- `frontend/chat.html` — chat WhatsApp simulado para professores registrarem aulas
- `frontend/ceo.html` — Cláudia, CEO IA que coordena os 3 gerentes
- `frontend/manager.html` — Gerente de Projetos IA
- `frontend/marketing.html` — Gerente de Marketing IA
- `frontend/negocios.html` — Gerente de Negócios IA

## Plano Gerenciado — Terceirização Total (01/07/2026)
Professor manda as informações por WhatsApp (turma, conteúdo, notas, faltas) e o Luth opera o sistema por ele. Professor não precisa saber que existe robô.

| Modalidade | Quem opera | Preço |
|-----------|------------|-------|
| Self-service Diário | Professor pelo chat | R$ 9,90/mês |
| Self-service Completo | Professor pelo chat | R$ 19,90/mês |
| Gerenciado | Luth faz por ele | R$ 49,90/mês |

**Público-alvo do plano gerenciado:** professores mais velhos, avessos à tecnologia, que preferem delegar tudo.

**Como funciona:**
- Professor manda foto da lista de notas, lista de faltas ou texto com conteúdo
- Luth (ou futuramente um assistente) opera o sistema e registra
- Professor recebe confirmação com screenshot

**Robô Rebeca — identificação de perfil:**
Durante a conversa de vendas, a Rebeca deve identificar:
- Professor tech-friendly → direcionar para self-service
- Professor avesso à tecnologia / mais velho → oferecer plano gerenciado
- Objeção "não sei usar WhatsApp" → argumento para gerenciado
- Objeção de preço → mostrar economia de tempo (2h/semana × R$/hora do professor)

**Escalabilidade:** começa com a equipe operando, depois contrata assistente quando MRR > R$1.500

## Equipe SóDigita (consultores fictícios da marca)
A empresa não tem rosto individual — os consultores são personagens da marca.

| Consultor | Papel | Canal |
|-----------|-------|-------|
| **Rebeca** | Robô de vendas — aborda professores, identifica perfil, fecha contrato | WhatsApp / chat |
| **Ricardo** | Gerente comercial — abordagem em grupos, escolas particulares | WhatsApp grupos |
| **Cledson** | Suporte técnico — resolve problemas, bugs, dúvidas técnicas | WhatsApp direto |
| **Lucas** | Onboarding — cadastro, primeiros passos, orienta self-service | Chat / site |
| **Miguel** | Financeiro — cobranças, renovações, cancelamentos | WhatsApp |
| **Maitê** | Marketing — Instagram, conteúdo, Reels, calendário | Instagram |

## Decisões de Negócio
- Foco atual: SIAE + Infodat via chat/WhatsApp
- Mercado estimado: ~43.500 professores em sistemas compatíveis
- Canal de aquisição: grupos WhatsApp de professores + Instagram + indicação
- Meta curto prazo: 50 clientes pagantes antes de contratar funcionário
- B2C direto (professor individual) como foco principal por ora
- **Lançamento oficial: agosto 2026** — professores voltam das férias
- Sazonalidade: produto ativo fev–out, pausa nov–jan (diários fecham)
- Sempre mês a mês — sem plano anual (projeto depende de sistemas de terceiros)
- Sem automação de seguidores no Instagram — risco de ban
- Concorrência: **nenhuma direta** — ninguém faz automação via WhatsApp nos sistemas existentes para professor individual
- Preços sobem com o tempo: R$9,90→R$19,90 (fev/27) →R$29,90 (2028). Quem entrou no preço antigo recebe aviso com 30 dias — sem trava permanente (exceto os 50 fundadores originais se houver)

### Decisão — Preenchimento de Bimestre Completo (01/07/2026)
**Problema:** alguns sistemas permitem preencher o bimestre inteiro de uma vez. Professor pagaria R$9,90, preencheria 3 meses, cancelaria.

**Decisão:** NÃO oferecer preenchimento de bimestre pelo chat. Apenas aula a aula.
- Tela `/aulas.html` (modo bimestre) disponível **somente para plano Completo ativo** — professor que cancelar perde acesso imediatamente
- Motivação extra: a maioria dos sistemas escolares exige que o conteúdo bata com a data real da aula — bimestre antecipado pode gerar inconsistência no diário

## Identidade Visual
- **Logo:** S com gradiente roxo (#7C5CFF) → verde-água (#00D4AA), texto "SóDigita" em cinza escuro
- **Cores:** roxo #7C5CFF, verde-água #00D4AA, fundo branco
- **Nome nos vídeos/anúncios:** `SoDigita` (sem acento — evita distorção de fonte)
- **Nome no site e logo oficial:** `SóDigita` (com acento)
- **Tamanho do logo:** 400x120px, fundo branco, PNG

## Marketing — Produzido em 19/06/2026
- 13 ideias de anúncios (Reels 15s) criadas — estilo antes/depois emocional
- Briefings de design para cada anúncio
- Calendário de conteúdo julho 2026 completo
- 2 posts prontos para o feed do Instagram
- Script de stories (4 partes)
- Script de abordagem para professores no WhatsApp
- Prompts para Gemini gerar os Reels (estilo vídeo 1 — professora no sofá)

### Prompts dos Reels (estilo base):
> *"Create a 15-second Instagram Reels video. Scene 1 (0-5s): A tired Brazilian teacher sitting on a couch on Sunday night, yellow lamp light, laptop open showing a school system. White bold text overlay: 'Mais um domingo no diário?' Scene 2 (5-10s): Close up of hand holding smartphone, opening WhatsApp, typing a quick message. Dark background, phone light illuminating the face. Scene 3 (10-15s): Phone screen showing green ✅ and text 'Diário preenchido!'. Fade to purple background (#7C5CFF) with SoDigita logo centered. Bold white sans-serif font throughout. Soft positive background music in the style of Red Hot Chili Peppers — funky guitar riff, energetic but not aggressive, instrumental only, no lyrics. Realistic cinematic style, warm Brazilian home atmosphere."*

**Variações de personagem:**
- Anúncio 1: professora no sofá, domingo à noite
- Anúncio 2: professora jovem na escrivaninha
- Anúncio 3: professor homem mais velho em sala de aula

## Mensagem de Boas-vindas — Professores Beta (gratuito)

> *"[Nome], seja bem-vindo ao SóDigita! 🎉*
>
> *Você é um dos nossos primeiros professores e isso significa muito pra gente.*
>
> *Estamos em fase de testes e você vai nos ajudar a construir algo que vai devolver o tempo do professor — pra dar aula, não pra ficar na frente do computador.*
>
> *Seu acesso é completamente gratuito. Em troca, só pedimos sua opinião honesta.*
>
> *Veja o que já funciona e o que vem por aí:*
>
> *✅ Diário de classe — já disponível. Manda a turma e o conteúdo, a gente registra.*
>
> *🔜 Frequência — em breve. Você manda o nome dos alunos que faltaram, a gente marca no sistema.*
>
> *🔜 Notas — em breve. Você manda uma foto da sua lista de notas e a gente lança no sistema, respeitando o formato da sua escola (AV1, AV2, bimestral...).*
>
> *Juntos a gente faz o chato por você. 🙏"*

## Script de Abordagem — Grupos de WhatsApp (versão aprovada)

> *"Nós criamos uma automação que leva o que você digita no WhatsApp direto pro seu sistema escolar.*
>
> *Diário, frequência e nota — tudo pelo WhatsApp.*
>
> *Genuinamente sergipano. Feito por professores para professores. 👨‍🏫*
>
> *SIAE, Infodat, ActiveSoft, Totvs RM. 30 segundos. R$9,90/mês.*
>
> *Quem quiser testar grátis, me chama. 👇"*

## Script de Abordagem — WhatsApp
**Para professor conhecido:**
> "Oi [nome]! Tô testando uma coisa que fiz e quero tua opinião honesta. Criei um robô que preenche o diário escolar automaticamente pelo WhatsApp — você manda o conteúdo da aula e ele registra no sistema pra você. Usa [SIAE/Infodat], certo? Me deixa te mostrar funcionando?"

**Para grupo de professores:**
> "Professores, desenvolvi uma ferramenta que preenche o diário escolar automático pelo WhatsApp. Você manda o conteúdo da aula, a gente registra no sistema. Funciona com SIAE e Infodat. Tô abrindo pra 50 professores com preço de fundador — R$9,90/mês. Quem quiser testar grátis essa semana, me chama no privado."

## Custo de API por Professor

| Item | Valor |
|------|-------|
| Modelo usado | Claude Haiku 4.5 |
| Custo de entrada | US$ 0,80 / 1M tokens |
| Tokens por conversa (média) | ~1.000 tokens |
| Custo por conversa | ~US$ 0,001 (< R$ 0,01) |
| Conversas por professor/mês (estimado) | ~30 |
| Custo de API por professor/mês | ~US$ 0,03 (< R$ 0,30) |
| Receita por professor/mês | R$ 9,90 |
| **Margem de API** | **~97%** |

Referência: US$ 0,45 gasto nos primeiros dias de testes intensivos (junho/2026).

## Metas de Receita
| Mês | Diário (R$9,90) | Completo (R$19,90) | MRR | Custo infra |
|-----|-----------------|---------------------|-----|-------------|
| Ago 2026 | 15 | 0 | R$ 149 | R$ 0 (free) |
| Set 2026 | 30 | 5 | R$ 396 | R$ 204 (Render+ZAPI) |
| Out 2026 | 60 | 15 | R$ 893 | R$ 204 |
| Nov 2026 | — pausa sazonalidade — | | | |
| Fev 2027 | 80 | 25 | R$ 1.289 | R$ 204 |
| Abr 2027 | 100 | 30 | R$ 1.587 | R$ 204 |

## Automação de Marketing — Roadmap
- [ ] Gemini gera imagem/vídeo a partir de descrição do post (endpoint /design — em desenvolvimento)
- [ ] Meta Business Suite API: postagem automática no Instagram (requer conta business aprovada)
- [ ] Fluxo completo: descreve → IA gera imagem → agenda → posta sozinho

## Próximas Integrações Planejadas
- [ ] Z-API: conectar robô ao WhatsApp real (~R$50/mês)
- [ ] Cláudia: memória persistente entre conversas usando Supabase ✅ código pronto, aguarda teste
- [ ] Dashboard: métricas reais das automações (total rodadas, taxa de sucesso, por sistema)
- [ ] Fila de automações: evitar sobrecarga com 50+ usuários simultâneos
- [ ] Professor com múltiplas escolas: suportar perfil com SIAE em uma escola e Infodat em outra

## Pendências Técnicas
- [ ] Salesiano: navegação automática login → plano de aula (Angular token perdido com goto)
- [ ] Active: "Execution context destroyed" após Gravar (ainda ocorre ocasionalmente)
- [ ] SIAE: mostrar só as turmas do dia (segunda vs sexta são diferentes)
- [ ] Screenshot: substituir por texto formatado em produção (imagem é cara com muitos usuários)
- [ ] Migrar Render para plano Standard ($25/mês) — Starter tem mesma RAM do free, não resolve
- [ ] Contratar Z-API Start (R$69/mês) para WhatsApp real — fazer antes do lançamento escolas particulares
- [ ] Artigo científico sobre automação na burocracia docente — coletar dados desde já no Supabase

## Limpeza de Código Agendada — APÓS lançamento (após 16/07/2026)
⚠️ NÃO executar antes do lançamento — última limpeza quebrou sistemas em produção.
Itens identificados em 01/07/2026 (varredura completa do projeto):
- Remover funções Supabase nunca chamadas: `_buscar_professor_supabase`, `_classificar_conversa`, `_salvar_conversa_supabase`, `_salvar_professor_supabase` (linhas 3080–3168, ~90 linhas)
- Remover `import uuid` não utilizado (linha 44)
- Consolidar funções duplicadas: `_sem_acento()` e `norm(s)` definidas 4-5x; `async def achar()` definida 4x
- Deletar páginas órfãs: `gerar_prompt.html`, `gerar_conteudos.html`, `design.html`
- Impacto total estimado: ~150-200 linhas removidas, zero funcionalidade perdida

## Ritual Mensal — Exploração de Ferramentas
Todo mês reservar 30 min para explorar `github.com/hesreallyhim/awesome-claude-code` e avaliar o que vale instalar para o SóDigita. Categorias prioritárias: MCP (integrações), Hooks (segurança), Skills (produtividade).
Próxima avaliação: **01/08/2026** — explorar novas ferramentas + avaliar claude-mem mês 2

## Ferramentas Instaladas
- **claude-mem** ✅ — instalado 16/06/2026. Avaliado 01/07/2026: APROVADO. 92% economia de tokens, continuidade entre sessões funcionando. Não evita bugs de código mas mantém contexto do projeto. Usar `/mem-search` ativamente antes de debugar. Próxima avaliação: 01/08/2026.
- **Supabase** ✅ — instalado 18/06/2026. Tabelas: sessoes_claudia, metricas_automacoes
- **UptimeRobot** ✅ — instalado 19/06/2026
- **Gemini API** ✅ — chave configurada no Render (endpoint /design em desenvolvimento)

## ⚠️ Regras de Segurança — Lição Aprendida em 15/06/2026

> O SIAE funcionava no sábado/domingo. Tentativas de debug em sequência quebraram o login e não conseguimos reverter corretamente. Isso não pode se repetir.

**ANTES de qualquer alteração em código que está funcionando em produção:**
1. Perguntar: "Isso pode quebrar algo que já funciona?" — se sim, avisar o usuário antes de mexer
2. Registrar o commit atual: `git log --oneline -1` — anotar o hash aqui no CLAUDE.md
3. Criar branch de experimento separada — NUNCA debugar direto na branch de dev
4. Só mergear para `main` após confirmar que funcionou

**Se o usuário pedir para voltar ao código anterior:**
- Usar `git revert <hash>` ou `git checkout <hash> -- arquivo` — NUNCA reescrever manualmente

**Histórico de quebras:**
- 15/06/2026: SIAE login quebrou após 15+ commits de debug em sequência. Commit funcionando antes: `c6f5d2e`
- 17/06/2026: Causa raiz identificada — script local usava CPF com máscara `789.626.335-15`, site enviava sem máscara `78962633515`. Corrigido na v2026-06-17.46.

**Lições aprendidas:**
- Sempre comparar o script local que funciona com o código do servidor linha por linha antes de fazer qualquer mudança
- NUNCA usar `replace_all=True` em edições sem verificar se o padrão existe em outros sistemas no mesmo arquivo
- **REGRA INEGOCIÁVEL: NUNCA commitar seletor ou lógica de automação sem o usuário rodar o script .py local e confirmar o output primeiro. Sem exceção.**

## Regras para Novos Scripts
1. Sempre incluir captura de erro com `try/except BaseException` + log em arquivo + `input("ENTER para fechar")`
2. Sempre incluir log em tempo real (arquivo `.txt` gravado a cada print)
3. Login automático embutido (não deixar o professor digitar no terminal)
4. Acentuação completa nos assuntos/tópicos (ç, ã, é, etc.)
5. Comentar no topo o que o script faz e como usar

## Histórico de Scripts por Turma (Salesiano)
- `Historia_Otavio_1ano.py` — 1º ano História, turma 627185, 40 aulas, duplas
- `preencher_diario.py` — mesmo conteúdo (cópia de trabalho)

## Decisões Técnicas (22/06/2026)
- Detecção automática de escola por dia da semana implementada
- Detecção automática de escola por turma: 8A/8B→Vita, 2A/2B→Salesiano, demais→SIAE
- Criptografia AES (Fernet) para login/senha no Supabase — `ENCRYPTION_KEY` no Render
- Painel `/admin.html` com classificação automática de conversas por IA
- Robô de vendas com 3 fases: apresentação → qualificação → cadastro
- Limite de 10 trocas no fluxo de vendas para controlar custo de API
- Sistemas não suportados: coleta nome + sistema, encerra com mensagem de interesse
- Turmas do Prof. Luth salvas no Supabase:
  - Estado (SIAE): seg/sex — 6ºA, 7ºA, 3ªA, 3ªB, 2ªA, 2ªB, 1ªA, 1ª Etapa
  - Vita (ActiveSoft): ter/qua/qui — 8A, 8B
  - Salesiano (Totvs RM): ter/qui — 2A, 2B

## Registro de Horas e Valor Desenvolvido

| Data | Descrição | Horas |
|------|-----------|-------|
| Antes de 2026-06-13 | ActiveSoft diário + notas + frequência; Salesiano scripts locais; SESI login; infraestrutura Render/Docker; frontend base | ~28h |
| 2026-06-13 | Infodat completo; fix bugs; foto de notas Gemini; abas no Active; FAQ; loading animado; sábados letivos; Salesiano → Totvs RM | ~17h |
| 2026-06-14/15 | Cache professor Infodat; code review fixes; debug SIAE login; instalação claude-mem | ~4h |
| 2026-06-18 | Robô conversacional; integração SIAE+Infodat pelo chat; retry login; screenshot; notificações; Cláudia CEO + 3 gerentes IA | ~8h |
| 2026-06-19 | Supabase configurado; UptimeRobot; redesign site; logo; 13 anúncios; calendário marketing; plano de negócios; metas de receita | ~6h |
| 2026-06-21 | Robô de vendas; painel admin CRM; classificação automática de conversas; criptografia AES; mensagem de segurança na senha | ~4h |
| 2026-06-22 | Detecção de escola por dia/turma; perfil completo do Prof. Luth no Supabase; script aprovado para grupos WhatsApp; mensagem beta professores | ~5h |
| 2026-06-24/25 | Redesign completo index.html (hero escuro, stats, two-column form); WhatsApp button pós-cadastro; robô Mariana (vendas); painel admin Kanban + briefing IA; nav global; aulas.html; SEO/OG; copy de confiança senha; mobile fixes | ~8h |
| 2026-06-26 | Copy de confiança para senha (proximidade, força, sergipano); turmas automáticas no SYSTEM_PROMPT | ~2h |
| 2026-07-01 | Suporte a aulas solicitadas (SIAE radio button); screenshot final via polling; robô mais natural (respostas curtas, detecta mensagem incompleta); correção bug fill(None) + justificativa obrigatória | ~3h |
| **TOTAL** | | **~85h** |

### Valor de mercado estimado
| Perfil | Valor/hora | Total |
|--------|-----------|-------|
| Dev júnior | R$ 50/h | R$ 4.250 |
| Dev pleno | R$ 100/h | R$ 8.500 |
| Dev sênior | R$ 200/h | R$ 17.000 |
| Agência | R$ 300/h | R$ 25.500 |

