// Bibliothèque des peluches, stockée dans Vercel Blob.
// GET            : toutes les peluches (les plus récentes d'abord)
// GET ?nom=...   : une peluche
// POST           : { nom, p, image, code } enregistre (ou remplace) une peluche
// DELETE         : { nom, code } la retire
// Le code secret est la variable d'environnement PELUCHES_CODE du projet Vercel.
import { put, list, del } from '@vercel/blob';

const slugOf = s => String(s || '').normalize('NFD').replace(/\p{M}/gu, '').toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40);

async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  let d = '';
  for await (const ch of req) d += ch;
  return JSON.parse(d || '{}');
}

// Accès au stockage : connexion automatique de Vercel (OIDC, jeton reçu dans l'en-tête de la requête),
// sinon la variable BLOB_READ_WRITE_TOKEN si elle est réglée
let AUTH = {};
const authFrom = req => {
  const t = req.headers && req.headers['x-vercel-oidc-token'];
  return t && process.env.BLOB_STORE_ID ? { oidcToken: t, storeId: process.env.BLOB_STORE_ID } : {};
};

// Chaque envoi crée une adresse différente (?v=date), ce qui évite de lire une ancienne version en cache
const fresh = b => b.url + '?v=' + new Date(b.uploadedAt).getTime();

async function readAll(prefix) {
  const { blobs } = await list({ prefix, limit: 1000, ...AUTH });
  const images = Object.fromEntries(blobs.filter(b => b.pathname.endsWith('.png')).map(b => [b.pathname.slice(9, -4), fresh(b)]));
  return Promise.all(blobs.filter(b => b.pathname.endsWith('.json')).map(async b => {
    const d = await (await fetch(fresh(b))).json();
    const slug = b.pathname.slice(9, -5);
    return { slug, nom: d.nom, p: d.p, date: d.date, image: images[slug] || null };
  }));
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  // La page 3D sur GitHub Pages lit les peluches ici
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') { res.setHeader('Access-Control-Allow-Methods', 'GET'); return res.status(204).end(); }
  AUTH = authFrom(req);
  try {
    if (req.method === 'GET') {
      if (req.query.nom) {
        const slug = slugOf(req.query.nom);
        const [one] = slug ? await readAll(`peluches/${slug}.`) : [];
        return one ? res.status(200).json(one) : res.status(404).json({ erreur: 'Peluche introuvable.' });
      }
      const all = await readAll('peluches/');
      all.sort((a, b) => String(b.date).localeCompare(String(a.date)));
      return res.status(200).json(all);
    }
    if (req.method === 'POST' || req.method === 'DELETE') {
      const b = await readBody(req);
      if (!process.env.PELUCHES_CODE) return res.status(500).json({ erreur: 'Le code secret n\'est pas réglé sur Vercel (variable PELUCHES_CODE).' });
      if (b.code !== process.env.PELUCHES_CODE) return res.status(403).json({ erreur: 'Code secret incorrect.' });
      const slug = slugOf(b.nom);
      if (!slug) return res.status(400).json({ erreur: 'Donne un nom à la peluche.' });
      if (req.method === 'DELETE') {
        const { blobs } = await list({ prefix: `peluches/${slug}.`, ...AUTH });
        if (blobs.length) await del(blobs.map(x => x.url), AUTH);
        return res.status(200).json({ ok: true });
      }
      if (typeof b.p !== 'string' || !/^~?[A-Za-z0-9_-]{4,40000}$/.test(b.p)) return res.status(400).json({ erreur: 'Peluche invalide.' });
      const opts = { access: 'public', addRandomSuffix: false, allowOverwrite: true, cacheControlMaxAge: 60, ...AUTH };
      await put(`peluches/${slug}.json`, JSON.stringify({ nom: String(b.nom).trim().slice(0, 40), p: b.p, date: new Date().toISOString() }), { ...opts, contentType: 'application/json' });
      let image = null;
      if (typeof b.image === 'string' && b.image.startsWith('data:image/png;base64,') && b.image.length < 2000000)
        image = (await put(`peluches/${slug}.png`, Buffer.from(b.image.split(',')[1], 'base64'), { ...opts, contentType: 'image/png' })).url + '?v=' + Date.now();
      return res.status(200).json({ ok: true, slug, image });
    }
    res.setHeader('Allow', 'GET, POST, DELETE');
    return res.status(405).json({ erreur: 'Méthode non permise.' });
  } catch (e) {
    const msg = String(e && e.message || e);
    if (/credentials/i.test(msg)) return res.status(500).json({ erreur: "Le stockage n'est pas accessible : vérifie que le Blob est relié au projet et que l'OIDC est activé (Settings → Security), ou ajoute la variable BLOB_READ_WRITE_TOKEN du Blob, puis redéploie." });
    return res.status(500).json({ erreur: 'Erreur du stockage : ' + msg });
  }
}
