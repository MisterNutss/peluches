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
// Option : &tourne=non pour qu'elle ne tourne pas toute seule. Une peluche de la bibliothèque s'ouvre avec /p/son-nom.
const q=new URLSearchParams(location.search);
const scene=new THREE.Scene(),cam=new THREE.PerspectiveCamera(22,1,0.1,500);
const r=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});r.setClearColor(0x000000,0);r.setPixelRatio(1);r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;document.body.appendChild(r.domElement);
PL.setQuality(0.55);PL.setup(r);const camFill=PL.lights(scene);let P=null;
// Le lien court /p/nom est servi par la page 404 de GitHub Pages (même page que celle-ci) ; la peluche est lue sur le serveur Vercel
const API=/vercel\.app$/.test(location.hostname)?'':'https://peluches-tau.vercel.app';
const nom=q.get('nom')||decodeURIComponent((location.pathname.match(/\/p\/([^/?#]+)\/?$/)||[])[1]||'');
// Lecture directe dans le stockage Blob (rapide, pas de contrôle anti-robot), sinon par le serveur Vercel
// ?b=… : identifiant du stockage Blob, ajouté au lien par la bibliothèque ; la peluche est alors lue sans passer par Vercel
const bq=q.get('b')||'',BLOB=/^[a-z0-9]{6,40}$/.test(bq)?'https://'+bq+'.public.blob.vercel-storage.com':'',slug=nom.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,40);
// why : raison de l'échec, affichée sous le message pour comprendre ce qui bloque (réseau, serveur, lecture)
let why='';const getJ=(u,k)=>fetch(u,{cache:'no-store'}).then(x=>{if(!x.ok){why+=k+' : réponse '+x.status+'. ';return Promise.reject();}return x.json().catch(()=>{why+=k+' : réponse illisible (page de contrôle ?). ';return Promise.reject();});},e=>{if(e!==undefined)why+=k+' : injoignable. ';return Promise.reject();});
// 1) stockage Blob (toujours à jour), 2) copie sur GitHub (même site, jamais bloquée, mais en retard de quelques minutes après un enregistrement), 3) serveur Vercel
const pth=location.pathname,GH=(pth.includes('/p/')?pth.split('/p/')[0]+'/':pth.replace(/[^/]*$/,''))+'p/'+slug+'.json?t='+Date.now();
(nom?(BLOB?getJ(BLOB+'/peluches/'+slug+'.json?t='+Date.now(),'stockage'):Promise.reject()).catch(()=>getJ(GH,'github')).catch(()=>getJ(API+'/api/peluches?nom='+encodeURIComponent(slug),'serveur')).then(d=>d&&d.p?PL.unpack(d.p).then(c=>{if(!c)why+='lecture du lien impossible. ';return c;}):null).catch(()=>null):PL.unpack(q.get('p'))).then(c=>{
// Peluche de la bibliothèque introuvable : on le dit au lieu d'afficher une autre peluche
if(nom&&!c){const m=document.createElement('p');m.textContent='Peluche « '+nom+' » introuvable.'+(why?' ('+why.trim()+')':'');m.style.cssText='position:fixed;inset:auto 0 45% 0;text-align:center;font:600 18px system-ui,sans-serif;color:#888;margin:0';document.body.append(m);return;}
const cfg=c||PL.clean(PL.PRESETS.pompier);if(cfg.n)document.title=cfg.n;P=PL.build(cfg);scene.add(P.group);
// Fond choisi dans l'atelier (sinon transparent), avec sa forme : arrondi, rond ou carré
if(cfg.bg&&cfg.bg!=='aucun'){const b={k:cfg.bg,f:cfg.bf||'arrondi',c:cfg.bgc||'#ffd6e8'},cv=document.createElement('canvas');cv.width=cv.height=1024;PL.paintBg(cv.getContext('2d'),1024,b);
const d=document.createElement('div');d.style.cssText='position:fixed;inset:0;z-index:-1;background:url('+cv.toDataURL('image/jpeg',0.9)+') center/cover;border-radius:'+(b.f==='rond'?'50%':b.f==='arrondi'?'9vmin':'0');document.body.prepend(d);}});
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
// 30 images par seconde : assez fluide pour une peluche qui tourne, deux fois moins de travail
let last=0;(function loop(now){requestAnimationFrame(loop);now=now||0;if(now-last<32)return;last=now;if(autoSpin&&!pts.size&&now-idle>2500)ry+=0.012;
if(P){P.group.rotation.y=ry;PL.aim(cam,P.fit,el,zoom,camFill);r.render(scene,cam);}})();
</script>
</body>
</html>
"""

ATELIER = r"""<title>Blake & Billy</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap">
<style>
/* Layout: a toy-maker's studio — the plush on a big turntable stage pinned on the left, a tabbed workbench on the right (photos, réglages, lien); on phones the stage sits on top of the tabs. */
:root{
  --bg:#f1f7ff; --surface:#ffffff; --surface-2:#eef5ff; --fg:#2c3b57; --muted:#6c7f9f; --line:rgba(110,160,225,.25);
  --accent:#5aa2ea; --accent-soft:#e1efff; --pink:#4fbf8b; --pink-soft:#dcf5e8; --mint:#5aa2ea; --mint-soft:#e1efff; --on-accent:#ffffff; --stage-a:#f8fbff; --stage-b:#e6f1ff;
  --shadow:0 2px 4px rgba(90,162,234,.08),0 14px 34px rgba(90,162,234,.15);
  --display:"Fredoka","Trebuchet MS",system-ui,sans-serif; --body:"Nunito",system-ui,-apple-system,"Segoe UI",sans-serif; --mono:"DM Mono",ui-monospace,Consolas,monospace;
  --heart:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='72' height='72' viewBox='0 0 72 72'%3E%3Cpath d='M16 22c-3-5-11-3-10 3 1 5 10 10 10 10s9-5 10-10c1-6-7-8-10-3z' fill='%235aa2ea' fill-opacity='.1'/%3E%3Cpath d='M52 50c-2-3.5-8-2-7 2 .7 3.5 7 7 7 7s6.3-3.5 7-7c1-4-5-5.5-7-2z' fill='%234fbf8b' fill-opacity='.12'/%3E%3C/svg%3E");
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#16202f; --surface:#1f2b3d; --surface-2:#1b2636; --fg:#eaf3ff; --muted:#a6bad6; --line:rgba(160,200,255,.16);
  --accent:#8cc4ff; --accent-soft:#233a57; --pink:#7fdcae; --pink-soft:#1d3b30; --mint:#8cc4ff; --mint-soft:#233a57; --on-accent:#0f1d2e; --stage-a:#24334a; --stage-b:#1f2b3d;
  --shadow:0 2px 4px rgba(0,0,0,.3),0 14px 34px rgba(0,0,0,.35); color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#16202f; --surface:#1f2b3d; --surface-2:#1b2636; --fg:#eaf3ff; --muted:#a6bad6; --line:rgba(160,200,255,.16);
  --accent:#8cc4ff; --accent-soft:#233a57; --pink:#7fdcae; --pink-soft:#1d3b30; --mint:#8cc4ff; --mint-soft:#233a57; --on-accent:#0f1d2e; --stage-a:#24334a; --stage-b:#1f2b3d;
  --shadow:0 2px 4px rgba(0,0,0,.3),0 14px 34px rgba(0,0,0,.35); color-scheme:dark}
[hidden]{display:none!important}
body{background:var(--heart) 0 0/72px 72px,var(--bg);color:var(--fg);font-family:var(--body);font-size:16px;line-height:1.5}
.app{max-width:1360px;margin:0 auto;padding-block:20px 32px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:18px}
.top{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px}
.brand{display:flex;align-items:center;gap:12px;min-width:0}
.logo{width:64px;height:48px;flex:none}
.amp{color:var(--pink);font-weight:600}
.blake{color:var(--accent)}.billy{color:var(--pink)}
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
.stage{position:relative;width:100%;aspect-ratio:1;max-height:calc(100vh - 160px);min-height:320px;border-radius:32px;overflow:hidden;cursor:grab;touch-action:pan-y;border:1px solid var(--line);box-shadow:var(--shadow);
  background:repeating-conic-gradient(var(--stage-a) 0 25%,var(--stage-b) 0 50%) 0 0/28px 28px}
.stage.drag{cursor:grabbing}
.stage canvas{display:block;width:100%;height:100%}
.stage-bar{position:absolute;top:12px;left:12px;right:12px;display:flex;flex-wrap:wrap;gap:6px;justify-content:space-between;pointer-events:none}
.grp{display:flex;gap:2px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:4px;pointer-events:auto;box-shadow:var(--shadow)}
.grp button:disabled{opacity:.35;cursor:default}
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
.card{background:var(--surface);border:1px solid var(--line);border-radius:26px;padding:18px 20px;display:grid;gap:12px;min-width:0;box-shadow:var(--shadow)}
h2{font-family:var(--display);font-weight:600;font-size:19px;line-height:1.2;margin:0;color:var(--fg)}
h2::before{content:'♡ ';color:var(--pink)}
label{font-size:14px;color:var(--muted);font-weight:700}
textarea{font:16px/1.4 var(--body);padding:10px 14px;border-radius:16px;border:1px solid var(--line);background:var(--surface-2);color:var(--fg);width:100%;box-sizing:border-box;resize:vertical;min-height:84px}
input[type=text],input[type=url],input[type=password],select{font:16px var(--body);padding:10px 14px;border-radius:16px;border:1px solid var(--line);background:var(--surface-2);color:var(--fg);width:100%;min-width:0;box-sizing:border-box}
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
.flags{display:grid;gap:12px}
.fgroup{display:grid;gap:6px}.fgroup>span{font:600 13px var(--display);color:var(--muted);letter-spacing:.02em}
.pills{display:flex;flex-wrap:wrap;gap:6px}
.pills .check{font-size:14px;padding:7px 13px;border-radius:999px;border:1px solid var(--line);background:var(--surface-2);gap:6px}
.pills .check:has(input:checked){background:var(--accent-soft);border-color:var(--accent);color:var(--accent)}
.pills .check input{position:absolute;opacity:0;width:1px;height:1px}
.pills .check:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:2px}
.seg.small .btn{padding:8px 12px;font-size:13px}
details.card>summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:10px;margin:-4px 0}
details.card>summary::-webkit-details-marker{display:none}
details.card>summary::after{content:'';flex:none;width:9px;height:9px;border-right:2.5px solid var(--muted);border-bottom:2.5px solid var(--muted);transform:rotate(45deg);transition:transform .15s;margin:0 6px 4px 0}
details.card[open]>summary::after{transform:rotate(-135deg);margin-bottom:-4px}
details.card:not([open]){padding-block:16px}
details.more{border-top:1px dashed var(--line);padding-top:10px}
details.more>summary{cursor:pointer;font:700 14px var(--body);color:var(--accent);list-style:none;display:inline-flex;align-items:center;gap:6px}
details.more>summary::-webkit-details-marker{display:none}
details.more>summary::before{content:'＋';font-weight:800}
details.more[open]>summary::before{content:'－'}
details.more>.fields{margin-top:12px}
@media (prefers-reduced-motion:reduce){details.card>summary::after{transition:none}}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(88px,1fr));gap:8px}
.tile{display:grid;justify-items:center;align-content:start;gap:4px;padding:10px 4px 9px;border-radius:18px;border:1px solid var(--line);background:var(--surface-2);color:var(--fg);font:700 12px/1.15 var(--body);text-align:center;cursor:pointer;transition:transform .12s,border-color .12s,background .12s}
.tile .em{font-size:26px;line-height:1.1}
.tile:hover{border-color:var(--accent);transform:translateY(-1px)}
.tile[aria-pressed="true"]{background:var(--accent-soft);border-color:var(--accent);color:var(--accent);box-shadow:0 0 0 2px var(--accent-soft)}
.lbl{font-size:14px;color:var(--muted);font-weight:700}
@media (prefers-reduced-motion:reduce){.tile{transition:none}.tile:hover{transform:none}}
.btn,.pip{font:700 14px/1 var(--body);padding:10px 15px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--fg);cursor:pointer;white-space:nowrap;text-decoration:none}
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
      <svg class="logo" viewBox="0 0 64 48" aria-hidden="true"><g><circle cx="10" cy="12" r="5.5" fill="var(--accent)"/><circle cx="26" cy="12" r="5.5" fill="var(--accent)"/><circle cx="18" cy="24" r="13" fill="var(--accent)"/><circle cx="18" cy="28" r="5.5" fill="var(--accent-soft)"/><circle cx="13.5" cy="22" r="1.8" fill="var(--fg)"/><circle cx="22.5" cy="22" r="1.8" fill="var(--fg)"/></g><g><circle cx="38" cy="16" r="5.5" fill="var(--pink)"/><circle cx="54" cy="16" r="5.5" fill="var(--pink)"/><circle cx="46" cy="28" r="13" fill="var(--pink)"/><circle cx="46" cy="32" r="5.5" fill="var(--pink-soft)"/><circle cx="41.5" cy="26" r="1.8" fill="var(--fg)"/><circle cx="50.5" cy="26" r="1.8" fill="var(--fg)"/></g><path d="M32 41c-2-3-6-2-5 1 .5 2 5 5 5 5s4.5-3 5-5c1-3-3-4-5-1z" fill="var(--pink)"/></svg>
      <div><h1><span class="blake">Blake</span> <span class="amp">&amp;</span> <span class="billy">Billy</span></h1><p>L'atelier des peluches toutes douces ♡ faites d'après une photo, pour tes items FiveM.</p></div>
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
          <div class="grp"><button type="button" id="undo" title="Annuler" aria-label="Annuler" disabled>↶</button><button type="button" id="redo" title="Rétablir" aria-label="Rétablir" disabled>↷</button><button type="button" id="v-spin" aria-pressed="false">Tourner</button></div>
        </div>
        <p class="stage-status" id="stage-status" aria-live="polite"></p>
      </div>
      <div class="quick"><input id="out2" type="text" readonly aria-label="Lien de cette peluche"><button class="btn" id="copy2" type="button">Copier le lien</button></div>
    </section>
    <section class="panel no-photo" id="right">
      <nav class="tabs" role="tablist" aria-label="Réglages de la peluche">
        <button type="button" role="tab" data-tab="photos">📷 Photos</button>
        <button type="button" role="tab" data-tab="style">🧸 Style et pose</button>
        <button type="button" role="tab" data-tab="visage">😊 Visage</button>
        <button type="button" role="tab" data-tab="tete">💇 Tête</button>
        <button type="button" role="tab" data-tab="tenue">👕 Tenue</button>
        <button type="button" role="tab" data-tab="accessoires">🎀 Accessoires</button>
        <button type="button" role="tab" data-tab="lien">🔗 Lien</button>
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
            <div class="field" id="fix-box" hidden><label for="fix-txt">💬 Quelque chose ne va pas ? Dis-le à Claude</label>
            <textarea id="fix-txt" maxlength="800" placeholder="Par exemple : elle n'a pas le ventre à l'air, les cheveux sont rose uni sans mèches, le jean est plus clair, ajoute ses piercings…"></textarea>
            <div class="row"><button class="btn" id="fix-go" type="button">Corriger avec Claude</button></div></div>
          </section>
        </div>
        <div class="tabpanel" data-tab="style" id="tab-style" hidden>
                    <section class="card"><h2>Reprendre une peluche</h2><p class="help">Colle le lien d'une peluche déjà faite pour la modifier.</p>
            <div class="row"><input id="import" type="text" placeholder="https://misternutss.github.io/peluches/p/nom" autocomplete="off" spellcheck="false" aria-label="Lien d'une peluche"><button class="btn" id="import-go" type="button">Ouvrir</button></div><p class="status" id="import-status" aria-live="polite"></p></section>
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
            <div class="field"><label for="edit">Lien pour la modifier plus tard (atelier GitHub)</label><div class="row"><input id="edit" type="text" readonly><button class="btn" id="copy-edit" type="button">Copier</button></div></div>
            <p class="help">Envoie ce lien à quelqu'un : la peluche s'ouvre dans l'atelier, prête à être modifiée, sans compte Claude.</p>
            <div class="field"><span class="lbl">Fond (icône et page 3D)</span><div class="tiles" id="ibg" role="group"></div></div>
            <div class="fields"><div class="field"><span class="help">Forme</span><div class="seg small" id="ishape"></div></div>
            <div class="field" id="ibgc-f"><label for="ibgc">Couleur du fond</label><input id="ibgc" type="color" value="#ffd6e8"></div></div>
            <canvas id="ibg-prev" width="256" height="256" style="width:128px;height:128px;border-radius:12px;background:repeating-conic-gradient(var(--stage-a) 0 25%,var(--stage-b) 0 50%) 0 0/16px 16px" aria-label="Aperçu de l'icône"></canvas>
            <div class="row"><a class="btn" id="open" target="_blank" rel="noopener" hidden>Ouvrir la page</a><button class="btn" id="icon" type="button" disabled>Télécharger l'icône PNG</button></div>
            <p class="status" id="dl-status" aria-live="polite"></p>
          </section>
          <section class="card" id="lib-card" hidden>
            <h2>Bibliothèque</h2>
            <p class="help">Enregistre la peluche sous un nom : elle rejoint ta bibliothèque et reçoit un lien très court.</p>
            <div class="fields"><div class="field"><label for="lib-nom">Nom</label><input id="lib-nom" type="text" maxlength="40" autocomplete="off"></div>
            <div class="field" id="lib-code-f"><label for="lib-code">Code secret</label><input id="lib-code" type="password" autocomplete="off"></div></div>
            <div class="row"><button class="cta" id="lib-save" type="button">Enregistrer dans la bibliothèque</button><a class="btn" id="lib-open" href="bibliotheque">Ouvrir la bibliothèque</a></div>
            <p class="help" id="lib-code-ok" hidden>🔒 Code secret retenu sur cet appareil. <a href="#" id="lib-code-chg">Changer de code</a></p>
            <div class="field" id="lib-link" hidden><label for="lib-out">Lien court de cette peluche</label><div class="row"><input id="lib-out" type="text" readonly><button class="btn" id="lib-copy" type="button">Copier</button></div></div>
            <div class="field" id="lib-ico" hidden><label for="lib-ico-out">Icône pour « Icône URL personnalisé »</label><div class="row"><input id="lib-ico-out" type="text" readonly><button class="btn" id="lib-ico-copy" type="button">Copier</button></div></div>
            <p class="status" id="lib-status" aria-live="polite"></p>
          </section>
          <section class="card setup">
            <h2>Ton site</h2>
            <ol>
              <li>Les peluches s'affichent depuis <code>https://misternutss.github.io/peluches/</code> (GitHub Pages, sans contrôle anti-robot, donc fiable dans FiveM).</li>
              <li>L'atelier public est à <code>https://peluches-tau.vercel.app/atelier</code> et la bibliothèque à <code>https://peluches-tau.vercel.app/bibliotheque</code>.</li>
              <li>Chaque peluche est entièrement décrite dans son lien ; une peluche enregistrée dans la bibliothèque a en plus un lien court <code>https://misternutss.github.io/peluches/p/son-nom</code>.</li>
              <li>Pour remettre la page 3D à jour à la main : <button class="btn" id="get-viewer" type="button" disabled>Télécharger index.html</button></li>
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
var busy=false;const say=(id,t)=>{$(id).textContent=t;if(id==='ai-status'&&$('stage-status'))$('stage-status').textContent=busy?t:'';};

