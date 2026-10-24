"""Mapa Esquina da página inicial, desenhado com os recursos dos desenhos de Floriano Romano.

Recursos tirados dos desenhos (fita isolante, 2007– ; Esquinas I–X, 2023):
  - feixes de linhas que convergem para pontos de fuga diferentes, alguns fora do quadro;
  - um vértice de onde se abre um leque denso (aqui: a obra Esquina);
  - espessura conforme o plano: a linha grossa vem para a frente, a fina recua;
  - planos fechados (triângulos, quadriláteros) que se dobram, com a fita passando além do vértice;
  - linhas que começam ou terminam dentro do quadro;
  - a linha da frente interrompe a de trás (o papel aparece no cruzamento).

O desenho existe em três dimensões, dentro de uma esfera. Cada obra é um ponto no espaço; cada linha é uma corda
da esfera que passa pela obra e por um ponto de fuga (também no espaço). assets/js/mapa.js gira a esfera em torno
do eixo vertical — com o cursor, mais de 180 graus; sem cursor, gira devagar sozinha — e projeta tudo em perspectiva.
"""
import hashlib, json, math

W, H = 1000, 560
FOCO = 2200        # distância do olho para a perspectiva (mesmo valor em mapa.js)

# Pontos de fuga no espaço (x, y no desenho; z = profundidade). "E" é a própria obra Esquina.
VP = {
    "A": (-520, -640, 520),    # diagonais que descem para a direita, vindas da frente
    "B": (1270, 300, -380),    # feixe que converge à direita, lá atrás
    "C": (520, 830, 260),      # leque que sobe de baixo
    "D": (700, -3200, 0),      # quase verticais
    "F": (-420, 780, -460),    # diagonais que sobem para a direita, vindas de trás
}

# Obras: posição no desenho, nível (3 = premiadas e centrais), lado inicial do rótulo, profundidade z.
NOS = {
    # nível 3 — prêmios e obras centrais
    "esquina":           dict(p=(612, 196), t=3, lado="d", z=90),
    "sonar":             dict(p=(318, 96),  t=3, lado="d", z=-160),
    "cidade-sonora":     dict(p=(92, 210),  t=3, lado="d", z=-120),
    "chuveiros-sonoros": dict(p=(122, 462), t=3, lado="d", z=170),
    "errancia":          dict(p=(420, 352), t=3, lado="d", z=120),
    # nível 2
    "esquinas":          dict(p=(818, 318), t=2, lado="d", z=-90),
    "falante":           dict(p=(470, 512), t=2, lado="d", z=220),
    "sapatos-sonoros":   dict(p=(262, 292), t=2, lado="d", z=-30),
    "cidade-labirinto":  dict(p=(700, 470), t=2, lado="d", z=40),
    "muro-de-som":       dict(p=(206, 128), t=2, lado="e", z=-240),
    "chapeu-panoramico": dict(p=(848, 98),  t=2, lado="d", z=-220),
    "intrasom":          dict(p=(652, 284), t=2, lado="e", z=-10),
    "radio-lugar":       dict(p=(286, 524), t=2, lado="d", z=150),
    # nível 1
    "turbina":           dict(p=(726, 62),  t=1, lado="d", z=-300),
    "mascara-sonora":    dict(p=(934, 222), t=1, lado="e", z=-60),
    "historias-anonimas": dict(p=(492, 150), t=1, lado="e", z=-200),
    "mar-sobre-mar":     dict(p=(566, 408), t=1, lado="d", z=260),
    "cruz":              dict(p=(36, 336),  t=1, lado="d", z=60),
    "desenhos":          dict(p=(944, 486), t=1, lado="e", z=-40),
}

# Celular (composição vertical, 560 × 1000): posições próprias onde a rotação simples faria rótulos colidirem.
PV = {
    "cidade-sonora":     (104, 944, "d"),
    "chuveiros-sonoros": (450, 836, "e"),
    "falante":           (522, 492, "e"),
    "errancia":          (346, 586, "d"),
    "sapatos-sonoros":   (286, 744, "d"),
    "historias-anonimas": (150, 500, "d"),
    "intrasom":          (262, 452, "d"),
    "radio-lugar":       (520, 664, "e"),
}

