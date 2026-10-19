"""
El catálogo del evento (18-10-2026): los tres menús (cambios de dificultad, nuevos mobs y momentos) y lo que sale en el
chat al encender cada cosa. Juan: «categorízalo bien ... el cambio de dificultad de 30 min a mitad de vida sería un
momento fractura, es decir, sería en otro menú»; y «quiero todo en el juego».

Lo que hay en cada lista se lee del propio mod (una sola fuente): com.atalaya.cambios.Cambio, com.atalaya.momento.Momento
y com.atalaya.bestiario.Fichas (su id y su título). Este script hace:

  textures/gui/sprites/menu/
    titulo_cambios, titulo_mobs, titulo_momentos   los títulos de los menús, en nuestra letra y con el brillo que pasa
    pestana, pestana_activa                        las pestañas de arriba (para pasar de un menú a otro)
    cambio/<id>, momento/<id>                      el icono de cada uno (16 x 16; catalogo_iconos.py)
    (mob/<id>, el retrato de 32 x 32 de cada mob, lo hace bestiario_juego.py)
  textures/item/
    cambio_<id>_NN    el rótulo del chat de cada cambio (su título, del amarillo de la dificultad)
    mob_<id>_NN       el de cada mob (del naranja del huevo)
  carteles.json       cuántos cuadros tiene cada rótulo (lo lee Carteles en el mod)

Los momentos no llevan rótulo propio: los presenta el Momento Fractura (su cinemática dice el título y el chat,
«MOMENTO FRACTURA:» y el texto).

Uso: python catalogo.py <raíz del proyecto>
"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image

import menus_cambios as mc
import ruleta as r
from ruleta import H, Lienzo, malla_rect, rampa, sd_caja, tono

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
JAVA = os.path.join(RAIZ, 'src/main/java/com/atalaya')
ASSETS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
MENU = os.path.join(ASSETS, 'textures/gui/sprites/menu')
ITEM = os.path.join(ASSETS, 'textures/item')
mc.MENU = MENU
mc.RAIZ = RAIZ


# ----------------------------------------------------------------------------------------------------------------
#  Lo que hay en cada lista (del código del mod)
# ----------------------------------------------------------------------------------------------------------------
def _cadena(s):
    """Una cadena de Java (con sus escapes y, si va partida en varias líneas con +, junta)."""
    partes = re.findall(r'"((?:[^"\\]|\\.)*)"', s)
    return ''.join(p.encode('latin-1', 'backslashreplace').decode('unicode_escape') if '\\u' in p else p for p in partes)


def cambios():
    """(id, título) de cada cambio, en el orden del enum."""
    src = open(os.path.join(JAVA, 'cambios/Cambio.java'), encoding='utf-8').read()
    return [(m.group(1), m.group(2)) for m in
            re.finditer(r'^\s+[A-Z_0-9]+\("([a-z_0-9]+)",\s*Grupo\.[A-Z_]+,\s*"([^"]+)"', src, re.M)]


def momentos():
    src = open(os.path.join(JAVA, 'momento/Momento.java'), encoding='utf-8').read()
    return [(m.group(1), m.group(2)) for m in
            re.finditer(r'^\s+[A-Z_0-9]+\("([a-z_0-9]+)",\s*Grupo\.[A-Z_]+,\s*"([^"]+)"', src, re.M)]


def mobs():
    """(id, título) de cada mob del bestiario: Bestias.nueva("id", ...) y su .titulo("TÍTULO", ...)."""
    src = open(os.path.join(JAVA, 'bestiario/Fichas.java'), encoding='utf-8').read()
    out = []
    for m in re.finditer(r'nueva\("([a-z_0-9]+)"[^;]*?\.titulo\("([^"]+)"', src, re.S):
        out.append((m.group(1), m.group(2)))
    return out


# ----------------------------------------------------------------------------------------------------------------
#  Las pestañas
# ----------------------------------------------------------------------------------------------------------------
def pestanas():
    """Las pestañas de arriba (24 x 16, borde 5): la apagada, laca honda con el filo de oro viejo; la del menú abierto,
    más clara, con el filo de oro vivo y una raya de luz abajo."""
    W, Hh = 24, 16
    x, y = malla_rect(W, Hh)
    for activa in (False, True):
        L = Lienzo(W, Hh)
        caja = sd_caja(x, y, W / 2, Hh / 2, W / 2, Hh / 2, 3)
        L.pintar(caja < 0, mc.LACA[2] if activa else mc.LACA[0])
        L.pintar((caja < 0) & (caja > -1.0), mc.ORO[4] if activa else mc.ORO[1])
        if activa:
            L.pintar((caja <= -1.0) & (caja > -2.0) & (y < Hh / 2), mc.LACA[3])
            L.pintar((y > Hh - 3) & (y < Hh - 1.5) & (np.abs(x - W / 2) < W / 2 - 3), mc.ORO[3])
        mc.guardar(L.imagen(), 'pestana_activa' if activa else 'pestana', mc.nueve(W, Hh, 5))


# ----------------------------------------------------------------------------------------------------------------
#  Los rótulos del chat
# ----------------------------------------------------------------------------------------------------------------
def rotulo(nombre, texto, final, carteles):
    """El rótulo del chat de una entrada: su título en el estilo de los de la Ruleta, en cuadros de 32 x 32 animados
    (item/<nombre>_NN). Apunta cuántos cuadros tiene."""
    cuadros_img = r.rotulo(texto, final, r.ROTULO)
    n = cuadros_img[0].width // 32
    for viejo in os.listdir(ITEM):
        if re.fullmatch(re.escape(nombre) + r'_\d\d\.png(\.mcmeta)?', viejo):
            os.remove(os.path.join(ITEM, viejo))
    for i in range(n):
        tira = Image.new('RGBA', (32, 32 * len(cuadros_img)), (0, 0, 0, 0))
        for k, im in enumerate(cuadros_img):
            tira.paste(im.crop((i * 32, 0, i * 32 + 32, 32)), (0, k * 32))
        ruta = os.path.join(ITEM, f'{nombre}_{i:02d}.png')
        tira.save(ruta)
        with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'animation': {'frametime': 2, 'interpolate': False}}, fh, indent=2)
            fh.write('\n')
    carteles[nombre] = n
    return n


def hud_cambios():
    """Los iconos del HUD de los cambios (16 x 16 en el atlas de la interfaz: hud/plaga y hud/insomnio) y el del
    efecto Deslumbrado (18 x 18, textures/mob_effect)."""
    import catalogo_iconos as ci
    import catalogo_iconos_cambios  # noqa: F401 (apunta los iconos)
    hud = os.path.join(ASSETS, 'textures/gui/sprites/hud')
    os.makedirs(hud, exist_ok=True)
    ci.ICONOS['cambio/la_plaga'](16).imagen().save(os.path.join(hud, 'plaga.png'))
    ci.ICONOS['cambio/insomnio'](16).imagen().save(os.path.join(hud, 'insomnio.png'))
    ci.ICONOS['cambio/no_mires_al_sol'](18).imagen().save(os.path.join(ASSETS, 'textures/mob_effect/deslumbrado.png'))
    import catalogo_iconos_momentos  # noqa: F401
    ci.ICONOS['momento/el_intercambio'](18).imagen().save(os.path.join(ASSETS, 'textures/mob_effect/vida_oculta.png'))


def hoja(carpeta, lista, prefijo):
    """Una hoja con todos los iconos de una lista (para revisarlos de un vistazo), a 4x."""
    import catalogo_iconos as ci
    cols = 8
    filas = max(1, (len(lista) + cols - 1) // cols)
    im = Image.new('RGBA', (cols * 76, filas * 76), (36, 28, 48, 255))
    for i, (ident, _) in enumerate(lista):
        fn = ci.ICONOS.get(f'{prefijo}/{ident}', ci.icono_falta)
        ic = fn(16).imagen().resize((64, 64), Image.NEAREST)
        im.paste(ic, ((i % cols) * 76 + 6, (i // cols) * 76 + 6), ic)
    im.save(os.path.join(carpeta, f'hoja_{prefijo}.png'))


def main():
    import catalogo_iconos as ci
    import catalogo_iconos_cambios  # noqa: F401 (apunta los iconos de los cambios)
    import catalogo_iconos_momentos  # noqa: F401 (y los de los momentos)
    os.makedirs(MENU, exist_ok=True)
    mc.panel()
    mc.fila(False)
    mc.fila(True)
    mc.buscador()
    mc.interruptores()
    mc.lupa()
    mc.candado()
    pestanas()
    # Los títulos de los menús, cada uno del color de su lista: el amarillo de los cambios, el naranja del huevo y
    # el rojo del Momento Fractura.
    tamanos = {
        'cambios': mc.titulo('CAMBIOS DE DIFICULTAD', 'titulo_cambios', (255, 210, 58), (255, 241, 176), (60, 40, 0)),
        'mobs': mc.titulo('NUEVOS MOBS', 'titulo_mobs', (255, 154, 60), (255, 216, 168), (64, 22, 2)),
        'momentos': mc.titulo('MOMENTOS', 'titulo_momentos', (255, 90, 74), (255, 206, 196), (60, 6, 4)),
        'dimensiones': mc.titulo('DIMENSIONES', 'titulo_dimensiones', (196, 150, 255), (240, 224, 255), (30, 10, 50)),
    }
    mc.nether()
    mc.end()
    carteles = {}
    lista_c, lista_m, lista_b = cambios(), momentos(), mobs()
    sin_icono = []
    for ident, titulo in lista_c:
        rotulo(f'cambio_{ident}', titulo, 'dificultad', carteles)
        fn = ci.ICONOS.get(f'cambio/{ident}')
        if fn is None:
            sin_icono.append(f'cambio/{ident}')
            fn = ci.icono_falta
        mc.guardar(fn(16).imagen(), f'cambio/{ident}')
    for ident, titulo in lista_m:
        fn = ci.ICONOS.get(f'momento/{ident}')
        if fn is None:
            sin_icono.append(f'momento/{ident}')
            fn = ci.icono_falta
        mc.guardar(fn(16).imagen(), f'momento/{ident}')
    for ident, titulo in lista_b:
        rotulo(f'mob_{ident}', titulo, 'mob', carteles)
    hud_cambios()
    if len(sys.argv) > 2:
        hoja(sys.argv[2], lista_c, 'cambio')
        hoja(sys.argv[2], lista_m, 'momento')
    with open(os.path.join(ASSETS, 'carteles.json'), 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(dict(sorted(carteles.items())), fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print('titulos (ancho x alto):', tamanos)
    print(len(lista_c), 'cambios,', len(lista_m), 'momentos,', len(lista_b), 'mobs;', len(carteles), 'rotulos')
    if sin_icono:
        print('SIN ICONO TODAVIA:', ', '.join(sin_icono))


if __name__ == '__main__':
    main()
