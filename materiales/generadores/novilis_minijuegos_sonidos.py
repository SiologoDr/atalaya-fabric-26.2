"""
Los sonidos de los minijuegos de Novilis (octubre de 2026): El Caballero
Manda, la Forja del Juramento, Piedra, Papel o Tijera y Frio o Caliente.
Todos hechos por nosotros (Juan: "no debemos usar lo que tiene minecraft").
Como rajang_minijuegos_sonidos.py: toma las herramientas de
novilis_sonidos.py y anade sus eventos a sounds.json sin quitar los otros.

  manda_orden       da una orden: el toque de heraldo de su trompeta y su voz por el yelmo
  manda_bien        la has cumplido: un toque de campana de oro
  manda_fallo       no la has cumplido: el fuego te prende (fwump y siseo)
  forja_sale        salen los yunques: la piedra que muele, el acero que suena
  forja_perfecto    golpe perfecto: el martillo en el acero al rojo, limpio y brillante
  forja_bien        golpe bueno: el martillo, menos brillante
  forja_mal         golpe a destiempo: sordo, con chispas y un siseo
  forja_hoja        una hoja forjada: el acero que canta al enfriarse
  forja_vuelan      las hojas salen volando hacia el: el aire que cortan
  piedra_cuenta     cada golpe de la cuenta (piedra... papel...): un tambor de guerra
  piedra_revela     ¡tijera!: el tambor fuerte y el fuego que saca su mano
  piedra_gana       le ganas: un destello de oro
  piedra_pierde     te gana: el fuego que te prende
  caliente_entierra entierra sus brasas: clava la espada y la tierra se traga el fuego
  caliente_hallada  sacas una brasa: la tierra que se abre y la brasa que chisporrotea
  caliente_revienta las que quedan revientan en lava
  mini_exito        ganado: la fanfarria de su trompeta, en mayor
  mini_fallo        perdido: la fanfarria que baja y el fuego que ruge

Uso: python novilis_minijuegos_sonidos.py <raiz del proyecto>
"""
import collections, json, os, sys, tempfile

RAIZ = sys.argv[1]
AQUI = os.path.dirname(os.path.abspath(__file__))
fuente = open(os.path.join(AQUI, 'novilis_sonidos.py'), encoding='utf-8').read()
corte = fuente.index('#  AMBIENTE: el fuego de las grietas')
corte = fuente.rindex('# ====', 0, corte)
herramientas = fuente[:corte]

falsa = tempfile.mkdtemp()
_argv = sys.argv
sys.argv = [_argv[0], falsa]
ns = {'__name__': 'novilis_sonidos_herramientas'}
exec(compile(herramientas, 'novilis_sonidos.py', 'exec'), ns)
sys.argv = _argv
ns['OUT'] = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/novilis')
ns['EVENTOS'] = collections.OrderedDict()
globals().update({k: v for k, v in ns.items() if not k.startswith('__') and k != 'RAIZ'})
import numpy as np

rng = np.random.default_rng(20261010)
ns['rng'] = rng


def toque(notas, paso=0.16, dur=0.5, vel=0.8):
    """Un toque de trompeta (las notas en texto, como 'C5 E5 G5')."""
    capas = []
    for k, n in enumerate(notas.split()):
        capas.append(en(paso * k, nota_metal(midi(n), dur, vel, 'leg' if k else 'acc')))
    return mezcla_(*capas)


def mezcla_(*capas):
    return mezclar(*capas)


# ======================================================================
#  EL CABALLERO MANDA
# ======================================================================
voz = garganta(curva(n_(0.7), [(0, 120), (0.3, 150), (1, 110)]), 0.7, formantes_voz(H_O, H_A, 0.7), aspereza=0.7, sub=0.3,
               jitter=0.04, aliento=0.5)
guardar('manda_orden', reverb(mezclar(pico(toque('G4 C5', 0.12, 0.45, 0.9), 0.8), en(0.28, pico(yelmo(voz, 0.5), 0.9))),
                              0.35, 2.0, 5000), largo=2.2)

guardar('manda_bien', reverb(mezclar(pico(campana(1046.5, 0.8), 0.8), en(0.06, pico(campana(1568.0, 0.6), 0.5))), 0.3, 1.4, 8000),
        techo=-16, largo=1.4)

guardar('manda_fallo', reverb(mezclar(pico(ignicion(0.9, 0.8, 3000.0, 70.0), 1.0), en(0.15, pico(siseo(0.6), 0.5)),
                                      en(0.1, pico(chasquidos(0.6, 40, 1.0), 0.4))), 0.25, 1.2), largo=1.5)

# ======================================================================
#  LA FORJA DEL JURAMENTO
# ======================================================================
d = 2.0
muele = moler(1.6, 1.2, (20, 50), 0.8) * campana_env(1.6, 1.2)
guardar('forja_sale', reverb(mezclar(pico(muele, 0.7), en(0.9, pico(metal(330, None, 0.6), 0.6)), en(1.1, pico(boom(80, 40, 0.1, 0.5), 0.6))),
                             0.3, 1.8), largo=2.6)

