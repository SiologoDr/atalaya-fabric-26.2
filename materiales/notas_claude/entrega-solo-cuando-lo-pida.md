---
name: entrega-solo-cuando-lo-pida
description: No subir la versión del mod ni dejar un .jar nuevo en entrega/ salvo que el usuario lo pida
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-08T22:18:07.718Z
---

No crear una «versión de entrega» (subir `mod_version`, compilar y dejar `entrega/atalaya-X.jar` borrando el anterior) al acabar cada tarea. Solo cuando el usuario lo pida expresamente.

**Why:** el 08-10-2026 lo dijo así: «deja de crear versión de entrega, eso deberías hacerlo cuando yo te lo pida, no cada vez que te doy una tarea». Hasta entonces se hacía en cada encargo.

**How to apply:** compilar para comprobar (`compileClientJava`, pruebas en el juego con `runClient`) sí; pero no tocar `gradle.properties`, las menciones de versión del README ni `entrega/` hasta que lo pida. Cuando lo pida, subir la versión, compilar, copiar el jar a `entrega/` y quitar el viejo.

Última entrega: **1.2.5** (22-10-2026, `entrega/atalaya-1.2.5.jar`, pedida por Juan tras rediseñar por completo los hermanos de la familia: Plumosaurio, Cavador, Reptisaurio Salvaje, Guerrero y Dromoraptores con animaciones únicas, texturas y mecánicas). Antes, la 1.2.4 (22-10-2026, integración de los 12 mobs de Quiu con animaciones y sonidos), la 1.2.3 (20-10-2026, el catálogo del DEDsafío con el bestiario, el Limbo y la pestaña Atalaya del creativo). La siguiente, 1.2.6 salvo que diga otra cosa. Al subirla, cambiar también las cuatro menciones del README (arriba, el jar de build/libs, la lista de mods y la de entrega/).
