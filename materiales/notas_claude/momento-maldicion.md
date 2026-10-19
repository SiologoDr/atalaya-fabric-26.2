---
name: momento-maldicion
description: El Momento Maldición/Fractura (nuestro «momento Reviil» de DEDsafío) — lo que Juan pidió y lo que no quiere
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-16T04:09:09.998Z
---

El 15-10-2026 Juan pidió nuestro «momento Reviil» de DEDsafío. En DEDsafío 4, Reviil (el villano de la serie) lanza un evento en el que el cielo se vuelve rojo y se raja, y al final sale en el chat un icono con «MOMENTO REVIIL:» y el texto en rojo. Pidió: «hazlo mil veces mejor, que me sorprendas».

Se lanza con `/atalaya momento_maldicion "título" "texto" [segundos]` y se para con `stop`; también está en el menú. Está hecho en `MomentoMaldicion` (servidor), `MomentoMaldicionCliente`, `MomentoMaldicionHud` y `CieloRoto`. Los generadores son `momento_maldicion.py` y `momento_maldicion_sonidos.py`. La sección del README es «El Momento Maldición».

Lo que fijó Juan, ronda a ronda:
- **Todo creado por nosotros.** Los compañeros dejaron vídeo, sonido y música solo como idea («no era que lo copies igual»). La cinemática propia es el Sello: un sello que se dibuja, un núcleo que se carga, silencio en blanco y la pantalla que revienta.
- **Sin texto en la animación, de ninguna forma.** Ni título ni runas que parezcan letras: se usan sigilos geométricos. El texto solo sale al final, en el chat.
- **En el chat**, la cabecera es siempre «MOMENTO FRACTURA:» en letras metálicas con brillo, y el texto en rojo, como en DEDsafío. El rótulo son cuadros animados de 32×32 en el atlas de objetos, que el chat pinta seguidos.
- **Nada en el HUD mientras dura:** fuera las bandas de cine («como cine antiguo»), las rayas de las esquinas, el contador y el título de la esquina.
- **La fractura va en el cielo, no en el HUD.** El cielo de sangre le pareció «god». Las grietas tienen que cubrir todo el cielo y estar animadas. Hoy es un mosaico de cristal (Voronoi) con ondas de luz, huecos, trozos que caen y una rasgadura arriba.
- **Pide más detalle e intensidad cada vez:** la cinemática a resolución de pantalla, con brillo y movimiento, y sonido trabajado.

**Why:** quiere un evento de serie al nivel de DEDsafío, pero propio y sorprendente.

**How to apply:** si se retoca, no volver a meter texto ni HUD fijo. Probar en el juego con fotos (`scratchpad/dp_momento.py`) y enseñar el resultado. Relacionado: [[serie-tipo-dedsafio]], [[todo-propio-sin-vanilla]], [[letras-de-pixel-en-el-juego]].
