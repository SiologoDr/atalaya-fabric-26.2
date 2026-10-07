"""
La alerta de los jefes (opiniones de los testers, 07-10-2026: "un sonido especial
para que los que no alcancen a ver puedan escuchar lo que va a pasar; como el
signo de exclamacion del Snake").

Dos sonidos, los mismos para todos los jefes (asi se aprenden una vez):
  jefes/alerta.ogg         el "!": dos campanadas agudas y rapidas, la segunda
                           mas alta, con un golpe grave debajo para que se note
  jefes/alerta_mortal.ogg  para los ataques que matan (la Mirada, la Gran
                           Marea...): un acorde disonante de metal, el "!" encima
                           y un golpe sordo

Salen del jefe (posicionales), asi se sabe tambien de donde viene.

Uso: python alerta_jefes_sonidos.py <raiz del proyecto>
"""
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
SR = 44100
SALIDA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/sounds/jefes')


def t_(dura):
    return np.arange(int(SR * dura)) / SR


def campana(f, dura, caida):
    t = t_(dura)
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (caida * d))
            for r, a, d in ((1.0, 1.0, 1.0), (2.0, 0.45, 0.6), (3.01, 0.22, 0.4), (4.2, 0.1, 0.25)))
    return x * np.minimum(1, t / 0.002)


def golpe(f0, dura):
    t = t_(dura)
    f = f0 + 90 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (dura * 0.35))


def poner(pista, s, en):
    i = int(en * SR)
    pista[i:i + len(s)] += s[:len(pista) - i]


def alerta():
    p = np.zeros(int(SR * 0.6))
    poner(p, campana(1568.0, 0.12, 0.05) * 0.7, 0.0)
    poner(p, campana(2093.0, 0.5, 0.16), 0.075)
    poner(p, golpe(90, 0.18) * 0.6, 0.0)
    return p


def alerta_mortal():
    p = np.zeros(int(SR * 1.0))
    t = t_(0.8)
    acorde = sum(2 * ((f * t) % 1.0) - 1 for f in (220.0, 311.1, 466.2))
    b, a = signal.butter(2, 2400 / (SR / 2), 'low')
    acorde = np.tanh(signal.lfilter(b, a, acorde) * 1.6) * np.exp(-t / 0.28) * np.minimum(1, t / 0.004)
    poner(p, acorde * 0.55, 0.0)
    poner(p, campana(1568.0, 0.12, 0.05) * 0.6, 0.0)
    poner(p, campana(2093.0, 0.6, 0.2) * 0.9, 0.075)
    poner(p, golpe(55, 0.45) * 0.9, 0.0)
    return p


def guardar(nombre, x):
    x = x / max(1e-6, np.abs(x).max()) * 0.89
    os.makedirs(SALIDA, exist_ok=True)
    sf.write(os.path.join(SALIDA, nombre + '.ogg'), x.astype(np.float32), SR, format='OGG', subtype='VORBIS')
    print('ok', nombre)


if __name__ == '__main__':
    guardar('alerta', alerta())
    guardar('alerta_mortal', alerta_mortal())
