"""
Los sonidos de las mecanicas cooperativas de Nerea (octubre de 2026): el Canto
de Sirena, la Marea Alta (burbujas de refugio) y los Encadenados. Como
nerea_mejoras_sonidos.py: toma las herramientas de nerea_sonidos.py (todo lo de
antes del primer sonido) y anade sus eventos a sounds.json sin quitar los otros.

  canto         8 s: la sirena vocaliza, deslizandose entre notas, con una
                segunda voz debajo y el coro del abismo
  trance        al quedar hechizado: un brillo que baja y un susurro
  trance_clic   cada clic que te saca del trance: una pompa (3 variantes)
  despierta     al salir del trance: la pompa grande y un brillo que sube
  encadenar     lanza las cadenas: latigazo de eslabones y chapuzon
  cadena_tiron  la cadena se tensa de golpe (2 variantes)
  refugio       nace una burbuja de refugio
  cuenta        un segundo de la cuenta atras de la Marea Alta (un sonar)
  marea_alta    revienta el mar fuera de las burbujas

Uso: python nerea_cooperativas_sonidos.py <raiz del proyecto>
"""
import collections, json, os, sys, tempfile

RAIZ = sys.argv[1]
AQUI = os.path.dirname(os.path.abspath(__file__))
fuente = open(os.path.join(AQUI, 'nerea_sonidos.py'), encoding='utf-8').read()
corte = fuente.index('#  AMBIENTE: el fondo del mar')
corte = fuente.rindex('# ====', 0, corte)
herramientas = fuente[:corte]

falsa = tempfile.mkdtemp()
_argv = sys.argv
sys.argv = [_argv[0], falsa]
ns = {'__name__': 'nerea_sonidos_herramientas'}
exec(compile(herramientas, 'nerea_sonidos.py', 'exec'), ns)
sys.argv = _argv
ns['OUT'] = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/nerea')
ns['EVENTOS'] = {}
globals().update({k: v for k, v in ns.items() if not k.startswith('__') and k != 'RAIZ'})
import numpy as np

rng = np.random.default_rng(20261008)
ns['rng'] = rng


def nota(hz):
    return float(hz)


# ======================================================================
#  CANTO: tres frases de sirena en re menor, la segunda voz una tercera por
#  debajo y un coro de "aaa" muy hondo que sostiene. Todo bajo el agua.
# ======================================================================
D = 8.0
n = n_(D)
frases = [
    (0.0, 2.9, [(0, 294), (0.18, 440), (0.45, 415), (0.7, 349), (1, 330)]),
    (2.5, 2.9, [(0, 349), (0.2, 523), (0.5, 466), (0.75, 440), (1, 392)]),
    (5.0, 3.0, [(0, 440), (0.25, 587), (0.5, 523), (0.75, 440), (1, 294)]),
]
voz = np.zeros(n + n_(1.0))
segunda = np.zeros_like(voz)
for t0, d, puntos in frases:
    v = lamento(d, puntos, armonicos=11, vibrato=0.018, brillo=1100)
    i = n_(t0)
    voz[i:i + len(v)] += v
    baja = lamento(d, [(p, f * 0.8) for p, f in puntos], armonicos=9, vibrato=0.014, brillo=800)
    segunda[i + n_(0.12):i + n_(0.12) + len(baja)] += baja[:len(segunda) - i - n_(0.12)]
coro = garganta(curva(n, [(0, 147), (0.33, 175), (0.66, 196), (1, 147)]), D,
                VOCAL_A, aspereza=0.1, sub=0.1, jitter=0.012, aliento=0.5, fmax=3000)
coro = coro * ventana(D, 1.2, 2.0)
burbujas = nube(D, 30 + 20 * suave(n, 0.5) ** 2, 1.0, 6.0)
capas = mezclar(pico(sumergir(voz[:n], 3200, 0.12), 1.0), pico(sumergir(segunda[:n], 2400, 0.12), 0.45),
                pico(sumergir(coro, 1400, 0.2), 0.35), pico(burbujas, 0.12))
