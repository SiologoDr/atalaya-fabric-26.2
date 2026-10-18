"""
Los menús de los cambios de dificultad y de las dimensiones (17-10-2026). Juan: «los quiero en un menú que ponga yo
/atalaya menu cambios ... un menú personalizado bonito, no el de Minecraft ... deben verse ON u OFF ... que haya un
buscador»; y otro para las dimensiones, «con ON y OFF en Nether y End». Son pantallas propias (MenuCambiosScreen y
MenuDimensionesScreen) con el mismo aire que la Ruleta: laca morada, oro y nuestra letra de píxel. Todo se pinta a un
texel por píxel de la interfaz, así que se ve nítido a cualquier escala. Este script hace, en
textures/gui/sprites/menu (el atlas de la interfaz):

  panel, fila, fila_encima, buscador  los fondos que se estiran (nine_slice): el marco de oro del panel, las filas de
                                      los cambios (y la que tiene el ratón encima) y el campo del buscador
  interruptor_on, _off, _espera       el interruptor con ON u OFF escrito, y el que espera a que pare la Ruleta
  lupa, candado                       la lupa del buscador y el candado de lo cerrado
  titulo_cambios, titulo_dimensiones  los títulos en nuestra letra, con el brillo que los cruza (animados)
  cambio/<id>                         el icono de cada cambio (16 x 16)
  nether, end                         las ilustraciones de las dimensiones (64 x 64, animadas)

y en textures/item los rótulos del chat de cada cambio (cambio_<id>_NN: su título en el estilo de los de la Ruleta).

Uso: python menus_cambios.py <raiz del proyecto>
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

import ruleta as r
from ruleta import (H, LETRA, TILDES, SIN_FILA, Lienzo, bisel, esfera, malla, malla_rect, rampa, sd_caja, sd_circulo,
                    sd_corazon, sd_poligono, sd_segmento, tono, union)

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
MENU = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/gui/sprites/menu')

# Los cambios de dificultad: id, título (el rótulo del chat y el del menú) y su icono. Los textos están en
# com.atalaya.cambios.Cambio.
CAMBIOS = {
    'ni_un_totem_mas': 'NI UN TÓTEM MÁS',
    'end_sellado': 'EL END, SELLADO',
    'vida_a_medias': 'VIDA A MEDIAS',
    'portales_arden': 'LOS PORTALES ARDEN',
}

LACA = rampa('0e0816', '1a0f26', '2a1a3a', '3b2650', '4e3466')
ORO = rampa('5a3608', '9a6214', 'd49a28', 'f2c64a', 'ffe58a', 'fff6d0')
OSCURO = np.array(H('0a0610')[:3], float)


def guardar(im, nombre, mcmeta=None):
    ruta = os.path.join(MENU, nombre + '.png')
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    im.save(ruta)
    if mcmeta is not None:
        with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(json.dumps(mcmeta, indent=2) + '\n')
    elif os.path.exists(ruta + '.mcmeta'):
        os.remove(ruta + '.mcmeta')


def nueve(w, h, borde):
    return {'gui': {'scaling': {'type': 'nine_slice', 'width': w, 'height': h, 'border': borde}}}


# ----------------------------------------------------------------------------------------------------------------
#  Los fondos que se estiran
# ----------------------------------------------------------------------------------------------------------------
def panel():
    """El panel: contorno oscuro, marco de oro con su bisel, un filete hondo y la laca dentro; en las esquinas, un
    remache en rombo. 48 x 48 con borde de 14 (el centro, liso, se repite)."""
    n = 48
    x, y = malla_rect(n, n)
    L = Lienzo(n)
    caja = sd_caja(x, y, n / 2, n / 2, n / 2 - 1, n / 2 - 1, 4)
    L.pintar(caja < 0, LACA[1])
    marco = (caja < -0.5) & (caja > -5.5)
    L.pintar(marco, tono(ORO, bisel(caja, 1.0, 2.2, base=0.6, fuerza=0.42)))
    L.pintar((caja <= -5.5) & (caja > -6.5), LACA[0])
    L.pintar((caja <= -6.5) & (caja > -7.5), ORO[1])
    for cx_, cy_ in ((7.5, 7.5), (n - 7.5, 7.5), (7.5, n - 7.5), (n - 7.5, n - 7.5)):
        rombo = np.abs(x - cx_) + np.abs(y - cy_)
        L.pintar(rombo < 3.6, OSCURO)
        L.pintar(rombo < 2.6, tono(ORO, np.clip(0.75 - (x - cx_ + y - cy_) * 0.12, 0, 1)))
    L.contorno(OSCURO)
    guardar(L.imagen(), 'panel', nueve(n, n, 14))


def fila(encima):
    """Una fila de la lista: una tarjeta de laca honda con un filo de oro (más vivo y más clara si el ratón está
    encima). 32 x 32 con borde de 6."""
    n = 32
    x, y = malla_rect(n, n)
    L = Lienzo(n)
    caja = sd_caja(x, y, n / 2, n / 2, n / 2, n / 2, 3)
    L.pintar(caja < 0, LACA[2] if encima else LACA[1] * 0.9 + LACA[0] * 0.1)
    L.pintar((caja < 0) & (caja > -1.0), ORO[4] if encima else ORO[1])
    L.pintar((caja <= -1.0) & (caja > -2.0) & (y < n / 2), LACA[3] if encima else LACA[2])
    guardar(L.imagen(), 'fila_encima' if encima else 'fila', nueve(n, n, 6))


def buscador():
    """El campo del buscador: hundido, oscuro y con su filo de oro. 16 x 16 con borde de 4."""
    n = 16
    x, y = malla_rect(n, n)
    L = Lienzo(n)
    caja = sd_caja(x, y, n / 2, n / 2, n / 2, n / 2, 2)
    L.pintar(caja < 0, LACA[0])
    L.pintar((caja < 0) & (caja > -1.0), ORO[2])
    L.pintar((caja <= -1.0) & (caja > -2.0) & (y < 4), OSCURO)
    guardar(L.imagen(), 'buscador', nueve(n, n, 4))


# ----------------------------------------------------------------------------------------------------------------
#  Las letras pequeñas (3 x 5) para el interruptor y la letra grande para los títulos
# ----------------------------------------------------------------------------------------------------------------
PEQUENA = {
    'O': ["###", "#.#", "#.#", "#.#", "###"],
    'N': ["#.#", "###", "###", "###", "#.#"],
    'F': ["###", "#..", "##.", "#..", "#.."],
    '.': ["...", "...", "...", "...", ".#."],
}


def letras_pequenas(L, texto, x0, y0, color):
    x = x0
    for c in texto:
        g = PEQUENA[c]
        for fy, fila_ in enumerate(g):
            for fx, ch in enumerate(fila_):
                if ch == '#':
                    L.rgb[y0 + fy, x + fx] = color
                    L.a[y0 + fy, x + fx] = 1.0
        x += len(g[0]) + 1


def interruptores():
    """El interruptor (34 x 16): OFF, la pista oscura con el pomo a la izquierda y OFF escrito; ON, la pista verde con
    el pomo a la derecha y ON escrito; y el de espera (mientras gira la Ruleta), dorado con el pomo en medio y tres
    puntos que se encienden por turnos (animado)."""
    W, Hh = 34, 16
    x, y = malla_rect(W, Hh)

    def base(color_pista, color_alto, pomo_x, cuadro=None):
        L = Lienzo(W, Hh)
        pista = sd_caja(x, y, W / 2, Hh / 2, W / 2 - 1, Hh / 2 - 1, 6.5)
        L.pintar(pista < 0, np.where((y < Hh / 2)[..., None], np.array(color_alto, float), np.array(color_pista, float)))
        L.pintar((pista < 0) & (pista > -1.0) & (y > Hh / 2), np.array(color_pista, float) * 0.6)
        pomo = sd_circulo(x, y, pomo_x, Hh / 2, 5.6)
        L.pintar(pomo < 0.8, OSCURO * 0 + np.array((0, 0, 0)), 0.35)
        L.pintar(pomo < 0, tono(rampa('8a8e9e', 'c8ccd8', 'eef0f6', 'ffffff'), esfera(x, y, pomo_x - 1, Hh / 2 - 1, 5.6, 5.6, amb=0.3)))
        L.contorno(OSCURO)
        return L

    off = base(H('2a2236')[:3], H('3a3048')[:3], 8.5)
    letras_pequenas(off, 'OFF', 17, 5, np.array(H('9a90aa')[:3], float))
    guardar(off.imagen(), 'interruptor_off')
    on = base(H('2f8a3c')[:3], H('4fbf5e')[:3], W - 8.5)
    letras_pequenas(on, 'ON', 7, 5, np.array(H('ffffff')[:3], float))
    guardar(on.imagen(), 'interruptor_on')
    # En espera: cuatro cuadros, los puntos se encienden uno a uno.
    hoja = Image.new('RGBA', (W, Hh * 4), (0, 0, 0, 0))
    for k in range(4):
        L = base(H('a87410')[:3], H('d8a420')[:3], W / 2)
        for i in range(3):
            c = H('fff2c0')[:3] if i == k % 3 else H('7a5408')[:3]
            px, py = 5 + i * 3, 10
            L.rgb[py:py + 2, px:px + 2] = c
            L.a[py:py + 2, px:px + 2] = 1.0
        hoja.paste(L.imagen(), (0, Hh * k))
    guardar(hoja, 'interruptor_espera', {'animation': {'frametime': 5, 'interpolate': False, 'width': W, 'height': Hh}})


def lupa():
    n = 10
    x, y = malla_rect(n, n)
    L = Lienzo(n)
    aro = np.abs(sd_circulo(x, y, 4.0, 4.0, 2.9)) - 0.9
    mango = sd_segmento(x, y, 6.2, 6.2, 8.6, 8.6, 1.0)
    L.pintar(union(aro, mango) < 0, ORO[3])
    L.pintar((aro < 0) & (y < 3.5) & (x < 4), ORO[5])
    L.contorno(OSCURO)
    guardar(L.imagen(), 'lupa')


def candado():
    """El candado de lo cerrado (16 x 16): el arco de cromo y el cuerpo de oro con su ojo."""
    n = 16
    x, y = malla_rect(n, n)
    L = Lienzo(n)
    arco = sd_segmento(x, y, 5, 8, 5, 5, 1.1)
    arco = union(arco, sd_segmento(x, y, 11, 8, 11, 5, 1.1),
                 np.abs(sd_circulo(x, y, 8, 5, 3.0)) - 1.1 + np.where(y > 5, 9, 0))
    L.pintar(arco < 0, tono(rampa('5a6478', '9aa4b8', 'd4dae6', 'ffffff'), np.clip(0.7 - (x - 8) * 0.08, 0, 1)))
    cuerpo = sd_caja(x, y, 8, 11, 5.5, 4, 1.2)
    L.pintar(cuerpo < 0, tono(ORO, bisel(cuerpo, 1.0, 1.5, base=0.6)))
    L.pintar(union(sd_circulo(x, y, 8, 10.3, 1.2), sd_caja(x, y, 8, 12.2, 0.5, 1.4)) < 0, OSCURO)
    L.contorno(OSCURO)
    guardar(L.imagen(), 'candado')


def texto_pixel(texto, esc, base, claro, oscuro, grueso=1):
    """El texto en nuestra letra a escala esc, en dos tonos planos (arriba más claro), con su contorno y su sombra:
    devuelve la máscara, el color y el alfa (para animarle el brillo)."""
    ancho = sum(len(LETRA[c][0]) * esc + grueso + esc for c in texto) - esc
    alto = 7 * esc
    W, Hh = ancho + 4, alto + 4
    dentro = np.zeros((Hh, W), bool)
    fila_de = np.zeros((Hh, W))
    xx = 1
    for c in texto:
        g = LETRA[c]
        tilde = TILDES.get(c)
        quita = SIN_FILA.get(c, 2)
        filas = g[:quita] + g[quita + 1:] if tilde else g
        dy0 = 1 + (esc if tilde else 0)
        for fy, fila_ in enumerate(filas):
            for fx, ch in enumerate(fila_):
                if ch == '#':
                    ya, xa = dy0 + fy * esc, xx + fx * esc
                    dentro[ya:ya + esc, xa:xa + esc + grueso] = True
                    fila_de[ya:ya + esc, xa:xa + esc + grueso] = (fy + (1 if tilde else 0)) / 6.0
        if tilde:
            m = max(1, esc // 2)
            cx_ = xx + (len(g[0]) * esc) // 2
            celdas = ((1, 0), (0, 1)) if tilde == 'tilde' else ((-2, 1), (-1, 0), (0, 1), (1, 0))
            for cxl, cyl in celdas:
                xa, ya = cx_ + cxl * m, 1 + cyl * m
                dentro[ya:ya + m, xa:xa + m] = True
        xx += len(g[0]) * esc + grueso + esc
    return dentro, fila_de, W, Hh


def titulo(texto, nombre, base, claro, oscuro, esc=2):
    """Un título del menú: el texto a escala 2 (14 de alto), con el brillo que lo cruza (animado como los rótulos del
    chat: 36 cuadros de 2 ticks, y el brillo cruza en los 22 primeros)."""
    dentro, fila_de, W, Hh = texto_pixel(texto, esc, base, claro, oscuro)
    contorno = np.zeros_like(dentro)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        contorno |= np.roll(np.roll(dentro, dy, 0), dx, 1)
    contorno &= ~dentro
    sombra = np.roll(np.roll(dentro | contorno, 1, 0), 1, 1) & ~(dentro | contorno)
    ys, xs = np.mgrid[0:Hh, 0:W]
    cuadros = r.CARTEL_CUADROS
    hoja = Image.new('RGBA', (W, Hh * cuadros), (0, 0, 0, 0))
    for f in range(cuadros):
        franja = -20 + (W + 40) * f / (r.CARTEL_CRUZA - 1) if f < r.CARTEL_CRUZA else -1000
        d = np.abs(xs - franja - ys * 0.55)
        luz = np.where(d < 5, np.clip(1 - d / 5, 0, 1) ** 1.2, 0.0)
        tono_ = np.where((fila_de < 0.45)[..., None], np.array(base) * 0.6 + np.array(claro) * 0.4, np.array(base, float))
        filo = dentro & ~np.roll(dentro, 1, 0)
        tono_ = np.where(filo[..., None], np.array(claro, float), tono_)
        tono_ = tono_ + (255 - tono_) * luz[..., None]
        im = np.zeros((Hh, W, 4), np.uint8)
        im[sombra] = (0, 0, 0, 120)
        im[contorno, :3] = oscuro
        im[contorno, 3] = 255
        im[dentro, :3] = np.clip(tono_[dentro], 0, 255)
        im[dentro, 3] = 255
        hoja.paste(Image.fromarray(im), (0, Hh * f))
    guardar(hoja, nombre, {'animation': {'frametime': 2, 'interpolate': False, 'width': W, 'height': Hh}})
    return W, Hh


# ----------------------------------------------------------------------------------------------------------------
#  Los iconos de los cambios (16 x 16, en el cuadro de 32 unidades del pincel de ruleta.py)
# ----------------------------------------------------------------------------------------------------------------
def icono_tachado(L, x, y):
    """La raya roja que tacha (de arriba a la derecha a abajo a la izquierda)."""
    T = Lienzo(L.a.shape[1])
    raya = sd_segmento(x, y, 26, 6, 6, 26, 2.4)
    T.pintar(raya < 0, H('e8322a')[:3])
    T.pintar((raya < -1.0) & (x + y < 32), H('ff7a60')[:3])
    T.contorno(H('3a0604')[:3])
    L.encima(T)


def icono_totem(n=16):
    """Ni un tótem más: un tótem de oro tachado."""
    x, y, k = malla(n)
    L = Lienzo(n)
    cuerpo = union(sd_caja(x, y, 16, 20, 5.5, 7.5, 2.0),            # el cuerpo
                   sd_circulo(x, y, 16, 9.5, 5.2),                   # la cabeza
                   sd_caja(x, y, 16, 16.5, 10.5, 2.4, 1.2))          # los brazos abiertos
    L.pintar(cuerpo < 0, tono(ORO, esfera(x, y, 14, 12, 12, 14, amb=0.3)))
    L.pintar(union(sd_circulo(x, y, 13.6, 9.6, 1.4), sd_circulo(x, y, 18.4, 9.6, 1.4)) < 0, H('2fbf6a')[:3])
    L.contorno(H('3a2204')[:3])
    icono_tachado(L, x, y)
    return L


def icono_end(n=16):
    """El End, sellado: el ojo de ender con un candado."""
    x, y, k = malla(n)
    L = Lienzo(n)
    ojo = sd_circulo(x, y, 14, 13, 10.5)
    L.pintar(ojo < 0, tono(rampa('0a3a32', '13705e', '2fae8e', '7ae8c8', 'd8fff2'), esfera(x, y, 14, 13, 10.5, 10.5, amb=0.2)))
    pupila = sd_caja(x, y, 14, 13, 2.2, 5.6, 2.0)
    L.pintar(pupila < 0, H('06140f')[:3])
    L.contorno(H('041810')[:3])
    C = Lienzo(n)
    arco = np.abs(sd_circulo(x, y, 23, 21, 3.6)) - 1.3 + np.where(y > 21, 9, 0)
    C.pintar(arco < 0, H('d4dae6')[:3])
    cuerpo = sd_caja(x, y, 23, 25.5, 6.2, 4.6, 1.2)
    C.pintar(cuerpo < 0, tono(ORO, bisel(cuerpo, k, 1.6 * k, base=0.62)))
    C.pintar(sd_circulo(x, y, 23, 25, 1.3) < 0, OSCURO)
    C.contorno(OSCURO)
    L.encima(C)
    return L


def icono_vida(n=16):
    """Vida a medias: un corazón con la mitad derecha vacía."""
    x, y, k = malla(n)
    L = Lienzo(n)
    d = sd_corazon(x, y, 16, 28.5, 22.5)
    lleno = (d < 0) & (x < 16)
    L.pintar(lleno, tono(rampa('6a0808', 'b8141a', 'e8322a', 'ff7a60', 'ffd0c8'), esfera(x, y, 12, 13, 12, 12, amb=0.25)))
    L.pintar((d < 0) & (x >= 16), H('2a1018')[:3])
    L.pintar((d < 0) & (d > -1.6 * k) & (x >= 16), H('5a2a32')[:3])
    L.contorno(H('1a0204')[:3])
    return L


def icono_portal(n=16):
    """Los portales arden: un portal del Nether, morado por dentro, con llamas encima."""
    x, y, k = malla(n)
    L = Lienzo(n)
    marco = sd_caja(x, y, 16, 18, 10, 12.5, 0.5)
    L.pintar(marco < 0, tono(rampa('0c0614', '1e1230', '3a2458'), np.clip(0.6 - (x - 16) * 0.03, 0, 1)))
    dentro_ = sd_caja(x, y, 16, 18.5, 6.4, 9, 0)
    rem = (np.sin((x - 16) * 0.55 + (y - 18) * 0.35) + np.cos((y - 18) * 0.6 - (x - 16) * 0.2)) * 0.25 + 0.55
    L.pintar(dentro_ < 0, tono(rampa('3a0a6a', '6a1ab0', 'a040f0', 'd890ff'), np.clip(rem, 0, 1)))
    L.contorno(OSCURO)
    F = Lienzo(n)
    llamas = union(sd_poligono(x, y, [(8, 6.5), (11, 0.5), (13, 6.5)]), sd_poligono(x, y, [(13, 6.5), (16.5, -0.5), (20, 6.5)]),
                   sd_poligono(x, y, [(19, 6.5), (22, 1.5), (25, 6.5)]))
    F.pintar(llamas < 0, H('ff9a2a')[:3])
    F.pintar(llamas < -1.4, H('ffe08a')[:3])
    F.contorno(H('5a1a04')[:3])
    L.encima(F)
    return L


ICONOS_CAMBIO = {'ni_un_totem_mas': icono_totem, 'end_sellado': icono_end, 'vida_a_medias': icono_vida,
                 'portales_arden': icono_portal}


# ----------------------------------------------------------------------------------------------------------------
#  Las ilustraciones de las dimensiones (64 x 64, animadas)
# ----------------------------------------------------------------------------------------------------------------
def nether():
    """El Nether: un portal de obsidiana con el remolino morado que gira (8 cuadros), sobre netherrack y con el
    brillo de la lava abajo."""
    n = 64
    x, y = malla_rect(n, n)
    cuadros = 8
    hoja = Image.new('RGBA', (n, n * cuadros), (0, 0, 0, 0))
    for f in range(cuadros):
        L = Lienzo(n)
        fondo = sd_caja(x, y, 32, 32, 31, 31, 6)
        cielo = np.clip(0.35 + (y - 10) / 80, 0, 1)
        L.pintar(fondo < 0, tono(rampa('1a0406', '3a0a0c', '5a1410', '8a2a14'), cielo))
        suelo = (y > 50) & (fondo < 0)
        rugoso = (np.floor(x / 4) + np.floor(y / 3) * 3) % 3 == 0
        L.pintar(suelo, np.where(rugoso[..., None], H('6a1a1a')[:3], H('8a2422')[:3]))
        L.pintar(suelo & (y < 52), H('c04a1a')[:3])
        marco = sd_caja(x, y, 32, 30, 15, 21, 0)
        L.pintar(marco < 0, tono(rampa('0a0612', '1a1028', '2e1e48', '44306a'),
                                 np.clip(0.45 + ((np.floor(x / 5) + np.floor(y / 5)) % 2) * 0.15 - (x - 32) * 0.01, 0, 1)))
        dentro_ = sd_caja(x, y, 32, 30.5, 9.5, 15.5, 0)
        ang = math.tau * f / cuadros
        rx, ry = x - 32, y - 30.5
        rem = np.sin(np.hypot(rx * 1.4, ry) * 0.55 - np.arctan2(ry, rx) * 2 + ang) * 0.5 + 0.5
        L.pintar(dentro_ < 0, tono(rampa('2a0656', '5212a0', '8a2ee0', 'c070ff', 'f0c8ff'), np.clip(rem * 0.85 + 0.1, 0, 1)))
        L.pintar(fondo >= -0.0, 0.0)
        L.contorno(OSCURO)
        im = L.imagen()
        hoja.paste(im, (0, n * f))
    guardar(hoja, 'nether', {'animation': {'frametime': 3, 'interpolate': False}})


def end():
    """El End: el marco del portal visto desde arriba (piedra del End con sus ojos) y, dentro, el negro con estrellas
    que titilan (8 cuadros)."""
    n = 64
    x, y = malla_rect(n, n)
    cuadros = 8
    rng = np.random.default_rng(3)
    estrellas = [(rng.uniform(20, 44), rng.uniform(20, 44), rng.uniform(0, math.tau)) for _ in range(16)]
    hoja = Image.new('RGBA', (n, n * cuadros), (0, 0, 0, 0))
    for f in range(cuadros):
        L = Lienzo(n)
        fondo = sd_caja(x, y, 32, 32, 31, 31, 6)
        L.pintar(fondo < 0, tono(rampa('0a0812', '141022', '1e1832'), np.clip(0.5 + (y - 32) / 120, 0, 1)))
        marco = np.maximum(sd_caja(x, y, 32, 32, 22, 22, 1), -sd_caja(x, y, 32, 32, 13, 13, 0))
        piedra = rampa('8a8a5a', 'c8c890', 'e8e8b0', 'fafad0')
        L.pintar(marco < 0, tono(piedra, np.clip(0.55 + ((np.floor(x / 9) + np.floor(y / 9)) % 2) * 0.12 - (x + y - 64) * 0.004, 0, 1)))
        for cx_, cy_ in ((22.5, 13.5), (32.5, 13.5), (42.5, 13.5), (22.5, 51.5), (32.5, 51.5), (42.5, 51.5),
                         (13.5, 22.5), (13.5, 32.5), (13.5, 42.5), (51.5, 22.5), (51.5, 32.5), (51.5, 42.5)):
            ojo = sd_circulo(x, y, cx_, cy_, 2.6)
            L.pintar(ojo < 0, tono(rampa('0a3a32', '2fae8e', '7ae8c8'), esfera(x, y, cx_ - 0.6, cy_ - 0.6, 2.6, 2.6, amb=0.3)))
            L.pintar(sd_circulo(x, y, cx_, cy_, 0.9) < 0, H('06140f')[:3])
        hueco = sd_caja(x, y, 32, 32, 13, 13, 0)
        L.pintar(hueco < 0, H('04020a')[:3])
        for sx, sy, fase in estrellas:
            b = 0.5 + 0.5 * math.sin(fase + math.tau * f / cuadros)
            c = np.array((120 + 135 * b, 200 + 55 * b, 190 + 65 * b))
            L.pintar(sd_circulo(x, y, int(sx) + 0.5, int(sy) + 0.5, 0.6 + 0.5 * b) < 0, c)
        L.pintar(fondo >= 0.0, 0.0)
        L.contorno(OSCURO)
        hoja.paste(L.imagen(), (0, n * f))
    guardar(hoja, 'end', {'animation': {'frametime': 4, 'interpolate': False}})


# ----------------------------------------------------------------------------------------------------------------
#  Los rótulos del chat de cada cambio (su título, en el estilo de los de la Ruleta y del color de la dificultad)
# ----------------------------------------------------------------------------------------------------------------
def rotulos_cambios():
    carpeta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')
    for ident, texto in CAMBIOS.items():
        cuadros_img = r.rotulo(texto, 'dificultad', r.ROTULO)
        n = cuadros_img[0].width // 32
        for viejo in os.listdir(carpeta):
            if viejo.startswith(f'cambio_{ident}_'):
                os.remove(os.path.join(carpeta, viejo))
        for i in range(n):
            tira = Image.new('RGBA', (32, 32 * len(cuadros_img)), (0, 0, 0, 0))
            for k, im in enumerate(cuadros_img):
                tira.paste(im.crop((i * 32, 0, i * 32 + 32, 32)), (0, k * 32))
            ruta = os.path.join(carpeta, f'cambio_{ident}_{i:02d}.png')
            tira.save(ruta)
            with open(ruta + '.mcmeta', 'w', encoding='utf-8', newline='\n') as fh:
                json.dump({'animation': {'frametime': 2, 'interpolate': False}}, fh, indent=2)
                fh.write('\n')
        print(f'rotulo {ident}: {n} cuadros')


def main():
    os.makedirs(MENU, exist_ok=True)
    panel()
    fila(False)
    fila(True)
    buscador()
    interruptores()
    lupa()
    candado()
    amarillo = ((255, 210, 58), (255, 241, 176), (60, 40, 0))
    print('titulo_cambios', titulo('CAMBIOS DE DIFICULTAD', 'titulo_cambios', *amarillo))
    print('titulo_dimensiones', titulo('DIMENSIONES', 'titulo_dimensiones', (196, 150, 255), (240, 224, 255), (30, 10, 50)))
    for ident, fn in ICONOS_CAMBIO.items():
        guardar(fn(16).imagen(), f'cambio/{ident}')
    nether()
    end()
    rotulos_cambios()
    print('ok')


if __name__ == '__main__':
    main()
