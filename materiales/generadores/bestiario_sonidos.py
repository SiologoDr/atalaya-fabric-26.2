"""
Los sonidos del bestiario: las mismas utilidades de minijefes_sonidos.py (la física de cada material, las voces, las
salas), con los nombres de los mobs nuevos: el evento bestia.<id>.<nombre> y los archivos en sounds/bestia/<id>/.

  empezar(id)                          borra los de antes de ese mob y empieza a apuntar los suyos
  guardar(nombre, x, variante, ...)    lo guarda (como ms.guardar)
  subtitulos(id, {nombre: (es, en)})   lo que dice el subtítulo de cada uno
  escribir_json()                      sounds.json y los subtítulos de los dos idiomas (solo los del bestiario)
"""
import collections
import json
import os

import minijefes_sonidos as ms

EVENTOS = collections.OrderedDict()
SUBTITULOS = {}
_ACTUAL = [None]


def empezar(ident, sala=('plaza', 6000)):
    """Empieza los de ese mob, con su sala (la reverberación: 'plaza', 'cumbre', 'abismo' o 'volcan', y su brillo)."""
    ms.empezar(f'bestia/{ident}')
    ms.SALAS[f'bestia/{ident}'] = sala
    _ACTUAL[0] = ident


def guardar(nombre, x, variante=None, alto=0.85, limite=None, largo=None, techo=None):
    ident = _ACTUAL[0]
    antes = len(ms.EVENTOS.get((f'bestia/{ident}', nombre), []))
    ms.guardar(nombre, x, variante, alto=alto, limite=limite, largo=largo, techo=techo)
    archivos = ms.EVENTOS[(f'bestia/{ident}', nombre)]
    EVENTOS[(ident, nombre)] = list(archivos)


def subtitulos(ident, d):
    SUBTITULOS[ident] = d


def escribir_json(raiz=None):
    raiz = raiz or ms.RAIZ
    r = os.path.join(raiz, 'src/main/resources/assets/atalaya/sounds.json')
    datos = json.load(open(r, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
    mobs = {i for i, _ in EVENTOS}
    for k in [k for k in datos if k.startswith('bestia.') and k.split('.')[1] in mobs]:
        del datos[k]
    for (i, ev), archivos in EVENTOS.items():
        datos[f'bestia.{i}.{ev}'] = {'subtitle': f'subtitles.atalaya.bestia.{i}.{ev}',
                                     'sounds': [f'atalaya:bestia/{i}/{a}' for a in archivos]}
    with open(r, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(datos, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    for idioma, k in (('es_es', 0), ('en_us', 1)):
        p = os.path.join(raiz, f'src/main/resources/assets/atalaya/lang/{idioma}.json')
        d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)
        for clave in [c for c in d if c.startswith('subtitles.atalaya.bestia.') and c.split('.')[3] in mobs]:
            del d[clave]
        for (i, ev) in EVENTOS:
            assert ev in SUBTITULOS.get(i, {}), (i, ev)
            d[f'subtitles.atalaya.bestia.{i}.{ev}'] = SUBTITULOS[i][ev][k]
        with open(p, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False)
            fh.write('\n')
    print(len(EVENTOS), 'eventos del bestiario,', sum(len(v) for v in EVENTOS.values()), 'archivos')
