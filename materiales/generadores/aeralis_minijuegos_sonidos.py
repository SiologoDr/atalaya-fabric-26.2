"""
Los sonidos de los minijuegos de Aeralis (octubre de 2026): Ocelos, Veletas
del Vendaval, Pararrayos y La Chispa. Todos hechos por nosotros. Como
aeralis_mejoras_sonidos.py: toma las herramientas de aeralis_sonidos.py y anade
sus eventos a sounds.json sin quitar los otros.

  ocelos_aviso      los ocelos van a abrirse: un trino de quitina que sube
  ocelos_abre       se abren: un zumbido grave que mira y el roce de las alas
  ocelos_cierra     se cierran: el soplo de las alas al plegarse
  ocelos_rayo       te has movido: el rayo de un ocelo (chasquido y zumbido)
  ocelos_toca       la han tocado: un golpe de viento y su chillido, sorprendida
  veleta_sale       salen las veletas: la piedra que sube y el bronce que suena
  veleta_gira       un clic a una veleta: el bronce que chirria y encaja (45 grados)
  veleta_apunta     una veleta apunta a ella: una campanilla de viento
  veleta_atrapa     las cuatro a la vez: el viento que se cierra sobre ella
  pararrayos_marca  los circulos donde va a caer: la estatica que crepita
  pararrayos_rayo   cae el rayo en un pararrayos: chasquido seco y zumbido de carga
  pararrayos_estalla cae sin pararrayos: el rayo revienta el suelo
  pararrayos_descarga la descarga en ella: un latigazo electrico que se apaga
  chispa_cae        la chispa cae sobre alguien: un silbido que baja y el chispazo
  chispa_tic        cada segundo de la cuenta: un tic electrico
  chispa_pasa       un pase: el silbido de ida y el chispazo al llegar
  chispa_cargada    cargada: el zumbido que sube hasta pitar
  chispa_revienta   revienta en las manos: chasquido, estallido y el zumbido que se apaga
  mini_exito        ganado: el chillido de ella que cae y un acorde de viento
  mini_fallo        perdido: una rafaga que se lleva todo

Uso: python aeralis_minijuegos_sonidos.py <raiz del proyecto>
"""
import collections, json, os, sys, tempfile

RAIZ = sys.argv[1]
AQUI = os.path.dirname(os.path.abspath(__file__))
fuente = open(os.path.join(AQUI, 'aeralis_sonidos.py'), encoding='utf-8').read()
corte = fuente.index('#  AMBIENTE: alrededor de ella')
corte = fuente.rindex('# ====', 0, corte)
herramientas = fuente[:corte]

falsa = tempfile.mkdtemp()
_argv = sys.argv
sys.argv = [_argv[0], falsa]
ns = {'__name__': 'aeralis_sonidos_herramientas'}
exec(compile(herramientas, 'aeralis_sonidos.py', 'exec'), ns)
sys.argv = _argv
ns['OUT'] = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/aeralis')
ns['EVENTOS'] = collections.OrderedDict()
ns['GUARDADOS'] = []
globals().update({k: v for k, v in ns.items() if not k.startswith('__') and k != 'RAIZ'})
import numpy as np

rng = np.random.default_rng(20261011)
ns['rng'] = rng


def tono(f0, f1, dur, armonicos=(1, 2, 3), vel=1.0):
    """Un tono que va de f0 a f1 con algunos armonicos (para campanillas y zumbidos)."""
    n = n_(dur)
    t = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = np.zeros(n)
    for k, a in enumerate(armonicos):
        x += np.sin(fase * a) / (k + 1) ** 1.3
    return x * vel


def campanilla(f, dur=1.6, brillo=1.0):
    """Una campanilla de viento: parciales inarmonicos que se apagan a ritmos distintos."""
    n = n_(dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for r, tau, a in ((1.0, 0.9, 1.0), (2.76, 0.5, 0.5 * brillo), (5.40, 0.25, 0.3 * brillo), (8.93, 0.12, 0.2 * brillo)):
        x += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (tau * dur / 1.6))
    return x * np.clip(t / 0.003, 0, 1)