// Aperçu 3D
const reduceMotion=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;let spin=false;
const stage=$('stage'),scene=new THREE.Scene(),cam=new THREE.PerspectiveCamera(22,1,0.1,500);
const r=new THREE.WebGLRenderer({antialias:true,alpha:true,preserveDrawingBuffer:true});r.setClearColor(0x000000,0);r.shadowMap.enabled=true;r.shadowMap.type=THREE.PCFSoftShadowMap;stage.prepend(r.domElement);
PL.setup(r);const camFill=PL.lights(scene);PL.HOOKS.onTex=()=>{dirty=true;};
let cfg=PL.clean(PL.NEUTRAL),cur=null,ry=-0.25,el=0.24,dirty=true,drag=false,lx=0,ly=0;
function fitSize(){const w=stage.clientWidth||480,h=stage.clientHeight||480;r.setPixelRatio(Math.min(2,window.devicePixelRatio||1));r.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();dirty=true;}
fitSize();if(window.ResizeObserver)new ResizeObserver(fitSize).observe(stage);window.addEventListener('resize',fitSize);
// Historique des réglages pour annuler / rétablir
let hist=[],hi=-1,restoring=false;
function record(){const t=JSON.stringify(cfg);if(hist[hi]===t)return;hist=hist.slice(0,hi+1);hist.push(t);if(hist.length>80)hist.shift();hi=hist.length-1;updUndo();}
function updUndo(){$('undo').disabled=hi<=0;$('redo').disabled=hi>=hist.length-1;}
function goHist(d){const n=hi+d;if(n<0||n>=hist.length)return;hi=n;cfg=JSON.parse(hist[hi]);restoring=true;syncForm();rebuild();updateLink();restoring=false;updUndo();}
function rebuild(){if(cur){scene.remove(cur.group);cur.dispose();}cur=PL.build(cfg);scene.add(cur.group);dirty=true;if(!restoring)record();if(curTab==='lien'&&window.ibgSync)setTimeout(ibgSync,0);}
let rbT=0;function changed(){updateLink();clearTimeout(rbT);rbT=setTimeout(rebuild,140);}
stage.addEventListener('pointerdown',e=>{if(e.target.closest('button'))return;drag=true;lx=e.clientX;ly=e.clientY;stage.classList.add('drag');});
window.addEventListener('pointermove',e=>{if(!drag)return;ry+=(e.clientX-lx)*0.01;el=Math.min(0.8,Math.max(-0.15,el+(e.clientY-ly)*0.006));lx=e.clientX;ly=e.clientY;dirty=true;});
const up=()=>{drag=false;stage.classList.remove('drag');};window.addEventListener('pointerup',up);window.addEventListener('pointercancel',up);
$('undo').addEventListener('click',()=>goHist(-1));$('redo').addEventListener('click',()=>goHist(1));
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&!/^(INPUT|SELECT|TEXTAREA)$/.test((document.activeElement||{}).tagName||'')){if(e.key==='z'&&!e.shiftKey){e.preventDefault();goHist(-1);}else if(e.key==='y'||(e.key==='z'&&e.shiftKey)||e.key==='Z'){e.preventDefault();goHist(1);}}});
stage.addEventListener('dblclick',()=>{ry=-0.25;el=0.24;dirty=true;});
(function loop(){if(spin&&!drag&&!reduceMotion){ry+=0.008;dirty=true;}if(dirty&&cur){cur.group.rotation.y=ry;PL.aim(cam,cur.fit,el,1.16,camFill);r.render(scene,cam);dirty=false;}requestAnimationFrame(loop);})();

