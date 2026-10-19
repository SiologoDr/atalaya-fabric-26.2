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
   'effect give @a minecraft:saturation infinite 255 true', 'tellraw @a "FOV 70"')

# A. La fila de los diez, de cerca (en dos mitades), de día y de noche; y cada uno de frente.
for i, m in enumerate(MOBS):
    x = 2.75 + i * 2.5
    en(240, f'summon atalaya:{m} {x} {Y} -6 {{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}}')
en(250, f'tp @a 6.5 {Y + 0.3} 1.5 180 8')
foto(282, 'creepers_mitad1')
en(276, f'tp @a 16.5 {Y + 0.3} 1.5 180 8')
foto(290, 'creepers_mitad2')
for i, m in enumerate(MOBS):
    x = 2.75 + i * 2.5
    en(300 + i * 50, f'tp @a {x + 0.9} {Y} -3.4 160 14')
    foto(330 + i * 50, f'creepers_{m}')
T0 = 300 + len(MOBS) * 50 + 10
# De muy cerca (la textura), cada uno.
for i, m in enumerate(MOBS):
    x = 2.75 + i * 2.5
    alto = 0.2 if m == 'matojo' else 0.9
    en(T0 + i * 50, f'tp @a {x + 0.45} {Y + alto} -4.55 165 {28 if m == "matojo" else 12}')
    foto(T0 + 30 + i * 50, f'creepers_cerca_{m}')
T = T0 + len(MOBS) * 50 + 10
en(T, 'time set 18000')
en(T + 2, f'tp @a 6.5 {Y + 0.3} 1.5 180 8')
foto(T + 40, 'creepers_noche1')
en(T + 50, f'tp @a 16.5 {Y + 0.3} 1.5 180 8')
foto(T + 76, 'creepers_noche2')
en(T + 90, 'time set 6000')
for m in MOBS:
    en(T + 50, f'kill @e[type=atalaya:{m}]')
en(T + 50, f'tp @a 14 {Y} 3 180 6')
foto(T + 62, 'creepers_muerte')
en(T + 90, 'kill @e[type=item]')

# Junto a un creeper de vanilla (para ver el tamaño del píxel): el de vanilla y los cuatro nuevos, en fila.
C = T + 130
en(C, f'summon minecraft:creeper 4 {Y} -14 {{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}}',
   f'summon atalaya:ciego 6.5 {Y} -14 {{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}}',
   f'summon atalaya:matojo 9 {Y} -14 {{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}}',
   f'summon atalaya:marchito 11.5 {Y} -14 {{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}}',
   f'summon atalaya:gelatina 14 {Y} -14 {{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}}')
en(C + 10, f'tp @a 9 {Y + 0.2} -8.6 180 6')
foto(C + 40, 'creepers_fila')
en(C + 55, f'tp @a 5.25 {Y + 0.4} -11.4 180 10')
foto(C + 85, 'creepers_fila_cerca1')
en(C + 100, f'tp @a 12.75 {Y + 0.4} -11.4 180 10')
foto(C + 130, 'creepers_fila_cerca2')
t = C + 160
en(t, 'tellraw @a "FIN DE LA PRUEBA CREEPERS"')

lineas = ['scoreboard players add #t tp 1']
for tt in sorted(ev):
    for c in ev[tt]:
        lineas.append(f'execute if score #t tp matches {tt} run {c}')
open(os.path.join(F, 'tick.mcfunction'), 'w', encoding='utf-8').write(chr(10).join(lineas) + chr(10))
print('hasta', t, 'ticks')
