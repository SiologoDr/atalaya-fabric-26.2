---
name: bestiario-generadores-cuidado
description: Los generadores del bestiario (y las vistas) escriben siempre en src/main/resources; cómo mirar sin estropear el repo y cómo deshacerlo bien
metadata:
  node_type: memory
  type: reference
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-19T14:56:22.164Z
---

Todo lo que corre un generador del bestiario escribe en `src/main/resources`, aunque solo sea para sacar vistas. Esto incluye `ver_bestia.py` del scratchpad y `python bestiario_<familia>.py ../.. <carpeta>`. Escribe el json, las texturas, el huevo, el retrato, las partículas y los nombres en `lang/es_es.json` y `lang/en_us.json`.

**Al volver a generarlos, los PNG cambian de compresión aunque los píxeles sean idénticos.** Comprobarlo píxel a píxel con numpy contra `git show HEAD:<fichero>` antes de dar algo por cambiado.

**`B.manchas` no es determinista.** Usa `hash(cara)`, que cambia en cada proceso de Python. Pasa en el Espectro Negro, el Murciélago y la Parca Menor: si se regeneran, salen distintos. Para dejarlos como estaban, `git checkout` de sus ficheros.

**Deshacer bien:**
- Nunca `git checkout -- src/main/resources` entero. El 19-10-2026 eso borró las hormigas y las plantas nuevas sin subir; se recuperaron regenerándolas, porque sus generadores sí son deterministas.
- Revertir solo los ficheros de la familia que se ha mirado, y borrar los nuevos que no estaban.
- Quitar de `lang` las entradas que se colaron.

**Las vistas sin tocar el modelo:** `ver_bestia.py` fija `B.TEXEL = 1`. Para familias viejas, que van con `TEXEL = None`, usar el `main` del generador con una carpeta de vistas.

Relacionado: [[atalaya-hormigas-plantas-2026-10]].
