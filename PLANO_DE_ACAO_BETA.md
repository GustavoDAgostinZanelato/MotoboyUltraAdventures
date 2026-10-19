# Motoboy Ultra Adventures — Plano de ação da versão Beta

Base: GDD (versão preliminar) + análise do projeto Construct 2 em 19/10/2026.
Decisões já tomadas pela equipe:

1. **Controles seguem o GDD** (seção 2.2): D/→ acelera, A/← freia, Espaço/W pula, ↑ inclina para trás, ↓ inclina para frente, Esc pausa.
2. **Rotação livre da moto no ar** por enquanto (revisitar a física depois).

## Visão geral dos 9 pontos

| # | Frente | Esforço | Status |
|---|--------|---------|--------|
| 1 | Ciclo de fase (tempo, chegada, vitória, derrota, queda) | Baixo | **Sprint 1 — implementado** |
| 2 | Acrobacias e estilo (ângulo no ar, flips, pouso) | Médio | **Sprint 1 — implementado** |
| 3 | Qualidade do lanche, combo, pontuação e HUD | Médio | **Sprint 1 — implementado** |
| 4 | Obstáculos (espinhos, muros, lombadas, plataformas) | Médio | Sprint 2 (sprites novos + versão inicial na Fase 1 já feitos) |
| 5 | Fases 2 e 3 e transição entre layouts | Alto | Sprint 2 |
| 6 | Menus, pausa e tela de resultado completa | Médio | Sprint 3 (resultado básico já existe) |
| 7 | Áudio (trilha, motor, SFX) | Médio | Sprint 3 |
| 8 | Sprites faltantes, parallax e polimento | Alto | Sprint 3/4 (parallax e arte de cenário já iniciados) |
| 9 | Power-ups, recorde local e narrativa | Baixo | Opcional |

## Sprint 1 — o que foi feito

### 1. Ciclo de fase
- Variáveis globais: `TempoFase`, `TempoRestante`, `Estado` (0 jogando, 1 vitória, 2 tempo esgotado).
- Cronômetro regressivo em MM:SS; vermelho nos últimos 10 s.
- Sprite de **Chegada**: ao tocar com tempo restante, calcula `bônus de tempo + bônus de estilo` e abre o painel de resultado (Enter reinicia).
- **Tempo esgotado**: mensagem e reinício imediato da fase (sem vidas).
- **Queda no vazio**: penalidade de 5 s e retorno ao último ponto seguro do chão.

### 2. Acrobacias e estilo
- Moto dividida em corpo físico (`motoCol`, comportamento Platform, não gira) e sprite visual (`moto`, gira livremente) para a rotação livre não prender a moto no cenário.
- No ar: ↑ gira anti-horário, ↓ gira horário (280°/s). Cada volta completa (≈360°) conta um **flip**.
- No chão: segurar ↑ em movimento = **wheelie** (manobra de estilo).
- **Pouso**: ângulo até 35° do chão é pouso limpo (combo continua e ganha bônus se houve flip); acima disso é pouso desequilibrado (combo zera, −10% de lanche, −1 s).

### 3. Lanche, combo, pontuação e HUD
- `QualidadeLanche` começa em 100% e cai a cada acrobacia: pulo −1, wheelie −0,5/0,5 s, flip −8, pouso ruim −10.
- `Combo` sobe a cada flip e multiplica os pontos de estilo; zera em pouso ruim, espinho ou queda.
- Pontuação final = `floor(tempo restante) × 100` + `pontos de estilo` + `(100 − lanche) × 10`.
- HUD: tempo (esq.), combo (centro), ícone e barra do lanche (dir.), pontos, textos **SMASH!** / **CRUNCH!** / **PERFEITO!**.

## Sprint 2 — próximos passos sugeridos
- Definir efeito oficial dos espinhos (hoje: −3 s, combo zerado e retorno ao ponto seguro) e dos muros (−2 s e rebote).
- Construir Fases 2 e 3 (copiar `Fase1`, trocar `TempoFase` e layout) e ligar `Go to layout` na chegada.
- Lombadas/rampas: calibrar inclinação com a velocidade máxima (400 px/s).
- Plataformas móveis (comportamento Sine).

## Sprint 3 — menus, áudio e polimento
- Menu principal, pausa (Esc), tela de resultado final, créditos.
- Trilha synthwave, motor variando com `motoCol.Platform.Speed`, SFX de pulo/pouso/dano/alerta.
- Sprites faltantes do GDD: freando, flip, 360°, expressões do lanche.

## Decisões pendentes (GDD ainda em aberto)
| Pendência | Proposta adotada provisoriamente |
|-----------|----------------------------------|
| Efeito dos espinhos | −3 s + combo zerado + retorno ao último ponto seguro |
| Muros de colisão | Sólidos; penalidade de tempo fica para o Sprint 2 |
| Power-ups | Fora da beta |
| Recorde local | Fora da beta |

## Arte nova (Sprint 1)
Os tiles do pacote Kenney (uso livre) foram substituídos por arte própria em pixel art, no estilo cyberpunk/entardecer do jogo (paleta dos prédios do cenário: roxos escuros `#1a102e`/`#211438`, neon ciano `#5af0ff`, magenta `#ff5adc`, amarelo `#ffd25a`).
O gerador está em `tools/gerar_sprites.py` — rode `python tools/gerar_sprites.py` para regenerar todos os PNGs:
`chao`, `plataforma`, `bloco`, `espinho`, `lombada`, `muro`, `chegada`, ícone/barra do lanche e painel de resultado.
