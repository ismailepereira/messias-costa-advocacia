/* =========================================================================
   Sistema de movimento — Motion (motion.dev)
   Direção "arquivo/processo": movimento contido e estrutural. Texto que
   assenta, réguas que se desenham, wipe no retrato. Nada de brilho seguindo
   o cursor, botão magnético ou contador de números — são clichês de
   portfólio de agência e, num site de advogado, leem como truque.

   O cabeçalho corrido fixo de cada seção (.running-head) é CSS puro
   (position: sticky) — não custa JS nem frame.

   Duas armadilhas resolvidas aqui (ambas verificadas em runtime):

   1. No Motion v11 a opção de curva é `ease`. `easing` (API antiga do
      Motion One) é aceita sem erro mas IGNORADA — cai na curva padrão.

   2. `inView` usa IntersectionObserver, que só reporta o estado no frame
      atual. Um salto de scroll (arrastar a barra, tecla End, link âncora,
      recarregar no meio da página) pula o elemento sem nunca marcá-lo como
      visível — e ele fica invisível PARA SEMPRE. Daí o `catchUp()`.
   ========================================================================= */
import { animate, inView, scroll, stagger } from "motion";

window.__motionOK = true; // sinaliza pra rede de segurança inline do index.html

(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var EASE = [0.22, 1, 0.36, 1];      // saída suave e controlada
  var EASE_MASK = [0.16, 1, 0.3, 1];  // mais "pesada", pra texto mascarado

  var anoEl = document.getElementById("ano");
  if (anoEl) anoEl.textContent = new Date().getFullYear();

  /* ---------------------------------------------------------------
     Fatiamento de texto
     --------------------------------------------------------------- */

  /* Palavra a palavra: <span class="word"><i>palavra</i></span>.
     Percorre nó a nó pra PRESERVAR a marcação interna — um título com
     <span> de destaque perderia o estilo se fosse reconstruído a partir
     do textContent. As classes do elemento original vão pro <i>. */
  function splitWords(el) {
    var nodes = Array.prototype.slice.call(el.childNodes);
    var inners = [];
    el.textContent = "";
    nodes.forEach(function (node) {
      var cls = node.nodeType === 1 ? (node.getAttribute("class") || "") : "";
      var words = (node.textContent || "").trim().split(/\s+/).filter(Boolean);
      words.forEach(function (w) {
        var outer = document.createElement("span");
        outer.className = "word";
        var inner = document.createElement("i");
        if (cls) inner.className = cls;
        inner.textContent = w;
        outer.appendChild(inner);
        el.appendChild(outer);
        el.appendChild(document.createTextNode(" "));
        inners.push(inner);
      });
    });
    return inners;
  }

  /* Linha a linha: envolve o conteúdo de cada <span> filho num <i> deslizante */
  function splitLines(el) {
    var inners = [];
    Array.prototype.forEach.call(el.children, function (line) {
      var inner = document.createElement("i");
      while (line.firstChild) inner.appendChild(line.firstChild);
      line.appendChild(inner);
      inners.push(inner);
    });
    return inners;
  }

  function show(el) { el.style.opacity = 1; el.style.transform = "none"; }
  function showAll(list) { Array.prototype.forEach.call(list, show); }
  function drawRule(el) { el.style.transform = "scaleX(1)"; }

  /* ---------------------------------------------------------------
     Caminho sem animação (prefers-reduced-motion)
     --------------------------------------------------------------- */
  if (reduce) {
    showAll(document.querySelectorAll(".reveal,[data-intro],[data-split],[data-split-lines]"));
    document.querySelectorAll("[data-rule]").forEach(drawRule);
    document.querySelectorAll("[data-wipe]").forEach(function (el) { el.style.clipPath = "none"; });
    setupNavMenu();
    return;
  }

  document.documentElement.classList.add("js-split");

  /* ---------------------------------------------------------------
     Registro de entradas + rede contra saltos de scroll
     --------------------------------------------------------------- */
  var pending = [];

  function onEnter(el, play, finish, amount) {
    var rec = { el: el, done: false, finish: finish };
    pending.push(rec);
    inView(el, function () {
      if (rec.done) return;
      rec.done = true;
      play();
    }, { amount: amount == null ? 0.25 : amount });
  }

  /* Finaliza sem animar tudo cujo topo já passou do topo da viewport.
     Critério é `top < 0` (e não `bottom < 0`): um elemento parcialmente
     cortado por cima pode nunca atingir o `amount` do observer e ficaria
     invisível pra sempre se o usuário rolasse de volta. */
  function catchUp() {
    for (var i = 0; i < pending.length; i++) {
      var rec = pending[i];
      if (rec.done) continue;
      if (rec.el.getBoundingClientRect().top < 0) { rec.done = true; rec.finish(); }
    }
  }

  var catchUpQueued = false;
  addEventListener("scroll", function () {
    if (catchUpQueued) return;
    catchUpQueued = true;
    requestAnimationFrame(function () { catchUpQueued = false; catchUp(); });
  }, { passive: true });

  /* ---------------------------------------------------------------
     1. Barra de progresso de leitura
     --------------------------------------------------------------- */
  var progress = document.getElementById("progress");
  if (progress) {
    try { scroll(animate(progress, { scaleX: [0, 1] }, { ease: "linear" })); } catch (e) {}
  }

  /* ---------------------------------------------------------------
     2. Abertura do cabeçalho — metadados, nome, réguas, texto, ações
     --------------------------------------------------------------- */
  var hero = document.querySelector(".hero");

  var heroTitle = document.querySelector(".hero h1[data-split-lines]");
  var heroLines = heroTitle ? splitLines(heroTitle) : [];
  if (heroTitle) heroTitle.style.opacity = 1;

  // os [data-intro] do hero entram em cascata, na ordem do documento
  var heroIntro = hero ? hero.querySelectorAll("[data-intro]") : [];
  Array.prototype.forEach.call(heroIntro, function (el, i) {
    animate(el, { opacity: [0, 1], y: [12, 0] },
      { duration: 0.7, delay: 0.15 + i * 0.14, ease: EASE });
  });

  if (heroLines.length) {
    animate(heroLines, { y: ["110%", "0%"] },
      { duration: 1.1, delay: stagger(0.1, { startDelay: 0.3 }), ease: EASE_MASK });
  }

  var heroRules = hero ? hero.querySelectorAll("[data-rule]") : [];
  Array.prototype.forEach.call(heroRules, function (el, i) {
    animate(el, { scaleX: [0, 1] }, { duration: 0.9, delay: 0.35 + i * 0.35, ease: EASE });
  });

  // garante o estado final da abertura mesmo se algo acima falhar
  setTimeout(function () {
    showAll(document.querySelectorAll("[data-intro]"));
    if (heroTitle) {
      heroTitle.style.opacity = 1;
      heroLines.forEach(function (l) { l.style.transform = "none"; });
    }
    Array.prototype.forEach.call(heroRules, drawRule);
  }, 3000);

  /* ---------------------------------------------------------------
     3. Parallax da pauta do fundo + sumiço da indicação de rolagem
     --------------------------------------------------------------- */
  document.querySelectorAll("[data-parallax]").forEach(function (el) {
    var depth = parseFloat(el.dataset.parallax) || 0.12;
    var section = el.closest("section, header") || el.parentElement;
    var isHero = !!el.closest(".hero");
    try {
      scroll(
        animate(el, { y: [0, Math.round(depth * 320)] }, { ease: "linear" }),
        { target: section, offset: isHero ? ["start start", "end start"] : ["start end", "end start"] }
      );
    } catch (e) { /* decorativo — não pode quebrar a página */ }
  });

  var cue = document.getElementById("scroll-cue");
  if (cue && hero) {
    try {
      scroll(animate(cue, { opacity: [1, 0] }, { ease: "linear" }),
        { target: hero, offset: ["start start", "30% start"] });
    } catch (e) {}
  }

  /* ---------------------------------------------------------------
     4. Títulos — máscara palavra a palavra
     --------------------------------------------------------------- */
  document.querySelectorAll("[data-split]").forEach(function (el) {
    var inners = splitWords(el);
    el.style.opacity = 1;
    onEnter(el,
      function () { animate(inners, { y: ["110%", "0%"] }, { duration: 1, delay: stagger(0.05), ease: EASE_MASK }); },
      function () { inners.forEach(function (i) { i.style.transform = "none"; }); },
      0.4);
  });

  /* ---------------------------------------------------------------
     5. Reveals — em grupo (stagger) e individuais
     --------------------------------------------------------------- */
  document.querySelectorAll("[data-stagger]").forEach(function (group) {
    var items = group.querySelectorAll(".reveal");
    if (!items.length) return;
    onEnter(group,
      function () { animate(items, { opacity: [0, 1], y: [18, 0] }, { duration: 0.8, delay: stagger(0.07), ease: EASE }); },
      function () { showAll(items); },
      0.15);
  });

  document.querySelectorAll(".reveal").forEach(function (el) {
    if (el.closest("[data-stagger]")) return; // já coberto pelo grupo
    onEnter(el,
      function () { animate(el, { opacity: [0, 1], y: [18, 0] }, { duration: 0.8, ease: EASE }); },
      function () { show(el); },
      0.25);
  });

  /* réguas fora do hero se desenham ao entrar em tela */
  document.querySelectorAll("[data-rule]").forEach(function (el) {
    if (el.closest(".hero")) return; // já animada na abertura
    onEnter(el,
      function () { animate(el, { scaleX: [0, 1] }, { duration: 1, ease: EASE }); },
      function () { drawRule(el); },
      0.9);
  });

  /* wipe vertical no retrato */
  document.querySelectorAll("[data-wipe]").forEach(function (el) {
    onEnter(el,
      function () { animate(el, { clipPath: ["inset(0 0 100% 0)", "inset(0 0 0% 0)"] }, { duration: 1.1, ease: EASE_MASK }); },
      function () { el.style.clipPath = "none"; },
      0.3);
  });

  /* já abriu a página com o scroll no meio? resolve na hora */
  catchUp();
  addEventListener("load", catchUp);

  /* ---------------------------------------------------------------
     6. Nav — fundo ao rolar, auto-hide descendo, link ativo por seção
     --------------------------------------------------------------- */
  var nav = document.getElementById("site-nav");
  var lastY = window.scrollY;
  var navHidden = false;

  addEventListener("scroll", function () {
    var y = window.scrollY;
    if (nav) {
      nav.classList.toggle("scrolled", y > 10);
      var goingDown = y > lastY;
      if (goingDown && y > 400 && !navHidden) {
        navHidden = true;
        animate(nav, { y: "-100%" }, { duration: 0.45, ease: EASE });
      } else if (!goingDown && navHidden) {
        navHidden = false;
        animate(nav, { y: "0%" }, { duration: 0.45, ease: EASE });
      }
    }
    lastY = y;
  }, { passive: true });

  document.querySelectorAll("section[id]").forEach(function (sec) {
    var link = document.querySelector('.nav-link[href="#' + sec.id + '"]');
    if (!link) return;
    inView(sec, function () {
      document.querySelectorAll(".nav-link").forEach(function (l) { l.classList.remove("active"); });
      link.classList.add("active");
      return function () {};
    }, { amount: 0.3 });
  });

  setupNavMenu();

  /* ---------------------------------------------------------------
     Menu mobile (usado pelos dois caminhos)
     --------------------------------------------------------------- */
  function setupNavMenu() {
    var toggle = document.getElementById("nav-toggle");
    var mobile = document.getElementById("nav-mobile");
    if (!toggle || !mobile) return;
    toggle.addEventListener("click", function () {
      var open = mobile.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open && !reduce) {
        animate(mobile.querySelectorAll("a"), { opacity: [0, 1], y: [8, 0] },
          { duration: 0.4, delay: stagger(0.05), ease: EASE });
      }
    });
    mobile.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        mobile.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

})();
