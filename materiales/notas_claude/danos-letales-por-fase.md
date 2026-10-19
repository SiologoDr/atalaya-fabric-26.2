---
name: danos-letales-por-fase
description: "Cómo quiere el daño de los jefes: letal en todas las fases, muy letal en la IV, medido contra netherita P4 + manzana de Notch"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-05T02:00:02.758Z
---

El usuario quiere que los jefes sean letales en todas las fases y que maten de verdad: el evento es de unos 40 jugadores en hardcore y «deben morir personas». La fase IV debe ser muy letal, la III algo menos, y la II y la I letales pero menos.

**Referencia de cálculo:** un jugador con netherita entera, Protección IV y manzana de Notch, que aguanta 18 corazones con la absorción. Daño final por golpe, en corazones:

| Tipo de golpe | Fase I | Fase II | Fase III | Fase IV |
|---|---|---|---|---|
| Fuerte | 3,5 | 5 | 7,5 | 11 |
| De área | 2,5 | 4 | 5,5 | 8 |
| Por segundo | 1 | 1,5 | 2 | 3 |

Además:
- La Mirada de Nerea, el impacto directo del meteorito de Rajang y el Rugido de Jade (si el Sello no se rompe a tiempo, en cualquier fase y a todos los que estén en su rango) matan. Solo salva un tótem.
- En sus ataques cooperativos o «de mecánica», los jefes son inmunes: Rajang durante el Sello (solo sirve romper los tótems), Nerea durante la Mirada (solo se para disparándole a los ojos) y Aeralis durante el Juicio del Ciclón (solo sirve romper los núcleos). No durante sus tornados pequeños: el usuario lo aclaró.
- Al público le gustó el Cataclismo: ahora son 6 oleadas (12 s) y caen más. El Sello sale menos: 2 min de descanso tras acabar.
- El Juicio de Aeralis mata al marcado si no le rompen ningún núcleo; cada núcleo roto le quita un 25 %.

Implementado (2026-10-04) como tablas `float[] DANO_X = {I, II, III, IV}` y `dano(float[])` en NereaEntity, AeralisEntity y RajangEntity. Se comprobó en el juego: el zarpazo de la fase IV quitó 22 puntos (11 corazones), tal como dice la fórmula.

**Why:** tal como estaban, con netherita P4 y manzana la fase IV necesitaba entre 3 y 14 golpes para matar; el usuario quiere un reto de verdad.

**How to apply:** para un jefe nuevo, partir de estos objetivos y sacar el daño en bruto con las fórmulas de armadura, Protección y Resistencia. Los tipos de daño llevan `scaling: never`, así que la dificultad no los cambia. Aeralis y Rajang pegan ×1,3 contra armadura completa (`contraArmadura`). Ver [[jefes-rapidos-e-imponentes]] y [[rajang-jaguar-de-jade]].
