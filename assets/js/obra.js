/* Escuta primeiro: o som antecede a imagem. As imagens surgem conforme se ouve. */
document.addEventListener("DOMContentLoaded", function () {
  var bloco = document.querySelector("[data-escuta]");
  if (!bloco) return;
  var botao = bloco.querySelector("[data-play]");
  var canvas = bloco.querySelector("[data-onda]");
  var tempo = bloco.querySelector("[data-tempo]");
  var audio = bloco.querySelector("audio");
  var iframe = bloco.querySelector("iframe.sc");
  var imagens = document.querySelector("[data-imagens]");
  var mostrar = document.querySelector("[data-mostrar]");
  var reduzido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var REVELA_EM = 45; /* segundos de escuta até a imagem aparecer por inteiro */

  var tocando = false, posicao = 0, duracao = 0, revelado = 0;

  /* forma de onda: uma assinatura fixa por obra, desenhada até o ponto já ouvido */
  var semente = 0;
  for (var i = 0; i < location.pathname.length; i++) semente = (semente * 31 + location.pathname.charCodeAt(i)) >>> 0;
  function aleat() { semente = (semente * 1664525 + 1013904223) >>> 0; return semente / 4294967296; }
  var N = 260, amps = [];
  for (var k = 0; k < N; k++) {
    var t = k / N;
    amps.push((0.25 + 0.75 * Math.pow(Math.sin(t * Math.PI * (2 + aleat() * 3)), 2)) * (0.35 + 0.65 * aleat()));
  }
  var cor = getComputedStyle(document.body);
  function desenhar() {
    var dpr = window.devicePixelRatio || 1;
    var w = canvas.clientWidth, h = canvas.clientHeight;
    if (canvas.width !== w * dpr) { canvas.width = w * dpr; canvas.height = h * dpr; }
    var g = canvas.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, w, h);
    var prog = duracao ? posicao / duracao : 0;
    var meio = h / 2, passo = w / N;
    var claro = cor.getPropertyValue("--ink-200").trim() || "#CFCBC4";
    var escuro = cor.getPropertyValue("--ink-900").trim() || "#151515";
    for (var j = 0; j < N; j++) {
      var x = j * passo;
      var ouvido = j / N <= prog;
      var a = amps[j] * (h * 0.46);
      if (!ouvido) a *= 0.35; /* o que ainda não foi ouvido é só um rastro */
      else if (tocando && !reduzido && j / N > prog - 0.02) a *= 0.6 + 0.4 * Math.random();
      g.fillStyle = ouvido ? escuro : claro;
      g.fillRect(x, meio - a, Math.max(1, passo * 0.45), Math.max(1, a * 2));
    }
  }

  function fmt(s) { s = Math.max(0, Math.floor(s)); return Math.floor(s / 60) + ":" + ("0" + (s % 60)).slice(-2); }
  function atualizar() {
    if (tempo) tempo.textContent = duracao ? fmt(posicao) + " / " + fmt(duracao) : "";
    if (imagens && imagens.classList.contains("velado")) {
      var v = Math.min(1, 0.08 + revelado / REVELA_EM);
      imagens.style.setProperty("--revela", v.toFixed(3));
      if (v >= 1) imagens.classList.remove("velado");
    }
    desenhar();
  }
  function estado(v) {
    tocando = v;
    botao.classList.toggle("tocando", v);
    botao.setAttribute("aria-label", (v ? "Pausar " : "Escutar ") + document.querySelector(".obra-titulo").textContent);
  }

  var ultimo = null;
  function laco(ts) {
    if (tocando) {
      if (ultimo !== null) revelado += (ts - ultimo) / 1000;
      ultimo = ts;
    } else ultimo = null;
    atualizar();
    requestAnimationFrame(laco);
  }
  requestAnimationFrame(laco);
  window.addEventListener("resize", desenhar);

  if (audio) {
    audio.addEventListener("loadedmetadata", function () { duracao = audio.duration; });
    audio.addEventListener("timeupdate", function () { posicao = audio.currentTime; });
    audio.addEventListener("play", function () { estado(true); });
    audio.addEventListener("pause", function () { estado(false); });
    audio.addEventListener("ended", function () { estado(false); });
    botao.addEventListener("click", function () { audio.paused ? audio.play() : audio.pause(); });
  } else if (iframe) {
    var widget = null;
    function preparar() {
      if (widget || !window.SC || !SC.Widget) return;
      widget = SC.Widget(iframe);
      widget.bind(SC.Widget.Events.READY, function () {
        widget.getDuration(function (d) { duracao = d / 1000; });
      });
      widget.bind(SC.Widget.Events.PLAY_PROGRESS, function (e) { posicao = e.currentPosition / 1000; });
      widget.bind(SC.Widget.Events.PLAY, function () { estado(true); });
      widget.bind(SC.Widget.Events.PAUSE, function () { estado(false); });
      widget.bind(SC.Widget.Events.FINISH, function () { estado(false); });
    }
    var tentativas = 0;
    var espera = setInterval(function () { preparar(); if (widget || ++tentativas > 60) clearInterval(espera); }, 250);
    botao.addEventListener("click", function () { preparar(); if (widget) widget.toggle(); });
  }

  if (mostrar) mostrar.addEventListener("click", function () {
    revelado = REVELA_EM; atualizar(); mostrar.remove();
  });
  if (reduzido && imagens) imagens.classList.remove("velado");
});
