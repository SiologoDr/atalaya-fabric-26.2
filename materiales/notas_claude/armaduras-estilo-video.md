---
name: armaduras-estilo-video
description: Rediseño de las armaduras de los jefes (11-10-2026) al estilo de un vídeo de DEDsafío: probado y descartado por Juan; qué no le gustó
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-12T00:14:49.041Z
---

El 11-10-2026 Juan dijo que las armaduras de los jefes (mareas, jade, vendaval, solar: mallas 3D con alas, halos, capas y cristales) «se pasan mucho». Pidió un rediseño «que no se pase pero que quede bien», visto primero en una página.

Su referencia es una armadura de flor rosa de DEDsafío (vídeo de TikTok: https://vt.tiktok.com/ZSb3vWTD8/). Rasgos:
- la forma de la armadura de vanilla, con colores limpios y degradados suaves;
- el casco en franjas;
- **las manos al aire**: la manga acaba en la muñeca;
- la cara a la vista;
- unas hombreras sencillas y un faldón a la espalda hasta las rodillas;
- toques de otro color (flores, hojas).

Lo que rechazó:
- Las tandas con placas, ribetes de oro y escamas («lo veo raro»). Cubrir las manos («eso no va»).
- El traje moteado, de manchas de ruido como un camuflaje («se ve rara igual»).

Página de propuestas: «Armaduras de Atalaya», https://claude.ai/artifact/Uf9Cvw9jFeZbWhA8PLGgb9. Por armadura:
- la de ahora (foto del juego);
- A: la armadura sola;
- B: como la del vídeo, con hombreras, faldón y un detalle en el casco.

Se generaron con `scratchpad/armaduras_flor.py` y `render_armadura.py`, que imita el render del juego.

**Descartado (11-10-2026):** vio la página y dijo «está feo, dejemos ese tema ahí de las armaduras». Las armaduras se quedan como estaban. No volver a proponer el rediseño salvo que él lo saque.

**Why:** quiere que se parezcan a la serie que imita ([[serie-tipo-dedsafio]]) y que no recarguen al jugador.

**How to apply:** en armaduras y ropa, partir de la forma de vanilla con poco 3D. Usar color plano con degradado y motivos gráficos, no ruido. Dejar siempre las manos y la cara a la vista. Si manda un vídeo, sacar fotogramas (imageio-ffmpeg está instalado) en vez de suponer. Relacionado: [[armaduras-por-rol]], [[iconos-con-propuestas]].
