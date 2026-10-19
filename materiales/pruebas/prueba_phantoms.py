"""Prueba de los phantoms del bestiario (19-10-2026) en el mundo MiniJefes (con run/atalaya_fotos.flag).

Primero cómo se ven: los dos quietos en el aire junto a un phantom de vanilla, de lado, desde arriba, de cerca y de
noche. Luego lo que hace cada uno, de uno en uno y contra el jugador (en supervivencia, con regeneración y algo de
resistencia), y lo que pasa sale en el chat (y en el registro) como «OK …» o «MAL …»:

  Oscuro     al darte, te hace soltar algo del inventario (cae al suelo)
  Explosivo  al darte, te deja una brasa que revienta y abre el suelo donde estabas
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
    {'pack': {'description': 'Prueba de los phantoms', 'min_format': [107, 0], 'max_format': [107, 1]}}))
json.dump({'values': ['templos_prueba:carga']}, open(os.path.join(BASE, 'data/minecraft/tags/function/load.json'), 'w'))
json.dump({'values': ['templos_prueba:tick']}, open(os.path.join(BASE, 'data/minecraft/tags/function/tick.json'), 'w'))
open(os.path.join(F, 'carga.mcfunction'), 'w').write('scoreboard objectives add tp dummy\nscoreboard players set #t tp 0\n')

ev = {}


def en(t, *cmds):
    ev.setdefault(int(t) + (300 if int(t) >= 200 else 0), []).extend(cmds)


def foto(t, nombre):
    en(t, f'tellraw @a "FOTO {nombre}"')


def si(t, condicion, bien, mal):
    en(t, f'execute {condicion} run tellraw @a "OK {bien}"',
       f'execute {condicion.replace("if ", "unless ", 1)} run tellraw @a "MAL {mal}"')


Y = 100
en(20, 'gamerule send_command_feedback false', 'gamerule advance_time false', 'gamerule advance_weather false',
   'gamerule spawn_mobs false', 'gamerule mob_griefing false', 'weather clear 1000000', 'time set 6000',
   'gamemode creative @a', 'forceload add -64 -64 64 64', f'tp @a 0 {Y + 1} 0 180 0')
for k in range(0, 14):
    en(30 + k, f'fill -24 {Y - 1 + k} -30 44 {Y - 1 + k} 20 {"minecraft:grass_block" if k == 0 else "minecraft:air"}')
# Las fotos del aire, en espectador (en supervivencia caería antes de la foto).
en(50, 'gamemode spectator @a', 'effect give @a minecraft:resistance infinite 255 true',
   'effect give @a minecraft:saturation infinite 255 true', 'effect give @a minecraft:night_vision infinite 0 true',
   'tellraw @a "FOV 70"')

# ---- Cómo se ven: quietos en el aire, de cara a nosotros.
NA = '{NoAI:1b,NoGravity:1b,Rotation:[0f,0f],PersistenceRequired:1b}'
fila = (('minecraft:phantom', 0.5), ('atalaya:phantom_oscuro', 5.0), ('atalaya:phantom_explosivo', 9.5))
for e, x in fila:
    en(240, f'summon {e} {x} {Y + 2.5} -10 {NA}')
tomas = [
    ('phantoms_fila', (5.0, Y + 3.2, -2.5, 180, 6)),
    ('phantoms_arriba', (5.0, Y + 8.0, -6.0, 180, 60)),
    ('phantoms_lado', (16.0, Y + 3.5, -10.0, 90, 5)),
]
for k, (nombre, (x, y, z, yaw, pitch)) in enumerate(tomas):
    en(260 + k * 50, f'tp @a {x} {y} {z} {yaw} {pitch}')
    foto(290 + k * 50, nombre)
t = 260 + len(tomas) * 50
en(t, 'tellraw @a "FOV 40"')
for k, (e, x) in enumerate(fila[1:]):
    en(t + 10 + k * 40, f'tp @a {x - 1.5} {Y + 4.2} -7.5 160 28')
    foto(t + 40 + k * 40, 'phantoms_zoom_' + e.split(':')[1])
t += 20 + len(fila[1:]) * 40
en(t, 'tellraw @a "FOV 70"', 'time set 18000', 'effect clear @a minecraft:night_vision')
en(t + 10, f'tp @a 5.0 {Y + 3.2} -2.5 180 6')
foto(t + 50, 'phantoms_noche')
t += 70
en(t, 'time set 6000', 'effect give @a minecraft:night_vision infinite 0 true', 'kill @e[type=!minecraft:player]')

# ---- Lo que hace cada uno.
en(t + 10, 'gamemode survival @a', 'effect clear @a minecraft:resistance',
   'effect give @a minecraft:resistance infinite 2 true',
   'effect give @a minecraft:regeneration infinite 3 true', f'tp @a 0 {Y} 0 180 0')
t += 20

# El Oscuro: el inventario lleno de cosas; cuando le da, algo cae al suelo.
en(t, 'clear @a', 'give @a minecraft:cobblestone 64', 'give @a minecraft:oak_log 32', 'give @a minecraft:bread 16',
   'give @a minecraft:torch 48', 'give @a minecraft:iron_ingot 20',
   f'summon atalaya:phantom_oscuro 0 {Y + 10} -6')
en(t + 1, 'scoreboard players set #suelta tp 0')
for k in range(2, 600):
    en(t + k, 'execute at @p if score #suelta tp matches 0 if entity @e[type=minecraft:item,distance=..8] '
              'run tellraw @a "FOTO phantoms_oscuro_suelta"',
       'execute at @p if entity @e[type=minecraft:item,distance=..8] run scoreboard players set #suelta tp 1')
si(t + 600, 'if score #suelta tp matches 1', 'OSCURO te ha hecho soltar algo', 'OSCURO no te ha hecho soltar nada')
en(t + 605, 'kill @e[type=atalaya:phantom_oscuro]', 'kill @e[type=minecraft:item]', 'clear @a')
t += 620

# El Explosivo: cuando le da, la brasa revienta y abre el suelo donde estabas.
en(t, 'gamerule mob_griefing true', f'summon atalaya:phantom_explosivo 0 {Y + 10} -6')
en(t + 1, 'scoreboard players set #boom tp 0')
for k in range(2, 600):
    en(t + k, 'execute if score #boom tp matches 0 at @p unless block ~ ~-1 ~ minecraft:grass_block '
              'run tellraw @a "FOTO phantoms_explosivo_boom"',
       'execute at @p unless block ~ ~-1 ~ minecraft:grass_block run scoreboard players set #boom tp 1')
si(t + 600, 'if score #boom tp matches 1', 'EXPLOSIVO ha reventado donde estabas', 'EXPLOSIVO no ha reventado')
en(t + 605, 'kill @e[type=atalaya:phantom_explosivo]', 'gamerule mob_griefing false')
t += 620
en(t, 'tellraw @a "FIN DE LA PRUEBA PHANTOMS"')

lineas = ['scoreboard players add #t tp 1']
for tt in sorted(ev):
    for c in ev[tt]:
        lineas.append(f'execute if score #t tp matches {tt} run {c}')
open(os.path.join(F, 'tick.mcfunction'), 'w', encoding='utf-8').write(chr(10).join(lineas) + chr(10))
print('hasta', t, 'ticks')
