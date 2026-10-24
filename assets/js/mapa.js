/* Mapa Esquina — o desenho Esquina VI girando no espaço.
   Cada linha está numa profundidade própria, como camadas de fita; o conjunto gira em torno do eixo vertical:
   com o cursor, de uma borda à outra do quadro, uma volta inteira; sem cursor, gira devagar sozinho.
   De frente, o desenho é exatamente o da tela (projeção sem perspectiva).
   O que está atrás fica mais claro; o que está na frente, mais escuro. Sobre uma obra, tudo para.
   Ao passar sobre um cruzamento, as linhas que o atravessam ficam em evidência e um som escapa. */
document.addEventListener("DOMContentLoaded", function () {
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".mapa").forEach(function (svg) {
    var linhas = Array.prototype.slice.call(svg.querySelectorAll(".m-linhas line"));
    var W = parseFloat(svg.getAttribute("data-w")), H = parseFloat(svg.getAttribute("data-h"));
    var FOCO = parseFloat(svg.getAttribute("data-foco")) || 0;   /* 0 = sem perspectiva */
    var RAIO = parseFloat(svg.getAttribute("data-raio")) || 400;
    var cx = W / 2, cy = H / 2;

    var segs = linhas.map(function (l) {
      return { el: l, p: l.getAttribute("data-p").split(",").map(parseFloat), halo: l.classList.contains("m-halo") };
    });
    var circ = svg.querySelector(".m-circulo");
    var circPts = circ ? circ.getAttribute("data-p").split(" ").map(function (t) { return t.split(",").map(parseFloat); }) : [];
    var obras = [];
    svg.querySelectorAll(".m-no").forEach(function (no) {
      obras.push({
        el: no, x0: parseFloat(no.getAttribute("data-x")), y0: parseFloat(no.getAttribute("data-y")),
        p: no.getAttribute("data-p").split(",").map(parseFloat),
        textos: Array.prototype.slice.call(no.querySelectorAll("text")),
        lado: no.getAttribute("data-lado")
      });
    });

    /* giro: theta em torno do eixo vertical, phi inclina para cima e para baixo */
    var ct = 1, st = 0, cp = 1, sp = 0;
    function gira(X, Y, Z) {
      var X1 = X * ct + Z * st, Z1 = -X * st + Z * ct;
      var Y2 = Y * cp - Z1 * sp, Z2 = Y * sp + Z1 * cp;
      var k = FOCO ? FOCO / (FOCO - Z2) : 1;
      return [cx + X1 * k, cy + Y2 * k, Z2];
    }
    /* quanto um ponto foi para trás com o giro (0 = de frente, como na tela; 1 = bem atrás) */
    function atras(X, Z) { return Math.max(0, Math.min(1, (X * st + Z * (1 - ct)) / RAIO)); }

    function desenha(theta, phi) {
      ct = Math.cos(theta); st = Math.sin(theta); cp = Math.cos(phi); sp = Math.sin(phi);
      segs.forEach(function (s) {
        var a = gira(s.p[0], s.p[1], s.p[2]), b = gira(s.p[3], s.p[4], s.p[5]);
        s.el.setAttribute("x1", a[0].toFixed(1)); s.el.setAttribute("y1", a[1].toFixed(1));
        s.el.setAttribute("x2", b[0].toFixed(1)); s.el.setAttribute("y2", b[1].toFixed(1));
        var t = atras((s.p[0] + s.p[3]) / 2, (s.p[2] + s.p[5]) / 2);
        s.el.setAttribute("stroke-opacity", (1 - 0.45 * t).toFixed(2));
      });
      if (circ) {
        circ.setAttribute("points", circPts.map(function (c) { var q = gira(c[0], c[1], c[2]); return q[0].toFixed(1) + "," + q[1].toFixed(1); }).join(" "));
      }
      obras.forEach(function (o) {
        var q = gira(o.p[0], o.p[1], o.p[2]);
        o.el.setAttribute("transform", "translate(" + (q[0] - o.x0).toFixed(1) + " " + (q[1] - o.y0).toFixed(1) + ")");
        var t = atras(o.p[0], o.p[2]);
        o.el.style.opacity = (1 - 0.5 * t).toFixed(2);
        /* nomes das obras que passam para trás quase se apagam, para não se misturar aos da frente */
        var ft = Math.max(0.06, Math.min(1, 1 - (t - 0.25) / 0.2)).toFixed(2);
        o.textos.forEach(function (tx) { tx.style.opacity = ft; });
        /* de frente o rótulo fica do lado escolhido; girado, troca de lado perto da borda */
        var lado = o.lado0 || (o.lado0 = o.lado);
        if (Math.abs(q[0] - o.x0) > 40) { if (q[0] > W * 0.66) lado = "e"; else if (q[0] < W * 0.34) lado = "d"; }
        if (lado !== o.lado) {
          o.lado = lado;
          o.textos.forEach(function (t) {
            t.setAttribute("x", (o.x0 + (lado === "e" ? -14 : 14)).toFixed(1));
            t.setAttribute("text-anchor", lado === "e" ? "end" : "start");
          });
        }
      });
    }

    /* foco num cruzamento */
    var parado = false;
    function focar(id) {
      parado = true;
      svg.classList.add("foco");
      linhas.forEach(function (l) {
        l.classList.toggle("on", (" " + l.getAttribute("data-n") + " ").indexOf(" " + id + " ") > -1);
      });
    }
    function soltar() {
      parado = false;
      svg.classList.remove("foco");
      linhas.forEach(function (l) { l.classList.remove("on"); });
    }
    svg.querySelectorAll(".m-no").forEach(function (no) {
      var id = no.getAttribute("data-id");
      var ano = parseInt(no.getAttribute("data-ano"), 10) || 2010;
      var freq = 260 + (ano - 2000) * 85;   /* obras mais recentes soam mais agudas */
      function entrar() { focar(id); if (window.FRSom) window.FRSom.escapar(freq); }
      no.addEventListener("mouseenter", entrar);
      no.addEventListener("focus", entrar);
      no.addEventListener("mouseleave", soltar);
      no.addEventListener("blur", soltar);
    });

    if (reduz) return;

    /* cursor: de uma borda à outra, 360 graus; sem cursor, uma volta inteira a cada 90 s */
    var ARCO = 2 * Math.PI, VOLTA = 2 * Math.PI / 90;
    var theta = 0, phi = 0, alvoT = 0, alvoP = 0, base = 0;
    var comCursor = false, ultimoCursor = -1e9, visivel = true, antes = performance.now();
    var area = svg.closest(".inicio") || svg;
    area.addEventListener("pointermove", function (ev) {
      if (ev.pointerType && ev.pointerType !== "mouse") return;
      var r = svg.getBoundingClientRect();
      if (!r.width) return;
      var ox = Math.max(-1, Math.min(1, ((ev.clientX - r.left) / r.width - 0.5) * 2));
      var oy = Math.max(-1, Math.min(1, ((ev.clientY - r.top) / r.height - 0.5) * 2));
      if (!comCursor) { base = theta - ox * ARCO / 2; comCursor = true; }
      alvoT = base + ox * ARCO / 2;
      alvoP = -oy * 0.22;
      ultimoCursor = performance.now();
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { visivel = es[0].isIntersecting; }).observe(svg);
    }

    function quadro(t) {
      requestAnimationFrame(quadro);
      var dt = Math.min(0.05, (t - antes) / 1000); antes = t;
      if (!visivel || document.hidden || !svg.getBoundingClientRect().width || parado) return;
      if (t - ultimoCursor > 2500) {
        comCursor = false;
        alvoT = theta + VOLTA * dt * 20;          /* segue girando devagar */
        alvoP = 0.08 * Math.sin(t / 9000);
      }
      theta += (alvoT - theta) * (comCursor ? 0.08 : 0.05);
      phi += (alvoP - phi) * 0.06;
      desenha(theta, phi);
    }
    requestAnimationFrame(quadro);
  });
});