def zumbido(dur, f=60.0, aspero=0.6):
    """El zumbido electrico: una onda de red con armonicos impares que raspa."""
    n = n_(dur)
    t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * f * t)) * aspero + np.sin(2 * np.pi * f * 3 * t) * 0.4 + np.sin(2 * np.pi * f * 5 * t) * 0.2
    return pb(x, 2400) * campana_env(dur, 0.6)


def chasquido_electrico(dur=0.25, fuerza=1.0):
    """El chasquido de una chispa: ruido muy corto y brillante con un crepitar."""
    x = pa(ruido(dur), 2500) * caida(dur, 0.02)
    return mezclar(pico(x, fuerza), pico(granos(dur, 900, 0.8), 0.5 * fuerza))


def bronce(f=310.0, dur=1.2):
    """El golpe del bronce de una veleta: parciales metalicos que se apagan."""
    n = n_(dur)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for r, tau, a in ((1.0, 0.6, 1.0), (2.32, 0.35, 0.6), (3.86, 0.22, 0.4), (5.21, 0.12, 0.25)):
        x += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / tau)
    return x


# ======================================================================
#  OCELOS
# ======================================================================
guardar('ocelos_aviso', reverb(mezclar(pico(chirrido(0.7, (60, 110), fuerza=0.8), 0.7),
                                      pico(tono(500, 900, 0.7, (1, 2)) * campana_env(0.7, 1.0), 0.4)), 0.3, 1.6))
guardar('ocelos_abre', reverb(mezclar(pico(zumbido(1.6, 48, 0.4), 0.6), pico(aletazo(1.2, 0.8), 0.8),
                                     pico(tono(140, 90, 1.6, (1, 2, 3)) * campana_env(1.6, 0.8), 0.6)), 0.35, 2.2))
guardar('ocelos_cierra', reverb(mezclar(pico(aletazo(1.0, 0.6), 0.8), pico(viento(0.9, [(0, 600), (1, 300)], 1.2, 0.4), 0.4)),
                                0.3, 1.6))
guardar('ocelos_rayo', reverb(mezclar(pico(chasquido_electrico(0.3, 1.0), 1.0), en(0.02, pico(zumbido(0.7, 75, 0.7), 0.6)),
                                      en(0.05, pico(trueno(1.2, 0.4), 0.3))), 0.25, 1.4))
guardar('ocelos_toca', reverb(mezclar(pico(boom(70, 30, 0.2), 0.8), pico(chillido(1.2, 520, 380, 0.7, 0.6), 0.7),
                                      en(0.1, pico(aletazo(1.3, 0.9), 0.6))), 0.35, 2.2))

# ======================================================================
#  VELETAS DEL VENDAVAL
# ======================================================================
roce = moler = None
piedra = pb(ruido(1.4, 'rosa'), 700) * campana_env(1.4, 1.0)
guardar('veleta_sale', reverb(mezclar(pico(piedra, 0.7), en(0.9, pico(bronce(260, 1.4), 0.6)), en(1.0, pico(boom(80, 40, 0.1), 0.4))),
                              0.3, 1.8))
chirria = bp(ruido(0.3), 1800, 4200) * (0.6 + 0.4 * np.sin(np.arange(n_(0.3)) / SR * 2 * np.pi * 38)) * campana_env(0.3, 1.0)
guardar('veleta_gira', reverb(mezclar(pico(chirria, 0.6), en(0.22, pico(bronce(420, 0.6), 0.7)),
                                      en(0.22, pico(chasquido_electrico(0.08, 0.3), 0.3))), 0.2, 1.0), alto=0.7)
guardar('veleta_apunta', reverb(mezclar(pico(campanilla(1568, 1.4), 0.7), en(0.08, pico(campanilla(2093, 1.2), 0.5))), 0.3, 1.6),
        alto=0.6)
guardar('veleta_atrapa', reverb(mezclar(pico(tornado(2.4, 3.0, 0.9, 1.0, 0.6), 0.8), en(0.3, pico(viento(2.0, [(0, 300), (0.5, 900),
                                                                                                           (1, 500)], 1.0, 0.8), 0.6)),
                                        en(1.6, pico(boom(60, 28, 0.3), 0.8))), 0.35, 2.4))

