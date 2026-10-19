---
name: mini-jefes
description: "Los cuatro mini jefes (Moctezuma, Yiatzo, Atlahua, Xiuhquetzal): reglas de Juan, diseño aprobado y cómo están hechos en el juego"
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-11T21:36:25.403Z
---

Mini jefes elementales (pedidos el 10-10-2026): Moctezuma (tierra, guerrero águila de jade), Yiatzo (viento, mago), Atlahua (agua, tritón) y Xiuhquetzal (fuego, fénix rojo y violeta).

Reglas de Juan:
- Tamaño de 5 a 6 bloques, con anatomía imponente.
- **Una sola barra de vida, sin fases.** La barra es más baja que la de los jefes, pero con detalle.
- **No alteran el clima.**
- **Sin interactividad** (nada de minijuegos).
- **Solo tres ataques:** normal, de área y especial.
- Ataques y efectos increíbles.
- Animaciones según la anatomía de cada uno.
- **Presentación como los jefes.**
- Tienen huevos.

Diseños aprobados el 11-10-2026: «todos los diseños están god».

Estado (11-10-2026): implementados en el juego.
- `minijefes_juego.py` convierte los vóxeles en una malla propia (`assets/atalaya/minijefes/*.malla`, que lee `MiniJefeMalla`). No usa cajas de vanilla.
- La pintan `MiniJefeCuerpoLayer` y `MiniJefeRenderer`.
- Las animaciones salen de `minijefes_anim.py`, con cinemática inversa y física horneada.
- La base es `MiniJefeEntity` y cada uno tiene su `<Nombre>Entity` y `<Nombre>Efectos`.
- Para probar: `/atalaya minijefe <orden>`.
- Mundo de prueba: `run/saves/MiniJefes`, generado por `scratchpad/dp_minijefes.py`.
- Página de la ficha: https://claude.ai/artifact/PsYn7rRH4Uu89cqTwG7xDq

Sonidos (11-10-2026): Juan dijo que se parecían a los de los jefes. Era cierto: usaban la misma física (roca y jade como Rajang, agua como Nerea, viento como Aeralis, fuego como Novilis). Se rehicieron con instrumentos propios:
- Moctezuma: música de guerra mexica.
- Yiatzo: cuencos, campanas y arpa eólica.
- Atlahua: caracola, orcas y delfines, tridente-diapasón, tam-tam. No "bajo el agua": eso es de Nerea.
- Fénix: canto de ave, bengala y fuegos artificiales.

`scratchpad/comparar_mj.py` mide el parecido con los jefes.

Rendimiento (11-10-2026): la malla tiene niveles de detalle, elegidos por píxeles por bloque. Además se recortan fuera de cámara solo andando o dormidos.

Cambios del 11-10-2026 por la tarde, pedidos por Juan:
- **Estilo de mob de Minecraft**: bloques de 2 píxeles con textura de píxel y luz plana. Ver [[detalle-sin-cubos-visibles]].
- **4 bloques más de alto**: `ESCALA` en minijefes_modelo pasa a la `Geometria`. En cada `<Nombre>Entity`, `K` escala lo del cuerpo y `KA` (su raíz) las zonas de ataque.
- **Barra como la de los jefes pero más baja**: 220x32, con medallón, cresta, punta y muescas de su material.
- **Animaciones de Yiatzo y del fénix rehechas** porque "no parecen reales":
  - Yiatzo: deriva al flotar, codos doblados, anticipación y seguimiento, el Ciclón dirigido con el bastón y sin girar.
  - Fénix: la mano del ala llega tarde, cuello estirado en el picado.

Tras probarlo en el juego (11-10-2026, noche), Juan pidió más cambios. Están hechos:
- **Fénix:** vuela tendido a 60°, con patas y cola hacia atrás. La pieza vacía `hombros` deshace la inclinación para que las alas batan igual; `VIEJA` devuelve el cuerpo erguido en el capullo. La cabeza mira a su presa (`mirarA` + `DATA_MIRA`). Tiene plumas bajo el ala. El picado no se hunde (sin noPhysics). Al morir queda tendido boca abajo.
  - Las animaciones de alas le parecieron "excelentes": no tocarlas.
- **Moctezuma:** macuahuitl delante como un jugador. La Tormenta, con círculos del brazo (antes giraba como un tornillo). El Terremoto sacude la cámara (onda 2.8).
- **Yiatzo:** túnica en jirones con física (`falda`/`falda2`); al morir se desploma como túnica vacía.
- **Atlahua:** al morir cae de frente, no de lado "como tronco".
- **Barras:** el nombre se cortaba arriba; ahora mide 11 de alto.

**Revisión en el juego (11-10-2026, tarde):** Juan pidió que yo mismo revisara cada detalle y le diera la lista; luego pidió "haz todas las mejoras". Hechas:
- Giros sin tirones: `continuas()` + `entre_ticks()` en minijefes_anim (vanilla interpola ángulos por el camino largo; el macuahuitl, el bastón y el tridente daban la vuelta en un tick). `scratchpad/verificar_curvas.py` lo mide.
- Fénix: alas tendidas hacia atrás (`XIUHQUETZAL_ALA_TENDIDA`), patas recogidas bajo el vientre (`XIUHQUETZAL_PATAS`), caída de vientre con alas flojas.
- Yiatzo: la falda se corta en y = 15/23 (solo jirones), juntas con solape 2/3 y poca física.
- Moctezuma: se planta a 2.9·K; alza el arma recta antes de clavar (no cruza el casco).
- Presentación: primer plano más lejos para los mini jefes.

**Botín (11-10-2026):** los mini jefes no sueltan nada por ahora (Juan tiene una idea para ellos).

**Estilo Mitologías descartado (11-10-2026):** Juan pidió rehacerlos como los jefes de la serie Mitologías (pocas cajas grandes con el detalle pintado). Vio las primeras pruebas y prefirió el diseño que ya tenían ("es mejor continuar con lo anterior"). Se borró el módulo de prueba. No volver a proponerlo.

**How to apply:** no añadirles fases, clima ni minijuegos; si se retocan, regenerar con los scripts (`minijefes_juego` → `minijefes_anim` → compilar), nunca editar a mano los `.java` GENERADO. Un sonido nuevo de mini jefe no debe salir de la física de sonido de su jefe del mismo elemento.

Relacionado: [[jefes-rapidos-e-imponentes]], [[todo-propio-sin-vanilla]], [[disenar-con-libertad]], [[detalle-sin-cubos-visibles]].
