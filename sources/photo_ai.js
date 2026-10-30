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
if(k){const f=F[k];say('ai-status','Clique sur une photo pour prendre la couleur : '+((typeof f.l==='function'?f.l(cfg):f.l)||'Gants').toLowerCase()+'.');$('shots').scrollIntoView({block:'nearest',behavior:'smooth'});}}
function startPrintPick(){setPick(null);printPick=true;printA=null;pickUI(true);say('ai-status',"Clique sur un coin de l'imprimé, puis sur le coin opposé.");$('shots').scrollIntoView({block:'nearest',behavior:'smooth'});}
$('settings').addEventListener('click',e=>{const b=e.target.closest('.pip');if(b)setPick(pick===b.dataset.pip?null:b.dataset.pip);
const ch=e.target.closest('.seg button');if(ch&&ch.parentElement.id.startsWith('f-')){cfg[ch.parentElement.id.slice(2)]=ch.dataset.v;cfg=PL.clean(cfg);syncForm();changed();}
if(e.target.id==='f-im-pick')startPrintPick();if(e.target.id==='f-im-rm'){cfg.im='';syncForm();changed();}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&(pick||printPick)){setPick(null);say('ai-status',readyMsg());}});
function photoClick(slot,e){const cn=shots[slot].cn,b=cn.getBoundingClientRect(),x=(e.clientX-b.left)*cn.width/b.width,y=(e.clientY-b.top)*cn.height/b.height;
if(printPick){const p=[x/cn.width,y/cn.height];if(!printA){printA=[slot,p];say('ai-status',"Maintenant, clique sur le coin opposé de l'imprimé.");return;}
const[s0,a]=printA;printPick=false;printA=null;pickUI(false);if(s0!==slot){say('ai-status','Clique les deux coins sur la même photo.');return;}
say('ai-status',cropPrint(cn,[Math.min(a[0],p[0]),Math.min(a[1],p[1]),Math.abs(p[0]-a[0]),Math.abs(p[1]-a[1])])?'Imprimé ajouté sur la peluche.':'Zone trop petite : recommence.');return;}
if(!pick)return;const d=cn.getContext('2d').getImageData(Math.max(0,Math.round(x)-2),Math.max(0,Math.round(y)-2),5,5).data;let R=0,G=0,B=0,n=0;for(let i=0;i<d.length;i+=4){R+=d[i];G+=d[i+1];B+=d[i+2];n++;}
const h='#'+[R,G,B].map(v=>Math.round(v/n).toString(16).padStart(2,'0')).join('');if(pick==='gv'){lastGlove=h;cfg.gv=h;}else cfg[pick]=h;
setPick(null);cfg=PL.clean(cfg);syncForm();changed();say('ai-status','Couleur prise sur la photo.');}
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
function keysText(){return '';}
function readyMsg(){if(!(sample&&imagesOK))return "La création automatique n'est pas disponible ici. Règle la peluche à la main : le bouton Pipette prend une couleur sur la photo.";return anyPhoto()?'Peluche prête. Tu peux relancer la création ou corriger les réglages.':'Ajoute une photo de face : la peluche se crée toute seule.';}
function reviewPrompt(w,slots,nr){const cur=Object.assign({},cfg);delete cur.im;delete cur.imt;delete cur.ia;
return intro(w,slots)+"Les "+nr+" dernières images ne sont pas des photos : c'est le rendu actuel de la peluche ("+(nr>1?'de face, puis de dos':'de face')+"), fabriquée avec ce réglage :\n"+JSON.stringify(cur)+"\n"
+"Compare la peluche aux photos comme un client exigeant : coiffure et frange, couleurs des cheveux, de la peau et des yeux, barbe, lunettes, couvre-chef, haut et motif, couleurs des vêtements, accessoires, mascotte, objets. "
+"Corrige tout ce qui ne ressemble pas et garde ce qui est juste. Renvoie le réglage complet corrigé.\n"+keysText();}
function updateAnalyse(){const b=$('analyse');b.hidden=!(sample&&imagesOK&&anyPhoto());b.disabled=false;b.textContent=ctl?'Arrêter':'Relancer la création';}
// Rendu de la peluche sur fond gris neutre, pour que Claude la compare aux photos
async function renderView(rot,S){await new Promise(res=>setTimeout(res,250));const pr=r.getPixelRatio(),keep=cur.group.rotation.y;r.setPixelRatio(1);r.setSize(S,S,false);cam.aspect=1;cam.updateProjectionMatrix();cur.group.rotation.y=rot;PL.aim(cam,cur.fit,0.12,1.05,camFill);r.render(scene,cam);
const o=document.createElement('canvas');o.width=o.height=S;const g=o.getContext('2d');g.fillStyle='#8a929c';g.fillRect(0,0,S,S);g.drawImage(r.domElement,0,0);cur.group.rotation.y=keep;r.setPixelRatio(pr);fitSize();return new Promise(res=>o.toBlob(res,'image/jpeg',0.9));}
function applyAnswer(data,keep,first0,first){const prev=first?null:(cfg.im?{im:cfg.im,imt:cfg.imt,ia:cfg.ia}:null);cfg=PL.clean(Object.assign({},data,keep),PL.NEUTRAL);
if(Array.isArray(data.imp)&&data.imp.length===4)cropPrint(shots[first0].cn,data.imp.map(Number));else if(prev&&data.imp!==null)Object.assign(cfg,prev);syncForm();rebuild();updateLink();}
async function runAnalysis(){const slots=photoList();if(!slots.length||!sample||!imagesOK)return;clearTimeout(anaT);if(ctl)ctl.abort();const my=new AbortController();ctl=my;updateAnalyse();
const w=$('who').value,keep={st:cfg.st,po:cfg.po,fc:''},use=slots.slice(0,Math.max(1,maxImages)),imgs=use.map(s=>shots[s].blob);
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
refused:"Claude n'a pas pu décrire cette photo. Essaie une autre image.",invalid_json:'La réponse était incomplète. Clique sur « Relancer la création ».',session_expired:'Reconnecte-toi à Claude, puis relance la création.'})[code]||'La création a échoué. Clique sur « Relancer la création ».');}
finally{if(ctl===my){ctl=null;updateAnalyse();}}}
const getSample=window.claude&&window.claude.use?window.claude.use('sample'):Promise.resolve(null);
getSample.then(async s=>{sample=s;if(s){try{const lim=await s.limits();imagesOK=!!(lim&&lim.images);if(imagesOK)maxImages=lim.images.maxCount||1;}catch(e){imagesOK=false;}}updateAnalyse();if(!pick)say('ai-status',readyMsg());if(anyPhoto())runAnalysis();},()=>{updateAnalyse();say('ai-status',readyMsg());});
$('analyse').addEventListener('click',()=>{if(ctl){const c0=ctl;ctl=null;c0.abort();updateAnalyse();say('ai-status','Création arrêtée.');return;}runAnalysis();});
$('who').addEventListener('change',()=>{if(anyPhoto())runAnalysis();});

