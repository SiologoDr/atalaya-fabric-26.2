"""
La familia de Quiu del bestiario (DEDsafío 4), recreada pieza a pieza sobre los iconos del libro del juego, los carteles
oficiales y los fotogramas de los directos (módulos en `materiales/generadores/quiu/`):

  reptisaurio_arquero   «Atacante a distancia: utiliza su arco para alejar a los intrusos.» Veneno Primitivo.
  reptisaurio_lancero   «Combatiente con lanza.» Veneno Primitivo.
  dromoraptor_verde     En manada; su mordisco aplica Veneno II durante 2 segundos.
  narval                Depredador acuático; embiste y empuja a gran velocidad (y puede llevar un Arquero de jinete).
  fluviosaurus          Semiacuático; trepa paredes y rompe bloques al perseguir.
  zarinosa              Zarinosa Espigüeya: salta a la cabeza del jugador, ciega y drena vida hasta que otro la quita.
  kragtops              Coloso acorazado neutral; embiste con los cuernos y golpea con la maza de la cola.
  dactylo_adulto        Depredador volador; se lanza en picado, agarra al jugador con las garras, lo sube y lo suelta.
  chelonia              Tortuga acorazada con cristales; muerde, dispara cristales y se esconde en su caparazón.
  tyrannok              Gran depredador bípedo dorado; destruye todo a su paso y aplica Lentitud.
  mastodino             Gran depredador bípedo rojo de púas moradas; destruye todo a su paso e impulsa hacia arriba.
  espinosaurio          Gran depredador bípedo de vela de discos; destruye todo a su paso y aplica Veneno.

Uso: python bestiario_quiu.py <raíz> [carpeta de las vistas] [ids]
"""
import math
import os
import sys

import numpy as np

import bestiario as B
import bestiario_creepers as bc
import bestiario_reptiles as R
from bestiario import T
from bestiario_reptiles import _con_cara, agrandar

from quiu import (
    chelonia,
    dactylo_adulto,
    dromoraptor_verde,
    espinosaurio,
    fluviosaurus,
    kragtops,
    mastodino,
    narval,
    reptisaurio_arquero,
    reptisaurio_lancero,
    tyrannok,
    zarinosa,
)


def sagital(x, y, z, alto=0.0):
    """El marco de una lámina de perfil (en el plano YZ), en (x, y, z)."""
    return T(x, y, z) @ B.girar((alto, 90, 0))


def ojo_en(nombre, piel, cara, patron, fx, fy, colores):
    """La piel con un ojo ('patron', a 32 por bloque y sin estirar) en las dos caras de lado de una caja."""
    W, H_ = int(round(cara[0] * 2)), int(round(cara[1] * 2))
    filas = [['.'] * W for _ in range(H_)]
    x0, y0 = int(round(fx * W)), int(round(fy * H_))
    for j, fila in enumerate(patron):
        for i, ch in enumerate(fila):
            if ch != '.' and 0 <= y0 + j < H_ and 0 <= x0 + i < W:
                filas[y0 + j][x0 + i] = ch
    mapa = [''.join(f) for f in filas]
    return _con_cara(nombre, piel, {'izq': mapa, 'der': mapa}, colores, fino=True)


def quijada(m, padre, gozne, abre):
    """La parte de la mandíbula y el marco donde van sus cajas, abierto 'abre' grados desde el gozne."""
    m.parte('mandibula', padre, tuple(gozne))
    return T(*gozne) @ B.girar((abre, 0, 0))


MODULOS = (
    reptisaurio_arquero,
    reptisaurio_lancero,
    dromoraptor_verde,
    narval,
    fluviosaurus,
    zarinosa,
    kragtops,
    dactylo_adulto,
    chelonia,
    tyrannok,
    mastodino,
    espinosaurio,
)

for _mod in MODULOS:
    R.TAM[_mod.ID] = _mod.TAM


def _huevo(mod):
    piel, contorno, puntos = mod.HUEVO
    return (piel, contorno, R._puntos(puntos))