# ======================================================================
#  PARARRAYOS
# ======================================================================
estatica = granos(1.6, 400, 1.0) * campana_env(1.6, 0.7)
guardar('pararrayos_marca', reverb(mezclar(pico(estatica, 0.7), pico(zumbido(1.6, 50, 0.3), 0.3)), 0.3, 1.6))
guardar('pararrayos_rayo', reverb(mezclar(pico(trueno(1.6, 1.0), 0.9), en(0.05, pico(zumbido(1.2, 90, 0.8), 0.5)),
                                          pico(chasquido_electrico(0.2, 1.2), 0.8)), 0.3, 2.0), limite=0.55)
guardar('pararrayos_estalla', reverb(mezclar(pico(estallido(1.0, 2.0), 1.0), pico(trueno(2.0, 1.0), 0.7)), 0.3, 2.2), limite=0.5)
guardar('pararrayos_descarga', reverb(mezclar(pico(chasquido_electrico(0.4, 1.2), 1.0), en(0.03, pico(tono(900, 180, 0.6, (1, 3, 5))
                                                                                                    * caida(0.6, 0.2), 0.6)),
                                              en(0.08, pico(trueno(1.4, 0.6), 0.4))), 0.3, 1.8))

# ======================================================================
#  LA CHISPA
# ======================================================================
guardar('chispa_cae', reverb(mezclar(pico(pasada(0.6, 3200, 900, 2.0, 0.4), 0.6), en(0.5, pico(chasquido_electrico(0.25, 1.0), 0.9))),
                             0.25, 1.4))
guardar('chispa_tic', reverb(mezclar(pico(chasquido_electrico(0.06, 0.8), 0.8), pico(tono(1400, 1400, 0.08, (1, 2)) * caida(0.08, 0.02), 0.5)),
                             0.15, 0.6), alto=0.6)
guardar('chispa_pasa', reverb(mezclar(pico(pasada(0.4, 1800, 2600, 2.5, 0.3), 0.6), en(0.28, pico(chasquido_electrico(0.2, 1.0), 0.8))),
                              0.2, 1.2))
guardar('chispa_cargada', reverb(mezclar(pico(tono(200, 1600, 1.2, (1, 2, 3)) * rampa(1.2, 1.5), 0.6), pico(zumbido(1.2, 80, 0.5), 0.4),
                                         en(1.0, pico(chasquido_electrico(0.25, 1.0), 0.6))), 0.3, 1.6))
guardar('chispa_revienta', reverb(mezclar(pico(chasquido_electrico(0.3, 1.3), 1.0), pico(estallido(0.8, 1.6), 0.8),
                                          en(0.1, pico(zumbido(1.0, 60, 0.6), 0.4))), 0.3, 1.8), limite=0.55)

# ======================================================================
#  EL FINAL DE CADA UNO
# ======================================================================
acorde = mezclar(*[pico(eolica(2.6, f, lento=0.4, brillo=0.8), 0.5) for f in (196.0, 246.9, 293.7)])
guardar('mini_exito', reverb(mezclar(pico(chillido(1.6, 560, 300, 0.7, 0.8), 0.7), en(0.3, pico(acorde, 0.6)),
                                     en(0.2, pico(boom(60, 26, 0.3), 0.6))), 0.4, 2.6))
guardar('mini_fallo', reverb(mezclar(pico(viento(2.4, [(0, 400), (0.3, 1200), (1, 300)], 1.0, 0.9), 0.8),
                                     pico(aletazo(1.6, 1.0), 0.7)), 0.4, 2.4))

# ----------------------------------------------------------------------
#  sounds.json: se anaden (o se rehacen) solo estos eventos.
# ----------------------------------------------------------------------
EVENTOS = ns['EVENTOS']
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for ev, archivos in EVENTOS.items():
    datos['aeralis.' + ev] = {'subtitle': 'subtitles.atalaya.aeralis.' + ev,
                             'sounds': ['atalaya:aeralis/' + a for a in archivos]}
with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(datos, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(len(EVENTOS), 'eventos,', sum(len(v) for v in EVENTOS.values()), 'archivos')
