#!/usr/bin/env python3
"""Gera o site estático e bilíngue (português / inglês) de Floriano Romano a partir de data/obras.json.

Uso:  python3 build.py            (escreve em ./public)
      python3 build.py --previa   (versão para navegar dentro do Claude, sem players externos)

Português na raiz; inglês em /en/. Mídia e estilos são compartilhados.
"""
import json, shutil, html, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
PREVIA = "--previa" in sys.argv
OUT = ROOT / ("previa" if PREVIA else "public")
DATA = json.loads((ROOT / "data" / "obras.json").read_text(encoding="utf-8"))
OBRAS = DATA["obras"]
BY_ID = {o["id"]: o for o in OBRAS}
_IMGS = ROOT / "data" / "imagens.json"
if _IMGS.exists():
    for _id, _lista in json.loads(_IMGS.read_text(encoding="utf-8")).items():
        if _id in BY_ID:
            atuais = BY_ID[_id].get("imagens", [])
            BY_ID[_id]["imagens"] = _lista + [i for i in atuais if i not in _lista]
EXPOS = {x["id"]: x for x in DATA["exposicoes"]}
COLS = {c["id"]: c for c in DATA["coletivas"] if c.get("id")}
ANO_ATUAL = "2026"
e = html.escape

# ----------------------------------------------------------------- textos da interface
T = {
 "pt": dict(
   html_lang="pt-BR", nav=[("indice.html", "Índice"), ("exposicoes.html", "Exposições"), ("radio.html", "Rádio"),
                           ("textos.html", "Textos"), ("sobre.html", "Sobre")],
   pular="Pular para o conteúdo", som="Ligar som", todas="Todas as obras", outra_lingua="EN", outra_lingua_nome="English",
   desc="Floriano Romano, artista visual e sonoro. Instalações, objetos, ações urbanas e rádio-arte. Rio de Janeiro.",
   dica_hover="Passe sobre um cruzamento para ouvir. Clique para abrir a obra.", dica_toque="Toque num cruzamento para abrir a obra.",
   apresenta="Artista visual e sonoro. Escutar a cidade é enxergar o outro.",
   mapa_aria="Mapa das obras: cada cruzamento é uma obra", voltar="← Mapa", fones="Use fones de ouvido",
   escutar="Escutar", sc_previa="Na prévia, o áudio abre no SoundCloud", assistir="assistir no",
   sem_som="Registro sonoro em preparação.", sem_img="Imagens em preparação", mostrar="Mostrar imagens agora",
   preparo="Página em preparação.", video="Vídeo", anterior="Anterior", seguinte="Seguinte", outras="Outras obras",
   premio="Prêmio", fomento="Financiamento", materiais="Materiais", dimensoes="Dimensões", local="Local", colecao="Coleção", expo="Exposição", expo_col="Exposição coletiva",
   indice="Índice", filtrar="Filtrar por tipo", todas_f="Todas", ano="Ano", obra="Obra", tipo="Tipo", midia="Mídia",
   m_som="som", m_video="vídeo", m_img="imagem",
   radio="Rádio", dial_aria="Dial: arraste ou use as setas para sintonizar", sintonizar="arraste para sintonizar", estacoes="Estações",
   exposicoes="Exposições", individuais="Individuais", coletivas="Coletivas (seleção)", curadoria="Curadoria",
   textos="Textos", em_destaque="Em destaque", col_destaque="Coletivas em destaque", sobre_obra="Sobre a obra", do_artista="Do artista", entrevistas="Entrevistas",
   academia="Mais textos e catálogos no Academia.edu ↗",
   sobre="Sobre", premios="Prêmios", financiamentos="Financiamentos e residências", indicacao="Indicação", colecoes="Coleções", videos="Vídeos", contato="Contato", contato_txt="e-mail a definir",
   d_indice="Todas as obras de Floriano Romano, da mais recente à mais antiga.",
   d_radio="Rádio-arte de Floriano Romano: micro-rádio, programas e radionovelas.",
   d_expos="Exposições individuais e coletivas de Floriano Romano.",
   d_textos="Textos sobre a obra de Floriano Romano e textos do artista.",
   d_sobre="Biografia, prêmios e coleções de Floriano Romano."),
 "en": dict(
   html_lang="en", nav=[("indice.html", "Index"), ("exposicoes.html", "Exhibitions"), ("radio.html", "Radio"),
                        ("textos.html", "Texts"), ("sobre.html", "About")],
   pular="Skip to content", som="Sound on", todas="All works", outra_lingua="PT", outra_lingua_nome="Português",
   desc="Floriano Romano, visual and sound artist. Installations, objects, urban actions and radio art. Rio de Janeiro.",
   dica_hover="Hover over a crossing to listen. Click to open the work.", dica_toque="Tap a crossing to open the work.",
   apresenta="Visual and sound artist. To listen to the city is to see the other.",
   mapa_aria="Map of works: each crossing is a work", voltar="← Map", fones="Use headphones",
   escutar="Listen to", sc_previa="In the preview, audio opens on SoundCloud", assistir="watch on",
   sem_som="Sound recording in preparation.", sem_img="Images in preparation", mostrar="Show images now",
   preparo="Page in preparation.", video="Video", anterior="Previous", seguinte="Next", outras="Other works",
   premio="Award", fomento="Funding", materiais="Materials", dimensoes="Dimensions", local="Venue", colecao="Collection", expo="Exhibition", expo_col="Group exhibition",
   indice="Index", filtrar="Filter by type", todas_f="All", ano="Year", obra="Work", tipo="Type", midia="Media",
   m_som="sound", m_video="video", m_img="image",
   radio="Radio", dial_aria="Dial: drag or use the arrow keys to tune", sintonizar="drag to tune", estacoes="Stations",
   exposicoes="Exhibitions", individuais="Solo", coletivas="Group (selection)", curadoria="Curated by",
   textos="Texts", em_destaque="Highlights", col_destaque="Selected group exhibitions", sobre_obra="On the work", do_artista="By the artist", entrevistas="Interviews",
   academia="More texts and catalogues on Academia.edu ↗",
   sobre="About", premios="Awards", financiamentos="Funding and residencies", indicacao="Nomination", colecoes="Collections", videos="Videos", contato="Contact", contato_txt="email to be confirmed",
   d_indice="All works by Floriano Romano, from the most recent to the earliest.",
   d_radio="Radio art by Floriano Romano: micro-radio, programmes and radio plays.",
   d_expos="Solo and group exhibitions by Floriano Romano.",
   d_textos="Texts on Floriano Romano's work and texts by the artist.",
   d_sobre="Biography, awards and collections of Floriano Romano."),
}