// Réglages
const CHOICES={hs:{court:'Courts',banane:'Banane (plaqués en arrière)',meches:'Mi-longs en mèches',herisse:'Hérissés',iroquoise:'Iroquoise',carre:'Carré',long:'Longs',tresse:"Tresse sur l'épaule",couettes:'Couettes',queue:'Queue de cheval',chignon:'Chignon',boucle:'Bouclés',afro:'Afro',dreads:'Dreads',rase:'Rasés',chauve:'Chauve'},
bd:{aucune:'Aucune',barbe3j:'Barbe de 3 jours',barbe:'Barbe',longue:'Barbe longue',moustache:'Moustache',bouc:'Bouc'},ex:{sourire:'Grand sourire',content:'Petit sourire',rire:'Rire',clin:"Clin d'œil",amour:'Yeux en cœur',etoiles:'Yeux étoiles',langue:'Tire la langue',bisou:'Bisou',surpris:'Surpris',gene:'Gêné',neutre:'Neutre',serieux:'Sérieux',boude:'Boude',triste:'Triste',pleure:'Pleure',dodo:'Endormi'},
gl:{aucune:'Aucunes',lunettes:'Lunettes de vue',soleil:'Lunettes de soleil',aviateur:'Lunettes aviateur',tete:'Lunettes relevées sur la tête',masque:'Lunettes de protection',coeur:'Lunettes cœur',rondes:'Rondes rétro',etoile:'Lunettes étoiles'},
hw:{aucun:'Aucun',capuche:'Capuche relevée',casquette:'Casquette',inverse:"Casquette à l'envers",bonnet:'Bonnet',chapeau:'Chapeau',bandeau:'Bandeau',durag:'Durag',beret:'Béret',bob:'Bob',cowboy:'Chapeau de cowboy',fleurs:'Couronne de fleurs',pompier:'Casque de pompier',police:'Casquette de police'},
tp:{tshirt:'T-shirt',chemise:'Chemise',sweat:'Sweat à capuche',zip:'Veste zippée fermée (survêtement)',veste:'Veste ouverte',costume:'Costume',gilet:'Gilet sur manches',debardeur:'Débardeur (sans manches)',dosnu:'Haut dos nu (bretelle au cou)',bandeau:'Haut bandeau (sans bretelles)',polo:'Polo',pull:'Pull en maille',maillot:'Maillot de sport (numéro)',doudoune:'Doudoune',cuir:'Veste en cuir',cardigan:'Cardigan ouvert',manteau:'Manteau long'},mt:{uni:'Uni',rayures:'Rayures',camo:'Camouflage',carreaux:'Carreaux',taches:'Taches',pois:'Pois',coeurs:'Cœurs',etoiles:'Étoiles',fleurs:'Fleurs',leopard:'Léopard',zebre:'Zèbre',tiedye:'Tie-dye',jean:'Toile de jean'},
bt:{pantalon:'Pantalon',jean:'Jean',cargo:'Cargo (poches sur les côtés)',jogging:'Jogging',short:'Short',salopette:'Salopette',jupe:'Jupe',longue:'Jupe longue',robe:'Robe (couleur du haut)'},sh:{bottes:'Bottes',baskets:'Baskets',chaussures:'Chaussures de ville',talons:'Talons',chaussons:'Chaussons tout doux',sandales:'Sandales',claquettes:'Claquettes-chaussettes',crocs:'Crocs'},
it:{aucun:'Rien',lance:'Lance à incendie',coeur:'Cœur',telephone:'Téléphone',cafe:'Café',donut:'Donut',trousse:'Trousse de secours',bouquet:'Bouquet de fleurs',billets:'Liasse de billets',manette:'Manette de jeu',ballon:'Ballon de basket',cle:'Clé de voiture',micro:'Micro de chanteur',glace:'Glace',sucette:'Sucette',cadeau:'Cadeau',livre:'Livre',pizza:'Pizza',poisson:'Poisson',baguette:'Baguette',banane:'Banane',poele:'Poêle',papier:'Papier toilette',biberon:'Biberon',bonbon:'Bonbon',coussin:'Coussin cœur'}};
CHOICES.hm=CHOICES.mt;
CHOICES.hp={aucune:'Pas de raie',gauche:"Raie à gauche de l'image",milieu:'Raie au milieu',droite:"Raie à droite de l'image"};
CHOICES.hf={aucune:'Pas de frange (coiffés en arrière ou sur les côtés)',courte:'Frange courte',droite:'Frange droite (au ras des sourcils)',balayee:'Frange balayée sur le côté',rideau:'Frange rideau (ouverte au milieu)',longue:'Frange longue (sur les yeux)',arriere:'Relevés en arrière (banane, houppe)'};
CHOICES.hx={lisse:'Lisses',ondule:'Ondulés',boucle:'Bouclés',crepu:'Crépus (afro)',pique:'En pics',dreads:'Dreadlocks'};
CHOICES.ml={longues:'Longues',coudes:'Retroussées aux coudes',courtes:'Courtes'};
CHOICES.ht={aucune:'Détachés',queue:'Queue de cheval basse',haute:'Queue de cheval haute',couettes:'Deux couettes',chignon:'Chignon',tresse:"Tresse sur l'épaule",demi:'Demi-queue (dessus attaché)',macarons:'Deux chignons en haut (macarons)'};
CHOICES.hd={normaux:'Comme le reste',courts:'Courts (dégradé)',rases:'Rasés'};
CHOICES.ms={aucune:'Aucune',monstre:'Petit monstre (oreilles et dents)',lapin:'Lapin',ours:'Ours',chat:'Chat',chien:'Chien',oiseau:'Oiseau / perroquet'};
CHOICES.po={assis:'Assise',debout:'Debout',coucou:'Coucou',bravo:'Bras levés',calin:'Câlin',coeur:'Cœur',pensif:'Pensive',tailleur:'En tailleur',dab:'Dab',joues:'Mains sur les joues',danse:'Danse',victoire:'Victoire',croises:'Bras croisés',bisou:'Envoie un bisou',salut:'Coucou assise'};
CHOICES.ey={kawaii:'Mignons (peluche)',realiste:'Réalistes'};
CHOICES.cos={aucun:'Aucune',ours:'Ours',lapin:'Lapin',chat:'Chat',renard:'Renard',grenouille:'Grenouille',dino:'Dino',licorne:'Licorne',panda:'Panda',cochon:'Cochon',poussin:'Poussin',requin:'Requin',vache:'Vache'};
CHOICES.st={classique:'Classique',ours:'Ourson',lapin:'Lapin',chat:'Chaton',monstre:'Petit monstre',avatar:'Avatar',figurine:'Figurine (jouet de collection)'};
CHOICES.mp={droite:"Sur l'épaule, à droite de l'image",gauche:"Sur l'épaule, à gauche de l'image",tete:'Sur la tête',mains:'Dans les mains'};
const FLAGS={m:'🎧 Micro-casque',o:"💎 Boucles d'oreilles",a:'😷 Bandana sur le visage',q:'🎀 Nœud dans les cheveux',f:'🌼 Fleur dans les cheveux',x:'👑 Couronne',j:'🐱 Oreilles de chat',M:'🐰 Oreilles de lapin',A:'👽 Antennes',B:'😈 Cornes de diable',C:'😇 Auréole',L:'🦄 Corne de licorne',D:'🧢 Casquette à hélice',R:'🎀 Bigoudis',T:'🏴‍☠️ Cache-œil',E:'🩹 Pansement',
P:'🍎 Pomme sur la tête',Q:'🦆 Canard sur la tête',V:'🚧 Cône sur la tête',N:'🏹 Flèche dans la tête',G:'🥸 Faux nez et moustache',H:'🫧 Bulle de chewing-gum',S:'💕 Cœurs qui flottent',Y:'✨ Paillettes',I:'🥳 Chapeau de fête',U:'🌧️ Nuage de pluie',K:'💫 Étoiles qui tournent',W:'💡 Ampoule idée',O:'🍼 Tétine',X:'🖤 Harnais croisé',F:'🎧 Casque audio sur la tête',J:'💍 Piercings au nez',
r:'📻 Radio',b:'⭐ Badge',c:'📿 Chaîne en or',d:'🏷️ Plaques militaires',e:'🧣 Écharpe',h:'🎧 Casque audio au cou',p:'📍 Pins',n:'👜 Sac en bandoulière',t:'🎩 Nœud papillon',
s:'💼 Sacoche',u:'👝 Sac banane',v:'🔫 Étui à la ceinture',y:'🔦 Lampe torche',z:'⛓️ Menottes',w:'⌚ Montre',l:'📿 Bracelets',k:'🎒 Sac à dos',i:"🪽 Ailes d'ange",g:'🦸 Cape'};
const FLAG_GROUPS=[['Tête et visage','moaqfxjMACBLDRTEJF'],['Pipou et magique','SYI'],['Pour rigoler','PQVNGHUKWO'],['Haut du corps','rbcdehpntX'],['Ceinture','suvyz'],['Bras et dos','wlkig']];
// Émoji des tuiles : on voit le choix d'un coup d'œil
const EMO={ex:{sourire:'😄',content:'🙂',rire:'😆',clin:'😉',amour:'😍',etoiles:'🤩',langue:'😛',bisou:'😘',surpris:'😮',neutre:'😐',gene:'😳',serieux:'😠',triste:'😢',pleure:'😭',boude:'😤',dodo:'😴'},
po:{assis:'🧸',debout:'🧍',coucou:'👋',salut:'🙋',bravo:'🙌',calin:'🤗',coeur:'🫶',pensif:'🤔',tailleur:'🧘',dab:'🕺',joues:'🥰',danse:'💃',victoire:'✌️',croises:'🙅',bisou:'😘'},
it:{aucun:'🚫',lance:'🚒',coeur:'❤️',telephone:'📱',cafe:'☕',donut:'🍩',trousse:'🩹',bouquet:'💐',billets:'💵',manette:'🎮',ballon:'🏀',cle:'🔑',micro:'🎤',glace:'🍦',sucette:'🍭',cadeau:'🎁',livre:'📖',pizza:'🍕',poisson:'🐟',baguette:'🥖',banane:'🍌',poele:'🍳',papier:'🧻',biberon:'🍼',bonbon:'🍬',coussin:'💗'},
hw:{aucun:'🚫',capuche:'🧥',casquette:'🧢',inverse:'🧢',bonnet:'🧶',chapeau:'🎩',bandeau:'🎽',durag:'🖤',beret:'🎨',bob:'👒',cowboy:'🤠',fleurs:'🌸',pompier:'⛑️',police:'👮'},
gl:{aucune:'🚫',lunettes:'👓',soleil:'🕶️',aviateur:'😎',tete:'🕶️',masque:'🥽',coeur:'💖',rondes:'🤓',etoile:'⭐'},
cos:{aucun:'🚫',ours:'🐻',lapin:'🐰',chat:'🐱',renard:'🦊',grenouille:'🐸',dino:'🦖',licorne:'🦄',panda:'🐼',cochon:'🐷',poussin:'🐥',requin:'🦈',vache:'🐮'},
st:{classique:'🧒',ours:'🐻',lapin:'🐰',chat:'🐱',monstre:'👹',avatar:'🙂',figurine:'🪆'},
ms:{aucune:'🚫',monstre:'👹',lapin:'🐰',ours:'🐻',chat:'🐱',chien:'🐶',oiseau:'🦜'}};
const hairOn=c=>!['rase','chauve','iroquoise'].includes(c.hs);
const SECTIONS=[
{t:'Style, pose et nom',f:[{k:'st',type:'tiles',l:'Style de peluche',wide:1},{k:'cos',type:'tiles',l:"Combinaison d'animal (capuche, oreilles, queue)",wide:1},{k:'coc',type:'optcolor',l:'Couleur de la combinaison à part',show:c=>c.cos&&c.cos!=='aucun'},{k:'po',type:'tiles',l:'Position',wide:1},{k:'fc',type:'color',l:'Couleur de la fourrure',show:c=>['ours','lapin','chat','monstre','figurine'].includes(c.st)},{k:'n',type:'text',l:'Nom',max:24,wide:1}]},
{t:'Visage',f:[{k:'ey',type:'chips',l:'Yeux',wide:1},{k:'sk',type:'color',l:'Peau'},{k:'ec',type:'color',l:'Yeux'},{k:'ex',type:'tiles',wide:1,l:'Expression'},{k:'ta',type:'check',l:'Tatouages sur les bras'},{k:'bd',type:'choice',l:'Barbe'},{k:'fr',adv:1,type:'check',l:'Taches de rousseur'},{k:'cl',adv:1,type:'check',l:'Longs cils'}]},
{t:'Cheveux',f:[{k:'hs',type:'choice',l:'Coiffure de départ'},{k:'hc',type:'color',l:'Couleur des cheveux'},{k:'h2',adv:1,type:'optcolor',l:"Mèches d'une autre couleur",show:hairOn},
{k:'hl',type:'range',l:'Longueur',min:0.3,max:5,step:0.1,fmt:'len',show:hairOn},{k:'hv',adv:1,type:'range',l:'Volume',min:0,max:1,step:0.05,fmt:'pct',show:hairOn},
{k:'hx',type:'choice',l:'Texture',show:hairOn},{k:'hp',adv:1,type:'choice',l:'Raie',show:hairOn},{k:'hf',type:'choice',l:'Frange',show:hairOn},{k:'ht',adv:1,type:'choice',l:'Attache',show:hairOn},{k:'hd',adv:1,type:'choice',l:'Côtés et nuque',show:hairOn}]},
{t:'Couvre-chef',f:[{k:'hw',type:'tiles',wide:1,l:'Couvre-chef'},{k:'hwc',type:'color',l:'Couleur du couvre-chef',show:c=>c.hw!=='aucun'},{k:'hwt',type:'text',l:'Texte ou numéro',max:6,show:c=>['casquette','bonnet','pompier'].includes(c.hw)},{k:'hm',adv:1,type:'choice',l:'Motif du couvre-chef',show:c=>['capuche','casquette','inverse','chapeau'].includes(c.hw)}]},
{t:'Lunettes',f:[{k:'gl',type:'tiles',wide:1,l:'Lunettes'},{k:'glc',type:'color',l:'Monture',show:c=>c.gl!=='aucune'},{k:'lc',type:'color',l:'Couleur des verres',show:c=>['soleil','aviateur','tete'].includes(c.gl)}]},
{t:'Haut',f:[{k:'tp',type:'choice',l:'Haut'},{k:'ml',type:'choice',l:'Manches',show:c=>!['tshirt','debardeur','dosnu','bandeau'].includes(c.tp)},{k:'cr',type:'check',l:'Haut court (ventre visible)',show:c=>c.tp!=='costume'},{k:'cc',type:'check',l:'Col roulé',show:c=>!['costume','dosnu','bandeau'].includes(c.tp)},{k:'mt',type:'choice',l:'Motif'},{k:'tc',type:'color',l:c=>({gilet:'Gilet',veste:'Veste',costume:'Veste de costume'})[c.tp]||'Couleur du haut'},
{k:'t2',type:'color',l:c=>({gilet:'Manches',veste:'Haut en dessous',costume:'Chemise',sweat:'Cordons'})[c.tp]||'Dessous',show:c=>['gilet','veste','costume','sweat'].includes(c.tp)},
{k:'yc',adv:1,type:'optcolor',l:"Épaules d'une autre couleur",show:c=>!['veste','costume','gilet'].includes(c.tp)},{k:'sl',adv:1,type:'optcolor',l:"Manches d'une autre couleur",show:c=>c.tp!=='gilet'},{k:'sb',adv:1,type:'optcolor',l:'Bandes sur les manches',show:c=>c.tp!=='tshirt'},
{k:'im',type:'print',l:'Imprimé sur le devant (découpé dans la photo)',wide:1,show:c=>c.tp!=='costume'},{k:'imf',type:'check',l:"Utiliser l'imprimé comme motif sur tout le haut",show:c=>!!c.im&&c.tp!=='costume'},{k:'tt',adv:1,type:'text',l:'Texte imprimé (dos)',max:8},{k:'rf',adv:1,type:'check',l:'Bandes réfléchissantes'},]},
{t:'Bas et chaussures',f:[{k:'bt',type:'choice',l:'Bas'},{k:'pc',type:'color',l:c=>c.bt==='short'?'Couleur du short':'Couleur du bas'},{k:'pb',adv:1,type:'optcolor',l:'Bandes sur les côtés du bas',show:c=>c.bt!=='short'},
{k:'sh',type:'choice',l:'Chaussures'},{k:'sc',type:'color',l:'Couleur des chaussures'},{k:'gv',adv:1,type:'glove',l:'Gants'}]},
{t:'Accessoires',f:[{k:'acc',type:'flags',l:'Équipement',wide:1},{k:'ac',type:'color',l:"Couleur d'accent (par défaut pour tous les accessoires)"}]},
{t:'Dans les mains',f:[{k:'it',type:'tiles',wide:1,l:'Objet'}]},
{t:'Mascotte',f:[{k:'ms',type:'tiles',wide:1,l:'Mascotte (mini-peluche)'},{k:'mc',type:'color',l:'Couleur de la mascotte',show:c=>c.ms!=='aucune'},{k:'mp',type:'choice',l:'Place de la mascotte',show:c=>c.ms!=='aucune'},{k:'mz',type:'range',l:'Taille de la mascotte',min:0.5,max:2,step:0.05,show:c=>c.ms!=='aucune'},{k:'mx',adv:1,type:'range',l:'Mascotte : gauche / droite',min:-1,max:1,step:0.05,fmt:'off',show:c=>c.ms!=='aucune'},{k:'my',adv:1,type:'range',l:'Mascotte : bas / haut',min:-1,max:1,step:0.05,fmt:'off',show:c=>c.ms!=='aucune'},{k:'mf',adv:1,type:'range',l:'Mascotte : arrière / avant',min:-1,max:1,step:0.05,fmt:'off',show:c=>c.ms!=='aucune'},{k:'mr',adv:1,type:'range',l:'Mascotte : rotation',min:-180,max:180,step:5,fmt:'deg',show:c=>c.ms!=='aucune'}]}];
const F={};let lastGlove='#86ace6';const lastOpt={coc:'#9a6a46',h2:'#f3dc9a',yc:'#f2f2f2',sl:'#f2f2f2',sb:'#f2f2f2',pb:'#1c1c1e'};
function el2(tag,props,kids){const n=document.createElement(tag);Object.assign(n,props||{});(kids||[]).forEach(k=>n.append(k));return n;}
function colorRow(k,id){return el2('div',{className:'colorrow'},[el2('input',{type:'color',id}),el2('button',{type:'button',className:'pip',textContent:'Pipette',title:'Prendre la couleur sur la photo'})]);}
const TAB_OF={'Style, pose et nom':'style',Visage:'visage',Cheveux:'tete','Couvre-chef':'tete',Lunettes:'tete',Haut:'tenue','Bas et chaussures':'tenue',Accessoires:'accessoires','Dans les mains':'accessoires',Mascotte:'accessoires'};
// Cartes repliables : la première de chaque onglet est ouverte, le navigateur se souvient du reste
function foldCard(title,kids,first,id){const d=el2('details',{className:'card'});if(id)d.id=id;const st=store('peluches-ouvert-'+title);d.open=st===null?!!first:st==='1';
d.addEventListener('toggle',()=>store('peluches-ouvert-'+title,d.open?'1':'0'));d.append(el2('summary',{},[el2('h2',{textContent:title})]),...kids);return d;}
for(const sec of SECTIONS){const grid=el2('div',{className:'fields'}),tab=$('tab-'+TAB_OF[sec.t]),first=!tab.querySelector('details.card');let adv=null;const card=foldCard(sec.t,[grid],first);tab.append(card);
for(const f of sec.f){const id='f-'+f.k,row=el2('div',{className:'field'+(f.wide?' wide':'')});const lab=el2('label',{htmlFor:id});f.lab=lab;
if(f.type==='color'){row.append(lab,colorRow(f.k,id));row.querySelector('.pip').dataset.pip=f.k;}
else if(f.type==='choice'&&Object.keys(CHOICES[f.k]).length<=6){f.type='chips';const g=el2('div',{className:'seg small',id});for(const[v,t]of Object.entries(CHOICES[f.k])){const b=el2('button',{type:'button',className:'btn',textContent:t});b.dataset.v=v;g.append(b);}row.append(lab,g);lab.htmlFor='';}
else if(f.type==='choice'){const s=el2('select',{id});for(const[v,t]of Object.entries(CHOICES[f.k]))s.append(el2('option',{value:v,textContent:t}));row.append(lab,s);}
else if(f.type==='text'){row.append(lab,el2('input',{type:'text',id,maxLength:f.max,autocomplete:'off'}));}
else if(f.type==='check'){row.append(el2('label',{className:'check'},[el2('input',{type:'checkbox',id}),f.l]));f.lab=null;}
else if(f.type==='glove'){row.append(el2('label',{className:'check'},[el2('input',{type:'checkbox',id:id+'-on'}),'Gants']),colorRow(f.k,id));row.querySelector('.pip').dataset.pip=f.k;f.lab=null;}
else if(f.type==='optcolor'){row.append(el2('label',{className:'check'},[el2('input',{type:'checkbox',id:id+'-on'}),f.l]),colorRow(f.k,id));row.querySelector('.pip').dataset.pip=f.k;f.lab=null;}
else if(f.type==='range'){row.append(el2('div',{className:'row rangehead'},[lab,el2('span',{className:'help',id:id+'-v'})]),el2('input',{type:'range',id,min:f.min,max:f.max,step:f.step}));}
else if(f.type==='print'){const im=el2('img',{id:id+'-img',alt:'Imprimé pris sur la photo',className:'printimg'});row.append(el2('span',{className:'help',textContent:f.l}),el2('div',{className:'row'},[im,el2('button',{type:'button',className:'btn',id:id+'-pick',textContent:'Choisir sur la photo'}),el2('button',{type:'button',className:'btn',id:id+'-rm',textContent:'Retirer'})]));f.lab=null;}
else if(f.type==='tiles'){f.type='chips';const g=el2('div',{className:'tiles',id,role:'group'});for(const[v,t]of Object.entries(CHOICES[f.k])){const b=el2('button',{type:'button',className:'tile'},[el2('span',{className:'em',textContent:(EMO[f.k]||{})[v]||'•'}),el2('span',{textContent:t})]);b.dataset.v=v;g.append(b);}row.append(el2('span',{className:'lbl',textContent:typeof f.l==='function'?f.l(cfg):f.l}),g);f.lab=null;}
else if(f.type==='chips'){const g=el2('div',{className:'seg',id});for(const[v,t]of Object.entries(CHOICES[f.k])){const b=el2('button',{type:'button',className:'btn',textContent:t});b.dataset.v=v;g.append(b);}row.append(el2('span',{className:'help',textContent:f.l}),g);f.lab=null;}
else if(f.type==='flags'){row.append(el2('span',{className:'help',textContent:f.l}),el2('div',{className:'flags'},FLAG_GROUPS.map(([gt,ks])=>el2('div',{className:'fgroup'},[el2('span',{textContent:gt}),el2('div',{className:'pills'},[...ks].map(v=>el2('label',{className:'check'},[el2('input',{type:'checkbox',id:id+'-'+v,value:v}),FLAGS[v]])))]))));f.lab=null;}
f.row=row;F[f.k]=f;if(f.adv){if(!adv){adv=el2('div',{className:'fields'});card.append(el2('details',{className:'more'},[el2('summary',{textContent:'Plus de réglages'}),adv]));}adv.append(row);}else grid.append(row);}}
function syncForm(){const HV=PL.hair(cfg),val=k=>PL.HAIRK.includes(k)?HV[k]:cfg[k];for(const k in F){const f=F[k],id='f-'+k;if(f.lab)f.lab.textContent=typeof f.l==='function'?f.l(cfg):f.l;f.row.hidden=!!(f.show&&!f.show(cfg));
if(f.type==='color'||f.type==='choice'||f.type==='text'){if(document.activeElement!==$(id))$(id).value=k==='fc'?(cfg.fc||cfg.hc):val(k);}
else if(f.type==='range'){if(document.activeElement!==$(id))$(id).value=val(k);const v=Number(val(k));$(id+'-v').textContent=f.fmt==='len'?[[0.6,'Ras'],[1.4,'Courts'],[2.2,'Aux oreilles'],[2.8,'Mi-longs'],[3.5,'Au menton'],[4.5,'Aux épaules'],[9,'Dans le dos']].find(x=>v<x[0])[1]+' ('+v.toFixed(1).replace('.',',')+')':f.fmt==='pct'?Math.round(v*100)+' %':f.fmt==='deg'?Math.round(v)+'°':f.fmt==='off'?(v>0?'+':'')+v.toFixed(2).replace('.',','):'× '+v.toFixed(2).replace('.',',');}
else if(f.type==='print'){const on=!!cfg.im;$(id+'-img').hidden=!on;if(on)$(id+'-img').src='data:image/'+cfg.imt+';base64,'+cfg.im;$(id+'-rm').hidden=!on;$(id+'-pick').disabled=!anyPhoto();}
else if(f.type==='chips')$(id).querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===val(k))));
else if(f.type==='check')$(id).checked=!!cfg[k];
else if(f.type==='glove'){$(id+'-on').checked=!!cfg.gv;if(cfg.gv)lastGlove=cfg.gv;$(id).value=lastGlove;$(id).disabled=!cfg.gv;}
else if(f.type==='optcolor'){$(id+'-on').checked=!!cfg[k];if(cfg[k])lastOpt[k]=cfg[k];$(id).value=lastOpt[k];$(id).disabled=!cfg[k];}
else if(f.type==='flags')for(const v in FLAGS)$(id+'-'+v).checked=cfg.acc.includes(v);}renderPieces();if(typeof renderAdj==='function')renderAdj();}
// Ajuster un accessoire à la main : position, taille, rotation (montre et bracelets suivent le bras)
const ADJ=[['x','Gauche ↔ Droite',-8,8,0.1,0],['y','Bas ↕ Haut',-8,8,0.1,0],['z','Arrière ↔ Avant',-8,8,0.1,0],['s','Taille',0.3,3,0.05,1],['r','Rotation',-180,180,5,0]];
{const sel=el2('select',{id:'adj-k'}),grid=el2('div',{className:'fields'});
for(const[k,l,mi,ma,stp]of ADJ){const row=el2('div',{className:'field'});row.append(el2('div',{className:'row rangehead'},[el2('label',{htmlFor:'adj-'+k,textContent:l}),el2('span',{className:'help',id:'adj-'+k+'-v'})]),el2('input',{type:'range',id:'adj-'+k,min:mi,max:ma,step:stp}));grid.append(row);}
$('tab-accessoires').append(foldCard('Ajuster et colorer un accessoire',[el2('p',{className:'help',textContent:"Choisis un accessoire, puis donne-lui sa propre couleur, déplace-le, change sa taille ou tourne-le."}),
el2('div',{className:'field'},[el2('label',{htmlFor:'adj-k',textContent:'Accessoire'}),sel]),grid,el2('div',{className:'row'},[el2('label',{className:'check'},[el2('input',{type:'checkbox',id:'adj-col-on'}),'Couleur à part']),el2('input',{type:'color',id:'adj-col'})]),el2('div',{className:'row'},[el2('button',{type:'button',className:'btn',id:'adj-reset',textContent:'Remettre à sa place'})]),el2('p',{className:'help',id:'adj-none',textContent:'Ajoute un accessoire ou un objet dans les mains pour pouvoir le régler ici.'})],false,'adj-card'));}
function adjList(){const l=[...cfg.acc].filter(k=>!'wl'.includes(k)).map(k=>[k,FLAGS[k]]);if(cfg.it&&cfg.it!=='aucun')l.unshift(['_','🤲 Objet dans les mains : '+CHOICES.it[cfg.it]]);return l;}
function renderAdj(){const sel=$('adj-k');if(!sel)return;const l=adjList(),cur0=sel.value,old=sel.dataset.sig||'';if(old!==l.map(x=>x[0]).join('')){const added=l.map(x=>x[0]).filter(k=>!old.includes(k));sel.textContent='';l.forEach(([k,t])=>sel.append(el2('option',{value:k,textContent:t})));sel.dataset.sig=l.map(x=>x[0]).join('');if(old&&added.length)sel.value=added[added.length-1];else if(l.some(x=>x[0]===cur0))sel.value=cur0;}
const none=!l.length;$('adj-none').hidden=!none;sel.disabled=none;$('adj-reset').disabled=none;const a=(cfg.aj&&cfg.aj[sel.value])||[0,0,0,1,0];
{const cl=cfg.acol&&cfg.acol[sel.value];$('adj-col-on').checked=!!cl;$('adj-col-on').disabled=none;$('adj-col').disabled=none||!cl;if(document.activeElement!==$('adj-col'))$('adj-col').value=cl||cfg.ac;}
ADJ.forEach(([k],i)=>{const inp=$('adj-'+k);inp.disabled=none;if(document.activeElement!==inp)inp.value=a[i];$('adj-'+k+'-v').textContent=k==='s'?'× '+Number(a[i]).toFixed(2).replace('.',','):k==='r'?Math.round(a[i])+'°':(a[i]>0?'+':'')+Number(a[i]).toFixed(1).replace('.',',');});}
$('adj-card').addEventListener('input',e=>{if(e.target.id==='adj-k'){renderAdj();return;}
if(e.target.id==='adj-col'||e.target.id==='adj-col-on'){const k=$('adj-k').value;if(!k)return;const n=Object.assign({},cfg.acol||{});if($('adj-col-on').checked)n[k]=$('adj-col').value;else delete n[k];cfg.acol=n;renderAdj();changed();return;}const k=$('adj-k').value;if(!k)return;const a=ADJ.map(([n])=>Number($('adj-'+n).value));cfg.aj=Object.assign({},cfg.aj||{},{[k]:a});renderAdj();changed();});
$('adj-k').addEventListener('change',renderAdj);
$('adj-reset').addEventListener('click',()=>{const k=$('adj-k').value;if(!k)return;const n=Object.assign({},cfg.aj||{}),c2=Object.assign({},cfg.acol||{});delete n[k];delete c2[k];cfg.aj=n;cfg.acol=c2;renderAdj();changed();});
// Pièces sur mesure ajoutées par Claude : on peut changer leur couleur ou les retirer
const SHAPE_L={sphere:'Boule',goutte:'Goutte',cone:'Cône',cylindre:'Cylindre',tore:'Anneau',boite:'Bloc'},ANCH_L={tete:'tête',corps:'corps',mains:'mains',dos:'dos',jambes:'jambes'};
$('tab-accessoires').append(foldCard('Pièces sur mesure',[el2('p',{className:'help',textContent:"Ce que Claude ajoute pour coller à la photo : oreilles, cornes, queue, nœud… Change une couleur ou retire une pièce."}),el2('div',{id:'pz-list',className:'pzlist'})],false));
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
const ch=e.target.closest('.seg button,.tiles button');if(ch&&ch.parentElement.id.startsWith('f-')){cfg[ch.parentElement.id.slice(2)]=ch.dataset.v;cfg=PL.clean(cfg);syncForm();changed();}
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
+"Chaque tenue est unique : ne reprends jamais une tenue type. Décris les vêtements tels qu'ils sont sur les photos, avec leurs zones de couleur (épaules, manches, bandes, côtés du pantalon), leur fermeture et leur motif. "
+"Prends les vraies couleurs des photos en compensant l'éclairage si la scène est sombre ou colorée, jamais des couleurs génériques.\n"
+"Avant de répondre, vérifie point par point sur la photo, sans rien inventer de ce qui ne se voit pas :\n"
+"1. Ventre : y a-t-il de la peau visible entre le bas du haut et la ceinture ? Oui → \"cr\" 1. Non (le haut descend jusqu'au pantalon ou est rentré dedans) → 0.\n"
+"2. Épaules : nues (bandeau, dos nu, débardeur, haut qui tombe d'une épaule) ou couvertes ? Choisis \"tp\" en conséquence.\n"
+"3. Manches : regarde où elles s'arrêtent sur le bras. Au poignet → \"longues\" ; au coude ou retroussées, avant-bras nus → \"coudes\" ; en haut du bras → \"courtes\" (ou \"tshirt\" pour un t-shirt ou un haut moulant à petites manches).\n"
+"4. Peau des bras : des tatouages visibles → \"ta\" 1.\n"
+"5. Couleur des cheveux : une seule couleur dans \"hc\" (la couleur moyenne, pas les reflets). \"h2\" seulement si une autre couleur est nettement teinte sur une bonne partie des cheveux (racines foncées, pointes, mèches colorées) ; la lumière, les reflets et les ombres ne comptent pas : dans le doute, \"h2\" = \"\".\n"
+"6. Attache : chignons, macarons, queue, couettes ? Regarde le haut et l'arrière de la tête.\n"
+"7. Bas : type, et couleur exacte (un jean clair délavé est bleu-gris clair, pas blanc ; un jean brut est bleu foncé), bandes éventuelles.\n"
+"8. Chaussures, ceinture, bijoux et piercings, lunettes, couvre-chef : reprends seulement ce qui se voit.\n"
+"Réponds uniquement avec un objet JSON qui a exactement ces clés :\n"
+'- "vu" : en PREMIER, écris en une à trois phrases ce que tu vois vraiment sur la photo, de haut en bas : cheveux (couleur, longueur, attache), visage (barbe, lunettes, piercings), haut (type, longueur, manches, couleur, motif), bas, chaussures, accessoires, tatouages. Les clés suivantes doivent toutes correspondre à cette description\n'
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
+'- "ht" : attache, parmi "aucune" (détachés), "queue" (queue de cheval basse), "haute" (queue de cheval haute), "couettes", "chignon", "tresse" (une tresse devant l\'épaule), "demi" (le dessus attaché derrière, le reste détaché), "macarons" (deux chignons ronds en haut de la tête, mèches libres autour du visage)\n'
+'- "hd" : côtés et nuque, parmi "normaux", "courts" (dégradé), "rases" (undercut, côtés rasés)\n'
+'- "ec" : couleur des yeux, "#rrggbb" ("#5a3b22" si on ne les voit pas)\n'
+'- "ex" : expression, parmi "sourire" (grand sourire), "content" (petit sourire), "rire" (rire, yeux fermés), "clin" (clin d\'œil), "amour" (yeux en cœur), "surpris", "neutre", "serieux", "triste", "boude" (fâché, boudeur), "dodo" (endormi), "etoiles" (yeux étoiles, émerveillé), "langue" (tire la langue), "bisou" (fait un bisou), "pleure" (en larmes), "gene" (gêné, rougit)\n'
+'- "bd" : pilosité du visage, parmi "aucune", "barbe3j" (barbe de quelques jours), "barbe", "longue" (barbe longue), "moustache", "bouc"\n'
+'- "fr" : 1 si on voit des taches de rousseur, sinon 0\n'
+'- "cl" : 1 pour de longs cils recourbés (visage féminin ou maquillé), 0 sinon\n'
+'- "gl" : lunettes, parmi "aucune", "lunettes" (de vue, sur les yeux), "soleil" (de soleil rondes ou rectangulaires, sur les yeux), "aviateur" (aviateur : verres en goutte, fine monture métal), "tete" (lunettes relevées sur le front, la tête ou la capuche), "masque" (lunettes de protection ou de ski sur les yeux), "coeur" (lunettes en forme de cœur), "rondes" (grosses lunettes rondes rétro), "etoile" (lunettes en forme d\'étoile)\n'
+'- "glc" : couleur de la monture, "#rrggbb"\n'
+'- "lc" : couleur des verres des lunettes de soleil ou aviateur, "#rrggbb" (brun, gris fumé, vert, bleu miroir…)\n'
+'- "hw" : couvre-chef, parmi "aucun", "capuche" (capuche relevée sur la tête), "casquette", "inverse" (casquette à l\'envers), "bonnet", "chapeau", "bandeau", "durag" (durag, foulard ou bonnet en tissu satiné bien ajusté sur le crâne), "beret", "bob" (bob ou chapeau de pêcheur), "cowboy" (chapeau de cowboy), "fleurs" (couronne de fleurs), "pompier" (casque de pompier ou de chantier), "police" (casquette d\'uniforme à visière)\n'
+'- "hwc" : couleur du couvre-chef ou de la capuche, "#rrggbb"\n'
+'- "hwt" : texte ou numéro visible sur le couvre-chef, 6 caractères maximum, sinon ""\n'
+'- "hm" : motif de la capuche, de la casquette ou du chapeau, parmi "uni", "rayures", "camo", "carreaux", "taches" (le motif prend la couleur "ac")\n'
+'- "tp" : haut, parmi "tshirt", "chemise", "sweat" (sweat ou pull), "zip" (veste zippée fermée, veste de survêtement, polaire zippée), "veste" (veste ouverte sur un autre haut), "costume" (veste de costume, chemise et cravate), "gilet" (gilet sans manches porté sur un autre haut), "debardeur" (débardeur, top à fines bretelles, haut sans manches), "dosnu" (haut dos nu, top bandana ou haut noué derrière le cou, épaules nues), "bandeau" (haut bandeau ou tube sans bretelles, épaules nues), "polo", "pull" (pull en maille, tricot), "maillot" (maillot de sport à numéro, mets le numéro dans "tt"), "doudoune" (veste matelassée), "cuir" (veste en cuir ouverte, perfecto), "cardigan" (gilet en maille ouvert à boutons), "manteau" (manteau long ouvert, trench)\n'
+'- "ta" : 1 si les bras sont tatoués, sinon 0\n'
+'- "ml" : longueur des manches du haut, parmi "longues", "coudes" (manches retroussées ou s\'arrêtant aux coudes, avant-bras nus), "courtes"\n'
+'- "cc" : 1 si le haut a un col roulé, sinon 0\n'
+'- "cr" : 1 si le haut est court et laisse voir le ventre (crop top, sweat court), sinon 0\n'
+'- "mt" : motif du haut, parmi "uni", "rayures", "camo", "carreaux", "taches" (taches de vache, de dalmatien… dans la couleur "ac"), "pois", "coeurs", "etoiles", "fleurs", "leopard", "zebre", "tiedye", "jean" (haut en toile de jean)\n'
+'- "tc" : couleur principale du haut (pour gilet, veste ou costume : la pièce du dessus), "#rrggbb"\n'
+'- "t2" : couleur du vêtement en dessous (les manches pour un gilet, le haut sous une veste, la chemise d\'un costume, les cordons d\'un sweat), "#rrggbb"\n'
+'- "yc" : couleur des épaules et du haut des manches quand elles sont d\'une autre couleur que le reste du haut (empiècement, veste de survêtement bicolore, maillot), "#rrggbb", sinon ""\n'
+'- "sl" : couleur des manches si elles sont d\'une autre couleur que le corps du haut, "#rrggbb", sinon ""\n'
+'- "sb" : couleur des bandes le long des manches (survêtement à bandes), "#rrggbb", sinon ""\n'
+'- "imp" : si le haut porte un grand dessin, logo ou imprimé sur le devant, sa boîte [x, y, largeur, hauteur] dans l\'image 1, en fractions de 0 à 1 (x et y = coin en haut à gauche), bien serrée autour du dessin ; sinon null\n'
+'- "imf" : 1 si le haut est couvert d\'un motif sur toute sa surface (bandana, cachemire, fleurs, léopard, imprimé tie-dye…) : donne alors dans "imp" la boîte d\'un morceau bien net de ce motif, sans peau ni fond ; 0 sinon\n'
+'- "tt" : texte imprimé sur le haut (par exemple LSPD, EMS, LSFD), 8 caractères maximum, sinon ""\n'
+'- "rf" : 1 s\'il y a des bandes réfléchissantes, sinon 0\n'
+'- "ac" : couleur d\'accent pour les rayures, la cravate, le pompon, le bandana, l\'écharpe, le sac à dos ou les bandes du jogging, "#rrggbb"\n'
+'- "bt" : bas, parmi "pantalon", "jogging", "short", "salopette" (salopette à bretelles et plastron, le haut se voit dessous), "jupe", "jean", "cargo" (pantalon cargo à poches sur les côtés), "longue" (jupe longue), "robe" (robe : prend la couleur et le motif du haut)\n'
+'- "pc" : couleur du bas, "#rrggbb"\n'
+'- "pb" : couleur des bandes sur les côtés du pantalon ou du jogging, "#rrggbb", sinon ""\n'
+'- "sh" : chaussures, parmi "bottes", "baskets", "chaussures" (de ville), "chaussons" (chaussons doux à pompon), "sandales", "talons", "crocs", "claquettes" (claquettes avec chaussettes)\n'
+'- "sc" : couleur des chaussures, "#rrggbb"\n'
+'- "gv" : couleur des gants, "#rrggbb", ou "" sans gants\n'
+'- "cos" : combinaison ou pyjama d\'animal porté par la personne (kigurumi), parmi "aucun", "ours", "lapin", "chat", "renard", "grenouille", "dino", "licorne", "panda", "cochon", "poussin", "requin", "vache" ; elle remplace la capuche et le haut\n'
+'- "coc" : couleur de la combinaison si elle n\'a pas la couleur habituelle de l\'animal, "#rrggbb", sinon ""\n'
+'- "acol" : couleurs propres des accessoires qui n\'ont pas la couleur d\'accent, par exemple {"x":"#c0c0c0","Q":"#ff7eb6","_":"#5aa2ea"} (la clé "_" = l\'objet tenu) ; {} si rien\n'
+'- "acc" : lettres des accessoires visibles, "" s\'il n\'y en a aucun : r = radio ou talkie, b = badge ou insigne, m = micro-casque ou oreillette, s = sacoche à la ceinture, c = chaîne ou collier, o = boucles d\'oreilles, w = montre, k = sac à dos, e = écharpe, h = casque audio autour du cou, a = bandana ou masque sur le bas du visage, n = sac en bandoulière, u = sac banane, d = plaques militaires, q = nœud dans les cheveux, f = fleur dans les cheveux, v = étui ou holster à la ceinture, y = lampe torche à la ceinture, z = menottes à la ceinture, l = bracelets, p = pins sur le haut, x = couronne, j = serre-tête oreilles de chat, t = nœud papillon, i = ailes d\'ange, g = cape, M = oreilles de lapin, A = antennes, B = cornes de diable, C = auréole, L = corne de licorne, D = casquette à hélice, R = bigoudis, T = cache-œil, E = pansement, P = pomme sur la tête, Q = canard sur la tête, V = cône de chantier sur la tête, N = flèche dans la tête, G = faux nez et moustache, H = bulle de chewing-gum, S = cœurs qui flottent, Y = paillettes, I = chapeau de fête, U = petit nuage de pluie, K = étoiles qui tournent (sonné), W = ampoule idée, O = tétine, X = harnais croisé (sangles noires sur la poitrine jusqu\'au cou), J = piercings au nez, F = casque audio porté sur la tête (majuscules et minuscules sont des accessoires différents)\n'
+'- "it" : objet tenu en main, parmi "aucun", "lance" (lance à incendie), "coeur", "telephone", "cafe", "donut", "trousse" (trousse de secours), "bouquet" (fleurs), "billets" (liasse d\'argent), "manette" (manette de jeu), "ballon" (ballon de basket ou de sport), "cle" (clé de voiture), "micro" (micro de chanteur), "glace", "sucette", "cadeau", "livre", "pizza", "poisson", "baguette", "banane", "poele", "papier" (papier toilette), "biberon", "bonbon", "coussin" (coussin cœur)\n'
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
+"Exemple de FORME seulement (les valeurs sont à remplacer par ce que montrent les photos, ne les recopie pas) : "+JSON.stringify({vu:'Homme barbu aux cheveux bruns courts, veste de survêtement noire à épaules blanches, jogging blanc à bandes noires, baskets blanches.',n:'Surnom',sk:'#d9a07c',hc:'#2a1c14',h2:'',hs:'court',hl:1.2,hv:0.4,hx:'lisse',hp:'aucune',hf:'courte',ht:'aucune',hd:'courts',ec:'#5a3b22',ex:'neutre',bd:'barbe',fr:0,cl:0,gl:'aucune',glc:'#2b2b2b',lc:'#3a2a1e',hw:'aucun',hwc:'#1c1c1e',hwt:'',hm:'uni',tp:'zip',mt:'uni',tc:'#1c1c1e',t2:'#f2f2f2',yc:'#f2f2f2',sl:'',sb:'',imp:null,tt:'',rf:0,ac:'#f2f2f2',bt:'jogging',pc:'#f2f2f2',pb:'#1c1c1e',sh:'baskets',sc:'#f2f2f2',gv:'',acc:'',it:'aucun',ms:'aucune',mc:'#8ec5f0',mp:'droite',mz:1,pz:[]});}
function readyMsg(){if(!(sample&&imagesOK))return "Règle la peluche à la main : le bouton Pipette prend une couleur sur la photo. Pour reprendre une peluche déjà faite, colle son lien dans l'onglet « Style et pose ».";return anyPhoto()?'Peluche prête. Tu peux relancer la création ou corriger les réglages.':'Ajoute une photo de face : la peluche se crée toute seule.';}
function reviewPrompt(w,slots,nr){const cur=Object.assign({},cfg);delete cur.im;delete cur.imt;delete cur.ia;
return intro(w,slots)+"Les "+nr+" dernières images ne sont pas des photos : c'est le rendu actuel de la peluche ("+(nr>1?'de face, puis de dos':'de face')+"), fabriquée avec ce réglage :\n"+JSON.stringify(cur)+"\n"
+"Compare la peluche aux photos comme un client exigeant, en commençant par la coiffure (longueur, volume, raie, frange, texture, attache, côtés) et les vêtements (type de haut, zones de couleur des épaules et des manches, bandes, bas et ses bandes), puis couleurs des cheveux, de la peau et des yeux, barbe, lunettes, couvre-chef, haut et motif, couleurs des vêtements, accessoires, mascotte, objets. "
+"Vérifie en particulier : peau du ventre visible ou non (cr), épaules nues ou couvertes (tp), longueur des manches (ml), tatouages (ta), une ou deux couleurs de cheveux (h2 vide dans le doute), attache des cheveux (ht), couleur exacte du bas (pc). "
+"Corrige tout ce qui ne ressemble pas et garde ce qui est juste. Renvoie le réglage complet corrigé.\n"+keysText();}
function updateAnalyse(){$('fix-box').hidden=!(sample&&imagesOK);$('fix-go').textContent=ctl&&ctl.fix?'Arrêter':'Corriger avec Claude';const b=$('analyse');b.hidden=!(sample&&imagesOK&&anyPhoto());b.disabled=false;b.textContent=ctl?'Arrêter':'Relancer la création';}
// Rendu de la peluche sur fond gris neutre, pour que Claude la compare aux photos
async function renderView(rot,S){await new Promise(res=>setTimeout(res,250));const pr=r.getPixelRatio(),keep=cur.group.rotation.y;r.setPixelRatio(1);r.setSize(S,S,false);cam.aspect=1;cam.updateProjectionMatrix();cur.group.rotation.y=rot;PL.aim(cam,cur.fit,0.12,1.05,camFill);r.render(scene,cam);
const o=document.createElement('canvas');o.width=o.height=S;const g=o.getContext('2d');g.fillStyle='#8a929c';g.fillRect(0,0,S,S);g.drawImage(r.domElement,0,0);cur.group.rotation.y=keep;r.setPixelRatio(pr);fitSize();return new Promise(res=>o.toBlob(res,'image/jpeg',0.9));}
function applyAnswer(data,keep,first0,first){const prev=first?null:(cfg.im?{im:cfg.im,imt:cfg.imt,ia:cfg.ia}:null);cfg=PL.clean(Object.assign({},data,keep,{bg:cfg.bg,bf:cfg.bf,bgc:cfg.bgc}),PL.NEUTRAL);
if(Array.isArray(data.imp)&&data.imp.length===4)cropPrint(shots[first0].cn,data.imp.map(Number));else if(prev&&data.imp!==null)Object.assign(cfg,prev);syncForm();rebuild();updateLink();}
async function runAnalysis(){const slots=photoList();if(!slots.length||!sample||!imagesOK)return;clearTimeout(anaT);if(ctl)ctl.abort();const my=new AbortController();ctl=my;updateAnalyse();
const w=$('who').value,keep={st:cfg.st,po:cfg.po,ey:cfg.ey,fc:''},use=slots.slice(0,Math.max(1,maxImages)),imgs=use.map(s=>shots[s].blob);
busy=true;try{say('ai-status','Claude regarde '+(use.length>1?'les photos':'la photo')+'… Ça prend souvent 10 à 40 secondes.');
let data=await sample.json(prompt(w,use),{images:imgs,signal:my.signal,modelTier:'complex'});if(ctl!==my)return;applyAnswer(data,keep,use[0],true);
const nr=Math.min(maxImages-use.length,shots.dos.blob?2:1);
if($('review').checked&&nr>=1){say('ai-status','Peluche créée. Claude la compare maintenant aux photos pour corriger ce qui ne ressemble pas…');
// Deux tours : Claude compare le rendu aux photos, corrige, puis revérifie le résultat corrigé
for(let pass=0;pass<2;pass++){if(pass)say('ai-status','Deuxième vérification : Claude recompare la peluche corrigée aux photos…');
const renders=[await renderView(-0.34,512)];if(nr>1)renders.push(await renderView(Math.PI-0.34,512));
const before=JSON.stringify(cfg);data=await sample.json(reviewPrompt(w,use,renders.length),{images:imgs.concat(renders),signal:my.signal,cache:false,modelTier:'complex'});if(ctl!==my)return;applyAnswer(data,keep,use[0],false);if(JSON.stringify(cfg)===before)break;}
say('ai-status','Peluche créée puis vérifiée par Claude. Corrige ce qui ne va pas, puis copie le lien.');}
else say('ai-status','Peluche créée depuis '+(use.length>1?'les photos':'la photo')+'. Corrige ce qui ne va pas, puis copie le lien.');}
catch(e){if(ctl!==my)return;const code=e&&e.code;
if(['not_granted','sampling_disabled','not_declared','capability_disabled','capability_removed','images_unavailable'].includes(code)){sample=null;say('ai-status',"La création automatique n'est pas autorisée ici. Règle la peluche à la main : le bouton Pipette prend une couleur sur la photo.");}
else say('ai-status',({cancelled:'Création arrêtée.',rate_limited:'Trop de demandes pour le moment. Réessaie dans un moment.',image_rejected:"Une des images n'est pas acceptée. Essaie des captures en PNG ou JPEG.",
refused:"Claude n'a pas pu décrire cette photo. Essaie une autre image.",invalid_json:'La réponse était incomplète. Clique sur « Relancer la création ».',session_expired:'Reconnecte-toi à Claude, puis relance la création.'})[code]||'La création a échoué. Clique sur « Relancer la création ».');}
finally{busy=false;if($('stage-status'))$('stage-status').textContent='';if(ctl===my){ctl=null;updateAnalyse();}}}
const getSample=window.claude&&window.claude.use?window.claude.use('sample'):Promise.resolve(null);
getSample.then(async s=>{sample=s;if(s){try{const lim=await s.limits();imagesOK=!!(lim&&lim.images);if(imagesOK)maxImages=lim.images.maxCount||1;}catch(e){imagesOK=false;}}updateAnalyse();if(!pick)say('ai-status',readyMsg());if(anyPhoto())runAnalysis();},()=>{updateAnalyse();say('ai-status',readyMsg());});
// Dialogue : la personne écrit ce qui ne va pas, Claude regarde les photos et le rendu, puis corrige seulement ça
function fixPrompt(msg,w,slots,nr){const cur=Object.assign({},cfg);delete cur.im;delete cur.imt;delete cur.ia;
return (slots.length?intro(w,slots):"Il n'y a pas de photo. ")+(nr?"Les "+nr+" dernières images ne sont pas des photos : c'est le rendu actuel de la peluche ("+(nr>1?'de face, puis de dos':'de face')+"), fabriquée avec ce réglage :\n":"La peluche est fabriquée avec ce réglage :\n")+JSON.stringify(cur)+"\n"
+"La personne qui fabrique la peluche te dit ce qui ne va pas : « "+msg+" »\n"
+"Applique exactement ce qu'elle demande, en t'aidant des photos pour les détails (couleurs, formes). Ne change pas ce dont elle ne parle pas. Si elle parle de la pose, tu peux aussi changer \"po\" parmi "+PL.ENUM.po.map(x=>'"'+x+'"').join(', ')+". Renvoie le réglage complet corrigé.\n"+keysText();}
async function runFix(){const msg=$('fix-txt').value.trim();if(!msg){say('ai-status','Écris d\'abord ce qui ne va pas dans la case.');$('fix-txt').focus();return;}if(!sample||!imagesOK)return;
if(ctl)ctl.abort();const my=new AbortController();my.fix=true;ctl=my;updateAnalyse();
const w=$('who').value,use=photoList().slice(0,maxImages>1?maxImages-1:1),imgs=use.map(s=>shots[s].blob),nr=Math.max(0,Math.min(maxImages-use.length,shots.dos.blob?2:1));
busy=true;try{say('ai-status','Claude corrige : « '+msg.slice(0,80)+(msg.length>80?'…':'')+' »');
const renders=nr?[await renderView(-0.34,512)]:[];if(nr>1)renders.push(await renderView(Math.PI-0.34,512));
const data=await sample.json(fixPrompt(msg,w,use,renders.length),{images:imgs.concat(renders),signal:my.signal,cache:false,modelTier:'complex'});if(ctl!==my)return;
const prev={im:cfg.im,imt:cfg.imt,ia:cfg.ia};cfg=PL.clean(Object.assign({},cfg,data,{bg:cfg.bg,bf:cfg.bf,bgc:cfg.bgc}),PL.NEUTRAL);
if(Array.isArray(data.imp)&&data.imp.length===4&&use[0])cropPrint(shots[use[0]].cn,data.imp.map(Number));else Object.assign(cfg,prev);
syncForm();rebuild();updateLink();$('fix-txt').value='';say('ai-status','Corrigé. Si ce n\'est pas encore ça, réécris ce qui ne va pas (Ctrl + Z pour annuler).');}
catch(e){if(ctl!==my)return;const code=e&&e.code;say('ai-status',({cancelled:'Correction arrêtée.',rate_limited:'Trop de demandes pour le moment. Réessaie dans un moment.',invalid_json:'La réponse était incomplète. Réessaie.',session_expired:'Reconnecte-toi à Claude, puis réessaie.'})[code]||'La correction a échoué. Réessaie.');}
finally{busy=false;if(ctl===my){ctl=null;updateAnalyse();}}}
$('fix-go').addEventListener('click',()=>{if(ctl&&ctl.fix){const c0=ctl;ctl=null;c0.abort();updateAnalyse();say('ai-status','Correction arrêtée.');return;}runFix();});
$('fix-txt').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();runFix();}});
$('analyse').addEventListener('click',()=>{if(ctl){const c0=ctl;ctl=null;c0.abort();updateAnalyse();say('ai-status','Création arrêtée.');return;}runAnalysis();});
$('who').addEventListener('change',()=>{if(anyPhoto())runAnalysis();});

