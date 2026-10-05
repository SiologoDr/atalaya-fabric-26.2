"""
Sonidos del Vigia, sintetizados desde cero. Nada de vanilla.

Ingredientes de la paleta sonora, todos sacados del propio bicho:
  - HIERRO del farol: parciales inarmonicos (campana rota), con batido
  - CRISTAL del farol: parciales agudos y finos, decaimiento largo
  - CADENA: tintineos cortos y aleatorios
  - VOZ: diente de sierra grave con formantes y distorsion suave
  - ALIENTO: ruido filtrado en banda
  - FUEGO: siseo de ruido rosa con chasquidos
Todo mono (Minecraft solo posiciona en 3D los mono) a 44,1 kHz, Vorbis.
"""
import numpy as np
import soundfile as sf
from scipy import signal
import os, sys

SR = 44100
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(1234)

def t_(dur):
    return np.arange(int(dur * SR)) / SR

def env(dur, ataque=0.005, caida=None, sostener=0.0, curva=4.0):
    """Envolvente: ataque lineal, meseta y caida exponencial."""
    t = t_(dur)
    e = np.ones_like(t)
    a = int(ataque * SR)
    if a > 0:
        e[:a] = np.linspace(0, 1, a)
    s = a + int(sostener * SR)
    if s < len(t):
        n = len(t) - s
        e[s:] = np.exp(-curva * np.linspace(0, 1, n))
    return e

def ruido(dur, color='blanco'):
    n = rng.standard_normal(int(dur * SR))
    if color == 'rosa':
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        n = signal.lfilter(b, a, n)
    elif color == 'marron':
        n = np.cumsum(n); n = n - signal.lfilter([1], [1, -0.995], n) * 0.0 ; n = signal.lfilter([1, -1], [1, -0.995], n)
    return n / (np.max(np.abs(n)) + 1e-9)

def banda(x, lo, hi, orden=2):
    sos = signal.butter(orden, [lo, hi], btype='bandpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x)

def paso_bajo(x, f, orden=2):
    return signal.sosfilt(signal.butter(orden, f, btype='lowpass', fs=SR, output='sos'), x)

def paso_alto(x, f, orden=2):
    return signal.sosfilt(signal.butter(orden, f, btype='highpass', fs=SR, output='sos'), x)

def glide(f0, f1, dur, curva='exp'):
    t = t_(dur)
    if curva == 'exp':
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * (t / dur)
    return 2 * np.pi * np.cumsum(f) / SR

def sierra(fase):
    return 2 * ((fase / (2 * np.pi)) % 1.0) - 1

def mezclar(*capas):
    n = max(len(c) for c in capas)
    out = np.zeros(n)
    for c in capas:
        out[:len(c)] += c
    return out

def desplazar(x, seg):
    return np.concatenate([np.zeros(int(seg * SR)), x])

def saturar(x, k=2.0):
    return np.tanh(k * x) / np.tanh(k)

def reverb(x, mezcla=0.3, tamano=1.0, cola=2.0):
    """Schroeder: cuatro peines en paralelo y dos pasatodo en serie."""
    x = np.concatenate([x, np.zeros(int(cola * SR))])
    wet = np.zeros_like(x)
    for d, g in ((1557, 0.84), (1617, 0.83), (1491, 0.82), (1422, 0.81)):
        d = int(d * tamano)
        a = np.zeros(d + 1); a[0] = 1; a[d] = -g
        wet += signal.lfilter([1], a, x)
    for d, g in ((225, 0.7), (556, 0.7)):
        b = np.zeros(d + 1); b[0] = -g; b[d] = 1
        a = np.zeros(d + 1); a[0] = 1; a[d] = -g
        wet = signal.lfilter(b, a, wet)
    wet = paso_bajo(wet, 6000)
    return (1 - mezcla) * x + mezcla * wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(x))

def campana(f, dur, parciales=((1, 1), (2.76, 0.5), (5.4, 0.25), (8.93, 0.12)), caida=5.0, batido=1.5):
    """Hierro: parciales inarmonicos, los agudos mueren antes."""
    t = t_(dur)
    s = np.zeros_like(t)
    for r, a in parciales:
        fr = f * r
        if fr > SR / 2.2:
            continue
        s += a * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) * np.exp(-caida * r ** 0.6 * t) \
             * (1 + 0.15 * np.sin(2 * np.pi * batido * r * t))
    return s

def cristal(f, dur, caida=3.0):
    return campana(f, dur, parciales=((1, 1), (2.32, 0.6), (4.25, 0.35), (6.63, 0.2)), caida=caida, batido=0.7)

