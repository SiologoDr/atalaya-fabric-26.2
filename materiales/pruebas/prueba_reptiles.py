"""Prueba de los reptiles del bestiario (20-10-2026) en el mundo MiniJefes (con run/atalaya_fotos.flag).

Primero cómo se ven: los seis quietos sobre la hierba, en fila, de cerca y de lado. Luego lo que hace cada uno, de uno
en uno y contra el jugador (en supervivencia, con regeneración y algo de resistencia), y lo que pasa sale en el chat (y
en el registro) como «OK …» o «MAL …»:

  Salvaje      te pega
  Guerrero     te pega y te envenena
  Rojo, Azul   salen tres (la manada) y te muerden
  Plumosaurio  no te ataca; cuando le pegas, sí (y te lanza)
  Cavador      se te acerca, se entierra y sale a morderte
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
PRED = os.path.join(BASE, 'data', 'templos_prueba', 'predicate')
os.makedirs(F, exist_ok=True)
os.makedirs(PRED, exist_ok=True)
os.makedirs(os.path.join(BASE, 'data', 'minecraft', 'tags', 'function'), exist_ok=True)
open(os.path.join(BASE, 'pack.mcmeta'), 'w').write(json.dumps(
    {'pack': {'description': 'Prueba de los reptiles', 'min_format': [107, 0], 'max_format': [107, 1]}}))
json.dump({'values': ['templos_prueba:carga']}, open(os.path.join(BASE, 'data/minecraft/tags/function/load.json'), 'w'))
json.dump({'values': ['templos_prueba:tick']}, open(os.path.join(BASE, 'data/minecraft/tags/function/tick.json'), 'w'))
json.dump({'condition': 'minecraft:entity_properties', 'entity': 'this',
           'predicate': {'effects': {'minecraft:poison': {}}}}, open(os.path.join(PRED, 'envenenado.json'), 'w'))
open(os.path.join(F, 'carga.mcfunction'), 'w').write(
    'scoreboard objectives add tp dummy\nscoreboard players set #t tp 0\n'
    'scoreboard objectives add dano minecraft.custom:minecraft.damage_taken\n')

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
    en(30 + k, f'fill -24 {Y - 1 + k} -40 44 {Y - 1 + k} 20 {"minecraft:grass_block" if k == 0 else "minecraft:air"}')
en(50, 'gamemode spectator @a', 'effect give @a minecraft:resistance infinite 255 true',
   'effect give @a minecraft:saturation infinite 255 true', 'effect give @a minecraft:night_vision infinite 0 true',
   'tellraw @a "FOV 70"')

# ---- Cómo se ven: quietos sobre la hierba, de cara a nosotros (con NBT, el raptor no trae su manada).
NA = '{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}'
# (el mob, su x, lo lejos que se le mira de cerca)
fila = (('reptisaurio_salvaje', -10.0, 5.5), ('reptisaurio_guerrero', -4.0, 5.5), ('dromoraptor_rojo', 3.0, 6.0),
        ('dromoraptor_azul', 10.0, 6.0), ('plumosaurio', 20.0, 11.0), ('molusco_rocoso', 29.0, 2.6))
ZF = -16.0
for e, x, _ in fila:
    en(240, f'summon atalaya:{e} {x} {Y} {ZF} {NA}')
tomas = [
    ('reptiles_fila', (9.5, Y + 5.0, 12.0, 180, 10)),
    ('reptiles_lado', (40.0, Y + 4.0, ZF, 90, 6)),
    ('reptiles_tres_cuartos', (34.0, Y + 6.0, 4.0, 140, 14)),
]
for k, (nombre, (x, y, z, yaw, pitch)) in enumerate(tomas):
    en(260 + k * 50, f'tp @a {x} {y} {z} {yaw} {pitch}')
    foto(290 + k * 50, nombre)
t = 260 + len(tomas) * 50
en(t, 'tellraw @a "FOV 50"')
for k, (e, x, d) in enumerate(fila):
    en(t + 10 + k * 40, f'tp @a {x + d * 0.5} {Y + d * 0.45} {ZF + d} 152 14')
    foto(t + 40 + k * 40, 'reptiles_cerca_' + e)
t += 20 + len(fila) * 40
en(t, 'tellraw @a "FOV 70"', 'kill @e[type=!minecraft:player]')

# ---- Lo que hace cada uno.
en(t + 10, 'gamemode survival @a', 'effect clear @a minecraft:resistance',
   'effect give @a minecraft:resistance infinite 3 true', 'effect give @a minecraft:health_boost infinite 4 true',
   'effect give @a minecraft:regeneration infinite 4 true', 'gamerule immediate_respawn true', f'tp @a 0 {Y} 0 180 0')
t += 20


def prueba_golpe(t, mob, nombre, extra=()):
    """Sale el mob a ocho bloques; a los 300 ticks, ¿te ha hecho daño?"""
    en(t, 'scoreboard players set @a dano 0', f'tp @a 0 {Y} 0 180 0', f'summon atalaya:{mob} 0 {Y} -8')
    foto(t + 14, f'reptiles_{nombre}_ve')
    foto(t + 32, f'reptiles_{nombre}_corre')
    foto(t + 70, f'reptiles_{nombre}_ataca')
    si(t + 300, 'if entity @a[scores={dano=1..}]', f'{nombre.upper()} te ha hecho daño', f'{nombre.upper()} no te ha hecho daño')
    for k, (dt, cond, bien, mal) in enumerate(extra):
        si(t + dt, cond, bien, mal)
    en(t + 305, f'kill @e[type=atalaya:{mob}]', 'effect clear @a minecraft:poison')
    return t + 320


t = prueba_golpe(t, 'reptisaurio_salvaje', 'salvaje')
t = prueba_golpe(t, 'reptisaurio_guerrero', 'guerrero', [
    (300, 'as @p if predicate templos_prueba:envenenado', 'GUERRERO te ha envenenado', 'GUERRERO no te ha envenenado')])
for mob, nombre in (('dromoraptor_rojo', 'rojo'), ('dromoraptor_azul', 'azul')):
    en(t + 2, f'execute store result score #n tp if entity @e[type=atalaya:{mob}]')
    si(t + 3, 'if score #n tp matches 3', f'{nombre.upper()} ha salido en manada (tres)',
       f'{nombre.upper()} no ha salido en manada')
    t = prueba_golpe(t, mob, nombre)

# El Plumosaurio: doscientos ticks a su lado sin que te ataque; luego le pegas y te ataca.
en(t, 'scoreboard players set @a dano 0', f'tp @a 0 {Y} 0 180 0', f'summon atalaya:plumosaurio 0 {Y} -7')
foto(t + 60, 'reptiles_plumosaurio_tranquilo')
si(t + 200, 'if entity @a[scores={dano=0}]', 'PLUMOSAURIO no te ataca si no le pegas', 'PLUMOSAURIO te ha atacado sin pegarle')
en(t + 205, 'damage @e[type=atalaya:plumosaurio,limit=1] 2 minecraft:player_attack by @p')
for k in range(210, 500, 2):
    en(t + k, 'execute if score #lanza tp matches 0 as @p at @s unless block ~ ~-1 ~ minecraft:grass_block '
              'unless block ~ ~-0.5 ~ minecraft:grass_block run tellraw @a "FOTO reptiles_plumosaurio_lanza"',
       'execute as @p at @s unless block ~ ~-1 ~ minecraft:grass_block unless block ~ ~-0.5 ~ minecraft:grass_block '
       'run scoreboard players set #lanza tp 1')
en(t + 206, 'scoreboard players set #lanza tp 0')
si(t + 500, 'if entity @a[scores={dano=1..}]', 'PLUMOSAURIO te ataca cuando le pegas', 'PLUMOSAURIO no se ha revuelto')
si(t + 501, 'if score #lanza tp matches 1', 'PLUMOSAURIO te ha lanzado por los aires', 'PLUMOSAURIO no te ha lanzado')
en(t + 505, 'kill @e[type=atalaya:plumosaurio]')
t += 520

# El Molusco Rocoso: sale a cinco bloques y te ataca; te alejas a doce: se entierra, te sigue bajo tierra y sale a
# morderte.
en(t, 'scoreboard players set @a dano 0', f'tp @a 0 {Y} 0 180 0', f'summon atalaya:molusco_rocoso 0 {Y} -5')
en(t + 60, f'tp @a 0 {Y} 8 180 0')
for k in range(60, 260, 12):
    foto(t + k, f'reptiles_molusco_{k:03d}')
en(t + 59, 'scoreboard players set @a dano 0')
si(t + 400, 'if entity @a[scores={dano=1..}]', 'MOLUSCO te ha seguido bajo tierra y mordido', 'MOLUSCO no te ha alcanzado')
en(t + 405, 'kill @e[type=atalaya:molusco_rocoso]')
t += 420
en(t, 'tellraw @a "FIN DE LA PRUEBA REPTILES"')

lineas = ['scoreboard players add #t tp 1']
for tt in sorted(ev):
    for c in ev[tt]:
        lineas.append(f'execute if score #t tp matches {tt} run {c}')
open(os.path.join(F, 'tick.mcfunction'), 'w', encoding='utf-8').write(chr(10).join(lineas) + chr(10))
print('hasta', t, 'ticks')