// Lien
const VIEW='https://misternutss.github.io/peluches/',baseIn=$('base');{const v=store('peluches-base');if(v&&!v.startsWith(VIEW))store('peluches-base','');}baseIn.value=store('peluches-base')||VIEW;
baseIn.addEventListener('input',()=>{store('peluches-base',baseIn.value.trim());updateLink();});
function baseUrl(){const v=baseIn.value.trim();if(!/^https?:\/\//i.test(v))return '';try{const u=new URL(v);if(!/\.[a-z0-9]+$/i.test(u.pathname)&&!u.pathname.endsWith('/'))u.pathname+='/';u.search='';u.hash='';return u.toString();}catch(e){return '';}}
let linkN=0;function updateLink(){const my=++linkN;PL.pack(cfg).then(code=>{if(my===linkN)showLink(code);});}
function showLink(code){if($('lib-nom')&&document.activeElement!==$('lib-nom')&&!$('lib-nom').value)$('lib-nom').value=cfg.n||'';const b=baseUrl(),url=(b||VIEW)+'?p='+code;$('out').value=url;$('out2').value=url;$('edit').value='https://peluches-tau.vercel.app/atelier?p='+code;$('out').classList.toggle('example',!b);
$('open').hidden=!b;$('open').href=url;say('link-help',b?'Colle ce lien dans URLS, avec le type Site Web.':"Lien d'exemple : renseigne d'abord l'adresse de ta page 3D (étapes en bas de page).");}
// Reprendre une peluche depuis son lien (page 3D ou atelier)
$('import-go').addEventListener('click',()=>{const v=$('import').value.trim();let code=null;try{code=new URL(v).searchParams.get('p');}catch(e){const m=v.match(/[?&]p=(~?[A-Za-z0-9_-]+)/);code=m?m[1]:(/^~?[A-Za-z0-9_-]{8,}$/.test(v)?v:null);}
PL.unpack(code).then(c=>{if(!code||!c){say('import-status',"Ce lien ne contient pas de peluche. Copie le lien complet, avec ?p=…");return;}cfg=c;syncForm();rebuild();updateLink();say('import-status','Peluche ouverte : tu peux la modifier.');});});
$('copy-edit').addEventListener('click',()=>{const t=$('edit').value,done=()=>{$('copy-edit').textContent='Copié';setTimeout(()=>{$('copy-edit').textContent='Copier';},1500);},sel=()=>{$('edit').focus();$('edit').select();};
try{navigator.clipboard.writeText(t).then(done,sel);}catch(e){sel();}});
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
const bg=IBG.k!=='aucun',w=x1-x0+1,h=y1-y0+1,k=out*(bg?(IBG.f==='rond'?0.74:0.82):0.9)/Math.max(w,h),o=document.createElement('canvas');o.width=o.height=out;const og=o.getContext('2d');og.imageSmoothingQuality='high';
if(bg){og.save();iconShape(og,out);og.clip();paintBg(og,out);og.restore();}
og.drawImage(c,x0,y0,w,h,(out-w*k)/2,(out-h*k)/2+(bg?out*0.02:0),w*k,h*k);return o;}
// Fond de l'icône : transparent par défaut, ou un fond pipou (réglage retenu sur cet appareil)
// Le fond fait partie de la peluche : il suit son lien et s'affiche aussi sur la page 3D
const IBG={get k(){return cfg.bg||'aucun';},set k(v){cfg.bg=v;},get f(){return cfg.bf||'arrondi';},set f(v){cfg.bf=v;},get c(){return cfg.bgc||'#ffd6e8';},set c(v){cfg.bgc=v;}};
const iconShape=(g,S)=>PL.bgShape(g,S,IBG),paintBg=(g,S)=>PL.paintBg(g,S,IBG);
const BGS={aucun:'Transparent',blake:'Blake',billy:'Billy',duo:'Blake & Billy',coeurs:'Cœurs',etoiles:'Nuit étoilée',arcenciel:'Arc-en-ciel',nuages:'Ciel et nuages',bonbon:'Bonbons',damier:'Damier',spot:'Projecteur',perso:'Ma couleur'};
{const t=$('ibg');for(const[v,n]of Object.entries(BGS)){const sw=document.createElement('canvas');sw.width=sw.height=48;sw.className='em';sw.style.cssText='width:28px;height:28px;border-radius:8px;background:repeating-conic-gradient(#ddd 0 25%,#fff 0 50%) 0 0/8px 8px';
const b=document.createElement('button');b.type='button';b.className='tile';b.dataset.v=v;const l=document.createElement('span');l.textContent=n;b.append(sw,l);t.append(b);}
const sh=$('ishape');for(const[v,n]of Object.entries({arrondi:'Arrondi',rond:'Rond',carre:'Carré'})){const b=document.createElement('button');b.type='button';b.className='btn';b.textContent=n;b.dataset.v=v;sh.append(b);}
const swatches=()=>{const keep=IBG.k;t.querySelectorAll('canvas').forEach(cv=>{IBG.k=cv.parentNode.dataset.v;const g=cv.getContext('2d');g.clearRect(0,0,48,48);if(IBG.k!=='aucun'){g.save();g.beginPath();g.rect(0,0,48,48);g.clip();paintBg(g,48);g.restore();}});IBG.k=keep;};
window.ibgSync=()=>{t.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===IBG.k)));sh.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===IBG.f)));$('ibgc').value=IBG.c;$('ibgc-f').hidden=IBG.k!=='perso';$('ishape').parentNode.hidden=IBG.k==='aucun';
if(cur){const p=$('ibg-prev'),g=p.getContext('2d');g.clearRect(0,0,256,256);g.drawImage(renderIcon(256),0,0);}};
const set=(a,v)=>{IBG[a]=v;changed();};
t.addEventListener('click',e=>{const b=e.target.closest('button');if(b)set('k',b.dataset.v);});
sh.addEventListener('click',e=>{const b=e.target.closest('button');if(b)set('f',b.dataset.v);});
$('ibgc').addEventListener('input',e=>{IBG.c=e.target.value;swatches();changed();});
swatches();}
$('icon').addEventListener('click',async()=>{if(!dl||!cur)return;$('icon').disabled=true;say('dl-status','Création de l\'icône…');const blob=await new Promise(res=>renderIcon(512).toBlob(res,'image/png'));await save(slug(cfg.n)+'.png',blob,'dl-status');$('icon').disabled=!dl;});
$('get-viewer').addEventListener('click',async()=>{if(!dl)return;await save('index.html',VIEWER_HEAD+$('pl-src').textContent.trim()+'\n'+VIEWER_TAIL,'setup-status');});

