"""Prueba de la pestana del mod en el creativo (19-10-2026) en el mundo MiniJefes (con run/atalaya_fotos.flag).

Abre el inventario de creativo en la pestana Atalaya y la fotografia arriba, en medio y abajo (pestana_0, pestana_1,
pestana_2), y en las de los huevos y el combate de Minecraft, para ver que alli ya no queda nada del mod
(pestana_huevos, pestana_combate).
"""
import json
import os
import shutil

RUN = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'run'))
MUNDO = RUN + '/saves/MiniJefes'
if os.path.exists(MUNDO):
    shutil.rmtree(MUNDO)
os.makedirs(MUNDO + '/data/minecraft')
shutil.copy(RUN + '/saves/PruebaVigia/level.dat', MUNDO + '/level.dat')
for f in ('world_gen_settings.dat', 'game_rules.dat'):
    shutil.copy(RUN + '/saves/PruebaVigia/data/minecraft/' + f, MUNDO + '/data/minecraft/' + f)
BASE = MUNDO + '/datapacks/templos_prueba'
F = os.path.join(BASE, 'data', 'templos_prueba', 'function')
os.makedirs(F, exist_ok=True)
os.makedirs(os.path.join(BASE, 'data', 'minecraft', 'tags', 'function'), exist_ok=True)
open(os.path.join(BASE, 'pack.mcmeta'), 'w').write(json.dumps(
    {'pack': {'description': 'Prueba de la pestana', 'min_format': [107, 0], 'max_format': [107, 1]}}))
json.dump({'values': ['templos_prueba:carga']}, open(os.path.join(BASE, 'data/minecraft/tags/function/load.json'), 'w'))
json.dump({'values': ['templos_prueba:tick']}, open(os.path.join(BASE, 'data/minecraft/tags/function/tick.json'), 'w'))
open(os.path.join(F, 'carga.mcfunction'), 'w').write('scoreboard objectives add tp dummy\nscoreboard players set #t tp 0\n')

ev = {}


def en(t, *cmds):
    ev.setdefault(int(t), []).extend(cmds)


en(20, 'gamerule send_command_feedback false', 'gamerule advance_time false', 'time set 6000',
   'gamemode creative @a')
t = 60
tomas = [('atalaya:atalaya', 0, 'pestana_0'), ('atalaya:atalaya', 0.5, 'pestana_1'), ('atalaya:atalaya', 1, 'pestana_2'),
         ('minecraft:spawn_eggs', 1, 'pestana_huevos'), ('minecraft:combat', 0.6, 'pestana_combate')]
for pestana, bajada, nombre in tomas:
    en(t, f'tellraw @a "CREATIVO {pestana} {bajada}"')
    en(t + 20, f'tellraw @a "FOTO {nombre}"')
    t += 40
en(t, 'tellraw @a "CERRAR"')
en(t + 40, 'tellraw @a "FIN DE LA PRUEBA PESTANA"')

lineas = ['scoreboard players add #t tp 1']
for tt in sorted(ev):
    for c in ev[tt]:
        lineas.append(f'execute if score #t tp matches {tt} run {c}')
open(os.path.join(F, 'tick.mcfunction'), 'w', encoding='utf-8').write(chr(10).join(lineas) + chr(10))
print('hasta', t + 40, 'ticks')
