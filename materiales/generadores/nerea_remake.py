"""
El antes y el despues del remake de Nerea, Guardian de los Mares (octubre de
2026), para la ficha (nerea_remake_escenas.py). No escribe nada en el repo.

  - antes:   la malla de antes del remake, tal como estaba (nerea_juego_v1.py,
             la copia que se guardo al pasar el remake al juego), a x1,6.
  - despues: la malla del juego (nerea_juego.py, que ya lleva el remake), a x2,4.

Lo que cambio con el remake (lo construye nerea_juego.py, en _remake()):
  - Tamano: de unos 10 bloques a unos 15 (el renderer escala x2,4 en vez de x1,6).
  - La CONCHA: un abanico de venera detras de la cabeza, de nacar, con el filo
    encendido y una perla que brilla en el centro (el halo de un dios del mar).
  - La CORONA: puas de prismarina y cuernos de coral mucho mas largos.
  - La BARBA y la CAPA de algas; tres ESPINAS de hueso por el lomo.
  - La CARACOLA de hombrera; hombreras, brazos y piernas mas gruesos.
  - El ANCLA: el gancho de la cadena-latigo pasa a ser un ancla de verdad.
  - El TRIDENTE: mas largo, con las puntas mas grandes y una espiral de espuma.

Antes, este fichero construia el remake encima de nerea_juego.py; desde que el
remake esta en el juego eso lo aplicaba dos veces.

Uso: import nerea_remake as nr; nr.usar('antes') / nr.usar('despues') y despues
nerea_juego.quads(...) con nr.ESCALA[cual].
"""
import os
os.environ.setdefault('NEREA_SIN_FISICA', '1')
import nerea_juego as nj
import nerea_juego_anim as nja      # construye la malla del juego y sus poses
import nerea_juego_v1 as nj1

ESCALA = {'antes': 1.6, 'despues': 2.4}

# Las dos mallas: la de antes la construye su propio modulo (con sus mismos
# materiales, que nerea_juego.py tambien tiene) y la del juego, nerea_juego.py.
nj1.construir()
_ANTES = (nj1.PARTES, nj1.ORDEN)
_DESPUES = (nj.PARTES, nj.ORDEN)


def usar(cual):
    """Cambia la malla que usan las funciones de nerea_juego (quads, matrices...)."""
    nj.PARTES, nj.ORDEN = _ANTES if cual == 'antes' else _DESPUES


# ----------------------------------------------------------------------
#  Atlas de cada una (la espuma lleva el color de las puntas de la fase)
# ----------------------------------------------------------------------
_ATLAS = {}


def atlas(cual, fase):
    k = (cual, fase)
    if k not in _ATLAS:
        usar(cual)
        nj.BRILLO['espuma'] = nj.PUNTAS_FASE[fase] if fase in nj.PUNTAS_FASE else nj.BRILLO['espuma']
        uv, alto = nj.empaquetar()
        base, brillo, libre = nj.pintar_atlas(uv, alto, fase if fase != 'libre' else 1)
        if fase == 'libre':
            brillo = libre
        _ATLAS[k] = (base, brillo, uv, alto)
    return _ATLAS[k]
