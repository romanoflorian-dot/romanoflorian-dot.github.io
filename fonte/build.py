#!/usr/bin/env python3
"""Gera o site estático de Floriano Romano a partir de data/obras.json.

Uso:  python3 build.py        (escreve em ./public)
"""
import json, os, shutil, html, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).parent
PREVIA = "--previa" in sys.argv  # versão para navegar dentro do Claude (sem iframes externos)
PENDENTES = "--com-pendentes" in sys.argv  # inclui imagens que aguardam aprovação do artista (só para revisão local)
OUT = ROOT / ("revisao" if PENDENTES else ("previa" if PREVIA else "public"))
DATA = json.loads((ROOT / "data" / "obras.json").read_text(encoding="utf-8"))
OBRAS = DATA["obras"]
BY_ID = {o["id"]: o for o in OBRAS}
_IMGS = ROOT / "data" / "imagens.json"
if _IMGS.exists():
    for _id, _lista in json.loads(_IMGS.read_text(encoding="utf-8")).items():
        if _id in BY_ID:
            BY_ID[_id].setdefault("imagens", [])
            BY_ID[_id]["imagens"] = _lista + [i for i in BY_ID[_id]["imagens"] if i not in _lista]
EXPOS = {e["id"]: e for e in DATA["exposicoes"]}
ANO_ATUAL = "2026"

e = html.escape

NAV = [("indice.html", "Índice"), ("exposicoes.html", "Exposições"),
       ("radio.html", "Rádio"), ("textos.html", "Textos"), ("sobre.html", "Sobre")]


def page(title, body, r="", desc="", body_class="", scripts=(), active="", fragmento=False):
    cur = ' aria-current="page"'
    nav = "".join(
        f'<a href="{r}{href}"{cur if href == active else ""}>{label}</a>'
        for href, label in NAV)
    full_title = f"{title} — Floriano Romano" if title else "Floriano Romano"
    desc = desc or "Floriano Romano, artista visual e sonoro. Instalações, objetos, ações urbanas e rádio-arte. Rio de Janeiro."
    js = "".join(f'<script src="{r}assets/js/{s}" defer></script>' for s in ("site.js",) + tuple(scripts))
    miolo = f"""<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <a class="marca" href="{r}index.html">Floriano Romano</a>
  <nav class="nav" aria-label="Principal">{nav}</nav>
  <button class="som" type="button" aria-pressed="false" data-som><span class="som-ponto" aria-hidden="true"></span><span data-som-rotulo>Ligar som</span></button>
</header>
<main id="conteudo">
{body}
</main>
<footer class="rodape">
  <span>© {ANO_ATUAL} Floriano Romano</span>
  <span class="rodape-links"><a href="https://www.instagram.com/florianoromano/" rel="noopener">Instagram</a> <a href="https://www.youtube.com/@openradio" rel="noopener">YouTube</a> <a href="{r}indice.html">Todas as obras</a></span>
</footer>
{js}"""
    fontes = '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&family=Instrument+Sans:wght@400;500&family=Instrument+Serif:ital@0;1&family=Jura:wght@500&display=swap" rel="stylesheet">'
    if fragmento:
        return f"""<title>{e(full_title)}</title>
{fontes}
<link rel="stylesheet" href="{r}assets/css/site.css">
<div class="{body_class}">
{miolo}
</div>
"""
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&family=Instrument+Sans:wght@400;500&family=Instrument+Serif:ital@0;1&family=Jura:wght@500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/site.css">
</head>
<body class="{body_class}">
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <a class="marca" href="{r}index.html">Floriano Romano</a>
  <nav class="nav" aria-label="Principal">{nav}</nav>
  <button class="som" type="button" aria-pressed="false" data-som><span class="som-ponto" aria-hidden="true"></span><span data-som-rotulo>Ligar som</span></button>
</header>
<main id="conteudo">
{body}
</main>
<footer class="rodape">
  <span>© {ANO_ATUAL} Floriano Romano</span>
  <span class="rodape-links"><a href="https://www.instagram.com/florianoromano/" rel="noopener">Instagram</a> <a href="https://www.youtube.com/@openradio" rel="noopener">YouTube</a> <a href="{r}indice.html">Todas as obras</a></span>
