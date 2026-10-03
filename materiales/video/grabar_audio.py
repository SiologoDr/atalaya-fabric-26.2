"""Graba lo que suena por los altavoces (loopback) durante N segundos."""
import sys, time
import numpy as np
import soundcard as sc
import soundfile as sf

salida, segundos = sys.argv[1], float(sys.argv[2])
SR = 48000
altavoz = sc.default_speaker()
mic = sc.get_microphone(id=str(altavoz.name), include_loopback=True)
bloques = []
with mic.recorder(samplerate=SR, channels=2) as rec:
    inicio = time.time()
    while time.time() - inicio < segundos:
        bloques.append(rec.record(numframes=SR // 10))
audio = np.concatenate(bloques)
sf.write(salida, audio, SR)
print(f'inicio={inicio:.3f} muestras={len(audio)}')