# Poucas cordas que atravessam a esfera: cada uma passa por uma obra e por um ponto de fuga no espaço.
# (âncora, espessura, frações do trecho visível da corda)
SISTEMAS = {
    "B": [("cidade-sonora", 3.4, (0, .96))],
    "C": [("errancia", 2.2, (0, .9))],
    "F": [("chuveiros-sonoros", 4.4, (0, .66))],
}

# Planos fechados que se sobrepõem, como no desenho a lápis de 2026; "dupla" = traço passado duas vezes.
PLANOS = [
    dict(nos=["cidade-sonora", "turbina", "esquina"], larg=1.4, dupla=True),                      # triângulo alto
    dict(nos=["sapatos-sonoros", "esquinas", "cidade-labirinto", "radio-lugar"], larg=1.4),        # quadrilátero central
    dict(nos=["chapeu-panoramico", "mascara-sonora", "desenhos", "esquinas"], larg=1, dupla=True), # caixa à direita
    dict(nos=["errancia", "falante", "chuveiros-sonoros"], larg=4.0),                              # triângulo da frente
    dict(nos=["muro-de-som", "sonar", "cidade-sonora"], larg=1),
    dict(nos=["cruz", "chuveiros-sonoros", "radio-lugar"], larg=1.4),
]

# Vértice: várias linhas partem da Esquina e terminam em outras obras.
VERTICE = dict(no="esquina", alvos=[("sonar", 1.4), ("intrasom", 1), ("mar-sobre-mar", 1.4), ("errancia", 2.2),
                                     ("historias-anonimas", 1)])

# Ponta longa e fina que escapa para baixo, à direita (duas linhas que se encontram fora das obras).
PONTA = dict(apice=(990, 556, 40), de=[("falante", 1), ("mar-sobre-mar", 1.4)])

FRENTE = 3.0      # a partir desta espessura a linha interrompe as que passam atrás
PASSA = 0.04      # no vértice (Esquina) as linhas passam um pouco do ponto, como a fita


def _h(*xs):
    return int(hashlib.md5("|".join(map(str, xs)).encode()).hexdigest(), 16)


class Cena:
    """O desenho no espaço, centrado na origem, dentro de um elipsoide do tamanho do quadro."""

    def __init__(self, w, h, vertical):
        self.w, self.h, self.vertical = w, h, vertical
        self.cx, self.cy = w / 2, h / 2
        self.a, self.b = w / 2 - 8, h / 2 - 6       # raios horizontal e vertical
        self.c = self.a * 0.95                       # raio em profundidade: igual ao horizontal, a esfera gira sem sair do quadro

    def T(self, x, y):
        """Desenho horizontal → composição do quadro (gira 90° no celular)."""
        return (y, W - x) if self.vertical else (x, y)

    def ponto(self, x, y, z):
        """Coordenadas do quadro + z → espaço centrado."""
        return (x - self.cx, y - self.cy, z)

    def dentro(self, p, folga=0.9):
        """Empurra um ponto para dentro do elipsoide, se preciso."""
        X, Y, Z = p
        q = (X / self.a) ** 2 + (Y / self.b) ** 2 + (Z / self.c) ** 2
        if q <= folga ** 2:
            return p
        # reduz primeiro a profundidade; se não bastar, aproxima do centro
        r2 = folga ** 2 - (X / self.a) ** 2 - (Y / self.b) ** 2
        if r2 > 0.02:
            return (X, Y, math.copysign(self.c * math.sqrt(r2), Z) if Z else 0)
        k = folga / math.sqrt(q)
        return (X * k, Y * k, Z * k)

    def corda(self, v, p):
        """Interseção da reta que passa por v e p com o elipsoide: (t0, t1) na forma v + t·(p − v)."""
        d = [p[i] - v[i] for i in range(3)]
        r = (self.a, self.b, self.c)
        A = sum((d[i] / r[i]) ** 2 for i in range(3))
        B = 2 * sum(v[i] * d[i] / r[i] ** 2 for i in range(3))
        C = sum((v[i] / r[i]) ** 2 for i in range(3)) - 1
        disc = B * B - 4 * A * C
        if A == 0 or disc <= 0:
            return None, d
        s = math.sqrt(disc)
        return ((-B - s) / (2 * A), (-B + s) / (2 * A)), d

    def projeta(self, p):
        """Perspectiva sem giro (estado inicial, igual ao primeiro quadro de mapa.js)."""
        k = FOCO / (FOCO - p[2])
        return (self.cx + p[0] * k, self.cy + p[1] * k)