</footer>
{js}
</body>
</html>
"""


# ----------------------------------------------------------------- mapa
def clip(p, q, W, H):
    (x1, y1), (x2, y2) = p, q
    dx, dy = x2 - x1, y2 - y1
    ts = []
    if dx:
        ts += [(0 - x1) / dx, (W - x1) / dx]
    if dy:
        ts += [(0 - y1) / dy, (H - y1) / dy]
    good = []
    for t in ts:
        x, y = x1 + t * dx, y1 + t * dy
        if -0.01 <= x <= W + 0.01 and -0.01 <= y <= H + 0.01:
            good.append(t)
    good.sort()
    a, b = good[0], good[-1]
    return (x1 + a * dx, y1 + a * dy), (x1 + b * dx, y1 + b * dy)


ESPESSURAS = [0.6, 1, 1.4, 1.4, 2.2, 3.4]


def svg_mapa(vertical=False):
    W, H = (560, 1000) if vertical else (1000, 560)
    def pos(o):
        x, y = o["mapa"]["x"], o["mapa"]["y"]
        return (y, 1000 - x) if vertical else (x, y)
    linhas = []
    for a, b in DATA["mapa_pares"]:
        (sx, sy), (ex, ey) = clip(pos(BY_ID[a]), pos(BY_ID[b]), W, H)
        h = int(hashlib.md5(f"{a}{b}".encode()).hexdigest(), 16)
        w = ESPESSURAS[h % len(ESPESSURAS)]
        linhas.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
                      f'stroke-width="{w}" data-n="{a} {b}"/>')
    nos = []
    for o in OBRAS:
        if "mapa" not in o:
            continue
        x, y = pos(o)
        m = o["mapa"]
        t = m["tier"]
        lx, ly = m["lx"], m["ly"]
        esq = m.get("lado") == "esquerda"
        if vertical:
            esq = x > 360
            lx = -abs(lx) if esq else abs(lx)
        anchor = "end" if esq else "start"
        r = {3: 9, 2: 7, 1: 5}[t]
        circ = (f'<circle class="m-pt" cx="{x}" cy="{y}" r="{r}"/>' if t >= 2 else
                f'<circle class="m-pt m-vazado" cx="{x}" cy="{y}" r="{r}"/>')
        nome_y = y + ly + (16 if t == 3 else 12)
        nos.append(
            f'<a class="m-no t{t}" href="obras/{o["id"]}.html" data-id="{o["id"]}" data-ano="{o["ano_num"]}" '
            f'aria-label="{e(o["titulo"])}, {e(o["ano"])}">'
            f'<circle class="m-alvo" cx="{x}" cy="{y}" r="22"/>{circ}'
            f'<text class="m-nome" x="{x + lx}" y="{nome_y}" text-anchor="{anchor}">{e(o["titulo"])}</text>'
            f'<text class="m-ano" x="{x + lx}" y="{nome_y + (17 if t == 3 else 14)}" text-anchor="{anchor}">{e(o.get("ano_mapa") or o["ano"].split(" /")[-1].strip())}</text>'
            f'</a>')
    cls = "mapa-v" if vertical else "mapa-h"
    return (f'<svg class="mapa {cls}" viewBox="0 0 {W} {H}" role="group" aria-label="Mapa das obras: cada cruzamento é uma obra">'
            f'<g class="m-linhas" aria-hidden="true">{"".join(linhas)}</g>'
            f'<g class="m-nos">{"".join(nos)}</g></svg>')


def build_index():
    body = f"""
<section class="inicio">
  <h1 class="oculto">Floriano Romano — obras</h1>
  <div class="mapa-moldura">
    {svg_mapa(False)}
    {svg_mapa(True)}
  </div>
  <div class="inicio-pe">
    <p class="dica"><span class="dica-hover">Passe sobre um cruzamento para ouvir. Clique para abrir a obra.</span><span class="dica-toque">Toque num cruzamento para abrir a obra.</span></p>
    <p class="apresenta">Artista visual e sonoro. Trabalha com som em instalações, objetos e ações urbanas desde 2002. Rio de Janeiro.</p>
  </div>
