/* 蓬萊仙闕首屏水墨：底圖是一幅水墨山水（.hero-art 的 <img>），上面疊兩層即時渲染——
 * 緩慢流動的雲霧，以及手指或滑鼠劃過時在紙上暈開、慢慢淡去的墨。標題與首屏文字範圍內的墨會淡到幾乎看不見。
 * 自寫 WebGL1，不用外部函式庫。降級：不支援 WebGL、低階裝置、省流量、偏好減少動態 → 不啟動，就是那張靜態山水。
 * 執行中：分頁在背景或首屏捲出畫面就暫停；畫面太慢先降解析度，再慢就停在最後一格。
 * 量測：window.__ink（狀態、等級、平均幀間隔 avgFrame、每格繪製 avgDraw，單位 ms）。 */
(function () {
  "use strict";
  var hero = document.querySelector("[data-ink]");
  var art = hero && hero.querySelector(".hero-art img");
  if (!hero || !art) return;
  var stat = (window.__ink = { state: "init", tier: 0, frames: 0, avgFrame: 0, avgDraw: 0 });
  var mq = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : null;
  var nav = navigator, conn = nav.connection || {};
  if ((mq && mq.matches) || conn.saveData || (nav.deviceMemory && nav.deviceMemory <= 2) ||
      (nav.hardwareConcurrency && nav.hardwareConcurrency <= 2)) { stat.state = "static"; return; }

  var canvas = document.createElement("canvas");
  canvas.className = "ink-canvas";
  canvas.setAttribute("aria-hidden", "true");
  var opts = { alpha: false, antialias: false, depth: false, stencil: false, premultipliedAlpha: false, powerPreference: "low-power" };
  var gl = canvas.getContext("webgl", opts) || canvas.getContext("experimental-webgl", opts);
  if (!gl) { stat.state = "no-webgl"; return; }

  var NOISE = [
    "float hash(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}",
    "float noise(vec2 p){vec2 i=floor(p),f=fract(p);vec2 u=f*f*(3.-2.*f);",
    "return mix(mix(hash(i),hash(i+vec2(1,0)),u.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),u.x),u.y);}",
    "float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*noise(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return v;}"
  ].join("\n");
  var VS = "attribute vec2 a;varying vec2 v;void main(){v=a*.5+.5;gl_Position=vec4(a,0.,1.);}";
  // 墨的擴散：上一格的墨＋鄰近平均（暈開）＋沿雜訊流動，乘上衰減，再加上手指劃過的一段
  var FS_SIM = [
    "precision highp float;varying vec2 v;uniform sampler2D P;uniform vec2 S;uniform float T,K,M;",
    "uniform vec2 A,B;uniform float AR,RAD;", NOISE,
    "float seg(vec2 p,vec2 a,vec2 b){vec2 pa=p-a,ba=b-a;float h=clamp(dot(pa,ba)/max(dot(ba,ba),1e-6),0.,1.);return length(pa-ba*h);}",
    "void main(){vec2 px=1./S;",
    "  vec2 fl=(vec2(noise(v*5.+T*.03),noise(v*5.+vec2(7.3,2.1)-T*.03))-.5)*px*.8;",
    "  float c=texture2D(P,v-fl).r;",
    "  float n=(texture2D(P,v+vec2(px.x,0.)).r+texture2D(P,v-vec2(px.x,0.)).r+texture2D(P,v+vec2(0.,px.y)).r+texture2D(P,v-vec2(0.,px.y)).r)*.25;",
    "  float val=mix(c,n,.22)*K-.0022;",
    "  if(M>0.){vec2 q=vec2(v.x*AR,v.y);float d=seg(q,vec2(A.x*AR,A.y),vec2(B.x*AR,B.y));",
    "    val+=M*exp(-d*d/(RAD*RAD))*(.75+.25*noise(v*S*.2));}",
    "  gl_FragColor=vec4(clamp(val,0.,1.),0.,0.,1.);}"
  ].join("\n");
  // 合成：山水底圖（object-fit: cover 的對應）＋雲霧＋墨；G1、G2 是文字範圍，墨在裡面淡掉
  var FS_OUT = [
    "precision highp float;varying vec2 v;uniform sampler2D BG,INK;uniform vec2 S;uniform float T,SC,AR;",
    "uniform vec4 CV,G1,G2;uniform vec3 PA;", NOISE,
    "float box(vec4 r,vec2 p){vec2 e=vec2(.05,.04);return smoothstep(r.x-e.x,r.x,p.x)*smoothstep(r.z+e.x,r.z,p.x)*smoothstep(r.y-e.y,r.y,p.y)*smoothstep(r.w+e.y,r.w,p.y);}",
    "void main(){vec2 uv=v;",
    "  vec2 iu=vec2(CV.z+uv.x*CV.x,1.-(CV.w+(1.-uv.y)*CV.y));iu.y=clamp(iu.y-SC*.04,0.,1.);",
    "  vec3 col=texture2D(BG,iu).rgb;",
    "  float m=fbm(vec2(uv.x*AR*1.2-T*.012,uv.y*3.4+T*.004));",
    "  float band=smoothstep(.08,.30,uv.y)*smoothstep(.80,.42,uv.y);",
    "  col=mix(col,PA,clamp(smoothstep(.46,.78,m)*band*(.38+SC*.5),0.,.8));",
    "  vec2 px=1./S;float i=texture2D(INK,uv).r;",
    "  float g=abs(texture2D(INK,uv+vec2(px.x,0.)).r-texture2D(INK,uv-vec2(px.x,0.)).r)+abs(texture2D(INK,uv+vec2(0.,px.y)).r-texture2D(INK,uv-vec2(0.,px.y)).r);",
    "  float a=(1.-exp(-i*2.4))*(.9+.15*noise(uv*S*.6));",
    "  float guard=1.-.88*max(box(G1,uv),box(G2,uv));",
    "  col=mix(col,vec3(.11,.10,.10),clamp((a*.68+g*.8)*guard,0.,.82));",
    "  gl_FragColor=vec4(col,1.);}"
  ].join("\n");

  function sh(type, src) {
    var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  function prog(fs) {
    var p = gl.createProgram();
    gl.attachShader(p, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs));
    gl.bindAttribLocation(p, 0, "a"); gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    var u = {}, n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (var i = 0; i < n; i++) { var name = gl.getActiveUniform(p, i).name; u[name] = gl.getUniformLocation(p, name); }
    return { p: p, u: u };
  }
  function texParams() {
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  }
  function target(w, h) {
    var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t); texParams();
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    var f = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, f);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0);
    return { t: t, f: f, w: w, h: h };
  }
  function free(o) { if (o) { gl.deleteTexture(o.t); gl.deleteFramebuffer(o.f); } }

  var P_SIM, P_OUT;
  try { P_SIM = prog(FS_SIM); P_OUT = prog(FS_OUT); }
  catch (e) { stat.state = "shader-error"; stat.error = String(e); return; }
  var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
  function quad() { gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); }

  // ------------------------------------------------------------------ 山水底圖（和畫面上的 <img> 同一張）
  var bgTex = null, bgSrc = "", imgW = 1, imgH = 1;
  function loadBg() {
    if (!art.complete || !art.naturalWidth || art.currentSrc === bgSrc) return !!bgTex;
    bgSrc = art.currentSrc; imgW = art.naturalWidth; imgH = art.naturalHeight;
    if (!bgTex) bgTex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, bgTex); texParams();
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    try { gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, art); }
    catch (e) { stat.state = "texture-error"; return false; }
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    return true;
  }
  art.addEventListener("load", function () { wake(); });

  // ------------------------------------------------------------------ 尺寸、畫質等級、文字範圍
  var TIERS = [1.5, 1.0, 0.7];
  var small = Math.min(window.innerWidth, screen.width || 9999) < 700;
  var tier = small ? 1 : 0;
  var W = 0, H = 0, simA = null, simB = null, guards = [[0, 0, 0, 0], [0, 0, 0, 0]], cover = [1, 1, 0, 0];
  var guardEls = hero.querySelectorAll("[data-ink-guard]");
  function measure() {
    var r = hero.getBoundingClientRect();
    for (var i = 0; i < 2; i++) {
      var el = guardEls[i];
      if (!el) { guards[i] = [0, 0, 0, 0]; continue; }
      var b = el.getBoundingClientRect();
      guards[i] = [(b.left - r.left) / r.width, 1 - (b.bottom - r.top) / r.height, (b.right - r.left) / r.width, 1 - (b.top - r.top) / r.height];
    }
    // object-fit: cover ＋ object-position（照 CSS 算，讓墨對得上山）
    var pos = getComputedStyle(art).objectPosition.split(" ");
    var px = parseFloat(pos[0]) / 100, py = parseFloat(pos[1] || "50%") / 100;
    if (isNaN(px)) px = .5; if (isNaN(py)) py = .5;
    var ca = r.width / r.height, ia = imgW / imgH, sx = 1, sy = 1;
    if (ca > ia) sy = ia / ca; else sx = ca / ia;
    cover = [sx, sy, px * (1 - sx), py * (1 - sy)];
  }
  function resize() {
    var r = hero.getBoundingClientRect();
    var scale = Math.min(window.devicePixelRatio || 1, TIERS[tier]);
    var w = Math.max(2, Math.round(r.width * scale)), h = Math.max(2, Math.round(r.height * scale));
    if (w === W && h === H) return;
    W = w; H = h; canvas.width = w; canvas.height = h;
    measure();
    var sw = Math.max(96, Math.min(320, Math.round(r.width / 4))), shh = Math.max(96, Math.round(sw * r.height / r.width));
    if (!simA || simA.w !== sw || simA.h !== shh) {
      free(simA); free(simB); simA = target(sw, shh); simB = target(sw, shh);
      [simA, simB].forEach(function (s) { gl.bindFramebuffer(gl.FRAMEBUFFER, s.f); gl.clearColor(0, 0, 0, 1); gl.clear(gl.COLOR_BUFFER_BIT); });
    }
  }

  // ------------------------------------------------------------------ 指標
  var cur = null, last = null, moved = false, fresh = false;
  function point(cx, cy) {
    var r = hero.getBoundingClientRect();
    var p = { x: (cx - r.left) / r.width, y: 1 - (cy - r.top) / r.height, t: performance.now() };
    if (p.x < 0 || p.x > 1 || p.y < 0 || p.y > 1) { last = null; return; }
    if (!last) { last = p; fresh = true; }
    cur = p; moved = true; wake();
  }
  hero.addEventListener("pointermove", function (e) { if (e.pointerType !== "touch") point(e.clientX, e.clientY); }, { passive: true });
  hero.addEventListener("pointerleave", function () { last = null; }, { passive: true });
  hero.addEventListener("touchstart", function (e) { last = null; var t = e.touches[0]; if (t) point(t.clientX, t.clientY); }, { passive: true });
  hero.addEventListener("touchmove", function (e) { var t = e.touches[0]; if (t) point(t.clientX, t.clientY); }, { passive: true });
  hero.addEventListener("touchend", function () { last = null; }, { passive: true });

  // 開場：一滴墨落在山腳的霧裡，慢慢暈開（提示可以用手劃）
  var drop = small ? { x: .34, y: .45 } : { x: .70, y: .30 };

  // ------------------------------------------------------------------ 迴圈
  var t0 = performance.now(), prevT = t0, raf = 0, running = false, visible = true, slowCount = 0, sum = 0, sumDraw = 0, n = 0;
  var scrollK = 0, PA = [0.98, 0.93, 0.855];
  function frame(now) {
    raf = 0;
    if (!loadBg()) { running = false; return; }        // 等底圖載好（load 事件會再叫醒）
    var dt = Math.min(.05, (now - prevT) / 1000); prevT = now;
    var T = (now - t0) / 1000;
    var d0 = performance.now();
    resize();
    var aspect = W / H, amt = 0, A = [0, 0], B = [0, 0], rad = small ? .026 : .022;
    if (moved && cur && last) {
      var dx = (cur.x - last.x) * aspect, dy = cur.y - last.y, dist = Math.sqrt(dx * dx + dy * dy);
      var speed = dist / Math.max(.008, (cur.t - last.t) / 1000);
      amt = fresh ? .05 : Math.min(.26, .08 + .035 / Math.max(.15, speed));   // 第一下輕；慢慢劃，墨比較多
      A = [last.x, last.y]; B = [cur.x, cur.y]; last = cur; moved = false; fresh = false;
    } else if (T > .8 && T < 2.3) {
      var k = (T - .8) / 1.5; amt = .045 * (1 - k); rad = (small ? .022 : .016) * (1 + k * .8); A = B = [drop.x, drop.y];
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER, simB.f); gl.viewport(0, 0, simB.w, simB.h);
    gl.useProgram(P_SIM.p);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, simA.t); gl.uniform1i(P_SIM.u.P, 0);
    gl.uniform2f(P_SIM.u.S, simA.w, simA.h); gl.uniform1f(P_SIM.u.T, T);
    gl.uniform1f(P_SIM.u.K, Math.pow(.9955, dt * 60)); gl.uniform1f(P_SIM.u.M, amt);
    gl.uniform2f(P_SIM.u.A, A[0], A[1]); gl.uniform2f(P_SIM.u.B, B[0], B[1]);
    gl.uniform1f(P_SIM.u.AR, aspect); gl.uniform1f(P_SIM.u.RAD, rad);
    quad();
    var s = simA; simA = simB; simB = s;
    gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H);
    gl.useProgram(P_OUT.p);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, bgTex); gl.uniform1i(P_OUT.u.BG, 0);
    gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, simA.t); gl.uniform1i(P_OUT.u.INK, 1);
    gl.uniform2f(P_OUT.u.S, simA.w, simA.h); gl.uniform1f(P_OUT.u.T, T + 40);
    gl.uniform1f(P_OUT.u.SC, scrollK); gl.uniform1f(P_OUT.u.AR, aspect);
    gl.uniform4f(P_OUT.u.CV, cover[0], cover[1], cover[2], cover[3]);
    gl.uniform4f(P_OUT.u.G1, guards[0][0], guards[0][1], guards[0][2], guards[0][3]);
    gl.uniform4f(P_OUT.u.G2, guards[1][0], guards[1][1], guards[1][2], guards[1][3]);
    gl.uniform3f(P_OUT.u.PA, PA[0], PA[1], PA[2]);
    quad();
    var drawMs = performance.now() - d0;
    if (!canvas.parentNode) { art.parentNode.insertAdjacentElement("afterend", canvas); requestAnimationFrame(function () { canvas.classList.add("on"); }); }
    stat.frames++;
    if (stat.frames > 20 && dt > 0) {
      sum += dt * 1000; sumDraw += drawMs; n++;
      stat.avgFrame = +(sum / n).toFixed(2); stat.avgDraw = +(sumDraw / n).toFixed(2);
      if (n % 90 === 0) {
        var avg = sum / n;
        if (avg > 26 && tier < TIERS.length - 1) { tier++; stat.tier = tier; W = 0; sum = sumDraw = n = 0; }
        else if (avg > 40) { slowCount++; if (slowCount >= 2) { stat.state = "stopped-slow"; running = false; return; } }
      }
    }
    stat.state = "running";
    if (running) raf = requestAnimationFrame(frame);
  }
  function wake() { if (!running && visible && !document.hidden && stat.state !== "stopped-slow") { running = true; prevT = performance.now(); raf = requestAnimationFrame(frame); } }
  function sleep() { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; if (stat.state === "running") stat.state = "paused"; }
  document.addEventListener("visibilitychange", function () { document.hidden ? sleep() : wake(); });
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; visible ? wake() : sleep(); }).observe(hero);
  }
  window.addEventListener("scroll", function () {
    var r = hero.getBoundingClientRect(); scrollK = Math.max(0, Math.min(1, -r.top / Math.max(1, r.height)));
  }, { passive: true });
  window.addEventListener("resize", function () { W = 0; wake(); }, { passive: true });
  canvas.addEventListener("webglcontextlost", function (e) { e.preventDefault(); sleep(); stat.state = "context-lost"; canvas.remove(); });
  stat.tier = tier;
  wake();
})();
