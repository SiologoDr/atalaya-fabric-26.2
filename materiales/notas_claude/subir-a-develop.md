---
name: subir-a-develop
description: "Cuando Juan pide subir los cambios, van directos a la rama develop; no crear ramas aparte"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-19T04:39:27.307Z
---

Cuando Juan dice «sube los cambios», se hace commit y push directamente en `develop` (su rama de trabajo; `main` le llega por PR). El 18-10-2026 los subí a una rama nueva y me corrigió: «ojo, sube todo a la rama develop, no que crearas una rama».

**Why:** trabaja él solo en `develop` y la usa para continuar en otras máquinas (`git pull`).

**How to apply:** solo cuando lo pida (ver [[entrega-solo-cuando-lo-pida]]); commit en `develop` y `git push origin develop`, sin ramas nuevas ni PR salvo que lo pida.
