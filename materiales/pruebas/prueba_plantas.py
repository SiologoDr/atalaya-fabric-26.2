"""Prueba de las plantas rehechas (19-10-2026: al píxel de Minecraft) en el mundo MiniJefes (con
run/atalaya_fotos.flag): las seis en fila junto a un zombi de vanilla, de día y de noche, de cerca de dos en dos, de
lado y por detrás."""
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
    {'pack': {'description': 'Prueba de las plantas', 'min_format': [107, 0], 'max_format': [107, 1]}}))
json.dump({'values': ['templos_prueba:carga']}, open(os.path.join(BASE, 'data/minecraft/tags/function/load.json'), 'w'))
json.dump({'values': ['templos_prueba:tick']}, open(os.path.join(BASE, 'data/minecraft/tags/function/tick.json'), 'w'))
open(os.path.join(F, 'carga.mcfunction'), 'w').write('scoreboard objectives add tp dummy\nscoreboard players set #t tp 0\n')

ev = {}


def en(t, *cmds):
    ev.setdefault(int(t) + (300 if int(t) >= 200 else 0), []).extend(cmds)


def foto(t, nombre):
    en(t, f'tellraw @a "FOTO {nombre}"')


Y = 100
en(20, 'gamerule send_command_feedback false', 'gamerule advance_time false', 'gamerule advance_weather false',
   'gamerule spawn_mobs false', 'gamerule mob_griefing false', 'weather clear 1000000', 'time set 6000',
   'gamemode creative @a', 'forceload add -64 -64 64 64', f'tp @a 0 {Y + 1} 0 180 0')
for k in range(0, 14):
    en(30 + k, f'fill -24 {Y - 1 + k} -30 44 {Y - 1 + k} 20 {"minecraft:grass_block" if k == 0 else "minecraft:air"}')
en(50, 'gamemode survival @a', 'effect give @a minecraft:resistance infinite 255 true',
   'effect give @a minecraft:saturation infinite 255 true', 'effect give @a minecraft:night_vision infinite 0 true',
   'tellraw @a "FOV 70"')

NA = '{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}'
fila = (('minecraft:zombie', 0.5), ('atalaya:fauces_verde', 3.5), ('atalaya:fauces_carmin', 6.5),
        ('atalaya:fauces_escarcha', 9.5), ('atalaya:trampa', 12.5), ('atalaya:pina', 15), ('atalaya:zombi_planta', 18))
for e, x in fila:
    en(240, f'summon {e} {x} {Y} -12 {NA}')
tomas = [
    ('plantas_fila', (9.25, Y + 0.6, -3.0, 180, 8)),
    ('plantas_cerca1', (5.75, Y + 0.9, -7.4, 180, 8)),
    ('plantas_cerca2', (12.75, Y + 0.9, -7.4, 180, 8)),
    ('plantas_cerca3', (17.0, Y + 0.9, -7.6, 180, 8)),
    ('plantas_lado', (24.5, Y + 1.2, -10.5, 115, 10)),
    ('plantas_detras', (9.25, Y + 2.2, -18.5, 0, 16)),
]
for k, (nombre, (x, y, z, yaw, pitch)) in enumerate(tomas):
    en(260 + k * 50, f'tp @a {x} {y} {z} {yaw} {pitch}')
    foto(290 + k * 50, nombre)
t = 260 + len(tomas) * 50
# Cada uno de cerca (el campo de visión cerrado, para ver los píxeles).
en(t, 'tellraw @a "FOV 40"')
for k, (e, x) in enumerate(fila[1:]):
    # La piña y la trampa son bajas: la cámara, más cerca del suelo y mirando hacia abajo.
    alto_, z_, cab_ = {'atalaya:pina': (0.2, -9.9, 38), 'atalaya:trampa': (1.1, -10.2, 50)}.get(e, (1.0, -9.2, 10))
    en(t + 10 + k * 40, f'tp @a {x + 0.4} {Y + alto_} {z_} 172 {cab_}')
    foto(t + 40 + k * 40, 'plantas_zoom_' + e.split(':')[1])
t += 20 + len(fila[1:]) * 40
en(t, 'tellraw @a "FOV 70"')
# La trampa escondida, como la vería un despistado (de pie, a unos tres bloques, mirando al suelo al andar).
for k, (z_, cab_) in enumerate(((-9.0, 32), (-7.0, 22))):
    en(t + 10 + k * 40, f'tp @a 12.9 {Y} {z_} 180 {cab_}')
    foto(t + 40 + k * 40, f'plantas_trampa_camuflada{k + 1}')
t += 90
# De noche (sin visión nocturna): lo que brilla.
en(t, 'time set 18000', 'effect clear @a minecraft:night_vision')
en(t + 10, f'tp @a 9.25 {Y + 0.6} -3.0 180 8')
foto(t + 50, 'plantas_noche')
en(t + 60, f'tp @a 16.25 {Y + 0.9} -7.4 180 8')
foto(t + 100, 'plantas_noche_cerca')
t += 120
en(t, 'tellraw @a "FIN DE LA PRUEBA PLANTAS"')

lineas = ['scoreboard players add #t tp 1']
for tt in sorted(ev):
    for c in ev[tt]:
        lineas.append(f'execute if score #t tp matches {tt} run {c}')
open(os.path.join(F, 'tick.mcfunction'), 'w', encoding='utf-8').write(chr(10).join(lineas) + chr(10))
print('hasta', t, 'ticks')