TIPOS_EN = {"instalação": "installation", "desenho": "drawing", "performance": "performance", "objeto sonoro": "sound object",
            "intervenção urbana": "urban intervention", "exposição": "exhibition", "rádio": "radio", "vídeo": "video"}
ANO_EN = {"início dos anos 2000": "early 2000s", "anos 2000": "2000s"}
LEGENDA_EN = [("Foto:", "Photo:"), ("Arquivo do artista", "Artist's archive"), ("frame do vídeo", "video still"),
              ("vista da instalação", "installation view"), ("vista da exposição", "exhibition view"),
              ("detalhe", "detail"), ("com o artista", "with the artist"), ("na exposição", "in the exhibition"),
              ("diante da praia de Ipanema", "facing Ipanema beach"), ("as duas paredes de alto-falantes", "the two loudspeaker walls"),
              ("a escada diante da obra", "the staircase before the work"), ("na escada de acesso", "on the access stairs"),
              ("voltados para a Baía de Guanabara", "facing Guanabara Bay"), ("no mirante do", "at the lookout of the"),
              ("sapatos pandeiro", "tambourine shoes"), ("sapatos com conchas", "shoes with shells"),
              ("Desenhos com fita isolante", "Electrical-tape drawings")]


def tr(o, k, lang):
    """Valor traduzido de um campo, com recuo para o português."""
    if lang == "en" and o.get(k + "_en"):
        return o[k + "_en"]
    return o.get(k, "")


def tipo(o, lang):
    return TIPOS_EN.get(o["tipo"], o["tipo"]) if lang == "en" else o["tipo"]


def ano(o, lang):
    return ANO_EN.get(o["ano"], o["ano"]) if lang == "en" else o["ano"]


def legenda(txt, lang):
    if lang == "en":
        for a, b in LEGENDA_EN:
            txt = txt.replace(a, b)
    return txt


# ----------------------------------------------------------------- página
class Ctx:
    """Caminhos relativos de uma página: base (raiz do site) e lbase (raiz da língua)."""
    def __init__(self, lang, rel):
        self.lang, self.rel = lang, rel            # rel: caminho da página a partir da raiz da língua
        depth = rel.count("/")
        self.lbase = "../" * depth
        self.base = self.lbase + ("../" if lang == "en" else "")
        self.t = T[lang]

    def outra(self):
        return self.base + ("" if self.lang == "en" else "en/") + self.rel


