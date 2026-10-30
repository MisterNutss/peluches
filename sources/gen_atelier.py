"""Construit l'atelier (atelier-peluches.html, page publiée) et la page 3D transparente (site-peluches/index.html) à partir de plush_model.js."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
atelier_out, viewer_out = sys.argv[1], sys.argv[2]
site_out = sys.argv[3] if len(sys.argv) > 3 else None
model = open(os.path.join(HERE, "plush_model.js"), encoding="utf-8").read()

VIEWER_HEAD = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Peluche</title>
<style>html,body{margin:0;height:100%;background:transparent;overflow:hidden}canvas{display:block;width:100%;height:100%;touch-action:none;cursor:grab}canvas.drag{cursor:grabbing}</style>
</head>
<body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
"""

VIEWER_TAIL = r"""
// Page 3D : la peluche est décrite dans l'adresse (?p=...). Glisser : tourner. Molette ou deux doigts : zoomer. Double-clic : remettre en place.
// Option : &tourne=non pour qu'elle ne tourne pas toute seule.
const q=new URLSearchParams(location.search);
const cfg=(q.get('p')&&PL.decode(q.get('p')))||PL.clean(PL.PRESETS.pompier);
if(cfg.n)document.title=cfg.n;
const scene=new THREE.Scene(),cam=new THREE.PerspectiveCamera(22,1,0.1,500);
const r=new THREE.WebGLRenderer({antialias:true,alpha:true});r.setClearColor(0x000000,0);r.setPixelRatio(Math.min(2,window.devicePixelRatio||1));r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;document.body.appendChild(r.domElement);
PL.setup(r);const camFill=PL.lights(scene),P=PL.build(cfg);scene.add(P.group);
const reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches,autoSpin=q.get('tourne')!=='non'&&!reduce;
const START={ry:-0.25,el:0.24,zoom:1.05};let ry=START.ry,el=START.el,zoom=START.zoom,idle=0;
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
function fit(){const w=window.innerWidth||400,h=window.innerHeight||400;r.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();}
fit();window.addEventListener('resize',fit);
const cvs=r.domElement,pts=new Map();
cvs.addEventListener('pointerdown',e=>{cvs.setPointerCapture(e.pointerId);pts.set(e.pointerId,[e.clientX,e.clientY]);cvs.classList.add('drag');idle=performance.now();});
cvs.addEventListener('pointermove',e=>{const p=pts.get(e.pointerId);if(!p)return;idle=performance.now();
if(pts.size===2){const[a,b]=[...pts.values()],d0=Math.hypot(a[0]-b[0],a[1]-b[1]);pts.set(e.pointerId,[e.clientX,e.clientY]);const[c,d]=[...pts.values()],d1=Math.hypot(c[0]-d[0],c[1]-d[1]);if(d0>0&&d1>0)zoom=clamp(zoom*d0/d1,0.6,1.8);return;}
ry+=(e.clientX-p[0])*0.01;el=clamp(el+(e.clientY-p[1])*0.006,-0.15,0.8);pts.set(e.pointerId,[e.clientX,e.clientY]);});
const up=e=>{pts.delete(e.pointerId);if(!pts.size)cvs.classList.remove('drag');idle=performance.now();};
cvs.addEventListener('pointerup',up);cvs.addEventListener('pointercancel',up);
cvs.addEventListener('wheel',e=>{e.preventDefault();zoom=clamp(zoom*Math.exp(e.deltaY*0.001),0.6,1.8);idle=performance.now();},{passive:false});
cvs.addEventListener('dblclick',()=>{ry=START.ry;el=START.el;zoom=START.zoom;});
(function loop(now){now=now||0;if(autoSpin&&!pts.size&&now-idle>2500)ry+=0.006;
P.group.rotation.y=ry;PL.aim(cam,P.fit,el,zoom,camFill);r.render(scene,cam);requestAnimationFrame(loop);})();
</script>
</body>
</html>
"""

