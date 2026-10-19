---
name: todo-propio-sin-vanilla
description: "El usuario exige que los mobs nuevos usen solo assets propios — sonidos, partículas, animaciones (incluida la muerte), nada de vanilla"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-16T02:54:11.822Z
---

Todo lo que tenga que ver con un mob nuevo debe ser creado por nosotros, no reutilizado de Minecraft:
- **sonidos:** se sintetizan con Python (numpy, scipy y soundfile → .ogg Vorbis mono);
- **partículas:** sprites propios y una clase de cliente propia;
- **animaciones:** reposo o inactivo, andar, persecución, ataques y **muerte** propia (anulando el tumbado de vanilla con getFlipDegrees=0 y tickDeath alargado).

También hay que ocultar las partículas de los efectos de vanilla que se apliquen (MobEffectInstance con visible=false).

**Why:** el usuario lo pidió de forma explícita y en dos tandas: primero los sonidos y la muerte, después las partículas ("todo debe ser creado, no usar lo de minecraft"). Lo quiere a nivel profesional para su serie estilo DEDsafío ([[serie-tipo-dedsafio]]).

Los sonidos también tienen que sonar a la temática del mob, no a tonos sintéticos genéricos. Con Nerea, el jefe de agua, pidió rehacerlos "acorde con el boss y su temática de agua" (2026-10-03). Se rehicieron con modelos físicos: burbujas de Minnaert, chapuzones, olas con espuma, gotas, vapor y una voz con gárgaras.

Lo mismo vale para los **ataques y las texturas**. Con Rajang (2026-10-04) dijo: «los ataques debes recrearlos tú, no sacar bloques de Minecraft». Los picos y columnas hechos de cajas de tierra y los tótems y meteoritos cúbicos le parecieron raros. También le pareció «repetitiva» la piel hecha con una loseta que se repite por todo el cuerpo.

Tampoco vale el material de otros, ni el de los compañeros del equipo. El 15-10-2026, para el Momento Maldición, unos compañeros dejaron vídeo, sonido y música como idea. Juan: «la música y animación lo debes de crear tú mismo, solo te di más o menos una idea pero no era que lo copies igual; recuerda que aquí todo lo creamos». Lo que traigan es referencia de tono: no se mete en el mod y no se calca su estructura.

**How to apply:**
- Las ideas de terceros (vídeos, audios, imágenes) se usan solo para entender qué se busca. La música, los sonidos y la cinemática se crean desde cero con un concepto propio.
- Los ataques se hacen con mallas propias que no parezcan bloques: esquirlas facetadas, columnas hexagonales, estelas talladas, cristales bipiramidales, losas arrancadas, calcos en el suelo con glifos y cuentas atrás.
- Las texturas de los jefes se pintan cara por cara a partir de su posición en el cuerpo, nunca con losetas repetidas (ver materiales/generadores/tierra_piel.py y tierra_ataques.py).
- En los renders, lo que brilla sumado se pinta al final, después de lo opaco.
- En cada mob nuevo hay que entregar desde el principio: modelo, textura, animaciones (inactivo, andar en calma, persecución, ataques, muerte), sonidos y partículas propios.
- El sonido se diseña desde el material o elemento del mob (agua, piedra, fuego...), no con osciladores sueltos. nerea_sonidos.py sirve de plantilla y saca una hoja de espectrogramas para revisarlo.
- Hay que verificarlo en el juego con capturas.
- Los generadores están en materiales/generadores/ (vigia_tex.py, vigia_iconos.py, vigia_particulas.py, vigia_sonidos.py) y sirven de plantilla.
