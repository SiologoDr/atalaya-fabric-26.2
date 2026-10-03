"""
Edicion del video del Vigia: cortes, rotulos, cortinillas, voz, musica y mezcla.

Entrada: la toma grabada (toma.mkv + toma.wav), las voces (voz_*.mp3), el
poster. Los tiempos de cada toma dentro de la grabacion se midieron buscando
los cortes de camara; el desfase del audio, con el golpe de sincronia.

Uso: python editar.py <carpeta de trabajo> <raiz del proyecto> <salida.mp4>
"""
import os, subprocess, sys
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guion import ESCENAS
import musica

TRAB, RAIZ, SALIDA = sys.argv[1], sys.argv[2], sys.argv[3]
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = musica.SR
W, H = 1920, 1080
FUNDIDO = 0.45
DESFASE_AUDIO = -1.97        # el audio arranco ~2 s tarde: medido con el rugido de la alerta

# (clave, inicio y fin en la grabacion, reencuadre (zoom, centro x, centro y) o None)
TOMAS = [
    ('vigilar', 7.50, 15.10, None),
    ('alerta', 15.20, 19.90, None),
    ('mirada', 20.00, 31.90, None),
    ('cepo', 32.03, 37.85, None),
    ('espalda', 37.93, 45.35, None),
    ('buscar', 45.46, 49.38, None),
    ('muerte', 49.46, 54.38, None),
    ('botin', 54.46, 61.80, (1.6, 0.62, 0.74)),
]
INTRO, CIERRE = 3.2, 9.5
ETIQUETAS = {k: e for k, e, _ in ESCENAS}

def fuente(n, t):
    return ImageFont.truetype('C:/Windows/Fonts/' + n, t)

# ----------------------------------------------------------------------
#  Graficos: rotulos y cortinilla, con el estilo del poster
# ----------------------------------------------------------------------
def rotulo(texto, ruta):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    f = fuente('Oswald-Bold.ttf', 74)
    d = ImageDraw.Draw(im)
    x, y = 110, 820
    ancho = d.textlength(texto, font=f)
    # banda oscura difuminada detras, para que se lea sobre cualquier plano
    banda = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(banda).rectangle((x - 40, y - 30, x + ancho + 60, y + 110), fill=(0, 0, 0, 150))
    im.alpha_composite(banda.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(im)
    d.rectangle((x, y - 8, x + 70, y - 3), fill=(255, 64, 40, 255))
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).text((x, y), texto, font=f, fill=(255, 40, 20, 170))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).text((x, y), texto, font=f, fill=(245, 242, 236, 255))
    im.save(ruta)

def cortinilla(ruta):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.hypot((xx - W / 2) / (W * 0.45), (yy - H / 2) / (H * 0.55))
    col = np.array([8, 6, 14]) + np.array([70, 10, 8]) * np.exp(-d ** 2 * 2.2)[..., None]
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert('RGBA')
    dd = ImageDraw.Draw(im)
    f1 = fuente('Montserrat-Bold.ttf', 30)
    txt = 'A T A L A Y A'
    dd.text(((W - dd.textlength(txt, font=f1)) / 2, H / 2 - 60), txt, font=f1, fill=(255, 180, 58, 255))
    f2 = fuente('Montserrat-SemiBoldItalic.ttf', 34)
    txt = 'presenta una nueva amenaza'
    dd.text(((W - dd.textlength(txt, font=f2)) / 2, H / 2 + 2), txt, font=f2, fill=(200, 194, 205, 255))
    dd.rectangle((W / 2 - 45, H / 2 + 70, W / 2 + 45, H / 2 + 74), fill=(255, 64, 40, 255))
    im.convert('RGB').save(ruta)

# ----------------------------------------------------------------------
#  Linea de tiempo
# ----------------------------------------------------------------------
def linea_de_tiempo():
    dur = [INTRO] + [b - a for _, a, b, _ in TOMAS] + [CIERRE]
    inicios = []
    t = 0.0
    for i, d in enumerate(dur):
        inicios.append(t)
        t += d - FUNDIDO
    total = t + FUNDIDO
    return dur, inicios, total

def run(args):
    r = subprocess.run([FF, '-y', '-v', 'error'] + args, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); raise SystemExit(1)

