// AMH space kit: one globe + sky for every AMH landing (Site Revival, AMH hub, Walrus Tusk, Service Pricer).
// <div data-space-globe data-base="/space/" data-accent="#3ef2a2" data-rocks="1"></div>
// <canvas data-space-sky data-accent="#3ef2a2" data-density="4200" data-every="2.4"></canvas>
// Earth = day/night shader (NASA blue marble + city lights) with moving clouds, cloud shadows, ocean glint,
// twilight band and a scattering limb. Rocks = Blender/Cycles 6x6 turntable sheets. Meteors burn up in the air.
import * as THREE from "./vendor/three.module.js";

const REDUCE = matchMedia("(prefers-reduced-motion: reduce)").matches;
const lerp = (a, b, t) => a + (b - a) * t;
const ADD = { blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneFactor, blendSrcAlpha: THREE.ZeroFactor, blendDstAlpha: THREE.OneFactor };
const hexRgb = (h) => { const n = parseInt(String(h || "#3ef2a2").replace("#", ""), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };

function flareDot() { const c = document.createElement("canvas"); c.width = c.height = 32; const x = c.getContext("2d"), g = x.createRadialGradient(16, 16, 0, 16, 16, 16); g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(.5, "rgba(255,255,255,.5)"); g.addColorStop(1, "rgba(255,255,255,0)"); x.fillStyle = g; x.fillRect(0, 0, 32, 32); return new THREE.CanvasTexture(c); }
/* ------------------------------------------------------------------ GLOBE */
export function mountGlobe(wrap, o = {}) {
  if (!wrap || wrap.__space) return; wrap.__space = 1;
  // lazy: textures + WebGL only spin up when the globe is about to scroll into view
  if ("IntersectionObserver" in window && !o.now) {
    const io = new IntersectionObserver((e) => { if (e.some((x) => x.isIntersecting)) { io.disconnect(); startGlobe(wrap, o); } }, { rootMargin: "600px 0px" });
    io.observe(wrap); return;
  }
  startGlobe(wrap, o);
}
function startGlobe(wrap, o) {
  const arcsOn = o.arcs === true || o.arcs === "1";
  const base = o.base || "/space/", accent = new THREE.Color(o.accent || "#3ef2a2"), rocksOn = o.rocks !== false && o.rocks !== "0";
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" }); }
  catch (e) { wrap.classList.add("space-nogl"); return; }
  const small = Math.min(innerWidth, innerHeight) < 700;
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, small ? 1.75 : 2));
  renderer.setClearColor(0, 0);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const cv = renderer.domElement; cv.className = "space-globe-cv"; cv.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block"; cv.style.opacity = "0"; cv.style.transition = "opacity 1.2s ease";
  // Keep the full orbit visible; a circular fade used to erase the outer asteroids.
  wrap.appendChild(cv);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 300);
  const camBase = new THREE.Vector3(0, 0.5, 4.75); camera.position.copy(camBase); camera.lookAt(0, 0, 0);
  const SUN = new THREE.Vector3(1.0, 0.32, 0.62).normalize();
