"""Mapa Esquina da página inicial, construído sobre o desenho Esquina VI (série Esquinas I–X, 2023).

As linhas foram vetorizadas da fotografia da tela (tools/vetoriza_esquina.py → data/esquina-06.json):
mesmas linhas, mesmos vértices, mesmas espessuras relativas, incluindo os feixes de três paralelas.
O desenho é alargado para o formato do quadro e recortado pela moldura; cada obra ocupa um cruzamento
real do desenho, escolhido para que os nomes se leiam bem.

Movimento (assets/js/mapa.js): leve e bidimensional, sem giro. O plano inteiro se inclina um pouco em perspectiva
conforme o cursor (uma transformação projetiva, que mantém linhas retas e vértices unidos); sem cursor,
deriva devagar.
"""
import hashlib, json, math
from pathlib import Path

W, H = 1000, 560
DESENHO = json.loads((Path(__file__).parent / "data" / "esquina-06.json").read_text(encoding="utf-8"))
# Ajuste pedido pelo artista (out/2026): entre Errância e Esquina, a linha da direita do feixe some
# e volta só depois da linha que cruza, para encostar na Esquina.
_l = DESENHO[14]
DESENHO[14] = dict(a=_l["a"], b=[374.0, 506.3], w=_l["w"])
DESENHO.append(dict(a=[431.8, 344.5], b=[443.6, 280.1], w=_l["w"]))
DW, DH = 800, 790            # tamanho da imagem de onde as linhas foram tiradas
SX, SY = 1.12, 0.80          # alargamento para o quadro horizontal
SXV, SYV = 0.69, 1.18        # no celular a tela fica de pé, alongada na vertical (quadro 560 × 1000)
ESP = 0.42                   # espessura medida (px da imagem) → unidades do quadro
PROF = 230                   # profundidade máxima das camadas de linha (±), para o giro
FRENTE = 99                  # na tela pintada as linhas se cruzam sem interrupção (sem contorno de papel)

# Obras: cruzamento do desenho escolhido para cada uma (coordenadas aproximadas do quadro; o código
# encaixa no cruzamento exato mais próximo), nível e lado do rótulo.
NOS = {
    "esquina":           dict(p=(550, 188), t=3, lado="d"),
    "sonar":             dict(p=(365, 197), t=3, lado="d"),
    "cidade-sonora":     dict(p=(249, 233), t=3, lado="d"),
    "chuveiros-sonoros": dict(p=(71, 365),  t=3, lado="d"),
    "errancia":          dict(p=(437, 348), t=3, lado="d"),
    "esquinas":          dict(p=(808, 321), t=2, lado="e"),
    "falante":           dict(p=(466, 528), t=2, lado="d"),
    "sapatos-sonoros":   dict(p=(207, 289), t=2, lado="d"),
    "cidade-labirinto":  dict(p=(675, 397), t=2, lado="d"),
    "muro-de-som":       dict(p=(461, 142), t=2, lado="e"),
    "chapeu-panoramico": dict(p=(784, 173), t=2, lado="d"),
    "intrasom":          dict(p=(704, 281), t=2, lado="e"),
    "radio-lugar":       dict(p=(341, 397), t=2, lado="d"),
    "turbina":           dict(p=(722, 204), t=1, lado="d"),
    "mascara-sonora":    dict(p=(797, 221), t=1, lado="d"),
    "historias-anonimas": dict(p=(471, 299), t=1, lado="e"),
    "mar-sobre-mar":     dict(p=(567, 428), t=1, lado="e"),
    "cruz":              dict(p=(301, 365), t=1, lado="d"),
    "desenhos":          dict(p=(851, 418), t=1, lado="d"),
}


