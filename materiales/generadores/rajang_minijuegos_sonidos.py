"""
Los sonidos de los minijuegos de Rajang (octubre de 2026): El Rayo del Prisma,
El Impostor de Jade, Glifos del Templo y Suelo que se Hunde. Todos hechos por
nosotros (Juan: "no debemos usar lo que tiene minecraft"). Como
rajang_mejoras_sonidos.py: toma las herramientas de rajang_sonidos.py y anade
sus eventos a sounds.json sin quitar los otros.

  prisma_cae          el prisma baja del cielo: destellos que caen y un tin de cristal
  prisma_luz          se enciende la luz del prisma: el jade que canta y sube
  trampa_abre         sale una trampa de oro: piedra que roza, oro que suena, pinchos
  trampa_cae          Rajang cae en la trampa: los pinchos se parten, el golpe y su queja
  impostor_disfraz    se envuelve en polvo de jade y se encoge: soplo, brillo y un puf
  impostor_descubierto  le pillan: el disfraz revienta en jade y ruge
  senuelo_rompe       una copia falsa se deshace en arenilla de jade
  glifo_alza          salen las columnas de los glifos: la tierra y el jade que zumba
  glifo_golpe         un golpe a una columna: piedra densa que suena (3 variantes)
  glifo_rompe         un glifo verdadero se rompe: campana de oro y esquirlas
  glifo_falso         un glifo falso estalla: golpe, roca que se raja y la maldicion
  vidente             eres el Vidente: un canto de jade lejano
  suelo_alza          el suelo se vuelve losas y sube: retumbo y piedra que muele
  losa_cruje          una losa pisada se agrieta (2 variantes)
  losa_cae            una losa cae al foso
  pinchos             caes en los pinchos del foso
  mini_exito          minijuego ganado: campanas de oro que suben
  mini_fallo          minijuego perdido: la maldicion que baja

Uso: python rajang_minijuegos_sonidos.py <raiz del proyecto>
"""
import collections, json, os, sys, tempfile

RAIZ = sys.argv[1]
AQUI = os.path.dirname(os.path.abspath(__file__))
fuente = open(os.path.join(AQUI, 'rajang_sonidos.py'), encoding='utf-8').read()
corte = fuente.index('#  AMBIENTE: despierto')
corte = fuente.rindex('# ====', 0, corte)
herramientas = fuente[:corte]

falsa = tempfile.mkdtemp()
_argv = sys.argv
sys.argv = [_argv[0], falsa]
ns = {'__name__': 'rajang_sonidos_herramientas'}
exec(compile(herramientas, 'rajang_sonidos.py', 'exec'), ns)
sys.argv = _argv
ns['OUT'] = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/rajang')
ns['EVENTOS'] = collections.OrderedDict()
globals().update({k: v for k, v in ns.items() if not k.startswith('__') and k != 'RAIZ'})
import numpy as np

rng = np.random.default_rng(20261010)
ns['rng'] = rng


def tin(f, dur=1.2, tau=0.5):
    """Un cristal de jade tallado que suena limpio."""
    return jade(f, dur, tau, JADE_TALLA, 0.6)


# ======================================================================
#  EL RAYO DEL PRISMA
# ======================================================================
d = 1.6
caen = mezclar(*[en(0.07 * k, tin(2800 * (0.93 ** k), 0.5, 0.12) * (0.85 ** (k * 0.5))) for k in range(10)])
llega = mezclar(pico(tin(1760, 1.4, 0.6), 1.0), pico(campana_oro(440, 1.2), 0.35))
guardar('prisma_cae', reverb(mezclar(pico(caen, 0.6), pico(destellos(0.8, 30, 3000, 8000), 0.3), en(0.72, llega)), 0.35, 2.2,
                             7500), techo=-12, largo=2.6)

hum = canto_jade(0.9, 660) * rampa(0.9, 0.6, 0.2, 1.0) * ventana(0.9, 0.02, 0.3)
guardar('prisma_luz', reverb(mezclar(pico(hum, 0.8), pico(tin(1320, 0.8, 0.3), 0.5), en(0.15, pico(tin(1980, 0.6, 0.2), 0.35))),
                             0.3, 1.4, 8000), techo=-16)

