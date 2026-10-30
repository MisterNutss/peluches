// ===== Peluche paramétrable : le même code construit la peluche dans l'atelier et dans la page 3D =====
const PL=(()=>{
const V=(x,y,z)=>new THREE.Vector3(x,y,z),FWD=V(0,0,-1),BACK=V(0,0,1),X=V(1,0,0),NX=V(-1,0,0),Y=V(0,1,0);

// Réglages possibles (clés courtes pour que le lien reste court)
const ENUM={st:['classique','ours','lapin','chat','monstre','avatar'],po:['assis','debout','coucou','bravo','calin','coeur','pensif','tailleur','dab'],ey:['kawaii','realiste'],hs:['court','banane','meches','herisse','iroquoise','carre','long','tresse','couettes','queue','chignon','boucle','afro','dreads','rase','chauve'],
bd:['aucune','barbe3j','barbe','longue','moustache','bouc'],gl:['aucune','lunettes','soleil','aviateur','tete','masque'],
hw:['aucun','capuche','casquette','inverse','bonnet','chapeau','bandeau','pompier','police'],tp:['tshirt','chemise','sweat','veste','costume','gilet'],
mt:['uni','rayures','camo','carreaux','taches'],hm:['uni','rayures','camo','carreaux','taches'],bt:['pantalon','jogging','short','salopette'],sh:['bottes','baskets','chaussures'],ex:['sourire','content','neutre','serieux'],
it:['aucun','lance','coeur','telephone','cafe','donut','trousse'],
hp:['aucune','gauche','milieu','droite'],hf:['aucune','courte','droite','balayee','rideau','longue','arriere'],hx:['lisse','ondule','boucle','crepu','pique','dreads'],ht:['aucune','queue','haute','couettes','chignon','tresse','demi'],hd:['normaux','courts','rases'],ms:['aucune','monstre','lapin','ours','chat','chien','oiseau'],mp:['droite','gauche','tete','mains']};
const ACC='rbmscowkehan';
// Proportions par style : h = taille de la tête, b = corps [largeur, hauteur, profondeur], a = bras [épaisseur, longueur], l = jambes [largeur, hauteur, longueur]
// Ourson : ventre rond, membres épais. Lapin : corps allongé, longues pattes. Chaton : tête un peu plus grosse.
// Petit monstre : tête surdimensionnée, corps trapu et dodu, petits bras et petites jambes. Avatar : grosse tête ronde, corps étroit, membres fins.
const PROPS={classique:{h:1,b:[1,1,1],a:[1,1],l:[1,1,1]},ours:{h:1.0,b:[1.16,1.0,1.16],a:[1.25,1.05],l:[1.2,1.1,1.05]},
lapin:{h:0.94,b:[0.9,1.14,0.9],a:[0.85,1.18],l:[0.88,0.9,1.35]},chat:{h:1.1,b:[0.92,0.92,0.92],a:[0.9,0.92],l:[0.9,0.9,0.95]},
monstre:{h:1.24,b:[1.0,0.8,1.0],a:[1.0,0.72],l:[1.0,0.85,0.75]},avatar:{h:1.2,b:[0.74,0.95,0.78],a:[0.6,1.0],l:[0.62,0.85,0.95]}};
const COLS=['sk','hc','ec','glc','lc','hwc','tc','t2','ac','pc','sc','gv','mc'];
const HOOKS={onTex:null};
const PRESETS={
pompier:{n:'Pompier 23',sk:'#f6d0b4',hc:'#e2ad6c',hs:'court',ec:'#245c9e',bd:'aucune',fr:1,ex:'sourire',gl:'masque',glc:'#9fdc2e',hw:'pompier',hwc:'#e8571f',hwt:'23',hm:'uni',pz:[],st:'classique',po:'assis',ey:'kawaii',fc:'',mz:1,mx:0,my:0,mf:0,mr:0,cl:1,lc:'#3a2a1e',im:'',imt:'webp',ia:1,ms:'aucune',mc:'#8ec5f0',mp:'droite',tp:'gilet',mt:'uni',tc:'#f26a1b',t2:'#f5ce14',tt:'LSFD',rf:1,ac:'#c8261f',bt:'pantalon',pc:'#24304e',sh:'bottes',sc:'#161618',gv:'#86ace6',acc:'rms',it:'lance'},
police:{n:'Agent LSPD',sk:'#e2ac86',hc:'#3b2a20',hs:'rase',ec:'#5a3b22',bd:'barbe3j',fr:0,cl:0,ex:'content',gl:'soleil',glc:'#1c1c1e',hw:'police',hwc:'#1b2440',hwt:'',tp:'chemise',mt:'uni',tc:'#2b3d6b',t2:'#2b3d6b',tt:'LSPD',rf:0,ac:'#c9a227',bt:'pantalon',pc:'#1b2238',sh:'chaussures',sc:'#111113',gv:'',acc:'rbw',it:'donut'},
ems:{n:'Ambulancière',sk:'#c98a64',hc:'#1d1512',hs:'queue',ec:'#3d2a1c',bd:'aucune',fr:0,ex:'sourire',gl:'aucune',glc:'#2b2b2b',hw:'aucun',hwc:'#2e6b3a',hwt:'',tp:'veste',mt:'uni',tc:'#2e6b3a',t2:'#e9eef2',tt:'EMS',rf:1,ac:'#d23a3a',bt:'pantalon',pc:'#1f2b25',sh:'baskets',sc:'#151515',gv:'#7fb2e8',acc:'rmo',it:'trousse'},
civil:{n:'Civil',sk:'#f1c6a6',hc:'#7a4a26',hs:'boucle',ec:'#4b6b2a',bd:'aucune',fr:1,ex:'content',gl:'lunettes',glc:'#2b2b2b',hw:'bonnet',hwc:'#c2402f',hwt:'',tp:'sweat',mt:'uni',tc:'#5b6f8f',t2:'#e9e9e9',tt:'',rf:0,ac:'#f2c418',bt:'jogging',pc:'#3c4a63',sh:'baskets',sc:'#e8e8e8',gv:'',acc:'h',it:'cafe'}};
// Coiffure : "hs" donne un point de départ, les réglages fins (longueur, volume, raie, frange, texture, attache, côtés) le remplacent un par un
// hl : 0 ras, 1 courts, 2 aux oreilles, 3 au menton, 4 aux épaules, 5 dans le dos ; hv : volume de 0 à 1
const HAIRK=['hl','hv','hp','hf','hx','ht','hd'];
const HSDEF={court:{hl:1,hv:0.3,hf:'courte'},banane:{hl:1.4,hv:0.85,hf:'arriere',hd:'courts'},meches:{hl:2.6,hv:0.6,hp:'gauche',hf:'balayee'},herisse:{hl:1.1,hv:0.5,hf:'aucune',hx:'pique'},
iroquoise:{hl:1.5,hd:'rases'},carre:{hl:3,hv:0.4,hf:'droite'},long:{hl:4.4,hv:0.4,hp:'milieu',hf:'aucune'},tresse:{hl:4,hp:'milieu',hf:'aucune',ht:'tresse'},couettes:{hl:3.6,hp:'milieu',hf:'courte',ht:'couettes'},
queue:{hl:4,hv:0.3,hf:'aucune',ht:'queue'},chignon:{hl:3,hv:0.3,hf:'aucune',ht:'chignon'},boucle:{hl:1.6,hv:0.7,hf:'courte',hx:'boucle'},afro:{hl:2.2,hv:1,hf:'aucune',hx:'crepu'},
dreads:{hl:3.6,hv:0.4,hf:'aucune',hx:'dreads'},rase:{hl:0.3,hv:0},chauve:{hl:0,hv:0}};
const HDEF={hl:1,hv:0.4,hp:'aucune',hf:'courte',hx:'lisse',ht:'aucune',hd:'normaux'};
function hair(c){const b=Object.assign({},HDEF,HSDEF[c.hs]||{});for(const k of HAIRK)if(c[k]!==undefined&&c[k]!==null)b[k]=c[k];b.h2=c.h2||'';return b;}
const NEUTRAL=Object.assign({},PRESETS.civil,{n:'',hs:'court',fr:0,cl:0,ms:'aucune',mc:'#8ec5f0',mp:'droite',mz:1,ex:'content',gl:'aucune',hw:'aucun',hwt:'',tp:'tshirt',mt:'uni',tt:'',bt:'pantalon',sh:'baskets',gv:'',acc:'',it:'aucun'});

function clean(o,base){const d=Object.assign({},base||PRESETS.pompier);if(!o||typeof o!=='object')return d;
for(const k in ENUM)if(ENUM[k].includes(o[k]))d[k]=o[k];
for(const k of COLS)if(typeof o[k]==='string'&&/^#[0-9a-f]{6}$/i.test(o[k]))d[k]=o[k].toLowerCase();
if('gv' in o&&!o.gv)d.gv='';
if(typeof o.h2==='string'&&/^#[0-9a-f]{6}$/i.test(o.h2))d.h2=o.h2.toLowerCase();else if('h2' in o&&!o.h2)delete d.h2;
for(const[k,lo,hi]of[['hl',0,5],['hv',0,1]])if(k in o&&o[k]!==null&&o[k]!==''){const v=Number(o[k]);if(Number.isFinite(v))d[k]=Math.round(Math.min(hi,Math.max(lo,v))*100)/100;}
if(typeof o.fc==='string'&&/^#[0-9a-f]{6}$/i.test(o.fc))d.fc=o.fc.toLowerCase();else if('fc' in o&&!o.fc)d.fc='';
for(const[k,m]of[['hwt',6],['tt',8],['n',24]])if(typeof o[k]==='string')d[k]=o[k].replace(/[^\p{L}\p{N} .'\-]/gu,'').trim().slice(0,m);
for(const k of['fr','rf','cl'])if(k in o)d[k]=o[k]&&o[k]!=='0'?1:0;
if('mz' in o){const v=Number(o.mz);if(Number.isFinite(v))d.mz=Math.round(Math.min(2,Math.max(0.5,v))*100)/100;}
for(const[k,lo,hi]of[['mx',-1,1],['my',-1,1],['mf',-1,1],['mr',-180,180]])if(k in o){const v=Number(o[k]);if(Number.isFinite(v))d[k]=Math.round(Math.min(hi,Math.max(lo,v))*100)/100;}
// Imprimé découpé dans la photo : petite image en base64 (webp, png ou jpeg) et son rapport largeur/hauteur
if('im' in o)d.im=typeof o.im==='string'&&/^[A-Za-z0-9+/=]{40,16000}$/.test(o.im)?o.im:'';
if(['webp','png','jpeg'].includes(o.imt))d.imt=o.imt;
if('ia' in o){const v=Number(o.ia);if(Number.isFinite(v))d.ia=Math.round(Math.min(3,Math.max(0.33,v))*100)/100;}
if(typeof o.acc==='string')d.acc=[...ACC].filter(ch=>o.acc.includes(ch)).join('');
d.pz=cleanPieces('pz' in o?o.pz:d.pz);
return d;}
// Pièces sur mesure : [forme, ancre, x,y,z, tx,ty,tz, rx,ry,rz, couleur, collée]. Positions et tailles en rayons d'ancre, rotations en degrés.
const SHAPES=['sphere','goutte','cone','cylindre','tore','boite'],ANCHORS=['tete','corps','mains','dos','jambes'];
function cleanPieces(a){if(!Array.isArray(a))return[];const out=[],num=(x,lo,hi,def)=>{x=Number(x);return Number.isFinite(x)?Math.round(Math.min(hi,Math.max(lo,x))*100)/100:def;};
for(let v of a.slice(0,24)){if(v&&!Array.isArray(v)&&typeof v==='object'){const P=v.pos||[],T=v.taille||[],Q=v.rot||[];v=[v.forme,v.ancre,P[0],P[1],P[2],T[0],T[1],T[2],Q[0],Q[1],Q[2],v.couleur,v.colle];}
if(!Array.isArray(v)||!SHAPES.includes(v[0])||!ANCHORS.includes(v[1])||!/^#[0-9a-f]{6}$/i.test(v[11]))continue;
out.push([v[0],v[1],num(v[2],-3,3,0),num(v[3],-3,3,0),num(v[4],-3,3,0),num(v[5],0.02,2,0.2),num(v[6],0.02,2,0.2),num(v[7],0.02,2,0.2),num(v[8],-360,360,0),num(v[9],-360,360,0),num(v[10],-360,360,0),v[11].toLowerCase(),v[12]&&v[12]!=='0'?1:0]);}
return out;}
function encode(c){const b=new TextEncoder().encode(JSON.stringify(clean(c)));let s='';b.forEach(x=>{s+=String.fromCharCode(x);});return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');}
function decode(str){try{const s=atob(String(str).replace(/-/g,'+').replace(/_/g,'/'));return clean(JSON.parse(new TextDecoder().decode(Uint8Array.from(s,ch=>ch.charCodeAt(0)))));}catch(e){return null;}}

// Hasard reproductible : une même peluche a toujours les mêmes petites bosses
let R=Math.random;
function rng(seed){let a=seed>>>0;return()=>{a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return((t^(t>>>14))>>>0)/4294967296;};}
function hashStr(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619);}return h>>>0;}

// Couleurs
const col=c=>new THREE.Color(c),shade=(c,k)=>col(c).multiplyScalar(k),mix=(a,b,t)=>col(a).lerp(col(b),t),hex=c=>'#'+col(c).getHexString();
const lum=c=>{const k=col(c);return 0.2126*k.r+0.7152*k.g+0.0722*k.b;};
const ink=c=>lum(c)>0.55?'#1a1a1a':'#f6f6f2';

// Textures
function cv(w,h){h=h||w;const c=document.createElement('canvas');c.width=w;c.height=h;return[c,c.getContext('2d')];}
function fabTex(base,lo,n,rep){const[c,g]=cv(512);g.fillStyle=base;g.fillRect(0,0,512,512);
for(let i=0;i<n;i++){const x=Math.random()*512,y=Math.random()*512,a=Math.random()*6.28,l=2+Math.random()*6;g.strokeStyle=Math.random()<0.5?lo:'#ffffff';g.globalAlpha=0.15+Math.random()*0.3;g.lineWidth=0.6+Math.random()*0.9;g.beginPath();g.moveTo(x,y);g.quadraticCurveTo(x+Math.cos(a)*l*0.5+1,y+Math.sin(a)*l*0.5,x+Math.cos(a)*l,y+Math.sin(a)*l);g.stroke();}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(rep,rep);t.anisotropy=8;return t;}
function bumpTex(){const[c,g]=cv(256);g.fillStyle='#808080';g.fillRect(0,0,256,256);g.globalAlpha=0.6;for(let i=0;i<12000;i++){const v=Math.floor(60+Math.random()*140);g.fillStyle='rgb('+v+','+v+','+v+')';g.fillRect(Math.random()*256,Math.random()*256,1.2,2.5);}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(6,6);return t;}
function knitTex(){const[c,g]=cv(256);g.fillStyle='#ededed';g.fillRect(0,0,256,256);for(let x=0;x<256;x+=16){g.fillStyle='rgba(0,0,0,0.16)';g.fillRect(x,0,5,256);g.fillStyle='rgba(255,255,255,0.4)';g.fillRect(x+8,0,4,256);}
for(let y=0;y<256;y+=8){g.fillStyle='rgba(0,0,0,0.05)';g.fillRect(0,y,256,2);}const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(10,2);return t;}
let FAB,HAIR,BMP,KNIT;
function shared(){if(FAB)return;FAB=fabTex('#f2f2f2','#c9c9c9',20000,3);HAIR=fabTex('#eeeeee','#a0a0a0',26000,4);BMP=bumpTex();KNIT=knitTex();}
function noise(g,w,h,n){for(let i=0;i<n;i++){g.fillStyle=R()<0.5?'rgba(255,255,255,0.06)':'rgba(0,0,0,0.08)';g.fillRect(R()*w,R()*h,2,2);}}
function rr(g,x,y,w,h,rad){g.beginPath();if(g.roundRect)g.roundRect(x,y,w,h,rad);else g.rect(x,y,w,h);}
function dash(g,c,segs){g.save();g.setLineDash([10,7]);g.strokeStyle=c;g.lineWidth=2.2;g.beginPath();segs.forEach(s=>{g.moveTo(s[0],s[1]);g.lineTo(s[2],s[3]);});g.stroke();g.restore();}
function clothTex(c,rf,kind,mt,ac){const[cn,g]=cv(512,256),[e,ge]=cv(512,256),base=col(c);g.fillStyle=hex(base);g.fillRect(0,0,512,256);
if(mt==='rayures'){g.fillStyle=hex(ac||shade(base,0.6));for(let y=14;y<256;y+=42)g.fillRect(0,y,512,15);}
if(mt==='camo'){const tones=[shade(base,0.6),mix(base,'#4b5320',0.5),shade(base,1.35)];for(let i=0;i<80;i++){g.fillStyle=hex(tones[i%3]);g.beginPath();g.ellipse(R()*512,R()*256,8+R()*18,12+R()*22,R()*3,0,7);g.fill();}}
if(mt==='carreaux'){g.globalAlpha=0.38;g.fillStyle=hex(ac||'#111111');for(let x=0;x<512;x+=48)g.fillRect(x,0,16,256);for(let y=0;y<256;y+=72)g.fillRect(0,y,512,24);
g.globalAlpha=0.5;g.fillStyle=hex(shade(base,0.45));for(let x=24;x<512;x+=48)g.fillRect(x,0,3,256);for(let y=36;y<256;y+=72)g.fillRect(0,y,512,4);g.globalAlpha=1;}
if(mt==='taches'){g.fillStyle=hex(ac||'#222222');for(let i=0;i<14;i++){const x=R()*512,y=R()*256,r=18+R()*22,pts=[];for(let k=0;k<12;k++){const a=k/12*Math.PI*2,q=r*(0.75+R()*0.35);pts.push([x+Math.cos(a)*q*0.7,y+Math.sin(a)*q]);}
g.beginPath();pts.forEach((p,k)=>{const n=pts[(k+1)%12],mx=(p[0]+n[0])/2,my=(p[1]+n[1])/2;if(k===0)g.moveTo(mx,my);else g.quadraticCurveTo(p[0],p[1],mx,my);});g.quadraticCurveTo(pts[0][0],pts[0][1],(pts[0][0]+pts[1][0])/2,(pts[0][1]+pts[1][1])/2);g.closePath();g.fill();}}
noise(g,512,256,9000);ge.fillStyle='#000';ge.fillRect(0,0,512,256);
if(rf)for(const y of(kind==='manche'?[100,170]:[150,200])){g.fillStyle='#d4ee3a';g.fillRect(0,y,512,30);g.fillStyle='#e6eaee';g.fillRect(0,y+9,512,12);ge.fillStyle='#4a5410';ge.fillRect(0,y,512,30);ge.fillStyle='#ffffff';ge.fillRect(0,y+9,512,12);}
dash(g,'rgba(255,255,255,0.28)',[[0,10,512,10],[0,246,512,246]]);const t=new THREE.CanvasTexture(cn);t.anisotropy=8;return[t,rf?new THREE.CanvasTexture(e):null];}
function textTex(txt,c){const[cn,g]=cv(512,160);g.font='bold 104px "Arial Black",Arial,sans-serif';const w=g.measureText(txt).width||1,k=Math.min(1,470/w);
g.save();g.translate(256,84);g.scale(k,1);g.textAlign='center';g.textBaseline='middle';g.lineJoin='round';g.lineWidth=12;g.strokeStyle=c==='#1a1a1a'?'rgba(255,255,255,0.55)':'rgba(0,0,0,0.45)';g.strokeText(txt,0,0);g.fillStyle=c;g.fillText(txt,0,0);g.restore();
const t=new THREE.CanvasTexture(cn);t.anisotropy=8;return t;}
function shieldTex(num){const[c,g]=cv(256);rr(g,40,28,176,200,26);g.fillStyle='#7d1612';g.fill();g.lineWidth=5;g.strokeStyle='#3d0a08';g.stroke();
g.textAlign='center';g.textBaseline='middle';rr(g,52,40,152,34,14);g.fillStyle='#f4f1ea';g.fill();g.fillStyle='#7d1612';g.font='bold 21px sans-serif';g.fillText('FIREFIGHTER',128,58);
rr(g,62,84,132,96,10);g.fillStyle='#c8261f';g.fill();if(num){g.fillStyle='#ffffff';g.font='bold '+(num.length>2?(num.length>4?34:50):76)+'px sans-serif';g.fillText(num,128,135);}
rr(g,70,190,116,30,8);g.fillStyle='#4a0d0a';g.fill();const t=new THREE.CanvasTexture(c);t.anisotropy=8;return t;}
function discTex(num){const[c,g]=cv(128);g.fillStyle='#151515';g.beginPath();g.arc(64,64,60,0,7);g.fill();g.fillStyle='#ffffff';g.font='bold '+(num.length>2?30:52)+'px sans-serif';g.textAlign='center';g.textBaseline='middle';g.fillText(num,64,68);const t=new THREE.CanvasTexture(c);t.anisotropy=8;return t;}
function tagTex(){const[c,g]=cv(128);g.fillStyle='#fbf8f2';g.fillRect(0,0,128,128);g.fillStyle='#c8261f';g.beginPath();g.arc(56,40,10,0,7);g.arc(72,40,10,0,7);g.fill();g.beginPath();g.moveTo(47,45);g.lineTo(64,64);g.lineTo(81,45);g.fill();g.fillStyle='#b8b2a8';for(let i=0;i<3;i++)g.fillRect(30,80+i*12,68-i*14,4);return new THREE.CanvasTexture(c);}
function irisTex(c1,c2){const[c,g]=cv(256);const gr=g.createLinearGradient(0,0,0,256);gr.addColorStop(0,'#0a0a10');gr.addColorStop(0.2,'#0a0a10');gr.addColorStop(0.23,c1);gr.addColorStop(0.45,c2);gr.addColorStop(0.62,c1);gr.addColorStop(0.68,'#140d0b');gr.addColorStop(1,'#140d0b');g.fillStyle=gr;g.fillRect(0,0,256,256);
g.globalAlpha=0.22;for(let x=0;x<256;x+=3){g.fillStyle=R()<0.5?'#ffffff':'#000000';g.fillRect(x,58,1.5,25+R()*95);}g.globalAlpha=1;return new THREE.CanvasTexture(c);}
function fuzz(m){m.onBeforeCompile=sh=>{sh.fragmentShader=sh.fragmentShader.replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n totalEmissiveRadiance += diffuseColor.rgb * pow(1.0 - saturate(dot(normal, normalize(vViewPosition))), 2.2) * 0.32;');};m.customProgramCacheKey=()=>'fuzz';return m;}

// Formes
function blob(rx,ry,rz,o){o=o||{};const big=Math.max(rx,ry,rz)>=2.5,part=o.t1||o.pl;
const g=part?new THREE.SphereGeometry(1,big?64:32,big?40:20,o.p0||0,o.pl||Math.PI*2,o.t0||0,(o.t1||Math.PI)-(o.t0||0)):new THREE.SphereGeometry(1,big?64:32,big?48:24);
const p=g.attributes.position;const s=R()*10;const L=o.lump===undefined?0.025:o.lump,P=o.pear||0,T=o.tip||0,Q=o.sq||0;
for(let i=0;i<p.count;i++){let x=p.getX(i),y=p.getY(i),z=p.getZ(i);if(Q){x=Math.sign(x)*Math.pow(Math.abs(x),Q);y=Math.sign(y)*Math.pow(Math.abs(y),Q);z=Math.sign(z)*Math.pow(Math.abs(z),Q);}
const f=(1+P*(-y))*(y<0?1+y*T:1);const n=1+L*(Math.sin(x*4+s)*Math.cos(y*3.3+s)+0.6*Math.sin(z*4.6+s*1.7));p.setXYZ(i,x*rx*f*n,y*ry*n,z*rz*f*n);}g.computeVertexNormals();return g;}
function visor(w,len,back,droop){const g=new THREE.CylinderGeometry(1,1,1,40,1,false,-Math.PI/2,Math.PI),p=g.attributes.position;
for(let i=0;i<p.count;i++){const x=p.getX(i)*w,z=p.getZ(i)*len+back;p.setXYZ(i,x,p.getY(i)*0.5-Math.max(0,z-back-len*0.45)*droop,z);}g.computeVertexNormals();return g;}

function build(cfg){shared();const c=clean(cfg);R=rng(hashStr(JSON.stringify(c)));
const G=new THREE.Group(),owned=[],own=t=>{owned.push(t);return t;};
// Couleurs données en sRGB, converties en linéaire pour un rendu avec tons doux (ACES) ; les images couleur sont marquées sRGB
const LIN=o=>{if(o.color!==undefined)o.color=new THREE.Color(o.color).convertSRGBToLinear();if(o.emissive!==undefined)o.emissive=new THREE.Color(o.emissive).convertSRGBToLinear();if(o.map)o.map.encoding=THREE.sRGBEncoding;if(o.emissiveMap)o.emissiveMap.encoding=THREE.sRGBEncoding;return o;};
const SM=o=>new THREE.MeshStandardMaterial(LIN(o)),FZ=o=>fuzz(SM(o));
const decal=t=>SM({map:own(t),transparent:true,alphaTest:0.4,roughness:0.85,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2});
function clothMat(k,rf,kind,mt){const[t,e]=clothTex(k,rf,kind,mt,c.ac);own(t);if(e)own(e);return FZ({map:t,emissive:e?0xffffff:0x000000,emissiveMap:e,emissiveIntensity:e?0.08:0,roughness:0.85,bumpMap:BMP,bumpScale:0.15,side:THREE.DoubleSide});}
function mk(geo,mat){const m=new THREE.Mesh(geo,mat);m.castShadow=m.receiveShadow=true;return m;}
// PART étiquette les éléments dont la zone (tête, corps, objet) ne se devine pas à leur position
let PART=null;
function add(m,pos,rot,par){if(pos)m.position.set(pos[0],pos[1],pos[2]);if(rot)m.rotation.set(rot[0],rot[1],rot[2]);(par||G).add(m);if(PART&&!par)m.userData.part=PART;m.updateMatrixWorld(true);return m;}
const ray=new THREE.Raycaster(),NM=new THREE.Matrix3();
function hitAt(t,o,d){ray.set(o,d);const h=ray.intersectObjects(t,false)[0];if(!h)return null;NM.getNormalMatrix(h.object.matrixWorld);return{p:h.point.clone(),n:h.face.normal.clone().applyMatrix3(NM).normalize()};}
function stick(obj,t,x,y,emb,par){(par||G).add(obj);if(PART&&!par)obj.userData.part=PART;const h=hitAt(t,V(x,y,60),FWD);if(!h){obj.position.set(x,y,0);return obj;}obj.position.copy(h.p).addScaledVector(h.n,-emb);obj.lookAt(h.p.clone().addScaledVector(h.n,5));obj.updateMatrixWorld(true);return obj;}
function conform(t,ctr,u,v,w,h,seg,d,off){const geo=new THREE.PlaneGeometry(w,h,seg,seg);const p=geo.attributes.position;for(let i=0;i<p.count;i++){const q=ctr.clone().addScaledVector(u,p.getX(i)).addScaledVector(v,p.getY(i));const hh=hitAt(t,q.clone().addScaledVector(d,-60),d);const pt=hh?hh.p.addScaledVector(d,-off):q;p.setXYZ(i,pt.x,pt.y,pt.z);}geo.computeVertexNormals();return geo;}
const tor=(R0,t,mat,y,zs,z)=>{const m=add(mk(new THREE.TorusGeometry(R0,t,12,96),mat),[0,y,z||0],[Math.PI/2,0,0]);m.scale.set(1,zs,1);m.updateMatrixWorld(true);return m;};
const tube=(pts,r,mat,closed)=>add(mk(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts,!!closed),Math.max(40,pts.length*16),r,8,!!closed),mat));
// Points posés sur une surface, vus depuis l'extérieur (sangles, chaîne…)
function onSurf(t,pts,off){return pts.map(([o,d])=>{const h=hitAt(t,o,d);return h?h.p.addScaledVector(h.n,off):o.clone().addScaledVector(d,40);});}
// Pique orientée vers l'extérieur d'un ellipsoïde (cheveux hérissés, crête)
function spike(cy,cz,rx,ry,rz,th,ph,rad,len,mat){const s=Math.sin(th),p=V(-Math.cos(ph)*s*rx,Math.cos(th)*ry,Math.sin(ph)*s*rz),n=V(p.x/(rx*rx),p.y/(ry*ry),p.z/(rz*rz)).normalize();
const m=mk(new THREE.ConeGeometry(rad,len,10),mat);m.position.set(p.x,cy+p.y,cz+p.z).addScaledVector(n,len*0.35);m.quaternion.setFromUnitVectors(Y,n);G.add(m);m.updateMatrixWorld(true);return m;}

// Coutures : tube fin texturé en pointillés, comme des points de couture
const[stc,stg]=cv(64,8);stg.clearRect(0,0,64,8);stg.fillStyle='#ffffff';stg.fillRect(10,1,30,6);
function seam(pts,col,closed,par){if(pts.length<2)return null;const curve=new THREE.CatmullRomCurve3(pts,!!closed),len=curve.getLength(),t=own(new THREE.CanvasTexture(stc));t.wrapS=THREE.RepeatWrapping;t.repeat.set(Math.max(1,Math.round(len/0.8)),1);
const m=new THREE.Mesh(new THREE.TubeGeometry(curve,Math.max(24,Math.round(len*4)),0.08,5,!!closed),SM({color:col,map:t,transparent:true,alphaTest:0.5,roughness:0.9}));m.userData.seam=true;(par||G).add(m);return m;}
const ring=(r1,r2,axis,at,n)=>{const pts=[];for(let i=0;i<(n||36);i++){const a=i/(n||36)*Math.PI*2,u=Math.cos(a),v=Math.sin(a);pts.push(axis==='y'?V(u*r1,at,v*r2):V(u*r1,v*r2,at));}return pts;};

// Matières (le style change la peau : fourrure pour les animaux, peau lisse pour l'avatar)
// Petit monstre : la fourrure prend la couleur de la capuche s'il en porte une (la capuche devient la fourrure), le visage est plus clair
const st=c.st,animal=['ours','lapin','chat'].includes(st),furry=animal||st==='monstre',fur=c.fc||(st==='monstre'&&c.hw==='capuche'?c.hwc:c.hc),skinC=st==='monstre'?hex(mix(c.sk,'#f7e7da',0.6)):c.sk;
const mFur=FZ({color:fur,map:HAIR,bumpMap:BMP,bumpScale:0.5,roughness:1,side:THREE.DoubleSide}),mFurL=FZ({color:mix(fur,'#ffffff',0.55),map:FAB,roughness:1});
const mSkin=st==='avatar'?SM({color:skinC,roughness:0.55}):FZ({color:skinC,map:FAB,bumpMap:BMP,bumpScale:0.08,roughness:1}),mBodySkin=furry?mFur:mSkin;
const mHair=st==='monstre'?mFur:FZ({color:c.hc,map:HAIR,bumpMap:BMP,bumpScale:0.45,roughness:1,side:THREE.DoubleSide});
const mBrow=FZ({color:shade(c.hc,0.72),map:HAIR,roughness:1});
const mBlush=FZ({color:mix(c.sk,'#f07f90',0.5),map:FAB,roughness:1}),mFreckle=SM({color:shade(c.sk,0.7),roughness:1});
// Yeux foncés : on éclaircit l'iris pour qu'il reste lisible au lieu de faire un rond noir
const eyeBase=lum(c.ec)<0.1?mix(c.ec,'#8a6440',0.6):col(c.ec);
const mIris=SM({map:own(irisTex(hex(eyeBase),hex(mix(eyeBase,'#ffffff',0.5)))),roughness:0.06,metalness:0.1}),mLash=SM({color:0x2a1d18,roughness:0.6}),mShine=new THREE.MeshBasicMaterial({color:0xffffff});
const mMouth=SM({color:0x5a1e22,roughness:0.7,side:THREE.DoubleSide}),mTongue=SM({color:0xe8848f,roughness:0.6}),mNose=FZ({color:shade(c.sk,0.92),map:FAB,roughness:1});
const mP=FZ({color:c.pc,map:FAB,bumpMap:BMP,bumpScale:0.2,roughness:0.95}),mDark=FZ({color:0x1c1c1e,roughness:0.75,map:FAB,side:THREE.DoubleSide});
const mSilver=SM({color:0xcfd5dc,metalness:0.6,roughness:0.28}),mGold=SM({color:0xd9a833,metalness:0.7,roughness:0.3}),mGray=SM({color:0xd9dce0,roughness:0.5,metalness:0.2});
const mAcc=FZ({color:c.ac,map:FAB,bumpMap:BMP,bumpScale:0.1,roughness:0.7}),mWhite=SM({color:0xf2f2f2,roughness:0.6});
const mLime=SM({color:0x9fd63a,roughness:0.5}),mScreen=SM({color:0x1d2a1a,roughness:0.15,metalness:0.2});
const has=k=>c.acc.includes(k),hats=!['aucun','bandeau'].includes(c.hw),hood=c.hw==='capuche'&&st!=='monstre';
// Poses : direction de chaque bras depuis l'épaule, vers la main. 'hold' = bras vers l'avant (tient l'objet), 'down' = le long du corps
const POSE={assis:{l:'sit',a:['hold','hold']},debout:{l:'stand',a:['hold','hold']},coucou:{l:'stand',a:['down','wave']},bravo:{l:'stand',a:['up','up']},calin:{l:'stand',a:['open','open']},
coeur:{l:'sit',a:['heart','heart']},pensif:{l:'sit',a:['chin','lap']},tailleur:{l:'cross',a:['hold','hold']},dab:{l:'stand',a:['dabB','dabA']}}[c.po]||{l:'sit',a:['hold','hold']};
const holding=POSE.a[0]==='hold',showIt=holding?c.it:(c.po==='coeur'?'coeur':'aucun'),mpE=(c.mp==='mains'&&!holding)?'droite':c.mp;
const ARM={wave:[0.5,0.82,0.28],up:[0.42,0.88,0.2],open:[0.85,0.05,0.52],heart:[-0.45,0.05,0.89],chin:[-0.55,0.45,0.72],lap:[-0.3,-0.6,0.74],dabA:[0.75,0.62,0.2],dabB:[-0.8,0.45,0.4]};

// Corps et haut
add(mk(blob(8.6,9.2,7.6,{pear:0.1}),st==='monstre'?mFur:mP),[0,9.2,0]);
const layered=['gilet','veste','costume'].includes(c.tp);
const shirt=add(mk(blob(9.0,9.65,7.98,{pear:0.1,lump:0,t0:0,t1:1.86}),clothMat(layered?c.t2:c.tc,!layered&&c.rf,'torse',layered?'uni':c.mt)),[0,9.2,0]);
let outer=shirt;
if(c.tp==='gilet'){outer=add(mk(blob(9.15,9.78,8.1,{pear:0.1,lump:0,t0:0.62,t1:1.86}),clothMat(c.tc,c.rf,'torse',c.mt)),[0,9.2,0]);tor(9.05,0.35,FZ({color:shade(c.tc,0.85),map:FAB,roughness:0.9}),6.4,0.883);}
if(c.tp==='veste'||c.tp==='costume'){const gap=c.tp==='costume'?0.9:0.55;outer=add(mk(blob(9.18,9.8,8.12,{pear:0.1,lump:0,t0:0.12,t1:1.86,p0:Math.PI/2+gap/2,pl:Math.PI*2-gap}),clothMat(c.tc,c.rf,'torse',c.mt)),[0,9.2,0]);
if(c.tp==='veste')for(const s of[-1,1])for(const y of[15.0,12.6,10.2,7.8])stick(mk(blob(0.34,0.34,0.18,{lump:0}),mSilver),[outer],s*3.3,y,-0.05);}
const collar=c.tp==='gilet'?shade(c.t2,0.9):layered?col(c.t2):shade(c.tc,0.85),mCol=FZ({color:collar,map:FAB,roughness:0.9});
const colT=tor(4.9,0.95,mCol,17.1,0.88),colB=add(mk(blob(4.6,1.8,4.1,{lump:0}),mCol),[0,16.4,0.2]),torso=[...new Set([outer,shirt,colT,colB])];
const ovr=c.bt==='salopette';
if(!ovr){const belt=tor(8.45,0.55,FZ({color:shade(c.pc,0.45),map:FAB,roughness:0.75}),5.85,0.875);stick(mk(blob(1.0,0.7,0.3,{lump:0}),mSilver),[belt],0,5.85,-0.1);}
else{// Salopette : ceinture du même tissu, plastron avec poche, bretelles qui passent sur les épaules et se croisent dans le dos, boutons métal
const mOv=FZ({color:c.pc,map:FAB,bumpMap:BMP,bumpScale:0.2,roughness:0.95,side:THREE.DoubleSide}),mOvS=FZ({color:shade(c.pc,0.82),map:FAB,roughness:0.9,side:THREE.DoubleSide}),stc=mix(c.pc,'#e8b04a',0.55);
tor(8.5,0.75,mOv,6.1,0.88);
const bib=add(mk(conform([shirt],V(0,10.4,0),X,Y,8.2,7.2,18,FWD,0.16),mOv));
add(mk(conform([shirt],V(0,10.9,0),X,Y,3.6,2.6,10,FWD,0.3),mOvS));
seam(onSurf([bib],[[V(-1.8,12.2,40),FWD],[V(1.8,12.2,40),FWD]],0.06),stc);seam(onSurf([bib],[[V(-1.8,9.6,40),FWD],[V(-1.8,12.2,40),FWD]],0.06),stc);seam(onSurf([bib],[[V(1.8,9.6,40),FWD],[V(1.8,12.2,40),FWD]],0.06),stc);
for(const s of[-1,1]){const pts=[];for(let b=1.0;b>=-1.5;b-=0.1){const d=V(0,Math.cos(b),Math.sin(b)),x=s*(3.3-Math.max(0,-b-0.2)*2.6);pts.push([V(x,9.0,0).addScaledVector(d,30),d.clone().negate()]);}
tube(onSurf(torso,pts,0.32),0.48,mOvS);stick(mk(new THREE.CylinderGeometry(0.5,0.5,0.25,18).rotateX(Math.PI/2),mSilver),torso,s*3.3,13.5,-0.45);}}
if(c.tp==='gilet'){const mPk=FZ({color:shade(c.tc,0.88),map:FAB,bumpMap:BMP,bumpScale:0.15,roughness:0.9});
for(const s of[-1,1]){const pk=new THREE.Group();pk.add(mk(blob(2.6,1.6,0.8,{lump:0.01}),mPk));const fl=mk(blob(2.7,0.55,0.85,{lump:0}),mPk);fl.position.set(0,1.3,0.1);pk.add(fl);stick(pk,[outer],s*3.4,8.5,0.4);
add(mk(conform([outer],V(s*3,13.9,0),X,Y,1.0,5.6,12,FWD,0.15),mDark));stick(mk(blob(0.75,0.95,0.25,{lump:0}),mSilver),[outer],s*3,13.6,-0.15);}
add(mk(conform([outer],V(-0.3,12.8,0),V(0.5,-0.867,0),V(0.867,0.5,0),1.1,13.6,24,FWD,0.28),mDark));}
if(c.tp==='sweat'){if(!hood)add(mk(blob(6.4,3.6,3.2,{lump:0.01}),clothMat(c.tc,false,'torse',c.mt)),[0,18.2,-6.6],[0.55,0,0]);
stick(mk(blob(4.6,2.3,0.7,{lump:0.01}),FZ({color:shade(c.tc,0.92),map:FAB,roughness:0.9})),[shirt],0,8.4,0.35);
for(const s of[-1,1])stick(mk(blob(0.22,1.6,0.22,{lump:0}),SM({color:c.t2,roughness:0.7})),[shirt],s*1.3,14.9,-0.05);}
if(c.tp==='chemise'){const mB=SM({color:shade(c.tc,0.55),roughness:0.5});for(const y of[15.4,13.2,11.0,8.8])stick(mk(blob(0.32,0.32,0.15,{lump:0}),mB),[shirt],0,y,-0.05);
for(const s of[-1,1]){const k=stick(mk(blob(1.6,0.9,0.3,{lump:0}),mCol),[shirt],s*1.7,16.9,-0.05);k.rotateZ(s*0.55);}}
if(c.tp==='costume'){const mT=FZ({color:c.ac,map:FAB,roughness:0.6});stick(mk(blob(0.85,3.1,0.35,{lump:0,tip:0.45}),mT),[shirt],0,12.9,0.05);stick(mk(blob(0.75,0.6,0.4,{lump:0}),mT),[shirt],0,15.9,0.05);}
if(c.tt){const tc=ink(c.tc);
if((c.tp==='tshirt'||c.tp==='sweat')&&!c.im)add(mk(conform([shirt],V(0,12.8,0),X,Y,7,2.4,14,FWD,0.12),decal(textTex(c.tt,tc))));
if(c.tp==='chemise')add(mk(conform([shirt],V(4.4,12.4,0),X,Y,4.4,1.5,10,FWD,0.12),decal(textTex(c.tt,tc))));
if(c.tp!=='costume'&&!has('k'))add(mk(conform([outer],V(0,12.4,0),NX,Y,11,3.8,16,BACK,0.14),decal(textTex(c.tt,tc))));}

// Coutures du haut : côtés et milieu du dos
{const topCol=shade(layered?c.tc:c.tc,0.55);for(const sx of[-1,1]){const pts=[];for(let y=7.4;y<=16.2;y+=0.6)pts.push([V(sx*30,y,0.4),V(-sx,0,0)]);seam(onSurf(torso,pts,0.06),topCol);}
const bk=[];for(let y=7.4;y<=16.6;y+=0.6)bk.push([V(0,y,-30),V(0,0,1)]);if(!has('k'))seam(onSurf(torso,bk,0.06),topCol);}

// Imprimé du haut découpé dans la photo, collé sur la poitrine (sur le gilet s'il y en a un)
if(c.im&&c.tp!=='costume'){const img=new Image(),tx=own(new THREE.Texture(img));tx.anisotropy=4;img.onload=()=>{tx.needsUpdate=true;if(HOOKS.onTex)HOOKS.onTex();};img.src='data:image/'+c.imt+';base64,'+c.im;
const S0=7.4,W=c.ia>=1?S0:S0*c.ia,H=Math.min(8.5,c.ia>=1?S0/c.ia:S0);add(mk(conform([c.tp==='gilet'?outer:shirt],V(0,11.6,0),X,Y,W,H,16,FWD,0.13),SM({map:tx,transparent:true,roughness:0.85,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-3})));}

// Bras, mains, montre
const longS=c.tp!=='tshirt',mSl=longS?clothMat(c.tp==='gilet'?c.t2:c.tc,c.rf,'manche',c.tp==='gilet'?'uni':c.mt):null,mCap=longS?null:clothMat(c.tc,c.rf,'manche',c.mt);
const mHand=c.gv?SM({color:c.gv,roughness:0.45}):mBodySkin;
// Bras selon la pose ; debout sans rien à tenir, les bras tombent le long du corps
const empty=showIt==='aucun'&&mpE!=='mains';
for(const s of[-1,1]){let kind=POSE.a[s<0?0:1];if(kind==='hold'&&POSE.l==='stand'&&empty)kind='down';const a=mk(blob(2.8,5.1,2.8),longS?mSl:mBodySkin);
if(kind==='hold')add(a,[s*6.6,11.3,3.8],[-0.85,0,-s*0.45]);else if(kind==='down')add(a,[s*10.0,10.2,0.6],[0.1,0,s*0.2]);
else{const d=V(s*ARM[kind][0],ARM[kind][1],ARM[kind][2]).normalize();a.position.copy(V(s*7.0,15.0,1.2)).addScaledVector(d,4.4);a.quaternion.setFromUnitVectors(V(0,-1,0),d);add(a);}
a.userData.part='arm';
if(!longS){const cp=mk(blob(3.1,2.7,3.1,{lump:0.01}),mCap);cp.position.set(0,2.7,0);a.add(cp);}
if(longS)seam(ring(2.2,2.2,'y',-3.3),shade(c.tp==='gilet'?c.t2:c.tc,0.55),true,a);
const gl=mk(blob(1.75,1.65,1.75),mHand);gl.position.set(0,-4.8,0);a.add(gl);const th=mk(blob(0.6,0.95,0.6,{lump:0}),mHand);th.position.set(-s*1.3,-4.1,0.9);th.rotation.z=s*0.5;a.add(th);
if(c.gv){const cf=mk(new THREE.TorusGeometry(1.75,0.35,10,32),mHand);cf.position.set(0,-4.0,0);cf.rotation.x=Math.PI/2;a.add(cf);}
if(has('w')&&s<0){const wb=mk(new THREE.TorusGeometry(1.98,0.36,10,32),mDark);wb.position.set(0,-3.2,0);wb.rotation.x=Math.PI/2;a.add(wb);const fc=mk(new THREE.CylinderGeometry(0.75,0.75,0.35,20),mGold);fc.rotation.x=Math.PI/2;fc.position.set(0,-3.2,2.15);a.add(fc);}}

// Jambes et chaussures
const shoeMat=c.sh==='chaussures'?SM({color:c.sc,roughness:0.18,metalness:0.15}):SM({color:c.sc,roughness:0.55});
const soleMat=SM({color:lum(c.sc)<0.15?0x3a3b3f:shade(c.sc,0.75),roughness:0.9});
// Assise : jambes tendues vers l'avant. Debout : jambes sous le corps, semelles au sol
// En tailleur : jambes repliées qui se croisent devant
PART='leg';const paw=st==='monstre',legMat=paw?mFur:(c.bt==='short'?mBodySkin:mP),mPad=FZ({color:mix(fur,'#f2b8c0',0.55),map:FAB,roughness:1});
for(const s of[-1,1]){
if(POSE.l==='stand'){// Debout : jambe fuselée sous le corps, pied pointé vers l'avant, semelle à plat au sol
const lg=add(mk(blob(2.75,4.4,2.75,{lump:0.015}),legMat),[s*4.0,-2.6,0.9]);if(!paw)seam(ring(1.75,1.75,'y',-3.4),shade(c.pc,0.55),true,lg);
if(!paw&&c.bt==='short'){const sh2=mk(blob(3.0,2.2,3.0,{lump:0.01}),mP);sh2.position.set(0,2.4,0);lg.add(sh2);}
if(!paw&&c.bt==='jogging'){const pts=[];for(let y=1.4;y>=-6.2;y-=0.5){const k=Math.sqrt(Math.max(0,1-((y+2.6)/4.4)**2));pts.push(V(s*(4.0+2.78*k),y,0.9));}tube(pts,0.24,mAcc);add(mk(new THREE.TorusGeometry(1.9,0.42,10,28),mP),[s*4.0,-6.0,0.9],[Math.PI/2,0,0]);}
if(paw){add(mk(blob(2.6,1.7,3.3,{lump:0.03}),mFur),[s*4.0,-7.5,1.6]);add(mk(blob(1.7,0.3,2.1,{lump:0}),mPad),[s*4.0,-9.15,1.9]);}
else{if(c.sh==='bottes')add(mk(blob(2.95,2.2,2.95,{lump:0}),shoeMat),[s*4.0,-5.9,0.9]);
add(mk(blob(2.7,1.75,3.7,{lump:0,sq:0.75}),shoeMat),[s*4.0,-7.6,1.9]);add(mk(blob(2.85,c.sh==='baskets'?0.6:0.42,3.85,{lump:0,sq:0.6}),c.sh==='baskets'?mWhite:soleMat),[s*4.0,-9.1,1.9]);
if(c.sh==='baskets')add(mk(blob(1.15,0.4,1.5,{lump:0}),mWhite),[s*4.0,-6.0,3.4],[0.5,0,0]);}
continue;}
// Assise (jambes tendues) ou en tailleur (jambes repliées qui se croisent devant)
const cr=POSE.l==='cross',rot=cr?[0,-s*1.2,0]:[0,s*0.25,0];
const leg=add(mk(blob(3.3,2.9,4.0),legMat),cr?[s*3.4,s>0?1.9:2.5,5.4]:[s*4.6,2.9,4.6],rot);if(!paw)seam(ring(2.62,2.3,'z',2.4),shade(c.pc,0.55),true,leg);
if(!paw&&c.bt==='short'){const sh=mk(blob(3.5,3.1,2.3,{lump:0.01}),mP);sh.position.set(0,0,-1.9);leg.add(sh);}
if(!paw&&c.bt==='jogging'){const pts=[];for(let z=-3.4;z<=3.2;z+=0.4){const k=Math.sqrt(Math.max(0,1-(z/4.0)**2));pts.push(leg.localToWorld(V(s*(3.3*k+0.05),0.3,z)));}tube(pts,0.24,mAcc);
const cu=mk(new THREE.TorusGeometry(2.2,0.45,10,28),mP);cu.position.set(0,0,3.2);leg.add(cu);}
const b=leg.localToWorld(V(0,0,3.3));add(mk(blob(3.0,2.95,2.1),paw?mFur:shoeMat),[b.x,b.y,b.z],rot);
const so=leg.localToWorld(V(0,0,!paw&&c.sh==='baskets'?5.4:5.3));add(mk(blob(paw?1.9:2.7,paw?1.8:2.6,!paw&&c.sh==='baskets'?0.6:0.4,{lump:0}),paw?mPad:soleMat),[so.x,so.y,so.z],rot);
if(!paw&&c.sh==='baskets'){const lc=leg.localToWorld(V(0,1.9,3.6));add(mk(blob(1.2,0.5,1.0,{lump:0}),mWhite),[lc.x,lc.y,lc.z],rot);
const rim=leg.localToWorld(V(0,0,5.1));add(mk(new THREE.TorusGeometry(2.6,0.42,8,36),mWhite),[rim.x,rim.y,rim.z],rot);}}
PART=null;add(mk(new THREE.BoxGeometry(0.08,2.2,1.5),SM({map:own(tagTex()),roughness:0.9})),[-7.0,2.4,-2.5],[0,0,-0.35]);

// Tête et cheveux
const head=add(mk(blob(9.6,8.8,9.0,{lump:0.012,pear:0.05}),animal?mFur:mSkin),[0,24.6,0.6]);
// Petit monstre : la fourrure remplace les cheveux (calotte et côtés), le visage reste dégagé
let hairS=null,hairCap=null;const hs=st==='monstre'?'monstre':c.hs,HH=hair(c),strandy=!['monstre','rase','chauve','iroquoise'].includes(hs)&&HH.hl>0.15;
if(hs==='monstre'){// Tête de petit monstre : capuche de fourrure épaisse, visage ovale dégagé, couronne de touffes irrégulières sur deux rangs
const g=blob(10.6,9.9,10.2,{lump:0.05,pear:0.05}),gp=g.attributes.position;
for(let i=0;i<gp.count;i++){const x=gp.getX(i)/10.6,y=gp.getY(i)/9.9,z=gp.getZ(i)/10.2;if(z>0.15&&(x/0.63)**2+((y+0.1)/0.56)**2<1)gp.setXYZ(i,gp.getX(i)*0.85,gp.getY(i)*0.85,gp.getZ(i)*0.85);}
g.computeVertexNormals();hairCap=hairS=add(mk(g,FZ({color:fur,map:HAIR,bumpMap:BMP,bumpScale:0.6,roughness:1,side:THREE.DoubleSide})),[0,24.6,0.6]);
const furB=FZ({color:mix(fur,'#ffffff',0.14),map:HAIR,bumpMap:BMP,bumpScale:0.6,roughness:1});
for(let ring=0;ring<2;ring++){const n=ring?18:30,sc=ring?1.3:1;for(let i=0;i<n;i++){const a=(i+R()*0.7)/n*Math.PI*2,rr=1+ring*0.12+(R()-0.5)*0.05,fx=Math.cos(a)*0.63*rr,fy=Math.sin(a)*0.56*rr-0.1,fz=Math.sqrt(Math.max(0.03,1-fx*fx-fy*fy)),sz=(0.8+R()*0.7)*sc;
const t=mk(blob(1.0*sz,1.4*sz,0.75*sz,{lump:0.09,tip:0.4}),R()<0.55?mFur:furB);t.position.set(fx*10.4,24.6+fy*9.7,0.6+fz*(9.9-ring*0.7));
t.quaternion.setFromUnitVectors(Y,V(Math.cos(a)+(R()-0.5)*0.5,Math.sin(a)+(R()-0.5)*0.5,0.45+R()*0.3).normalize());t.rotateY((R()-0.5)*1.4);G.add(t);}}}
// Crâne rasé ou iroquoise : fine calotte collée au crâne
if(hs==='rase'||hs==='iroquoise'||(hs!=='chauve'&&hs!=='monstre'&&!strandy)){hairS=add(mk(blob(9.72,8.92,9.12,{lump:0.004,t0:0.78,t1:1.95,p0:2.52,pl:4.38}),mHair),[0,24.6,0.6]);hairCap=add(mk(blob(9.76,8.96,9.16,{lump:0.004,t0:0,t1:0.86}),mHair),[0,24.6,0.6]);}
if(strandy)hairStrands(HH);
if(hs==='iroquoise'&&!hats)for(let a=0.85;a>=-1.9;a-=0.3){const s=Math.sin(a),p=V(0,Math.cos(a)*8.92,s*9.12),n=V(0,p.y/79.6,p.z/83.2).normalize(),len=4.4-Math.abs(a-0.2)*0.8;
const m=mk(new THREE.ConeGeometry(1.35,len,10),mHair);m.position.set(0,24.6+p.y,0.6+p.z).addScaledVector(n,len*0.35);m.quaternion.setFromUnitVectors(Y,n);G.add(m);}
if(['rase','chauve','iroquoise'].includes(hs)&&!furry)for(const s of[-1,1])add(mk(blob(1.0,2.0,1.4,{lump:0}),mSkin),[s*9.55,23.6,0.6]);

// Cheveux en vraies mèches : chaque mèche part du cuir chevelu, suit le crâne (raie, épi, frange), puis tombe avec la gravité.
// Les mèches se chevauchent : celles qui partent plus haut passent par-dessus. Une sous-couche plus sombre donne de la profondeur entre les mèches.
function hairStrands(H){
const HC=V(0,24.6,0.6),HA=V(9.6,8.8,9.0),q=p=>V((p.x-HC.x)/HA.x,(p.y-HC.y)/HA.y,(p.z-HC.z)/HA.z),fromQ=v=>V(HC.x+v.x*HA.x,HC.y+v.y*HA.y,HC.z+v.z*HA.z);
const enorm=v=>V(v.x/HA.x,v.y/HA.y,v.z/HA.z).normalize(),sm=(a,b,x)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);};
const lerpT=(tab,x)=>{for(let i=1;i<tab.length;i++)if(x<=tab[i][0]){const[a,va]=tab[i-1],[b,vb]=tab[i];return va+(vb-va)*(x-a)/(b-a);}return tab[tab.length-1][1];};
const hl=H.hl,hx=H.hx,soft=hl<1.5||hx==='boucle',hood2=hood,cutY=hood?null:hats?({chapeau:30.0,police:27.6}[c.hw]||27.2):null;
const vol=(hats?0.02:0.03+H.hv*0.17)+(hx==='boucle'?0.08:0);
// Sous-couche : calotte et pourtour, un peu plus sombres ; côtés rasés : mélange avec la peau
const mUnder=FZ({color:shade(c.hc,0.82),map:HAIR,bumpMap:BMP,bumpScale:0.45,roughness:1,side:THREE.DoubleSide}),mSides=H.hd==='rases'?FZ({color:mix(c.hc,c.sk,0.55),map:HAIR,bumpMap:BMP,bumpScale:0.3,roughness:1}):mUnder;
hairCap=add(mk(blob(HA.x*1.02,HA.y*1.02,HA.z*1.02,{lump:0.004,t0:0,t1:0.86}),mUnder),[0,24.6,0.6]);
const under=add(mk(blob(HA.x*1.015,HA.y*1.015,HA.z*1.015,{lump:0.004,t0:0.78,t1:1.95,p0:2.52,pl:4.38}),mSides),[0,24.6,0.6]);
add(mk(blob(HA.x*1.012,HA.y*1.012,HA.z*1.012,{lump:0.004,t0:1.9,t1:2.15,p0:3.8,pl:1.82}),mSides),[0,24.6,0.6]);
// Zone où poussent les cheveux (la même que la sous-couche)
const scalp=u=>{const th=Math.acos(Math.max(-1,Math.min(1,u.y)));let ph=Math.atan2(u.z,-u.x);if(ph<0)ph+=Math.PI*2;return th<0.84||(th<1.93&&(ph>=2.56||ph<=0.58))||(th<2.12&&ph>3.85&&ph<5.57);};
const pos=[],uvs=[],cols=[],idx=[],cBase=col(c.hc).convertSRGBToLinear(),cHi=H.h2?col(H.h2).convertSRGBToLinear():null;
// Mèche : section en amande qui s'enroule vers le crâne, large au départ, pointue au bout (bout net pour une frange droite)
function ribbon(P,w,th,tint,blunt,round){const n=P.length;if(n<3)return;const base=pos.length/3,RS=8,acc=[0];for(let i=1;i<n;i++)acc.push(acc[i-1]+P[i].distanceTo(P[i-1]));const len=acc[n-1]||1;let prevN=V(0,0,1);
for(let i=0;i<n;i++){const T=P[Math.min(i+1,n-1)].clone().sub(P[Math.max(i-1,0)]).normalize(),N0=enorm(q(P[i]));let N=N0.clone().addScaledVector(T,-N0.dot(T));if(N.lengthSq()<1e-4)N=prevN.clone();N.normalize();prevN=N;
const B=V(0,0,0).crossVectors(T,N).normalize(),s=acc[i]/len,root=0.75+0.25*Math.min(1,acc[i]/1.4),prof=root*(blunt?1-Math.pow(s,10)*0.5:soft?Math.max(0.35,1-Math.pow(s,2)*0.62):Math.max(0.12,1-Math.pow(s,3.2)*0.9)),wi=w*prof,ti=th*Math.max(0.45,prof);
for(let k=0;k<RS;k++){const a=k/RS*Math.PI*2,ca=Math.cos(a),sa=Math.sin(a),p=P[i].clone().addScaledVector(B,ca*wi).addScaledVector(N,sa*ti-(round?0:ca*ca*wi*(soft?0.12:0.28)));pos.push(p.x,p.y,p.z);uvs.push(k/RS,acc[i]/3);
const sh=(0.7+0.3*Math.min(1,acc[i]/2.5))*(sa<0?0.86:1);cols.push(tint[0]*sh,tint[1]*sh,tint[2]*sh);}}
const tipI=pos.length/3,T1=P[n-1].clone().sub(P[n-2]).normalize(),tp=P[n-1].clone().addScaledVector(T1,blunt?0.05:0.15),T0=P[1].clone().sub(P[0]).normalize(),rp=P[0].clone().addScaledVector(T0,-0.2);
pos.push(tp.x,tp.y,tp.z,rp.x,rp.y,rp.z);uvs.push(0.5,len/3,0.5,0);cols.push(tint[0],tint[1],tint[2],tint[0]*0.7,tint[1]*0.7,tint[2]*0.7);
for(let i=0;i<n-1;i++)for(let k=0;k<RS;k++){const a=base+i*RS+k,b=base+i*RS+(k+1)%RS;idx.push(a,b,a+RS,b,b+RS,a+RS);}
for(let k=0;k<RS;k++){idx.push(base+(n-1)*RS+k,tipI,base+(n-1)*RS+(k+1)%RS);idx.push(base+(k+1)%RS,tipI+1,base+k);}}
// Couleur d'une mèche : légères variations, et quelques mèches d'une autre couleur si demandé
const tintOf=()=>{const k=0.9+R()*0.18,cc=(cHi&&R()<0.3)?cHi:cBase;return[cc.r*k,cc.g*k,cc.b*k];};
// Pousse d'une mèche : avance pas à pas, épouse le crâne (avec du volume sur le dessus), tombe sous l'effet de la gravité,
// contourne le corps, s'arrête au bord du visage, à la longueur voulue ou en arrivant à l'attache
function grow(p0,t0,o){const P=[p0.clone()];let p=p0.clone(),t=t0.clone(),s=0;const ds=0.42;
while(s<o.L){const hugNow=o.hug>1||(o.hug&&q(p).y>-0.12);t.y-=o.grav*(hugNow||!o.grav?1:4)*ds;if(o.tie){const d=o.tie.clone().sub(p),dl=d.length();if(dl<1.1)break;t.addScaledVector(d.normalize(),0.45);}if(o.out){t.addScaledVector(enorm(q(p)),o.out);}t.normalize();
const np=p.clone().addScaledVector(t,ds),v=q(np),r=v.length(),top=sm(-0.3,0.8,v.y),K=1.045+o.layer+vol*(o.tie?0.25:1)*top*Math.min(1,s/2.2)+(o.lift||0)*Math.max(0,1-s/5);
if(r<K)np.copy(fromQ(v.multiplyScalar(K/r)));else if(o.hug&&(o.hug>1||v.y>-0.12))np.copy(fromQ(v.multiplyScalar((K+(r-K)*0.25)/r)));
const b=V(np.x/9.9,(np.y-9.2)/10.6,np.z/8.9),rb=b.length();if(rb<1)np.set(b.x/rb*9.9,9.2+b.y/rb*10.6,b.z/rb*8.9);
const f=q(np);if(f.z>0.12&&Math.abs(f.x)<o.faceHalf&&f.y<(o.faceTop+(o.faceSlope||0)*f.x))break;if(np.y<o.yEnd)break;
if(hood2&&q(np).length()>1.095)break;
t=np.clone().sub(p).normalize();p=np;P.push(p.clone());s+=ds;}
// Lissage, puis ondulation ou boucles autour de la trajectoire
for(let k=0;k<2;k++)for(let i=1;i<P.length-1;i++)P[i]=P[i-1].clone().add(P[i+1]).multiplyScalar(0.25).addScaledVector(P[i],0.5);
if((hx==='ondule'||hx==='boucle')&&P.length>4){const Q=P.map(x=>x.clone()),ph=R()*6.28;let a=0;for(let i=1;i<P.length;i++){a+=Q[i].distanceTo(Q[i-1]);const T=Q[Math.min(i+1,Q.length-1)].clone().sub(Q[i-1]).normalize(),N=enorm(q(Q[i])),B=V(0,0,0).crossVectors(T,N).normalize(),gr=Math.min(1,a/2.5);
if(hx==='ondule')P[i].addScaledVector(B,Math.sin(a/5.2*6.28+ph)*0.65*gr);else{const w=a/2.1*6.28+ph;P[i].addScaledVector(B,Math.cos(w)*0.75*gr).addScaledVector(N,(Math.sin(w)+1)*0.6*gr);}}}
if(cutY!==null){const k=P.findIndex(x=>x.y<cutY);return k<0?[]:P.slice(k);}
return P;}
// Longueur des mèches et hauteur où s'arrêtent les pointes
const Lh=lerpT([[0,1.6],[1,5.2],[2,9],[3,14],[4,21],[5,32]],hl)*(hx==='boucle'?0.8:1),yEnd=hl<1.6?-99:lerpT([[1.6,24],[2,21.5],[3,17.4],[4,12.8],[5,5.5]],hl);
const blunt=H.hf==='droite'||hs==='carre',sw=H.hp==='droite'?-1:1,px={gauche:-0.3,milieu:0,droite:0.3,aucune:0}[H.hp];
const TIES={queue:[V(0,25.2,-9.7)],haute:[V(0,31.6,-7.4)],couettes:[V(-9.2,26.2,-2.6),V(9.2,26.2,-2.6)],chignon:[V(0,31.2,-6.6)],tresse:[V(-8.6,22.6,1.2)],demi:[V(0,28.6,-9.3)]}[H.ht]||null;
const fringeZone=u=>u.z>0.42&&u.y>0.38&&Math.abs(u.x)<0.62;
const N=hx==='dreads'?150:hx==='pique'?190:hx==='boucle'?420:hl<1.5?400:260,wid=hx==='dreads'?0.62:hx==='boucle'?0.8:hx==='pique'?1.45:hl<1.5?1.2:1.85,thk=hx==='dreads'||hx==='boucle'?wid:0.42;
if(hx==='crepu'){// Afro ou cheveux crépus : volume rond fait de petites bouclettes serrées, sans cacher le visage
const E=(hats?0.25:1)*(0.6+hl*0.55)*(0.55+H.hv*0.6),cy=25.4,R0=V(10.0+E,9.2+E*0.9,9.6+E);
const mCurl=FZ({color:c.hc,map:HAIR,bumpMap:BMP,bumpScale:0.6,roughness:1}),mCurl2=FZ({color:shade(c.hc,0.85),map:HAIR,bumpMap:BMP,bumpScale:0.6,roughness:1});
hairS=add(mk(blob(R0.x-0.9,R0.y-0.9,R0.z-0.9,{lump:0.06,t0:0,t1:2.0,p0:2.45,pl:4.52}),mCurl2),[0,cy,0.2]);add(mk(blob(R0.x-0.9,R0.y-0.9,R0.z-0.9,{lump:0.06,t0:0,t1:0.9}),mCurl2),[0,cy,0.2]);
for(let i=0;i<340;i++){const t=R()*1.98,p2=t>0.9?2.5+R()*4.4:R()*Math.PI*2,pt=V(-Math.cos(p2)*Math.sin(t)*R0.x,cy+Math.cos(t)*R0.y,0.2+Math.sin(p2)*Math.sin(t)*R0.z);if(cutY!==null&&pt.y>cutY-0.5)continue;
const sz=0.8+R()*0.45;add(mk(blob(sz,sz,sz,{lump:0.05}),R()<0.6?mCurl:mCurl2),[pt.x,pt.y,pt.z]);}return;}
// Racines réparties régulièrement sur le cuir chevelu, avec un peu de hasard
const roots=[];for(let i=0;i<N;i++){const y=1-(i+0.5)/N*2,rr=Math.sqrt(1-y*y),a=i*2.39996+(R()-0.5)*0.35,u=V(Math.cos(a)*rr,y,Math.sin(a)*rr);if(scalp(u))roots.push(u);}
const isTied=u=>TIES&&(H.ht!=='demi'||u.y>0.3);
PART='head';
for(const u of roots){const P0=fromQ(u.clone().multiplyScalar(1.02)),n=enorm(u),layer=0.012+0.05*(u.y+1)/2+R()*0.012,side=u.y<0.25&&Math.abs(u.z)<0.75;
if(H.hd==='rases'&&u.y<0.28&&!fringeZone(u))continue;
const o={L:Lh*(0.88+R()*0.22),grav:0.07,hug:hl<1.8?2:1,layer,faceHalf:0.68,faceTop:0.46,yEnd:yEnd+(blunt?0.2:1.2)*(R()-0.5)};let d,bl=false;
if(hx==='pique'){const up=sm(0.0,0.6,u.y);d=n.clone().multiplyScalar(0.6).add(V(0,0.9*up,-0.5));Object.assign(o,{L:(1.2+hl*1.6)*(0.5+0.5*up)+R()*0.6,grav:0,hug:up>0.3?0:2,out:0.08*up});if(up<0.3)o.L=Math.max(o.L,2.8);}
else if(hx==='dreads'){d=V(u.x*0.4,-1,u.z*0.4);Object.assign(o,{grav:0.2,faceHalf:0.76,faceTop:0.55});}
else if(isTied(u)){const tie=TIES.length>1?TIES[u.x<0?0:1]:TIES[0];d=tie.clone().sub(P0);Object.assign(o,{tie,L:40,grav:0.0,hug:2});}
else if(fringeZone(u)&&H.hf!=='aucune'){const f=H.hf;o.L=Math.min(o.L,f==='courte'?4.6:f==='arriere'?7:11);bl=f==='droite';
d={courte:V(sw*0.15,-1,0.45),droite:V(0,-1,0.55),balayee:V(sw*1.15,-0.8,0.35),rideau:V((u.x>=0?1:-1)*1.1,-0.9,0.3),longue:V(sw*0.1,-1,0.45),arriere:V(0,0.4,-1)}[f];
o.faceTop={courte:0.42,droite:0.2,balayee:0.3,rideau:0.62,longue:0.04,arriere:0.6}[f];if(f==='balayee')o.faceSlope=-0.28*sw;if(f==='rideau')o.faceHalf=0.58;if(f==='arriere'){o.lift=0.12+H.hv*0.15;o.grav=0.01;}if(f==='courte'||f==='droite')o.L=Math.max(o.L,f==='droite'?9:4.6);}
else if(H.hp!=='aucune'){// La raie va du front au sommet du crâne ; derrière, les cheveux retombent depuis l'épi
const topW=sm(0.05,0.7,u.y)*sm(-0.5,0.05,u.z),sd=Math.sign(u.x-px)||1;d=V(sd*topW*1.2,-0.3-(1-topW)*1.2,(fringeZone(u)?-0.6:-0.1)*topW-(1-topW)*0.5*Math.max(0,-u.z));}
else if(H.hf==='aucune'||H.hf==='arriere')d=u.clone().sub(V(0,0.55,0.85)).add(V(0,-0.25,0));
else d=u.clone().sub(V(0,0.8,-0.6)).add(V(0,-0.25,0));
if(side&&!TIES&&hx!=='pique')o.grav=0.12;
if(hl<1.6&&u.z>-0.2&&!TIES)o.yEnd=Math.max(o.yEnd,22.2);
if(H.hd==='courts'&&u.y<0.28&&!fringeZone(u)){o.L=Math.min(o.L,2.4);o.hug=2;}
if(hood2&&!fringeZone(u))continue;if(hood2)o.layer=0.004;
const t0=d.clone().addScaledVector(n,-d.dot(n));if(t0.lengthSq()<1e-6)t0.set(0,-1,0);t0.normalize();
const P=grow(P0,t0,o);ribbon(P,wid*(0.85+R()*0.3)*(fringeZone(u)?1.2:1)*(u.y>0.6?1.15:1),thk,tintOf(),bl||blunt&&!fringeZone(u),hx==='dreads'||hx==='boucle');}
// Attaches : élastique, puis queue, couettes, chignon ou tresse
if(TIES&&!hood2)for(const tie of TIES){const n=enorm(q(tie)),ring=mk(new THREE.TorusGeometry(1.15,0.45,10,24),mAcc);ring.position.copy(tie).addScaledVector(n,0.3);ring.lookAt(tie.clone().addScaledVector(n,3));add(ring);
if(H.ht==='chignon'){for(let j=0;j<7;j++){const P=[],rad=2.9-j*0.32,ax=n.clone(),u1=V(0,0,0).crossVectors(ax,V(1,0,0)).normalize(),u2=V(0,0,0).crossVectors(ax,u1),c0=tie.clone().addScaledVector(ax,1.2+j*0.42),a0=R()*6.28;
for(let a=0;a<Math.PI*2.3;a+=0.3)P.push(c0.clone().addScaledVector(u1,Math.cos(a+a0)*rad).addScaledVector(u2,Math.sin(a+a0)*rad));ribbon(P,1.25,0.6,tintOf(),true,false);}continue;}
if(H.ht==='tresse'){const L=Math.max(5,(hl-1.2)*4.2),steps=Math.round(L/1.25);for(let i=0;i<steps;i++){const k=i%2?1:-1,sz=1.35-i*0.03;add(mk(blob(sz,1.0,1.05,{lump:0.02}),mHair),[-7.0+i*0.15+k*0.35,21.4-i*1.25,4.8+i*0.12],[0,0,k*0.5]);}
const yb=21.4-steps*1.25;add(mk(blob(0.8,0.6,0.8,{lump:0}),mAcc),[-7.0+steps*0.15,yb+0.6,4.8+steps*0.12]);add(mk(blob(0.9,1.5,0.8,{lump:0.03,tip:0.8}),mHair),[-7.0+steps*0.15,yb-0.9,4.9+steps*0.12]);continue;}
const L=Math.max(4,(hl-(H.ht==='demi'?0.5:1))*5.2)*(H.ht==='couettes'?0.85:1);
for(let j=0;j<18;j++){const a=j/18*6.28+R()*0.3,off=V(Math.cos(a),Math.sin(a),0).multiplyScalar(0.5+R()*0.5),p0=tie.clone().addScaledVector(n,0.8).add(off),t0=n.clone().multiplyScalar(H.ht==='couettes'?0.5:0.8).add(V(0,H.ht==='couettes'?-0.9:-0.4,0)).add(off).normalize();
const P=grow(p0,t0,{L:L*(0.85+R()*0.25),grav:H.ht==='couettes'?0.3:0.12,hug:0,layer:0.3,faceHalf:0,faceTop:-9,yEnd:-99});ribbon(P,1.5,0.55,tintOf(),false,false);}}
const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));geo.setAttribute('color',new THREE.Float32BufferAttribute(cols,3));geo.setIndex(idx);geo.computeVertexNormals();
const mStr=FZ({color:0xffffff,vertexColors:true,map:HAIR,bumpMap:BMP,bumpScale:0.4,roughness:1,side:THREE.DoubleSide});
hairS=add(mk(geo,mStr));PART=null;
if(!hairS.geometry.index.count)hairS=under;}

// Couture du dessus de la tête, visible quand la tête est en fourrure ou sans cheveux
if((animal||['rase','chauve'].includes(hs))&&!hats){const pts=[];for(let a=0.55;a>=-1.9;a-=0.12)pts.push([V(0,24.6+Math.cos(a)*40,0.6+Math.sin(a)*40),V(0,-Math.cos(a),-Math.sin(a))]);seam(onSurf([hairCap,head].filter(Boolean),pts,0.05),shade(animal?fur:skinC,0.55));}

// Visage et expression
const blushes=[],browTilt={sourire:-0.1,content:-0.1,neutre:0,serieux:0.32}[c.ex],kawaii=(c.ey!=='realiste'||st==='monstre')&&st!=='avatar';
const[bc2,bg4]=cv(128),bgr=bg4.createRadialGradient(64,64,4,64,64,62),bcol=hex(mix(skinC,'#f0607a',0.62));bgr.addColorStop(0,bcol+'d0');bgr.addColorStop(1,bcol+'00');bg4.fillStyle=bgr;bg4.fillRect(0,0,128,128);
const mBlushSoft=SM({map:own(new THREE.CanvasTexture(bc2)),transparent:true,depthWrite:false,roughness:1,polygonOffset:true,polygonOffsetFactor:-2});
const mKw=SM({color:mix('#0c0a10',eyeBase,0.22),roughness:0.07,metalness:0.15}),mKwC=SM({color:mix(eyeBase,'#ffffff',0.18),roughness:0.25,transparent:true,opacity:0.92,side:THREE.DoubleSide});
for(const s of[-1,1]){
if(kawaii){const e=new THREE.Group();e.add(mk(blob(1.5,1.75,0.55,{lump:0}),mKw));const cr=new THREE.Mesh(new THREE.RingGeometry(0.5,1.3,36,1,Math.PI*1.12,Math.PI*0.76),mKwC);cr.scale.set(1,1.12,1);cr.position.z=0.56;e.add(cr);
const k1=new THREE.Mesh(new THREE.SphereGeometry(0.5,16,12),mShine);k1.scale.set(1,1.15,0.3);k1.position.set(-0.5,0.62,0.52);e.add(k1);const k2=new THREE.Mesh(new THREE.SphereGeometry(0.22,12,10),mShine);k2.scale.z=0.3;k2.position.set(0.55,-0.55,0.54);e.add(k2);
if(c.cl){const fl=new THREE.Mesh(blob(0.45,0.13,0.12,{lump:0}),mLash);fl.position.set(s*1.5,1.3,0.2);fl.rotation.z=s*0.55;e.add(fl);}
if(st==='monstre'){const lid=mk(blob(1.66,0.62,0.66,{lump:0}),mSkin);lid.position.set(0,1.42,0.06);lid.rotation.z=s*0.12;e.add(lid);}stick(e,[head],s*3.85,23.6,0.3);
if(st!=='monstre'){const br=stick(mk(blob(0.95,0.24,0.2,{lump:0}),mBrow),[head],s*3.9,c.ex==='serieux'?26.0:26.4,0.08);br.rotateZ(s*browTilt);}
stick(new THREE.Mesh(new THREE.CircleGeometry(2.1,32),mBlushSoft),[head],s*6.0,21.5,-0.3);continue;}
if(st==='avatar'){// Avatar : petits yeux ovales noirs et sourcils fins
const e=new THREE.Group();e.add(mk(blob(0.62,0.85,0.25,{lump:0}),SM({color:0x141414,roughness:0.15})));const hl=new THREE.Mesh(new THREE.SphereGeometry(0.17,10,8),mShine);hl.position.set(0.18,0.32,0.22);e.add(hl);stick(e,[head],s*3.0,24.0,0.08);
const br=stick(mk(blob(1.0,0.16,0.12,{lump:0}),mBrow),[head],s*3.1,26.0,0.04);br.rotateZ(s*browTilt);continue;}
const e=new THREE.Group();const ig=new THREE.SphereGeometry(1,48,24,0,Math.PI*2,0,Math.PI/2);ig.rotateX(Math.PI/2);ig.scale(1.4,1.62,0.85);e.add(mk(ig,mIris));
const h1=new THREE.Mesh(new THREE.SphereGeometry(0.42,16,12),mShine);h1.scale.z=0.4;h1.position.set(0.5,0.62,0.66);e.add(h1);
const h2=new THREE.Mesh(new THREE.SphereGeometry(0.2,12,10),mShine);h2.scale.z=0.4;h2.position.set(-0.45,-0.55,0.68);e.add(h2);
const la=new THREE.Mesh(new THREE.TorusGeometry(1,0.11,8,28,Math.PI*0.9),mLash);la.scale.set(1.5,1.7,1);la.rotation.z=Math.PI*0.05;la.position.z=0.12;e.add(la);
if(c.cl){const fl=new THREE.Mesh(blob(0.42,0.13,0.12,{lump:0}),mLash);fl.position.set(s*1.55,0.98,0.15);fl.rotation.z=s*0.55;e.add(fl);}
stick(e,[head],s*3.7,24.1,0.35);
const br=stick(mk(blob(1.05,0.27,0.22,{lump:0}),mBrow),[head],s*3.8,c.ex==='serieux'?26.5:26.8,0.08);br.rotateZ(s*browTilt);
blushes.push(stick(mk(blob(1.7,1.05,0.22,{lump:0}),mBlush),[head],s*6.2,21.4,0.1));}
if(c.fr&&st!=='avatar')for(const s of[-1,1])[[4.9,21.9],[5.7,21.4],[4.6,21.1],[5.4,20.8],[6.3,22.0],[6.6,21.2]].forEach(f=>stick(mk(blob(0.17,0.17,0.06,{lump:0}),mFreckle),blushes.concat([head]),s*f[0],f[1],-0.02));
// Nez : museau et truffe pour les animaux, petit nez sinon
let muzzle=null;
if(animal){muzzle=stick(mk(blob(3.2,2.3,1.3,{lump:0}),mFurL),[head],0,21.6,0.7);stick(mk(blob(0.95,0.62,0.5,{lump:0,tip:0.5}),SM({color:0x2a1a14,roughness:0.3})),[muzzle],0,22.5,0.15);
if(st==='chat')for(const s of[-1,1])for(const k of[-1,0,1])add(mk(new THREE.CylinderGeometry(0.06,0.06,3.4,6),mDark),[s*3.7,21.4+k*0.55,9.7],[0,0,Math.PI/2+s*k*0.15]);}
else stick(mk(blob(st==='avatar'?0.45:0.55,st==='avatar'?0.32:0.4,0.35,{lump:0}),mNose),[head],0,22.5,0.15);
const mouthT=muzzle?[muzzle,head]:[head];
if(st==='monstre'){// Grand sourire plein de dents
const mo=new THREE.Group(),cav=new THREE.Mesh(new THREE.CircleGeometry(1,32,Math.PI,Math.PI),mMouth);cav.scale.set(2.3,1.15,1);mo.add(cav);
for(let i=0;i<9;i++){const t=mk(new THREE.ConeGeometry(0.27,0.62,8),mWhite);t.rotation.z=Math.PI;t.position.set(-1.9+i*0.475,-0.3,0.06);mo.add(t);}stick(mo,[head],0,21.3,0.02);}
else if(c.ex==='sourire'){const mo=new THREE.Group();mo.add(new THREE.Mesh(new THREE.CircleGeometry(1.0,28,Math.PI,Math.PI),mMouth));const tg=new THREE.Mesh(blob(0.55,0.3,0.08,{lump:0}),mTongue);tg.position.set(0,-0.62,0.04);mo.add(tg);
const lip=new THREE.Mesh(new THREE.TorusGeometry(1.0,0.07,6,28,Math.PI),mMouth);lip.rotation.z=Math.PI;mo.add(lip);stick(mo,mouthT,0,21.15-(muzzle?0.5:0),0.03);}
const my=muzzle?-0.5:0,human=st!=='monstre';
if(human&&c.ex==='content'){const mo=new THREE.Group(),arc=new THREE.Mesh(new THREE.TorusGeometry(0.85,0.13,8,28,Math.PI*0.8),mMouth);arc.rotation.z=Math.PI*1.1;mo.add(arc);stick(mo,mouthT,0,21.6+my,-0.02);}
if(human&&c.ex==='neutre')stick(mk(blob(0.75,0.13,0.1,{lump:0}),mMouth),mouthT,0,21.0+my,-0.02);
if(human&&c.ex==='serieux'){const mo=new THREE.Group(),arc=new THREE.Mesh(new THREE.TorusGeometry(0.7,0.12,8,24,Math.PI*0.7),mMouth);arc.rotation.z=Math.PI*0.15;mo.add(arc);stick(mo,mouthT,0,20.6+my,-0.02);}
// Barbe : coque autour du bas du visage ; un masque de transparence trace un bord net qui remonte vers les oreilles et dégage la bouche
const BT0=1.5,BT1=2.8,BP0=0.1,BPL=2.94;
function beardMat(color,hairy){const W=256,H=128,[bc,bg3]=cv(W,H),img=bg3.createImageData(W,H);
for(let j=0;j<H;j++){const th=BT0+(j+0.5)/H*(BT1-BT0),st=Math.sin(th),y=Math.cos(th)*8.8;for(let i=0;i<W;i++){const ph=BP0+(i+0.5)/W*BPL,x=-Math.cos(ph)*st*9.6,z=Math.sin(ph)*st*9.0,k=(j*W+i)*4;
const on=!(y>-2.6+0.3*Math.max(0,Math.abs(x)-1.6)||(Math.abs(x)<1.3&&y>-4.35&&y<-2.75&&z>0));img.data[k]=img.data[k+1]=img.data[k+2]=on?255:0;img.data[k+3]=255;}}
// Pas de texture de tissu ici : three.js appliquerait sa répétition au masque aussi, et le masque serait lu en mosaïque
bg3.putImageData(img,0,0);return FZ({color,alphaMap:own(new THREE.CanvasTexture(bc)),alphaTest:0.5,roughness:1,side:THREE.DoubleSide});}
// Même forme de poire que la tête, sinon le bas de la barbe passe à l'intérieur du visage
const beard=(off,lp,mat)=>{const m=add(mk(blob(9.6+off,8.8+off,9.0+off,{lump:lp,pear:0.05,t0:BT0,t1:BT1,p0:BP0,pl:BPL}),mat),[0,24.6,0.6]);m.castShadow=false;return m;};
if(c.bd==='barbe3j')beard(0.16,0,beardMat(mix(c.sk,c.hc,0.5),false));
if(c.bd==='barbe'||c.bd==='longue')beard(0.3,0.02,beardMat(c.hc,true));
if(c.bd==='longue'){PART='head';add(mk(blob(4.6,4.4,3.0,{lump:0.03,tip:0.55}),mHair),[0,17.0,6.4]);PART=null;}
if(['barbe','longue','moustache'].includes(c.bd))for(const s of[-1,1]){const m=stick(mk(blob(1.25,0.42,0.35,{lump:0}),mHair),[head],s*1.05,21.75,0.05);m.rotateZ(-s*0.18);}
if(c.bd==='bouc')stick(mk(blob(1.1,1.0,0.5,{lump:0.03,tip:0.5}),mHair),[head],0,19.5,0.1);
if(has('a')){// Bandana : motif de petites fleurs blanches, pointe sous le menton
const[bc,bg2]=cv(256);bg2.fillStyle=hex(c.ac);bg2.fillRect(0,0,256,256);bg2.fillStyle='rgba(255,255,255,0.85)';bg2.strokeStyle='rgba(255,255,255,0.85)';bg2.lineWidth=2;
for(let y=12;y<256;y+=32)for(let x=(y/32)%2?28:12;x<256;x+=32){bg2.beginPath();bg2.arc(x,y,3.2,0,7);bg2.fill();for(let k=0;k<4;k++){bg2.beginPath();bg2.arc(x+Math.cos(k*1.57)*7,y+Math.sin(k*1.57)*7,2,0,7);bg2.stroke();}}
const bt2=own(new THREE.CanvasTexture(bc));bt2.wrapS=bt2.wrapT=THREE.RepeatWrapping;bt2.repeat.set(3,1.2);const mBd=FZ({map:bt2,roughness:0.85,side:THREE.DoubleSide});
add(mk(blob(9.8,9.0,9.25,{lump:0.01,t0:1.84,t1:2.62,p0:0.42,pl:2.3}),mBd),[0,24.6,0.6]);PART='head';add(mk(blob(2.8,2.4,0.6,{lump:0,tip:0.95}),mBd),[0,17.4,7.4],[0.45,0,0]);PART=null;}
if(has('o'))for(const s of[-1,1])add(mk(new THREE.TorusGeometry(0.5,0.13,8,20),mGold),[s*9.9,21.4,1.2],[0,Math.PI/2,0]);

// Couvre-chef
const tops=[];
if(hood){// Capuche relevée : dessus fermé, ouverture devant le visage, bord roulé
const mHd=c.hm==='uni'?FZ({color:c.hwc,map:FAB,bumpMap:BMP,bumpScale:0.15,roughness:0.9,side:THREE.DoubleSide}):clothMat(c.hwc,false,'torse',c.hm),RX=10.6,RY=9.85,RZ=10.15,T0=0.84,T1=2.55,P0=Math.PI/2+0.78,PLn=2*Math.PI-1.56,CY=24.8,CZ=0.45;
tops.push(add(mk(blob(RX,RY,RZ,{lump:0.012,t0:0,t1:T0+0.04}),mHd),[0,CY,CZ]));
tops.push(add(mk(blob(RX-0.02,RY-0.02,RZ-0.02,{lump:0.012,t0:T0,t1:T1,p0:P0,pl:PLn}),mHd),[0,CY,CZ]));
const sp=(t,p)=>V(-Math.cos(p)*Math.sin(t)*RX,CY+Math.cos(t)*RY,CZ+Math.sin(p)*Math.sin(t)*RZ),edge=[];
for(let t=T1;t>T0;t-=0.12)edge.push(sp(t,P0));for(let p=P0;p>P0+PLn-2*Math.PI;p-=0.12)edge.push(sp(T0,p));for(let t=T0;t<=T1+0.001;t+=0.12)edge.push(sp(t,P0+PLn));
tube(edge,0.4,FZ({color:shade(c.hwc,0.9),map:FAB,roughness:0.9}));
if(c.tp!=='sweat')for(const s of[-1,1])stick(mk(blob(0.22,1.8,0.22,{lump:0}),SM({color:0xe8e8e8,roughness:0.7})),[shirt],s*2.2,14.6,-0.05);}
if(c.hw==='pompier'){const mH=FZ({color:c.hwc,map:FAB,bumpMap:BMP,bumpScale:0.12,roughness:0.75,side:THREE.DoubleSide});
const dome=add(mk(blob(10.6,8.0,10.0,{lump:0,t0:0,t1:1.5}),mH),[0,27,-0.4]);tops.push(dome);
const bg=new THREE.CylinderGeometry(1,1,1,72,1);const bp=bg.attributes.position;for(let i=0;i<bp.count;i++){const x=bp.getX(i)*12.2,z=bp.getZ(i)*13.0-1.4;let y=bp.getY(i)*0.45;if(z<-3)y-=(-3-z)*0.15;bp.setXYZ(i,x,y,z);}bg.computeVertexNormals();add(mk(bg,mH),[0,27.3,0]);
[[0,0.75,-80,15],[-4.6,0.45,-80,55],[4.6,0.45,-80,55]].forEach(rb=>{const kx=Math.sqrt(1-(rb[0]/10.6)**2);const pts=[];for(let a=rb[2];a<=rb[3];a+=5){const t=a*Math.PI/180;pts.push(V(rb[0],27+8*kx*Math.cos(t),-0.4+10*kx*Math.sin(t)));}tube(pts,rb[1],mH);});
add(mk(conform([dome],V(0,32.2,0),X,Y,4.8,4.8,16,FWD,0.14),decal(shieldTex(c.hwt))));
if(c.hwt){add(mk(conform([dome],V(0,30.6,-1.2),V(0,0,1),Y,2.6,2.6,10,X,0.1),decal(discTex(c.hwt))));add(mk(conform([dome],V(0,30.6,-1.2),V(0,0,-1),Y,2.6,2.6,10,NX,0.1),decal(discTex(c.hwt))));}
const hc=V(0,24.6,0.6),Dc=V(0,-0.8,0.6).normalize(),cs=[V(-10.6,27.0,0.6)],tg2=[hairS,head].filter(Boolean);
for(let a=-90;a<=90;a+=10){const t=a*Math.PI/180;const d=X.clone().multiplyScalar(Math.sin(t)).addScaledVector(Dc,Math.cos(t)).normalize();const h=hitAt(tg2,hc.clone().addScaledVector(d,40),d.clone().negate());if(h)cs.push(h.p.addScaledVector(d,0.25));}
cs.push(V(10.6,27.0,0.6));tube(cs,0.18,mDark);}
if(c.hw==='casquette'||c.hw==='inverse'){const rev=c.hw==='inverse',mC=c.hm==='uni'?FZ({color:c.hwc,map:FAB,bumpMap:BMP,bumpScale:0.12,roughness:0.85,side:THREE.DoubleSide}):clothMat(c.hwc,false,'torse',c.hm),mSeam=FZ({color:shade(c.hwc,0.8),map:FAB,roughness:0.85});
const crown=add(mk(blob(10.4,8.0,10.0,{lump:0,t0:0,t1:1.5}),mC),[0,26.8,0.4]);tops.push(crown);
add(mk(visor(9.2,10.5,3.0,rev?0.05:0.12),FZ({color:shade(c.hwc,0.9),map:FAB,roughness:0.8})),[0,27.4,0.4],[0,rev?Math.PI:0,0]);
add(mk(blob(0.9,0.5,0.9,{lump:0}),mAcc),[0,34.75,0.4]);
[-3.8,0,3.8].forEach(x=>{const kx=Math.sqrt(1-(x/10.4)**2),pts=[];for(let a=-80;a<=80;a+=8){const t=a*Math.PI/180;pts.push(V(x,26.8+8.08*kx*Math.cos(t),0.4+10.08*kx*Math.sin(t)));}tube(pts,0.16,mSeam);});
if(rev)add(mk(blob(2.4,1.0,0.5,{lump:0}),mDark),[0,28.6,10.0]);
else if(c.hwt)add(mk(conform([crown],V(0,30.7,0),X,Y,6.2,2.4,12,FWD,0.12),decal(textTex(c.hwt,ink(c.hwc)))));}
if(c.hw==='bonnet'){const mB=FZ({color:c.hwc,map:KNIT,bumpMap:KNIT,bumpScale:0.35,roughness:1,side:THREE.DoubleSide});
tops.push(add(mk(blob(10.7,9.0,10.3,{lump:0.012,t0:0,t1:1.5}),mB),[0,27.3,0.4]));
const cuff=add(mk(new THREE.TorusGeometry(10.35,1.35,14,80),FZ({color:shade(c.hwc,0.9),map:KNIT,bumpMap:KNIT,bumpScale:0.35,roughness:1})),[0,28.3,0.4],[Math.PI/2,0,0]);cuff.scale.set(1,0.965,1);cuff.updateMatrixWorld(true);
add(mk(blob(2.7,2.6,2.7,{lump:0.09}),FZ({color:c.ac,map:HAIR,bumpMap:BMP,bumpScale:0.5,roughness:1})),[0,37.0,0.4]);
if(c.hwt)add(mk(conform([cuff],V(0,28.3,0),X,Y,5.2,1.7,12,FWD,0.08),decal(textTex(c.hwt,ink(c.hwc)))));}
if(c.hw==='chapeau'){const mHt=c.hm==='uni'?FZ({color:c.hwc,map:FAB,bumpMap:BMP,bumpScale:0.1,roughness:0.8,side:THREE.DoubleSide}):clothMat(c.hwc,false,'torse',c.hm);
tops.push(add(mk(blob(8.6,4.8,8.2,{lump:0,sq:0.7}),mHt),[0,33.4,0.3]));
const bg=new THREE.CylinderGeometry(1,1,1,72,1),bp=bg.attributes.position;for(let i=0;i<bp.count;i++){const x=bp.getX(i)*13.5,z=bp.getZ(i)*13.0;bp.setXYZ(i,x,bp.getY(i)*0.5+(x/13.5)**2*1.6,z);}bg.computeVertexNormals();add(mk(bg,mHt),[0,30.3,0.3]);
const bd2=add(mk(new THREE.TorusGeometry(8.35,0.75,10,64),FZ({color:c.ac,map:FAB,roughness:0.8})),[0,30.9,0.3],[Math.PI/2,0,0]);bd2.scale.set(1,0.96,1);}
if(c.hw==='bandeau'){const hb=add(mk(new THREE.TorusGeometry(8.95,0.85,12,72),FZ({color:c.hwc,map:FAB,bumpMap:BMP,bumpScale:0.15,roughness:0.9})),[0,29.2,0.5],[Math.PI/2,0,0]);hb.scale.set(1,0.94,1);hb.updateMatrixWorld(true);tops.push(hb);}
if(c.hw==='police'){const mTop=FZ({color:c.hwc,map:FAB,bumpMap:BMP,bumpScale:0.1,roughness:0.75});
const band=add(mk(new THREE.CylinderGeometry(10.15,9.95,3.4,64,1,true),SM({color:0x141418,roughness:0.5,side:THREE.DoubleSide})),[0,29.3,0.5]);band.scale.z=0.97;band.updateMatrixWorld(true);
add(mk(blob(10.25,1.6,10.0,{lump:0}),mTop),[0,31.0,0.5]);tops.push(band,add(mk(blob(11.8,2.6,11.4,{lump:0,sq:0.85}),mTop),[0,32.2,0.1]));
add(mk(visor(8.4,7.0,3.0,0.18),SM({color:0x0d0d10,roughness:0.15,metalness:0.2})),[0,27.9,0.5]);
stick(mk(blob(1.3,1.5,0.35,{lump:0,sq:0.6}),mGold),[band],0,29.6,0.1);}

// Lunettes
if(c.gl==='masque'){const mF=SM({color:c.glc,roughness:0.45}),mL=SM({color:0xe8f25a,emissive:0x6b7a00,emissiveIntensity:0.12,transparent:true,opacity:0.28,roughness:0.05,metalness:0.1,depthWrite:false});
for(const s of[-1,1]){const fr=mk(new THREE.TorusGeometry(2.0,0.4,12,40),mF);stick(fr,[head],s*3.7,24.1,-0.3);fr.scale.set(1.18,0.95,1);stick(mk(blob(2.25,1.85,0.45,{lump:0}),mL),[head],s*3.7,24.1,-0.55);}
stick(mk(blob(1.0,0.45,0.4,{lump:0}),mF),[head],0,24.4,-0.45);
const sg=new THREE.Group();const sm=mk(new THREE.TorusGeometry(10.45,0.42,10,80,Math.PI+1.6),mDark);sm.rotation.x=-Math.PI/2;sm.scale.set(1,0.94,1);sg.add(sm);sg.position.set(0,24.1,0.6);sg.rotation.y=-0.8;G.add(sg);}
if(c.gl==='lunettes'||c.gl==='soleil'){const mF=SM({color:c.glc,roughness:0.35,metalness:0.25}),sun=c.gl==='soleil';
const mL=sun?SM({color:c.lc,transparent:true,opacity:0.86,roughness:0.08,metalness:0.3}):SM({color:0xe8f4ff,transparent:true,opacity:0.14,roughness:0.05,depthWrite:false});
const k=sun?0.86:1;for(const s of[-1,1]){const fr=mk(new THREE.TorusGeometry(2.05*k,0.24,10,40),mF);stick(fr,[head],s*3.7,24.1,-0.25);fr.scale.set(1.12,sun?0.85:0.98,1);stick(mk(blob(2.2*k,(sun?1.6:1.95),0.3,{lump:0}),mL),[head],s*3.7,24.1,-0.4);}
stick(mk(blob(0.9,0.22,0.22,{lump:0}),mF),[head],0,24.5,-0.35);}
if(c.gl==='aviateur'){// Aviateurs : verres en goutte, fine monture métal, double pont
const mF=SM({color:c.glc,roughness:0.25,metalness:0.7}),mL=SM({color:c.lc,transparent:true,opacity:0.84,roughness:0.06,metalness:0.35});
for(const s of[-1,1]){const g=new THREE.Group(),rim=mk(blob(2.55,2.15,0.16,{lump:0,tip:0.32}),mF);rim.position.z=-0.06;g.add(rim);g.add(mk(blob(2.35,1.95,0.24,{lump:0,tip:0.32}),mL));stick(g,[head],s*3.75,24.0,-0.3);g.rotateZ(s*0.08);}
for(const y of[25.35,24.75])stick(mk(new THREE.CylinderGeometry(0.09,0.09,2.4,8),mF),[head],0,y,-0.32).rotateZ(Math.PI/2);}
if(c.gl==='tete'){// Lunettes de soleil relevées sur la tête (ou sur la capuche)
const mF=SM({color:c.glc,roughness:0.35,metalness:0.25}),mL=SM({color:c.lc,roughness:0.08,metalness:0.4}),tg=tops.concat([hairCap,hairS,head].filter(Boolean));
for(const s of[-1,1]){const g=new THREE.Group(),fr=mk(new THREE.TorusGeometry(1.5,0.2,10,36),mF);fr.scale.set(1.2,0.85,1);g.add(fr);g.add(mk(blob(1.65,1.2,0.24,{lump:0}),mL));stick(g,tg,s*3.0,32.0,-0.12);}
stick(mk(blob(0.75,0.18,0.18,{lump:0}),mF),tg,0,32.2,-0.08);}

// Oreilles d'animal ou de petit monstre, posées sur ce qui est le plus à l'extérieur (cheveux, capuche, chapeau)
if(furry){const tg=tops.concat([hairCap,hairS,head].filter(Boolean)),mIn=FZ({color:st==='monstre'?mix(fur,'#f2a6b0',0.6):mix(fur,'#ffffff',0.55),map:FAB,roughness:1});
const E={ours:[[0.62,0.78,0],[2.3,2.3,1.1],[1.35,1.35,0.5],0],lapin:[[0.3,0.95,0],[1.4,4.6,0.7],[0.8,3.6,0.3],0.12],chat:[[0.55,0.83,0],[2.0,3.4,2.0],[1.2,2.3,1.2],0],monstre:[[0.34,0.94,-0.05],[1.6,6.0,0.7],[0.95,4.7,0.3],0.16]}[st];
const shape=sz=>{if(st==='chat'){const q=new THREE.ConeGeometry(1,2,24);q.scale(sz[0],sz[1]/2,sz[2]);return q;}return blob(sz[0],sz[1],sz[2],{lump:0.02,pear:st==='monstre'?0.35:0});};
for(const s of[-1,1]){const d=V(s*E[0][0],E[0][1],E[0][2]).normalize(),ctr=V(0,24.6,0.6);ray.set(ctr.clone().addScaledVector(d,80),d.clone().negate());const h=ray.intersectObjects(tg,false)[0];
let n=d.clone();const p=h?h.point.clone():ctr.clone().addScaledVector(d,9.5);if(h){NM.getNormalMatrix(h.object.matrixWorld);n=h.face.normal.clone().applyMatrix3(NM).normalize();if(n.dot(d)<0)n.negate();}
const g=new THREE.Group();g.add(mk(shape(E[1]),mFur));const inn=mk(shape(E[2]),mIn);inn.position.set(0,-E[1][1]*0.05,E[1][2]*0.55);g.add(inn);
g.position.copy(p).addScaledVector(n,E[1][1]*0.55);g.quaternion.setFromUnitVectors(Y,n).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(0,0,-s*E[3])));G.add(g);g.updateMatrixWorld(true);}}

// Queues des animaux
if(st==='ours')add(mk(blob(1.7,1.6,1.5,{lump:0.06}),mFur),[0,6.6,-7.6]);
if(st==='lapin')add(mk(blob(2.2,2.1,2.1,{lump:0.12}),mFurL),[0,6.6,-7.9]);
if(st==='chat')tube([V(0,5.5,-7.2),V(1.8,4.4,-10.2),V(4.2,6.6,-11.8),V(5.0,10.5,-11.0),V(4.2,13.2,-9.8)],0.85,mFur);

// Accessoires
if(has('r')){const rad=new THREE.Group();rad.add(mk(blob(1.25,1.8,0.7,{lump:0}),mLime));const an=mk(new THREE.CylinderGeometry(0.15,0.15,1.6,8),mDark);an.position.set(0.5,2.4,0);rad.add(an);
const kn=mk(new THREE.CylinderGeometry(0.28,0.28,0.5,12),mDark);kn.position.set(-0.5,1.95,0);rad.add(kn);const scr=mk(new THREE.BoxGeometry(1.4,0.9,0.12),mScreen);scr.position.set(0,0.5,0.68);rad.add(scr);stick(rad,[outer],-5.4,14.6,0.3);}
if(has('b')){const b=new THREE.Group();const sh=mk(new THREE.CylinderGeometry(1.15,1.15,0.25,6),mGold);sh.rotation.x=Math.PI/2;b.add(sh);const ct=mk(new THREE.CylinderGeometry(0.5,0.5,0.3,16),SM({color:0x1b2a5a,roughness:0.5}));ct.rotation.x=Math.PI/2;ct.position.z=0.08;b.add(ct);stick(b,[outer],4.4,15.4,-0.05);}
if(has('m')){add(mk(blob(1.3,1.9,1.7,{lump:0}),mDark),[-10.1,24.0,0.8]);tube([V(-10.4,23.2,2.0),V(-9.3,21.8,5.2),V(-6.5,20.9,8.0),V(-3.6,20.4,9.3),V(-2.0,20.5,9.5)],0.18,mDark);add(mk(blob(0.55,0.5,0.55,{lump:0.06}),mDark),[-2.0,20.5,9.5]);}
if(has('s')){const[bt,be]=clothTex(shade(c.pc,0.9),true,'manche','uni');own(bt);own(be);add(mk(blob(1.5,2.3,2.4,{lump:0,sq:0.5}),FZ({map:bt,emissive:0xffffff,emissiveMap:be,emissiveIntensity:0.08,roughness:0.85,bumpMap:BMP,bumpScale:0.15})),[9.3,6.8,1.2]);}
if(has('c')){const pts=[];for(let a=0;a<Math.PI*2-0.01;a+=Math.PI/24){const d=V(Math.sin(a),0,Math.cos(a)),y=17.2-2.8*Math.pow(Math.max(0,Math.cos(a)),1.5);pts.push([V(0,y,0).addScaledVector(d,30),d.clone().negate()]);}
tube(onSurf(torso,pts,0.22),0.2,mGold,true);stick(mk(blob(0.65,0.8,0.25,{lump:0}),mGold),torso,0,13.9,-0.05);}
if(has('e')){const mSc=FZ({color:c.ac,map:KNIT,bumpMap:KNIT,bumpScale:0.3,roughness:1});const sc=add(mk(new THREE.TorusGeometry(5.5,1.55,14,48),mSc),[0,16.9,0.4],[Math.PI/2,0,0]);sc.scale.set(1,0.9,1);
stick(mk(blob(1.5,3.4,0.7,{lump:0.01}),mSc),torso,-2.6,13.2,0.2);}
if(has('h')){PART='body';const mHp=SM({color:0x1c1c1e,roughness:0.4});for(const s of[-1,1]){add(mk(new THREE.CylinderGeometry(1.7,1.7,1.1,24),mHp),[s*6.0,17.2,1.6],[0,0,Math.PI/2]);add(mk(new THREE.TorusGeometry(1.45,0.25,8,24),mAcc),[s*6.6,17.2,1.6],[0,Math.PI/2,0]);}
tube([V(-6.0,17.8,0.6),V(-5.3,18.2,-3.8),V(0,18.4,-6.9),V(5.3,18.2,-3.8),V(6.0,17.8,0.6)],0.4,mHp);PART=null;}
if(has('n')){add(mk(conform(torso,V(0.4,12.6,0),V(0.5,0.867,0),V(-0.867,0.5,0),1.0,14.5,24,FWD,0.25),FZ({color:shade(c.ac,0.55),map:FAB,roughness:0.8,side:THREE.DoubleSide})));
stick(mk(blob(2.7,1.5,1.1,{lump:0,sq:0.5}),mAcc),torso,3.2,8.8,-0.2);}
if(has('k')){const mK=FZ({color:c.ac,map:FAB,bumpMap:BMP,bumpScale:0.15,roughness:0.85}),mKs=FZ({color:shade(c.ac,0.6),map:FAB,roughness:0.8});
add(mk(blob(5.4,6.2,2.6,{lump:0.01,sq:0.6}),mK),[0,11.8,-9.2]);add(mk(blob(4.2,2.6,1.4,{lump:0.01,sq:0.6}),mK),[0,9.6,-11.4]);
for(const s of[-1,1]){const pts=[];for(let b=-1.6;b<=1.25;b+=0.15){const d=V(0,Math.cos(b),Math.sin(b));pts.push([V(s*4.3,11.5,0).addScaledVector(d,30),d.clone().negate()]);}tube(onSurf(torso,pts,0.35),0.42,mKs);}}

// Objet dans les mains (étiqueté pour suivre les mains quand la longueur des bras change)
PART='item';const iy=c.po==='coeur'?6.6:0;
if(showIt==='lance'){const mR=FZ({color:0xc8261f,map:FAB,bumpMap:BMP,bumpScale:0.1,roughness:0.6});
add(mk(new THREE.CylinderGeometry(0.7,0.75,5.8,24),mR),[-0.7,7.9,9.5],[0,0,Math.PI/2]);add(mk(blob(0.55,1.25,0.6,{lump:0}),mR),[-2.7,6.7,9.5],[0,0,0.25]);
add(mk(new THREE.TorusGeometry(1.0,0.17,8,20,Math.PI),mDark),[0.4,7.9,9.5]);add(mk(new THREE.TorusGeometry(0.9,0.3,10,24),mSilver),[2.3,7.9,9.5],[0,Math.PI/2,0]);
add(mk(new THREE.CylinderGeometry(1.2,0.95,1.1,28),mGray),[3.1,7.9,9.5],[0,0,-Math.PI/2]);add(mk(new THREE.TorusGeometry(0.72,0.13,8,24),mDark),[3.68,7.9,9.5],[0,Math.PI/2,0]);
tube(POSE.l==='stand'?[V(-3.6,7.9,9.5),V(-4.8,7.0,10.6),V(-6.6,2.6,10.6),V(-7.8,-3.6,9.0),V(-8.6,-8.9,7.0),V(-10.4,-9.0,4.2),V(-11.8,-9.0,1.6)]:[V(-3.6,7.9,9.5),V(-4.8,7.5,10.8),V(-7.0,5.8,12.0),V(-9.4,3.0,11.2),V(-10.6,0.6,8.6),V(-10.2,0.6,5.6),V(-11.6,0.6,3.2)],0.55,mR);}
if(showIt==='coeur'){const mH=FZ({color:0xe0303a,map:FAB,bumpMap:BMP,bumpScale:0.12,roughness:0.8});
for(const s of[-1,1])add(mk(blob(1.9,1.9,1.4,{lump:0.01}),mH),[s*1.2,8.9+iy,10.2]);add(mk(blob(2.5,2.6,1.35,{lump:0.01,tip:0.85}),mH),[0,7.9+iy,10.2]);}
if(showIt==='telephone'){const ph=new THREE.Group();ph.add(mk(blob(1.15,2.0,0.28,{lump:0,sq:0.4}),SM({color:0x16161a,roughness:0.3,metalness:0.3})));
const sc=new THREE.Mesh(new THREE.PlaneGeometry(1.8,3.3),new THREE.MeshBasicMaterial({color:0x6fb6ff}));sc.position.z=0.29;ph.add(sc);add(ph,[0,8.6,10.4],[-0.7,0,0]);}
if(showIt==='cafe'){add(mk(new THREE.CylinderGeometry(1.25,1.0,2.8,24),mWhite),[0,8.8,10.4]);add(mk(new THREE.CylinderGeometry(1.2,1.1,1.1,24),SM({color:0x9b6b43,roughness:0.9})),[0,8.7,10.4]);
add(mk(new THREE.CylinderGeometry(1.35,1.35,0.45,24),SM({color:0x2b1d14,roughness:0.5})),[0,10.4,10.4]);}
if(showIt==='donut'){add(mk(new THREE.TorusGeometry(1.5,0.78,16,32),SM({color:0xd9a25e,roughness:0.8})),[0,8.6,10.3]);const gz=add(mk(new THREE.TorusGeometry(1.5,0.8,16,32),SM({color:0xf28fb8,roughness:0.35})),[0,8.6,10.6]);gz.scale.z=0.55;
const sp=['#ffffff','#5bc0eb','#fde74c','#9bc53d'];for(let i=0;i<14;i++){const a=R()*Math.PI*2,r2=1.0+R()*1.0;add(mk(new THREE.BoxGeometry(0.4,0.12,0.12),SM({color:sp[i%4]})),[Math.cos(a)*r2,8.6+Math.sin(a)*r2,11.05],[0,0,R()*3]);}}
if(showIt==='trousse'){add(mk(blob(2.7,1.9,1.1,{lump:0,sq:0.35}),SM({color:0xd23a3a,roughness:0.6})),[0,8.4,10.6]);const mW=SM({color:0xffffff,roughness:0.5});
add(mk(new THREE.BoxGeometry(1.6,0.5,0.2),mW),[0,8.4,11.7]);add(mk(new THREE.BoxGeometry(0.5,1.6,0.2),mW),[0,8.4,11.7]);add(mk(new THREE.TorusGeometry(0.8,0.18,8,20,Math.PI),mDark),[0,10.2,10.6]);}

PART=null;
// Mascotte : mini-peluche assise sur une épaule ou tenue dans les mains
if(c.ms!=='aucune'){const mM=FZ({color:c.mc,map:HAIR,bumpMap:BMP,bumpScale:0.35,roughness:1}),mMl=FZ({color:mix(c.mc,'#ffffff',0.5),map:FAB,roughness:1}),mE=SM({color:0x111111,roughness:0.15}),M=new THREE.Group();
const part=(geo,mat,p,r)=>{const m=mk(geo,mat);m.position.set(p[0],p[1],p[2]);if(r)m.rotation.set(r[0],r[1],r[2]);M.add(m);return m;};
const mon=c.ms==='monstre';
if(c.ms==='oiseau'){// Oiseau / perroquet : corps en goutte, bec crochu, cercles autour des yeux, ailes et longue queue
const mBk=SM({color:0x2a2a2a,roughness:0.4}),mRing=SM({color:0xf2c418,roughness:0.5});
part(blob(1.35,1.9,1.3,{lump:0.02,tip:0.25}),mM,[0,0.2,0]);part(blob(1.25,1.25,1.2,{lump:0.015}),mM,[0,2.55,0.35]);
part(new THREE.ConeGeometry(0.42,1.2,16),mBk,[0,2.2,1.55],[2.3,0,0]);part(blob(0.35,0.25,0.3,{lump:0}),mRing,[0,2.35,1.35]);
for(const s of[-1,1]){part(new THREE.SphereGeometry(0.17,10,8),mE,[s*0.62,2.75,1.0]);part(new THREE.TorusGeometry(0.24,0.07,8,16),mRing,[s*0.62,2.75,0.97],[0,s*0.6,0]);
part(blob(0.5,1.5,1.05,{lump:0.02,tip:0.4}),mM,[s*1.25,0.4,-0.1],[0.2,0,s*0.18]);part(blob(0.3,0.25,0.45,{lump:0}),mBk,[s*0.5,-1.75,0.5]);}
part(blob(0.5,2.0,0.25,{lump:0.01,tip:0.6}),mM,[0,-1.9,-1.1],[0.55,0,0]);}
else{part(blob(1.6,1.7,1.4,{pear:0.1,lump:0.02}),mM,[0,0,0]);if(!mon)part(blob(1.0,1.1,0.4,{lump:0}),mMl,[0,-0.1,1.15]);
part(blob(1.8,1.6,1.6,{lump:0.015}),mM,[0,2.6,0.1]);
// Petit monstre : visage clair dans la fourrure, sourire plein de dents, longues oreilles
if(mon){part(blob(1.3,1.12,0.5,{lump:0}),SM({color:0xf3d9c4,roughness:0.8}),[0,2.5,1.3]);const mo=part(new THREE.CircleGeometry(1,24,Math.PI,Math.PI),mMouth,[0,2.05,1.78]);mo.scale.set(0.5,0.3,1);
for(let i=0;i<5;i++){const t=part(new THREE.ConeGeometry(0.075,0.17,6),mWhite,[-0.34+i*0.17,1.98,1.8]);t.rotation.z=Math.PI;}}
else part(blob(1.2,0.9,0.5,{lump:0}),mMl,[0,2.3,1.35]);
for(const s of[-1,1]){const eye=part(new THREE.SphereGeometry(mon?0.24:0.2,12,10),mE,[s*(mon?0.5:0.55),mon?2.78:2.75,mon?1.72:1.62]);if(mon)part(new THREE.SphereGeometry(0.07,8,6),mShine,[s*0.5+0.08,2.88,1.94]);
if(mon){part(blob(0.5,1.8,0.3,{lump:0.01}),mM,[s*0.72,4.8,0],[0,0,-s*0.12]);part(blob(0.3,1.35,0.12,{lump:0}),SM({color:0xf2a6b0,roughness:0.9}),[s*0.72,4.8,0.22],[0,0,-s*0.12]);}part(blob(0.45,0.8,0.45,{lump:0.02}),mM,[s*1.55,0.3,0.5],[0.5,0,s*0.5]);part(blob(0.55,0.5,0.75,{lump:0.02}),mM,[s*0.8,-1.35,0.9]);
if(c.ms==='lapin'){part(blob(0.45,1.5,0.28,{lump:0.01}),mM,[s*0.75,4.6,0],[0,0,-s*0.15]);part(blob(0.26,1.1,0.12,{lump:0}),mMl,[s*0.75,4.6,0.2],[0,0,-s*0.15]);}
if(c.ms==='ours')part(blob(0.6,0.55,0.35,{lump:0}),mM,[s*1.25,3.9,0]);
if(c.ms==='chat')part(new THREE.ConeGeometry(0.6,1.2,16),mM,[s*1.0,4.0,0],[0,0,-s*0.3]);
if(c.ms==='chien')part(blob(0.5,1.05,0.28,{lump:0.01}),mM,[s*1.65,2.5,0.1],[0,0,s*0.35]);}
if(!mon)part(new THREE.SphereGeometry(0.18,10,8),mE,[0,2.55,1.8]);}
// Taille réglable : la mascotte garde les pieds au même endroit et s'écarte de la tête quand elle grandit
const ms0=mpE==='mains'?1.0:1.3,msz=ms0*c.mz,grow=msz-ms0,sd=mpE==='droite'?1:mpE==='gauche'?-1:0;
const pos=mpE==='tete'?[0,35.6+grow*1.9,0.5]:sd?[sd*(8.5+grow*1.6),17.0+grow*1.7,2.0]:[0,9.4+grow*1.2,10.9+grow*1.4];
M.position.set(pos[0]+c.mx*5,pos[1]+c.my*5,pos[2]+c.mf*5);M.scale.setScalar(msz);M.rotation.y=(mpE==='droite'?0.2:mpE==='gauche'?0.35:0)+c.mr*Math.PI/180;M.userData.part=mpE==='mains'?'item':'head';G.add(M);}

// Pièces sur mesure (oreilles, cornes, queue…) : collées sur la surface la plus extérieure, ou placées librement autour d'une ancre
const AN={tete:[V(0,24.6,0.6),9.2],corps:[V(0,10.5,0),9.0],mains:[V(0,8.2,10.2),3.0],dos:[V(0,11.5,-8.0),6.0],jambes:[V(0,3.0,5.0),5.0]},DEG=Math.PI/180;
const solid=[];G.updateMatrixWorld(true);G.traverse(o=>{if(o.isMesh&&!(o.material&&o.material.transparent))solid.push(o);});
for(const q of c.pz){const[f,an,x,y,z,sx,sy,sz,rx,ry,rz,colr,glue]=q,[ctr,ar]=AN[an],S=[sx*ar,sy*ar,sz*ar];let geo;
if(f==='sphere')geo=blob(S[0],S[1],S[2],{lump:0.01});else if(f==='goutte')geo=blob(S[0],S[1],S[2],{lump:0,tip:0.9});else if(f==='boite')geo=blob(S[0],S[1],S[2],{lump:0,sq:0.35});
else{geo=f==='cone'?new THREE.ConeGeometry(1,2,24):f==='cylindre'?new THREE.CylinderGeometry(1,1,2,24):new THREE.TorusGeometry(1,0.32,12,36);geo.scale(S[0],S[1],S[2]);}
const m=mk(geo,FZ({color:colr,map:FAB,bumpMap:BMP,bumpScale:0.12,roughness:0.85,side:THREE.DoubleSide})),e=new THREE.Euler(rx*DEG,ry*DEG,rz*DEG);
if(glue){const d=V(x,y,z);if(d.lengthSq()<1e-6)d.set(0,1,0);d.normalize();ray.set(ctr.clone().addScaledVector(d,80),d.clone().negate());const h=ray.intersectObjects(solid,false)[0];
let n=d.clone();const p=h?h.point.clone():ctr.clone().addScaledVector(d,ar);if(h){NM.getNormalMatrix(h.object.matrixWorld);n=h.face.normal.clone().applyMatrix3(NM).normalize();if(n.dot(d)<0)n.negate();}
m.position.copy(p).addScaledVector(n,S[1]*0.55);m.quaternion.setFromUnitVectors(Y,n).multiply(new THREE.Quaternion().setFromEuler(e));}
else{m.position.copy(ctr).addScaledVector(V(x,y,z),ar);m.rotation.copy(e);}
G.add(m);}

// Proportions du style : chaque élément va dans la tête, le corps, les jambes ou les objets tenus, puis chaque zone est déformée
const PR=PROPS[st]||PROPS.classique,TILT={coucou:[0,0,0.12],pensif:[0.12,0,0.16],dab:[0.3,0,-0.4],bravo:[-0.12,0,0],calin:[0,0,-0.06]}[c.po];
if(PR!==PROPS.classique||TILT){const HG=new THREE.Group(),BG=new THREE.Group(),LG=new THREE.Group(),IG=new THREE.Group(),bb=new THREE.Box3(),cc=V(0,0,0),arms=[];
for(const m of[...G.children]){let part=m.userData.part;if(!part){bb.setFromObject(m);bb.getCenter(cc);part=cc.y>17.6?'head':(cc.y<5.6&&cc.z>1.5?'leg':'body');}
if(part==='arm')arms.push(m);(part==='head'?HG:part==='leg'?LG:part==='item'?IG:BG).add(m);}
// Bras : épaisseur et longueur changées depuis l'épaule, mains gardées à leur taille ; les objets tenus suivent les mains
const[th,ln]=PR.a,before=V(0,0,0),after=V(0,0,0);
for(const a of arms){a.updateMatrixWorld(true);before.add(a.localToWorld(V(0,-4.8,0)));a.scale.set(th,ln,th);a.position.add(V(0,5.1*(1-ln),0).applyQuaternion(a.quaternion));
a.children.forEach(ch=>{if(!ch.userData.seam)ch.scale.multiply(V(1/th,1/ln,1/th));});a.updateMatrixWorld(true);after.add(a.localToWorld(V(0,-4.8,0)));}
if(arms.length)IG.position.copy(after.sub(before).multiplyScalar(1/arms.length));BG.add(IG);
const[bx,by,bz]=PR.b,[lx,ly,lz]=PR.l;BG.scale.set(bx,by,bz);LG.scale.set(lx,ly,lz);LG.position.set(0,0,1.5*(1-lz));
const HP=new THREE.Group();HG.scale.setScalar(PR.h);HG.position.set(0,-17*PR.h,-0.6*PR.h);HP.position.set(0,17*by,0.6*bz);if(TILT)HP.rotation.set(TILT[0],TILT[1],TILT[2]);HP.add(HG);G.add(BG,LG,HP);}

G.scale.setScalar(0.75);G.updateMatrixWorld(true);
const box=new THREE.Box3().setFromObject(G),rx=Math.max(-box.min.x,box.max.x),rz=Math.max(-box.min.z,box.max.z);
const fit={c:V(0,(box.min.y+box.max.y)/2,0),r:Math.max(box.max.y-box.min.y,2*Math.hypot(rx,rz)*0.82)/2*1.04};
const[sc0,sg0]=cv(128),gr0=sg0.createRadialGradient(64,64,6,64,64,62);gr0.addColorStop(0,'rgba(0,0,0,0.5)');gr0.addColorStop(1,'rgba(0,0,0,0)');sg0.fillStyle=gr0;sg0.fillRect(0,0,128,128);
const shw=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:own(new THREE.CanvasTexture(sc0)),transparent:true,depthWrite:false}));shw.rotation.x=-Math.PI/2;shw.renderOrder=-1;
shw.scale.set((box.max.x-box.min.x)*1.15/0.75,(box.max.z-box.min.z)*1.15/0.75,1);shw.position.set((box.min.x+box.max.x)/1.5,box.min.y/0.75+0.05,(box.min.z+box.max.z)/1.5);G.add(shw);
function dispose(){G.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material)[].concat(o.material).forEach(m=>m.dispose());});owned.forEach(t=>t.dispose());}
return{group:G,fit,dispose,cfg:c};}