def svg(c, by_id, esc, ano_fn, ano_en, vertical=False):
    """SVG do mapa. vertical=True gira a composição para o celular."""
    w, h = (H, W) if vertical else (W, H)
    S = Cena(w, h, vertical)

    # obras no espaço
    pos3 = {}
    for k, nd in NOS.items():
        x, y = (PV[k][:2] if vertical and k in PV else S.T(*nd["p"]))
        pos3[k] = S.dentro(S.ponto(x, y, nd["z"] * 0.5))   # profundidade moderada: de frente, todos os nomes legíveis
    vps = {k: S.ponto(*S.T(v[0], v[1]), v[2]) for k, v in VP.items()}

    fundo, meio, halos, frente = [], [], [], []

    def emite(p1, p2, wd, ns):
        a, b = S.projeta(p1), S.projeta(p2)
        dados = ",".join(f"{v:.1f}" for v in (*p1, *p2))
        attrs = f'x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" data-n="{" ".join(ns)}" data-p="{dados}"'
        if wd >= FRENTE:
            halos.append(f'<line class="m-halo" {attrs} stroke-width="{wd + 7:.1f}"/>')
            frente.append(f'<line {attrs} stroke-width="{wd}"/>')
        elif wd <= 1:
            fundo.append(f'<line {attrs} stroke-width="{wd}"/>')
        else:
            meio.append(f'<line {attrs} stroke-width="{wd}"/>')

    # cordas dos sistemas
    for sv, itens in SISTEMAS.items():
        for anc, wd, fr in itens:
            if isinstance(anc, str):
                p, ns = pos3[anc], [anc]
            else:
                p, ns = S.dentro(S.ponto(*S.T(anc[0], anc[1]), anc[2]), 1.2), []
            if sv == "E":
                v, ns = pos3["esquina"], ["esquina"] + ns
            else:
                v = vps[sv]
            ts, d = S.corda(v, p)
            if not ts:
                continue
            t0, t1 = ts
            if sv == "E":
                t0 = max(t0, -PASSA)
            ta, tb = t0 + (t1 - t0) * fr[0], t0 + (t1 - t0) * fr[1]
            emite(tuple(v[i] + d[i] * ta for i in range(3)), tuple(v[i] + d[i] * tb for i in range(3)), wd, ns)

    # planos: arestas entre obras, passando do vértice
    for pl in PLANOS:
        nn = pl["nos"]
        for i in range(len(nn)):
            A, B = pos3[nn[i]], pos3[nn[(i + 1) % len(nn)]]
            d = [B[j] - A[j] for j in range(3)]
            L = math.sqrt(sum(x * x for x in d)) or 1
            u = [x / L for x in d]
            e1, e2 = 8 + _h(nn[i], i) % 14, 8 + _h(i, nn[i]) % 14
            p1 = tuple(A[j] - u[j] * e1 for j in range(3))
            p2 = tuple(B[j] + u[j] * e2 for j in range(3))
            emite(p1, p2, pl["larg"], [nn[i], nn[(i + 1) % len(nn)]])
            if pl.get("dupla"):          # segundo traço, levemente desencontrado
                o1, o2 = 2 + _h(nn[i], "a") % 3, 4 + _h(nn[i], "b") % 4
                emite((p1[0], p1[1] + o1, p1[2]), (p2[0] + 2, p2[1] + o2, p2[2]), 0.6, [nn[i], nn[(i + 1) % len(nn)]])

    # vértice da Esquina e ponta fina
    e = pos3[VERTICE["no"]]
    for alvo, wd in VERTICE["alvos"]:
        q = pos3[alvo]
        d = [q[j] - e[j] for j in range(3)]
        emite(tuple(e[j] - d[j] * 0.05 for j in range(3)), tuple(q[j] + d[j] * 0.04 for j in range(3)), wd, ["esquina", alvo])
    ap = S.dentro(S.ponto(*S.T(PONTA["apice"][0], PONTA["apice"][1]), PONTA["apice"][2]), 1.0)
    for alvo, wd in PONTA["de"]:
        q = pos3[alvo]
        d = [ap[j] - q[j] for j in range(3)]
        emite(tuple(q[j] - d[j] * 0.04 for j in range(3)), ap, wd, [alvo])

    # círculo de compasso: um meridiano da esfera, que gira com ela
    pts = []
    for i in range(73):
        ang = 2 * math.pi * i / 72
        pts.append((0.0, S.b * 0.96 * math.cos(ang), S.c * 0.96 * math.sin(ang)))
    circulo = (f'<polyline class="m-circulo" points="{" ".join(f"{S.projeta(q)[0]:.1f},{S.projeta(q)[1]:.1f}" for q in pts)}" '
               f'data-p="{" ".join(f"{q[0]:.0f},{q[1]:.0f},{q[2]:.0f}" for q in pts)}"/>')

    # obras: só nome e ano
    nos = []
    for k, nd in NOS.items():
        o = by_id[k]
        X, Y, Z = pos3[k]
        x, y = S.projeta(pos3[k])
        t = nd["t"]
        esq = nd["lado"] == "e"
        if vertical:
            esq = PV[k][2] == "e" if k in PV else x > w * 0.6
        dx = -14 if esq else 14
        anchor = "end" if esq else "start"
        r = {3: 9.5, 2: 6.5, 1: 4.5}[t]
        premiada = bool(o.get("premio"))
        circ = f'<circle class="m-pt{"" if t >= 2 else " m-vazado"}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
        if premiada:
            circ = f'<circle class="m-selo" cx="{x:.1f}" cy="{y:.1f}" r="{r + 4.5}"/>' + circ
        ny = y - 6 if t == 3 else y - 4
        rot_ano = o.get("ano_mapa") or o["ano"].split(" /")[-1].strip()
        if c.lang == "en":
            rot_ano = ano_en.get(rot_ano, rot_ano)
        txt = (f'<text class="m-nome" x="{x + dx:.1f}" y="{ny:.1f}" text-anchor="{anchor}">{esc(o["titulo"])}</text>'
               f'<text class="m-ano" x="{x + dx:.1f}" y="{ny + (16 if t == 3 else 13):.1f}" text-anchor="{anchor}">{esc(rot_ano)}</text>')
        nos.append(
            f'<a class="m-no t{t}{" premiada" if premiada else ""}" href="obras/{k}.html" data-id="{k}" data-ano="{o["ano_num"]}" '
            f'data-x="{x:.1f}" data-y="{y:.1f}" data-p="{X:.1f},{Y:.1f},{Z:.1f}" data-lado="{"e" if esq else "d"}" '
            f'aria-label="{esc(o["titulo"])}, {esc(ano_fn(o, c.lang))}">'
            f'<circle class="m-alvo" cx="{x:.1f}" cy="{y:.1f}" r="22"/>{circ}{txt}</a>')

    return (f'<svg class="mapa {"mapa-v" if vertical else "mapa-h"}" viewBox="0 0 {w} {h}" role="group" '
            f'aria-label="{c.t["mapa_aria"]}" data-w="{w}" data-h="{h}" data-foco="{FOCO}" data-raio="{S.c:.0f}">'
            f'<g class="m-linhas" aria-hidden="true">{circulo}<g class="m-fundo">{"".join(fundo)}</g><g class="m-meio">{"".join(meio)}</g>'
            f'<g class="m-halos">{"".join(halos)}</g><g class="m-frente">{"".join(frente)}</g></g>'
            f'<g class="m-nos">{"".join(nos)}</g></svg>')
