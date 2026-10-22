---
name: atalaya-quiu-2026-10
description: "Familia de Quiu (22-10): 12 mobs rehechos sobre fotogramas de directos en generadores/quiu/*.py y metidos al juego con animaciones, ataques, sonidos y huevos en la 1.2.4"
metadata:
  node_type: memory
  type: project
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-22T15:35:00.000Z
---

El 20-10 y 22-10-2026 se completó toda la familia de Quiu del DEDsafío 4 y se integró en el juego en la versión `1.2.4`:

- **Módulos de modelo (`materiales/generadores/quiu/*.py` + `bestiario_quiu.py`):** `reptisaurio_arquero`, `reptisaurio_lancero`, `dromoraptor_verde`, `narval`, `fluviosaurus`, `zarinosa`, `kragtops`, `dactylo_adulto`, `chelonia`, `tyrannok`, `mastodino` y `espinosaurio`.
- **Monturas dinámicas (`con_silla=True`):** `narval` y `mastodino` exportan su silla y correas en la pieza hija `'silla'` (invisible en el retrato y activada en `BestiaModel.java` cuando `s.valor > 0.5F`, es decir, `isVehicle()`). El `Narval` tiene un 35 % de probabilidad de aparecer con un `Reptisaurio.Arquero` montado en postura `estado1`.
- **Sonidos, huevos, ataques y mecánicas (`bestiario_sonidos_reptiles.py`, `Reptiles.java`, `Fichas.java`):** todos integrados en el grupo `REPTILES`, con sus rótulos en `catalogo.py` y entregados en `entrega/atalaya-1.2.4.jar`.