for nombre, f, brillo in (('forja_perfecto', 520, 1.0), ('forja_bien', 440, 0.6)):
    golpe = mezclar(pico(metal(f, None, 0.5, PLACA, 1.0, 0.0025, brillo), 1.0), pico(bp(ruido(0.04), 2000, 9000) * caida(0.04, 0.006), 0.6))
    if nombre == 'forja_perfecto':
        golpe = mezclar(golpe, en(0.02, pico(destellos(0.5, 30, 3000, 8000), 0.4)), en(0.03, pico(campana(1318.5, 0.6), 0.3)))
    guardar(nombre, reverb(mezclar(golpe, en(0.02, pico(chasquidos(0.4, 60 if brillo > 0.8 else 30, 1.0), 0.35))), 0.25, 1.4, 7000),
            largo=1.4)

guardar('forja_mal', reverb(mezclar(pico(boom(140, 80, 0.05, 0.3), 0.8), pico(metal(240, None, 0.15, PLACA, 0.6), 0.5),
                                    en(0.05, pico(siseo(0.5), 0.5))), 0.2, 1.0), largo=1.0)

canta = metal(660, 2.5, 1.2, PLACA, 0.4, 0.004, 0.9)
guardar('forja_hoja', reverb(mezclar(pico(canta, 0.8), en(0.1, pico(siseo(1.2, 2000, 8000), 0.5)), pico(campana(784.0, 1.2), 0.4)),
                             0.35, 2.2, 7000), largo=2.6)

guardar('forja_vuelan', reverb(mezclar(pico(pasada(1.2, 1800, 400, 1.6, 0.4), 0.9), en(0.9, pico(clang(260, 0.6, 1.4), 0.9))),
                               0.3, 1.8), largo=2.4)

# ======================================================================
#  PIEDRA, PAPEL O TIJERA
# ======================================================================
def tambor(fuerza=1.0):
    piel = pb(ruido(0.3, 'rosa'), 900) * caida(0.3, 0.06)
    return mezclar(pico(boom(90, 45, 0.12, 0.5), fuerza), pico(piel, 0.5 * fuerza))


guardar('piedra_cuenta', reverb(tambor(0.9), 0.25, 1.2, 3000), largo=1.0)
guardar('piedra_revela', reverb(mezclar(pico(tambor(1.2), 1.0), en(0.05, pico(ignicion(0.8, 0.9, 3200.0, 60.0), 0.7)),
                                        en(0.05, pico(clang(380, 0.5, 1.0), 0.4))), 0.3, 1.6), largo=1.8)
guardar('piedra_gana', reverb(mezclar(pico(destellos(0.6, 50, 3000, 8000), 0.6), pico(campana(1174.66, 0.7), 0.6)), 0.3, 1.4, 8000),
        techo=-16, largo=1.4)
guardar('piedra_pierde', reverb(mezclar(pico(ignicion(0.8, 0.7, 2600.0, 70.0), 1.0), en(0.1, pico(siseo(0.5), 0.4))), 0.25, 1.2),
        largo=1.3)

# ======================================================================
#  FRIO O CALIENTE
# ======================================================================
d = 2.6
clava = mezclar(pico(clang(200, 0.8, 1.6), 0.8), pico(golpe_tierra(1.0, 0.8, 0.6, 2.2), 0.9))
traga = mezclar(*[en(0.5 + 0.25 * k, pico(burbuja_lava(90 + 20 * k, 0.3, 0.8), 0.5)) for k in range(4)])
guardar('caliente_entierra', reverb(mezclar(clava, pico(traga, 0.6), en(0.6, pico(retumbo(1.8, 90, 2.0, 0.5, 1.0), 0.5))), 0.3, 2.0),
        limite=0.55, largo=3.0)

guardar('caliente_hallada', reverb(mezclar(pico(rajar_roca(6, 0.05, 1.0, 0.9), 0.7), en(0.08, pico(chasquidos(0.8, 50, 1.2), 0.6)),
                                           en(0.12, pico(tono_sube(0.6, 300, 900, 3, 0.5), 0.5)), en(0.2, pico(campana(987.77, 0.8), 0.4))),
                                   0.3, 1.6, 7000), largo=2.0)

guardar('caliente_revienta', reverb(explosion(1.0, 2.6, 1.0, 0.8, 1.0, 0.6), 0.3, 2.0), limite=0.5, largo=3.0)

# ======================================================================
#  EL FINAL DE CADA UNO
# ======================================================================
guardar('mini_exito', reverb(mezclar(pico(toque('C5 E5 G5 C6', 0.14, 0.7, 0.9), 1.0), en(0.4, pico(destellos(1.0, 25, 3000, 8000), 0.3))),
                             0.4, 2.6, 7000), largo=3.4)
guardar('mini_fallo', reverb(mezclar(pico(toque('G4 Eb4 C4', 0.18, 0.7, 0.8), 0.9), en(0.3, pico(llama(1.6, 0.8, 0.8), 0.5))), 0.4, 2.4, 4000),
        largo=3.2)

# ----------------------------------------------------------------------
#  sounds.json: se anaden (o se rehacen) solo estos eventos.
# ----------------------------------------------------------------------
EVENTOS = ns['EVENTOS']
ruta = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds.json')
with open(ruta, encoding='utf-8') as fh:
    datos = json.load(fh, object_pairs_hook=collections.OrderedDict)
for ev, archivos in EVENTOS.items():
    datos['novilis.' + ev] = {'subtitle': 'subtitles.atalaya.novilis.' + ev,
                              'sounds': ['atalaya:novilis/' + a for a in archivos]}
with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
    json.dump(datos, fh, indent=2, ensure_ascii=False)
    fh.write('\n')
print(len(EVENTOS), 'eventos,', sum(len(v) for v in EVENTOS.values()), 'archivos')
