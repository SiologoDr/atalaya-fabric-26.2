---
name: cambios-de-dificultad
description: "Menús propios de cambios de dificultad (/atalaya menu cambios) y de dimensiones; ON lanza la Ruleta y se aplica con su aviso; títulos y textos nuestros, no los de DEDsafío"
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-18T02:39:21.652Z
---

El 17-10-2026 Juan pidió los cambios de dificultad en **un menú propio y bonito, no el de Minecraft**
(`/atalaya menu cambios`), con buscador y ON/OFF visible:
- **OFF → ON:** sale la Ruleta (final de dificultad) y el cambio **se aplica al salir su aviso**. El rótulo del chat es
  **el título del cambio**, no «CAMBIO DE DIFICULTAD».
- **ON → OFF:** se quita al momento, sin animación («no se hace nada, solo se desactiva»).
- Otro menú, `/atalaya menu dimensiones`, con ON/OFF para el Nether y el End.

Los primeros cuatro venían de DEDsafío 2 y pidió **título y texto propios** («cámbialo para que no sea lo mismo»):
NI UN TÓTEM MÁS (evocadores sin tótem), EL END, SELLADO, VIDA A MEDIAS (media vida 30 min) y LOS PORTALES ARDEN (abre
el Nether). Juan los irá dictando: «todos los cambios de dificultad que te diga».

Código: `Cambio` (la lista), `CambiosDificultad` (SavedData y efectos), `PortalCerradoMixin`, `MenuCambiosScreen`,
`MenuDimensionesScreen`; arte en `menus_cambios.py`; README «Los cambios de dificultad».

**Why:** es el sistema diario del evento ([[serie-tipo-dedsafio]]), unido a la [[ruleta-cambios-de-dificultad]].

**How to apply:** cada cambio nuevo que dicte va en `Cambio` con título y texto nuestros (aunque lo saque de DEDsafío),
su icono y su rótulo en `menus_cambios.py` y su efecto en `CambiosDificultad`. Apagar un cambio debe deshacerlo (y las
dimensiones vuelven a como estaban). Probar con `FotosPrueba` (`CLIC`, `BUSCA`, `CERRAR`). Ver
[[todo-propio-sin-vanilla]].
