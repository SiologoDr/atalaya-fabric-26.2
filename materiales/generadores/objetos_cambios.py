"""
Los objetos de los cambios de dificultad (18-10-2026): la Píldora de la Plaga y las ayudas (la Bolsa del Vacío, el
Yunque Dorado, el Fruto del Recuerdo y la Raíz de Agua). Este script hace su textura (16 x 16, con el pincel de
ruleta.py), su modelo, su nombre en los dos idiomas y su receta (las de las ayudas se llaman cambio_<id del cambio>:
el mod solo las deja usar con su cambio encendido).

Uso: python objetos_cambios.py <raíz del proyecto>
"""
import collections
import json
import os
import sys

import numpy as np

import menus_cambios as mc
from ruleta import H, Lienzo, bisel, esfera, malla, rampa, sd_caja, sd_circulo, sd_elipse, sd_poligono, sd_segmento, tono, union

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
ASSETS = os.path.join(RAIZ, 'src/main/resources/assets/atalaya')
DATA = os.path.join(RAIZ, 'src/main/resources/data/atalaya')
OSCURO = mc.OSCURO


def pildora(n=16):
    """La Píldora de la Plaga: una cápsula partida en dos, verde podrido y hueso, con una calavera diminuta."""
    x, y, k = malla(n)
    L = Lienzo(n)
    eje = sd_segmento(x, y, 9, 23, 23, 9, 6.2)
    mitad = (x + y) < 32
    L.pintar((eje < 0) & mitad, tono(rampa('1e4a14', '3a7a22', '5aae34', '9ad864', 'd8ffb0'), esfera(x, y, 13, 13, 11, 11, amb=0.35)))
    L.pintar((eje < 0) & ~mitad, tono(rampa('6a6250', '9a9278', 'c8c0a4', 'ece4cc', 'fffaf0'), esfera(x, y, 13, 13, 11, 11, amb=0.35)))
    L.pintar((np.abs(x + y - 32) < 0.9) & (eje < 0), H('2a2418')[:3])
    for cx, cy in ((10.5, 14.5), (13.5, 11.5)):
        L.pintar(sd_circulo(x, y, cx, cy, 1.0) < 0, H('0e2a08')[:3])
    L.contorno(OSCURO)
    return L


def bolsa(n=16):
    """La Bolsa del Vacío: un saco de cuero morado oscuro, atado con cuerda, con el ojo de ender asomando."""
    x, y, k = malla(n)
    L = Lienzo(n)
    saco = union(sd_elipse(x, y, 16, 20, 10.5, 9.5), sd_poligono(x, y, [(10, 13), (22, 13), (19, 7), (13, 7)]))
    L.pintar(saco < 0, tono(rampa('140a22', '2a1640', '42245e', '603a80', '8a5aa8'), esfera(x, y, 13, 16, 12, 12, amb=0.3)))
    L.pintar(sd_caja(x, y, 16, 10.5, 7, 1.4, 0.5) < 0, H('c8a46a')[:3])
    L.pintar(sd_circulo(x, y, 16, 21, 4.6) < 0, tono(rampa('0a3a32', '13705e', '2fae8e', '7ae8c8', 'd8fff2'),
                                                     esfera(x, y, 15, 20, 4.6, 4.6, amb=0.25)))
    L.pintar(sd_elipse(x, y, 16, 21, 1.4, 2.8) < 0, H('06140f')[:3])
    L.pintar(sd_poligono(x, y, [(13, 7), (11, 3), (14.5, 5.5)]) < 0, H('42245e')[:3])
    L.pintar(sd_poligono(x, y, [(19, 7), (21, 3), (17.5, 5.5)]) < 0, H('42245e')[:3])
    L.contorno(OSCURO)
    return L


