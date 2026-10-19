---
name: atalaya-fantasmas-2026-10
description: "Los 4 fantasmas del DEDsafío (Blanco, Negro, Amarillo, Rojo) metidos en el juego el 19-10 con sus mecánicas; Corazón Blanco; sin Espada Fantasmal"
metadata:
  node_type: memory
  type: project
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-19T21:06:26.446Z
---

Los cuatro fantasmas con ilustración (Blanco, Negro, Amarillo, Rojo) se metieron en el juego el 19-10-2026.

**Diseño:** el de la recreación tal cual (`bestiario_fantasmas_v2.py`). Juan rechazó todas las mejoras y dijo: «mejor déjalo como está». Ver [[recrear-primero-luego-mejorar]].

**Código:** `bestiario/mobs/Fantasmas.java`, las fichas `ESPECTRO_*` en `Fichas.java` y `CorazonesRobados`. Vuelan como las bombas. Su zarpazo es el daño `atalaya:fantasma`, que no empuja.
- **Blanco:** un zarpazo cada 8 ticks, y cada uno te pone Lentitud.
- **Negro:** cada golpe te quita un corazón para siempre; el dato se guarda en el jugador y sigue al morir. Al morir suelta un **Corazón Blanco** por cada corazón que robó, y comiéndolo recuperas uno.
- **Amarillo:** te gasta el tótem de la mano (con `TotemInvoker`), se te mete dentro 5 segundos y sale a por otro jugador cercano.
- **Rojo:** te agarra (te deja enraizado) y te pega hasta que muere él o mueres tú.

**Decisiones de Juan (19-10):**
- Sin Espada Fantasmal: «que cualquier arma les haga daño».
- El corazón robado se recupera «con un corazón blanco, no uno dorado».
- El Atómico se queda con su píxel: «déjalo así, me gusta».

**Why:** son los mobs del Limbo y de la noche del DEDsafío 3 y 4.

**How to apply:** la prueba es `materiales/pruebas/prueba_fantasmas.py`. Cómo se consigue el Corazón Blanco (que lo suelte el Negro) lo decidí yo; Juan puede cambiarlo.
