"""Mapa Esquina da página inicial, desenhado com os recursos dos desenhos de Floriano Romano.

Recursos tirados dos desenhos (fita isolante, 2007– ; Esquinas I–X, 2023):
  - feixes de linhas quase paralelas que convergem para pontos de fuga diferentes, alguns fora do quadro;
  - um vértice dentro do quadro de onde se abre um leque denso (aqui: a obra Esquina);
  - espessura conforme o plano: a linha grossa vem para a frente, a fina recua;
  - planos fechados (triângulos, quadriláteros) que se dobram uns sobre os outros, com a fita passando além do vértice;
  - linhas que começam ou terminam dentro do quadro;
  - verticais de elevação misturadas com diagonais de perspectiva;
  - a linha da frente interrompe a de trás (o papel aparece no cruzamento).

Cada obra é o cruzamento de linhas que vêm de pontos de vista diferentes. Quando o visitante move o cursor,
os pontos de fuga se deslocam e as linhas giram em torno das obras (assets/js/mapa.js): as obras ficam no lugar,
o ponto de vista muda.
"""
import hashlib, json, math

W, H = 1000, 560

# Pontos de fuga. "E" é a própria obra Esquina (vértice interno, não se move).
VP = {
    "A": (-520, -640),    # diagonais finas que descem para a direita (fundo)
    "B": (1270, 300),     # feixe que converge logo além da borda direita (teto)
    "C": (520, 830),      # leque que sobe de baixo (chão)
    "D": (700, -3200),    # quase verticais: elevação (fundo)
    "F": (-420, 780),     # diagonais que sobem para a direita
}
MOVE = {"A": 1.0, "B": 0.7, "C": 1.1, "D": 0.5, "F": 0.9, "E": 0}   # quanto cada ponto de vista se desloca

# Obras no mapa: posição, nível (3 = premiadas e centrais), lado do rótulo.
NOS = {
    # nível 3 — prêmios e obras centrais
    "esquina":           dict(p=(612, 196), t=3, lado="d"),
    "sonar":             dict(p=(318, 96),  t=3, lado="d"),
    "cidade-sonora":     dict(p=(92, 210),  t=3, lado="d"),
    "chuveiros-sonoros": dict(p=(122, 462), t=3, lado="d"),
    "errancia":          dict(p=(420, 352), t=3, lado="d"),
    # nível 2
    "esquinas":          dict(p=(818, 318), t=2, lado="d"),
    "falante":           dict(p=(470, 512), t=2, lado="d"),
    "sapatos-sonoros":   dict(p=(262, 292), t=2, lado="d"),
    "cidade-labirinto":  dict(p=(700, 470), t=2, lado="d"),
    "muro-de-som":       dict(p=(206, 128), t=2, lado="e"),
    "chapeu-panoramico": dict(p=(848, 98),  t=2, lado="d"),
    # nível 1
    "turbina":           dict(p=(726, 62),  t=1, lado="d"),
    "mascara-sonora":    dict(p=(934, 222), t=1, lado="e"),
    "historias-anonimas": dict(p=(492, 150), t=1, lado="e"),
    "mar-sobre-mar":     dict(p=(566, 408), t=1, lado="d"),
    "cruz":              dict(p=(36, 336),  t=1, lado="d"),
    "desenhos":          dict(p=(944, 486), t=1, lado="e"),
}

# Celular (composição vertical, 560 × 1000): posições próprias onde a rotação simples faria rótulos colidirem.
PV = {
    "cidade-sonora":     (104, 944, "d"),
    "chuveiros-sonoros": (446, 848, "e"),
    "falante":           (522, 492, "e"),
    "errancia":          (346, 586, "d"),
    "sapatos-sonoros":   (286, 744, "d"),
    "historias-anonimas": (150, 500, "d"),
}