def cadena(dur, golpes=6, densidad=1.0):
    out = np.zeros(int(dur * SR))
    for _ in range(golpes):
        t0 = rng.uniform(0, dur * 0.8) * densidad
        c = campana(rng.uniform(1800, 3800), 0.18, caida=18.0) * rng.uniform(0.3, 1.0)
        c += banda(ruido(0.18), 3000, 9000) * env(0.18, 0.001, curva=40) * 0.4
        i = int(t0 * SR)
        n = min(len(c), len(out) - i)
        if n > 0:
            out[i:i + n] += c[:n]
    return out

def voz(f0, f1, dur, aspereza=0.3, formantes=((500, 1.0), (900, 0.6), (2400, 0.25)), distorsion=2.5, vibrato=5.0):
    """Garganta grave: sierra con jitter y formantes de vocal oscura."""
    t = t_(dur)
    base = f0 * (f1 / f0) ** (t / dur)
    jitter = 1 + 0.02 * paso_bajo(rng.standard_normal(len(t)), 30) * 8 + 0.01 * np.sin(2 * np.pi * vibrato * t)
    fase = 2 * np.pi * np.cumsum(base * jitter) / SR
    s = sierra(fase) + 0.5 * sierra(fase * 1.005)
    s += aspereza * ruido(dur, 'rosa')
    out = np.zeros_like(s)
    for fc, g in formantes:
        out += g * banda(s, fc * 0.8, fc * 1.25)
    return saturar(out / (np.max(np.abs(out)) + 1e-9), distorsion)

def aliento(dur, lo=300, hi=1800):
    e = np.sin(np.pi * np.linspace(0, 1, int(dur * SR))) ** 2
    return banda(ruido(dur, 'rosa'), lo, hi) * e

def golpe_grave(f0=70, f1=35, dur=0.35):
    return np.sin(glide(f0, f1, dur)) * env(dur, 0.002, curva=7)

def chasquido(dur=0.03, lo=1500, hi=7000):
    return banda(ruido(dur), lo, hi) * env(dur, 0.0005, curva=12)

def siseo(dur, lo=2000, hi=9000):
    return banda(ruido(dur), lo, hi)

def normalizar(x, pico=0.89):
    x = x - np.mean(x)
    # fundido de 5 ms en los extremos para que no haya chasquido de corte
    f = int(0.005 * SR)
    x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    return x * pico / (np.max(np.abs(x)) + 1e-9)

def guardar(nombre, x):
    x = normalizar(x)
    sf.write(os.path.join(OUT, nombre + '.ogg'), x.astype(np.float32), SR, format='OGG', subtype='VORBIS')

# ======================================================================
#  AMBIENTE (en calma): respira dentro del farol, crujen las cadenas
# ======================================================================
for i in range(3):
    d = 2.6
    resp = aliento(d * 0.8, 180 + 40 * i, 900) * 0.8
    zumbido = np.sin(glide(52 + 4 * i, 47 + 3 * i, d)) * np.sin(np.pi * np.linspace(0, 1, int(d * SR))) * 0.35
    vidrio = cristal(1240 + 180 * i, d, caida=1.6) * 0.12
    guardar(f'ambiente{i + 1}', mezclar(desplazar(resp, 0.2), zumbido, cadena(d, golpes=3 + i) * 0.35, vidrio))

# ======================================================================
#  ACECHO (ambiente con presa): grunido que vibra en el hierro
# ======================================================================
for i in range(2):
    d = 1.6
    g = voz(62 + 8 * i, 48, d, aspereza=0.5, distorsion=4) * env(d, 0.15, curva=2.5, sostener=0.5)
    resonancia = campana(220 + 30 * i, d, caida=2.5) * 0.25 * env(d, 0.2, curva=2)
    guardar(f'acecho{i + 1}', reverb(mezclar(g, resonancia), 0.2, cola=0.6))

# ======================================================================
#  PASOS: hueso contra el suelo, y el farol que tintinea al apoyar
# ======================================================================
for i in range(4):
    d = 0.4
    golpe = golpe_grave(85 + 10 * i, 40, d) * 0.9
    hueso = chasquido(0.05, 900, 4000) * 0.8
    tierra = paso_bajo(ruido(0.12, 'rosa'), 800) * env(0.12, 0.001, curva=10) * 0.6
    guardar(f'paso{i + 1}', mezclar(golpe, hueso, tierra, desplazar(cadena(0.25, golpes=2) * 0.25, 0.03)))

# ======================================================================
#  HERIDO: clang del farol, cristal que se raja, quejido corto
# ======================================================================
for i in range(3):
    clang = campana(310 + 70 * i, 0.9, caida=4.5) * 0.8
    raja = mezclar(*[desplazar(chasquido(0.02, 3000, 10000) * rng.uniform(0.3, 0.8), rng.uniform(0, 0.08)) for _ in range(6)])
    queja = voz(95 + 15 * i, 60, 0.5, distorsion=3) * env(0.5, 0.02, curva=3) * 0.7
    guardar(f'herido{i + 1}', mezclar(clang, raja, desplazar(queja, 0.04), golpe_grave(110, 50, 0.25) * 0.5))

