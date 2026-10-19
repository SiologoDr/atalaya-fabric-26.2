---
name: segunda-capa-como-dientes
description: "Cuando Juan dice «2.ª capa» quiere picos o dientes macizos en una caja algo mayor (como los dientes de las Fauces), no velo translúcido"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-19T19:56:28.200Z
---

Juan, 19-10-2026, sobre los hombros y la falda de los fantasmas: «la 2.ª capa me refiero a como los dientes del mob de plantas, así deben ser sus hombros, quita ese trasparente».

Yo había entendido «2.ª capa» como la segunda capa de una skin: una funda de velo translúcido medio píxel más grande. No era eso.

Para él, una 2.ª capa es lo de `dientes_capa` en `bestiario_plantas.py`:
- una caja medio píxel más grande que la pieza;
- transparente salvo una banda que monta sobre la pieza y una fila de picos macizos que asoman por el borde;
- pintada a 32 por bloque (`B.fino`), para que salgan en punta.

En los fantasmas está en `picos_capa` (`bestiario_fantasmas_v2.py`):
- en los hombros, los picos se levantan;
- en la falda, cuelgan.

**Why:** los picos macizos dan la silueta rota y viva de los dibujos. El velo translúcido apenas se ve y no se parece.

**How to apply:** si Juan pide una «2.ª capa» (de dientes, hombros, falda, bordes rotos…), hazla con picos macizos sobre una caja algo mayor. No la hagas translúcida salvo que lo diga.

Relacionado: [[recrear-primero-luego-mejorar]], [[atalaya-hormigas-plantas-2026-10]].
