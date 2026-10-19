---
name: mariposa-vendaval
description: "Jefe elemental del aire (2 de 4), la Mariposa del Vendaval — diseño propio a partir de sus referencias, ficha publicada y decisiones pendientes"
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-04T17:52:48.922Z
---

Segundo jefe elemental (aire), empezado el 2026-10-04 a partir de las ilustraciones del usuario («La Mariposa del Vendaval»). El usuario pidió explícitamente no copiarlas, sino hacerlo "lo mejor que se vea e imponente".

**Diseño propuesto (mío)**
- Polilla de tormenta erguida, con unos 20 bloques de envergadura y 17 de alto; vuela con el tórax a 9 bloques.
- Cuerpo y cara:
  - quitina azul pizarra, collar de pelaje;
  - ojos compuestos rasgados bajo un ceño, colmillos, antenas plumosas;
  - «ojo de la tormenta» en el pecho.
- Alas y cola:
  - cuatro alas translúcidas con ocelos-ciclón;
  - colas de mariposa luna en las alas de abajo;
  - dos cintas de viento en el abdomen.
- Fases: Brisa → Ráfaga (añil) → Tempestad (violeta con rayos) → Ojo de la tormenta (negra, alas rasgadas, cae agotada cada 25 s).
- Ataques: Aleteo Cortante, Tornados, Picado (propio), Cacería del Vendaval (desde fase II), Juicio del Ciclón (desde fase III, con 4 núcleos).
- Números: vida 11.250 y +7 de daño por fase, como Nerea.

El usuario pidió además (2026-10-04) dos diseños basados en imágenes que le pasaron:
- **B, «El Dragón de los Mil Ojos»:** dragón mariposa con racimo de ojos-gema, escamas negras con grietas de rayo cian, cristales de amatista, cola larga (cambia el Picado por un Coletazo) y alas de mariposa sobre armazón de dragón con espirales de galaxia.
- **C, «La Polilla de Rayos»:** polilla negra con vetas de rayo, dos ojos azules, antenas con punta brillante, cristales y alas de armazón oscuro con espirales.

Ficha con A, B y C: https://claude.ai/artifact/Q1kbaPjfxNWNZp6Fi2s129. Generadores:
- A: `viento_modelo.py`;
- B y C: `viento_bc_modelo.py`;
- escenas: `viento_escenas.py`, que acepta `heroica_b`, `vistas_c`, `escala_abc`…

**Decisiones (2026-10-04):**
- Elige el **diseño A**: B y C «no dan la talla» y prefiere que lo diseñe yo con libertad (ver [[disenar-con-libertad]]).
- **Nombre: Aeralis** (no Céfira); la barra de vida pone «AERALIS» en letras de píxel.
- Los 4 ataques de sus ilustraciones (Aleteo Cortante, Tornados, Cacería del Vendaval, Juicio del Ciclón), sin el Picado.
- Mismas fases y barra propia que Nerea, pero más fuerte: vida 13.500 y +9 de daño por fase.
- Construido en el mod (2026-10-04): AeralisEntity y sus cuchillas, tornados, ráfagas y núcleos, barra, 70 sonidos de viento.
- Daños base tras su revisión (2026-10-04, «no influyen mucho daño a las armaduras»): cuchilla 14, ráfaga 16, estallido del tornado 13 (todos +9 por fase y hasta +30 % contra armadura), tornado 7/s que atraviesa la armadura, Juicio 44 −11 por núcleo roto.
- Sonidos y efectos nuevos de viento; alcance alto.

**Why:** se sigue el mismo proceso que con Nerea: ficha → aprobación → construir. Ver [[nerea-diseno-a]] y [[jefes-rapidos-e-imponentes]].

**How to apply:** las clases y recursos del mod usan el nombre Aeralis. Aplicar [[todo-propio-sin-vanilla]]: sonidos de viento propios, partículas propias, barra propia con letras en píxel y huevo dibujado.