syncForm();rebuild();updateLink();
// Aperçu de l'icône : rafraîchi quand l'onglet Lien s'ouvre
document.querySelectorAll('[data-tab]').forEach(b=>{if(b.tagName==='BUTTON')b.addEventListener('click',()=>{if(b.dataset.tab==='lien')setTimeout(ibgSync,30);});});setTimeout(()=>{try{ibgSync();}catch(e){}},800);
// Atelier ouvert avec ?p=… ou ?nom=… : la peluche du lien ou de la bibliothèque
{let p=null,n=null,sv=null;try{const u=new URLSearchParams(location.search);p=u.get('p');n=u.get('nom');sv=u.get('enregistrer');}catch(e){}
const got=c=>{if(c){cfg=c;syncForm();rebuild();updateLink();}
// Venue de la page Claude pour enregistrer : nom prérempli, et enregistrement tout seul si le code est déjà retenu ici
if(sv&&c){$('lib-nom').value=sv;showTab('lien');setTimeout(()=>{if($('lib-code').value)$('lib-save').click();else{say('lib-status','Entre le code secret une fois, puis clique sur Enregistrer : il sera retenu pour les prochaines fois.');$('lib-code').focus();}},600);}};
if(n)fetch((/vercel\.app$/.test(location.hostname)?'':'https://peluches-tau.vercel.app')+'/api/peluches?nom='+encodeURIComponent(n)).then(x=>x.ok?x.json():null).then(d=>{if(d){$('lib-nom').value=d.nom||'';return PL.unpack(d.p);}}).then(got).catch(()=>{});else if(p)PL.unpack(p).then(got);}
// Bibliothèque : sur le site Vercel directement ; depuis la page Claude, envoi au serveur Vercel, ou ouverture du site pour finir l'enregistrement
const SITE='https://peluches-tau.vercel.app',onSite=/vercel\.app$/.test(location.hostname),LIBAPI=(onSite?'':SITE)+'/api/peluches';
if(/^https?:$/.test(location.protocol)){$('lib-card').hidden=false;if(!onSite){$('lib-open').href=SITE+'/bibliotheque';$('lib-open').target='_blank';$('lib-open').rel='noopener';}}
function finishOnSite(nom,p){const a=document.createElement('a');a.href=SITE+'/atelier?p='+encodeURIComponent(p)+'&enregistrer='+encodeURIComponent(nom);a.target='_blank';a.rel='noopener';document.body.append(a);a.click();a.remove();
say('lib-status',"Le site s'ouvre dans un nouvel onglet pour finir l'enregistrement (la page Claude ne peut pas l'envoyer elle-même). Si rien ne s'ouvre, autorise les fenêtres pour cette page.");}
$('lib-code').value=store('peluches-code')||'';
// Code déjà retenu : la case est cachée, un lien permet d'en changer
const codeUI=()=>{const k=!!store('peluches-code');$('lib-code-f').hidden=k;$('lib-code-ok').hidden=!k;};codeUI();
$('lib-code-chg').addEventListener('click',e=>{e.preventDefault();$('lib-code-f').hidden=false;$('lib-code-ok').hidden=true;$('lib-code').value='';$('lib-code').focus();});
$('lib-save').addEventListener('click',async()=>{const nom=$('lib-nom').value.trim()||cfg.n,code=$('lib-code').value;if(!nom){say('lib-status','Donne un nom à la peluche.');return;}
const p0=await PL.pack(cfg);if(!onSite&&!code){finishOnSite(nom,p0);return;}if(!code){say('lib-status','Entre le code secret.');return;}
$('lib-save').disabled=true;say('lib-status','Enregistrement…');
try{const p=p0,image=cur?renderIcon(512).toDataURL('image/png'):'';
let x,d;try{x=await fetch(LIBAPI,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({nom,p,image,code})});d=await x.json();}
catch(e){if(!onSite){finishOnSite(nom,p);return;}throw e;}
if(!x.ok&&!onSite&&!d.erreur){finishOnSite(nom,p);return;}
if(!x.ok){if(x.status===403){store('peluches-code','');codeUI();}say('lib-status',d.erreur||"L'enregistrement a échoué.");return;}
store('peluches-code',code);codeUI();const bid=(String(d.image||'').match(/^https:\/\/([a-z0-9]+)\.public\.blob\.vercel-storage\.com\//)||[])[1];$('lib-out').value=VIEW+'p/'+d.slug+(bid?'?b='+bid:'');$('lib-link').hidden=false;if(d.image){$('lib-ico-out').value=d.image;$('lib-ico').hidden=false;}say('lib-status',!d.github||d.github==='ok'?'Peluche enregistrée dans la bibliothèque. Le lien marche dans FiveM d\'ici une à deux minutes.':d.github==='absent'?"Peluche enregistrée. Pour qu'elle s'affiche dans FiveM, ajoute la variable GITHUB_TOKEN sur Vercel (voir le README).":'Peluche enregistrée, mais la copie sur GitHub a échoué ('+d.github+').');}
catch(e){say('lib-status',"L'enregistrement a échoué. Vérifie ta connexion.");}finally{$('lib-save').disabled=false;}});
$('lib-ico-copy').addEventListener('click',()=>{const t=$('lib-ico-out').value;try{navigator.clipboard.writeText(t).then(()=>{$('lib-ico-copy').textContent='Copié';setTimeout(()=>{$('lib-ico-copy').textContent='Copier';},1500);});}catch(e){$('lib-ico-out').select();}});
$('lib-copy').addEventListener('click',()=>{const t=$('lib-out').value;try{navigator.clipboard.writeText(t).then(()=>{$('lib-copy').textContent='Copié';setTimeout(()=>{$('lib-copy').textContent='Copier';},1500);});}catch(e){$('lib-out').select();}});
</script>
"""

def js_str(s):
    return json.dumps(s, ensure_ascii=False).replace("</", "<\\/")

atelier = ATELIER.replace("__MODEL__", model.strip()).replace("__VIEWER_HEAD__", js_str(VIEWER_HEAD)).replace("__VIEWER_TAIL__", js_str(VIEWER_TAIL))
viewer = VIEWER_HEAD + model.strip() + "\n" + VIEWER_TAIL
os.makedirs(os.path.dirname(viewer_out) or ".", exist_ok=True)
open(atelier_out, "w", encoding="utf-8").write(atelier)
open(viewer_out, "w", encoding="utf-8").write(viewer)
# GitHub Pages sert 404.html pour /p/nom : c'est la même page 3D, qui lit le nom dans l'adresse
open(os.path.join(os.path.dirname(viewer_out) or ".", "404.html"), "w", encoding="utf-8").write(viewer)
if site_out:
    # Même atelier, en page complète pour GitHub Pages
    open(site_out, "w", encoding="utf-8").write('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' + atelier + '\n</html>\n')
print("ok", len(atelier), len(viewer))
