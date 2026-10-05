"""
Las texturas de las piezas de los ataques de Rajang y de las plataformas del Sello,
sacadas de las mismas texturas de la ficha (tierra_ataques.py):

  textures/entity/rajang/roca.png (+ roca_brillo)   la roca parda en estratos de
                                                    los picos y los pilares
  textures/entity/rajang/totem.png (+ totem_brillo) las cuatro caras de glifos
                                                    (numero maya, el ojo, la
                                                    espiral, el jaguar): arriba
                                                    enteras, abajo rajadas
  textures/entity/rajang/fragmento.png (+ brillo)   el jade del Cataclismo
  textures/entity/rajang/llama.png                  la estela de llama verde
  textures/entity/rajang/oro.png y haz.png          la banda de oro y el haz de los totems
  textures/entity/rajang/rajang_disolver.png        la mascara para volverse
                                                    piedra y deshacerse
  textures/entity/rajang/cesped.png (+ _borde)      la hierba de lo alto de las
                                                    plataformas y piedras del Sello
                                                    y la que cuelga por sus lados

Uso: python rajang_piezas.py <raiz del proyecto>
"""
import os, sys
import numpy as np
from PIL import Image
import tierra_ataques as ta

RAIZ = sys.argv[1]
A = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures')
ENT = os.path.join(A, 'entity/rajang')
os.makedirs(ENT, exist_ok=True)


def guardar(arr, ruta):
    Image.fromarray(np.asarray(arr, np.uint8)).save(ruta)


# la roca
t, e = ta.tex('estrato')
guardar(t, os.path.join(ENT, 'roca.png'))
guardar(e, os.path.join(ENT, 'roca_brillo.png'))

# el totem: 4 caras de 24x40 en fila; abajo, las mismas rajadas
w, h = 24, 40
tot = np.zeros((h * 2, w * 4, 4), np.uint8)
gl = np.zeros_like(tot)
for k in range(4):
    a, b = ta._tex_totem(k, 'on', w, h)
    tot[0:h, k * w:(k + 1) * w] = ta._tex_totem(k, 'off', w, h)[0]
    gl[0:h, k * w:(k + 1) * w] = b
    tot[h:2 * h, k * w:(k + 1) * w] = ta._tex_totem(k, 'roto', w, h)[0]
guardar(tot, os.path.join(ENT, 'totem.png'))
guardar(gl, os.path.join(ENT, 'totem_brillo.png'))

# el fragmento y la llama
t, e = ta.tex('fragmento')
guardar(t, os.path.join(ENT, 'fragmento.png'))
guardar(e, os.path.join(ENT, 'fragmento_brillo.png'))
guardar(ta.LLAMA, os.path.join(ENT, 'llama.png'))

# la mascara de disolverse: grano de piedra a varias escalas (la piedra se
# deshace a terrones, no a pixeles sueltos)
n = ta._fbm2(256, 256, (8, 8), 77, 4)
m = np.zeros((256, 256, 4), np.uint8)
v = np.clip((n - n.min()) / (n.max() - n.min()) * 255, 0, 255).astype(np.uint8)
m[..., 0] = m[..., 1] = m[..., 2] = v
m[..., 3] = 255
guardar(m, os.path.join(ENT, 'rajang_disolver.png'))

# la banda de oro de los totems y el haz de luz de los totems vivos
guardar(ta.tex('oro_b')[0], os.path.join(ENT, 'oro.png'))
guardar(ta.HAZ, os.path.join(ENT, 'haz.png'))

# la hierba de lo alto de las plataformas y las piedras del Sello
guardar(ta.tex('cesped')[0], os.path.join(ENT, 'cesped.png'))

# el borde de la hierba, por los lados de las plataformas y las piedras: la
# franja de hierba arriba y, debajo, la hierba y las raices que cuelgan sobre
# la roca (lo demas, transparente: se ve la roca de detras)
ces = np.asarray(ta.tex('cesped')[0], np.uint8)
rb = np.random.default_rng(31)
borde = np.zeros((16, 32, 4), np.uint8)
borde[0:5] = ces[0:5, 0:32]
for x in range(32):
    largo = int(rb.choice([0, 1, 2, 2, 3, 4, 5, 7, 9], p=[0.08, 0.14, 0.18, 0.16, 0.14, 0.12, 0.09, 0.06, 0.03]))
    for y in range(5, 5 + largo):
        c = ces[(y * 3 + x) % 32, (x * 7) % 32].astype(int)
        oscuro = 1.0 - 0.07 * (y - 4)
        borde[y, x, :3] = np.clip(c[:3] * oscuro, 0, 255)
        borde[y, x, 3] = 255
    if rb.random() < 0.12:
        # una raiz parda que baja mas
        for y in range(5 + largo, min(16, 9 + largo + int(rb.integers(2, 6)))):
            borde[y, x] = (92 - 3 * y, 64 - 2 * y, 40 - y, 255)
guardar(borde, os.path.join(ENT, 'cesped_borde.png'))
print('ok')