# ======================================================================
#  MUERTE: el ultimo aliento. Quejido que baja, el hierro que cede.
# ======================================================================
d = 3.0
estertor = voz(110, 32, d, aspereza=0.6, distorsion=3.5) * env(d, 0.05, curva=2.2, sostener=0.6)
crujido = mezclar(*[desplazar(chasquido(0.03, 600, 3000) * rng.uniform(0.2, 0.6), rng.uniform(0.3, 1.6)) for _ in range(25)])
lamento = (cristal(880, d, caida=1.2) + cristal(830, d, caida=1.2)) * 0.15  # batido entre dos cristales: inquietud
grave = golpe_grave(60, 28, 1.2) * 0.6
guardar('muerte', reverb(mezclar(estertor, crujido * 0.7, lamento, grave), 0.3, cola=1.2))

# ======================================================================
#  APAGARSE: la llama del farol muere. Siseo, soplo y el cristal enfria.
# ======================================================================
d = 1.6
soplo = paso_bajo(ruido(d, 'rosa'), 900) * env(d, 0.01, curva=6) * 0.7
sis = siseo(d) * env(d, 0.005, curva=3.5) * 0.5
whoomp = np.sin(glide(140, 40, 0.5)) * env(0.5, 0.01, curva=6) * 0.8
enfria = mezclar(*[desplazar(cristal(rng.uniform(2500, 4200), 0.6, caida=8) * 0.15, rng.uniform(0.4, 1.4)) for _ in range(5)])
guardar('apagarse', mezclar(whoomp, soplo, sis, enfria))

# ======================================================================
#  FAROL CAE: el farol suelto golpea el suelo y rueda
# ======================================================================
d = 1.3
golpe = mezclar(campana(240, d, caida=3.5) * 0.9, golpe_grave(90, 40, 0.3))
rebote = desplazar(campana(255, 0.6, caida=6) * 0.4, 0.22)
rueda = mezclar(*[desplazar(campana(rng.uniform(600, 1500), 0.15, caida=20) * 0.25, 0.35 + k * 0.09 + rng.uniform(0, 0.03)) for k in range(8)])
roto = mezclar(*[desplazar(chasquido(0.03, 2500, 11000) * 0.6, rng.uniform(0, 0.05)) for _ in range(8)])
guardar('farol_cae', mezclar(golpe, rebote, rueda, roto))

# ======================================================================
#  ALERTA: el rugido. Garganta que sube, hierro que resuena en barrido.
# ======================================================================
d = 1.4
rugido = voz(70, 115, d, aspereza=0.7, distorsion=5, formantes=((420, 1.0), (750, 0.8), (2100, 0.4))) \
         * env(d, 0.08, curva=2.5, sostener=0.55)
chillido = np.sin(glide(900, 1400, d) + 3 * np.sin(glide(60, 90, d))) * env(d, 0.25, curva=3, sostener=0.3) * 0.18
peine = rugido.copy()
for k, retardo in enumerate((0.0071, 0.0113)):
    n = int(retardo * SR)
    peine[n:] += 0.6 * rugido[:-n]
guardar('alerta', reverb(mezclar(peine, chillido, golpe_grave(55, 30, 0.6) * 0.6), 0.25, cola=1.0))

# ======================================================================
#  CEPO: abrir (tension), cerrar (la trampa), fallo (al aire)
# ======================================================================
d = 0.55
# crujidos cada vez mas seguidos: la tension de los brazos al abrirse
clicks = np.zeros(int(d * SR)); t0 = 0.0; paso = 0.07
while t0 < d - 0.03:
    c = chasquido(0.025, 700, 3500) * (0.3 + t0)
    i = int(t0 * SR); clicks[i:i + len(c)] += c[:len(clicks) - i]
    t0 += paso; paso = max(paso * 0.82, 0.014)
susurro = banda(ruido(d, 'rosa'), 400, 2500) * np.linspace(0, 1, int(d * SR)) ** 2 * 0.6
guardar('cepo_abrir', mezclar(clicks, susurro, cadena(d, golpes=5) * 0.4, voz(55, 70, d, distorsion=3) * 0.35 * np.linspace(0.2, 1, int(d * SR))))

d = 0.7
cierre = mezclar(chasquido(0.012, 1500, 12000) * 1.0,
                 campana(520, d, parciales=((1, 1), (1.53, 0.8), (2.91, 0.5), (4.7, 0.3)), caida=7) * 0.8,
                 golpe_grave(120, 45, 0.3),
                 desplazar(cadena(0.3, golpes=4) * 0.4, 0.02))
guardar('cepo_cerrar', reverb(cierre, 0.15, cola=0.4))

