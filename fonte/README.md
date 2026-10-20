# Floriano Romano — site

Site estático, sem dependências, publicado pelo GitHub Pages.

## Estrutura

- `data/obras.json` — todas as obras, exposições e textos. **É aqui que o conteúdo se edita.**
- `assets/` — estilo (`css/site.css`), comportamento (`js/`) e ícone.
- `media/` — fotos e áudios das obras (criar quando houver arquivos).
- `build.py` — gera o site em `public/` a partir dos dados.
- `DESIGN.md` — sistema visual: cores, tipografia, espaçamento, componentes.

## Camadas

- **Início — Esquina**: mapa de cruzamentos; cada cruzamento é uma obra.
- **Obra — Escuta primeiro**: o som vem antes; as imagens surgem conforme se ouve.
- **Rádio — Dial**: as obras de rádio são estações; entre elas, ruído.

## Acrescentar fotos e áudio a uma obra

Em `data/obras.json`, na obra correspondente:

```json
"audio": "media/esquina/esquina.mp3",
"imagens": [
  {"src": "media/esquina/01.jpg", "alt": "Paredes vermelhas e amarelas na galeria", "credito": "Foto: Nome do fotógrafo"}
]
```

Depois: `python3 build.py`.