// Lumières et caméra communes
let RR=null;
function setup(r){RR=r;r.outputEncoding=THREE.sRGBEncoding;r.toneMapping=THREE.ACESFilmicToneMapping;r.toneMappingExposure=1.08;}
function studioEnv(scene){if(!RR||!THREE.PMREMGenerator)return;const es=new THREE.Scene(),sg=new THREE.SphereGeometry(50,32,16),pos=sg.attributes.position,cols=[];
for(let i=0;i<pos.count;i++){const y=pos.getY(i)/50,k=Math.max(0,y);cols.push(0.42+0.5*k,0.4+0.47*k,0.46+0.48*k);}sg.setAttribute('color',new THREE.Float32BufferAttribute(cols,3));
es.add(new THREE.Mesh(sg,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.BackSide})));
for(const[x,y,z,w,h,k]of[[22,28,34,34,22,1.6],[-34,18,-20,26,30,0.8]]){const pl=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:new THREE.Color(k,k,k)}));pl.position.set(x,y,z);pl.lookAt(0,0,0);es.add(pl);}
const pm=new THREE.PMREMGenerator(RR);scene.environment=pm.fromScene(es,0.04).texture;pm.dispose();}
function lights(scene){studioEnv(scene);scene.add(new THREE.HemisphereLight(0xfff6ee,0x8a8494,0.32));
const key=new THREE.DirectionalLight(0xfff4ea,0.95);key.position.set(30,36,72);key.castShadow=true;key.shadow.mapSize.set(2048,2048);const sc=key.shadow.camera;sc.left=-35;sc.right=35;sc.top=35;sc.bottom=-35;sc.near=1;sc.far=200;key.shadow.bias=-0.0004;key.shadow.radius=3;scene.add(key);
const rim=new THREE.DirectionalLight(0xffe6d0,0.85);rim.position.set(-40,30,-50);scene.add(rim);const fill=new THREE.DirectionalLight(0xe0ecff,0.22);fill.position.set(-50,10,30);scene.add(fill);
const camFill=new THREE.DirectionalLight(0xfff6ee,0.22);scene.add(camFill);return camFill;}
function aim(cam,fit,el,zoom,light){const vh=cam.fov*Math.PI/360,hh=Math.atan(Math.tan(vh)*cam.aspect),d=fit.r/Math.sin(Math.min(vh,hh))*zoom,AZ=0.34;
cam.position.set(fit.c.x+d*Math.sin(AZ)*Math.cos(el),fit.c.y+d*Math.sin(el),fit.c.z+d*Math.cos(AZ)*Math.cos(el));cam.lookAt(fit.c);if(light)light.position.copy(cam.position);}

return{build,clean,encode,decode,lights,setup,aim,hair,HAIRK,HSDEF,PRESETS,NEUTRAL,ENUM,ACC,SHAPES,ANCHORS,HOOKS};
})();