def page(c, title, body, desc="", body_class="", scripts=(), active=""):
    t = c.t
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{c.lbase}{h}"{cur if h == active else ""}>{lab}</a>' for h, lab in t["nav"])
    full_title = f"{title} — Floriano Romano" if title else "Floriano Romano"
    desc = desc or t["desc"]
    js = (f'<script>window.LANG="{c.lang}";</script>' +
          "".join(f'<script src="{c.base}assets/js/{s}" defer></script>' for s in ("site.js",) + tuple(scripts)))
    miolo = f"""<a class="pular" href="#conteudo">{t['pular']}</a>
<header class="topo">
  <a class="marca" href="{c.lbase}index.html">Floriano Romano</a>
  <nav class="nav" aria-label="Menu">{nav}</nav>
  <div class="topo-acoes">
    <a class="lingua" href="{c.outra()}" hreflang="{'pt-BR' if c.lang == 'en' else 'en'}" title="{t['outra_lingua_nome']}">{t['outra_lingua']}</a>
    <button class="som" type="button" aria-pressed="false" data-som><span class="som-ponto" aria-hidden="true"></span><span data-som-rotulo>{t['som']}</span></button>
  </div>
</header>
<main id="conteudo">
{body}
</main>
<footer class="rodape">
  <span>© {ANO_ATUAL} Floriano Romano</span>
  <span class="rodape-links"><a href="https://www.instagram.com/florianoromano/" rel="noopener">Instagram</a> <a href="https://www.youtube.com/@openradio" rel="noopener">YouTube</a></span>
</footer>
{js}"""
    fontes = ('<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&family=Instrument+Sans:wght@400;500'
              '&family=Instrument+Serif:ital@0;1&family=Jura:wght@500&display=swap" rel="stylesheet">')
    if PREVIA and c.rel == "index.html" and c.lang == "pt":
        return f'<title>{e(full_title)}</title>\n{fontes}\n<link rel="stylesheet" href="{c.base}assets/css/site.css">\n<div class="{body_class}">\n{miolo}\n</div>\n'
    alt_pt = c.base + c.rel if c.lang == "en" else c.lbase + c.rel
    return f"""<!doctype html>
<html lang="{t['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="alternate" hreflang="{'pt-BR' if c.lang == 'en' else 'en'}" href="{c.outra()}">
<link rel="icon" href="{c.base}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fontes}
<link rel="stylesheet" href="{c.base}assets/css/site.css">
</head>
<body class="{body_class}">
{miolo}
</body>
</html>
"""


# ----------------------------------------------------------------- mapa
import mapa as MAPA
MAPA.EXPOS = EXPOS


def svg_mapa(c, vertical=False):
    return MAPA.svg(c, BY_ID, e, ano, ANO_EN, vertical)


def build_index(c):
    t = c.t
    body = f"""
<section class="inicio">
  <h1 class="oculto">Floriano Romano</h1>
  <div class="mapa-moldura">
    {svg_mapa(c, False)}
    {svg_mapa(c, True)}
  </div>
  <div class="inicio-pe">
    <p class="dica"><span class="dica-hover">{t['dica_hover']}</span><span class="dica-toque">{t['dica_toque']}</span></p>
  </div>
</section>"""
    return page(c, "", body, scripts=("mapa.js",), body_class="pg-inicio")


# ----------------------------------------------------------------- obra
def video_embed(v, c):
    if PREVIA:
        url = f'https://vimeo.com/{v["id"]}' if v["plataforma"] == "vimeo" else f'https://www.youtube.com/watch?v={v["id"]}'
        return (f'<p class="video-link"><a href="{url}" target="_blank" rel="noopener"><span class="nome">{e(v["titulo"])}</span> '
                f'<span class="dado">{c.t["assistir"]} {v["plataforma"].capitalize()} ↗</span></a></p>')
    if v["plataforma"] == "vimeo":
        src = f'https://player.vimeo.com/video/{v["id"]}?dnt=1&title=0&byline=0&portrait=0&color=c8321e'
    else:
        src = f'https://www.youtube-nocookie.com/embed/{v["id"]}?rel=0'
    return (f'<figure class="video"><div class="video-quadro"><iframe src="{src}" title="{e(v["titulo"])}" loading="lazy" '
            f'allow="fullscreen; picture-in-picture" allowfullscreen></iframe></div><figcaption>{e(v["titulo"])}</figcaption></figure>')


def miniatura(o):
    imgs = [i for i in (o.get("imagens") or []) if not i.get("aprovar")]
    return imgs[0]["src"] if imgs else ""


