/* Mapa Esquina.
   Cada obra é o cruzamento de linhas que vêm de pontos de vista diferentes.
   O mapa gira no espaço: cada obra tem uma profundidade, e ao mover o cursor o plano gira —
   as obras da frente se deslocam mais que as do fundo, os planos se deformam, e ao mesmo tempo
   os pontos de fuga se deslocam, fazendo as linhas girarem em torno das obras.
   Sem cursor, o desenho gira devagar sozinho. Sobre uma obra, tudo para.
   Ao passar sobre um cruzamento, as linhas que o atravessam ficam em evidência e um som escapa. */
document.addEventListener("DOMContentLoaded", function () {
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".mapa").forEach(function (svg) {
    var linhas = Array.prototype.slice.call(svg.querySelectorAll(".m-linhas line"));
    var W = parseFloat(svg.getAttribute("data-w")), H = parseFloat(svg.getAttribute("data-h"));
    var VP0 = JSON.parse(svg.getAttribute("data-vp") || "{}");
    var MOVE = JSON.parse(svg.getAttribute("data-move") || "{}");
    var cx = W / 2, cy = H / 2, FOCO = 1700;
    var AMP = H > W ? 0.6 : 1;   /* no celular (composição vertical) o giro é mais contido */

    /* obras: posição e profundidade */
    var obras = {};
    svg.querySelectorAll(".m-no").forEach(function (no) {
      obras[no.getAttribute("data-id")] = {
        el: no, x: parseFloat(no.getAttribute("data-x")), y: parseFloat(no.getAttribute("data-y")),
        z: parseFloat(no.getAttribute("data-z")) || 0, px: 0, py: 0
      };
    });

    /* linhas de ponto de fuga: âncora (obra ou ponto livre), sistema, frações */
    var raios = [], planos = [];
    linhas.forEach(function (l) {
      if (l.hasAttribute("data-v")) {
        raios.push({
          el: l, v: l.getAttribute("data-v"), no: l.getAttribute("data-no"),
          a: l.getAttribute("data-a").split(",").map(parseFloat),
          s: l.getAttribute("data-s").split(",").map(parseFloat), raio: l.hasAttribute("data-r")
        });
      } else if (l.hasAttribute("data-e")) {
        var ns = l.getAttribute("data-plano").split(" ");
        planos.push({ el: l, a: ns[0], b: ns[1], e: l.getAttribute("data-e").split(",").map(parseFloat) });
      }
    });

    /* giro do plano em três eixos, com perspectiva */
    var R = { cz: 1, sz: 0, cy: 1, sy: 0, cx: 1, sx: 0 };
    function giro(ox, oy) {
      var rz = ox * 0.06 * AMP, ry = ox * 0.17 * AMP, rx = -oy * 0.10 * AMP;
      R = { cz: Math.cos(rz), sz: Math.sin(rz), cy: Math.cos(ry), sy: Math.sin(ry), cx: Math.cos(rx), sx: Math.sin(rx) };
    }
    function projeta(x, y, z) {
      var X = x - cx, Y = y - cy;
      var X1 = X * R.cz - Y * R.sz, Y1 = X * R.sz + Y * R.cz;
      var X2 = X1 * R.cy + z * R.sy, Z2 = -X1 * R.sy + z * R.cy;
      var Y2 = Y1 * R.cx - Z2 * R.sx, Z3 = Y1 * R.sx + Z2 * R.cx;
      var k = FOCO / (FOCO - Z3);
      return [cx + X2 * k, cy + Y2 * k];
    }

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
    function poe(el, x1, y1, x2, y2) {
      el.setAttribute("x1", x1.toFixed(1)); el.setAttribute("y1", y1.toFixed(1));
      el.setAttribute("x2", x2.toFixed(1)); el.setAttribute("y2", y2.toFixed(1));
    }

    function desenha(ox, oy) {
      giro(ox, oy);
      /* obras */
      Object.keys(obras).forEach(function (id) {
        var o = obras[id], p = projeta(o.x, o.y, o.z);
        o.px = p[0]; o.py = p[1];
        o.el.setAttribute("transform", "translate(" + (p[0] - o.x).toFixed(1) + " " + (p[1] - o.y).toFixed(1) + ")");
      });
      /* pontos de fuga */
      var vp = {};
      Object.keys(VP0).forEach(function (k) {
        var v = VP0[k], m = MOVE[k] || 0;
        var dist = Math.min(Math.hypot(v[0] - cx, v[1] - cy), 2600);
        vp[k] = [v[0] + ox * m * 0.13 * dist, v[1] + oy * m * 0.09 * dist];
      });
      if (obras.esquina) vp.E = [obras.esquina.px, obras.esquina.py];
      /* linhas que passam pelas obras ou por pontos livres (que também giram) */
      raios.forEach(function (m) {
        var v = vp[m.v]; if (!v) return;
        var a = m.no && obras[m.no] ? [obras[m.no].px, obras[m.no].py] : projeta(m.a[0], m.a[1], 0);
        var dx = a[0] - v[0], dy = a[1] - v[1];
        var r = recorte(v[0], v[1], dx, dy);
        if (!r) { m.el.style.visibility = "hidden"; return; }
        var t0 = r[0], t1 = r[1];
        if (m.raio) t0 = Math.max(t0, -0.035);
        if (t1 <= t0) { m.el.style.visibility = "hidden"; return; }
        m.el.style.visibility = "";
        var ta = t0 + (t1 - t0) * m.s[0], tb = t0 + (t1 - t0) * m.s[1];
        poe(m.el, v[0] + dx * ta, v[1] + dy * ta, v[0] + dx * tb, v[1] + dy * tb);
      });
      /* planos: arestas entre obras, passando um pouco do vértice */
      planos.forEach(function (pl) {
        var A = obras[pl.a], B = obras[pl.b]; if (!A || !B) return;
        var dx = B.px - A.px, dy = B.py - A.py, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
        poe(pl.el, A.px - ux * pl.e[0], A.py - uy * pl.e[0], B.px + ux * pl.e[1], B.py + uy * pl.e[1]);
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

    /* giro conduzido pelo cursor; sem cursor, giro lento */
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
      if (!visivel || document.hidden || !svg.getBoundingClientRect().width) return;
      var livre = t - ultimoCursor > 2500;
      if (livre) {
        var u = (t - inicio) / 1000;
        alvo[0] = 0.55 * Math.sin(u * 0.12);
        alvo[1] = 0.40 * Math.sin(u * 0.08 + 1.3);
      }
      if (parado) return;
      var k = livre ? 0.03 : 0.07;
      var nx = atual[0] + (alvo[0] - atual[0]) * k, ny = atual[1] + (alvo[1] - atual[1]) * k;
      if (Math.abs(nx - atual[0]) + Math.abs(ny - atual[1]) < 0.0003) return;
      atual = [nx, ny];
      desenha(atual[0], atual[1]);
    }
    requestAnimationFrame(quadro);
  });
});
