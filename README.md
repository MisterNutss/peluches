# Peluches

Peluches 3D sans fond pour des items « Site Web » FiveM.

- `index.html` : la page 3D transparente. Chaque peluche est décrite dans son lien (`?p=...`), donc chaque peluche a son propre lien. C'est cette page que GitHub Pages publie : https://misternutss.github.io/peluches/
- `atelier.html` : l'atelier sur GitHub Pages (https://misternutss.github.io/peluches/atelier.html). Réglages à la main, pipette, imprimé ; la création automatique depuis les photos y demande une clé API Claude (enregistrée dans le navigateur).
- `atelier-peluches.html` : le même atelier, publié comme page claude.ai : la création automatique depuis les photos y utilise le compte Claude de la personne connectée.
- `sources/` : le code d'origine.
  - `plush_model.js` : le modèle 3D de la peluche, partagé par l'atelier et la page 3D. Les cheveux sont faits de vraies mèches, réglées par longueur, volume, raie, frange, texture, attache et côtés.
  - `gen_atelier.py` : construit les trois pages à partir du modèle (mise en page, réglages, consignes données à Claude pour analyser les photos).

Régénérer les pages après une modification :

```bash
python sources/gen_atelier.py atelier-peluches.html index.html atelier.html
```