def build_obra(o, prev, nxt, c):
    t, b, lang = c.t, c.base, c.lang
    som_local = bool(o.get("audio"))
    if o.get("soundcloud") and not som_local:
        if PREVIA:
            player = (f'<p class="sc-link"><a class="play" href="{e(o["soundcloud"])}" target="_blank" rel="noopener" '
                      f'aria-label="{t["escutar"]} {e(o["titulo"])}"><span class="play-icone" aria-hidden="true"></span></a>'
                      f'<span class="dado">{t["sc_previa"]}</span></p>')
        else:
            sc = ("https://w.soundcloud.com/player/?url=" + o["soundcloud"] + "&color=%23c8321e&auto_play=false&hide_related=true"
                  "&show_comments=false&show_user=false&show_reposts=false&show_teaser=false&visual=false")
            player = f'<iframe class="sc-visivel" title="{t["escutar"]} {e(o["titulo"])}" src="{sc}" allow="autoplay" loading="lazy"></iframe>'
        escuta = f'<section class="escuta">{player}<div class="escuta-rodape escuta-rodape-sc"><span class="dado">{t["fones"]}</span></div></section>'
    elif som_local:
        escuta = f"""
<section class="escuta" data-escuta>
  <div class="escuta-linha">
    <button class="play" type="button" data-play aria-label="{t['escutar']} {e(o['titulo'])}"><span class="play-icone" aria-hidden="true"></span></button>
    <canvas class="onda" data-onda aria-hidden="true"></canvas>
  </div>
  <div class="escuta-rodape"><span class="dado">{t['fones']}</span><span class="dado" data-tempo></span></div>
  <audio preload="metadata" src="{b}{o['audio']}"></audio>
</section>"""
    elif o["tipo"] in ("desenho", "exposição", "vídeo"):
        escuta = ""
    else:
        escuta = f'<p class="escuta-vazia dado">{t["sem_som"]}</p>'

    imgs = [i for i in (o.get("imagens") or []) if not i.get("aprovar")]
    if imgs:
        figs = "".join(f'<figure><img src="{b}{e(i["src"])}" alt="{e(legenda(i.get("alt", o["titulo"]), lang))}" loading="lazy">'
                       f'<figcaption class="dado">{e(legenda(i.get("credito", ""), lang))}</figcaption></figure>' for i in imgs)
        imagens = f'<section class="imagens" data-imagens>{figs}</section>'
    elif o.get("video"):
        imagens = ""
    else:
        imagens = f'<div class="imagens-vazio" aria-hidden="true"><span class="dado">{t["sem_img"]}</span></div>'

    ficha = []
    if o.get("premio"):
        ficha.append(f'<dt class="sinal">{t["premio"]}</dt><dd class="ficha-premio">{e(tr(o, "premio", lang))}</dd>')
    if o.get("fomento"):
        ficha.append(f'<dt>{t["fomento"]}</dt><dd>{e(tr(o, "fomento", lang))}</dd>')
    for rot, k in [("materiais", "materiais"), ("dimensoes", "dimensoes"), ("local", "local"), ("colecao", "colecao")]:
        v = tr(o, k, lang)
        if v:
            ficha.append(f"<dt>{t[rot]}</dt><dd>{e(v)}</dd>")
    exps = ([o["exposicao"]] if o.get("exposicao") else []) + o.get("exposicoes_extra", [])
    if exps:
        links = ", ".join(f'<a href="{c.lbase}exposicoes.html#{x}">{e(EXPOS[x]["titulo"])}</a> ({EXPOS[x]["ano"]})' for x in exps)
        ficha.append(f"<dt>{t['expo']}</dt><dd>{links}</dd>")
    for cid in o.get("exposicoes_coletivas", []):
        if cid in COLS:
            col = COLS[cid]
            ficha.append(f'<dt>{t["expo_col"]}</dt><dd><a href="{c.lbase}exposicoes.html#{cid}">{e(tr(col, "titulo", lang))}</a> ({e(col["ano"])})</dd>')

    paras = tr(o, "texto", lang) or []
    texto = "".join(f"<p>{e(p)}</p>" for p in paras)
    cit = tr(o, "citacao", lang)
    if cit:
        texto += '<blockquote class="citacao">' + "<br>".join(e(v.strip()) for v in cit.split("/")) + "</blockquote>"
    if o.get("pendente") and not paras:
        texto += f'<p class="pendente dado">{t["preparo"]}</p>'

    videos = "".join(video_embed(v, c) for v in o.get("video", []))
    videos = f'<section class="videos"><h2 class="sub">{t["video"]}</h2>{videos}</section>' if videos else ""
    if o.get("links"):
        videos += '<p class="links-obra">' + " ".join(f'<a href="{e(l["url"])}" rel="noopener">{e(l["titulo"])} ↗</a>' for l in o["links"]) + "</p>"

    viz = f'<nav class="vizinhas" aria-label="{t["outras"]}">'
    viz += (f'<a href="{prev["id"]}.html" rel="prev"><span class="dado">{t["anterior"]}</span><span class="nome">{e(prev["titulo"])}</span></a>'
            if prev else "<span></span>")
    if nxt:
        viz += f'<a href="{nxt["id"]}.html" rel="next" class="dir"><span class="dado">{t["seguinte"]}</span><span class="nome">{e(nxt["titulo"])}</span></a>'
    viz += "</nav>"

    body = f"""
<article class="obra">
  <a class="voltar dado" href="{c.lbase}index.html">{t['voltar']}</a>
  <header class="obra-cabeca">
    <h1 class="obra-titulo">{e(o['titulo'])}</h1>
    <p class="dado obra-meta"><span class="sinal">{e(ano(o, lang))}</span>{' · ' + e(tipo(o, lang)) if o['tipo'] else ''}</p>
    {f'<p class="obra-premio">{e(tr(o, "premio", lang))}</p>' if o.get("premio") else ''}
  </header>
  {escuta}
  <div class="obra-corpo">
    <div class="obra-texto">{texto}</div>
    <dl class="ficha">{''.join(ficha)}</dl>
  </div>
  {imagens}
  {videos}
</article>"""
    desc = (paras or [f"{o['titulo']}, {ano(o, lang)}. Floriano Romano."])[0][:155]
    return page(c, o["titulo"], body, desc=desc, scripts=("obra.js",) if som_local else (), body_class="pg-obra")