</section>"""
    return page("", body, scripts=("mapa.js",), body_class="pg-inicio", fragmento=PREVIA)


# ----------------------------------------------------------------- obra
def video_embed(v):
    if PREVIA:
        url = (f'https://vimeo.com/{v["id"]}' if v["plataforma"] == "vimeo"
               else f'https://www.youtube.com/watch?v={v["id"]}')
        return (f'<p class="video-link"><a href="{url}" target="_blank" rel="noopener">'
                f'<span class="nome">{e(v["titulo"])}</span> <span class="dado">assistir no {v["plataforma"].capitalize()} ↗</span></a></p>')
    if v["plataforma"] == "vimeo":
        src = f'https://player.vimeo.com/video/{v["id"]}?dnt=1&title=0&byline=0&portrait=0&color=c8321e'
    else:
        src = f'https://www.youtube-nocookie.com/embed/{v["id"]}?rel=0'
    return (f'<figure class="video"><div class="video-quadro"><iframe src="{src}" title="{e(v["titulo"])}" '
            f'loading="lazy" allow="fullscreen; picture-in-picture" allowfullscreen></iframe></div>'
            f'<figcaption>{e(v["titulo"])}</figcaption></figure>')


def build_obra(o, prev, nxt):
    r = "../"
    tem_som = bool(o.get("audio") or o.get("soundcloud"))
    som_local = bool(o.get("audio"))
    if o.get("soundcloud") and not som_local:
        if PREVIA:
            player = (f'<p class="sc-link"><a class="play" href="{e(o["soundcloud"])}" target="_blank" rel="noopener" '
                      f'aria-label="Escutar {e(o["titulo"])} no SoundCloud"><span class="play-icone" aria-hidden="true"></span></a>'
                      f'<span class="dado">Na prévia, o áudio abre no SoundCloud</span></p>')
        else:
            sc_src = ("https://w.soundcloud.com/player/?url=" + o["soundcloud"] +
                      "&color=%23c8321e&auto_play=false&hide_related=true&show_comments=false"
                      "&show_user=false&show_reposts=false&show_teaser=false&visual=false")
            player = f'<iframe class="sc-visivel" title="Áudio de {e(o["titulo"])}" src="{sc_src}" allow="autoplay" loading="lazy"></iframe>'
        escuta = f"""
<section class="escuta" aria-label="Escuta">
  {player}
  <div class="escuta-rodape escuta-rodape-sc"><span class="dado">Use fones de ouvido</span></div>
</section>"""
    elif som_local:
        escuta = f"""
<section class="escuta" data-escuta aria-label="Escuta">
  <div class="escuta-linha">
    <button class="play" type="button" data-play aria-label="Escutar {e(o['titulo'])}"><span class="play-icone" aria-hidden="true"></span></button>
    <canvas class="onda" data-onda aria-hidden="true"></canvas>
  </div>
  <div class="escuta-rodape">
    <span class="dado">Use fones de ouvido</span>
    <span class="dado" data-tempo></span>
  </div>
  <audio preload="metadata" src="{r}{o["audio"]}"></audio>
