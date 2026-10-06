"""
Hojas de control de las animaciones de Novilis: una tira de fotogramas con dos
vistas cada uno, tres cuartos por delante (arriba) y de perfil (abajo), sobre
la rejilla del suelo. El perfil es el que delata los pies que flotan o se
hunden y las rodillas que se doblan al reves.

  tira(pose_fn, nombre, tiempos, uv, alto, tex, emis, carpeta, sufijo='')

pose_fn(nombre, s) -> pose del juego (la de nj.matrices / nj.quads), con
'oculto' en la espada que no toque.
"""
import os
import numpy as np
from PIL import Image, ImageDraw
import vigia_render as vr
import novilis_juego as nj

LUCES = [((-0.5, 0.8, -0.6), (1.0, 0.95, 0.88), 0.85, 'llave'), ((0.7, 0.3, 0.6), (1.0, 0.55, 0.3), 0.5, 'contra')]
W, H = 210, 280


def _suelo(lz, cam):
    g = np.zeros((16, 16, 4), np.uint8)
    g[...] = (200, 200, 194, 255)
    g[0, :] = g[:, 0] = (150, 150, 144, 255)
    for i in range(-16, 16):
        for j in range(-16, 16):
            Pq = [(i, 0, j), (i + 1, 0, j), (i + 1, 0, j + 1), (i, 0, j + 1)]
            for tri in ((0, 1, 2), (0, 2, 3)):
                lz.triangulo(cam, [Pq[q] for q in tri], [((0, 0), (1, 0), (1, 1), (0, 1))[q] for q in tri], g,
                             np.array([0.92, 0.92, 0.92]))


def vista(pose, uv, alto, tex, emis, lado=False):
    k = nj.ESCALA / 1.25
    if lado:
        # de perfil: la camara a su derecha, baja, para ver los pies contra el suelo
        cam = vr.Camara(ojo=(19 * k, 5.0 * k, -1.5 * k), objetivo=(0, 6.0 * k, -1.5 * k), fov=50, ancho=W, alto=H)
    else:
        cam = vr.Camara(ojo=(9 * k, 7.0 * k, -16 * k), objetivo=(0, 6.0 * k, 0), fov=50, ancho=W, alto=H)
    lz = vr.Lienzo(W, H)
    M = vr.entidad_a_mundo(0, 0, 0, -30 if not lado else 0, nj.ESCALA)
    _suelo(lz, cam)
    for Pq, UV, _ in nj.quads(pose, uv, alto, M):
        luz = vr.iluminar(vr.normal(Pq), cam, np.mean(Pq, axis=0), LUCES, (0.4, 0.38, 0.38))
        for tri in ((0, 1, 2), (0, 2, 3)):
            lz.triangulo(cam, [Pq[q] for q in tri], [UV[q] for q in tri], tex, luz, emis)
    col = np.clip(lz.color + lz.emis * 0.4, 0, 1)
    a = lz.alfa[..., None]
    arr = col * a + np.array([0.93, 0.94, 0.95]) * (1 - a)
    return Image.fromarray((arr * 255).astype(np.uint8))


def tira(pose_fn, nombre, tiempos, uv, alto, tex, emis, carpeta, sufijo='', marcas=()):
    """marcas: tiempos que van con el rotulo en rojo (golpes, avisos)."""
    cols = []
    for s in tiempos:
        pose = pose_fn(nombre, s)
        a = vista(pose, uv, alto, tex, emis)
        b = vista(pose, uv, alto, tex, emis, lado=True)
        col = Image.new('RGB', (W, 2 * H), (255, 255, 255))
        col.paste(a, (0, 0))
        col.paste(b, (0, H))
        d = ImageDraw.Draw(col)
        rojo = any(abs(s - m) < 1e-3 for m in marcas)
        d.text((6, 4), f'{nombre} {s:.2f}s', fill=(190, 20, 20) if rojo else (20, 20, 20))
        d.line([(0, H), (W, H)], fill=(255, 255, 255), width=2)
        cols.append(col)
    hoja = Image.new('RGB', (W * len(cols), 2 * H), (255, 255, 255))
    for i, c in enumerate(cols):
        hoja.paste(c, (i * W, 0))
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f'novilis_anim_{nombre.lower()}{sufijo}.jpg')
    hoja.save(ruta, quality=86)
    return ruta
