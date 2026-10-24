/* Mapa Esquina — sobre o desenho Esquina VI.
   Movimento leve e bidimensional: o plano do desenho se inclina um pouco em perspectiva conforme o cursor
   (transformação projetiva: as linhas continuam retas e os vértices unidos, as obras ficam nos cruzamentos).
   Sem cursor, deriva devagar. Sobre uma obra, tudo para.
   Ao passar sobre um cruzamento, as linhas que o atravessam ficam em evidência e um som escapa. */
document.addEventListener("DOMContentLoaded", function () {
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".mapa").forEach(function (svg) {
    var linhas = Array.prototype.slice.call(svg.querySelectorAll(".m-linhas line"));
    var W = parseFloat(svg.getAttribute("data-w")), H = parseFloat(svg.getAttribute("data-h"));
    var cx = W / 2, cy = H / 2, L = Math.max(W, H);

    /* data-p traz as pontas da linha centradas no quadro (x, y, profundidade); aqui só x e y importam */
    var segs = linhas.map(function (l) {
      var v = l.getAttribute("data-p").split(",").map(parseFloat);
      var p = v.length === 6 ? [v[0] + cx, v[1] + cy, v[3] + cx, v[4] + cy] : v;
      return { el: l, p: p };
    });
    var obras = [];
    svg.querySelectorAll(".m-no").forEach(function (no) {
      obras.push({ el: no, x: parseFloat(no.getAttribute("data-x")), y: parseFloat(no.getAttribute("data-y")) });
    });

    /* inclinação: A e B deformam em perspectiva, r gira um pouco o plano */
    var A = 0, B = 0, cr = 1, sr = 0;
    function leva(x, y) {
      var X = x - cx, Y = y - cy;
      var w = 1 + A * X + B * Y;
      X /= w; Y /= w;
      return [cx + X * cr - Y * sr, cy + X * sr + Y * cr];
    }
    function desenha(ox, oy) {
      A = ox * 0.16 / L; B = oy * 0.12 / L;
      var r = ox * 0.025; cr = Math.cos(r); sr = Math.sin(r);
      segs.forEach(function (s) {
        var a = leva(s.p[0], s.p[1]), b = leva(s.p[2], s.p[3]);
        s.el.setAttribute("x1", a[0].toFixed(1)); s.el.setAttribute("y1", a[1].toFixed(1));
        s.el.setAttribute("x2", b[0].toFixed(1)); s.el.setAttribute("y2", b[1].toFixed(1));
      });
      obras.forEach(function (o) {
        var q = leva(o.x, o.y);
        o.el.setAttribute("transform", "translate(" + (q[0] - o.x).toFixed(1) + " " + (q[1] - o.y).toFixed(1) + ")");
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

    var alvo = [0, 0], atual = [0, 0], ultimoCursor = -1e9, visivel = true, inicio = performance.now();
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
      if (!visivel || document.hidden || !svg.getBoundingClientRect().width || parado) return;
      var livre = t - ultimoCursor > 2500;
      if (livre) {                                  /* deriva lenta */
        var u = (t - inicio) / 1000;
        alvo[0] = 0.5 * Math.sin(u * 0.11);
        alvo[1] = 0.4 * Math.sin(u * 0.07 + 1.3);
      }
      var k = livre ? 0.03 : 0.07;
      var nx = atual[0] + (alvo[0] - atual[0]) * k, ny = atual[1] + (alvo[1] - atual[1]) * k;
      if (Math.abs(nx - atual[0]) + Math.abs(ny - atual[1]) < 0.0003) return;
      atual = [nx, ny];
      desenha(atual[0], atual[1]);
    }
    requestAnimationFrame(quadro);
  });
});
