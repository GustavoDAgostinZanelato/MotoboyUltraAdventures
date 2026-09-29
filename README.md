# Motoboy Ultra Adventures

Jogo de plataforma 2D arcade em pixel art, desenvolvido na engine **Construct 2** para a disciplina de Desenvolvimento de Jogos (Engenharia de Software — Centro Universitário UniSATC).

João é um motoboy de aplicativo que precisa cortar caminho por telhados, plataformas suspensas e obstáculos de uma cidade caótica, num cenário entre cyberpunk e fim de tarde, para concluir cada entrega dentro do tempo limite. Quanto mais acrobacias radicais o jogador arrisca no trajeto, mais o lanche se danifica — e, de forma irônica, mais pontos de estilo isso rende no final da fase.

## Pilares de design

- **Ritmo arcade acelerado**: partidas curtas, física de moto responsiva e leitura rápida dos obstáculos.
- **Risco e recompensa**: manobras custam controle e tempo, mas rendem pontuação de estilo.
- **Humor urbano e sátira**: tom irônico sobre a rotina de entregadores de aplicativo.
- **Dois objetivos em tensão**: cumprir o tempo da entrega x maximizar o estrago do lanche por meio de acrobacias.

## Status atual

- Protótipo jogável no Construct 2, com física de moto (comportamento Platform), inclinação no ar ("dar grau") e as animações de Idle, Corrida, Pulo e Empinar em pixel art.
- Cenário inicial da cidade cyberpunk (céu, skyline de prédios e letreiros neon) integrado à Fase 1.
- GDD com as seções de Mecânicas, Narrativa, Estética, Tecnologia e Referências completas; Level Design com a Fase 1 detalhada e o gráfico de ritmo das três fases planejadas.

Em desenvolvimento: Level Design das Fases 2 e 3, sistema de dano do lanche vinculado às acrobacias, HUD funcional (tempo, combo, dano), itens/power-ups, IA dos elementos móveis do cenário e trilha sonora/efeitos sonoros.

## Tecnologias

- **Engine**: Construct 2
- **Arte**: pixel art (sprites originais da equipe)
- **Documentação**: Word / Markdown

## Equipe

| Integrante | Função |
|---|---|
| Artur Bristot | Game Designer / Level Designer |
| Eric Garcia | Sound Designer / Narrative Designer |
| Gabriel Rodolfo | Programador Principal |
| Gustavo D'Agostin | Artista Visual / UI Designer |

## Estrutura do repositório

```
Motoboy Ultra Adventures.caproj   # Projeto principal do Construct 2
Animations/                       # Sprites por objeto/animação (moto, comida, cenário)
Event sheets/                     # Lógica de eventos do jogo
Layouts/                          # Fases/telas do jogo
Files/                            # Assets soltos (ícones, arte de cenário)
Textures/                         # Tilesets de plataforma
```

## Como rodar o projeto

1. Instale o [Construct 2](https://www.construct.net/en/construct-2) (versão r280 ou compatível).
2. Abra o arquivo `Motoboy Ultra Adventures.caproj`.
3. Use "Run Layout" (F5) para rodar o preview no navegador.

## Créditos e referências

Referências de gameplay: Urban Trial Playground, Elasto Mania, Joe Danger, Trials Rising.

---

Projeto acadêmico desenvolvido para a disciplina de Desenvolvimento de Jogos — Centro Universitário UniSATC.