d = 0.45
zas = banda(ruido(d), 300, 3000) * env(d, 0.06, curva=5)
zas = signal.sosfilt(signal.butter(2, 1200, 'lowpass', fs=SR, output='sos'), zas) * 0.5 + zas * 0.5
guardar('cepo_fallo', zas)

# ======================================================================
#  MIRADA: carga (2 s que suben), disparo (la maldicion), corte (se apaga)
# ======================================================================
d = 2.0
t = t_(d)
tremolo = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(4 + 22 * (t / d) ** 2) / SR)
carga = sum(np.sin(glide(f, f * 3.2, d)) * a for f, a in ((180, 1.0), (271, 0.6), (362, 0.4), (543, 0.25)))
carga = carga * tremolo * (t / d) ** 1.3
brillo = cristal(2200, d, caida=0.3) * (t / d) ** 3 * 0.3
guardar('mirada_carga', mezclar(carga, brillo, aliento(d, 1500, 6000) * 0.15 * (t / d)))

d = 2.2
# acorde disonante: tritono y segunda menor. Suena a "algo no esta bien".
acorde = sum(campana(f, d, caida=1.6, parciales=((1, 1), (2.0, 0.4), (3.01, 0.2), (4.2, 0.1))) for f in (311, 440, 466, 659))
boom = golpe_grave(75, 25, 1.4) * 1.2
susurros = banda(ruido(d, 'rosa'), 600, 3000) * env(d, 0.3, curva=3) * 0.35
inverso = cristal(1320, 0.5, caida=4)[::-1] * 0.4  # cristal al reves: aspira justo antes del golpe
guardar('mirada_disparo', reverb(mezclar(inverso, desplazar(mezclar(acorde * 0.6, boom, susurros), 0.48)), 0.35, cola=1.5))

d = 0.7
corte = np.sin(glide(700, 90, d)) * env(d, 0.005, curva=5) * 0.6 + siseo(d) * env(d, 0.005, curva=6) * 0.5
guardar('mirada_corte', corte)

# ======================================================================
#  RAYO: el impacto del proyectil. Chisporroteo electrico, golpe sordo y un
#  eco corto del acorde de la maldicion, para que se reconozca de quien es.
# ======================================================================
d = 1.2
chisporroteo = mezclar(*[desplazar(chasquido(0.015, 2000, 12000) * rng.uniform(0.3, 1.0), rng.uniform(0, 0.35) ** 1.5) for _ in range(40)])
golpe = golpe_grave(160, 45, 0.4)
eco = sum(campana(f, d, caida=4.0, parciales=((1, 1), (2.0, 0.3))) for f in (440, 466, 659)) * 0.25
sis = siseo(0.6, 3000, 10000) * env(0.6, 0.002, curva=6) * 0.5
guardar('rayo_impacto', reverb(mezclar(golpe, chisporroteo, sis, eco), 0.2, cola=0.6))

# el zumbido del rayo al salir: una nota que cae con el disparo
d = 0.8
zumbido = np.sin(glide(900, 300, d) + 2.5 * np.sin(glide(70, 40, d))) * env(d, 0.005, curva=4)
guardar('rayo_vuelo', mezclar(zumbido * 0.7, aliento(d, 2000, 8000) * 0.3))

# ======================================================================
#  TAMBALEO: le dan por la espalda. Cristal que cruje, hierro que oscila.
# ======================================================================
d = 0.9
osc = campana(180, d, caida=3, batido=6) * 0.7
crack = mezclar(*[desplazar(chasquido(0.02, 2500, 11000), k * 0.012) * (1 - k * 0.1) for k in range(8)])
gruñido = voz(80, 140, 0.35, distorsion=4) * env(0.35, 0.01, curva=3) * 0.8
guardar('tambaleo', mezclar(crack, osc, gruñido))

# ======================================================================
#  BUSCAR: perdio la presa. Tres olfateos y las cadenas al girar.
# ======================================================================
d = 1.4
olfato = mezclar(*[desplazar(aliento(0.16, 700, 3500) * 0.9, 0.1 + k * 0.22) for k in range(3)])
guardar('buscar', mezclar(olfato, desplazar(cadena(0.8, golpes=5) * 0.4, 0.6), desplazar(voz(60, 52, 0.6, distorsion=2) * env(0.6, 0.1) * 0.4, 0.8)))

# ======================================================================
#  OJO (item): revelar. Arpegio de cristal que sube y un soplo.
# ======================================================================
d = 1.6
arpegio = mezclar(*[desplazar(cristal(f, 1.2, caida=3) * 0.5, k * 0.07) for k, f in enumerate((523, 659, 784, 988, 1175, 1568))])
guardar('ojo_usar', reverb(mezclar(arpegio, aliento(1.0, 800, 5000) * 0.3), 0.35, cola=1.0))

print('\n'.join(sorted(os.listdir(OUT))))