# Celular (tela de pé, 560 × 1000): cruzamento e lado do rótulo escolhidos para essa composição.
PV = {
    "muro-de-som":       (256, 297, "d"),
    "sonar":             (187, 372, "d"),
    "esquina":           (311, 364, "d"),
    "chapeu-panoramico": (462, 413, "e"),
    "turbina":           (373, 442, "d"),
    "cidade-sonora":     (125, 431, "d"),
    "historias-anonimas": (337, 486, "e"),
    "intrasom":          (405, 501, "d"),
    "sapatos-sonoros":   (99, 513, "d"),
    "errancia":          (276, 554, "e"),
    "mascara-sonora":    (470, 561, "e"),
    "cruz":              (157, 626, "e"),
    "radio-lugar":       (267, 639, "d"),
    "esquinas":          (387, 671, "d"),
    "chuveiros-sonoros": (182, 673, "d"),
    "desenhos":          (496, 704, "e"),
    "cidade-labirinto":  (329, 729, "d"),
    "mar-sobre-mar":     (362, 769, "d"),
    "falante":           (259, 866, "d"),
}


def para_quadro(vertical=False):
    """Função que leva coordenadas do desenho para o quadro (centralizado, recortado nas bordas)."""
    w, h, sx, sy = (H, W, SXV, SYV) if vertical else (W, H, SX, SY)
    ox, oy = (w - DW * sx) / 2, (h - DH * sy) / 2
    return lambda x, y: (ox + x * sx, oy + y * sy)


def do_horizontal(p):
    """Posição no quadro horizontal → coordenadas do desenho."""
    ox, oy = (W - DW * SX) / 2, (H - DH * SY) / 2
    return ((p[0] - ox) / SX, (p[1] - oy) / SY)


def linhas_quadro(vertical=False):
    """Linhas do desenho nas coordenadas do quadro."""
    M = para_quadro(vertical)
    return [dict(a=M(*s["a"]), b=M(*s["b"]), w=round(max(1.2, s["w"] * ESP), 2)) for s in DESENHO]


def cruzamentos(ls, w=W, h=H):
    """Pontos onde duas linhas do desenho se cruzam (dentro dos dois segmentos e do quadro)."""
    pts = []
    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            (x1, y1), (x2, y2) = ls[i]["a"], ls[i]["b"]
            (x3, y3), (x4, y4) = ls[j]["a"], ls[j]["b"]
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(d) < 1e-6:
                continue
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / d
            if -0.02 <= t <= 1.02 and -0.02 <= u <= 1.02:
                x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
                if 20 < x < w - 20 and 20 < y < h - 20:
                    pts.append((x, y, i, j))
    return pts


def posicoes(ls, vertical=False):
    """Encaixa cada obra no cruzamento exato mais próximo da posição escolhida."""
    w, h = (H, W) if vertical else (W, H)
    pts = cruzamentos(ls, w, h)
    M = para_quadro(vertical)
    pos, linhas_de = {}, {}
    for k, nd in NOS.items():
        px, py = PV[k][:2] if vertical and k in PV else M(*do_horizontal(nd["p"]))
        q = min(pts, key=lambda q: (q[0] - px) ** 2 + (q[1] - py) ** 2)
        pos[k] = (q[0], q[1]) if (q[0] - px) ** 2 + (q[1] - py) ** 2 < 15 ** 2 else (px, py)
    for k, (x, y) in pos.items():
        linhas_de[k] = [i for i, l in enumerate(ls) if _dist_seg((x, y), l["a"], l["b"]) < 3.5]
    return pos, linhas_de


def _h(*xs):
    return int(hashlib.md5("|".join(map(str, xs)).encode()).hexdigest(), 16)


def profundidade(i):
    """Cada linha numa camada própria, com leve inclinação: (z no início, z no fim)."""
    base = ((_h("z", i) % 1000) / 1000 * 2 - 1) * PROF
    incl = ((_h("i", i) % 1000) / 1000 * 2 - 1) * PROF * 0.35
    return base - incl, base + incl


def z_no_ponto(l, z, p):
    """Profundidade de uma linha no ponto p (interpolação ao longo do segmento)."""
    (ax, ay), (bx, by) = l["a"], l["b"]
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / ((dx * dx + dy * dy) or 1)))
    return z[0] + (z[1] - z[0]) * t


