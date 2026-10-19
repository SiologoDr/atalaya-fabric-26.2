"""Prueba de los cuatro fantasmas (19-10-2026) en el mundo MiniJefes (con run/atalaya_fotos.flag).

Primero cómo se ven: los cuatro quietos en fila junto a un zombi de vanilla, de día, de cerca, de lado, por detrás y
de noche. Luego lo que hace cada uno, de uno en uno y contra el jugador (en supervivencia, con regeneración y algo de
resistencia para aguantar), y lo que pasa sale en el chat (y en el registro) como «OK …» o «MAL …»:

  Blanco    te deja con Lentitud
  Negro     te baja la vida máxima (te roba un corazón) y, al morir, suelta Corazones Blancos
  Amarillo  te gasta el tótem de la mano, se te mete dentro (invulnerable) y a los cinco segundos sale
  Rojo      te agarra: te deja enraizado
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
    {'pack': {'description': 'Prueba de los fantasmas', 'min_format': [107, 0], 'max_format': [107, 1]}}))
json.dump({'values': ['templos_prueba:carga']}, open(os.path.join(BASE, 'data/minecraft/tags/function/load.json'), 'w'))
json.dump({'values': ['templos_prueba:tick']}, open(os.path.join(BASE, 'data/minecraft/tags/function/tick.json'), 'w'))
open(os.path.join(F, 'carga.mcfunction'), 'w').write('scoreboard objectives add tp dummy\nscoreboard players set #t tp 0\n')

ev = {}


def en(t, *cmds):
    ev.setdefault(int(t) + (300 if int(t) >= 200 else 0), []).extend(cmds)


def foto(t, nombre):
    en(t, f'tellraw @a "FOTO {nombre}"')


def si(t, condicion, bien, mal):
    """Una comprobación: «OK bien» si se cumple, «MAL mal» si no."""
    en(t, f'execute {condicion} run tellraw @a "OK {bien}"',
       f'execute {condicion.replace("if ", "unless ", 1)} run tellraw @a "MAL {mal}"')


Y = 100
en(20, 'gamerule send_command_feedback false', 'gamerule advance_time false', 'gamerule advance_weather false',
   'gamerule spawn_mobs false', 'gamerule mob_griefing false', 'weather clear 1000000', 'time set 6000',
   'gamemode creative @a', 'forceload add -64 -64 64 64', f'tp @a 0 {Y + 1} 0 180 0')
for k in range(0, 14):
    en(30 + k, f'fill -24 {Y - 1 + k} -30 44 {Y - 1 + k} 20 {"minecraft:grass_block" if k == 0 else "minecraft:air"}')
en(50, 'gamemode survival @a', 'effect give @a minecraft:resistance infinite 255 true',
   'effect give @a minecraft:saturation infinite 255 true', 'effect give @a minecraft:night_vision infinite 0 true',
   'tellraw @a "FOV 70"')

# ---- Cómo se ven: quietos en fila (flotan: no tienen gravedad).
NA = '{NoAI:1b,Rotation:[0f,0f],PersistenceRequired:1b}'
fila = (('minecraft:zombie', 0.5), ('atalaya:espectro_blanco', 4), ('atalaya:espectro_negro', 7.5),
        ('atalaya:espectro_amarillo', 11), ('atalaya:espectro_rojo', 14.5))
for e, x in fila:
    en(240, f'summon {e} {x} {Y + 0.3} -12 {NA}')
tomas = [
    ('fantasmas_fila', (7.5, Y + 0.8, -3.0, 180, 6)),
    ('fantasmas_cerca1', (5.75, Y + 1.2, -7.6, 180, 6)),
    ('fantasmas_cerca2', (12.75, Y + 1.2, -7.6, 180, 6)),
    ('fantasmas_lado', (21.0, Y + 1.4, -10.5, 115, 8)),
    ('fantasmas_detras', (7.5, Y + 2.2, -18.5, 0, 12)),
]
for k, (nombre, (x, y, z, yaw, pitch)) in enumerate(tomas):
    en(260 + k * 50, f'tp @a {x} {y} {z} {yaw} {pitch}')
    foto(290 + k * 50, nombre)
t = 260 + len(tomas) * 50
en(t, 'tellraw @a "FOV 40"')
for k, (e, x) in enumerate(fila[1:]):
    en(t + 10 + k * 40, f'tp @a {x + 0.5} {Y + 1.5} -9.0 175 6')
    foto(t + 40 + k * 40, 'fantasmas_zoom_' + e.split(':')[1])
t += 20 + len(fila[1:]) * 40
en(t, 'tellraw @a "FOV 70"', 'time set 18000', 'effect clear @a minecraft:night_vision')
en(t + 10, f'tp @a 7.5 {Y + 0.8} -3.0 180 6')
foto(t + 50, 'fantasmas_noche')
t += 70
en(t, 'time set 6000', 'effect give @a minecraft:night_vision infinite 0 true',
   'kill @e[type=!minecraft:player]')

# ---- Lo que hace cada uno: contra el jugador, de uno en uno.
en(t + 10, 'effect clear @a minecraft:resistance', 'effect give @a minecraft:resistance infinite 2 true',
   'effect give @a minecraft:regeneration infinite 3 true', f'tp @a 0 {Y} 0 180 0')
t += 20

# El Blanco: Lentitud.
en(t, f'summon atalaya:espectro_blanco 0 {Y + 0.3} -5')
foto(t + 50, 'fantasmas_blanco_ataca')
si(t + 60, 'if entity @a[nbt={active_effects:[{id:"minecraft:slowness"}]}]', 'BLANCO te deja con Lentitud',
   'BLANCO no ha puesto Lentitud')
en(t + 70, 'kill @e[type=atalaya:espectro_blanco]', 'effect clear @a minecraft:slowness')
t += 100

# El Negro: te roba un corazón (vida máxima 18) y al morir suelta un Corazón Blanco por cada uno.
en(t, f'summon atalaya:espectro_negro 0 {Y + 0.3} -5')
foto(t + 60, 'fantasmas_negro_ataca')
en(t + 70, 'execute store result score #vida tp run attribute @p minecraft:max_health get',
   'tellraw @a ["VIDA MAX TRAS EL NEGRO: ",{"score":{"name":"#vida","objective":"tp"}}]')
si(t + 71, 'if score #vida tp matches ..18', 'NEGRO te ha robado un corazon', 'NEGRO no ha robado nada')
en(t + 80, 'kill @e[type=atalaya:espectro_negro]')
# El corazón cae al suelo o lo recoges: se mira cada tick durante dos segundos.
en(t + 79, 'scoreboard players set #cb tp 0')
for k in range(81, 121):
    en(t + k, 'execute if entity @e[type=minecraft:item,nbt={Item:{id:"atalaya:corazon_blanco"}}] run '
              'scoreboard players set #cb tp 1',
       'execute if entity @a[nbt={Inventory:[{id:"atalaya:corazon_blanco"}]}] run scoreboard players set #cb tp 1')
si(t + 121, 'if score #cb tp matches 1', 'NEGRO suelta Corazones Blancos al morir',
   'NEGRO no ha soltado el Corazon Blanco')
foto(t + 112, 'fantasmas_negro_corazon')
en(t + 120, 'kill @e[type=minecraft:item]')
t += 140

# El Amarillo: te gasta el tótem de la mano, se te mete dentro (invulnerable) y sale.
en(t, 'item replace entity @p weapon.offhand with minecraft:totem_of_undying',
   f'summon atalaya:espectro_amarillo 0 {Y + 0.3} -5')
en(t + 50, 'execute store result score #totem tp run clear @p minecraft:totem_of_undying 0')
si(t + 51, 'if score #totem tp matches 0', 'AMARILLO te ha gastado el totem', 'AMARILLO no ha gastado el totem')
si(t + 55, 'if entity @e[type=atalaya:espectro_amarillo,nbt={Invulnerable:1b}]', 'AMARILLO se te ha metido dentro',
   'AMARILLO no se ha metido dentro')
foto(t + 60, 'fantasmas_amarillo_dentro')
# Sale a los cinco segundos (y como no hay otro jugador, vuelve a por ti): se mira cada tick.
en(t + 59, 'scoreboard players set #sale tp 0')
for k in range(60, 200):
    en(t + k, 'execute if score #sale tp matches 0 if entity @e[type=atalaya:espectro_amarillo,nbt=!{Invulnerable:1b}] '
              'run tellraw @a "FOTO fantasmas_amarillo_sale"',
       'execute if entity @e[type=atalaya:espectro_amarillo,nbt=!{Invulnerable:1b}] run scoreboard players set #sale tp 1')
si(t + 200, 'if score #sale tp matches 1', 'AMARILLO ha vuelto a salir', 'AMARILLO no ha salido')
en(t + 205, 'kill @e[type=atalaya:espectro_amarillo]')
t += 220

# El Rojo: te agarra y te deja enraizado.
en(t, f'summon atalaya:espectro_rojo 0 {Y + 0.3} -5')
si(t + 60, 'if entity @a[nbt={active_effects:[{id:"atalaya:enraizado"}]}]', 'ROJO te ha agarrado',
   'ROJO no te ha agarrado')
foto(t + 62, 'fantasmas_rojo_agarra')
si(t + 90, 'if entity @a[nbt={active_effects:[{id:"atalaya:enraizado"}]}]', 'ROJO no te suelta',
   'ROJO te ha soltado')
en(t + 100, 'kill @e[type=atalaya:espectro_rojo]')
t += 120
en(t, 'tellraw @a "FIN DE LA PRUEBA FANTASMAS"')

lineas = ['scoreboard players add #t tp 1']
for tt in sorted(ev):
    for c in ev[tt]:
        lineas.append(f'execute if score #t tp matches {tt} run {c}')
open(os.path.join(F, 'tick.mcfunction'), 'w', encoding='utf-8').write(chr(10).join(lineas) + chr(10))
print('hasta', t, 'ticks')
