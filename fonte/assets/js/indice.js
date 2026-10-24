document.addEventListener("DOMContentLoaded", function () {
  var botoes = document.querySelectorAll("[data-filtro]");
  var linhas = document.querySelectorAll(".tabela tbody tr");
  var contagem = document.querySelector("[data-contagem]");
  function aplicar(tipo) {
    var n = 0;
    linhas.forEach(function (tr) {
      var ok = !tipo || tr.getAttribute("data-tipo") === tipo;
      tr.hidden = !ok; if (ok) n++;
    });
    botoes.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-filtro") === tipo ? "true" : "false"); });
    if (contagem) contagem.textContent = n + ((window.LANG === "en") ? (n === 1 ? " work" : " works") : (n === 1 ? " obra" : " obras"));
  }
  botoes.forEach(function (b) { b.addEventListener("click", function () { aplicar(b.getAttribute("data-filtro")); }); });
  aplicar("");
});