d = 1.4
roza = moler(0.9, 1.0, (20, 50), 0.8) * campana_env(0.9, 1.3)
oro = campana_oro(196, 1.6)
pinchos = mezclar(*[en(0.55 + 0.05 * k, brota(0.2, 1500 - 120 * k, 500, 0.6)) for k in range(4)])
guardar('trampa_abre', reverb(mezclar(pico(roza, 0.7), en(0.35, pico(oro, 0.45)), pico(pinchos, 0.6)), 0.3, 1.8), largo=2.4)

choque = golpe_tierra(1.4, 1.2, 1.0, 2.2)
rotos = mezclar(*[en(s, esquirlas(8, 0.25, 1500, 5200)) for s in (0.0, 0.04, 0.09)])
queja = quejido(1.0, 92)
guardar('trampa_cae', reverb(mezclar(pico(choque, 1.0), pico(rotos, 0.6), pico(campana_oro(147, 1.2), 0.3),
                                     en(0.25, pico(queja, 0.85))), 0.28, 2.2), limite=0.55, largo=3.0)

# ======================================================================
#  EL IMPOSTOR DE JADE
# ======================================================================
d = 1.8
soplo = pasada(1.4, 1800, 500, 1.5, 0.35) * ventana(1.4, 0.2, 0.5)
brillo = destellos(1.4, 40, 2500, 7500)
puf = mezclar(pico(pb(ruido(0.35, 'rosa'), 1800) * caida(0.35, 0.08), 1.0), pico(boom(160, 90, 0.05, 0.3), 0.5))
guardar('impostor_disfraz', reverb(mezclar(pico(soplo, 0.6), pico(brillo, 0.4), en(1.25, pico(puf, 0.8)),
                                           pico(grava(1.4, 300, (0.2, 1.0)), 0.25)), 0.3, 1.6, 6000))

revienta = mezclar(*[en(s, esquirlas(10, 0.3, 1600, 6500)) for s in (0.0, 0.03)])
ruge = rugido(2.0, 70, 110, cola=1.2, mezcla=0.25)
guardar('impostor_descubierto', reverb(mezclar(pico(revienta, 0.8), pico(boom(90, 40, 0.15, 0.6), 0.6), en(0.15, pico(ruge, 0.9))),
                                       0.28, 2.2), limite=0.55)

arena = grava(0.9, 900 * np.exp(-t_(0.9) / 0.25), (0.2, 1.5))
guardar('senuelo_rompe', reverb(mezclar(pico(esquirlas(12, 0.4, 2000, 6000), 0.7), pico(arena, 0.6),
                                        pico(pb(ruido(0.5, 'rosa'), 2500) * caida(0.5, 0.15), 0.4)), 0.25, 1.2, 6000))

# ======================================================================
#  GLIFOS DEL TEMPLO
# ======================================================================
d = 2.2
tierra = retumbo(d, 100, 2.0, 0.5, 1.0) * campana_env(d, 1.2)
suben = mezclar(*[en(0.2 + 0.25 * k, brota(0.35, 1100, 300, 0.8)) for k in range(6)])
guardar('glifo_alza', reverb(mezclar(pico(tierra, 0.7), pico(suben, 0.5), en(0.6, pico(glifo(196, 0.8, 1.4), 0.5))), 0.3, 2.0),
        limite=0.6)

for i in range(3):
    seco = pb(ruido(0.08, 'rosa'), 3000) * caida(0.08, 0.012)
    guardar('glifo_golpe', reverb(mezclar(pico(seco, 0.8), pico(jade(rng.uniform(300, 420), None, 0.35, JADE_TALLA, 1.0), 0.6),
                                          pico(canto(14, 0.7, False), 0.5)), 0.2, 1.0), i + 1, largo=1.0)

guardar('glifo_rompe', reverb(mezclar(pico(campana_oro(392, 2.0), 0.7), pico(esquirlas(14, 0.4, 1800, 6500), 0.7),
                                      pico(rajar_roca(8, 0.05, 1.0, 0.8), 0.5), en(0.1, pico(tin(1568, 1.0, 0.4), 0.4))), 0.32, 2.4),
        limite=0.6, largo=3.0)

