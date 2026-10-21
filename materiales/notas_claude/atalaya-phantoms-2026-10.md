---
name: atalaya-phantoms-2026-10
description: Phantom Oscuro y Phantom Explosivo (DEDsafío 4) rediseñados y metidos en el juego el 19-10; sin TNT; pesadillas del Insomnio
metadata:
  node_type: memory
  type: project
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-19T22:29:16.564Z
---

El 19-10-2026 se hicieron los dos phantoms con dibujo en el cartel del 07-10 (DEDsafío 4).

**Diseño:** se recrearon del cartel y Juan pidió mejorarlos: «creo que no debería tener la TNT, y en el caso del otro debería ser mejor su diseño y otro tipo de color; te lo dejo a tu criterio». Lo aprobó: «me gusta»; solo pidió arreglar la textura rara de debajo del ala.
- **Oscuro:** añil, con huesos de marfil y ojos violeta pálido; alas desgarradas, garras, colmillos y un garfio en la cola.
- **Explosivo:** carbonizado con grietas de brasa, alas con el borde ardiendo, un buche de fuego y una mecha en la cola.
- **Generador:** `bestiario_phantoms.py`.

**Juego:** `bestiario/mobs/Phantoms.java`. Dan vueltas por encima de ti y se lanzan en picado.
- El Oscuro te hace soltar un hueco entero del inventario.
- El Explosivo deja una brasa que revienta al segundo y medio (radio 3).
- Salen en las pesadillas (`Insomnio.PESADILLAS`) y con huevo. Los phantoms ladrones del DEDsafío 2 y 3 ya son un cambio.
- Juan los vio en la prueba y preguntó si iban muy rápidos (no se acelera el mundo en las pruebas). Pidió: «que sea como un phantom normal, pero al doble todo». Vuelan con la lógica copiada del phantom de Minecraft (control de vuelo, vueltas sobre un ancla a 20-40 bloques de altura, picado). La velocidad, la aceleración y el giro son el doble. El picado llega cada 4-5 s, cuando el phantom normal tarda 8-11 s. La prueba pasa (19-10). Juan lo subió a develop con la pestaña «Atalaya» del creativo (c6303ba).

**Lecciones de la membrana:**
- Una lámina con dos caras en el mismo plano se pisa, porque el render de las bestias no oculta las caras de atrás. Va una sola cara.
- Las cajas deben medir píxeles finos enteros; con 13,8 se colaba una columna de otra textura.
- Una parte girada no gira sus cajas: hay que girarlas como en las alas de las bombas.

**Why:** son las pesadillas del Insomnio del DEDsafío 4.

**How to apply:** la prueba es `materiales/pruebas/prueba_phantoms.py`. Las fotos del aire se hacen en espectador, porque en supervivencia la cámara cae antes de la foto.