def yunque(n=16):
    """El Yunque Dorado: un yunque pequeño de oro macizo, con su bisel."""
    x, y, k = malla(n)
    L = Lienzo(n)
    forma = union(sd_caja(x, y, 15, 11, 12, 3.2, 1), sd_poligono(x, y, [(27, 8), (31, 10), (27, 14)]),
                  sd_caja(x, y, 16, 18, 4.5, 4.5, 0.5), sd_caja(x, y, 16, 25, 9.5, 3.2, 1))
    L.pintar(forma < 0, tono(mc.ORO, bisel(forma, k, 2.0 * k, base=0.6)))
    L.pintar(sd_caja(x, y, 13, 9.2, 8, 0.8) < 0, mc.ORO[5])
    L.contorno(H('3a2204')[:3])
    return L


def fruto(n=16):
    """El Fruto del Recuerdo: un fruto de piel violeta con vetas de luz y una hoja de cristal."""
    x, y, k = malla(n)
    L = Lienzo(n)
    d = union(sd_circulo(x, y, 13, 19, 8.5), sd_circulo(x, y, 19, 19, 8.5))
    L.pintar(d < 0, tono(rampa('2a0a3a', '561a70', '8a3aa8', 'c27ae0', 'f0d0ff'), esfera(x, y, 12, 15, 11, 11, amb=0.28)))
    for a in (-0.5, 0.0, 0.5):
        L.pintar((np.abs((x - 16) * np.cos(a) + (y - 19) * np.sin(a) * 0.3) < 0.6) & (d < -1.5), H('ffe0ff')[:3])
    L.pintar(sd_segmento(x, y, 16, 11, 17, 6, 1.0) < 0, H('5e3c18')[:3])
    L.pintar(sd_elipse(x, y, 21, 7, 4.2, 2.0) < 0, tono(rampa('3a8a8a', '6ad0d0', 'b0fffa'), np.clip(0.6 - (y - 7) * 0.1, 0, 1)))
    L.contorno(OSCURO)
    return L


def raiz(n=16):
    """La Raíz de Agua: un rábano blanco azulado, con gotas en la piel y las hojas arriba."""
    x, y, k = malla(n)
    L = Lienzo(n)
    cuerpo = union(sd_elipse(x, y, 16, 18, 6.5, 8), sd_poligono(x, y, [(13, 22), (19, 22), (16, 31)]))
    L.pintar(cuerpo < 0, tono(rampa('3a6a8a', '6aa0c0', 'a8d4ea', 'dcf2fc', 'ffffff'), esfera(x, y, 14, 15, 8, 9, amb=0.3)))
    for cx, cy in ((14, 16), (18, 20), (15, 22)):
        L.pintar(sd_circulo(x, y, cx, cy, 1.0) < 0, H('3a90d8')[:3])
    for a, b in (((16, 10), (10, 3)), ((16, 10), (16, 2)), ((16, 10), (22, 3))):
        L.pintar(sd_segmento(x, y, *a, *b, 1.6) < 0, H('3aa040')[:3])
    L.contorno(OSCURO)
    return L


def pildora_tamano(n=16):
    """La Píldora del Tamaño: una cápsula dorada y celeste con una flecha que sube."""
    x, y, k = malla(n)
    L = Lienzo(n)
    eje = sd_segmento(x, y, 9, 23, 23, 9, 6.2)
    mitad = (x + y) < 32
    L.pintar((eje < 0) & mitad, tono(mc.ORO, esfera(x, y, 13, 13, 11, 11, amb=0.35)))
    L.pintar((eje < 0) & ~mitad, tono(rampa('1a5a88', '3a90c0', '6ac8e6', 'aeeaf8', 'e2fbff'), esfera(x, y, 13, 13, 11, 11, amb=0.35)))
    L.pintar((np.abs(x + y - 32) < 0.9) & (eje < 0), H('2a2418')[:3])
    L.contorno(OSCURO)
    return L