guardar('glifo_falso', reverb(mezclar(pico(boom(70, 28, 0.3, 1.4), 1.0), pico(rajar_roca(12, 0.06, 1.0, 1.0), 0.7),
                                      pico(escombros(1.2, 1.0, 0.35), 0.5), en(0.05, pico(maldicion(1.2, 55.0, 1.2), 0.45))), 0.28, 2.0),
        limite=0.5)

lejano = canto_jade(2.0, 523.25) * ventana(2.0, 0.3, 0.9)
guardar('vidente', reverb(mezclar(pico(lejano, 0.6), *[en(0.2 + 0.3 * k, pico(tin(f, 1.2, 0.5), 0.5)) for k, f in
                                                       enumerate((1046.5, 1318.5, 1568.0))]), 0.5, 3.0, 7000), techo=-14, largo=3.0)

# ======================================================================
#  SUELO QUE SE HUNDE
# ======================================================================
d = 2.6
tierra = retumbo(d, 90, 2.5, 0.55, 1.2) * np.interp(t_(d), [0, 0.3, 2.0, d], [0.2, 1.0, 0.8, 0])
muele = moler(2.0, 1.4, (30, 70), 1.0) * campana_env(2.0, 1.1)
guardar('suelo_alza', reverb(mezclar(pico(tierra, 0.8), pico(muele, 0.5), en(1.8, pico(boom(80, 36, 0.12, 0.6), 0.6))), 0.28, 2.0),
        limite=0.55)

for i in range(2):
    raja = crepitar(0.6, 60 + 40 * i, curva(n_(0.6), [(0, 900), (1, 2800)]), 1.3) * rampa(0.6, 0.7, 0.3, 1.0)
    guardar('losa_cruje', reverb(mezclar(pico(raja, 0.7), pico(rajar_roca(5, 0.04, 1.0, 0.8), 0.5)), 0.2, 1.0), i + 1)

guardar('losa_cae', reverb(mezclar(pico(rodar(1.0, 20.0, 4, 1.0, 0.2), 0.7), en(0.35, pico(boom(85, 40, 0.1, 0.5), 0.8)),
                                   en(0.35, pico(escombros(0.8, 0.7, 0.3), 0.5))), 0.25, 1.6))

guardar('pinchos', reverb(mezclar(pico(esquirlas(10, 0.25, 1400, 4800), 0.8), pico(canto(18, 1.0, True), 0.7),
                                  pico(boom(110, 60, 0.05, 0.3), 0.5)), 0.2, 1.2))

# ======================================================================
#  EL FINAL DE CADA UNO
# ======================================================================
sube = mezclar(*[en(0.12 * k, campana_oro(f, 2.2) * (0.92 ** k)) for k, f in enumerate((196.0, 246.94, 293.66, 392.0))])
guardar('mini_exito', reverb(mezclar(pico(sube, 1.0), en(0.4, pico(destellos(1.2, 25, 3000, 8000), 0.3))), 0.4, 2.8, 7000),
        techo=-12, largo=4.0)

bajan = mezclar(*[en(0.15 * k, jade(f, 1.4, 0.6, JADE, 0.8) * (0.9 ** k)) for k, f in enumerate((330.0, 277.0, 220.0, 165.0))])
guardar('mini_fallo', reverb(mezclar(pico(bajan, 0.8), pico(maldicion(2.0, 49.0, 1.0), 0.5)), 0.4, 2.6, 4000), techo=-14)

# ----------------------------------------------------------------------
#  sounds.json: se anaden (o se rehacen) solo estos eventos.
# ----------------------------------------------------------------------
EVENTOS = ns['EVENTOS']
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for ev, archivos in EVENTOS.items():
    datos['rajang.' + ev] = {'subtitle': 'subtitles.atalaya.rajang.' + ev,
                             'sounds': ['atalaya:rajang/' + a for a in archivos]}
with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(datos, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(len(EVENTOS), 'eventos,', sum(len(v) for v in EVENTOS.values()), 'archivos')
