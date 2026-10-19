"""Prueba de los creepers rediseñados (sexta vuelta: lo añadido en 2.ª capa) en el mundo MiniJefes (con
run/atalaya_fotos.flag): la fila de los diez de día y de noche, de cerca por grupos, la mecha (lo que hace cada uno al
hincharse), las lianas de la Enredadera, el disparo del Artillero, el oído del Ciego, sus muertes y el menú."""
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
    {'pack': {'description': 'Prueba de los creepers', 'min_format': [107, 0], 'max_format': [107, 1]}}))
json.dump({'values': ['templos_prueba:carga']}, open(os.path.join(BASE, 'data/minecraft/tags/function/load.json'), 'w'))
json.dump({'values': ['templos_prueba:tick']}, open(os.path.join(BASE, 'data/minecraft/tags/function/tick.json'), 'w'))
open(os.path.join(F, 'carga.mcfunction'), 'w').write('scoreboard objectives add tp dummy\nscoreboard players set #t tp 0\n')

ev = {}


def en(t, *cmds):
    ev.setdefault(int(t) + (300 if int(t) >= 200 else 0), []).extend(cmds)


def foto(t, nombre):
    en(t, f'tellraw @a "FOTO {nombre}"')


Y = 100
MOBS = ('atomico', 'ciego', 'tarta', 'matojo', 'marchito', 'enredadera', 'gelatina')
en(20, 'gamerule send_command_feedback false', 'gamerule advance_time false', 'gamerule advance_weather false',
   'gamerule spawn_mobs false', 'gamerule mob_griefing false', 'weather clear 1000000', 'time set 6000',
   'gamemode creative @a', 'forceload add -64 -64 64 176', f'tp @a 0 {Y + 1} 0 180 0')
for k in range(0, 14):
    en(30 + k, f'fill -24 {Y - 1 + k} -30 44 {Y - 1 + k} 20 {"minecraft:grass_block" if k == 0 else "minecraft:air"}')
en(50, 'gamemode survival @a', 'effect give @a minecraft:resistance infinite 255 true',
   'effect give @a minecraft:saturation infinite 255 true', 'effect give @a minecraft:night_vision infinite 0 true', 'tellraw @a "FOV 70"')

# Las arañas junto a una de vanilla, las saltarinas junto a una araña de cueva, y las bombas volando.
NA = '{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}'
NB = '{NoAI:1b,NoGravity:1b,Rotation:[0f,0f],PersistenceRequired:1b}'
fila1 = (('minecraft:spider', 2),)
fila2 = (('minecraft:cave_spider', 2.5),)
bombas = (('atalaya:ambar', 11.5), ('atalaya:carmesi', 15), ('atalaya:negra', 18.5), ('atalaya:abismo', 22))
for e, x in fila1:
    en(240, f'summon {e} {x} {Y} -6 {NA}')
for e, x in fila2:
    en(240, f'summon {e} {x} {Y} -13 {NA}')
for e, x in bombas:
    en(240, f'summon {e} {x} {Y + 1.2} -13 {NB}')
tomas = [
    ('bombas_bombas', (16.75, Y + 0.9, -7.6, 180, 8)),
    ('bombas_bombas_cerca1', (13.25, Y + 1.0, -10.2, 180, 8)),
    ('bombas_bombas_cerca2', (20.25, Y + 1.0, -10.2, 180, 8)),
    ('bombas_bombas_lado', (26.0, Y + 1.4, -11.0, 100, 10)),
]
for k, (nombre, (x, y, z, yaw, pitch)) in enumerate(tomas):
    en(260 + k * 50, f'tp @a {x} {y} {z} {yaw} {pitch}')
    foto(290 + k * 50, nombre)
t = 260 + len(tomas) * 50 + 20
en(t, 'tellraw @a "FIN DE LA PRUEBA BOMBAS"')

lineas = ['scoreboard players add #t tp 1']
for tt in sorted(ev):
    for c in ev[tt]:
        lineas.append(f'execute if score #t tp matches {tt} run {c}')
open(os.path.join(F, 'tick.mcfunction'), 'w', encoding='utf-8').write(chr(10).join(lineas) + chr(10))
print('hasta', t, 'ticks')