OBJETOS = {
    # id: (dibujo, nombre, nombre en inglés)
    'pildora_plaga': (pildora, 'Píldora de la Plaga', 'Plague Pill'),
    'bolsa_vacio': (bolsa, 'Bolsa del Vacío', 'Void Bag'),
    'yunque_dorado': (yunque, 'Yunque Dorado', 'Golden Anvil'),
    'fruto_recuerdo': (fruto, 'Fruto del Recuerdo', 'Fruit of Remembrance'),
    'raiz_agua': (raiz, 'Raíz de Agua', 'Water Root'),
    'pildora_tamano': (pildora_tamano, 'Píldora del Tamaño', 'Size Pill'),
}

RECETAS = {
    # Se fabrica siempre (de dos en dos, como el «efecto placebo» del DEDsafío 3).
    'pildora_plaga': {'type': 'minecraft:crafting_shapeless',
                      'ingredients': ['minecraft:rotten_flesh', 'minecraft:spider_eye', 'minecraft:sugar',
                                      'minecraft:glistering_melon_slice'],
                      'result': {'id': 'atalaya:pildora_plaga', 'count': 2}},
    'cambio_bolsa_del_vacio': {'type': 'minecraft:crafting_shaped', 'pattern': ['LSL', 'LEL', 'LLL'],
                               'key': {'L': 'minecraft:leather', 'S': 'minecraft:string', 'E': 'minecraft:ender_eye'},
                               'result': {'id': 'atalaya:bolsa_vacio', 'count': 1}},
    'cambio_yunque_dorado': {'type': 'minecraft:crafting_shaped', 'pattern': ['BBB', ' i ', 'iii'],
                             'key': {'B': 'minecraft:gold_block', 'i': 'minecraft:iron_ingot'},
                             'result': {'id': 'atalaya:yunque_dorado', 'count': 1}},
    'cambio_fruto_del_recuerdo': {'type': 'minecraft:crafting_shapeless',
                                  'ingredients': ['minecraft:golden_apple', 'minecraft:ender_pearl',
                                                  'minecraft:amethyst_shard', 'minecraft:glow_berries'],
                                  'result': {'id': 'atalaya:fruto_recuerdo', 'count': 1}},
    'pildora_tamano': {'type': 'minecraft:crafting_shapeless',
                       'ingredients': ['minecraft:golden_apple', 'minecraft:golden_apple', 'minecraft:rabbit_foot',
                                       'minecraft:rabbit_foot', 'minecraft:sugar'],
                       'result': {'id': 'atalaya:pildora_tamano', 'count': 1}},
    'cambio_raiz_de_agua': {'type': 'minecraft:crafting_shapeless',
                            'ingredients': ['minecraft:beetroot', 'minecraft:kelp', 'minecraft:sugar'],
                            'result': {'id': 'atalaya:raiz_agua', 'count': 1}},
}


def escribir_json(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(datos, fh, indent=2, ensure_ascii=False)
        fh.write('\n')


def nombres(pares_es, pares_en):
    for idioma, pares in (('es_es', pares_es), ('en_us', pares_en)):
        ruta = os.path.join(ASSETS, f'lang/{idioma}.json')
        d = json.load(open(ruta, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        d.update(pares)
        escribir_json(ruta, d)


def main():
    es, en = {}, {}
    for ident, (fn, nombre, nombre_en) in OBJETOS.items():
        ruta = os.path.join(ASSETS, f'textures/item/{ident}.png')
        fn(16).imagen().save(ruta)
        escribir_json(os.path.join(ASSETS, f'items/{ident}.json'),
                      {'model': {'type': 'minecraft:model', 'model': f'atalaya:item/{ident}'}})
        escribir_json(os.path.join(ASSETS, f'models/item/{ident}.json'),
                      {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'atalaya:item/{ident}'}})
        es[f'item.atalaya.{ident}'] = nombre
        en[f'item.atalaya.{ident}'] = nombre_en
    nombres(es, en)
    for ident, receta in RECETAS.items():
        escribir_json(os.path.join(DATA, f'recipe/{ident}.json'), receta)
    print('ok', len(OBJETOS), 'objetos,', len(RECETAS), 'recetas')


if __name__ == '__main__':
    main()