R.EN_JUEGO.update({
    'reptisaurio_arquero': (
        'Reptisaurio Arquero', 'Reptisaur Archer',
        _huevo(reptisaurio_arquero),
        (('veneno', bc.gota((120, 200, 60))), ('pluma', bc.esquirla((40, 178, 168)))),
    ),
    'reptisaurio_lancero': (
        'Reptisaurio con Lanza', 'Reptisaur Lancer',
        _huevo(reptisaurio_lancero),
        (('veneno', bc.gota((120, 200, 60))), ('astilla', bc.esquirla((182, 164, 108)))),
    ),
    'dromoraptor_verde': (
        'Dromoraptor Verde', 'Green Dromoraptor',
        _huevo(dromoraptor_verde),
        (('veneno', bc.gota((120, 200, 60))), ('pluma', bc.esquirla((174, 28, 140))),
         ('escama', bc.esquirla((82, 144, 30)))),
    ),
    'narval': (
        'Narval', 'Narwhal',
        _huevo(narval),
        (('espuma', bc.gota((200, 224, 255))), ('escama', bc.esquirla((36, 54, 123)))),
    ),
    'fluviosaurus': (
        'Fluviosaurus', 'Fluviosaurus',
        _huevo(fluviosaurus),
        (('gota', bc.gota((214, 70, 126))), ('escama', bc.esquirla((48, 86, 150)))),
    ),
    'zarinosa': (
        'Zarinosa Espigüeya', 'Spiketail Zarinosa',
        _huevo(zarinosa),
        (('espora', bc.esquirla((212, 184, 48))), ('escama', bc.esquirla((68, 124, 36)))),
    ),
    'kragtops': (
        'Kragtops', 'Kragtops',
        _huevo(kragtops),
        (('polvo', bc.esquirla((122, 114, 98))), ('esquirla', bc.esquirla((106, 142, 198)))),
    ),
    'dactylo_adulto': (
        'Dáctylo Adulto', 'Adult Dactylo',
        _huevo(dactylo_adulto),
        (('chispa', bc.chispa((240, 156, 36))), ('pluma', bc.esquirla((200, 62, 28)))),
    ),
    'chelonia': (
        'Chelonia', 'Chelonia',
        _huevo(chelonia),
        (('cristal', bc.esquirla((120, 220, 248))), ('hoja', bc.esquirla((62, 128, 38)))),
    ),
    'tyrannok': (
        'Tyrannok', 'Tyrannok',
        _huevo(tyrannok),
        (('polvo', bc.esquirla((180, 148, 82))), ('escama', bc.esquirla((212, 162, 62)))),
    ),
    'mastodino': (
        'Mastodino', 'Mastodino',
        _huevo(mastodino),
        (('polvo', bc.esquirla((168, 132, 108))), ('pua', bc.esquirla((90, 12, 192)))),
    ),
    'espinosaurio': (
        'Espinosaurio', 'Spinosaurus',
        _huevo(espinosaurio),
        (('veneno', bc.gota((120, 200, 60))), ('escama', bc.esquirla((42, 112, 91)))),
    ),
})


def _caja_envolvente(m):
    pts = []
    for p in m.partes.values():
        for c in p.cajas:
            M, x0, y0, z0, w, h, d = c[:7]
            for dx in (0, w):
                for dy in (0, h):
                    for dz in (0, d):
                        pts.append((M @ np.array((x0 + dx, y0 + dy, z0 + dz, 1.0)))[:3])
    pts = np.array(pts) / 16.0
    return pts.min(0), pts.max(0)


def al_juego_quiu(mod, raiz):
    """Exporta el modelo (con la pieza 'silla' en Narval y Mastodino para cuando lleven jinete), su huevo, nombres,
    el retrato del menú encuadrado a su caja envolvente y sus partículas."""
    con_silla = mod.ID in ('narval', 'mastodino')
    m = agrandar(mod.construir(con_silla=True) if con_silla else mod.construir(), mod.TAM)
    m.exportar(raiz)
    nombre_es, nombre_en, (piel, contorno, dib), particulas = R.EN_JUEGO[m.id]
    B.huevo(m.id, piel, contorno, dib)
    B.objeto(m.id, nombre_es, nombre_en)
    silla_p = m.partes.pop('silla', None)
    lo, hi = _caja_envolvente(m)
    c = (lo + hi) / 2.0
    ext = float((hi - lo).max())
    fov = 34.0
    r = ext * 0.5 / math.tan(math.radians(fov) / 2.0) * 1.12
    a, e = math.radians(-42.0), math.radians(18.0)
    ojo = c + r * np.array((math.cos(e) * math.sin(a), math.sin(e), math.cos(e) * math.cos(a)))
    B.retrato(m, ojo=tuple(ojo), objetivo=tuple(c), fov=fov)
    if silla_p is not None:
        m.partes['silla'] = silla_p
    for nombre, cuadros in particulas:
        B.particula(m.id, nombre, cuadros)
    return m


MOBS = {mod.ID: mod for mod in MODULOS}


def main():
    raiz = sys.argv[1] if len(sys.argv) > 1 else '../..'
    B.RAIZ = raiz
    carpeta = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] not in ('-', '') else None
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    pedidos = sys.argv[3].split(',') if len(sys.argv) > 3 else list(MOBS)
    B.TEXEL = 1.0
    for p in pedidos:
        m = al_juego_quiu(MOBS[p], raiz)
        if carpeta:
            m.hoja_vistas(os.path.join(carpeta, f'{m.id}.png'),
                          poses=[('reposo', 0.25), ('andar', 0.3), ('ataque', 0.2), ('muerte', 0.8)])
    B.TEXEL = None


if __name__ == '__main__':
    main()