guardar('canto', reverb(capas, 0.45, 3.0, 3000), alto=0.8)

# ======================================================================
#  TRANCE y DESPERTAR
# ======================================================================
d = 0.9
brillo = mezclar(*[en(0.06 * k, modos(1760 / (1 + 0.12 * k), 0.5, ((1, 1), (2.76, 0.2)), 0.18) * (0.8 ** k))
                   for k in range(6)])
susurro = bp(ruido(d, 'rosa'), 1800, 6000) * ventana(d, 0.2, 0.5)
guardar('trance', reverb(mezclar(pico(brillo, 0.8), pico(susurro, 0.25)), 0.4, 1.8, 5000))
for i in range(3):
    guardar('trance_clic', mezclar(pico(burbuja(5 + 2 * i, 0.08, 1.0, 1.2), 1.0),
                                   pico(modos(900 + 150 * i, 0.12, ((1, 1),), 0.04), 0.3)), i + 1)
sube = mezclar(*[en(0.05 * k, modos(880 * (1 + 0.15 * k), 0.4, ((1, 1), (2.01, 0.25)), 0.15) * (0.85 ** k))
                 for k in range(5)])
guardar('despierta', reverb(mezclar(pico(burbuja(14, 0.1, 1.0, 1.0), 1.0), en(0.05, pico(sube, 0.6)),
                                    pico(nube(0.5, 300, 1.0, 5.0), 0.3)), 0.3, 1.2, 5000))

# ======================================================================
#  ENCADENAR y el tiron
# ======================================================================
latigo = mezclar(*[en(0.035 * k, eslabon(k % 2 == 0, 1.0 - 0.06 * k)) for k in range(14)])
silbido = bp(ruido(0.6, 'rosa'), 400, 2500) * rampa(0.6, 2.0, 1.0, 0.0)
guardar('encadenar', reverb(mezclar(pico(silbido, 0.4), en(0.15, pico(latigo, 1.0)), en(0.55, pico(chapuzon(0.7), 0.6))),
                            0.3, 1.4, 3000))
for i in range(2):
    guardar('cadena_tiron', reverb(mezclar(pico(impacto(0.9 + 0.1 * i, 5), 0.9),
                                           pico(mezclar(*[en(0.012 * k, eslabon(True, 1.0)) for k in range(6)]), 1.0)),
                                   0.25, 1.0, 2500), i + 1)

# ======================================================================
#  MAREA ALTA: nace una burbuja de refugio, la cuenta y el mar que revienta
# ======================================================================
d = 1.1
forma = burbuja(26, 0.06, 1.0, 0.7, 0.3)
guardar('refugio', reverb(mezclar(pico(nube(d, rampa(d, 1.0, 600, 40), 1.0, 8.0), 0.6), en(0.25, pico(forma, 1.0))),
                          0.35, 1.6, 3000))
guardar('cuenta', mezclar(pico(modos(620, 0.35, ((1, 1), (2.01, 0.2)), 0.12), 1.0), pico(burbuja(8, 0.1, 0.6), 0.3)))
d = 2.8
guardar('marea_alta', reverb(mezclar(pico(rompiente(2.6, 0.3, 1.4), 1.0), pico(boom(55, 28, 0.5), 0.9),
                                     en(0.2, pico(nube(2.2, rampa(2.2, 1.0, 2000, 100), 2.0, 12.0), 0.5))),
                             0.4, 2.2, 2500), alto=0.85)

# ----------------------------------------------------------------------
#  sounds.json: se anaden (o se rehacen) solo estos eventos.
# ----------------------------------------------------------------------
EVENTOS = ns['EVENTOS']
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for ev, archivos in EVENTOS.items():
    datos['nerea.' + ev] = {'subtitle': 'subtitles.atalaya.nerea.' + ev,
                            'sounds': ['atalaya:nerea/' + a for a in archivos]}
with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(datos, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(len(EVENTOS), 'eventos,', sum(len(v) for v in EVENTOS.values()), 'archivos')
