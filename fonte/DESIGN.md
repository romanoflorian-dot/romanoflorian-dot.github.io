---
name: Floriano Romano — site
version: 0.1.0
direção: "Sintonia" — o espaço como frequência; linhas que se cruzam; texto em sussurro
camadas:
  inicial: Esquina (mapa de cruzamentos)
  obra: Escuta primeiro (o som antecede a imagem)
  rádio: Dial (estações e ruído)
---

# Sistema visual

Nível de maturidade: **L0 → L1**. Não havia sistema anterior. Este arquivo passa a ser a fonte de verdade; os valores estão implementados como variáveis CSS em `assets/css/site.css`.

## 1. Cor

### Primitivas

| Token | Valor | Nota |
|---|---|---|
| `color.paper.100` | `#F1EFEA` | fundo papel |
| `color.paper.050` | `#F7F6F2` | superfície levemente elevada |
| `color.ink.900` | `#151515` | tinta |
| `color.ink.700` | `#3C3A37` | tinta secundária |
| `color.ink.500` | `#6B6762` | texto discreto (4,9:1 sobre papel) |
| `color.ink.200` | `#CFCBC4` | fios e divisórias |
| `color.red.600` | `#C8321E` | sinal: pontos, agulha, play |
| `color.red.700` | `#B42D1B` | sinal em texto pequeno (5,5:1) |
| `color.silver.200` | `#D9DADC` | prata — reflexo |
| `color.silver.400` | `#A7A9AC` | prata — base |
| `color.silver.600` | `#8E9094` | prata — sombra |
| `color.night.900` | `#111111` | fundo noturno (Rádio) |
| `color.night.100` | `#ECE9E2` | texto sobre noite |
| `color.night.400` | `#8E8A84` | texto discreto sobre noite (5,5:1) |
| `color.night.red` | `#E2493A` | sinal sobre noite (4,7:1) |

### Semânticas

| Token semântico | → Primitiva (papel) | → Primitiva (noite / Rádio) |
|---|---|---|
| `color.bg.page` | `paper.100` | `night.900` |
| `color.text.primary` | `ink.900` | `night.100` |
| `color.text.secondary` | `ink.500` | `night.400` |
| `color.line.rule` | `ink.200` | `#3A3836` |
| `color.signal.fill` | `red.600` | `night.red` |
| `color.signal.text` | `red.700` | `night.red` |
| `color.edge` | gradiente prata (`silver.600 → 200 → 400 → 200 → 600`) | — |

Regra: o vermelho indica sempre **onde se está agora**: as obras recentes no mapa, a agulha do dial, o botão de escuta, o ano da obra aberta. Nunca é decoração. As bordas do mapa são **prata**. Não se usam amarelo nem azul.

## 2. Tipografia

| Papel | Família | Uso |
|---|---|---|
| `type.mark` | Jura 500, caixa alta, espaçamento 0,3em | assinatura do nome |
| `type.name` | Instrument Serif itálico | nomes de obras, títulos |
| `type.ui` | Instrument Sans 400 | navegação, parágrafos |
| `type.data` | IBM Plex Mono 400 | anos, fichas técnicas, coordenadas |

Escala (rem, base 16px): `0.75 · 0.875 · 1 · 1.25 · 1.75 · 2.5 · 3.5 · 5`.
Títulos de obra: 2.5–5rem itálico. Fichas: 0.75–0.875rem mono. Linhas de texto: 60–68 caracteres.

## 3. Espaço

Base 4px: `space.1=4 · 2=8 · 3=12 · 4=16 · 6=24 · 8=32 · 12=48 · 16=64 · 24=96 · 32=128`.
Margem lateral: 16px no celular, 64px a partir de 900px, 140px a partir de 1400px.

## 4. Mapa Esquina — múltiplos pontos de vista

O mapa usa os recursos de troca de plano dos desenhos do artista (fita isolante, 2007– ; Esquinas I–X, 2023). Código em `mapa.py` (geometria) e `assets/js/mapa.js` (movimento).

- **Pontos de fuga**: cinco sistemas de linhas (A, B, C, D, F), cada um um ponto de vista; vários ficam fora do quadro. O feixe B converge logo além da borda direita; o leque C sobe de baixo; D dá verticais de elevação.
- **Vértice interno**: um leque denso nasce na obra Esquina (sistema E) e passa um pouco do ponto, como a fita.
- **Espessura por plano**: `0.6–1` fundo · `1.4–2.2` meio · `≥ 3` frente. A linha da frente interrompe a de trás (contorno cor de papel).
- **Planos dobrados**: triângulos e quadriláteros com vértices nas obras; as arestas passam do vértice.
- **Linhas que começam ou terminam dentro do quadro** (frações do trecho visível).
- **Esfera**: o desenho existe em 3D dentro de um elipsoide do tamanho do quadro. Cada obra é um ponto (profundidade `z` em `mapa.py`); cada linha é uma corda (passa por uma obra e por um ponto de fuga no espaço) ou aresta de plano. O cursor gira a esfera em torno do eixo vertical — 220° de uma borda à outra —; sem cursor, uma volta a cada 100 s. O que está atrás fica mais claro e os nomes de trás se apagam; parado sobre uma obra. Um meridiano prateado (círculo de compasso) gira junto. Sem movimento com `prefers-reduced-motion`.
- **Densidade e traço**: referência no desenho a lápis de 2026 — poucos traços soltos, planos fechados que se sobrepõem, traço duplo em alguns lados, a Esquina como vértice de onde partem linhas, uma ponta longa e fina. Cerca de 37 linhas; não acrescentar linhas finas.
- **Rótulos na página inicial**: só nome e ano; os prêmios ficam nas páginas de obra, no Índice e em Sobre.
- **Hierarquia**: nível 3 (disco vermelho grande) = obras premiadas e centrais (Esquina, Sonar, A Cidade Sonora, Chuveiros Sonoros, Errância); nível 2 = disco vermelho menor; nível 1 = círculo vazado em tinta. Obra premiada recebe anel vermelho.
- **Celular**: composição girada (560 × 1000), com posições próprias em `PV` onde os rótulos colidiriam.

## 5. Componentes

- **Cabeçalho**: assinatura à esquerda, navegação à direita, botão de som. Sem fundo.
- **Mapa Esquina**: SVG; cada nó é um link com rótulo acessível; ao passar, as linhas que o atravessam ficam em evidência e um som curto escapa (se o som estiver ligado).
- **Escuta**: botão circular vermelho, forma de onda em linha fina; imagens surgem conforme se ouve; botão para mostrar as imagens imediatamente.
- **Dial**: faixa graduada horizontal; agulha vermelha; ruído entre estações.
- **Índice**: tabela filtrável por tipo.

## 6. Movimento

Transições de 160–240ms, `ease-out`. Nada pisca. Respeita `prefers-reduced-motion` (sem animação da forma de onda, imagens visíveis de imediato).

## 7. Acessibilidade

Contraste AA verificado para todos os pares texto/fundo acima. Som nunca toca sem ação do visitante. Todo conteúdo visual tem alternativa em texto; o Índice dá acesso a todas as obras sem depender do mapa.