# ----------------------------------------------------------------- índice
def build_indice(c):
    t, lang = c.t, c.lang
    ordem = sorted(OBRAS, key=lambda o: (-o["ano_num"], o["titulo"]))
    tipos = sorted({o["tipo"] for o in OBRAS if o["tipo"]}, key=lambda x: TIPOS_EN.get(x, x) if lang == "en" else x)
    filtros = f'<button type="button" class="filtro" aria-pressed="true" data-filtro="">{t["todas_f"]}</button>' + "".join(
        f'<button type="button" class="filtro" aria-pressed="false" data-filtro="{e(x)}">{e((TIPOS_EN.get(x, x) if lang == "en" else x).capitalize())}</button>'
        for x in tipos)
    linhas = []
    for o in ordem:
        midia = ([t["m_som"]] if o.get("audio") or o.get("soundcloud") else []) + ([t["m_video"]] if o.get("video") else []) + \
                ([t["m_img"]] if o.get("imagens") else [])
        linhas.append(f'<tr data-tipo="{e(o["tipo"])}"><td class="dado">{e(ano(o, lang))}</td>'
                      f'<td><a class="nome" href="obras/{o["id"]}.html">{e(o["titulo"])}</a>'
                      + (f' <span class="dado sinal indice-premio">{e(tr(o, "premio_curto", lang))}</span>' if o.get("premio") else "") + '</td>'
                      f'<td>{e(tipo(o, lang))}</td><td class="dado">{" · ".join(midia)}</td></tr>')
    body = f"""
<section class="indice">
  <h1 class="titulo-pagina">{t['indice']}</h1>
  <div class="filtros" role="group" aria-label="{t['filtrar']}">{filtros}</div>
  <table class="tabela">
    <thead><tr><th scope="col">{t['ano']}</th><th scope="col">{t['obra']}</th><th scope="col">{t['tipo']}</th><th scope="col">{t['midia']}</th></tr></thead>
    <tbody>{''.join(linhas)}</tbody>
  </table>
  <p class="dado contagem" data-contagem aria-live="polite"></p>
</section>"""
    return page(c, t["indice"], body, scripts=("indice.js",), active="indice.html", desc=t["d_indice"])


# ----------------------------------------------------------------- rádio
def build_radio(c):
    t, lang = c.t, c.lang
    est = sorted(({"id": o["id"], "titulo": o["titulo"], "ano": ano(o, lang), "freq": o["radio"]["freq"],
                   "texto": (tr(o, "texto", lang) or [""])[0], "soundcloud": o.get("soundcloud", "")}
                  for o in OBRAS if "radio" in o), key=lambda s: s["freq"])
    lista = "".join(f'<li><a href="obras/{s["id"]}.html"><span class="dado">{e(s["ano"])}</span> <span class="nome">{e(s["titulo"])}</span></a></li>'
                    for s in reversed(est))
    body = f"""
<section class="radio">
  <h1 class="oculto">{t['radio']}</h1>
  <div class="dial" data-dial tabindex="0" role="slider" aria-label="{t['dial_aria']}" aria-valuemin="2000" aria-valuemax="2027" aria-valuenow="2016" aria-valuetext="2016">
    <div class="dial-ruido" aria-hidden="true"><canvas data-ruido></canvas></div>
    <div class="dial-faixa" data-faixa aria-hidden="true"></div>
    <div class="dial-agulha" aria-hidden="true"></div>
  </div>
  <div class="dial-leitura"><span class="dado" data-freq>2016</span><span class="dado">{t['sintonizar']}</span></div>
  <div class="estacao" data-estacao aria-live="polite"></div>
  <div class="radio-lista"><h2 class="sub">{t['estacoes']}</h2><ul>{lista}</ul></div>
</section>
<script>window.ESTACOES = {json.dumps(est, ensure_ascii=False)};{' window.PREVIA = true;' if PREVIA else ''}</script>"""
    return page(c, t["radio"], body, scripts=("dial.js",), body_class="pg-radio noite", active="radio.html", desc=t["d_radio"])


# ----------------------------------------------------------------- exposições
def cartoes(obras, c):
    """Obras de uma exposição como cartões: imagem, título, ano."""
    itens = []
    for o in obras:
        src = miniatura(o)
        img = (f'<img src="{c.base}{e(src)}" alt="" loading="lazy">' if src else '<span class="cartao-vazio" aria-hidden="true"></span>')
        itens.append(f'<li><a href="obras/{o["id"]}.html">{img}<span class="nome">{e(o["titulo"])}</span>'
                     f'<span class="dado">{e(ano(o, c.lang))}</span></a></li>')
    return f'<ul class="cartoes">{"".join(itens)}</ul>'


def faixa_imagens(o, c, n=4):
    imgs = [i for i in (o.get("imagens") or []) if not i.get("aprovar")][:n]
    if not imgs:
        return ""
    return '<div class="faixa">' + "".join(f'<img src="{c.base}{e(i["src"])}" alt="{e(legenda(i.get("alt", ""), c.lang))}" loading="lazy">' for i in imgs) + "</div>"


