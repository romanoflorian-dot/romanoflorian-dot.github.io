/* Som do site: nunca toca sem ação do visitante. */
(function () {
  var ctx = null;
  var ligado = false;
  var ouvintes = [];

  function guardar(v) { try { localStorage.setItem("fr-som", v ? "1" : "0"); } catch (e) {} }
  function lido() { try { return localStorage.getItem("fr-som") === "1"; } catch (e) { return false; } }

  function contexto() {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
    }
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }

  function ruidoBuffer(c, seg) {
    var n = Math.floor(c.sampleRate * seg);
    var b = c.createBuffer(1, n, c.sampleRate);
    var d = b.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    return b;
  }

  /* Um som curto que "escapa" de um cruzamento: ruído filtrado numa faixa própria. */
  function escapar(freq) {
    if (!ligado) return;
    var c = contexto(); if (!c) return;
    var t = c.currentTime;
    var src = c.createBufferSource(); src.buffer = ruidoBuffer(c, 0.9);
    var bp = c.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = freq; bp.Q.value = 9;
    var g = c.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.5, t + 0.04);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.85);
    src.connect(bp); bp.connect(g); g.connect(c.destination);
    src.start(t); src.stop(t + 0.9);
  }

  /* Ruído contínuo de rádio, com volume controlável (para o dial). */
  function chiado() {
    var c = contexto(); if (!c) return null;
    var src = c.createBufferSource(); src.buffer = ruidoBuffer(c, 2); src.loop = true;
    var hp = c.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 500;
    var lp = c.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 5200;
    var g = c.createGain(); g.gain.value = 0;
    src.connect(hp); hp.connect(lp); lp.connect(g); g.connect(c.destination);
    src.start();
    return {
      volume: function (v) { g.gain.setTargetAtTime(ligado ? v : 0, c.currentTime, 0.05); },
      tom: function (f) { lp.frequency.setTargetAtTime(f, c.currentTime, 0.08); }
    };
  }

  function atualizarBotoes() {
    document.querySelectorAll("[data-som]").forEach(function (b) {
      b.setAttribute("aria-pressed", ligado ? "true" : "false");
      var r = b.querySelector("[data-som-rotulo]");
      if (r) r.textContent = (window.LANG === "en") ? (ligado ? "Sound off" : "Sound on") : (ligado ? "Desligar som" : "Ligar som");
    });
  }

  function definir(v) {
    ligado = v; guardar(v);
    if (v) contexto();
    atualizarBotoes();
    ouvintes.forEach(function (f) { f(v); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    ligado = lido();
    atualizarBotoes();
    document.querySelectorAll("[data-som]").forEach(function (b) {
      b.addEventListener("click", function () { definir(!ligado); });
    });
    /* o navegador só libera o áudio depois de um gesto */
    document.addEventListener("pointerdown", function () { if (ligado) contexto(); }, { once: true });
  });

  window.FRSom = {
    escapar: escapar,
    chiado: chiado,
    ligado: function () { return ligado; },
    aoMudar: function (f) { ouvintes.push(f); }
  };
})();