</section>"""
    elif o["tipo"] in ("desenho", "exposição"):
        escuta = ""
    else:
        escuta = '<p class="escuta-vazia dado">Registro sonoro em preparação.</p>'

    imgs = [i for i in (o.get("imagens") or []) if PENDENTES or not i.get("aprovar")]
    if imgs:
        figs = "".join(
            f'<figure><img src="{r}{e(i["src"])}" alt="{e(i.get("alt", o["titulo"]))}" loading="lazy">'
            f'<figcaption class="dado">{e(i.get("credito", ""))}</figcaption></figure>' for i in imgs)
        imagens = f'<section class="imagens{" velado" if som_local else ""}" data-imagens>{figs}</section>'
        if som_local:
            imagens += '<button class="mostrar" type="button" data-mostrar>Mostrar imagens agora</button>'
    else:
        imagens = '<div class="imagens-vazio" aria-hidden="true"><span class="dado">Imagens em preparação</span></div>'

    ficha = []
    for rotulo, chave in [("Materiais", "materiais"), ("Dimensões", "dimensoes"),
                          ("Local", "local"), ("Coleção", "colecao")]:
        if o.get(chave):
            ficha.append(f"<dt>{rotulo}</dt><dd>{e(o[chave])}</dd>")
    exps = ([o["exposicao"]] if o.get("exposicao") else []) + o.get("exposicoes_extra", [])
    COL = {c.get("id"): c for c in DATA["coletivas"] if c.get("id")}
    for cid in o.get("exposicoes_coletivas", []):
        if cid in COL:
            ficha.append(f'<dt>Exposição coletiva</dt><dd><a href="{r}exposicoes.html#{cid}">{e(COL[cid]["titulo"])}</a> ({e(COL[cid]["ano"])})</dd>')
    if exps:
        links = ", ".join(
            f'<a href="{r}exposicoes.html#{x}">{e(EXPOS[x]["titulo"])}</a> ({EXPOS[x]["ano"]})' for x in exps)
        ficha.append(f"<dt>Exposição</dt><dd>{links}</dd>")
    texto = "".join(f"<p>{e(p)}</p>" for p in o.get("texto", []))
    if o.get("citacao"):
        versos = "<br>".join(e(v.strip()) for v in o["citacao"].split("/"))
        texto += f'<blockquote class="citacao">{versos}</blockquote>'
    if o.get("autoria_texto") and o.get("texto"):
        texto += f'<p class="dado autoria">{e(o["autoria_texto"])}</p>'
    if o.get("pendente"):
        texto += f'<p class="pendente dado">Página em preparação.</p>'
    videos = "".join(video_embed(v) for v in o.get("video", []))
    videos = f'<section class="videos"><h2 class="sub">Vídeo</h2>{videos}</section>' if videos else ""
    if o.get("links"):
        videos += '<p class="links-obra">' + " ".join(
            f'<a href="{e(l["url"])}" rel="noopener">{e(l["titulo"])} ↗</a>' for l in o["links"]) + '</p>'

    nav_obras = '<nav class="vizinhas" aria-label="Outras obras">'
    if prev:
        nav_obras += f'<a href="{prev["id"]}.html" rel="prev"><span class="dado">Anterior</span><span class="nome">{e(prev["titulo"])}</span></a>'
    else:
        nav_obras += "<span></span>"
    if nxt:
        nav_obras += f'<a href="{nxt["id"]}.html" rel="next" class="dir"><span class="dado">Seguinte</span><span class="nome">{e(nxt["titulo"])}</span></a>'
    nav_obras += "</nav>"

    body = f"""
<article class="obra">
  <a class="voltar dado" href="{r}index.html">← Mapa</a>
  <header class="obra-cabeca">
    <h1 class="obra-titulo">{e(o['titulo'])}</h1>
    <p class="dado obra-meta"><span class="sinal">{e(o['ano'])}</span> · {e(o['tipo'])}</p>
  </header>
  {escuta}
  {imagens}
  <div class="obra-corpo">
    <div class="obra-texto">{texto}</div>
    <dl class="ficha">{''.join(ficha)}</dl>
  </div>
  {videos}
  {nav_obras}
</article>"""
    desc = (o.get("texto") or [f"{o['titulo']}, {o['ano']}. Obra de Floriano Romano."])[0][:155]
    scripts = ("obra.js",) if som_local else ()

    return page(o["titulo"], body, r=r, desc=desc, scripts=scripts, body_class="pg-obra")


# ----------------------------------------------------------------- índice
def build_indice():
    ordem = sorted(OBRAS, key=lambda o: (-o["ano_num"], o["titulo"]))
    tipos = sorted({o["tipo"] for o in OBRAS})
    filtros = '<button type="button" class="filtro" aria-pressed="true" data-filtro="">Todas</button>' + "".join(
        f'<button type="button" class="filtro" aria-pressed="false" data-filtro="{e(t)}">{e(t.capitalize())}</button>'
        for t in tipos)
    linhas = []
    for o in ordem:
        midia = []
        if o.get("audio") or o.get("soundcloud"):
            midia.append("som")
        if o.get("video"):
            midia.append("vídeo")
        if o.get("imagens"):
            midia.append("imagem")
        linhas.append(
            f'<tr data-tipo="{e(o["tipo"])}"><td class="dado">{e(o["ano"])}</td>'
            f'<td><a class="nome" href="obras/{o["id"]}.html">{e(o["titulo"])}</a></td>'
            f'<td>{e(o["tipo"])}</td><td class="dado">{" · ".join(midia)}</td></tr>')
    body = f"""
