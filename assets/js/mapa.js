/* Mapa Esquina.
   Cada obra é o cruzamento de linhas que vêm de pontos de vista diferentes.
   Ao mover o cursor, os pontos de fuga se deslocam e as linhas giram em torno das obras:
   as obras ficam onde estão, o ponto de vista muda. Sem cursor, o ponto de vista deriva devagar.
   Ao passar sobre um cruzamento, as linhas que o atravessam ficam em evidência e um som escapa. */
document.addEventListener("DOMContentLoaded", function () {
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".mapa").forEach(function (svg) {
    var linhas = Array.prototype.slice.call(svg.querySelectorAll(".m-linhas line"));
    var W = parseFloat(svg.getAttribute("data-w")), H = parseFloat(svg.getAttribute("data-h"));
    var VP0 = JSON.parse(svg.getAttribute("data-vp") || "{}");
    var MOVE = JSON.parse(svg.getAttribute("data-move") || "{}");
    var cx = W / 2, cy = H / 2;

    /* linhas que giram: âncora, sistema, frações */
    var moveis = linhas.filter(function (l) { return l.hasAttribute("data-v"); }).map(function (l) {
      var a = l.getAttribute("data-a").split(",").map(parseFloat);
      var s = l.getAttribute("data-s").split(",").map(parseFloat);
      return { el: l, v: l.getAttribute("data-v"), a: a, s: s, raio: l.hasAttribute("data-r") };
    });

    function recorte(px, py, dx, dy) {
      var t0 = -1e9, t1 = 1e9, lim = [[px, dx, W], [py, dy, H]];
      for (var i = 0; i < 2; i++) {
        var p = lim[i][0], d = lim[i][1], hi = lim[i][2];
        if (Math.abs(d) < 1e-9) { if (p < 0 || p > hi) return null; continue; }
        var a = (0 - p) / d, b = (hi - p) / d;
        if (a > b) { var tmp = a; a = b; b = tmp; }
        if (a > t0) t0 = a;
        if (b < t1) t1 = b;
      }
      return t0 < t1 ? [t0, t1] : null;
    }

    function desenha(ox, oy) {
      var vp = {};
      Object.keys(VP0).forEach(function (k) {
        var v = VP0[k], m = MOVE[k] || 0;
        var dist = Math.min(Math.hypot(v[0] - cx, v[1] - cy), 2600);
        vp[k] = [v[0] + ox * m * 0.13 * dist, v[1] + oy * m * 0.09 * dist];
      });
      moveis.forEach(function (m) {
        var v = vp[m.v]; if (!v) return;
        var dx = m.a[0] - v[0], dy = m.a[1] - v[1];
        var r = recorte(v[0], v[1], dx, dy);
        if (!r) { m.el.style.visibility = "hidden"; return; }
        var t0 = r[0], t1 = r[1];
        if (m.raio) t0 = Math.max(t0, -0.035);
        if (t1 <= t0) { m.el.style.visibility = "hidden"; return; }
        m.el.style.visibility = "";
        var ta = t0 + (t1 - t0) * m.s[0], tb = t0 + (t1 - t0) * m.s[1];
        m.el.setAttribute("x1", (v[0] + dx * ta).toFixed(1));
        m.el.setAttribute("y1", (v[1] + dy * ta).toFixed(1));
        m.el.setAttribute("x2", (v[0] + dx * tb).toFixed(1));
        m.el.setAttribute("y2", (v[1] + dy * tb).toFixed(1));
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

    /* deslocamento do ponto de vista */
    var alvo = [0, 0], atual = [0, 0], ultimoCursor = 0, visivel = true, inicio = performance.now();
    var area = svg.closest(".inicio") || svg;
    area.addEventListener("pointermove", function (ev) {
      if (ev.pointerType && ev.pointerType !== "mouse") return;
      var r = svg.getBoundingClientRect();
      if (!r.width) return;
      alvo[0] = Math.max(-1, Math.min(1, ((ev.clientX - r.left) / r.width - 0.5) * 2));
      alvo[1] = Math.max(-1, Math.min(1, ((ev.clientY - r.top) / r.height - 0.5) * 2));
      ultimoCursor = performance.now();
    });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { visivel = es[0].isIntersecting; }).observe(svg);
    }

    function quadro(t) {
      requestAnimationFrame(quadro);
      if (!visivel || document.hidden || !svg.getBoundingClientRect().width) return;
      if (t - ultimoCursor > 2500) {               /* sem cursor: deriva lenta */
        var u = (t - inicio) / 1000;
        alvo[0] = 0.42 * Math.sin(u * 0.11);
        alvo[1] = 0.32 * Math.sin(u * 0.07 + 1.3);
      }
      if (parado) return;                          /* sobre uma obra, o desenho fica quieto */
      var k = t - ultimoCursor > 2500 ? 0.02 : 0.07;
      var nx = atual[0] + (alvo[0] - atual[0]) * k, ny = atual[1] + (alvo[1] - atual[1]) * k;
      if (Math.abs(nx - atual[0]) + Math.abs(ny - atual[1]) < 0.0004) return;
      atual = [nx, ny];
      desenha(atual[0], atual[1]);
    }
    requestAnimationFrame(quadro);
  });
});
