"""
Los sonidos de los minijuegos de Nerea (octubre de 2026): la Pesca del Abismo,
los Canones del Naufragio, las Morenas de las Pozas y el Duelo de Canto. Juan:
"el sonido y todo deben ser nuevos, hechos por nosotros; no usar lo de
Minecraft". Como nerea_cooperativas_sonidos.py: toma las herramientas de
nerea_sonidos.py y anade sus eventos a sounds.json sin quitar los otros.

  pesca_lanzar     el latigazo de la cana y el carrete que suelta sedal
  pesca_cae        el corcho cae en la poza: un plop hondo
  pesca_pica       ALGO PICA: el tiron, el chapoteo y un brillo de perla (corto y claro)
  pesca_recoger    el carrete que recoge y el corcho que sale del agua
  pesca_escapa     se ha escapado: burbujas que se van al fondo
  perla_pescada    sale la perla: un acorde de cristal que sube
  perla_lanzar     la perla sale volando: soplo con brillo
  perla_corazon    la perla llega al corazon: latido y cristal
  morena_sale      la morena revienta el agua y bufa (3 variantes)
  morena_aviso     se echa atras antes de morder: siseo
  morena_mordisco  la dentellada (2 variantes)
  morena_golpe     le das: golpe seco y chillido (3 variantes)
  morena_baja      se mete en el agujero: trago y burbujas
  canon_sale       el canon sale del suelo: madera que cruje, tierra y cadenas
  bala_coger       coges una bala de la pila: hierro pesado
  canon_cargar     la bala rueda por el anima y topa al fondo
  canon_vacio      el chasquido de la mecha sin bala
  canon_disparo    el canonazo: estampido, chasquido y cola larga
  bala_impacto     la bala revienta contra Nerea
  bala_cae         la bala se pierde: golpe sordo contra la tierra
  duelo_nota1..4   el arpa del abismo, una nota por carril (re, fa, la, do)
  duelo_fallo      nota fallada: una cuerda que se destempla
  duelo_perfecto   el brillo de una nota perfecta
  duelo_cuenta     cada segundo de la preparacion
  duelo_gana       le vuelves el canto: arpegio que sube
  duelo_pierde     caes en su canto: arpegio que baja y se ahoga

Uso: python nerea_minijuegos_sonidos.py <raiz del proyecto>
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

rng = np.random.default_rng(20261009)
ns['rng'] = rng


def cuerda(f, dur, brillo=0.5, apagado=0.996):
    """Una cuerda pulsada (Karplus-Strong): el arpa del abismo."""
    n = n_(dur)
    p = max(2, int(round(SR / f)))
    buf = rng.uniform(-1, 1, p) * (1 - brillo) + bp(ruido(p / SR + 0.01), 800, 9000)[:p] * brillo
    out = np.zeros(n)
    for i in range(n):
        v = buf[i % p]
        out[i] = v
        buf[i % p] = apagado * 0.5 * (v + buf[(i + 1) % p])
    return out * caida(dur, dur * 0.45, 0.001)


def carraca(dur, tasa0, tasa1, f=2600, amp=1.0):
    """Un carrete: chasquidos de trinquete que van de tasa0 a tasa1 por segundo."""
    n = n_(dur)
    fase = np.cumsum(np.linspace(tasa0, tasa1, n)) / SR
    golpes = np.nonzero(np.diff(np.floor(fase)) > 0)[0]
    out = np.zeros(n + n_(0.02))
    for i in golpes:
        c = modos(f * rng.uniform(0.9, 1.1), 0.02, ((1, 1), (1.8, 0.5)), 0.004) * rng.uniform(0.5, 1.0)
        out[i:i + len(c)] += c
    return amp * out


def chillido(f0, f1, dur, aspero=0.3):
    """Un chillido de bicho: tono que se desliza con aspereza."""
    t = t_(dur)
    f = f0 + (f1 - f0) * (t / dur) ** 0.7
    fase = 2 * np.pi * np.cumsum(f * (1 + 0.04 * np.sin(2 * np.pi * 38 * t))) / SR
    s = np.sin(fase) + 0.4 * np.sin(2 * fase) + 0.2 * np.sin(3 * fase)
    s = s * (1 + aspero * bp(ruido(dur), 200, 1200) * 3)
    return s * campana_env(dur, 0.8)


# ======================================================================
#  PESCA DEL ABISMO
# ======================================================================
d = 0.7
latigo = zumbido(0.35, [(0, 600), (0.5, 3200), (1, 900)], 2.0)
guardar('pesca_lanzar', mezclar(pico(latigo, 1.0), en(0.1, pico(carraca(0.55, 40, 8, 3000), 0.45))))

guardar('pesca_cae', reverb(mezclar(pico(burbuja(9, 0.25, 1.0, 0.7), 1.0), pico(gota(3.0), 0.5),
                                    en(0.05, pico(nube(0.4, rampa(0.4, 1.0, 300, 0), 0.6, 2.5), 0.3))), 0.3, 1.0, 3000))

# Que pica: el tiron (un chapoteo seco), burbujas que suben y el brillo de la
# perla. Tiene que oirse en mitad de la pelea y acabar pronto.
tiron = pico(bp(ruido(0.08), 400, 5000) * caida(0.08, 0.012, 0.001), 1.0)
brillo_perla = mezclar(*[en(0.03 * k, modos(1568 * (1.26 ** k), 0.45, CRISTAL, 0.1) * (0.8 ** k)) for k in range(3)])
guardar('pesca_pica', mezclar(tiron, en(0.01, pico(chapuzon(0.25, 0.35), 0.7)), en(0.04, pico(brillo_perla, 0.75)),
                              en(0.02, pico(nube(0.3, 900, 0.5, 2.0), 0.35))))

guardar('pesca_recoger', mezclar(pico(carraca(0.4, 30, 60, 2400), 0.8),
                                 en(0.25, pico(chapuzon(0.2, 0.35), 0.7)), en(0.3, pico(goteo(0.4, 4, 0.0, 0.5), 0.3))))

baja = mezclar(*[en(0.05 * k, burbuja(4 + 1.5 * k, -0.15, 0.8 ** k, 1.0)) for k in range(6)])
guardar('pesca_escapa', reverb(mezclar(pico(baja, 0.9), pico(zumbido(0.4, [(0, 1200), (1, 300)], 1.5), 0.25)), 0.3, 1.0, 2500))

acorde = mezclar(*[en(0.06 * k, modos(f, 1.0, CRISTAL, 0.35) * a) for k, (f, a) in
                   enumerate(((1175, 1.0), (1397, 0.8), (1760, 0.7), (2349, 0.5)))])
guardar('perla_pescada', reverb(mezclar(pico(acorde, 1.0), pico(nube(0.6, 400, 0.4, 1.5), 0.2)), 0.35, 1.6, 7000))

soplo = zumbido(0.6, [(0, 500), (0.3, 2600), (1, 1400)], 1.8)
estela = mezclar(*[en(0.05 + 0.07 * k, modos(2093 * (1 + 0.05 * k), 0.3, CRISTAL, 0.08) * (0.75 ** k)) for k in range(6)])
guardar('perla_lanzar', reverb(mezclar(pico(soplo, 0.8), pico(estela, 0.5)), 0.3, 1.2, 6000))

guardar('perla_corazon', reverb(mezclar(pico(latido(52, 1.0), 1.0), pico(esquirlas(10, 0.35, 1800, 5200), 0.55),
                                        pico(modos(784, 1.4, CRISTAL, 0.5), 0.45)), 0.4, 2.2, 3000), alto=0.85)

# ======================================================================
#  MORENAS
# ======================================================================
for i in range(3):
    bufido = garganta(curva(n_(0.45), [(0, 260 + 30 * i), (0.4, 340), (1, 180)]), 0.45, VOCAL_A, aspereza=0.9, sub=0.1,
                      jitter=0.05, aliento=0.9, fmax=6000)
    guardar('morena_sale', reverb(mezclar(pico(chorro(0.45, 0.8), 0.9), en(0.05, pico(bufido, 0.55)),
                                          en(0.1, pico(goteo(0.5, 6, 0.0, 0.5), 0.35))), 0.25, 0.9, 3500), i + 1)

siseo = bp(ruido(0.45), 2500, 9000) * ventana(0.45, 0.03, 0.15)
guardar('morena_aviso', mezclar(pico(siseo, 0.8), pico(garganta(curva(n_(0.45), [(0, 200), (1, 150)]), 0.45, VOCAL_O,
                                                                    aspereza=1.0, sub=0.3, jitter=0.06, aliento=0.6), 0.6)))

for i in range(2):
    chasquido = mezclar(*[en(0.012 * k, modos(rng.uniform(1700, 2600), 0.06, ((1, 1), (2.3, 0.5)), 0.01)) for k in range(3)])
    grunido = garganta(curva(n_(0.35), [(0, 140 + 20 * i), (1, 95)]), 0.35, VOCAL_O, aspereza=1.0, sub=0.5, jitter=0.06,
                       aliento=0.4)
    guardar('morena_mordisco', mezclar(pico(chasquido, 1.0), pico(bp(ruido(0.05), 300, 4000) * caida(0.05, 0.008), 0.6),
                                       en(0.03, pico(grunido, 0.6))), i + 1)

for i in range(3):
    seco = pb(ruido(0.1), 2200) * caida(0.1, 0.014, 0.001)
    golpe = mezclar(pico(seco, 1.0), pico(boom(150, 70, 0.04, 0.15), 0.6))
    guardar('morena_golpe', mezclar(golpe, en(0.03, pico(chillido(900 + 120 * i, 1500 + 150 * i, 0.3), 0.55)),
                                    en(0.05, pico(chapuzon(0.15, 0.3), 0.3))), i + 1)

trago = mezclar(pico(burbuja(16, -0.3, 1.0, 0.6), 1.0), en(0.05, pico(nube(0.45, rampa(0.45, 1.0, 700, 0), 0.6, 3.0), 0.5)))
guardar('morena_baja', reverb(mezclar(trago, pico(zumbido(0.35, [(0, 900), (1, 250)], 1.4), 0.3)), 0.3, 1.1, 2500))

# ======================================================================
#  CANONES DEL NAUFRAGIO
# ======================================================================
d = 1.2
madera = crujir(d, (10, 40), ((180, 18), (420, 24), (760, 26)), 1.0) * rampa(d, 0.6, 1.0, 0.3)
tierra = pb(ruido(d, 'marron'), 300) * campana_env(d, 1.2)
guardar('canon_sale', reverb(mezclar(pico(madera, 0.7), pico(tierra, 0.6), en(0.3, pico(cadena(0.7, 6, True, False), 0.4)),
                                     en(0.85, pico(boom(80, 40, 0.08, 0.3), 0.5))), 0.3, 1.4, 2500))

guardar('bala_coger', mezclar(pico(modos(310, 0.5, METAL, 0.12), 1.0), pico(modos(470, 0.35, METAL, 0.06), 0.5),
                              pico(bp(ruido(0.03), 300, 3000) * caida(0.03, 0.005), 0.5)))

rodar = filtro_mov(ruido(0.5, 'marron'), curva(n_(0.5), [(0, 300), (1, 160)]), 'band', 3.0) * rampa(0.5, 0.5, 0.2, 1.0)
tope = mezclar(pico(modos(140, 0.6, METAL, 0.18), 1.0), pico(boom(110, 55, 0.06, 0.3), 0.8))
guardar('canon_cargar', mezclar(pico(rodar, 0.6), en(0.48, tope)))

guardar('canon_vacio', mezclar(pico(modos(2200, 0.08, ((1, 1), (1.7, 0.4)), 0.012), 1.0),
                               pico(bp(ruido(0.15), 1500, 6000) * caida(0.15, 0.04), 0.3)))

d = 2.6
estampido = pico(boom(70, 24, 0.35, d), 1.0)
chasquido = pico(bp(ruido(0.2), 300, 8000) * caida(0.2, 0.03, 0.0005), 0.9)
silbido = en(0.05, pico(zumbido(0.5, [(0, 2400), (1, 800)], 3.0), 0.25))
cola = pico(pb(ruido(d, 'marron'), 400) * caida(d, 0.7, 0.01), 0.5)
guardar('canon_disparo', reverb(saturar(mezclar(estampido, chasquido, silbido, cola), 1.6), 0.45, 2.8, 2200), alto=0.9)

guardar('bala_impacto', reverb(mezclar(pico(impacto(1.1, 18), 1.0), pico(boom(60, 28, 0.3), 0.8),
                                       pico(modos(240, 0.8, METAL, 0.2), 0.35)), 0.4, 2.0, 2500), alto=0.88)

guardar('bala_cae', reverb(mezclar(pico(boom(90, 35, 0.12, 0.5), 1.0), pico(pb(ruido(0.4, 'marron'), 900) * caida(0.4, 0.12), 0.6),
                                   pico(impacto(1.3, 10), 0.4)), 0.25, 1.2, 2000))

# ======================================================================
#  DUELO DE CANTO: el arpa del abismo (re menor, como el canto)
# ======================================================================
NOTAS = (587.33, 698.46, 880.0, 1046.5)
for i, f in enumerate(NOTAS):
    pulso = cuerda(f, 1.1, 0.4, 0.9975)
    halo = modos(f * 2, 0.8, CRISTAL, 0.25)
    guardar(f'duelo_nota{i + 1}', reverb(sumergir(mezclar(pico(pulso, 1.0), pico(halo, 0.18)), 5200, 0.05), 0.35, 1.6, 6000))

desafinada = mezclar(pico(cuerda(155, 0.5, 0.8, 0.99), 1.0), pico(cuerda(164, 0.5, 0.8, 0.99), 0.8))
guardar('duelo_fallo', mezclar(pico(desafinada, 1.0), pico(burbuja(12, -0.2, 1.0, 0.8), 0.5)))

guardar('duelo_perfecto', reverb(mezclar(*[en(0.025 * k, modos(2637 * (1.19 ** k), 0.35, CRISTAL, 0.08) * (0.8 ** k))
                                           for k in range(4)]), 0.3, 1.0, 8000))

guardar('duelo_cuenta', mezclar(pico(cuerda(293.66, 0.5, 0.3, 0.996), 1.0), pico(burbuja(7, 0.1, 0.6), 0.3)))

sube = mezclar(*[en(0.09 * k, cuerda(f, 1.4, 0.4, 0.998) * (0.95 ** k)) for k, f in
                 enumerate((587.33, 698.46, 880.0, 1174.66, 1396.9, 1760.0))])
guardar('duelo_gana', reverb(mezclar(pico(sube, 1.0), en(0.45, pico(nube(0.8, 500, 0.4, 1.6), 0.25))), 0.45, 2.4, 7000))

bajan = mezclar(*[en(0.12 * k, cuerda(f, 1.2, 0.5, 0.996) * (0.9 ** k)) for k, f in
                  enumerate((880.0, 698.46, 587.33, 466.16, 440.0))])
ahoga = sumergir(bajan, 1600, 0.5)
guardar('duelo_pierde', reverb(mezclar(pico(ahoga, 1.0), en(0.4, pico(nube(1.0, rampa(1.0, 1.0, 50, 600), 0.8, 4.0), 0.4))),
                               0.5, 2.5, 2500))

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