<section class="indice">
  <h1 class="titulo-pagina">Índice</h1>
  <div class="filtros" role="group" aria-label="Filtrar por tipo">{filtros}</div>
  <table class="tabela">
    <thead><tr><th scope="col">Ano</th><th scope="col">Obra</th><th scope="col">Tipo</th><th scope="col">Mídia</th></tr></thead>
    <tbody>{''.join(linhas)}</tbody>
  </table>
  <p class="dado contagem" data-contagem aria-live="polite"></p>
</section>"""
    return page("Índice", body, scripts=("indice.js",), active="indice.html",
                desc="Todas as obras de Floriano Romano, da mais recente à mais antiga.")


# ----------------------------------------------------------------- rádio
def build_radio():
    estacoes = []
    for o in OBRAS:
        if "radio" not in o:
            continue
        estacoes.append({
            "id": o["id"], "titulo": o["titulo"], "ano": o["ano"], "freq": o["radio"]["freq"],
            "texto": (o.get("texto") or [""])[0],
            "soundcloud": o.get("soundcloud", ""),
        })
    estacoes.sort(key=lambda s: s["freq"])
    lista = "".join(
        f'<li><a href="obras/{s["id"]}.html"><span class="dado">{e(s["ano"])}</span> <span class="nome">{e(s["titulo"])}</span></a></li>'
        for s in reversed(estacoes))
    body = f"""
<section class="radio">
  <h1 class="oculto">Rádio</h1>
  <div class="dial" data-dial tabindex="0" role="slider" aria-label="Dial: arraste ou use as setas para sintonizar"
       aria-valuemin="2000" aria-valuemax="2027" aria-valuenow="2016" aria-valuetext="2016">
    <div class="dial-ruido" aria-hidden="true"><canvas data-ruido></canvas></div>
    <div class="dial-faixa" data-faixa aria-hidden="true"></div>
    <div class="dial-agulha" aria-hidden="true"></div>
  </div>
  <div class="dial-leitura">
    <span class="dado" data-freq>2016</span>
    <span class="dado">arraste para sintonizar</span>
  </div>
  <div class="estacao" data-estacao aria-live="polite"></div>
  <div class="radio-lista">
    <h2 class="sub">Estações</h2>
    <ul>{lista}</ul>
  </div>
</section>
<script>window.ESTACOES = {json.dumps(estacoes, ensure_ascii=False)};{' window.PREVIA = true;' if PREVIA else ''}</script>"""
    return page("Rádio", body, scripts=("dial.js",), body_class="pg-radio noite", active="radio.html",
                desc="Rádio-arte de Floriano Romano: micro-rádio, programas e radionovelas.")


# ----------------------------------------------------------------- exposições
def build_exposicoes():
    blocos = []
    for x in DATA["exposicoes"]:
        obras = [o for o in OBRAS if o.get("exposicao") == x["id"] or x["id"] in o.get("exposicoes_extra", [])]
        obras_html = ", ".join(f'<a href="obras/{o["id"]}.html">{e(o["titulo"])}</a>' for o in obras)
        cur = f'<p class="dado">Curadoria: {e(x["curadoria"])}</p>' if x.get("curadoria") else ""
        cat = f'<p class="dado">{e(x["catalogo"])}</p>' if x.get("catalogo") else ""
        blocos.append(f"""
<section class="expo" id="{x['id']}">
  <p class="dado sinal">{x['ano']}</p>
  <h2 class="expo-titulo">{e(x['titulo'])}</h2>
  <p class="dado">{e(x['local'])}</p>
  {cur}
  <p class="expo-texto">{e(x['texto'])}</p>
  {f'<p class="expo-obras"><span class="dado">Obras:</span> {obras_html}</p>' if obras_html else ''}
  {cat}
</section>""")
    partes, simples = [], []
    def fecha():
        if simples:
            partes.append('<ul class="lista-simples">' + "".join(simples) + "</ul>")
            simples.clear()
    for c in DATA["coletivas"]:
        if c.get("video") or c.get("texto"):
            fecha()
            vid = video_embed(c["video"]) if c.get("video") else ""
            partes.append(f"""
