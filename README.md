# Peluches

Peluches 3D sans fond pour des items « Site Web » FiveM.

- `index.html` : la page 3D transparente. Chaque peluche est décrite dans son lien (`?p=...`). C'est cette page que GitHub Pages publie.
- `atelier-peluches.html` : l'atelier (photos, réglages, lien), publié comme page claude.ai.
- `sources/` : le code d'origine.
  - `plush_model.js` : le modèle 3D de la peluche, partagé par l'atelier et la page 3D.
  - `gen_atelier.py` : construit `atelier-peluches.html` et `index.html` à partir du modèle.
  - `prompt_fn.js` : les consignes données à Claude pour analyser les photos.
  - `photo_ai.js` : les photos, la pipette, l'imprimé et l'analyse.
  - `atelier_head.html` : la mise en page et les styles de l'atelier.

Régénérer les deux pages après une modification :

```bash
python sources/gen_atelier.py atelier-peluches.html index.html
```
