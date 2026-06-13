# Decisões do Projeto SóDigita

## Produto
- Nome: **SóDigita**
- Domínio: **sodigita.com.br**
- Cliente-alvo: **professor individual** (não escola, não diretor)
- Venda: por WhatsApp inicialmente, depois automatizar com Stripe/Hotmart

## Planos
- Diário: R$ 19,90/mês
- Notas: R$ 19,90/mês
- Faltas: R$ 19,90/mês
- Completo (tudo): R$ 39,90/mês

## Estratégia de Venda
- Landing page no sodigita.com.br → botão "Falar no WhatsApp"
- Primeiros 20-30 assinantes: cobrança manual (PIX)
- Depois: automatizar pagamento recorrente

## Tecnologia
- Site (Render) = melhor para venda (zero instalação, funciona no celular)
- .exe desktop = descartado por enquanto
- Scripts .py locais = fase de validação (professor navega + robô digita)
- Próximo passo: automatizar navegação clique-por-clique → robô faz tudo sozinho na nuvem

## Fluxo de Notas (validado)
- Regra: média AV1+AV2 ≥ 7 → nota alta | abaixo → nota baixa | lista de exceções → nota mínima
- Valores padrão: 5,0 / 4,0 / 3,0
- Professor navega até a lista → ENTER → robô digita tudo

## Sessões por Assunto (para evitar contexto longo)
Abrir sessões separadas para:
- Diário (Salesiano / Active / SIAE)
- Notas
- Frequência/Faltas
- Landing page / produto
- Infraestrutura / deploy

## Pendente para o Produto estar 100% Vendável
1. Automatizar navegação clique-por-clique em cada sistema
2. Tela do app com design SóDigita (logo, cores, nome)
3. Sistema de acesso por plano (controle de quem pode usar o quê)

## To-Do (infraestrutura)
- [ ] UptimeRobot: cadastrar monitor em uptimerobot.com apontando para sodigita.com.br a cada 5 min (evitar hibernação do Render free)
- [ ] Cronômetro: recalibrar estimativa de tempo (descalibrado)
- [ ] Pagamento recorrente: Stripe ou Hotmart (após 20-30 assinantes manuais)
