"""
Textura del rayo de la mirada: 128x64, cuadricula UV identica a RayoVigiaModel.

Tres cajas largas en el eje Z (el de vuelo):
  nucleo  2x2x28 en (0,0)   -> casi blanco, tirando a rosa: lo que mas brilla
  halo    5x5x22 en (0,30)  -> rojo translucido, se apaga hacia la cola
  punta   4x4x4  en (64,0)  -> la cabeza del rayo, ambar caliente
  cola    3x3x30 en (60,30) -> la estela, que se desvanece hasta transparente.
                               Es geometria, no particulas: el rayo se lee
                               como UN trazo y no como una ristra de puntos.

Va con un tipo de render translucido y emisivo, asi que el ALFA de cada pixel
es lo que decide cuanto se ve: el halo deja ver el nucleo a traves.

Uso: python vigia_rayo_tex.py <raiz del proyecto>
"""
from PIL import Image
import os, sys, random

RAIZ = sys.argv[1]
SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/vigia/rayo.png')
rnd = random.Random(5)
im = Image.new('RGBA', (128, 64), (0, 0, 0, 0))
p = im.load()

def caja(u, v, w, h, d, color):
    """color(cara, i, j, ancho, alto, frac_z) -> rgba. frac_z: 0 delante, 1 cola."""
    caras = {
        'arriba': (u + d, v, w, d, 'v'), 'abajo': (u + d + w, v, w, d, 'v'),
        'a': (u, v + d, d, h, 'u'), 'frente': (u + d, v + d, w, h, None),
        'b': (u + d + w, v + d, d, h, 'u'), 'espalda': (u + 2 * d + w, v + d, w, h, None),
    }
    for nombre, (x0, y0, ww, hh, eje) in caras.items():
        for j in range(hh):
            for i in range(ww):
                if eje == 'u':
                    fz = i / max(ww - 1, 1)
                elif eje == 'v':
                    fz = j / max(hh - 1, 1)
                else:
                    fz = 0.0 if nombre == 'frente' else 1.0
                p[x0 + i, y0 + j] = color(nombre, i, j, ww, hh, fz)

def nucleo(c, i, j, w, h, fz):
    # Incandescente: blanco puro delante, apenas amarillento detras.
    return (255, 255, int(250 - 50 * fz), 255)

def halo(c, i, j, w, h, fz):
    # Rojo de caza; el alfa cae hacia la cola y hacia los bordes de la cara,
    # con un grano que lo hace chisporrotear en vez de verse de plastico.
    borde = 0.6 if (i in (0, w - 1) or j in (0, h - 1)) and c in ('frente', 'espalda') else 1.0
    a = int((215 - 120 * fz) * borde * rnd.uniform(0.85, 1.0))
    r, g, b = 255, int(80 + 70 * (1 - fz) * rnd.random()), 25
    return (r, g, b, max(a, 0))

def punta(c, i, j, w, h, fz):
    return (255, 235 + rnd.randint(0, 20), 170, 255)

def cola(c, i, j, w, h, fz):
    # De rojo vivo a nada: el alfa cae con el cuadrado de la distancia.
    a = int(200 * (1 - fz) ** 2 * rnd.uniform(0.8, 1.0))
    return (255, int(60 + 80 * (1 - fz)), 20, a)

caja(0, 0, 2, 2, 28, nucleo)
caja(0, 30, 5, 5, 22, halo)
caja(64, 0, 4, 4, 4, punta)
caja(60, 30, 3, 3, 30, cola)
im.save(SALIDA)
im.resize((512, 512), Image.NEAREST).save(sys.argv[2] if len(sys.argv) > 2 else os.devnull, 'PNG') if len(sys.argv) > 2 else None
print('ok')
