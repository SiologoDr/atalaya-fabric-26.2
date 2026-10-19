---
name: serie-tipo-dedsafio
description: "Objetivo del proyecto Atalaya — mod Fabric para una serie hardcore estilo DEDsafío (fases de dificultad, minijuegos, maldiciones, mobs propios)"
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-03T03:06:22.895Z
---

El usuario quiere usar Atalaya (mod Fabric 26.2, ya es mod aunque la carpeta diga "plugin") para una serie hardcore al estilo DEDsafío de ElDed/Eufonia Studio: cambios de dificultad anunciados con animación (ruleta), minijuegos, "momentos maldición" y mobs propios con modelo y animaciones.

Decisión (2026-10-02): seguir como mod Fabric, sin pasar a plugin ni GeckoLib. Los mobs se hacen con el sistema de keyframes de vanilla (AnimationDefinition/KeyframeAnimation). La distribución a los jugadores (modpack o launcher) queda para más adelante.

Primer mob: el Vigía (VigiaEntity). Lo diseñé yo a petición suya. El usuario pidió que la animación de ataque fuera "profesional, no genérica", así que el ataque se rehízo como "Cepo" en cuatro fases: anticipación, golpe, retención y recuperación.

**Why:** el usuario va a mandar referencias de mobs nuevos y espera el paquete completo: modelo, textura, animaciones, IA y funciones.
**How to apply:**
- Las animaciones de ataque deben tener anticipación legible y el daño sincronizado con el fotograma del impacto.
- Hay que seguir el patrón del repo: interruptor en AtalayaConfig apagado de fábrica, texturas generadas por script según DISEÑO.md y comentarios en español.