def build_exposicoes(c):
    t, lang = c.t, c.lang
    blocos = []
    for x in DATA["exposicoes"]:
        obras = [o for o in OBRAS if o.get("exposicao") == x["id"] or x["id"] in o.get("exposicoes_extra", [])]
        mesma = len(obras) == 1 and obras[0]["titulo"] == x["titulo"]
        titulo = (f'<a href="obras/{obras[0]["id"]}.html">{e(x["titulo"])}</a>' if mesma else e(x["titulo"]))
        meta = tr(x, "local", lang)
        if x.get("curadoria"):
            meta += f' · {t["curadoria"]}: {x["curadoria"]}'
        cat = tr(x, "catalogo", lang)
        visual = faixa_imagens(obras[0], c) if mesma else (cartoes(obras, c) if obras else "")
        blocos.append(f"""
<section class="expo" id="{x['id']}">
  <p class="dado sinal">{x['ano']}</p>
  <h2 class="expo-titulo">{titulo}</h2>
  <p class="dado expo-meta">{e(meta)}</p>
  <p class="expo-texto">{e(tr(x, 'texto', lang))}</p>
  {visual}
  {f'<p class="dado">{e(cat)}</p>' if cat else ''}
</section>""")
    partes, simples = [], []
    def fecha():
        if simples:
            partes.append('<ul class="lista-simples">' + "".join(simples) + "</ul>")
            simples.clear()
    destaque_col = []
    for col in [x for x in DATA["coletivas"] if x.get("destaque")]:
        obras_col = [o for o in OBRAS if col["id"] in o.get("exposicoes_coletivas", [])]
        titulo_col = e(tr(col, "titulo", lang))
        if col.get("url"):
            titulo_col = f'<a href="{e(col["url"])}" rel="noopener">{titulo_col} ↗</a>'
        destaque_col.append(f"""
<section class="expo expo-destaque" id="{e(col['id'])}">
  <p class="dado sinal">{e(col['ano'])}</p>
  <h3 class="expo-titulo">{titulo_col}</h3>
  <p class="dado expo-meta">{e(tr(col, 'local', lang))}</p>
  {f'<p class="expo-texto">{e(tr(col, "texto", lang))}</p>' if col.get("texto") else ''}
  {cartoes(obras_col, c) if obras_col else ''}
</section>""")
    for col in [x for x in DATA["coletivas"] if not x.get("destaque")]:
        if col.get("video") or col.get("texto"):
            fecha()
            vid = video_embed(col["video"], c) if col.get("video") else ""
            txt = tr(col, "texto", lang)
            partes.append(f"""
<section class="expo expo-coletiva" id="{e(col.get('id', ''))}">
  <p class="dado sinal">{e(col['ano'])}</p>
  <h3 class="expo-titulo">{e(tr(col, 'titulo', lang))}</h3>
  <p class="dado expo-meta">{e(tr(col, 'local', lang))}</p>
  {f'<p class="expo-texto">{e(txt)}</p>' if txt else ''}
  {vid}
</section>""")
        else:
            simples.append(f'<li{" id=" + chr(34) + col["id"] + chr(34) if col.get("id") else ""}><span class="dado">{col["ano"]}</span> '
                           f'{e(tr(col, "titulo", lang))}, {e(tr(col, "local", lang))}</li>')
    fecha()
    body = f"""
<section class="exposicoes">
  <h1 class="titulo-pagina">{t['exposicoes']}</h1>
  <h2 class="sub">{t['individuais']}</h2>
  {''.join(blocos)}
  <h2 class="sub">{t['col_destaque']}</h2>
  {''.join(destaque_col)}
  <h2 class="sub">{t['coletivas']}</h2>
  {''.join(partes)}
</section>"""
    return page(c, t["exposicoes"], body, active="exposicoes.html", desc=t["d_expos"])


# ----------------------------------------------------------------- textos
def item_texto(x, com_autor=True):
    titulo = e(x["titulo"])
    if x.get("url"):
        titulo = f'<a href="{e(x["url"])}" rel="noopener">{titulo}</a>'
    autor = f'<span class="autor">{e(x["autor"])}</span>' if com_autor else ""
    a = f'<span class="dado">{e(x["ano"])}</span>' if x.get("ano") else '<span class="dado">—</span>'
    fonte = f'<span class="dado fonte">{e(x["fonte"])}</span>' if x.get("fonte") else ""
    return f'<li>{a}<div>{autor}<span class="nome">{titulo}</span>{fonte}</div></li>'