<section class="expo expo-coletiva" id="{e(c.get('id',''))}">
  <p class="dado sinal">{e(c['ano'])}</p>
  <h3 class="expo-titulo">{e(c['titulo'])}</h3>
  <p class="dado">{e(c['local'])}</p>
  {f'<p class="expo-texto">{e(c["texto"])}</p>' if c.get('texto') else ''}
  {vid}
</section>""")
        else:
            simples.append(f'<li><span class="dado">{c["ano"]}</span> {e(c["titulo"])}, {e(c["local"])}</li>')
    fecha()
    col = "".join(partes)
    body = f"""
<section class="exposicoes">
  <h1 class="titulo-pagina">Exposições</h1>
  <h2 class="sub">Individuais</h2>
  {''.join(blocos)}
  <h2 class="sub">Coletivas (seleção)</h2>
  {col}
</section>"""
    return page("Exposições", body, active="exposicoes.html",
                desc="Exposições individuais e coletivas de Floriano Romano.")


# ----------------------------------------------------------------- textos
def item_texto(t, com_autor=True):
    titulo = e(t["titulo"])
    if t.get("url"):
        titulo = f'<a href="{e(t["url"])}" rel="noopener">{titulo}</a>'
    autor = f'<span class="autor">{e(t["autor"])}</span>' if com_autor else ""
    ano = f'<span class="dado">{e(t["ano"])}</span>' if t.get("ano") else '<span class="dado">—</span>'
    return f'<li>{ano}<div>{autor}<span class="nome">{titulo}</span><span class="dado fonte">{e(t["fonte"])}</span></div></li>'


def build_textos():
    sobre = "".join(item_texto(t) for t in DATA["textos_sobre"])
    dele = "".join(item_texto(t, False) for t in DATA["textos_do_artista"])
    ents = DATA.get("entrevistas", [])
    entrevistas = ('<h2 class="sub">Entrevistas</h2>' + "".join(
        f'<div class="entrevista"><p><span class="dado">{e(x["ano"])}</span> <span class="nome">{e(x["titulo"])}</span> '
        f'<span class="dado fonte">{e(x["fonte"])}</span></p>{video_embed(x["video"])}</div>' for x in ents)) if ents else ""
    body = f"""
<section class="textos">
  <h1 class="titulo-pagina">Textos</h1>
  <h2 class="sub">Sobre a obra</h2>
  <ul class="lista-textos">{sobre}</ul>
  <h2 class="sub">Do artista</h2>
  <ul class="lista-textos">{dele}</ul>
  <p class="dado"><a href="https://ufrj.academia.edu/FlorianoRomano" rel="noopener">Mais textos e catálogos no Academia.edu ↗</a></p>
  {entrevistas}
</section>"""
    return page("Textos", body, active="textos.html",
                desc="Textos críticos sobre a obra de Floriano Romano e textos do artista.")


# ----------------------------------------------------------------- sobre
def build_sobre():
    body = """
