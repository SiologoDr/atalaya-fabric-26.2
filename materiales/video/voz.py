"""Sintetiza cada frase del guion con edge-tts y apunta su duracion."""
import asyncio, json, os, sys
import edge_tts
import soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guion import ESCENAS, VOZ, RITMO, TONO

SALIDA = sys.argv[1]
os.makedirs(SALIDA, exist_ok=True)

async def una(clave, frase):
    ruta = os.path.join(SALIDA, f'voz_{clave}.mp3')
    await edge_tts.Communicate(frase, VOZ, rate=RITMO, pitch=TONO).save(ruta)
    return ruta

async def main():
    duraciones = {}
    for clave, _, frase in ESCENAS:
        ruta = await una(clave, frase)
        info = sf.info(ruta) if ruta.endswith('.wav') else None
        duraciones[clave] = ruta
    print(json.dumps(duraciones, indent=1))

asyncio.run(main())
