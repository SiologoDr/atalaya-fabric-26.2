---
name: ruleta-cambios-de-dificultad
description: La Ruleta (medallón tragaperras de un rodillo) para los cambios de dificultad — 4 finales con su color; sale ya girando; rótulos sin metal; iconos A y rótulo B hasta que Juan elija
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-18T01:40:45.731Z
---

El 17-10-2026 Juan pidió los «cambios de dificultad» con una animación de casino: «no de 3 sino de solo 1», la casilla
que se mueve y para, una misma animación con **cuatro finales**: huevo con interrogación = mob nuevo (chat **naranja**),
advertencia = cambio de dificultad (**amarillo**), penalización (**celeste**) y minijuego (**verde**). «Fluida y con
sonido de casino». Con esos cuatro se cubre todo lo de DEDsafío.

Segunda ronda, el mismo día (le gustó el diseño):
- **Que salga ya girando** («para que los usuarios no sepan qué acción es»): nunca un icono quieto al principio. El
  icono en el que casi para (el señuelo) es al azar; la tira sale de una semilla del servidor.
- **Usar el espacio como el círculo de la ruleta de DEDsafío:** ahora es un medallón redondo en el que el rodillo lo ocupa
  casi todo (aro de bombillas, gemas por final, la atalaya en la cresta).
- **Más rápido y el doble de largo** (8,5 s de giro), **más inmersivo y con tensión** (corazón, viñeta, señuelo).
- Rótulos del chat: «no se lee muy bien; deja el brillo que pasa, pero la letra y la textura son muy metálicas». Ahora
  letra de píxel propia tan alta como el texto, colores planos; estilos A Clara, B Negrita (el que va) y C Etiqueta.

Hecho: `/atalaya ruleta <mob|dificultad|penalizacion|minijuego> [texto]` y `stop`; varias seguidas esperan turno.
Clases `Ruleta`, `RuletaCliente`, `RuletaHud`; generadores `ruleta.py` y `ruleta_sonidos.py`; README «La Ruleta».

Página: https://claude.ai/artifact/WLHtFq9NQoDapFU4nZ5WcP (iconos, rótulos y vídeo de la tirada). En el mod, la A de
cada icono y el rótulo B hasta que elija (`ELEGIDOS` y `ROTULO` en `ruleta.py`).

**Why:** es el sistema de eventos diarios de la serie ([[serie-tipo-dedsafio]]), al nivel del [[momento-maldicion]].

**How to apply:** mantener una sola animación con cuatro finales y los colores del chat; nada que delate el final antes
de tiempo. En el HUD, dibujar por tandas de la misma textura: alternar texturas bajaba de 60 a 30 FPS en su gráfica.
Probar con `FotosPrueba` `RULETA_FILM` (reloj parado, una foto por tiempo); **nunca grabar el escritorio**, porque
capturó otra ventana de Juan y hubo que borrarlo. Si Juan tiene abierto el cliente de prueba y lo usa, no cerrárselo.
Ver [[iconos-con-propuestas]] y [[todo-propio-sin-vanilla]].