<section class="sobre">
  <h1 class="titulo-pagina">Sobre</h1>
  <div class="sobre-grade">
    <div class="sobre-texto">
      <p class="abertura">Floriano Romano (Rio de Janeiro, 1969) é artista contemporâneo e trabalha com som em instalações, objetos e ações urbanas desde 2002.</p>
      <p>Sua prática parte do imaginário e do texto para pensar o som dentro das artes visuais. Pela rádio-arte, pela poesia sonora e pela performance, aborda a cidade e a memória, a partir de gestos simples — caminhar, transmitir, escutar — e da reorganização das experiências sensíveis que eles desencadeiam.</p>
      <p>Entre 2002 e 2004 criou e apresentou O Inusitado, na Rádio Madame Satã, ponto de encontro da cena de arte sonora carioca. Participou da 7ª Bienal do Mercosul (2009). Doutor em Artes Visuais, é professor da Escola de Belas Artes da Universidade Federal do Rio de Janeiro e do Programa de Pós-Graduação em Linguagens Visuais.</p>
    </div>
    <div class="sobre-dados">
      <h2 class="sub">Prêmios e bolsas</h2>
      <ul class="lista-simples">
        <li><span class="dado">2021</span> Cidade Labirinto, instalação sonora e podcast — Centro Municipal de Arte Hélio Oiticica</li>
        <li><span class="dado">2017</span> HOBRA, residência artística Brasil–Holanda</li>
        <li><span class="dado">2016</span> Muro de Som, exposição individual — Parque das Ruínas, Prefeitura do Rio de Janeiro</li>
        <li><span class="dado">2016</span> Prêmio CCBB Contemporâneo — Errância</li>
        <li><span class="dado">2012</span> Prêmio Marcantonio Vilaça, Funarte — Chuveiros Sonoros</li>
        <li><span class="dado">2012</span> Prêmio Projéteis de Arte Contemporânea, Funarte — A Cidade Sonora</li>
        <li><span class="dado">2011</span> Intrasom, ações sonoras no MAM Rio — Secretaria de Estado de Cultura</li>
        <li><span class="dado">2010</span> Prêmio Interações Estéticas, Funarte — Esculturas Sonoras Urbanas</li>
        <li><span class="dado">2010</span> Artista indicado ao Prêmio PIPA</li>
        <li><span class="dado">2008</span> Bolsa de Apoio às Artes Visuais, Funarte — Chapéu Panorâmico</li>
        <li><span class="dado">2007</span> Prêmio Projéteis de Arte Contemporânea, Funarte — Sample Way of Life</li>
        <li><span class="dado">2007</span> Menção honrosa, 58º Salão de Abril, Fortaleza — Falante</li>
        <li><span class="dado">2000</span> Residência nos Ateliers da Lada, Porto, Portugal — Do Deslocamento</li>
      </ul>
      <h2 class="sub">Coleções</h2>
      <ul class="lista-simples">
        <li>Museu de Arte do Rio — O Rio dos Navegantes</li>
        <li>Museu de Arte Contemporânea de Niterói — Chuveiros Sonoros, Chapéu Panorâmico</li>
        <li>Museo de Artes Visuales, Santiago do Chile — Falante (vídeo)</li>
        <li>Centro Provincial de Diseño y Oficios, Havana — mochila de Falante</li>
      </ul>
      <h2 class="sub">Vídeos</h2>
      <p><a href="https://www.youtube.com/@openradio" rel="noopener">Canal no YouTube — @openradio</a><br>
      <a href="https://vimeo.com/user12897613" rel="noopener">Vimeo</a></p>
      <h2 class="sub">Instagram</h2>
      <p><a href="https://www.instagram.com/florianoromano/" rel="noopener">@florianoromano</a></p>
      <h2 class="sub">Contato</h2>
      <p class="dado" data-contato>e-mail a definir</p>
    </div>
  </div>
</section>"""
    return page("Sobre", body, active="sobre.html",
                desc="Biografia, prêmios, residências e coleções de Floriano Romano.")


# ----------------------------------------------------------------- main
def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "obras").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if (ROOT / "media").exists():
        shutil.copytree(ROOT / "media", OUT / "media")
    if PENDENTES and (ROOT / "media-pendente").exists():
        shutil.copytree(ROOT / "media-pendente", OUT / "media-pendente")
    (OUT / ".nojekyll").write_text("")
    if not PREVIA and not PENDENTES:
        (OUT / "CNAME").write_text("florianoromano.art.br\n")  # domínio próprio no GitHub Pages
    (OUT / "index.html").write_text(build_index(), encoding="utf-8")
    (OUT / "indice.html").write_text(build_indice(), encoding="utf-8")
    (OUT / "radio.html").write_text(build_radio(), encoding="utf-8")
    (OUT / "exposicoes.html").write_text(build_exposicoes(), encoding="utf-8")
    (OUT / "textos.html").write_text(build_textos(), encoding="utf-8")
    (OUT / "sobre.html").write_text(build_sobre(), encoding="utf-8")
    ordem = sorted(OBRAS, key=lambda o: (-o["ano_num"], o["titulo"]))
    for i, o in enumerate(ordem):
        prev = ordem[i - 1] if i > 0 else None
        nxt = ordem[i + 1] if i + 1 < len(ordem) else None
        (OUT / "obras" / f"{o['id']}.html").write_text(build_obra(o, prev, nxt), encoding="utf-8")
    print(f"ok — {len(OBRAS)} obras, saída em {OUT}")


if __name__ == "__main__":
    main()