def _dist_seg(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy or 1
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def svg(c, by_id, esc, ano_fn, ano_en, vertical=False):
    """SVG do mapa. vertical=True: a tela de pé, para o celular."""
    w, h = (H, W) if vertical else (W, H)
    def T(p):
        return p
    ls = linhas_quadro(vertical)
    pos, linhas_de = posicoes(ls, vertical)
    obras_na = {i: [k for k, idx in linhas_de.items() if i in idx] for i in range(len(ls))}

    cx, cy = w / 2, h / 2
    zs = [profundidade(i) for i in range(len(ls))]
    fundo, halos, frente = [], [], []
    for i, l in enumerate(ls):
        a, b = l["a"], l["b"]
        dados = f'{a[0] - cx:.1f},{a[1] - cy:.1f},{zs[i][0]:.0f},{b[0] - cx:.1f},{b[1] - cy:.1f},{zs[i][1]:.0f}'
        attrs = (f'x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                 f'data-p="{dados}" data-n="{" ".join(obras_na[i])}"')
        if l["w"] >= FRENTE:
            halos.append(f'<line class="m-halo" {attrs} stroke-width="{l["w"] + 6:.1f}"/>')
            frente.append(f'<line {attrs} stroke-width="{l["w"]}"/>')
        else:
            fundo.append(f'<line {attrs} stroke-width="{l["w"]}"/>')

    nos = []
    for k, nd in NOS.items():
        if k not in pos:
            continue
        o = by_id[k]
        x, y = T(pos[k])
        t = nd["t"]
        idx = linhas_de.get(k) or []
        if idx:      # a obra fica na camada das linhas que a atravessam (a mais grossa pesa mais)
            pesos = [ls[i]["w"] for i in idx]
            z = sum(z_no_ponto(ls[i], zs[i], (x, y)) * wgt for i, wgt in zip(idx, pesos)) / sum(pesos)
        else:
            z = 0
        esq = (PV[k][2] == "e" if k in PV else x > w * 0.6) if vertical else nd["lado"] == "e"
        dx = -13 if esq else 13
        anchor = "end" if esq else "start"
        r = {3: 5, 2: 4, 1: 3.2}[t]
        premiada = bool(o.get("premio"))
        circ = f'<circle class="m-pt{"" if t >= 2 else " m-vazado"}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
        if premiada:
            circ = f'<circle class="m-selo" cx="{x:.1f}" cy="{y:.1f}" r="{r + 2.6}"/>' + circ
        ny = y - 5 if t == 3 else y - 4
        rot_ano = o.get("ano_mapa") or o["ano"].split(" /")[-1].strip()
        if c.lang == "en":
            rot_ano = ano_en.get(rot_ano, rot_ano)
        txt = (f'<text class="m-nome" x="{x + dx:.1f}" y="{ny:.1f}" text-anchor="{anchor}">{esc(o["titulo"])}</text>'
               f'<text class="m-ano" x="{x + dx:.1f}" y="{ny + (14 if t == 3 else 12):.1f}" text-anchor="{anchor}">{esc(rot_ano)}</text>')
        nos.append(
            f'<a class="m-no t{t}{" premiada" if premiada else ""}" href="obras/{k}.html" data-id="{k}" data-ano="{o["ano_num"]}" '
            f'data-x="{x:.1f}" data-y="{y:.1f}" data-p="{x - cx:.1f},{y - cy:.1f},{z:.0f}" data-lado="{"e" if esq else "d"}" aria-label="{esc(o["titulo"])}, {esc(ano_fn(o, c.lang))}">'
            f'<circle class="m-alvo" cx="{x:.1f}" cy="{y:.1f}" r="22"/>{circ}{txt}</a>')

    return (f'<svg class="mapa {"mapa-v" if vertical else "mapa-h"}" viewBox="0 0 {w} {h}" role="group" '
            f'aria-label="{c.t["mapa_aria"]}" data-w="{w}" data-h="{h}" data-foco="0" data-raio="{w / 2:.0f}">'
            f'<defs><clipPath id="corte-{"v" if vertical else "h"}"><rect x="0" y="0" width="{w}" height="{h}"/></clipPath></defs>'
            f'<g class="m-linhas" aria-hidden="true" clip-path="url(#corte-{"v" if vertical else "h"})"><g class="m-fundo">{"".join(fundo)}</g>'
            f'<g class="m-halos">{"".join(halos)}</g><g class="m-frente">{"".join(frente)}</g></g>'
            f'<g class="m-nos">{"".join(nos)}</g></svg>')
