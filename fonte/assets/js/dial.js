/* Dial: cada obra de rádio é uma estação; entre elas, ruído. */
document.addEventListener("DOMContentLoaded", function () {
  var dial = document.querySelector("[data-dial]");
  if (!dial) return;
  var faixa = dial.querySelector("[data-faixa]");
  var ruido = dial.querySelector("[data-ruido]");
  var leitura = document.querySelector("[data-freq]");
  var caixa = document.querySelector("[data-estacao]");
  var EST = window.ESTACOES || [];
  var MIN = 2000, MAX = 2027, PX = 110; /* pixels por ano */
  var CAPTURA = 0.32; /* distância (em anos) em que a estação é sintonizada */

  // faixa graduada
  faixa.style.width = (MAX - MIN) * PX + "px";
  for (var q = MIN * 4; q <= MAX * 4; q++) {
    var ano = q / 4, x = (ano - MIN) * PX;
    var t = document.createElement("span");
    t.className = "tick" + (q % 4 === 0 ? (ano % 5 === 0 ? " cinco" : " ano") : "");
    t.style.left = x + "px";
    faixa.appendChild(t);
    if (q % 4 === 0 && ano % 5 === 0) {
      var r = document.createElement("span"); r.className = "rot"; r.style.left = x + "px"; r.textContent = ano;
      faixa.appendChild(r);
    }
  }
  var pontos = EST.map(function (s) {
    var p = document.createElement("span"); p.className = "est"; p.style.left = (s.freq - MIN) * PX + "px";
    faixa.appendChild(p); return p;
  });

  var freq = EST.length ? EST[EST.length - 1].freq : 2016; /* abre na estação mais recente */
  var atual = null;
  var som = null;

  function maisProxima() {
    var m = null, d = 99;
    EST.forEach(function (s, i) { var dd = Math.abs(s.freq - freq); if (dd < d) { d = dd; m = i; } });
    return { i: m, d: d };
  }

  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

  function render() {
    var meio = dial.clientWidth / 2;
    faixa.style.transform = "translateX(" + (meio - (freq - MIN) * PX) + "px)";
    leitura.textContent = freq.toFixed(1);
    dial.setAttribute("aria-valuenow", freq.toFixed(1));
    var p = maisProxima();
    pontos.forEach(function (el, i) { el.classList.toggle("perto", i === p.i && p.d < CAPTURA); });
    var dentro = p.d < CAPTURA ? p.i : null;
    if (dentro !== atual) {
      atual = dentro;
      if (atual === null) {
        caixa.innerHTML = '<p class="entre">entre estações</p>';
        dial.setAttribute("aria-valuetext", freq.toFixed(1) + ", entre estações");
      } else {
        var s = EST[atual];
        var sc = s.soundcloud && window.PREVIA ? '<p><a class="dado" href="' + esc(s.soundcloud) + '" target="_blank" rel="noopener">ouvir no SoundCloud ↗</a></p>' :
          s.soundcloud ? '<iframe title="Áudio de ' + esc(s.titulo) + '" loading="lazy" src="https://w.soundcloud.com/player/?url=' +
          encodeURIComponent(s.soundcloud) + '&color=%23e2493a&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&visual=false"></iframe>' : "";
        caixa.innerHTML = '<p class="dado">' + esc(s.ano) + '</p><h2><a href="obras/' + s.id + '.html">' + esc(s.titulo) + "</a></h2>" +
          (s.texto ? "<p>" + esc(s.texto) + "</p>" : "") + sc;
        dial.setAttribute("aria-valuetext", s.titulo + ", " + s.ano);
      }
    }
    if (som) {
      var perto = Math.min(1, p.d / 0.9);
      som.volume(0.16 * perto);
      som.tom(1800 + 3400 * perto);
    }
  }

  function mover(nf) { freq = Math.max(MIN, Math.min(MAX, nf)); render(); }

  // arrastar
  var arrastando = false, x0 = 0, f0 = 0;
  dial.addEventListener("pointerdown", function (e) {
    arrastando = true; x0 = e.clientX; f0 = freq; dial.setPointerCapture(e.pointerId);
    if (window.FRSom && window.FRSom.ligado() && !som) som = window.FRSom.chiado();
  });
  dial.addEventListener("pointermove", function (e) { if (arrastando) mover(f0 - (e.clientX - x0) / PX); });
  function soltar() {
    if (!arrastando) return; arrastando = false;
    var p = maisProxima(); if (p.d < CAPTURA * 1.6) mover(EST[p.i].freq); /* encaixa na estação */
  }
  dial.addEventListener("pointerup", soltar);
  dial.addEventListener("pointercancel", soltar);
  dial.addEventListener("wheel", function (e) {
    if (Math.abs(e.deltaX) > Math.abs(e.deltaY) || e.shiftKey) { e.preventDefault(); mover(freq + (e.deltaX || e.deltaY) / PX); }
  }, { passive: false });
  dial.addEventListener("keydown", function (e) {
    var passo = e.shiftKey ? 1 : 0.1;
    if (e.key === "ArrowRight" || e.key === "ArrowUp") { e.preventDefault(); mover(freq + passo); }
    if (e.key === "ArrowLeft" || e.key === "ArrowDown") { e.preventDefault(); mover(freq - passo); }
    if (e.key === "PageUp" || e.key === "PageDown") {
      e.preventDefault();
      var lista = EST.map(function (s) { return s.freq; });
      var alvo = e.key === "PageUp" ? lista.filter(function (f) { return f > freq + 0.01; })[0]
                                     : lista.filter(function (f) { return f < freq - 0.01; }).pop();
      if (alvo !== undefined) mover(alvo);
    }
  });
  if (window.FRSom) window.FRSom.aoMudar(function (v) {
    if (v && !som) som = window.FRSom.chiado();
    render();
  });
  window.addEventListener("resize", render);

  // granulação do ruído, mais densa longe das estações
  var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function grao() {
    var dpr = window.devicePixelRatio || 1, w = ruido.clientWidth, h = ruido.clientHeight;
    if (ruido.width !== w * dpr) { ruido.width = w * dpr; ruido.height = h * dpr; }
    var g = ruido.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    var meio = w / 2;
    for (var n = 0; n < 2600; n++) {
      var x = Math.random() * w;
      var fx = freq + (x - meio) / PX;
      var d = 99; for (var i = 0; i < EST.length; i++) d = Math.min(d, Math.abs(EST[i].freq - fx));
      if (Math.random() > Math.min(1, d / 0.8) * 0.95 + 0.03) continue;
      var y = h / 2 + (Math.random() + Math.random() + Math.random() - 1.5) * h * 0.42;
      g.fillStyle = "rgba(236,233,226," + (0.12 + Math.random() * 0.35).toFixed(2) + ")";
      g.fillRect(x, y, 1, 2 + Math.random() * 4);
    }
    if (!reduzido) setTimeout(function () { requestAnimationFrame(grao); }, 90);
  }
  render();
  grao();
});