# Sistemas de linhas: cada um é um ponto de vista. Âncora = obra (nome) ou ponto livre (x, y).
# (âncora, espessura, frações do trecho visível)
SISTEMAS = {
    "B": [("sonar", 1, (0, .97)), ("muro-de-som", .6, (0, .9)), ("cidade-sonora", 3.4, (0, .99)),
          ("esquina", 2.2, (0, .98)), ((0, 252), 1.4, (0, .96)), ((0, 270), .6, (0, .99)), ("mascara-sonora", .6, (.5, 1))],
    "C": [("falante", 2.2, (0, .78)), ("errancia", 3.4, (0, .86)), ("sapatos-sonoros", 1, (0, 1)),
          ("mar-sobre-mar", 1.4, (0, .7)), ("historias-anonimas", .6, (0, 1)), ((300, 0), .6, (0, .55)), ((650, 0), 1, (0, .62))],
    "A": [("chuveiros-sonoros", 1.4, (.1, 1)), ("cruz", .6, (0, 1)), ("esquinas", 1, (.2, 1)),
          ("turbina", .6, (0, .8)), ("desenhos", .6, (.3, 1))],
    "F": [("chapeu-panoramico", 1.4, (.15, 1)), ("cidade-labirinto", 2.2, (.25, 1)), ("sonar", 1, (.2, 1)),
          ("mascara-sonora", 1, (.4, 1)), ("chuveiros-sonoros", 4.4, (0, .62))],
    "D": [("muro-de-som", .6, (0, .7)), ("turbina", 1, (0, .5)), ("desenhos", .6, (.25, 1)), ("cruz", 1, (.3, 1)),
          ("historias-anonimas", .6, (0, .45)), ((410, 0), .6, (.4, 1)), ((880, 0), 1.4, (.1, .66))],
    # leque denso que nasce na Esquina e desce para a direita, como o vértice dos desenhos de fita
    "E": [((694, 560), 3.4, (0, 1)), ((706, 560), 1, (0, 1)), ((717, 560), .6, (0, 1)), ((731, 560), 2.2, (0, 1)),
          ((748, 560), .6, (0, 1)), ((772, 560), 1, (0, 1)), ("cidade-labirinto", 1.4, (0, 1)), ("esquinas", 1, (0, 1)),
          ((1000, 404), .6, (0, 1))],
}

# Planos fechados que se dobram: vértices em obras; a fita passa um pouco além do vértice.
PLANOS = [
    dict(nos=["cidade-sonora", "muro-de-som", "sonar", "sapatos-sonoros"], larg=1.4),
    dict(nos=["sapatos-sonoros", "sonar", "errancia"], larg=0.6),
    dict(nos=["errancia", "falante", "chuveiros-sonoros"], larg=4.0),
    dict(nos=["esquinas", "mar-sobre-mar", "cidade-labirinto"], larg=1),
    dict(nos=["turbina", "chapeu-panoramico", "esquina"], larg=0.6),
]

FRENTE = 3.0      # a partir desta espessura a linha interrompe as que passam atrás
PASSA = 0.035     # no vértice interno (Esquina) as linhas passam um pouco do ponto, como a fita


def _h(*xs):
    return int(hashlib.md5("|".join(map(str, xs)).encode()).hexdigest(), 16)


def recorte(p, d, w=W, h=H):
    """Interseção da reta p + t·d com o retângulo: devolve (t_entrada, t_saída) ou None."""
    t0, t1 = -1e9, 1e9
    for pi, di, lo, hi in ((p[0], d[0], 0, w), (p[1], d[1], 0, h)):
        if abs(di) < 1e-9:
            if pi < lo or pi > hi:
                return None
            continue
        a, b = (lo - pi) / di, (hi - pi) / di
        if a > b:
            a, b = b, a
        t0, t1 = max(t0, a), min(t1, b)
    return (t0, t1) if t0 < t1 else None


def segmento(v, a, s, raio=False, w=W, h=H):
    """Trecho da reta que vai do ponto de fuga v pelo ponto a; s = frações (início, fim) do trecho dentro do quadro."""
    d = (a[0] - v[0], a[1] - v[1])
    r = recorte(v, d, w, h)
    if not r:
        return None
    t0, t1 = r
    if raio:
        t0 = max(t0, -PASSA)
    if t1 <= t0:
        return None
    ta, tb = t0 + (t1 - t0) * s[0], t0 + (t1 - t0) * s[1]
    return (v[0] + d[0] * ta, v[1] + d[1] * ta, v[0] + d[0] * tb, v[1] + d[1] * tb)


def geometria(pos, T):
    """Lista de linhas: dict(v=sistema, a=âncora, s=frações, w=espessura, n=obras, raio). pos já transformadas."""
    linhas = []
    for sv, itens in SISTEMAS.items():
        for anc, wd, fr in itens:
            if isinstance(anc, str):
                a, ns = pos[anc], [anc]
            else:
                a, ns = T(anc), []
            if sv == "E":
                ns = ["esquina"] + ns
            linhas.append(dict(v=sv, a=a, s=fr, w=wd, n=ns, raio=(sv == "E")))
    return linhas


def arestas_planos(pos):
    out = []
    for pl in PLANOS:
        pts = [pos[n] for n in pl["nos"]]
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = math.hypot(dx, dy) or 1
            e1, e2 = 8 + _h(p, q) % 14, 8 + _h(q, p) % 14     # a fita passa do vértice
            ux, uy = dx / L, dy / L
            out.append(dict(x1=p[0] - ux * e1, y1=p[1] - uy * e1, x2=q[0] + ux * e2, y2=q[1] + uy * e2,
                            w=pl["larg"], n=[pl["nos"][i], pl["nos"][(i + 1) % len(pts)]]))
    return out