def build_textos(c):
    t = c.t
    ordem_d = ["Floriano Romano: Esquina", "Making Oneself Heard", "Acoustic Territories", "Brasilidade", "Corpo impulso", "Desorientação"]
    dest = sorted((x for x in DATA["textos_sobre"] if x.get("destaque")),
                  key=lambda x: next((i for i, k in enumerate(ordem_d) if x["titulo"].startswith(k)), 99))
    destaques = "".join(item_texto(x) for x in dest)
    sobre = "".join(item_texto(x) for x in DATA["textos_sobre"] if not x.get("destaque"))
    dele = "".join(item_texto(x, False) for x in DATA["textos_do_artista"])
    ents = DATA.get("entrevistas", [])
    entrevistas = (f'<h2 class="sub">{t["entrevistas"]}</h2>' + "".join(
        f'<div class="entrevista"><p><span class="dado">{e(x["ano"])}</span> <span class="nome">{e(x["titulo"])}</span> '
        f'<span class="dado fonte">{e(x["fonte"])}</span></p>{video_embed(x["video"], c)}</div>' for x in ents)) if ents else ""
    body = f"""
<section class="textos">
  <h1 class="titulo-pagina">{t['textos']}</h1>
  <h2 class="sub">{t['em_destaque']}</h2>
  <ul class="lista-textos lista-destaque">{destaques}</ul>
  <h2 class="sub">{t['sobre_obra']}</h2>
  <ul class="lista-textos">{sobre}</ul>
  <h2 class="sub">{t['do_artista']}</h2>
  <ul class="lista-textos">{dele}</ul>
  <p class="dado"><a href="https://ufrj.academia.edu/FlorianoRomano" rel="noopener">{t['academia']}</a></p>
  {entrevistas}
</section>"""
    return page(c, t["textos"], body, active="textos.html", desc=t["d_textos"])


# ----------------------------------------------------------------- sobre
BIO = {
 "pt": ["Floriano Romano (Rio de Janeiro, 1969) é artista visual. Trabalha com som em instalações, objetos, ações urbanas e rádio desde 2002.",
        "Criou o programa O Inusitado (2002–2004), na Rádio Madame Satã, e participou da 7ª Bienal do Mercosul (2009).",
        "É doutor em Artes Visuais pela Universidade Federal do Rio de Janeiro e professor da Escola de Belas Artes da UFRJ e do Programa de Pós-Graduação em Linguagens Visuais."],
 "en": ["Floriano Romano (Rio de Janeiro, 1969) is a visual artist. He has worked with sound in installations, objects, urban actions and radio since 2002.",
        "He created the radio programme O Inusitado (2002–2004) on Rádio Madame Satã and took part in the 7th Mercosul Biennial (2009).",
        "He holds a PhD in Visual Arts from the Federal University of Rio de Janeiro and teaches at its School of Fine Arts (EBA/UFRJ) and in the Graduate Programme in Visual Languages."],
}
# Prêmios — inclui os financiamentos e residências por edital, que o artista conta como premiações.
# (ano, prêmio pt, prêmio en, obra, id da página da obra ou "")
PREMIOS = [
 ("2021", "Centro Municipal de Arte Hélio Oiticica, Prefeitura do Rio de Janeiro", "Centro Municipal de Arte Hélio Oiticica, City of Rio de Janeiro", "Cidade Labirinto", "cidade-labirinto"),
 ("2016", "Parque das Ruínas, Prefeitura do Rio de Janeiro", "Parque das Ruínas, City of Rio de Janeiro", "Muro de Som", "muro-de-som"),
 ("2016", "Residência artística HOBRA, Brasil–Holanda", "HOBRA artist residency, Brazil–Netherlands", "", ""),
 ("2015", "Prêmio CCBB Contemporâneo, Centro Cultural Banco do Brasil", "CCBB Contemporary Award, Centro Cultural Banco do Brasil", "Errância", "errancia"),
 ("2012", "Prêmio Marcantonio Vilaça, Funarte — aquisição para o MAC Niterói", "Marcantonio Vilaça Award, Funarte — acquired by MAC Niterói", "Chuveiros Sonoros", "chuveiros-sonoros"),
 ("2012", "Prêmio Projéteis de Arte Contemporânea, Funarte", "Projéteis Contemporary Art Award, Funarte", "A Cidade Sonora", "cidade-sonora"),
 ("2010", "Apoio a Projeto Artístico, Secretaria de Estado de Cultura do Rio de Janeiro", "Artistic Project Support, Rio de Janeiro State Secretariat of Culture", "Intrasom", "intrasom"),
 ("2010", "Conexão Artes Visuais, Funarte — Projeto EME>>", "Conexão Artes Visuais, Funarte — Projeto EME>>", "Rádio Lugar", "radio-lugar"),
 ("2009", "Prêmio Interações Estéticas, Funarte", "Interações Estéticas Award, Funarte", "Sapatos Sonoros", "sapatos-sonoros"),
 ("2008", "Bolsa de Estímulo à Criação Artística, Funarte", "Artistic Creation Grant, Funarte", "Chapéu Panorâmico", "chapeu-panoramico"),
 ("2007", "Prêmio Projéteis de Arte Contemporânea, Funarte", "Projéteis Contemporary Art Award, Funarte", "Sample Way of Life", ""),
 ("2007", "Menção honrosa, 58º Salão de Abril, Fortaleza", "Honourable mention, 58th Salão de Abril, Fortaleza", "Falante", "falante"),
 ("2000", "Bolsa de residência, Câmara Municipal do Porto — Ateliers da Lada", "Residency grant, Porto City Council — Ateliers da Lada", "Do Deslocamento", ""),
 ("1992", "Menção honrosa, Prêmio Philips, Museu Nacional de Belas Artes", "Honourable mention, Philips Award, Museu Nacional de Belas Artes", "", ""),
]
INDICACOES = [("2010", "Prêmio PIPA", "PIPA Prize")]
COLECOES = [
 ("Museu de Arte do Rio — O Rio dos Navegantes", "Museu de Arte do Rio — O Rio dos Navegantes"),
 ("Museu de Arte Contemporânea de Niterói — Chuveiros Sonoros, Chapéu Panorâmico", "Museu de Arte Contemporânea de Niterói — Chuveiros Sonoros, Chapéu Panorâmico"),
 ("Museo de Artes Visuales, Santiago do Chile — Falante (vídeo)", "Museo de Artes Visuales, Santiago, Chile — Falante (video)"),
 ("Centro Provincial de Diseño y Oficios, Havana — mochila de Falante", "Centro Provincial de Diseño y Oficios, Havana — Falante backpack"),
 ("Coleção Sérgio Carvalho — Turbina, Chuveiros Sonoros, Radionovelas", "Sérgio Carvalho Collection — Turbina, Chuveiros Sonoros, Radionovelas"),
 ("Coleção Augusto Rodrigues — Sapatos Sonoros", "Augusto Rodrigues Collection — Sapatos Sonoros"),
]


