"""
Genera SOLO los sonidos de las mejoras de Rajang de octubre de 2026 (la
Embestida, la Tumba de Raices, la Furia, los escalones del Sello y el pulso
del totem), sin tocar los demas.

rajang_sonidos.py borra la carpeta y los rehace todos; aqui se toman de ese
mismo script las herramientas (todo lo de antes del primer sonido) y el
bloque de las mejoras (que lleva su propia semilla), y se anaden sus eventos
a sounds.json sin quitar los otros. Sale lo mismo que en la pasada entera.

Uso: python rajang_mejoras_sonidos.py <raiz del proyecto> [hoja_espectrogramas.png]
"""
import collections, json, os, sys, tempfile

RAIZ = sys.argv[1]
AQUI = os.path.dirname(os.path.abspath(__file__))
fuente = open(os.path.join(AQUI, 'rajang_sonidos.py'), encoding='utf-8').read()

# Las herramientas: hasta el primer sonido (el AMBIENTE). Se ejecutan con una
# raiz de mentira, para que el borrado del principio no toque los de verdad.
corte = fuente.index('#  AMBIENTE: despierto')
corte = fuente.rindex('# ====', 0, corte)
herramientas = fuente[:corte]
ini = fuente.index('#  MEJORAS DE OCTUBRE DE 2026')
ini = fuente.rindex('# ====', 0, ini)
fin = fuente.index('#  sounds.json: los eventos rajang.*')
fin = fuente.rindex('# ----', 0, fin)
mejoras = fuente[ini:fin]

falsa = tempfile.mkdtemp()
_argv = sys.argv
sys.argv = [_argv[0], falsa]
ns = {'__name__': 'rajang_sonidos_herramientas'}
exec(compile(herramientas, 'rajang_sonidos.py', 'exec'), ns)
sys.argv = _argv
ns['OUT'] = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/rajang')
ns['RAIZ'] = RAIZ
exec(compile(mejoras, 'rajang_sonidos.py', 'exec'), ns)
EVENTOS = ns['EVENTOS']

# sounds.json: se anaden (o se rehacen) solo estos eventos.
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for ev, archivos in EVENTOS.items():
    datos['rajang.' + ev] = {'subtitle': 'subtitles.atalaya.rajang.' + ev,
                             'sounds': ['atalaya:rajang/' + a for a in archivos]}
with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(datos, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(len(EVENTOS), 'eventos nuevos,', sum(len(v) for v in EVENTOS.values()), 'archivos')

if len(sys.argv) > 2:
    import numpy as np
    from PIL import Image, ImageDraw
    from scipy import signal
    SR = ns['SR']
    GUARDADOS = ns['GUARDADOS']
    an, al, col = 300, 110, 4
    filas = (len(GUARDADOS) + col - 1) // col
    hoja = Image.new('RGB', (an * col, (al + 14) * filas), (12, 14, 18))
    dib = ImageDraw.Draw(hoja)
    for k, (nombre, x) in enumerate(GUARDADOS):
        f, tt, S = signal.spectrogram(x, SR, nperseg=1024, noverlap=768)
        S = 10 * np.log10(S + 1e-12)
        S = np.clip((S - (S.max() - 65)) / 65, 0, 1)
        fl = np.geomspace(30, 16000, al)
        idx = np.clip(np.searchsorted(f, fl), 0, len(f) - 1)
        im = Image.fromarray((S[idx][::-1] * 255).astype(np.uint8)).resize((an - 4, al), Image.BILINEAR)
        cx, cy = (k % col) * an, (k // col) * (al + 14)
        hoja.paste(Image.merge('RGB', (im.point(lambda v: int(v * 0.6)), im, im.point(lambda v: int(v * 0.8)))), (cx + 2, cy + 14))
        dib.text((cx + 4, cy + 1), f'{nombre}  {len(x) / SR:.1f}s', fill=(220, 220, 220))
    hoja.save(sys.argv[2])