def svg(c, by_id, esc, ano_fn, ano_en, vertical=False):
    """SVG do mapa. vertical=True gira a composição para o celular."""
    w, h = (H, W) if vertical else (W, H)
    def T(p):
        return (p[1], W - p[0]) if vertical else (p[0], p[1])
    vps = {k: T(v) for k, v in VP.items()}
    pos = {k: (PV[k][:2] if vertical and k in PV else T(nd["p"])) for k, nd in NOS.items()}
    vps["E"] = pos["esquina"]
    fundo, meio, halos, frente = [], [], [], []

    def emite(x1, y1, x2, y2, wd, ns, extra=""):
        attrs = f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" data-n="{" ".join(ns)}"{extra}'
        if wd >= FRENTE:
            halos.append(f'<line class="m-halo" {attrs} stroke-width="{wd + 7:.1f}"/>')
            frente.append(f'<line {attrs} stroke-width="{wd}"/>')
        elif wd <= 1:
            fundo.append(f'<line {attrs} stroke-width="{wd}"/>')
        else:
            meio.append(f'<line {attrs} stroke-width="{wd}"/>')

    for ln in geometria(pos, T):
        v, a = vps[ln["v"]], ln["a"]
        seg = segmento(v, a, ln["s"], ln.get("raio", False), w, h)
        if not seg:
            continue
        extra = (f' data-v="{ln["v"]}" data-a="{a[0]:.1f},{a[1]:.1f}" data-s="{ln["s"][0]},{ln["s"][1]}"'
                 + (' data-r="1"' if ln.get("raio") else ""))
        emite(*seg, ln["w"], ln["n"], extra)
    for ar in arestas_planos(pos):
        p1, p2 = (ar["x1"], ar["y1"]), (ar["x2"], ar["y2"])
        emite(p1[0], p1[1], p2[0], p2[1], ar["w"], ar["n"], ' data-plano="1"')

    nos = []
    for k, nd in NOS.items():
        o = by_id[k]
        x, y = pos[k]
        t = nd["t"]
        esq = nd["lado"] == "e"
        if vertical:
            esq = PV[k][2] == "e" if k in PV else x > 340
        dx = -14 if esq else 14
        anchor = "end" if esq else "start"
        r = {3: 9.5, 2: 6.5, 1: 4.5}[t]
        premio = (o.get("premio_curto_en") if c.lang == "en" else o.get("premio_curto")) or ""
        circ = f'<circle class="m-pt{"" if t >= 2 else " m-vazado"}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
        if premio:
            circ = f'<circle class="m-selo" cx="{x:.1f}" cy="{y:.1f}" r="{r + 4.5}"/>' + circ
        fs = {3: 24, 2: 17, 1: 14}[t]
        ny = y - 6 if t == 3 else y - 4
        rot_ano = o.get("ano_mapa") or o["ano"].split(" /")[-1].strip()
        if c.lang == "en":
            rot_ano = ano_en.get(rot_ano, rot_ano)
        linha_ano = esc(rot_ano)
        txt = (f'<text class="m-nome" x="{x + dx:.1f}" y="{ny:.1f}" text-anchor="{anchor}">{esc(o["titulo"])}</text>'
               f'<text class="m-ano" x="{x + dx:.1f}" y="{ny + (16 if t == 3 else 13):.1f}" text-anchor="{anchor}">{linha_ano}</text>')
        if premio:
            txt += f'<text class="m-premio" x="{x + dx:.1f}" y="{ny + (29 if t == 3 else 25):.1f}" text-anchor="{anchor}">{esc(premio)}</text>'
        nos.append(
            f'<a class="m-no t{t}{" premiada" if premio else ""}" href="obras/{k}.html" data-id="{k}" data-ano="{o["ano_num"]}" '
            f'aria-label="{esc(o["titulo"])}, {esc(ano_fn(o, c.lang))}{", " + esc(premio) if premio else ""}">'
            f'<circle class="m-alvo" cx="{x:.1f}" cy="{y:.1f}" r="22"/>{circ}{txt}</a>')
    move = json.dumps({k: MOVE.get(k, 0) for k in vps})
    pontos = json.dumps({k: [round(v[0], 1), round(v[1], 1)] for k, v in vps.items()})
    return (f'<svg class="mapa {"mapa-v" if vertical else "mapa-h"}" viewBox="0 0 {w} {h}" role="group" '
            f'aria-label="{c.t["mapa_aria"]}" data-vp=\'{pontos}\' data-move=\'{move}\' data-w="{w}" data-h="{h}">'
            f'<g class="m-linhas" aria-hidden="true"><g class="m-fundo">{"".join(fundo)}</g><g class="m-meio">{"".join(meio)}</g>'
            f'<g class="m-halos">{"".join(halos)}</g><g class="m-frente">{"".join(frente)}</g></g>'
            f'<g class="m-nos">{"".join(nos)}</g></svg>')