ATELIER = r"""<title>Atelier peluches</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap">
<style>
/* Layout: a toy-maker's studio — the plush on a big turntable stage pinned on the left, a tabbed workbench on the right (photos, réglages, lien); on phones the stage sits on top of the tabs. */
:root{
  --bg:#f2eff6; --surface:#ffffff; --surface-2:#f7f4fa; --fg:#251b30; --muted:#6c6279; --line:rgba(37,27,48,.11);
  --accent:#d63a74; --accent-soft:#fbe3ec; --mint:#178a84; --on-accent:#ffffff; --stage-a:#ffffff; --stage-b:#ece7f3;
  --shadow:0 1px 2px rgba(37,27,48,.05),0 10px 28px rgba(37,27,48,.08);
  --display:"Fredoka","Trebuchet MS",system-ui,sans-serif; --body:"Nunito",system-ui,-apple-system,"Segoe UI",sans-serif; --mono:"DM Mono",ui-monospace,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#15111b; --surface:#1f1927; --surface-2:#1a1521; --fg:#f3eef8; --muted:#a79cb4; --line:rgba(243,238,248,.11);
  --accent:#ff6c9f; --accent-soft:#3a1d2a; --mint:#4fc7bf; --on-accent:#1a0c12; --stage-a:#2a2234; --stage-b:#231c2c;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 28px rgba(0,0,0,.35); color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#15111b; --surface:#1f1927; --surface-2:#1a1521; --fg:#f3eef8; --muted:#a79cb4; --line:rgba(243,238,248,.11);
  --accent:#ff6c9f; --accent-soft:#3a1d2a; --mint:#4fc7bf; --on-accent:#1a0c12; --stage-a:#2a2234; --stage-b:#231c2c;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 28px rgba(0,0,0,.35); color-scheme:dark}
[hidden]{display:none!important}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.5}
.app{max-width:1360px;margin:0 auto;padding-block:20px 32px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:18px}
.top{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px}
.brand{display:flex;align-items:center;gap:12px;min-width:0}
.logo{width:46px;height:46px;flex:none}
h1{font-family:var(--display);font-weight:700;font-size:clamp(26px,3.4vw,34px);line-height:1;margin:0;letter-spacing:-.01em}
.brand p{margin:4px 0 0;color:var(--muted);font-size:14px;max-width:46ch}
.steps{list-style:none;margin:0;padding:4px;display:flex;gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:999px;box-shadow:var(--shadow)}
.steps button{font:700 14px/1 var(--body);border:0;background:none;color:var(--muted);padding:8px 14px 8px 8px;border-radius:999px;cursor:pointer;display:flex;gap:8px;align-items:center}
.steps .n{font-family:var(--mono);font-size:12px;width:22px;height:22px;border-radius:50%;display:grid;place-items:center;background:var(--surface-2);color:var(--muted)}
.steps li.on button{background:var(--accent);color:var(--on-accent)}
.steps li.on .n{background:rgba(255,255,255,.28);color:var(--on-accent)}
.studio{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:18px;align-items:start}
.viewer{position:sticky;top:calc(env(safe-area-inset-top,0px) + 16px);display:grid;gap:10px;min-width:0}
@media (max-width:920px){.studio{grid-template-columns:minmax(0,1fr)}.viewer{position:static}}
.stage{position:relative;width:100%;aspect-ratio:1;max-height:calc(100vh - 160px);min-height:320px;border-radius:24px;overflow:hidden;cursor:grab;touch-action:pan-y;border:1px solid var(--line);box-shadow:var(--shadow);
  background:repeating-conic-gradient(var(--stage-a) 0 25%,var(--stage-b) 0 50%) 0 0/28px 28px}
.stage.drag{cursor:grabbing}
.stage canvas{display:block;width:100%;height:100%}
.stage-bar{position:absolute;top:12px;left:12px;right:12px;display:flex;flex-wrap:wrap;gap:6px;justify-content:space-between;pointer-events:none}
.grp{display:flex;gap:2px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:4px;pointer-events:auto;box-shadow:var(--shadow)}
.grp button{font:700 13px/1 var(--body);border:0;background:none;color:var(--fg);padding:8px 12px;border-radius:999px;cursor:pointer}
.grp button:hover{background:var(--surface-2)}
.grp button[aria-pressed="true"]{background:var(--accent);color:var(--on-accent)}
.stage-status{position:absolute;left:12px;right:12px;bottom:12px;margin:0;font-size:13px;font-weight:600;color:var(--fg);background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:9px 12px;box-shadow:var(--shadow);pointer-events:none}
.stage-status:empty{display:none}
.quick{display:flex;gap:8px;align-items:center;min-width:0}
.quick input{flex:1}
.panel{display:grid;gap:14px;min-width:0}
.tabs{display:flex;flex-wrap:wrap;gap:4px;overflow-x:auto;scrollbar-width:none;padding:4px;background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow)}
.tabs::-webkit-scrollbar{display:none}
.tabs button{font:700 14px/1 var(--body);border:0;background:none;color:var(--muted);padding:10px 14px;border-radius:12px;cursor:pointer;white-space:nowrap}
.tabs button:hover{color:var(--fg);background:var(--surface-2)}
.tabs button[aria-selected="true"]{background:var(--accent-soft);color:var(--accent)}
.tabpanel,#settings{display:grid;gap:14px;min-width:0}
.card{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:18px 20px;display:grid;gap:12px;min-width:0;box-shadow:var(--shadow)}
h2{font-family:var(--display);font-weight:600;font-size:19px;line-height:1.2;margin:0;color:var(--fg)}
label{font-size:14px;color:var(--muted);font-weight:700}
input[type=text],input[type=url],select{font:16px var(--body);padding:10px 12px;border-radius:12px;border:1px solid var(--line);background:var(--surface-2);color:var(--fg);width:100%;min-width:0;box-sizing:border-box}
input[readonly]{font-family:var(--mono);font-size:13px}
input.example{color:var(--muted)}
input[type=color]{width:52px;height:40px;padding:3px;border-radius:12px;border:1px solid var(--line);background:var(--surface-2);cursor:pointer;flex:none}
input[type=range]{width:100%;accent-color:var(--accent)}
input:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px 16px}
@media (max-width:560px){.fields{grid-template-columns:minmax(0,1fr)}}
.field{display:grid;gap:6px;align-content:start;min-width:0}
.field.wide{grid-column:1/-1}
.colorrow,.row{display:flex;gap:8px;align-items:center;min-width:0;flex-wrap:wrap}
.rangehead{justify-content:space-between;flex-wrap:nowrap}
.check{display:flex;gap:8px;align-items:center;color:var(--fg);font-size:15px;font-weight:600;cursor:pointer}
.check input{width:18px;height:18px;accent-color:var(--accent)}
.flags{display:flex;flex-wrap:wrap;gap:8px 18px}
.btn,.pip{font:700 14px/1 var(--body);padding:10px 14px;border-radius:12px;border:1px solid var(--line);background:var(--surface);color:var(--fg);cursor:pointer;white-space:nowrap;text-decoration:none}
.pip{font-size:13px;padding:8px 10px}
.btn:hover,.pip:hover{border-color:var(--accent)}
.btn:disabled{opacity:.45;cursor:not-allowed}
.no-photo .pip{display:none}
.pip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.cta{font:600 18px/1 var(--display);padding:14px 20px;border-radius:14px;border:0;background:var(--accent);color:var(--on-accent);cursor:pointer}
.cta:disabled{opacity:.45;cursor:not-allowed}
.seg{display:flex;flex-wrap:wrap;gap:6px}
.seg .btn[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.shots{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.shot{border:2px dashed var(--line);border-radius:16px;padding:10px;display:grid;justify-items:center;align-content:start;gap:8px;text-align:center;min-height:130px;min-width:0;background:var(--surface-2)}
.shot.over{border-color:var(--accent)}
.shot.has{border-style:solid}
.shot canvas{max-width:100%;height:auto;border-radius:10px;display:block}
.shot.picking canvas{cursor:crosshair;outline:3px solid var(--accent);outline-offset:2px}
.shot-l{font:600 14px/1 var(--display);color:var(--muted)}
.printimg{width:64px;height:64px;object-fit:contain;border-radius:10px;background:var(--surface-2);border:1px solid var(--line)}
.status{font-size:14px;margin:0;min-height:1.4em}
.help{font-size:14px;color:var(--muted);margin:0}
.pzlist{display:grid;gap:8px}
.pzrow{display:flex;gap:10px;align-items:center;min-width:0}
.pzrow label{flex:1;color:var(--fg);font-size:15px;min-width:0}
.setup ol{margin:0;padding-left:1.3em;display:grid;gap:8px;max-width:70ch}
code{font-family:var(--mono);font-size:13px;overflow-wrap:anywhere}
.err{color:var(--accent);font-size:14px;margin:0}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
</style>

<div class="app">
  <header class="top">
    <div class="brand">
      <svg class="logo" viewBox="0 0 48 48" aria-hidden="true"><circle cx="13" cy="12" r="7" fill="var(--accent)"/><circle cx="35" cy="12" r="7" fill="var(--accent)"/><circle cx="24" cy="26" r="17" fill="var(--accent)"/><circle cx="24" cy="31" r="7.5" fill="var(--accent-soft)"/><circle cx="17.5" cy="23" r="2.4" fill="var(--fg)"/><circle cx="30.5" cy="23" r="2.4" fill="var(--fg)"/><ellipse cx="24" cy="29" rx="2.6" ry="1.9" fill="var(--fg)"/><path d="M14 38 l4 2 M30 40 l4 -2" stroke="var(--on-accent)" stroke-width="1.6" stroke-dasharray="1.6 1.6" fill="none"/></svg>
      <div><h1>Atelier peluches</h1><p>Des peluches 3D sans fond, faites d'après une photo, pour tes items FiveM.</p></div>
    </div>
    <ol class="steps">
      <li data-step="photos"><button type="button"><span class="n">1</span>Photos</button></li>
      <li data-step="reglages"><button type="button"><span class="n">2</span>Réglages</button></li>
      <li data-step="lien"><button type="button"><span class="n">3</span>Lien</button></li>
    </ol>
  </header>
  <main class="studio">
    <section class="viewer" aria-label="Aperçu de la peluche">
      <div class="stage" id="stage" role="img" aria-label="Aperçu 3D de la peluche sur fond transparent">
        <div class="stage-bar">
          <div class="grp"><button type="button" id="v-front">Face</button><button type="button" id="v-side">Profil</button><button type="button" id="v-back">Dos</button></div>
          <div class="grp"><button type="button" id="v-spin" aria-pressed="false">Tourner</button></div>
        </div>
        <p class="stage-status" id="stage-status" aria-live="polite"></p>
      </div>
      <div class="quick"><input id="out2" type="text" readonly aria-label="Lien de cette peluche"><button class="btn" id="copy2" type="button">Copier le lien</button></div>
    </section>
    <section class="panel no-photo" id="right">
      <nav class="tabs" role="tablist" aria-label="Réglages de la peluche">
        <button type="button" role="tab" data-tab="photos">Photos</button>
        <button type="button" role="tab" data-tab="style">Style et pose</button>
        <button type="button" role="tab" data-tab="visage">Visage</button>
        <button type="button" role="tab" data-tab="tete">Tête</button>
        <button type="button" role="tab" data-tab="tenue">Tenue</button>
        <button type="button" role="tab" data-tab="accessoires">Accessoires</button>
        <button type="button" role="tab" data-tab="lien">Lien</button>
      </nav>
      <div id="settings">
        <div class="tabpanel" data-tab="photos" id="tab-photos">
          <section class="card">
            <h2>Photos de la personne</h2>
            <p class="help">Une photo de face suffit. Ajoute le côté et le dos pour une peluche plus fidèle : arrière de la coiffure, capuche, dos du vêtement.</p>
            <div class="shots" id="shots">
              <div class="shot" data-slot="face"><span class="shot-l">Face</span><canvas hidden></canvas><button class="btn" type="button">Choisir</button><input type="file" accept="image/*" hidden></div>
              <div class="shot" data-slot="cote"><span class="shot-l">Côté</span><canvas hidden></canvas><button class="btn" type="button">Choisir</button><input type="file" accept="image/*" hidden></div>
              <div class="shot" data-slot="dos"><span class="shot-l">Dos</span><canvas hidden></canvas><button class="btn" type="button">Choisir</button><input type="file" accept="image/*" hidden></div>
            </div>
            <p class="help">Glisse une photo sur une case ou colle-la avec Ctrl+V.</p>
            <div class="field"><label for="who">Sur les photos</label><select id="who"><option value="seule">Une seule personne</option><option value="gauche">La personne à gauche</option><option value="milieu">La personne au milieu</option><option value="droite">La personne à droite</option></select></div>
            <label class="check"><input type="checkbox" id="review" checked> Vérifier la ressemblance et corriger tout seul (plus lent, plus fidèle)</label>
            <button class="cta" id="analyse" type="button" disabled hidden>Créer la peluche avec la photo</button>
            <p class="status" id="ai-status" aria-live="polite">Ajoute une photo de face : la peluche se crée toute seule.</p>
            <div class="field" id="key-box" hidden><label for="api-key">Clé API Claude, pour la création automatique sur ce site</label><div class="row"><input id="api-key" type="password" placeholder="sk-ant-…" autocomplete="off" spellcheck="false"><button class="btn" id="key-save" type="button">Enregistrer</button></div>
            <p class="help">Facultatif. La clé reste dans ce navigateur et ne part que vers api.anthropic.com. Elle se crée sur platform.claude.com (facturée à l'usage, à part de l'abonnement Claude). Sans clé, règle la peluche à la main.</p></div>
          </section>
        </div>
        <div class="tabpanel" data-tab="style" id="tab-style" hidden>
          <section class="card"><h2>Modèles de départ</h2><div class="seg" id="presets"></div></section>
        </div>
        <div class="tabpanel" data-tab="visage" id="tab-visage" hidden></div>
        <div class="tabpanel" data-tab="tete" id="tab-tete" hidden></div>
        <div class="tabpanel" data-tab="tenue" id="tab-tenue" hidden></div>
        <div class="tabpanel" data-tab="accessoires" id="tab-accessoires" hidden></div>
        <div class="tabpanel" data-tab="lien" id="tab-lien" hidden>
          <section class="card">
            <h2>Lien pour ton item</h2>
            <div class="field"><label for="base">Adresse de ta page 3D</label><input id="base" type="url" placeholder="https://misternutss.github.io/peluches/" autocomplete="off" spellcheck="false"></div>
            <div class="field"><label for="out">Lien de cette peluche</label><div class="row"><input id="out" type="text" readonly><button class="btn" id="copy" type="button">Copier</button></div></div>
            <p class="help" id="link-help"></p>
            <div class="row"><a class="btn" id="open" target="_blank" rel="noopener" hidden>Ouvrir la page</a><button class="btn" id="icon" type="button" disabled>Télécharger l'icône PNG</button></div>
            <p class="status" id="dl-status" aria-live="polite"></p>
          </section>
          <section class="card setup">
            <h2>Mettre la page 3D en ligne (une seule fois)</h2>
            <ol>
              <li>La page 3D est déjà dans ton dépôt <code>peluches</code> (fichier <code>index.html</code>). Pour la mettre à jour à la main : <button class="btn" id="get-viewer" type="button" disabled>Télécharger index.html</button></li>
              <li>Sur github.com, dans le dépôt, ouvre <b>Settings → Pages</b>, choisis la branche <code>main</code> et le dossier <code>/ (root)</code>, puis <b>Save</b>. Une ou deux minutes après, l'adresse <code>https://misternutss.github.io/peluches/</code> fonctionne.</li>
              <li>L'atelier est aussi en ligne à <code>https://misternutss.github.io/peluches/atelier.html</code>.</li>
              <li>Chaque peluche est entièrement décrite dans son lien : chaque nouvelle peluche a son propre lien, rien d'autre à mettre en ligne.</li>
            </ol>
            <h2>Dans « Créer une image item »</h2>
            <ol>
              <li>Type d'item : <b>Site Web</b>, puis colle le lien de la peluche dans <b>URLS</b>.</li>
              <li>Pour l'icône d'inventaire : télécharge l'icône PNG, mets-la sur imgg.fr et colle son lien dans <b>Icône URL personnalisé</b>.</li>
            </ol>
            <p class="status" id="setup-status" aria-live="polite"></p>
          </section>
        </div>
      </div>
    </section>
  </main>
  <p class="err" id="err" hidden></p>
</div>

<script>window.addEventListener('error',e=>{const el=document.getElementById('err');if(el){el.hidden=false;el.textContent="L'atelier n'a pas pu se charger : "+e.message;}});</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script id="pl-src">
__MODEL__
</script>
<script>
const $=id=>document.getElementById(id);
function store(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){}return null;}
const say=(id,t)=>{$(id).textContent=t;if(id==='ai-status'&&$('stage-status'))$('stage-status').textContent=t;};

// Aperçu 3D
const reduceMotion=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;let spin=false;
const stage=$('stage'),scene=new THREE.Scene(),cam=new THREE.PerspectiveCamera(22,1,0.1,500);
const r=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});r.setClearColor(0x000000,0);r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;stage.prepend(r.domElement);
PL.setup(r);const camFill=PL.lights(scene);PL.HOOKS.onTex=()=>{dirty=true;};
let cfg=PL.clean(PL.PRESETS.pompier),cur=null,ry=-0.25,el=0.24,dirty=true,drag=false,lx=0,ly=0;
function fitSize(){const w=stage.clientWidth||480,h=stage.clientHeight||480;r.setPixelRatio(Math.min(2,window.devicePixelRatio||1));r.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();dirty=true;}
fitSize();if(window.ResizeObserver)new ResizeObserver(fitSize).observe(stage);window.addEventListener('resize',fitSize);
function rebuild(){if(cur){scene.remove(cur.group);cur.dispose();}cur=PL.build(cfg);scene.add(cur.group);dirty=true;}
let rbT=0;function changed(){updateLink();clearTimeout(rbT);rbT=setTimeout(rebuild,140);}
stage.addEventListener('pointerdown',e=>{if(e.target.closest('button'))return;drag=true;lx=e.clientX;ly=e.clientY;stage.classList.add('drag');});
window.addEventListener('pointermove',e=>{if(!drag)return;ry+=(e.clientX-lx)*0.01;el=Math.min(0.8,Math.max(-0.15,el+(e.clientY-ly)*0.006));lx=e.clientX;ly=e.clientY;dirty=true;});
const up=()=>{drag=false;stage.classList.remove('drag');};window.addEventListener('pointerup',up);window.addEventListener('pointercancel',up);
stage.addEventListener('dblclick',()=>{ry=-0.25;el=0.24;dirty=true;});
(function loop(){if(spin&&!drag&&!reduceMotion){ry+=0.008;dirty=true;}if(dirty&&cur){cur.group.rotation.y=ry;PL.aim(cam,cur.fit,el,1.04,camFill);r.render(scene,cam);dirty=false;}requestAnimationFrame(loop);})();

// Réglages
const CHOICES={hs:{court:'Courts',banane:'Banane (plaqués en arrière)',meches:'Mi-longs en mèches',herisse:'Hérissés',iroquoise:'Iroquoise',carre:'Carré',long:'Longs',tresse:"Tresse sur l'épaule",couettes:'Couettes',queue:'Queue de cheval',chignon:'Chignon',boucle:'Bouclés',afro:'Afro',dreads:'Dreads',rase:'Rasés',chauve:'Chauve'},
bd:{aucune:'Aucune',barbe3j:'Barbe de 3 jours',barbe:'Barbe',longue:'Barbe longue',moustache:'Moustache',bouc:'Bouc'},ex:{sourire:'Grand sourire',content:'Petit sourire',neutre:'Neutre',serieux:'Sérieux'},
gl:{aucune:'Aucunes',lunettes:'Lunettes de vue',soleil:'Lunettes de soleil',aviateur:'Lunettes aviateur',tete:'Lunettes relevées sur la tête',masque:'Lunettes de protection'},
hw:{aucun:'Aucun',capuche:'Capuche relevée',casquette:'Casquette',inverse:"Casquette à l'envers",bonnet:'Bonnet',chapeau:'Chapeau',bandeau:'Bandeau',pompier:'Casque de pompier',police:'Casquette de police'},
tp:{tshirt:'T-shirt',chemise:'Chemise',sweat:'Sweat à capuche',veste:'Veste ouverte',costume:'Costume',gilet:'Gilet sur manches'},mt:{uni:'Uni',rayures:'Rayures',camo:'Camouflage',carreaux:'Carreaux',taches:'Taches'},
bt:{pantalon:'Pantalon',jogging:'Jogging',short:'Short',salopette:'Salopette'},sh:{bottes:'Bottes',baskets:'Baskets',chaussures:'Chaussures de ville'},
it:{aucun:'Rien',lance:'Lance à incendie',coeur:'Cœur',telephone:'Téléphone',cafe:'Café',donut:'Donut',trousse:'Trousse de secours'}};
CHOICES.hm=CHOICES.mt;
CHOICES.hp={aucune:'Pas de raie',gauche:"Raie à gauche de l'image",milieu:'Raie au milieu',droite:"Raie à droite de l'image"};
CHOICES.hf={aucune:'Pas de frange (coiffés en arrière ou sur les côtés)',courte:'Frange courte',droite:'Frange droite (au ras des sourcils)',balayee:'Frange balayée sur le côté',rideau:'Frange rideau (ouverte au milieu)',longue:'Frange longue (sur les yeux)',arriere:'Relevés en arrière (banane, houppe)'};
CHOICES.hx={lisse:'Lisses',ondule:'Ondulés',boucle:'Bouclés',crepu:'Crépus (afro)',pique:'En pics',dreads:'Dreadlocks'};
CHOICES.ht={aucune:'Détachés',queue:'Queue de cheval basse',haute:'Queue de cheval haute',couettes:'Deux couettes',chignon:'Chignon',tresse:"Tresse sur l'épaule",demi:'Demi-queue (dessus attaché)'};
CHOICES.hd={normaux:'Comme le reste',courts:'Courts (dégradé)',rases:'Rasés'};
CHOICES.ms={aucune:'Aucune',monstre:'Petit monstre (oreilles et dents)',lapin:'Lapin',ours:'Ours',chat:'Chat',chien:'Chien',oiseau:'Oiseau / perroquet'};
CHOICES.po={assis:'Assise',debout:'Debout',coucou:'Coucou',bravo:'Bras levés',calin:'Câlin',coeur:'Cœur',pensif:'Pensive',tailleur:'En tailleur',dab:'Dab'};
CHOICES.ey={kawaii:'Mignons (peluche)',realiste:'Réalistes'};
CHOICES.st={classique:'Classique',ours:'Ourson',lapin:'Lapin',chat:'Chaton',monstre:'Petit monstre',avatar:'Avatar'};
CHOICES.mp={droite:"Sur l'épaule, à droite de l'image",gauche:"Sur l'épaule, à gauche de l'image",tete:'Sur la tête',mains:'Dans les mains'};
const FLAGS={r:'Radio',b:'Badge',m:'Micro-casque',s:'Sacoche',c:'Chaîne en or',o:"Boucles d'oreilles",w:'Montre',k:'Sac à dos',e:'Écharpe',h:'Casque audio au cou',a:'Bandana sur le visage',n:'Sac en bandoulière'};
const hairOn=c=>!['rase','chauve','iroquoise'].includes(c.hs);
const SECTIONS=[
{t:'Style, pose et nom',f:[{k:'st',type:'chips',l:'Style de peluche',wide:1},{k:'po',type:'chips',l:'Position',wide:1},{k:'fc',type:'color',l:'Couleur de la fourrure',show:c=>['ours','lapin','chat','monstre'].includes(c.st)},{k:'n',type:'text',l:'Nom',max:24,wide:1}]},
{t:'Visage',f:[{k:'ey',type:'chips',l:'Yeux',wide:1},{k:'sk',type:'color',l:'Peau'},{k:'ec',type:'color',l:'Yeux'},{k:'ex',type:'choice',l:'Expression'},{k:'bd',type:'choice',l:'Barbe'},{k:'fr',type:'check',l:'Taches de rousseur'},{k:'cl',type:'check',l:'Longs cils'}]},
{t:'Cheveux',f:[{k:'hs',type:'choice',l:'Coiffure de départ'},{k:'hc',type:'color',l:'Couleur des cheveux'},{k:'h2',type:'optcolor',l:"Mèches d'une autre couleur",show:hairOn},
{k:'hl',type:'range',l:'Longueur',min:0.3,max:5,step:0.1,fmt:'len',show:hairOn},{k:'hv',type:'range',l:'Volume',min:0,max:1,step:0.05,fmt:'pct',show:hairOn},
{k:'hx',type:'choice',l:'Texture',show:hairOn},{k:'hp',type:'choice',l:'Raie',show:hairOn},{k:'hf',type:'choice',l:'Frange',show:hairOn},{k:'ht',type:'choice',l:'Attache',show:hairOn},{k:'hd',type:'choice',l:'Côtés et nuque',show:hairOn}]},
{t:'Tête',f:[{k:'hw',type:'choice',l:'Couvre-chef'},{k:'hwc',type:'color',l:'Couleur du couvre-chef',show:c=>c.hw!=='aucun'},{k:'hwt',type:'text',l:'Texte ou numéro',max:6,show:c=>['casquette','bonnet','pompier'].includes(c.hw)},{k:'hm',type:'choice',l:'Motif du couvre-chef',show:c=>['capuche','casquette','inverse','chapeau'].includes(c.hw)},
{k:'gl',type:'choice',l:'Lunettes'},{k:'glc',type:'color',l:'Monture',show:c=>c.gl!=='aucune'},{k:'lc',type:'color',l:'Couleur des verres',show:c=>['soleil','aviateur','tete'].includes(c.gl)}]},
{t:'Tenue',f:[{k:'tp',type:'choice',l:'Haut'},{k:'mt',type:'choice',l:'Motif'},{k:'tc',type:'color',l:c=>({gilet:'Gilet',veste:'Veste',costume:'Veste de costume'})[c.tp]||'Couleur du haut'},
{k:'t2',type:'color',l:c=>({gilet:'Manches',veste:'Haut en dessous',costume:'Chemise',sweat:'Cordons'})[c.tp]||'Dessous',show:c=>['gilet','veste','costume','sweat'].includes(c.tp)},
{k:'im',type:'print',l:'Imprimé sur le devant (découpé dans la photo)',wide:1,show:c=>c.tp!=='costume'},{k:'tt',type:'text',l:'Texte imprimé (dos)',max:8},{k:'rf',type:'check',l:'Bandes réfléchissantes'},{k:'bt',type:'choice',l:'Bas'},{k:'pc',type:'color',l:c=>c.bt==='short'?'Couleur du short':'Couleur du bas'},
{k:'sh',type:'choice',l:'Chaussures'},{k:'sc',type:'color',l:'Couleur des chaussures'},{k:'gv',type:'glove',l:'Gants'}]},
{t:'Accessoires',f:[{k:'acc',type:'flags',l:'Équipement',wide:1},{k:'it',type:'choice',l:'Dans les mains'},{k:'ac',type:'color',l:"Couleur d'accent"},
{k:'ms',type:'choice',l:'Mascotte (mini-peluche)'},{k:'mc',type:'color',l:'Couleur de la mascotte',show:c=>c.ms!=='aucune'},{k:'mp',type:'choice',l:'Place de la mascotte',show:c=>c.ms!=='aucune'},{k:'mz',type:'range',l:'Taille de la mascotte',min:0.5,max:2,step:0.05,show:c=>c.ms!=='aucune'},{k:'mx',type:'range',l:'Mascotte : gauche / droite',min:-1,max:1,step:0.05,fmt:'off',show:c=>c.ms!=='aucune'},{k:'my',type:'range',l:'Mascotte : bas / haut',min:-1,max:1,step:0.05,fmt:'off',show:c=>c.ms!=='aucune'},{k:'mf',type:'range',l:'Mascotte : arrière / avant',min:-1,max:1,step:0.05,fmt:'off',show:c=>c.ms!=='aucune'},{k:'mr',type:'range',l:'Mascotte : rotation',min:-180,max:180,step:5,fmt:'deg',show:c=>c.ms!=='aucune'}]}];
const F={};let lastGlove='#86ace6';const lastOpt={h2:'#f3dc9a'};
function el2(tag,props,kids){const n=document.createElement(tag);Object.assign(n,props||{});(kids||[]).forEach(k=>n.append(k));return n;}
function colorRow(k,id){return el2('div',{className:'colorrow'},[el2('input',{type:'color',id}),el2('button',{type:'button',className:'pip',textContent:'Pipette',title:'Prendre la couleur sur la photo'})]);}
const TAB_OF={'Style, pose et nom':'style',Visage:'visage',Cheveux:'tete','Tête':'tete',Tenue:'tenue',Accessoires:'accessoires'};
for(const sec of SECTIONS){const grid=el2('div',{className:'fields'});$('tab-'+TAB_OF[sec.t]).append(el2('section',{className:'card'},[el2('h2',{textContent:sec.t}),grid]));
for(const f of sec.f){const id='f-'+f.k,row=el2('div',{className:'field'+(f.wide?' wide':'')});const lab=el2('label',{htmlFor:id});f.lab=lab;
if(f.type==='color'){row.append(lab,colorRow(f.k,id));row.querySelector('.pip').dataset.pip=f.k;}
else if(f.type==='choice'){const s=el2('select',{id});for(const[v,t]of Object.entries(CHOICES[f.k]))s.append(el2('option',{value:v,textContent:t}));row.append(lab,s);}
else if(f.type==='text'){row.append(lab,el2('input',{type:'text',id,maxLength:f.max,autocomplete:'off'}));}
else if(f.type==='check'){row.append(el2('label',{className:'check'},[el2('input',{type:'checkbox',id}),f.l]));f.lab=null;}
else if(f.type==='glove'){row.append(el2('label',{className:'check'},[el2('input',{type:'checkbox',id:id+'-on'}),'Gants']),colorRow(f.k,id));row.querySelector('.pip').dataset.pip=f.k;f.lab=null;}
else if(f.type==='optcolor'){row.append(el2('label',{className:'check'},[el2('input',{type:'checkbox',id:id+'-on'}),f.l]),colorRow(f.k,id));row.querySelector('.pip').dataset.pip=f.k;f.lab=null;}
else if(f.type==='range'){row.append(el2('div',{className:'row rangehead'},[lab,el2('span',{className:'help',id:id+'-v'})]),el2('input',{type:'range',id,min:f.min,max:f.max,step:f.step}));}
else if(f.type==='print'){const im=el2('img',{id:id+'-img',alt:'Imprimé pris sur la photo',className:'printimg'});row.append(el2('span',{className:'help',textContent:f.l}),el2('div',{className:'row'},[im,el2('button',{type:'button',className:'btn',id:id+'-pick',textContent:'Choisir sur la photo'}),el2('button',{type:'button',className:'btn',id:id+'-rm',textContent:'Retirer'})]));f.lab=null;}
else if(f.type==='chips'){const g=el2('div',{className:'seg',id});for(const[v,t]of Object.entries(CHOICES[f.k])){const b=el2('button',{type:'button',className:'btn',textContent:t});b.dataset.v=v;g.append(b);}row.append(el2('span',{className:'help',textContent:f.l}),g);f.lab=null;}
else if(f.type==='flags'){row.append(el2('span',{className:'help',textContent:f.l}),el2('div',{className:'flags'},Object.entries(FLAGS).map(([v,t])=>el2('label',{className:'check'},[el2('input',{type:'checkbox',id:id+'-'+v,value:v}),t]))));f.lab=null;}
f.row=row;F[f.k]=f;grid.append(row);}}
function syncForm(){const HV=PL.hair(cfg),val=k=>PL.HAIRK.includes(k)?HV[k]:cfg[k];for(const k in F){const f=F[k],id='f-'+k;if(f.lab)f.lab.textContent=typeof f.l==='function'?f.l(cfg):f.l;f.row.hidden=!!(f.show&&!f.show(cfg));
if(f.type==='color'||f.type==='choice'||f.type==='text'){if(document.activeElement!==$(id))$(id).value=k==='fc'?(cfg.fc||cfg.hc):val(k);}
else if(f.type==='range'){if(document.activeElement!==$(id))$(id).value=val(k);const v=Number(val(k));$(id+'-v').textContent=f.fmt==='len'?[[0.6,'Ras'],[1.4,'Courts'],[2.2,'Aux oreilles'],[2.8,'Mi-longs'],[3.5,'Au menton'],[4.5,'Aux épaules'],[9,'Dans le dos']].find(x=>v<x[0])[1]+' ('+v.toFixed(1).replace('.',',')+')':f.fmt==='pct'?Math.round(v*100)+' %':f.fmt==='deg'?Math.round(v)+'°':f.fmt==='off'?(v>0?'+':'')+v.toFixed(2).replace('.',','):'× '+v.toFixed(2).replace('.',',');}
else if(f.type==='print'){const on=!!cfg.im;$(id+'-img').hidden=!on;if(on)$(id+'-img').src='data:image/'+cfg.imt+';base64,'+cfg.im;$(id+'-rm').hidden=!on;$(id+'-pick').disabled=!anyPhoto();}
else if(f.type==='chips')$(id).querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===cfg[k])));
else if(f.type==='check')$(id).checked=!!cfg[k];
else if(f.type==='glove'){$(id+'-on').checked=!!cfg.gv;if(cfg.gv)lastGlove=cfg.gv;$(id).value=lastGlove;$(id).disabled=!cfg.gv;}
else if(f.type==='optcolor'){$(id+'-on').checked=!!cfg[k];if(cfg[k])lastOpt[k]=cfg[k];$(id).value=lastOpt[k];$(id).disabled=!cfg[k];}
else if(f.type==='flags')for(const v in FLAGS)$(id+'-'+v).checked=cfg.acc.includes(v);}renderPieces();}
// Pièces sur mesure ajoutées par Claude : on peut changer leur couleur ou les retirer
const SHAPE_L={sphere:'Boule',goutte:'Goutte',cone:'Cône',cylindre:'Cylindre',tore:'Anneau',boite:'Bloc'},ANCH_L={tete:'tête',corps:'corps',mains:'mains',dos:'dos',jambes:'jambes'};
$('tab-accessoires').append(el2('section',{className:'card'},[el2('h2',{textContent:'Pièces sur mesure'}),el2('p',{className:'help',textContent:"Ce que Claude ajoute pour coller à la photo : oreilles, cornes, queue, nœud… Change une couleur ou retire une pièce."}),el2('div',{id:'pz-list',className:'pzlist'})]));
function renderPieces(){const box=$('pz-list');if(!box)return;box.textContent='';if(!cfg.pz.length){box.append(el2('p',{className:'help',textContent:'Aucune pièce sur mesure pour cette peluche.'}));return;}
cfg.pz.forEach((q,i)=>{const b=el2('button',{type:'button',className:'btn',textContent:'Retirer'});b.dataset.rm=i;box.append(el2('div',{className:'pzrow'},[el2('label',{htmlFor:'pz-'+i,textContent:(i+1)+'. '+SHAPE_L[q[0]]+' sur '+ANCH_L[q[1]]}),el2('input',{type:'color',id:'pz-'+i,value:q[11]}),b]));});}
$('pz-list').addEventListener('input',e=>{const m=e.target.id.match(/^pz-(\d+)$/);if(m&&cfg.pz[+m[1]]){cfg.pz[+m[1]][11]=e.target.value;changed();}});
$('pz-list').addEventListener('click',e=>{const b=e.target.closest('[data-rm]');if(!b)return;cfg.pz.splice(+b.dataset.rm,1);renderPieces();changed();});
$('settings').addEventListener('input',e=>{const t=e.target,m=t.id.match(/^f-([a-z0-9]+)/);if(!m)return;const k=m[1],f=F[k];if(!f)return;
if(f.type==='check')cfg[k]=t.checked?1:0;
else if(f.type==='glove'){if(t.type==='color'){lastGlove=t.value;if(cfg.gv)cfg.gv=t.value;}else cfg.gv=t.checked?lastGlove:'';}
else if(f.type==='flags')cfg.acc=Object.keys(FLAGS).filter(v=>$('f-acc-'+v).checked).join('');
else if(f.type==='optcolor'){if(t.type==='color'){lastOpt[k]=t.value;if(cfg[k])cfg[k]=t.value;}else cfg[k]=t.checked?lastOpt[k]:'';}
else{cfg[k]=t.value;if(k==='hs')PL.HAIRK.forEach(h=>{delete cfg[h];});}
cfg=PL.clean(cfg);syncForm();changed();});

// Onglets et étapes ; la pipette et l'imprimé ouvrent l'onglet Photos puis ramènent à l'onglet d'avant
const TABS=['photos','style','visage','tete','tenue','accessoires','lien'];let curTab='photos',backTab=null;
function showTab(t){curTab=t;document.querySelectorAll('.tabpanel').forEach(pn=>{pn.hidden=pn.dataset.tab!==t;});document.querySelectorAll('.tabs button').forEach(bt=>bt.setAttribute('aria-selected',String(bt.dataset.tab===t)));
const stp=t==='photos'?'photos':t==='lien'?'lien':'reglages';document.querySelectorAll('.steps li').forEach(li=>li.classList.toggle('on',li.dataset.step===stp));store('peluches-onglet',t);}
function goPhotos(){if(curTab!=='photos'){backTab=curTab;showTab('photos');}}
function goBack(){if(backTab){showTab(backTab);backTab=null;}}
document.querySelector('.tabs').addEventListener('click',e=>{const bt=e.target.closest('button[data-tab]');if(bt)showTab(bt.dataset.tab);});
document.querySelector('.steps').addEventListener('click',e=>{const li=e.target.closest('[data-step]');if(li)showTab(li.dataset.step==='reglages'?'style':li.dataset.step);});
{const t0=store('peluches-onglet');showTab(TABS.includes(t0)?t0:'photos');}
// Vues de l'aperçu : face, profil, dos, rotation continue
const view=r0=>{spin=false;$('v-spin').setAttribute('aria-pressed','false');ry=r0;el=0.12;dirty=true;};
$('v-front').addEventListener('click',()=>view(-0.34));$('v-side').addEventListener('click',()=>view(-0.34-Math.PI/2));$('v-back').addEventListener('click',()=>view(Math.PI-0.34));
$('v-spin').addEventListener('click',()=>{spin=!spin;$('v-spin').setAttribute('aria-pressed',String(spin));dirty=true;});

// Modèles
const PRESET_NAMES={pompier:'Pompier',police:'Policier',ems:'Ambulancière',civil:'Civil'};
for(const[p,t]of Object.entries(PRESET_NAMES)){const b=el2('button',{type:'button',className:'btn',textContent:t});b.addEventListener('click',()=>{cfg=PL.clean(PL.PRESETS[p]);syncForm();rebuild();updateLink();});$('presets').append(b);}

// Photos (face, côté, dos), pipette et imprimé
const SLOTS=['face','cote','dos'],SLOT_L={face:'face',cote:'côté',dos:'dos'},shots={};let pick=null,printPick=false,printA=null,anaT=0;
const anyPhoto=()=>SLOTS.some(s=>shots[s].blob),photoList=()=>SLOTS.filter(s=>shots[s].blob);
document.querySelectorAll('.shot').forEach(el=>{const slot=el.dataset.slot,cn=el.querySelector('canvas'),inp=el.querySelector('input'),btn=el.querySelector('button');shots[slot]={el,cn,btn,blob:null};
btn.addEventListener('click',()=>inp.click());inp.addEventListener('change',e=>{loadPhoto(slot,e.target.files[0]);e.target.value='';});
el.addEventListener('dragover',e=>{e.preventDefault();el.classList.add('over');});el.addEventListener('dragleave',()=>el.classList.remove('over'));
el.addEventListener('drop',e=>{e.preventDefault();el.classList.remove('over');loadPhoto(slot,e.dataTransfer.files[0]);});
cn.addEventListener('click',e=>photoClick(slot,e));});
document.addEventListener('paste',e=>{const it=[...((e.clipboardData&&e.clipboardData.items)||[])].find(i=>i.type.startsWith('image/'));if(it){e.preventDefault();loadPhoto(SLOTS.find(s=>!shots[s].blob)||'face',it.getAsFile());}});
async function loadPhoto(slot,file){if(!file||!/^image\//.test(file.type)){say('ai-status',"Ce fichier n'est pas une image.");return;}
try{const S=shots[slot],bmp=await createImageBitmap(file),k=Math.min(1,1600/Math.max(bmp.width,bmp.height));S.cn.width=Math.round(bmp.width*k);S.cn.height=Math.round(bmp.height*k);S.cn.getContext('2d').drawImage(bmp,0,0,S.cn.width,S.cn.height);
S.cn.hidden=false;S.el.classList.add('has');S.btn.textContent='Changer';$('right').classList.remove('no-photo');
S.blob=await new Promise(res=>S.cn.toBlob(res,'image/jpeg',0.9));updateAnalyse();syncForm();
// Petite attente : si plusieurs photos arrivent d'affilée, la création ne part qu'une fois
clearTimeout(anaT);if(sample&&imagesOK){say('ai-status','Photo de '+SLOT_L[slot]+' ajoutée. La création démarre…');anaT=setTimeout(runAnalysis,1500);}else say('ai-status',readyMsg());}
catch(e){say('ai-status',"Impossible d'ouvrir cette image. Essaie une capture en PNG ou JPEG.");}}
function pickUI(on){document.querySelectorAll('.shot').forEach(el=>el.classList.toggle('picking',on));}
function setPick(k){pick=k;printPick=false;document.querySelectorAll('.pip').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.pip===k)));pickUI(!!k);
if(k){goPhotos();const f=F[k];say('ai-status','Clique sur une photo pour prendre la couleur : '+((typeof f.l==='function'?f.l(cfg):f.l)||'Gants').toLowerCase()+'.');$('shots').scrollIntoView({block:'nearest',behavior:'smooth'});}}
function startPrintPick(){setPick(null);goPhotos();printPick=true;printA=null;pickUI(true);say('ai-status',"Clique sur un coin de l'imprimé, puis sur le coin opposé.");$('shots').scrollIntoView({block:'nearest',behavior:'smooth'});}
$('settings').addEventListener('click',e=>{const b=e.target.closest('.pip');if(b)setPick(pick===b.dataset.pip?null:b.dataset.pip);
const ch=e.target.closest('.seg button');if(ch&&ch.parentElement.id.startsWith('f-')){cfg[ch.parentElement.id.slice(2)]=ch.dataset.v;cfg=PL.clean(cfg);syncForm();changed();}
if(e.target.id==='f-im-pick')startPrintPick();if(e.target.id==='f-im-rm'){cfg.im='';syncForm();changed();}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&(pick||printPick)){setPick(null);pickUI(false);printPick=false;say('ai-status',readyMsg());goBack();}});
function photoClick(slot,e){const cn=shots[slot].cn,b=cn.getBoundingClientRect(),x=(e.clientX-b.left)*cn.width/b.width,y=(e.clientY-b.top)*cn.height/b.height;
if(printPick){const p=[x/cn.width,y/cn.height];if(!printA){printA=[slot,p];say('ai-status',"Maintenant, clique sur le coin opposé de l'imprimé.");return;}
const[s0,a]=printA;printPick=false;printA=null;pickUI(false);if(s0!==slot){say('ai-status','Clique les deux coins sur la même photo.');return;}
say('ai-status',cropPrint(cn,[Math.min(a[0],p[0]),Math.min(a[1],p[1]),Math.abs(p[0]-a[0]),Math.abs(p[1]-a[1])])?'Imprimé ajouté sur la peluche.':'Zone trop petite : recommence.');goBack();return;}
if(!pick)return;const d=cn.getContext('2d').getImageData(Math.max(0,Math.round(x)-2),Math.max(0,Math.round(y)-2),5,5).data;let R=0,G=0,B=0,n=0;for(let i=0;i<d.length;i+=4){R+=d[i];G+=d[i+1];B+=d[i+2];n++;}
const h='#'+[R,G,B].map(v=>Math.round(v/n).toString(16).padStart(2,'0')).join('');if(pick==='gv'){lastGlove=h;cfg.gv=h;}else{cfg[pick]=h;if(pick in lastOpt)lastOpt[pick]=h;}
setPick(null);cfg=PL.clean(cfg);syncForm();changed();say('ai-status','Couleur prise sur la photo.');goBack();}
// Imprimé : découpé dans la photo, bords adoucis, réduit pour que le lien reste court
function cropPrint(cn,box){if(!box||!(box[2]>0.02)||!(box[3]>0.02))return false;const sx=box[0]*cn.width,sy=box[1]*cn.height,sw=box[2]*cn.width,sh=box[3]*cn.height,k=Math.min(1,96/Math.max(sw,sh)),w=Math.max(8,Math.round(sw*k)),h=Math.max(8,Math.round(sh*k));
const o=document.createElement('canvas');o.width=w;o.height=h;const g=o.getContext('2d');g.drawImage(cn,sx,sy,sw,sh,0,0,w,h);g.globalCompositeOperation='destination-in';
const gr=g.createRadialGradient(w/2,h/2,Math.min(w,h)*0.32,w/2,h/2,Math.max(w,h)*0.62);gr.addColorStop(0,'rgba(0,0,0,1)');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(0,0,w,h);
let url=o.toDataURL('image/webp',0.72),t='webp';if(!url.startsWith('data:image/webp')){url=o.toDataURL('image/png');t='png';}
cfg.im=url.split(',')[1];cfg.imt=t;cfg.ia=w/h;cfg=PL.clean(cfg);syncForm();changed();return!!cfg.im;}

// Création depuis les photos : Claude regarde, puis compare son résultat aux photos et corrige tout seul
let sample=null,imagesOK=false,maxImages=1,ctl=null;
const WHO={seule:'la personne des photos',gauche:'la personne à gauche sur les photos',milieu:'la personne au milieu des photos',droite:'la personne à droite sur les photos'};
function intro(w,slots){return "Tu reçois "+slots.length+" photo(s) de la même personne, souvent un personnage du jeu GTA en roleplay, dans cet ordre : "+slots.map((s,i)=>'image '+(i+1)+' = vue de '+SLOT_L[s]).join(', ')+". Décris "+WHO[w]+" pour fabriquer une peluche qui lui ressemble le plus possible.\n";}
function prompt(w,slots){return intro(w,slots)+keysText();}
function keysText(){return "Regarde d'abord ce qui rend la personne reconnaissable (coiffure et frange, couvre-chef ou capuche, forme des lunettes, barbe, imprimé du haut, veste, motif, accessoires, animal ou mascotte) et reprends tout ce qui se voit. Sers-toi des vues de côté et de dos pour l'arrière de la coiffure, la capuche et le texte au dos. "
+"Prends les vraies couleurs des photos en compensant l'éclairage si la scène est sombre ou colorée, jamais des couleurs génériques.\n"
+"Réponds uniquement avec un objet JSON qui a exactement ces clés :\n"
+'- "n" : nom court pour la peluche (métier ou surnom visible), 24 caractères maximum\n'
+'- "sk" : couleur de peau, "#rrggbb"\n'
+'- "hc" : couleur des cheveux (ou des sourcils si la personne est chauve), "#rrggbb"\n'
+'- "h2" : couleur des mèches, reflets ou pointes d\'une autre couleur, "#rrggbb", ou "" si les cheveux sont d\'une seule couleur\n'
+'- "hs" : coiffure de départ, parmi "court" (courts et nets), "banane" (plaqués en arrière ou banane : volume sur le dessus, côtés courts ou dégradés), "meches" (mi-longs en mèches ou frange sur le front), "herisse" (courts en petits pics), "iroquoise" (crête au milieu, côtés rasés), "carre" (carré au menton avec frange), "long" (aux épaules ou plus), "tresse" (une grosse tresse qui tombe devant l\'épaule), "couettes", "queue" (queue de cheval), "chignon", "boucle" (bouclés courts), "afro", "dreads" (dreadlocks ou tresses), "rase", "chauve"\n'
+'La coiffure est ce qui rend la personne reconnaissable : décris-la précisément avec les clés suivantes, qui remplacent les réglages du style de départ :\n'
+'- "hl" : longueur, nombre de 0.3 à 5 : 0.5 presque ras, 1 courts, 1.5 courts avec du volume, 2 jusqu\'aux oreilles, 2.5 mi-longs, 3 au menton ou à la mâchoire, 4 aux épaules, 5 dans le dos. Pour des cheveux attachés, la longueur qu\'ils auraient détachés\n'
+'- "hv" : volume, de 0 (plaqués) à 1 (très gonflés, en bataille)\n'
+'- "hx" : texture, parmi "lisse", "ondule", "boucle" (boucles bien dessinées), "crepu" (afro, frisé serré), "pique" (courts en pics ou au gel), "dreads"\n'
+'- "hp" : raie, parmi "aucune", "gauche" (à gauche de l\'image), "milieu", "droite" (à droite de l\'image)\n'
+'- "hf" : frange ou devant, parmi "aucune" (pas de frange, cheveux coiffés vers l\'arrière ou sur les côtés), "courte" (mèches courtes sur le haut du front), "droite" (frange droite au ras des sourcils), "balayee" (mèches balayées en biais sur le front, du côté opposé à la raie), "rideau" (frange ouverte au milieu qui encadre le visage), "longue" (frange qui descend jusqu\'aux yeux), "arriere" (relevés en arrière, banane, houppe)\n'
+'- "ht" : attache, parmi "aucune" (détachés), "queue" (queue de cheval basse), "haute" (queue de cheval haute), "couettes", "chignon", "tresse" (une tresse devant l\'épaule), "demi" (le dessus attaché derrière, le reste détaché)\n'
+'- "hd" : côtés et nuque, parmi "normaux", "courts" (dégradé), "rases" (undercut, côtés rasés)\n'
+'- "ec" : couleur des yeux, "#rrggbb" ("#5a3b22" si on ne les voit pas)\n'
+'- "ex" : expression, parmi "sourire" (grand sourire), "content" (petit sourire), "neutre", "serieux"\n'
+'- "bd" : pilosité du visage, parmi "aucune", "barbe3j" (barbe de quelques jours), "barbe", "longue" (barbe longue), "moustache", "bouc"\n'
+'- "fr" : 1 si on voit des taches de rousseur, sinon 0\n'
+'- "cl" : 1 pour de longs cils recourbés (visage féminin ou maquillé), 0 sinon\n'
+'- "gl" : lunettes, parmi "aucune", "lunettes" (de vue, sur les yeux), "soleil" (de soleil rondes ou rectangulaires, sur les yeux), "aviateur" (aviateur : verres en goutte, fine monture métal), "tete" (lunettes relevées sur le front, la tête ou la capuche), "masque" (lunettes de protection ou de ski sur les yeux)\n'
+'- "glc" : couleur de la monture, "#rrggbb"\n'
+'- "lc" : couleur des verres des lunettes de soleil ou aviateur, "#rrggbb" (brun, gris fumé, vert, bleu miroir…)\n'
+'- "hw" : couvre-chef, parmi "aucun", "capuche" (capuche relevée sur la tête), "casquette", "inverse" (casquette à l\'envers), "bonnet", "chapeau", "bandeau", "pompier" (casque de pompier ou de chantier), "police" (casquette d\'uniforme à visière)\n'
+'- "hwc" : couleur du couvre-chef ou de la capuche, "#rrggbb"\n'
+'- "hwt" : texte ou numéro visible sur le couvre-chef, 6 caractères maximum, sinon ""\n'
+'- "hm" : motif de la capuche, de la casquette ou du chapeau, parmi "uni", "rayures", "camo", "carreaux", "taches" (le motif prend la couleur "ac")\n'
+'- "tp" : haut, parmi "tshirt", "chemise", "sweat" (sweat ou pull), "veste" (veste ouverte sur un autre haut), "costume" (veste de costume, chemise et cravate), "gilet" (gilet sans manches porté sur un autre haut)\n'
+'- "mt" : motif du haut, parmi "uni", "rayures", "camo", "carreaux", "taches" (taches de vache, de dalmatien… dans la couleur "ac")\n'
+'- "tc" : couleur principale du haut (pour gilet, veste ou costume : la pièce du dessus), "#rrggbb"\n'
+'- "t2" : couleur du vêtement en dessous (les manches pour un gilet, le haut sous une veste, la chemise d\'un costume, les cordons d\'un sweat), "#rrggbb"\n'
+'- "imp" : si le haut porte un grand dessin, logo ou imprimé sur le devant, sa boîte [x, y, largeur, hauteur] dans l\'image 1, en fractions de 0 à 1 (x et y = coin en haut à gauche), bien serrée autour du dessin ; sinon null\n'
+'- "tt" : texte imprimé sur le haut (par exemple LSPD, EMS, LSFD), 8 caractères maximum, sinon ""\n'
+'- "rf" : 1 s\'il y a des bandes réfléchissantes, sinon 0\n'
+'- "ac" : couleur d\'accent pour les rayures, la cravate, le pompon, le bandana, l\'écharpe, le sac à dos ou les bandes du jogging, "#rrggbb"\n'
+'- "bt" : bas, parmi "pantalon", "jogging", "short", "salopette" (salopette à bretelles et plastron, le haut se voit dessous)\n'
+'- "pc" : couleur du bas, "#rrggbb"\n'
+'- "sh" : chaussures, parmi "bottes", "baskets", "chaussures" (de ville)\n'
+'- "sc" : couleur des chaussures, "#rrggbb"\n'
+'- "gv" : couleur des gants, "#rrggbb", ou "" sans gants\n'
+'- "acc" : lettres des accessoires visibles, "" s\'il n\'y en a aucun : r = radio ou talkie, b = badge ou insigne, m = micro-casque ou oreillette, s = sacoche à la ceinture, c = chaîne ou collier, o = boucles d\'oreilles, w = montre, k = sac à dos, e = écharpe, h = casque audio autour du cou, a = bandana ou masque sur le bas du visage, n = sac en bandoulière\n'
+'- "it" : objet tenu en main, parmi "aucun", "lance" (lance à incendie), "coeur", "telephone", "cafe", "donut", "trousse" (trousse de secours)\n'
+'- "ms" : petite peluche ou petit animal porté par la personne (sur l\'épaule, accroché au sac ou dans les bras), parmi "aucune", "monstre" (petite peluche monstre à longues oreilles, visage clair et grand sourire plein de dents, comme les figurines de collection à la mode), "lapin" (lapin classique), "ours", "chat", "chien", "oiseau" (oiseau ou perroquet) ; prends la forme la plus proche\n'
+'- "mc" : couleur de cette mascotte, "#rrggbb"\n'
+'- "mp" : place de la mascotte, parmi "droite" (sur l\'épaule à droite de l\'image), "gauche" (sur l\'épaule à gauche de l\'image), "mains"\n'
+'- "mz" : taille de la mascotte, nombre de 0.5 à 2 (1 = normale, à peu près la moitié de la hauteur de la tête ; 0.6 = petit porte-clés ; 1.6 = grosse peluche) ; estime-la par rapport à la tête sur la photo\n'
+'- "pz" : liste de pièces sur mesure (0 à 16) pour reproduire tout ce qui rend la personne reconnaissable et que les choix ci-dessus ne couvrent pas : oreilles ou cornes d\'un costume d\'animal, queue, ailes, nœud, fleur, couronne, antennes, pompons, gros boutons, etc. Mets [] s\'il n\'y a rien de spécial.\n'
+'  Chaque pièce : {"forme":"sphere"|"goutte"|"cone"|"cylindre"|"tore"|"boite","ancre":"tete"|"corps"|"mains"|"dos"|"jambes","pos":[x,y,z],"taille":[tx,ty,tz],"rot":[rx,ry,rz],"couleur":"#rrggbb","colle":true|false}\n'
+'  Unités : 1 = le rayon de l\'ancre (la tête fait 1 de rayon). x vers la droite de l\'image quand la peluche te fait face, y vers le haut, z vers l\'avant. "taille" donne des demi-dimensions, "rot" des degrés.\n'
+'  "colle":true (conseillé pour ce qui est posé sur la tête ou le corps) : "pos" est une direction depuis le centre de l\'ancre ; la pièce est posée sur la surface la plus extérieure (cheveux, capuche ou chapeau compris) et son axe y pointe vers l\'extérieur. "colle":false : "pos" est une position libre autour de l\'ancre.\n'
+'  Formes : "cone" a la pointe vers +y, "goutte" a la pointe vers -y, "tore" est un anneau dans le plan x-y, "boite" est un bloc arrondi.\n'
+'  Exemple pour une capuche de vache : oreilles {"forme":"sphere","ancre":"tete","pos":[0.9,0.45,0],"taille":[0.2,0.34,0.08],"rot":[0,0,0],"couleur":"#f2b5a0","colle":true} et la même avec x = -0.9 ; cornes {"forme":"cone","ancre":"tete","pos":[0.35,1,0.1],"taille":[0.08,0.26,0.08],"rot":[0,0,0],"couleur":"#e8c27a","colle":true} et la même avec x = -0.35.\n'
+"N'utilise jamais les pièces sur mesure pour une mascotte, une coiffure, des lunettes ou un vêtement : il y a des clés pour ça. Une pièce isolée qui ne ressemble à rien est pire que pas de pièce : en cas de doute, mets [].\n"
+"Une combinaison ou un pyjama d'animal se fait avec tp sweat et hw capuche de la même couleur, le même motif sur mt et hm, puis les oreilles, cornes ou queue en pièces sur mesure.\n"
+"Exemple de forme (sans pièce sur mesure) : "+JSON.stringify(Object.assign({},PL.PRESETS.police,{hm:'uni',pz:[],cl:0,ms:'aucune',mc:'#8ec5f0',mp:'droite',mz:1,lc:'#3a2a1e',imp:null}));}
function readyMsg(){if(!(sample&&imagesOK))return $('key-box')&&!$('key-box').hidden?"Pour la création automatique, enregistre une clé API Claude ci-dessous. Sinon règle la peluche à la main : le bouton Pipette prend une couleur sur la photo.":"La création automatique n'est pas disponible ici. Règle la peluche à la main : le bouton Pipette prend une couleur sur la photo.";return anyPhoto()?'Peluche prête. Tu peux relancer la création ou corriger les réglages.':'Ajoute une photo de face : la peluche se crée toute seule.';}
function reviewPrompt(w,slots,nr){const cur=Object.assign({},cfg);delete cur.im;delete cur.imt;delete cur.ia;
return intro(w,slots)+"Les "+nr+" dernières images ne sont pas des photos : c'est le rendu actuel de la peluche ("+(nr>1?'de face, puis de dos':'de face')+"), fabriquée avec ce réglage :\n"+JSON.stringify(cur)+"\n"
+"Compare la peluche aux photos comme un client exigeant, en commençant par la coiffure (longueur, volume, raie, frange, texture, attache, côtés), puis couleurs des cheveux, de la peau et des yeux, barbe, lunettes, couvre-chef, haut et motif, couleurs des vêtements, accessoires, mascotte, objets. "
+"Corrige tout ce qui ne ressemble pas et garde ce qui est juste. Renvoie le réglage complet corrigé.\n"+keysText();}
function updateAnalyse(){const b=$('analyse');b.hidden=!(sample&&imagesOK&&anyPhoto());b.disabled=false;b.textContent=ctl?'Arrêter':'Relancer la création';}
// Rendu de la peluche sur fond gris neutre, pour que Claude la compare aux photos
async function renderView(rot,S){await new Promise(res=>setTimeout(res,250));const pr=r.getPixelRatio(),keep=cur.group.rotation.y;r.setPixelRatio(1);r.setSize(S,S,false);cam.aspect=1;cam.updateProjectionMatrix();cur.group.rotation.y=rot;PL.aim(cam,cur.fit,0.12,1.05,camFill);r.render(scene,cam);
const o=document.createElement('canvas');o.width=o.height=S;const g=o.getContext('2d');g.fillStyle='#8a929c';g.fillRect(0,0,S,S);g.drawImage(r.domElement,0,0);cur.group.rotation.y=keep;r.setPixelRatio(pr);fitSize();return new Promise(res=>o.toBlob(res,'image/jpeg',0.9));}
function applyAnswer(data,keep,first0,first){const prev=first?null:(cfg.im?{im:cfg.im,imt:cfg.imt,ia:cfg.ia}:null);cfg=PL.clean(Object.assign({},data,keep),PL.NEUTRAL);
if(Array.isArray(data.imp)&&data.imp.length===4)cropPrint(shots[first0].cn,data.imp.map(Number));else if(prev&&data.imp!==null)Object.assign(cfg,prev);syncForm();rebuild();updateLink();}
async function runAnalysis(){const slots=photoList();if(!slots.length||!sample||!imagesOK)return;clearTimeout(anaT);if(ctl)ctl.abort();const my=new AbortController();ctl=my;updateAnalyse();
const w=$('who').value,keep={st:cfg.st,po:cfg.po,ey:cfg.ey,fc:''},use=slots.slice(0,Math.max(1,maxImages)),imgs=use.map(s=>shots[s].blob);
try{say('ai-status','Claude regarde '+(use.length>1?'les photos':'la photo')+'… Ça prend souvent 10 à 40 secondes.');
let data=await sample.json(prompt(w,use),{images:imgs,signal:my.signal});if(ctl!==my)return;applyAnswer(data,keep,use[0],true);
const nr=Math.min(maxImages-use.length,shots.dos.blob?2:1);
if($('review').checked&&nr>=1){say('ai-status','Peluche créée. Claude la compare maintenant aux photos pour corriger ce qui ne ressemble pas…');
const renders=[await renderView(-0.34,512)];if(nr>1)renders.push(await renderView(Math.PI-0.34,512));
data=await sample.json(reviewPrompt(w,use,renders.length),{images:imgs.concat(renders),signal:my.signal,cache:false});if(ctl!==my)return;applyAnswer(data,keep,use[0],false);
say('ai-status','Peluche créée puis vérifiée par Claude. Corrige ce qui ne va pas, puis copie le lien.');}
else say('ai-status','Peluche créée depuis '+(use.length>1?'les photos':'la photo')+'. Corrige ce qui ne va pas, puis copie le lien.');}
catch(e){if(ctl!==my)return;const code=e&&e.code;
if(['not_granted','sampling_disabled','not_declared','capability_disabled','capability_removed','images_unavailable'].includes(code)){sample=null;say('ai-status',"La création automatique n'est pas autorisée ici. Règle la peluche à la main : le bouton Pipette prend une couleur sur la photo.");}
else say('ai-status',({cancelled:'Création arrêtée.',rate_limited:'Trop de demandes pour le moment. Réessaie dans un moment.',image_rejected:"Une des images n'est pas acceptée. Essaie des captures en PNG ou JPEG.",
refused:"Claude n'a pas pu décrire cette photo. Essaie une autre image.",bad_key:'La clé API est refusée. Vérifie-la dans la case « Clé API Claude ».',network:'Pas de connexion avec Claude. Réessaie dans un moment.',invalid_json:'La réponse était incomplète. Clique sur « Relancer la création ».',session_expired:'Reconnecte-toi à Claude, puis relance la création.'})[code]||'La création a échoué. Clique sur « Relancer la création ».');}
finally{if(ctl===my){ctl=null;updateAnalyse();}}}
const getSample=window.claude&&window.claude.use?window.claude.use('sample'):Promise.resolve(null);
// Hors de claude.ai (page GitHub) : création automatique avec une clé API Claude enregistrée dans ce navigateur
function keySample(){const key=store('peluches-cle');if(!key)return null;
const b64=blob=>new Promise((res,rej)=>{const fr=new FileReader();fr.onload=()=>res(String(fr.result).split(',')[1]);fr.onerror=rej;fr.readAsDataURL(blob);});
const fail=code=>Object.assign(new Error(code),{code});
return{limits:async()=>({images:{maxCount:5}}),json:async(text,o)=>{const content=[];for(const im of(o.images||[]))content.push({type:'image',source:{type:'base64',media_type:im.type||'image/jpeg',data:await b64(im)}});content.push({type:'text',text});
let r;try{r=await fetch('https://api.anthropic.com/v1/messages',{method:'POST',signal:o.signal,headers:{'content-type':'application/json','x-api-key':key,'anthropic-version':'2026-10-21','anthropic-beta':'server-side-fallback-2026-07-01','anthropic-dangerous-direct-browser-access':'true'},
body:JSON.stringify({model:'claude-opus-5-5',max_tokens:16000,output_config:{effort:'medium'},fallbacks:'default',system:'Tu réponds uniquement avec un objet JSON valide, sans texte autour.',messages:[{role:'user',content}]})});}
catch(e){throw fail(e&&e.name==='AbortError'?'cancelled':'network');}
if(r.status===401||r.status===403)throw fail('bad_key');if(r.status===429)throw fail('rate_limited');if(!r.ok)throw fail('failed');
const d=await r.json();if(d.stop_reason==='refusal')throw fail('refused');const t=(d.content||[]).filter(x=>x.type==='text').map(x=>x.text).join('');
const a=t.indexOf('{'),z=t.lastIndexOf('}');try{return JSON.parse(t.slice(a,z+1));}catch(e){throw fail('invalid_json');}}};}
$('key-save').addEventListener('click',()=>{const v=$('api-key').value.trim();store('peluches-cle',v);$('api-key').value='';sample=keySample();imagesOK=!!sample;maxImages=5;updateAnalyse();
say('ai-status',sample?'Clé enregistrée. '+readyMsg():'Clé retirée. Règle la peluche à la main.');if(sample&&anyPhoto())runAnalysis();});
getSample.then(async s=>{if(!s){$('key-box').hidden=false;s=keySample();if(store('peluches-cle'))$('api-key').placeholder='Clé enregistrée (laisse vide puis Enregistrer pour la retirer)';}sample=s;if(s){try{const lim=await s.limits();imagesOK=!!(lim&&lim.images);if(imagesOK)maxImages=lim.images.maxCount||1;}catch(e){imagesOK=false;}}updateAnalyse();if(!pick)say('ai-status',readyMsg());if(anyPhoto())runAnalysis();},()=>{updateAnalyse();say('ai-status',readyMsg());});
$('analyse').addEventListener('click',()=>{if(ctl){const c0=ctl;ctl=null;c0.abort();updateAnalyse();say('ai-status','Création arrêtée.');return;}runAnalysis();});
$('who').addEventListener('change',()=>{if(anyPhoto())runAnalysis();});

// Lien
const baseIn=$('base');baseIn.value=store('peluches-base')||(/github\.io$/.test(location.hostname)?location.origin+location.pathname.replace(/[^/]*$/,''):'https://misternutss.github.io/peluches/');
baseIn.addEventListener('input',()=>{store('peluches-base',baseIn.value.trim());updateLink();});
function baseUrl(){const v=baseIn.value.trim();if(!/^https?:\/\//i.test(v))return '';try{const u=new URL(v);if(!/\.[a-z0-9]+$/i.test(u.pathname)&&!u.pathname.endsWith('/'))u.pathname+='/';u.search='';u.hash='';return u.toString();}catch(e){return '';}}
function updateLink(){const b=baseUrl(),url=(b||'https://misternutss.github.io/peluches/')+'?p='+PL.encode(cfg);$('out').value=url;$('out2').value=url;$('out').classList.toggle('example',!b);
$('open').hidden=!b;$('open').href=url;say('link-help',b?'Colle ce lien dans URLS, avec le type Site Web.':"Lien d'exemple : renseigne d'abord l'adresse de ta page 3D (étapes en bas de page).");}
$('copy2').addEventListener('click',()=>{const t=$('out2').value,done=()=>{$('copy2').textContent='Lien copié';setTimeout(()=>{$('copy2').textContent='Copier le lien';},1500);},sel=()=>{$('out2').focus();$('out2').select();};
try{navigator.clipboard.writeText(t).then(done,sel);}catch(e){sel();}});
$('copy').addEventListener('click',()=>{const t=$('out').value,done=()=>{$('copy').textContent='Copié';setTimeout(()=>{$('copy').textContent='Copier';},1500);},sel=()=>{$('out').focus();$('out').select();};
try{navigator.clipboard.writeText(t).then(done,sel);}catch(e){sel();}});

// Téléchargements : icône PNG et page 3D
const VIEWER_HEAD=__VIEWER_HEAD__,VIEWER_TAIL=__VIEWER_TAIL__;
let dl=null;const plainDl={save:async({filename,data})=>{const u=URL.createObjectURL(data instanceof Blob?data:new Blob([data],{type:'text/html'})),a=document.createElement('a');a.href=u;a.download=filename;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);}};
const getDl=(window.claude&&window.claude.use?window.claude.use('downloads'):Promise.resolve(null)).then(d=>d||plainDl,()=>plainDl);
getDl.then(d=>{dl=d;$('icon').disabled=$('get-viewer').disabled=!d;if(!d){say('dl-status',"Le téléchargement n'est pas disponible ici.");say('setup-status',"Le téléchargement n'est pas disponible ici.");}},()=>{});
async function save(name,data,out){try{await dl.save({filename:name,data});say(out,'Fichier enregistré : '+name+'.');}
catch(e){const c=e&&e.code;say(out,({declined:'Téléchargement annulé.',rate_limited:'Une fenêtre de téléchargement est déjà ouverte.',extension_not_enabled:'Ce type de fichier ne peut pas être téléchargé ici.'})[c]||"Le téléchargement n'est pas disponible ici.");}}
const slug=s=>(s||'peluche').normalize('NFD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_+|_+$/g,'')||'peluche';
function renderIcon(out){const S=1400,pr=r.getPixelRatio(),a=cam.aspect;r.setPixelRatio(1);r.setSize(S,S,false);cam.aspect=1;cam.updateProjectionMatrix();PL.aim(cam,cur.fit,el,1.25,camFill);r.render(scene,cam);
const[c,g]=(()=>{const cn=document.createElement('canvas');cn.width=cn.height=S;return[cn,cn.getContext('2d')];})();g.drawImage(r.domElement,0,0);r.setPixelRatio(pr);fitSize();
const px=g.getImageData(0,0,S,S).data;let x0=S,y0=S,x1=-1,y1=-1;for(let y=0;y<S;y++){const row=y*S*4;for(let x=0;x<S;x++)if(px[row+x*4+3]>6){if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}}
const w=x1-x0+1,h=y1-y0+1,k=out*0.9/Math.max(w,h),o=document.createElement('canvas');o.width=o.height=out;const og=o.getContext('2d');og.imageSmoothingQuality='high';og.drawImage(c,x0,y0,w,h,(out-w*k)/2,(out-h*k)/2,w*k,h*k);return o;}
$('icon').addEventListener('click',async()=>{if(!dl||!cur)return;$('icon').disabled=true;say('dl-status','Création de l\'icône…');const blob=await new Promise(res=>renderIcon(512).toBlob(res,'image/png'));await save(slug(cfg.n)+'.png',blob,'dl-status');$('icon').disabled=!dl;});
$('get-viewer').addEventListener('click',async()=>{if(!dl)return;await save('index.html',VIEWER_HEAD+$('pl-src').textContent.trim()+'\n'+VIEWER_TAIL,'setup-status');});

syncForm();rebuild();updateLink();
</script>
"""

def js_str(s):
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")

atelier = ATELIER.replace("__MODEL__", model.strip()).replace("__VIEWER_HEAD__", js_str(VIEWER_HEAD)).replace("__VIEWER_TAIL__", js_str(VIEWER_TAIL))
viewer = VIEWER_HEAD + model.strip() + "\n" + VIEWER_TAIL
os.makedirs(os.path.dirname(viewer_out) or ".", exist_ok=True)
open(atelier_out, "w", encoding="utf-8").write(atelier)
open(viewer_out, "w", encoding="utf-8").write(viewer)
if site_out:
    # Même atelier, en page complète pour GitHub Pages
    open(site_out, "w", encoding="utf-8").write('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' + atelier + '\n</html>\n')
print("ok", len(atelier), len(viewer))
