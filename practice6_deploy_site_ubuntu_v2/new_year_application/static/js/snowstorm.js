/*!
 * snowstorm.js — lightweight snow effect (educational implementation)
 * Creates a canvas overlay and renders falling snowflakes.
 *
 * Usage: include after <!--Scripts--> in index.html.
 */
/*
 * Эффект снежинок: рисуем прозрачный canvas поверх страницы.
 * Файл подключается из index.html.
 */

(function () {
  "use strict";

  var maxFlakes = 140;
  var flakes = [];
  var canvas, ctx;
  var w = 0, h = 0;
  var lastTs = 0;

  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  function resize() {
    w = window.innerWidth || document.documentElement.clientWidth;
    h = window.innerHeight || document.documentElement.clientHeight;
    canvas.width = Math.floor(w * devicePixelRatio);
    canvas.height = Math.floor(h * devicePixelRatio);
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  }

  function newFlake(y0) {
    return {
      x: rand(0, w),
      y: (typeof y0 === "number") ? y0 : rand(-h, 0),
      r: rand(1.2, 3.6),
      vy: rand(22, 60),         // px/sec
      vx: rand(-12, 12),        // px/sec
      phase: rand(0, Math.PI * 2),
      omega: rand(0.6, 1.6)     // sway
    };
  }

  function init() {
    canvas = document.createElement("canvas");
    canvas.id = "snowstorm-canvas";
    document.body.appendChild(canvas);
    ctx = canvas.getContext("2d", { alpha: true });

    resize();

    flakes.length = 0;
    for (var i = 0; i < maxFlakes; i++) flakes.push(newFlake(rand(-h, h)));

    window.addEventListener("resize", resize, { passive: true });
    requestAnimationFrame(tick);
  }

  function tick(ts) {
    if (!lastTs) lastTs = ts;
    var dt = Math.min(0.05, (ts - lastTs) / 1000);
    lastTs = ts;

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "rgba(255,255,255,0.9)";

    for (var i = 0; i < flakes.length; i++) {
      var f = flakes[i];

      f.phase += f.omega * dt;
      f.x += f.vx * dt + Math.sin(f.phase) * 10 * dt;
      f.y += f.vy * dt;

      if (f.y - f.r > h) {
        flakes[i] = newFlake(-10);
        continue;
      }
      if (f.x < -20) f.x = w + 20;
      if (f.x > w + 20) f.x = -20;

      ctx.beginPath();
      ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(tick);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
