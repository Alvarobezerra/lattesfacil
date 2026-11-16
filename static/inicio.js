(function () {
  // sombra na barra ao rolar
  var nav = document.getElementById("nav");
  function onScroll() { nav.classList.toggle("scrolled", window.scrollY > 8); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // entrada suave das seções
  var targets = document.querySelectorAll(".card, .who, .steps li, .qa, .checks li, .stats div");
  targets.forEach(function (el) { el.classList.add("rv"); });
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    targets.forEach(function (el) { io.observe(el); });
  } else {
    targets.forEach(function (el) { el.classList.add("in"); });
  }

  // demonstração: PDF -> campos do Lattes (em ciclo)
  var hl = document.querySelectorAll(".line.hl");
  var flds = document.querySelectorAll(".fld");
  var ok = document.querySelector(".demo-ok");
  if (!hl.length) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function reset() {
    hl.forEach(function (e) { e.classList.remove("on"); });
    flds.forEach(function (e) { e.classList.remove("on"); var s = e.firstElementChild; s.style.animation = "none"; void s.offsetWidth; s.style.animation = ""; });
    ok.classList.remove("on");
  }
  function run() {
    reset();
    [0, 1, 2].forEach(function (i) {
      setTimeout(function () { hl[i].classList.add("on"); }, 700 + i * 900);
      setTimeout(function () { flds[i].classList.add("on"); }, 1200 + i * 900);
    });
    setTimeout(function () { ok.classList.add("on"); }, 4300);
  }
  if (reduce) { hl.forEach(function (e) { e.classList.add("on"); }); flds.forEach(function (e) { e.classList.add("on"); }); ok.classList.add("on"); return; }
  run();
  setInterval(run, 8200);
})();