const SPIN = (Math.PI * 2) / 75; // earth: one revolution per 75 s
  const loader = new THREE.TextureLoader(); let pending = 0;
  const tex = (f, srgb, cb) => { pending++; return loader.load(base + f, (t) => { cb && cb(t); if (--pending === 0) ready(); }, undefined, () => { if (--pending === 0) ready(); }); };
  const srgb = (t) => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; };

  /* stars + milky-way band + faint nebulae */
  {
    const count = small ? 2600 : 4200, pos = new Float32Array(count * 3), col = new Float32Array(count * 3), siz = new Float32Array(count), c = new THREE.Color();
    const band = new THREE.Vector3(0.35, 1, 0.2).normalize(); // galactic pole
    const tmp = new THREE.Vector3();
    for (let i = 0; i < count; i++) {
      const r = 60 + Math.random() * 30;
      tmp.set(Math.random() * 2 - 1, Math.random() * 2 - 1, Math.random() * 2 - 1).normalize();
      if (i < count * 0.45) { tmp.addScaledVector(band, -tmp.dot(band) * (0.82 + Math.random() * 0.18)).normalize(); } // pull into the band
      pos.set([tmp.x * r, tmp.y * r, tmp.z * r], i * 3);
      const roll = Math.random();
      if (roll > 0.965) c.setHSL(0.08, 0.6, 0.78); else if (roll > 0.86) c.setHSL(0.6, 0.45, 0.84); else c.setHSL(0.12, 0.06, 0.7 + Math.random() * 0.3);
      col.set([c.r, c.g, c.b], i * 3);
      siz[i] = Math.random() > 0.988 ? 0.22 + Math.random() * 0.14 : 0.035 + Math.random() * 0.07;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setAttribute("color", new THREE.BufferAttribute(col, 3)); g.setAttribute("aSize", new THREE.BufferAttribute(siz, 1));
    const starMat = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, ...ADD, vertexColors: true,
      uniforms: { uTime: { value: 0 }, uScale: { value: 3400 } },
      vertexShader: "attribute float aSize;varying vec3 vC;varying float vTw;uniform float uTime;uniform float uScale;void main(){vC=color;float s=dot(position,vec3(.13,.27,.41));vTw=.72+.28*sin(uTime*(1.2+fract(s)*1.6)+s);vec4 mv=modelViewMatrix*vec4(position,1.);gl_PointSize=max(1.2,aSize*uScale/max(.001,-mv.z));gl_Position=projectionMatrix*mv;}",
      fragmentShader: "varying vec3 vC;varying float vTw;void main(){vec2 p=gl_PointCoord-.5;float d=length(p);float core=smoothstep(.5,.0,d);float k=core*core;float spike=max(0.,1.-abs(p.x)*14.)*max(0.,1.-abs(p.y)*2.2)+max(0.,1.-abs(p.y)*14.)*max(0.,1.-abs(p.x)*2.2);gl_FragColor=vec4(vC*(k+spike*.25*step(.5,vTw))*vTw,1.);}",
    });
    const pts = new THREE.Points(g, starMat); pts.frustumCulled = false; scene.add(pts); scene.userData.starMat = starMat;
    // nebula haze sprites (accent + violet), very faint, far behind
    const nc = document.createElement("canvas"); nc.width = nc.height = 128;
    const nx = nc.getContext("2d"), ng = nx.createRadialGradient(64, 64, 0, 64, 64, 64);
    ng.addColorStop(0, "rgba(255,255,255,.55)"); ng.addColorStop(.4, "rgba(255,255,255,.16)"); ng.addColorStop(1, "rgba(255,255,255,0)");
    nx.fillStyle = ng; nx.fillRect(0, 0, 128, 128);
    const nt = new THREE.CanvasTexture(nc);
    [[new THREE.Color(0xffffff), -26, 14, -55, 46, 0.012]].forEach(([cl, x, y, z, s, op]) => {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: nt, color: cl, transparent: true, opacity: op, depthWrite: false, ...ADD }));
      sp.position.set(x, y, z); sp.scale.setScalar(s); scene.add(sp);
    });
  }

  /* earth: day/night + clouds + glint + twilight in one shader */
  const tilt = new THREE.Group(); tilt.rotation.z = (-23.4 * Math.PI) / 180; scene.add(tilt);
  const spin = new THREE.Group(); spin.rotation.y = o.startRot != null ? +o.startRot : -2.2; tilt.add(spin);
  const U = {
    uDay: { value: tex("earth-day.webp", 1, srgb) }, uNight: { value: tex("earth-lights.webp", 1, srgb) },
    uSpec: { value: tex("earth-spec.webp", 0) }, uCloud: { value: tex("earth-clouds.webp", 0) },
    uSun: { value: SUN.clone() }, uTime: { value: 0 }, uAtmo: { value: new THREE.Color(0x6fb7ff) }, uNightTint: { value: new THREE.Color(1.0, 0.78, 0.5) },
  };
  for (const k of ["uDay", "uNight", "uSpec", "uCloud"]) { U[k].value.wrapS = THREE.RepeatWrapping; U[k].value.anisotropy = 4; }
  const earthMat = new THREE.ShaderMaterial({
    uniforms: U,
    vertexShader: "varying vec2 vUv;varying vec3 vN;varying vec3 vP;void main(){vUv=uv;vN=normalize(mat3(modelMatrix)*normal);vec4 w=modelMatrix*vec4(position,1.);vP=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}",
    fragmentShader: `
      uniform sampler2D uDay,uNight,uSpec,uCloud;uniform vec3 uSun,uAtmo,uNightTint;uniform float uTime;
      varying vec2 vUv;varying vec3 vN;varying vec3 vP;
      void main(){
        vec3 N=normalize(vN),L=normalize(uSun),V=normalize(cameraPosition-vP);
        float d=dot(N,L);
        vec3 day=texture2D(uDay,vUv).rgb;
        vec3 night=texture2D(uNight,vUv).rgb;
        vec2 cuv=vUv-vec2(uTime*.00035,0.); // clouds drift ~3% faster than the ground, same direction (NOT 10x)
        float cl=texture2D(uCloud,cuv).r;
        float sh=texture2D(uCloud,cuv+vec2(-.003,.0018)).r; // cloud shadow, offset toward the sun
        float ocean=texture2D(uSpec,vUv).r;
        float lit=smoothstep(-.1,.3,d);
        vec3 col=day*(smoothstep(-.06,.5,d)*1.2+.008)*(1.-sh*.38*lit);
        // Preserve the source Earth's color; add only reflected sunlight.
        vec3 H=normalize(L+V);float gl=pow(max(dot(N,H),0.),10.)*ocean*(1.-cl); // broad faint sheen only: the tight 140-power glint read as a fixed white dot (Austin 10-12)
        col+=vec3(.85,.9,1.)*gl*.035*lit;
        // clouds on top, lit by the sun
        col=mix(col,vec3(1.)*(max(d,0.)*1.25+.02),cl*.92*smoothstep(-.25,.15,d)+cl*.05);
        // city lights on the night side, dimmed under clouds, warm
        float nightW=1.-smoothstep(-.22,.08,d);
        col+=night*2.6*nightW*(1.-cl*.8);col+=day*vec3(.25,.4,.8)*.035*nightW;
        // twilight band (warm scattering at the terminator)
        float tw=exp(-pow((d-.02)*9.,2.));col+=vec3(1.,.5,.25)*tw*.01*(1.-cl*.4);
        // inner scattering limb
        float f=pow(1.-max(dot(N,V),0.),3.2);
        col+=uAtmo*f*(.008+.12*smoothstep(-.3,.6,d));
        gl_FragColor=vec4(col,1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
  const earth = new THREE.Mesh(new THREE.SphereGeometry(1, small ? 96 : 128, small ? 96 : 128), earthMat);
  spin.add(earth);


  /* optional: live routes between cities (pulses travel the arcs) */
  if (arcsOn) {
    const ll = (lat, lon, r = 1.004) => { const p = (90 - lat) * Math.PI / 180, t = (lon + 180) * Math.PI / 180; return new THREE.Vector3(-r * Math.sin(p) * Math.cos(t), r * Math.cos(p), r * Math.sin(p) * Math.sin(t)); };
    const C = { sf: [37.77, -122.42], ny: [40.71, -74], ld: [51.5, -0.12], mb: [19.07, 72.88], tk: [35.68, 139.69], sy: [-33.86, 151.2], sp: [-23.55, -46.63], sg: [1.35, 103.8], lg: [6.52, 3.37], dx: [25.2, 55.27] };
    const R = [["sf", "ny"], ["sf", "tk"], ["ny", "ld"], ["ld", "mb"], ["mb", "sg"], ["sg", "sy"], ["sf", "sp"], ["ld", "lg"], ["dx", "mb"], ["tk", "sg"], ["ny", "sp"], ["ld", "dx"]];
    const arcMat = new THREE.ShaderMaterial({ ...ADD, transparent: true, depthWrite: false, uniforms: { uT: { value: 0 }, uC: { value: accent } },
      vertexShader: "attribute float aU;attribute float aS;varying float vU;varying float vS;void main(){vU=aU;vS=aS;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}",
      fragmentShader: "uniform float uT;uniform vec3 uC;varying float vU;varying float vS;void main(){float h=fract(uT*.22+vS);float d=abs(vU-h);float pulse=exp(-d*d*900.);float base=.42*smoothstep(0.,.06,vU)*smoothstep(1.,.94,vU);gl_FragColor=vec4(uC*(base+pulse*3.)+vec3(1.)*pulse*.8,1.);}" });
    const dotTex = flareDot();
    R.forEach(([a, b], i) => {
      const A = ll(...C[a]), B = ll(...C[b]), mid = A.clone().add(B).multiplyScalar(.5), lift = 1 + A.distanceTo(B) * .32;
      mid.normalize().multiplyScalar(lift);
      const curve = new THREE.QuadraticBezierCurve3(A, mid, B), pts = curve.getPoints(80);
      const g = new THREE.BufferGeometry().setFromPoints(pts);
      g.setAttribute("aU", new THREE.BufferAttribute(new Float32Array(pts.map((_, k) => k / 80)), 1));
      g.setAttribute("aS", new THREE.BufferAttribute(new Float32Array(81).fill(i * .37 % 1), 1));
      spin.add(new THREE.Line(g, arcMat));
    });
    Object.keys(C).forEach((k) => { const d = new THREE.Sprite(new THREE.SpriteMaterial({ map: dotTex, color: accent, transparent: true, depthWrite: false, ...ADD })); d.position.copy(ll(...C[k], 1.012)); d.scale.setScalar(.045); spin.add(d); });
    scene.userData.arcMat = arcMat;
  }

  /* outer atmosphere glow */
  const atmo = new THREE.Mesh(new THREE.SphereGeometry(1.018, 96, 96), new THREE.ShaderMaterial({
    transparent: true, side: THREE.BackSide, depthWrite: false, ...ADD,
    uniforms: { uSun: { value: SUN.clone() }, uC: { value: new THREE.Color(0x5aa8ff) }, uC2: { value: new THREE.Color(0x9fe0ff) } },
    vertexShader: "varying vec3 vNv;varying vec3 vNw;void main(){vNv=normalize(normalMatrix*normal);vNw=normalize(mat3(modelMatrix)*normal);gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}",
    fragmentShader: "uniform vec3 uSun,uC,uC2;varying vec3 vNv;varying vec3 vNw;void main(){float i=pow(clamp(.7+dot(vNv,vec3(0.,0.,1.))*-1.,0.,1.),3.2);float s=smoothstep(-.45,.7,dot(vNw,normalize(uSun)));vec3 c=mix(uC,uC2,s);gl_FragColor=vec4(c*i*(.05+.8*s),1.);}",
  }));
  scene.add(atmo);

  /* sun glare just off-frame (tiny, warm) */
  {
    const gc = document.createElement("canvas"); gc.width = gc.height = 128; const gx = gc.getContext("2d"), gg = gx.createRadialGradient(64, 64, 0, 64, 64, 64);
    gg.addColorStop(0, "rgba(255,248,235,1)"); gg.addColorStop(.12, "rgba(255,230,200,.5)"); gg.addColorStop(.4, "rgba(255,190,140,.08)"); gg.addColorStop(1, "rgba(255,180,120,0)");
    gx.fillStyle = gg; gx.fillRect(0, 0, 128, 128);
    const sun = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(gc), transparent: true, depthWrite: false, ...ADD, opacity: 0.55 }));
    sun.position.copy(SUN).multiplyScalar(40); sun.scale.setScalar(16); scene.add(sun);
  }

  /* rocks: Blender turntables on tilted orbits + a thin debris belt */
  const rocks = [];
  if (rocksOn) {
    const ROCKS = [
      { sheet: "rock1", size: .62, r: 1.62, inc: 7, roll: -22, speed: .1, phase: 0.6, spin: 14 },
      { sheet: "r2", size: .40, r: 1.86, inc: 15, roll: 12, speed: .078, phase: 2.3, spin: 11 },
      { sheet: "r3", size: .30, r: 1.42, inc: -10, roll: 30, speed: .14, phase: 4.1, spin: 18 },
      { sheet: "r4", size: .22, r: 2.08, inc: 21, roll: -8, speed: .06, phase: 5.3, spin: 9 },
      { sheet: "r5", size: .15, r: 1.30, inc: -17, roll: -36, speed: .18, phase: 1.2, spin: 22 },
    ];
    const ringGeo = (r) => { const p = []; for (let k = 0; k <= 200; k++) { const t = (k / 200) * Math.PI * 2; p.push(new THREE.Vector3(Math.cos(t) * r, 0, Math.sin(t) * r)); } return new THREE.BufferGeometry().setFromPoints(p); };
    const ringMat = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, ...ADD, uniforms: { uC: { value: new THREE.Color(0xa6adb5) }, uT: { value: 0 } },
      vertexShader: "varying float vZ;varying float vA;void main(){vec4 w=modelMatrix*vec4(position,1.);vZ=w.z;vA=atan(position.z,position.x);gl_Position=projectionMatrix*viewMatrix*w;}",
      fragmentShader: "uniform vec3 uC;uniform float uT;varying float vZ;varying float vA;void main(){float front=smoothstep(-2.2,1.8,vZ);float chase=pow(max(0.,sin(vA*1.-uT*.6)),24.);gl_FragColor=vec4(uC*(.03+.1*front+chase*.55*front),1.);}",
    });
    for (const o2 of ROCKS) {
      const t = tex(o2.sheet + ".webp", 1, srgb); t.repeat.set(1 / 6, 1 / 6);
      const spr = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, transparent: true, depthWrite: false, alphaTest: 0.02 }));
      const plane = new THREE.Group(); plane.rotation.set((o2.inc * Math.PI) / 180, 0, (o2.roll * Math.PI) / 180); scene.add(plane); plane.add(spr);
      const ring = new THREE.Line(ringGeo(o2.r), ringMat); plane.add(ring);
      rocks.push({ o: o2, spr, tex: t, frame: -1 });
    }
    scene.userData.ringMat = ringMat;
    // debris belt
    const n = small ? 180 : 340, bp = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) { const a = Math.random() * Math.PI * 2, r = 1.55 + Math.random() * 0.55 + (Math.random() - .5) * .1; bp.set([Math.cos(a) * r, (Math.random() - .5) * .05, Math.sin(a) * r], i * 3); }
    const bg = new THREE.BufferGeometry(); bg.setAttribute("position", new THREE.BufferAttribute(bp, 3));
    const belt = new THREE.Points(bg, new THREE.PointsMaterial({ color: 0x9a9da4, size: 0.016, map: flareDot(), alphaTest: .05, sizeAttenuation: true, transparent: true, opacity: .5, depthWrite: false }));
    belt.rotation.set(0.12, 0, -0.38); scene.add(belt); scene.userData.belt = belt;
  }

  /* meteors burning up in the atmosphere (3D): a camera-facing ribbon with a hot head and a flash at the limb */
  const mets = [];
  const flareTex = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const x = c.getContext("2d"), g = x.createRadialGradient(32, 32, 0, 32, 32, 32); g.addColorStop(0, "rgba(255,255,255,1)"); g.addColorStop(.22, "rgba(255,214,170,.65)"); g.addColorStop(.55, "rgba(255,120,60,.12)"); g.addColorStop(1, "rgba(255,90,40,0)"); x.fillStyle = g; x.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
  const ribMat = new THREE.ShaderMaterial({ ...ADD, transparent: true, depthWrite: false, side: THREE.DoubleSide,
    uniforms: { uHot: { value: 0 }, uB: { value: 1 } },
    vertexShader: "attribute float aT;varying float vT;varying float vS;void main(){vT=aT;vS=position.z;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}",
    fragmentShader: "uniform float uHot;uniform float uB;varying float vT;void main(){float f=pow(1.-vT,2.2);vec3 hotc=mix(vec3(.85,.93,1.),vec3(1.,.45,.16),uHot*(1.-vT*.6));gl_FragColor=vec4(hotc*f*uB,1.);}" });
  const camDir = new THREE.Vector3(), side = new THREE.Vector3(), tmpV = new THREE.Vector3();
  function spawnMeteor() {
    camera.getWorldDirection(camDir);
    const up = new THREE.Vector3(0, 1, 0), right = new THREE.Vector3().crossVectors(camDir, up).normalize(), up2 = new THREE.Vector3().crossVectors(right, camDir).normalize();
    const ang = Math.random() * Math.PI * 2, radial = right.clone().multiplyScalar(Math.cos(ang)).addScaledVector(up2, Math.sin(ang));
    const end = radial.clone().multiplyScalar(1.035).addScaledVector(camDir, -.12); // just in front of the limb
    const tangent = right.clone().multiplyScalar(-Math.sin(ang)).addScaledVector(up2, Math.cos(ang)).multiplyScalar(Math.random() < .5 ? 1 : -1);
    const start = end.clone().addScaledVector(tangent, 1.1 + Math.random() * .6).addScaledVector(radial, .55 + Math.random() * .35);
    const geo = new THREE.BufferGeometry(); const N = 12;
    geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(N * 2 * 3), 3));
    const at = new Float32Array(N * 2); for (let k = 0; k < N; k++) { at[k * 2] = at[k * 2 + 1] = k / (N - 1); } geo.setAttribute("aT", new THREE.BufferAttribute(at, 1));
    const idx = []; for (let k = 0; k < N - 1; k++) { const q = k * 2; idx.push(q, q + 1, q + 2, q + 1, q + 3, q + 2); } geo.setIndex(idx);
    const mat = ribMat.clone(); const rib = new THREE.Mesh(geo, mat); rib.frustumCulled = false; scene.add(rib);
    const head = new THREE.Sprite(new THREE.SpriteMaterial({ map: flareTex, transparent: true, depthWrite: false, ...ADD })); scene.add(head);
    mets.push({ start, end, life: 0, dur: 1.1 + Math.random() * .5, rib, head, N, sparks: [] });
  }
  function updateMeteors(dt) {
    for (let i = mets.length - 1; i >= 0; i--) {
      const M = mets[i]; M.life += dt; const p = M.life / M.dur;
      if (p > 1.35) { scene.remove(M.rib); scene.remove(M.head); M.rib.geometry.dispose(); M.rib.material.dispose(); M.head.material.dispose(); mets.splice(i, 1); continue; }
      const hp = Math.min(1, p), ease = hp * hp * (3 - 2 * hp) * .35 + hp * .65;
      const hot = THREE.MathUtils.clamp((hp - .45) / .5, 0, 1);
      const b = p <= 1 ? lerp(.3, 1.1, hp) + (hp > .88 ? .9 : 0) : Math.max(0, 1 - (p - 1) * 3.2);
      const head = M.start.clone().lerp(M.end, ease), len = .28 + hp * .42;
      const dir = M.end.clone().sub(M.start).normalize();
      camera.getWorldDirection(camDir); side.crossVectors(dir, camDir).normalize();
      const pos = M.rib.geometry.attributes.position;
      for (let k = 0; k < M.N; k++) {
        const f = k / (M.N - 1); tmpV.copy(head).addScaledVector(dir, -len * f * (p <= 1 ? 1 : Math.max(0, 1.6 - p)));
        const w = (.012 + hot * .012) * (1 - f * .85);
        pos.setXYZ(k * 2, tmpV.x + side.x * w, tmpV.y + side.y * w, tmpV.z + side.z * w);
        pos.setXYZ(k * 2 + 1, tmpV.x - side.x * w, tmpV.y - side.y * w, tmpV.z - side.z * w);
      }
      pos.needsUpdate = true; M.rib.material.uniforms.uHot.value = hot; M.rib.material.uniforms.uB.value = b;
      const flash = hp > .88 && p < 1.08;
      M.head.position.copy(head); M.head.scale.setScalar((.07 + hot * .08 + (flash ? .22 : 0)) * Math.max(.25, Math.min(1.4, b))); M.head.material.opacity = Math.min(1, b);
      M.head.material.color.setRGB(1, lerp(1, .62, hot), lerp(1, .4, hot));
    }
  }

  /* size, visibility, input */
  function resize() {
    const w = wrap.clientWidth || 300, h = wrap.clientHeight || w; renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.fov = 42; camera.updateProjectionMatrix();
    // earth fills a set share of the narrow side (closer on phones), always fully in frame
    const fill = Math.min(.92, (w < 600 ? (+o.fillPhone || .50) : (+o.fill || .50)) * (+o.zoom || 1));
    const tv = Math.tan((camera.fov * Math.PI) / 360), tn = w < h ? tv * camera.aspect : tv;
    const z = 1 / Math.sin(Math.atan(fill * tn)); camBase.set(0, z * .1, z);
  }
  resize(); new ResizeObserver(resize).observe(wrap);
  let visible = true; new IntersectionObserver((e) => { visible = e[0].isIntersecting; }, { rootMargin: "160px" }).observe(wrap);
  let drag = null, vel = 0, px = 0, py = 0;
  wrap.style.touchAction = "pan-y";
  wrap.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, t: performance.now() }; });
  addEventListener("pointerup", () => { drag = null; });
  addEventListener("pointercancel", () => { drag = null; vel = 0; });
  addEventListener("pointermove", (e) => {
    const r = wrap.getBoundingClientRect(); px = ((e.clientX - r.left) / r.width - .5); py = ((e.clientY - r.top) / r.height - .5);
    if (drag) { const dx = e.clientX - drag.x; drag.x = e.clientX; vel = dx * .0045; spin.rotation.y += vel; }
  }, { passive: true });

  function ready() { cv.style.opacity = "1"; wrap.classList.add("space-ready"); if (REDUCE) { render(0, 0); setTimeout(() => render(0, 0), 1500); setTimeout(() => render(0, 0), 4000); } }
  let t0 = performance.now(), last = t0, nextMet = /[?&]met=1/.test(location.search) ? .3 : 2.5;
  const v = new THREE.Vector3();
  function render(t, dt) {
    spin.rotation.y += dt * SPIN + (drag ? 0 : vel); vel *= .94; // one turn per ~75s (Austin 10-12: yes, spin)
    U.uTime.value = t; scene.userData.starMat.uniforms.uTime.value = t;
    if (scene.userData.ringMat) scene.userData.ringMat.uniforms.uT.value = t;
    if (scene.userData.arcMat) scene.userData.arcMat.uniforms.uT.value = t;
    if (scene.userData.belt) scene.userData.belt.rotation.y = t * .02;
    camera.position.set(camBase.x + px * .35, camBase.y - py * .22, camBase.z); camera.lookAt(0, 0, 0);
    for (const R of rocks) {
      const a = t * R.o.speed + R.o.phase; R.spr.position.set(Math.cos(a) * R.o.r, 0, Math.sin(a) * R.o.r);
      const f = Math.floor(t * R.o.spin) % 36;
      if (f !== R.frame) { R.frame = f; R.tex.offset.set((f % 6) / 6, 1 - (Math.floor(f / 6) + 1) / 6); }
      R.spr.getWorldPosition(v); const near = THREE.MathUtils.clamp((v.z + 2) / 4, 0, 1);
      R.spr.scale.setScalar(R.o.size * (.8 + near * .32));
      // sun side brighter, far side dimmer
      const sh = .95 + .7 * THREE.MathUtils.clamp(v.clone().normalize().dot(SUN) * .5 + .5, 0, 1);
      R.spr.material.color.setScalar(sh);
    }
    if (!REDUCE) { nextMet -= dt; if (nextMet <= 0) { spawnMeteor(); nextMet = /[?&]met=1/.test(location.search) ? .6 : 3.5 + Math.random() * 5; } updateMeteors(dt); }
    renderer.render(scene, camera);
  }
  if (REDUCE) return;
  function tick(now) {
    requestAnimationFrame(tick);
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    if (!visible || document.hidden) return;
    render((now - t0) / 1000, dt);
  }
  requestAnimationFrame(tick);
}

/* ------------------------------------------------------------------ SKY (2D): stars, nebula haze, shooting stars */
export function mountSky(canvas, opts = {}) {
  if (!canvas || canvas.__space) return; canvas.__space = 1;
  const met = opts.met || null, mctx = met ? met.getContext("2d") : null;
  let ctx = canvas.getContext("2d"); const sctx0 = ctx, dpr = Math.min(devicePixelRatio || 1, 2), acc = hexRgb(opts.accent);
  let W = 0, H = 0, stars = [], mets = [], next = 1.0, on = true, haze = null, scrollK = 0;
  const density = +opts.density || 4200, every = +opts.every || 2.6, band = +opts.band || 1;
  function size() {
    const r = canvas.getBoundingClientRect(); W = Math.max(1, r.width); H = Math.max(1, r.height);
    canvas.width = W * dpr; canvas.height = H * dpr; sctx0.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (met) { met.width = W * dpr; met.height = H * dpr; mctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    stars = []; const n = Math.round((W * H) / density);
    for (let i = 0; i < n; i++) {
      const layer = Math.random() < .7 ? 0 : Math.random() < .75 ? 1 : 2;
      stars.push({ x: Math.random() * W, y: Math.random() * H * band, l: layer, r: layer === 2 ? 1.1 + Math.random() * .9 : layer === 1 ? .6 + Math.random() * .5 : .3 + Math.random() * .45, p: Math.random() * 6.3, s: .4 + Math.random() * 1.8, c: Math.random() < .12 ? "200,220,255" : Math.random() < .07 ? "255,214,180" : "255,250,240" });
    }
    // nebula haze baked once per size
    haze = document.createElement("canvas"); haze.width = Math.ceil(W / 2); haze.height = Math.ceil(H / 2);
    const hx = haze.getContext("2d");
    const blob = (x, y, rr, rgb, a) => { const g = hx.createRadialGradient(x, y, 0, x, y, rr); g.addColorStop(0, `rgba(${rgb},${a})`); g.addColorStop(1, `rgba(${rgb},0)`); hx.fillStyle = g; hx.fillRect(0, 0, haze.width, haze.height); };
    const hw = haze.width, hh = haze.height;
    // Neutral space backdrop: no green/purple wash over the natural Earth.
    blob(hw * .55, hh * .45, hw * .35, "180,190,205", .015);
  }
  function spawn(at) {
    const fromLeft = Math.random() < .5, ang = (fromLeft ? 1 : -1) * (0.38 + Math.random() * 0.32);
    const big = Math.random() < .12, sp = W * (0.5 + Math.random() * 0.45) * (big ? .8 : 1);
    mets.push({ x: at ? at.x : fromLeft ? Math.random() * W * .6 : W * .4 + Math.random() * W * .6, y: at ? at.y : Math.random() * H * .3,
      vx: Math.sin(ang) * sp, vy: Math.cos(Math.abs(ang)) * sp * .55, life: 0, dur: (big ? 1.5 : .9) + Math.random() * .9, len: (big ? 200 : 90) + Math.random() * 150, w: big ? 1.8 : 1,
      flareAt: .6 + Math.random() * .18, sparks: [], train: [] });
  }
  function draw(dt) {
    ctx.clearRect(0, 0, W, H);
    if (haze) ctx.drawImage(haze, 0, 0, W, H);
    const t = performance.now() / 1000;
    for (const s of stars) {
      const a = Math.max(0, Math.min(1, .5 + .45 * Math.sin(t * s.s + s.p)));
      const y = s.y - scrollK * (s.l + 1) * 14;
      ctx.fillStyle = `rgba(${s.c},${a * (s.l === 0 ? .7 : 1)})`;
      ctx.beginPath(); ctx.arc(s.x, ((y % H) + H) % H, s.r, 0, 6.283); ctx.fill();
      if (s.l === 2 && a > .8) { ctx.fillStyle = `rgba(${s.c},${(a - .8) * 1.2})`; ctx.fillRect(s.x - s.r * 3, ((y % H) + H) % H - .3, s.r * 6, .6); ctx.fillRect(s.x - .3, ((y % H) + H) % H - s.r * 3, .6, s.r * 6); }
    }
    next -= dt; if (next <= 0 && !REDUCE) { spawn(); if (Math.random() < .3) spawn(); next = every * (.45 + Math.random() * .8); }
    if (mctx) { mctx.clearRect(0, 0, W, H); ctx = mctx; }
    ctx.globalCompositeOperation = "lighter";
    for (let m = mets.length - 1; m >= 0; m--) {
      const M = mets[m]; M.life += dt; const p = M.life / M.dur;
      if (p > 1.7) { mets.splice(m, 1); continue; }
      if (p <= 1) { M.x += M.vx * dt; M.y += M.vy * dt; M.train.push({ x: M.x, y: M.y }); }
      const b = p < M.flareAt ? lerp(.22, .85, p / M.flareAt) : p < M.flareAt + .08 ? 1.6 : p <= 1 ? lerp(1, 0, (p - M.flareAt - .08) / (1 - M.flareAt - .08)) : 0;
      const hot = p < M.flareAt ? 0 : Math.min(1, (p - M.flareAt) / .25);
      const cr = Math.round(lerp(225, 255, hot)), cg = Math.round(lerp(238, 96, hot)), cb = Math.round(lerp(255, 40, hot));
      const vl = Math.hypot(M.vx, M.vy), ux = M.vx / vl, uy = M.vy / vl, L = M.len * (p <= 1 ? Math.min(1, p * 3) : 0);
      if (b > 0) {
        // soft outer glow pass + crisp core pass
        for (const [wMul, aMul] of [[4.5, .12], [1, 1]]) {
          const g = ctx.createLinearGradient(M.x, M.y, M.x - ux * L, M.y - uy * L);
          g.addColorStop(0, `rgba(${cr},${cg},${cb},${Math.min(1, b) * aMul})`);
          g.addColorStop(.25, `rgba(${cr},${Math.round(cg * .8)},${Math.round(cb * .7)},${b * .35 * aMul})`);
          g.addColorStop(1, "rgba(120,140,200,0)");
          ctx.strokeStyle = g; ctx.lineWidth = (1.1 + b * 1.1) * M.w * wMul; ctx.lineCap = "round";
          ctx.beginPath(); ctx.moveTo(M.x, M.y); ctx.lineTo(M.x - ux * L, M.y - uy * L); ctx.stroke();
        }
        const fl = p > M.flareAt && p < M.flareAt + .1, hr = (1.2 + b * (fl ? 7 : 2.2)) * M.w, hg = ctx.createRadialGradient(M.x, M.y, 0, M.x, M.y, hr * 3);
        hg.addColorStop(0, `rgba(255,255,255,${Math.min(1, b)})`); hg.addColorStop(.3, `rgba(${cr},${cg},${cb},${b * .5})`); hg.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
        ctx.fillStyle = hg; ctx.beginPath(); ctx.arc(M.x, M.y, hr * 3, 0, 6.283); ctx.fill();
        if (fl) { ctx.fillStyle = `rgba(255,240,225,${b * .25})`; ctx.fillRect(M.x - hr * 7, M.y - .5, hr * 14, 1); }
      }
      if (p > M.flareAt && !M.shed) { M.shed = 1; for (let k = 0; k < 5 + ((Math.random() * 5) | 0); k++) M.sparks.push({ x: M.x, y: M.y, vx: M.vx * (.25 + Math.random() * .35) + (Math.random() - .5) * 70, vy: M.vy * (.25 + Math.random() * .35) + (Math.random() - .5) * 70, l: 0, d: .25 + Math.random() * .5 }); }
      for (let q = M.sparks.length - 1; q >= 0; q--) {
        const S = M.sparks[q]; S.l += dt; if (S.l > S.d) { M.sparks.splice(q, 1); continue; }
        S.vy += 30 * dt; S.x += S.vx * dt; S.y += S.vy * dt; const sa = 1 - S.l / S.d;
        ctx.fillStyle = `rgba(255,${Math.round(lerp(150, 50, 1 - sa))},40,${sa})`; ctx.beginPath(); ctx.arc(S.x, S.y, .6 + sa, 0, 6.283); ctx.fill();
      }
      if (M.train.length > 2) {
        ctx.strokeStyle = "rgba(140,170,255,.06)"; ctx.lineWidth = 1;
        ctx.globalAlpha = Math.max(0, 1 - Math.max(0, p - .9) * 1.3);
        ctx.beginPath(); ctx.moveTo(M.train[0].x, M.train[0].y); for (let z = 1; z < M.train.length; z++) ctx.lineTo(M.train[z].x, M.train[z].y); ctx.stroke(); ctx.globalAlpha = 1;
      }
    }
    ctx.globalCompositeOperation = "source-over"; ctx = sctx0;
  }
  size(); new ResizeObserver(size).observe(canvas);
  addEventListener("scroll", () => { scrollK = Math.min(40, scrollY / 120); }, { passive: true });
  const host = opts.clickHost || canvas.parentElement;
  if (host) host.addEventListener("click", (e) => { if (e.target.closest("a,button,input,textarea,select,iframe,label")) return; const r = canvas.getBoundingClientRect(); spawn({ x: e.clientX - r.left, y: e.clientY - r.top }); });
  new IntersectionObserver((e) => { on = e[0].isIntersecting; }).observe(canvas);
  let last = performance.now();
  if (REDUCE) { draw(0); return; }
  (function loop(now) { requestAnimationFrame(loop); const dt = Math.min(.05, (now - last) / 1000); last = now; if (on && !document.hidden) draw(dt); })(last);
}

/* auto-mount from data attributes */
function boot() {
  document.querySelectorAll("[data-space-globe]").forEach((el) => mountGlobe(el, { base: el.dataset.base, accent: el.dataset.accent, rocks: el.dataset.rocks !== "0", arcs: el.dataset.arcs, zoom: el.dataset.zoom, fill: el.dataset.fill, fillPhone: el.dataset.fillPhone, startRot: el.dataset.rot }));
  document.querySelectorAll("canvas[data-space-sky]").forEach((c) => mountSky(c, { accent: c.dataset.accent, density: c.dataset.density, every: c.dataset.every, band: c.dataset.band, met: c.dataset.met ? document.querySelector(c.dataset.met) : null, clickHost: c.dataset.host ? document.querySelector(c.dataset.host) : null }));
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
// pages that render their markup client-side (the hub's template runtime) add hosts later
let bootQ = 0;
new MutationObserver(() => { if (!bootQ) bootQ = requestAnimationFrame(() => { bootQ = 0; boot(); }); }).observe(document.documentElement, { childList: true, subtree: true });