def build_sobre(c):
    t, lang = c.t, c.lang
    i = 1 if lang == "en" else 0
    bio = BIO[lang]
    def obra_link(nome, oid):
        if not nome:
            return ""
        return f'<a class="nome" href="obras/{oid}.html">{e(nome)}</a>' if oid else f'<span class="nome">{e(nome)}</span>'
    premios = "".join(f'<li><span class="dado sinal">{p[0]}</span><div>{obra_link(p[3], p[4])}<span class="premio-nome{" so-premio" if not p[3] else ""}">{e(p[1 + i])}</span></div></li>'
                      for p in PREMIOS)
    premios += "".join(f'<li class="indicacao"><span class="dado">{p[0]}</span><div><span class="premio-nome">{t["indicacao"]} — {e(p[1 + i])}</span></div></li>'
                       for p in INDICACOES)
    cols = "".join(f"<li>{e(x[i])}</li>" for x in COLECOES)
    body = f"""
<section class="sobre">
  <h1 class="titulo-pagina">{t['sobre']}</h1>
  <div class="sobre-grade">
    <div class="sobre-texto">
      <p class="abertura">{e(bio[0])}</p>
      {''.join(f'<p>{e(p)}</p>' for p in bio[1:])}
      <h2 class="sub sub-premios">{t['premios']}</h2>
      <ul class="lista-premios">{premios}</ul>
    </div>
    <div class="sobre-dados">
      <h2 class="sub">{t['colecoes']}</h2>
      <ul class="lista-simples">{cols}</ul>
      <h2 class="sub">{t['videos']}</h2>
      <p><a href="https://www.youtube.com/@openradio" rel="noopener">YouTube — @openradio</a><br><a href="https://vimeo.com/user12897613" rel="noopener">Vimeo</a></p>
      <h2 class="sub">Instagram</h2>
      <p><a href="https://www.instagram.com/florianoromano/" rel="noopener">@florianoromano</a></p>
      <h2 class="sub">{t['contato']}</h2>
      <p class="dado" data-contato>{t['contato_txt']}</p>
    </div>
  </div>
</section>"""
    return page(c, t["sobre"], body, active="sobre.html", desc=t["d_sobre"])


# ----------------------------------------------------------------- main
def escreve(rel_lang_root, lang, rel, conteudo):
    p = OUT / rel_lang_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(conteudo, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if (ROOT / "media").exists():
        shutil.copytree(ROOT / "media", OUT / "media")
    (OUT / ".nojekyll").write_text("")
    if not PREVIA:
        (OUT / "CNAME").write_text("florianoromano.art.br\n")
    ordem = sorted(OBRAS, key=lambda o: (-o["ano_num"], o["titulo"]))
    for lang, raiz in (("pt", ""), ("en", "en")):
        paginas = {"index.html": build_index, "indice.html": build_indice, "radio.html": build_radio,
                   "exposicoes.html": build_exposicoes, "textos.html": build_textos, "sobre.html": build_sobre}
        for rel, fn in paginas.items():
            escreve(raiz, lang, rel, fn(Ctx(lang, rel)))
        for i, o in enumerate(ordem):
            rel = f"obras/{o['id']}.html"
            escreve(raiz, lang, rel, build_obra(o, ordem[i - 1] if i else None, ordem[i + 1] if i + 1 < len(ordem) else None, Ctx(lang, rel)))
    print(f"ok — {len(OBRAS)} obras × 2 línguas, saída em {OUT}")


if __name__ == "__main__":
    main()
