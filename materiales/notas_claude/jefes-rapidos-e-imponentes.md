---
name: jefes-rapidos-e-imponentes
description: Cómo quiere el usuario los jefes y cómo probarlos en el juego (lecciones de Nerea)
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-04T02:39:18.042Z
---

Los jefes tienen que ser rápidos, fluidos e intimidantes: ataques secos con poco respiro entre ellos (solo los de aviso en grupo, como Remolino y Mirada, pueden ser lentos), con temblor de cámara, ondas expansivas, escombros y viñeta de miedo. Animaciones con física creíble: pies plantados (IK), inercia en cadenas, corales y algas, el arma bien agarrada (el tridente a plomo como bastón, giro de muñeca corto al atacar) y nada que se quede flotando. Proyectiles rápidos: le parecieron lentas unas burbujas a 3 bloques/s.

Cada jefe lleva sonidos y efectos nuevos: ni los del Vigía ni nada de vanilla, tampoco la niebla de la barra de jefe ni objetos vanilla en el botín. Nace inmóvil hasta detectar a un jugador. Ver [[todo-propio-sin-vanilla]].

Pruebas en el juego: esperar unos 20 s dentro del mundo antes de que empiece la escena (si no, todo va a tirones) y variar las cámaras por ataque. Las fotos se sacan desde dentro del juego (FotosPrueba + run/atalaya_fotos.flag) porque el usuario usa el PC mientras tanto.

Con Aeralis (2026-10-04) pidió que el movimiento y los ataques se vean «profesionales» como los de Nerea. Lo que lo arregló: un jefe volador necesita inercia (se inclina al avanzar, se ladea al girar), batida orgánica con física, pasadas rasantes y embestidas con cada golpe. Las poses deben leerse DE FRENTE: alas planas de canto no se ven. Los efectos importantes van con partículas de largo alcance (sendParticles con force), que el grupo está lejos. También compara el daño contra armadura con el del jefe anterior.

**Why:** lo pidió así al revisar a Nerea (2026-10-03): «deben ser intimidables, por algo es un boss».
**How to apply:** en cualquier jefe nuevo, aplicar desde el principio el pase de física (nerea_fisica.py), los efectos de presencia (NereaPresencia) y tiempos cortos.

**Jefes de suelo (Rajang):**
- Andar y correr con el MoveControl de vanilla (`setWantedPosition`). Al atacar hay que pararlo con `setWantedPosition` a su propia posición; si no, el control lo sigue arrastrando y girando.
- Si el jefe es muy largo, el origen va al centro de masa y la cabeza y la grupa llevan entidades-caja que le pasan el daño.
- Los saltos usan su propia gravedad, calculada para que la parábola dure lo que el vuelo de la animación.