def video(dur, inicios):
    toma = os.path.join(TRAB, 'toma.mkv')
    entradas, filtros = [], []
    cortina = os.path.join(TRAB, 'cortinilla.png'); cortinilla(cortina)
    poster = os.path.join(RAIZ, 'materiales/promo/vigia_poster_atalaya.png')
    entradas += ['-loop', '1', '-t', f'{INTRO}', '-framerate', '30', '-i', cortina]
    filtros.append(f'[0:v]format=yuv420p,fade=in:st=0:d=0.8,setsar=1[s0]')
    idx = 1
    for k, (clave, a, b, zoom) in enumerate(TOMAS, start=1):
        entradas += ['-ss', f'{a}', '-t', f'{b - a}', '-i', toma]
        cadena = f'[{idx}:v]setpts=PTS-STARTPTS,fps=30'
        if zoom:
            z, cx, cy = zoom
            cw, ch = int(W / z), int(H / z)
            x = int(min(max(cx * W - cw / 2, 0), W - cw)); y = int(min(max(cy * H - ch / 2, 0), H - ch))
            cadena += f',crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos'
        # etalonaje: algo mas de contraste y un punto calido, y vineta
        cadena += ',eq=contrast=1.08:saturation=1.12:gamma=1.05,vignette=PI/4.5,format=yuv420p,setsar=1'
        idx += 1
        etiqueta = ETIQUETAS.get(clave)
        if etiqueta:
            ruta = os.path.join(TRAB, f'rotulo_{clave}.png'); rotulo(etiqueta, ruta)
            entradas += ['-loop', '1', '-t', f'{b - a}', '-framerate', '30', '-i', ruta]
            filtros.append(f'{cadena}[v{k}]')
            filtros.append(f'[{idx}:v]format=rgba,fade=in:st=0.5:d=0.5:alpha=1,fade=out:st=3.6:d=0.5:alpha=1[r{k}]')
            filtros.append(f'[v{k}][r{k}]overlay=0:0:shortest=1,format=yuv420p[s{k}]')
            idx += 1
        else:
            filtros.append(f'{cadena}[s{k}]')
    n = len(TOMAS) + 1
    # UNA sola imagen: zoompan saca d fotogramas por cada fotograma de entrada,
    # asi que con la imagen en bucle multiplicaba la duracion del cierre.
    entradas += ['-i', poster]
    filtros.append(f'[{idx}:v]scale=2112:1188,zoompan=z=\'min(1+0.0004*on,1.1)\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={int(CIERRE * 30)}:s={W}x{H}:fps=30,'
                   f'fade=out:st={CIERRE - 1.2}:d=1.2,format=yuv420p,setsar=1[s{n}]')
    # encadenar con fundidos
    previo = 's0'
    for k in range(1, n + 1):
        off = inicios[k]
        filtros.append(f'[{previo}][s{k}]xfade=transition=fade:duration={FUNDIDO}:offset={off:.3f}[x{k}]')
        previo = f'x{k}'
    salida = os.path.join(TRAB, 'solo_video.mp4')
    run(entradas + ['-filter_complex', ';'.join(filtros), '-map', f'[{previo}]', '-c:v', 'libx264',
                    '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', salida])
    return salida

# ----------------------------------------------------------------------
#  Audio
# ----------------------------------------------------------------------
def leer_audio(ruta):
    tmp = ruta + '.wav'
    run(['-i', ruta, '-ar', str(SR), '-ac', '2', tmp])
    x, _ = sf.read(tmp)
    return x

def colocar(dest, x, t, ganancia=1.0, fundido=0.0):
    i = int(t * SR)
    if i >= len(dest):
        return
    x = x[:len(dest) - i].copy()
    if fundido:
        f = min(int(fundido * SR), len(x) // 2)
        x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]
    dest[i:i + len(x)] += x * ganancia

def audio(dur, inicios, total):
    n = int(total * SR)
    juego = np.zeros((n, 2)); voz = np.zeros((n, 2))
    toma, _ = sf.read(os.path.join(TRAB, 'toma.wav'))
    # el audio del juego llega bajo: se normaliza a su pico
    toma = toma / (np.max(np.abs(toma)) + 1e-9) * 0.8
    tramos_voz = []
    fin_voz = 0.0
    for k, (clave, a, b, _) in enumerate(TOMAS, start=1):
        i0, i1 = int((a + DESFASE_AUDIO) * SR), int((b + DESFASE_AUDIO) * SR)
        colocar(juego, toma[i0:i1], inicios[k], 1.0, fundido=FUNDIDO)
        v = leer_audio(os.path.join(TRAB, f'voz_{clave}.mp3'))
        t = max(inicios[k] + 0.35, fin_voz + 0.25)
        colocar(voz, v, t, 1.0)
        tramos_voz.append((t, t + len(v) / SR))
        fin_voz = t + len(v) / SR
    v = leer_audio(os.path.join(TRAB, 'voz_cierre.mp3'))
    t = max(inicios[-1] + 0.9, fin_voz + 0.25)
    colocar(voz, v, t, 1.0); tramos_voz.append((t, t + len(v) / SR))

    golpes = [inicios[2] + 0.55, inicios[3] + 1.6, inicios[4] + 0.6, inicios[7] + 0.45]
    mus = musica.componer(total, golpes, inicios[-1], inicios[1], inicios[-1] - 2.5)
    # la musica se aparta cuando habla el narrador
    duck = np.ones(n)
    for a, b in tramos_voz:
        duck[int((a - 0.15) * SR):int((b + 0.3) * SR)] = 0.45
    duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode='same')
    mezcla = juego * 0.55 + mus * duck[:, None] * 0.5 + voz * 1.0
    # limitador suave y fundido final
    mezcla = np.tanh(mezcla * 1.1) * 0.92
    f = int(1.5 * SR); mezcla[-f:] *= np.linspace(1, 0, f)[:, None]
    ruta = os.path.join(TRAB, 'mezcla.wav')
    sf.write(ruta, mezcla.astype(np.float32), SR)
    return ruta

def main():
    dur, inicios, total = linea_de_tiempo()
    print('duracion total %.1f s' % total)
    v = video(dur, inicios)
    a = audio(dur, inicios, total)
    run(['-i', v, '-i', a, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
         '-shortest', '-movflags', '+faststart', SALIDA])
    print('ok', SALIDA)

main()
