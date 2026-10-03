"""
Escribe el datapack de rodaje en el mundo de pruebas.

Todo cuelga de un marcador "origen": el Vigia se planta ahi mirando al norte
(-Z) y el maniqui —el actor que hace de jugador— a su frente. Las tomas van
por ticks desde que el jugador entra; la camara es el propio jugador en
espectador, recolocado al empezar cada toma y con un travelling por tick.

Uso: python rodaje.py <carpeta del mundo>
"""
import os, sys

MUNDO = sys.argv[1]
NS = 'rodaje'
BASE = os.path.join(MUNDO, 'datapacks', 'rodaje')
FN = os.path.join(BASE, 'data', NS, 'function')
os.makedirs(FN, exist_ok=True)
os.makedirs(os.path.join(BASE, 'data', 'minecraft', 'tags', 'function'), exist_ok=True)

def escribir(nombre, lineas):
    with open(os.path.join(FN, nombre + '.mcfunction'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lineas) + '\n')

with open(os.path.join(BASE, 'pack.mcmeta'), 'w') as f:
    f.write('{ "pack": { "description": "Rodaje del Vigia", "min_format": [107, 0], "max_format": [107, 1] } }\n')
with open(os.path.join(BASE, 'data', 'minecraft', 'tags', 'function', 'load.json'), 'w') as f:
    f.write('{ "values": ["rodaje:carga"] }\n')
with open(os.path.join(BASE, 'data', 'minecraft', 'tags', 'function', 'tick.json'), 'w') as f:
    f.write('{ "values": ["rodaje:tick"] }\n')

# --- Tomas: (clave, tick de inicio). La siguiente empieza donde acaba esta. ---
T = {
    'montaje': 20, 'sync': 350, 'vigilar': 370, 'alerta': 530, 'mirada': 630,
    'cepo': 870, 'espalda': 990, 'buscar': 1140, 'muerte': 1220, 'botin': 1320, 'fin': 1470,
}

def en(o):
    return f'execute at @e[tag=origen,limit=1] run {o}'

escribir('carga', ['scoreboard objectives add rj dummy', 'scoreboard players set #t rj 0'])

# Los gamerules van cada uno en su fichero: si el nombre no existe en 26.2,
# falla solo esa funcion y no se lleva por delante el resto.
for i, g in enumerate(['gamerule advance_time false', 'gamerule doDaylightCycle false',
                       'gamerule spawn_mobs false', 'gamerule doMobSpawning false',
                       'gamerule send_command_feedback false', 'gamerule sendCommandFeedback false',
                       'gamerule advance_weather false', 'gamerule doWeatherCycle false']):
    escribir(f'regla{i}', [g])

tick = ['execute if entity @a run scoreboard players add #t rj 1']
def a(t, cmd):
    tick.append(f'execute if score #t rj matches {t} run {cmd}')
def entre(t0, t1, cmd):
    tick.append(f'execute if score #t rj matches {t0}..{t1 - 1} run {cmd}')

# Limpieza continua: nada que no sea del rodaje entra en plano.
entre(1, T['fin'], 'kill @e[type=!minecraft:player,type=!atalaya:vigia,type=!minecraft:mannequin,type=!minecraft:item,type=!atalaya:rayo_vigia,type=!minecraft:marker,type=!minecraft:experience_orb,type=!minecraft:item_display]')

# ---------------- montaje del plato ----------------
a(T['montaje'], 'execute as @a[limit=1] at @s run function rodaje:montaje')
escribir('montaje', [
    'kill @e[type=!minecraft:player]',
    # El origen, alineado a la rejilla: la camara puede empezar flotando (la
    # toma anterior la dejo en el aire), y si el origen se queda a media
    # altura el Vigia cae al suelo y todos los encuadres salen altos.
    'summon minecraft:marker ~ ~ ~ {Tags:["origen"]}',
    'execute as @e[tag=origen] at @s align xyz run tp @s ~0.5 ~ ~0.5',
    *[f'function rodaje:regla{i}' for i in range(8)],
    'gamemode spectator @s',
    'time set 13350',
    'weather clear',
    'effect clear @s',
    'execute at @e[tag=origen,limit=1] run function rodaje:plato',
])
escribir('plato', [
    # despejar en tres tandas: /fill no admite mas de 32768 bloques
    'fill ~-20 ~ ~-20 ~20 ~9 ~20 minecraft:air',
    'fill ~-20 ~10 ~-20 ~20 ~19 ~20 minecraft:air',
    'fill ~-20 ~20 ~-20 ~20 ~30 ~20 minecraft:air',
    'fill ~-20 ~-1 ~-20 ~20 ~-1 ~20 minecraft:polished_deepslate',
    'fill ~-20 ~-2 ~-20 ~20 ~-2 ~20 minecraft:deepslate',
    # parches de piedra musgosa y grava: suelo viejo, no una losa nueva
    'fill ~-6 ~-1 ~-14 ~-2 ~-1 ~-9 minecraft:mossy_cobblestone',
    'fill ~3 ~-1 ~-6 ~7 ~-1 ~-3 minecraft:cracked_deepslate_tiles',
    'fill ~-9 ~-1 ~2 ~-5 ~-1 ~7 minecraft:mossy_cobblestone',
    'fill ~5 ~-1 ~4 ~9 ~-1 ~9 minecraft:deepslate_tiles',
    'fill ~-2 ~-1 ~-2 ~2 ~-1 ~2 minecraft:cracked_deepslate_tiles',
    # la atalaya en ruinas, al fondo a la derecha
    'fill ~9 ~ ~11 ~13 ~15 ~15 minecraft:stone_bricks hollow',
    'fill ~9 ~10 ~11 ~13 ~15 ~11 minecraft:air',
    'fill ~10 ~3 ~11 ~12 ~6 ~11 minecraft:air',
    'setblock ~11 ~7 ~11 minecraft:lantern[hanging=true]',
    'fill ~9 ~16 ~11 ~9 ~16 ~11 minecraft:stone_bricks',
    'fill ~11 ~16 ~15 ~11 ~16 ~15 minecraft:stone_bricks',
    'fill ~13 ~16 ~13 ~13 ~16 ~13 minecraft:mossy_stone_bricks',
    'fill ~9 ~ ~10 ~13 ~2 ~10 minecraft:mossy_stone_bricks',
    'fill ~-14 ~ ~8 ~-12 ~1 ~9 minecraft:cobblestone',
    'setblock ~-13 ~2 ~8 minecraft:mossy_cobblestone',
    'setblock ~-4 ~ ~-12 minecraft:dead_bush',
    'setblock ~6 ~ ~-9 minecraft:dead_bush',
    'setblock ~-8 ~ ~-4 minecraft:dead_bush',
])

# ---------------- sincronia: un golpe de sonido antes de la primera toma ----------------
a(T['sync'], 'playsound atalaya:vigia.cepo_cerrar master @a ~ ~ ~ 1 1')

# ---------------- 1. vigilar: el centinela junto a la torre, en calma ----------------
a(T['vigilar'], en('summon atalaya:vigia ~6 ~ ~9 {NoAI:1b,Rotation:[160f,0f],PersistenceRequired:1b,Tags:["v0"]}'))
a(T['vigilar'], en('tp @a ~2.2 ~1.4 ~3.4 facing ~6 ~2.3 ~9'))
entre(T['vigilar'] + 1, T['alerta'], 'execute as @a at @s run tp @s ^ ^ ^0.016')

# ---------------- 2. alerta: aparece el intruso y le ve ----------------
a(T['alerta'], 'kill @e[tag=v0]')
a(T['alerta'], en('summon atalaya:vigia ~ ~ ~ {Rotation:[180f,0f],PersistenceRequired:1b,Tags:["v"]}'))
a(T['alerta'], en('summon minecraft:mannequin ~ ~ ~-9 {Rotation:[0f,0f],Tags:["actor"],hide_description:1b}'))
a(T['alerta'], 'effect give @e[tag=actor] minecraft:resistance infinite 255 true')
a(T['alerta'], en('tp @a ~1.1 ~1.3 ~-4.4 facing ~ ~2.2 ~'))
a(T['alerta'] + 12, en('damage @e[tag=v,sort=nearest,limit=1] 1 minecraft:mob_attack by @e[tag=actor,sort=nearest,limit=1]'))
# el golpe lo empuja: de vuelta a su marca, o el primer plano se descentra
a(T['alerta'] + 14, en('tp @e[tag=v] ~ ~ ~ 180 0'))
# a partir del rugido, clavado en su sitio (sin particulas): ni persigue ni se
# sale de plano. Todo lo demas —mirar, cargar, el cepo— lo hace igual.
a(T['alerta'] + 38, 'effect give @e[tag=v] minecraft:slowness infinite 255 true')
entre(T['alerta'] + 1, T['mirada'], 'execute as @a at @s run tp @s ^ ^ ^0.012')

# ---------------- 3. mirada: plano lateral, se ve cruzar el rayo ----------------
a(T['mirada'], en('tp @a ~6.2 ~1.8 ~-4.4 facing ~ ~1.8 ~-4.4'))
a(T['mirada'], en('tp @e[tag=v] ~ ~ ~ 180 0'))
# Recordatorio de quien es la presa justo antes de la toma: si la perdio tras
# el rugido, no cargaria la mirada. Cae dentro del fundido, no se ve el golpe.
a(T['mirada'] - 6, en('damage @e[tag=v,sort=nearest,limit=1] 1 minecraft:mob_attack by @e[tag=actor,sort=nearest,limit=1]'))
a(T['mirada'] - 4, en('tp @e[tag=v] ~ ~ ~ 180 0'))
entre(T['mirada'] + 1, T['cepo'], 'execute as @a at @s run tp @s ^-0.008 ^ ^')

# ---------------- 4. cepo: el actor, a tiro de brazos ----------------
a(T['cepo'], en('tp @e[tag=actor] ~ ~ ~-2.3 0 0'))
a(T['cepo'], en('tp @e[tag=v] ~ ~ ~ 180 0'))
a(T['cepo'], en('tp @a ~-3.4 ~1.4 ~-1.3 facing ~ ~1.5 ~-1.2'))
entre(T['cepo'] + 1, T['espalda'], 'execute as @a at @s run tp @s ^ ^ ^0.008')

# ---------------- 5. punto ciego: alguien le da por la espalda ----------------
a(T['espalda'], en('tp @e[tag=actor] ~ ~ ~-30'))
a(T['espalda'], en('summon minecraft:mannequin ~ ~ ~2.3 {Rotation:[180f,0f],Tags:["actor","actor2"],hide_description:1b}'))
a(T['espalda'], 'effect give @e[tag=actor2] minecraft:resistance infinite 255 true')
a(T['espalda'], en('tp @a ~3.6 ~1.6 ~1.3 facing ~ ~1.7 ~1.1'))
a(T['espalda'], en('tp @e[tag=v] ~ ~ ~ 180 0'))
a(T['espalda'] + 22, en('damage @e[tag=v,sort=nearest,limit=1] 4 minecraft:mob_attack by @e[tag=actor2,sort=nearest,limit=1]'))
a(T['espalda'] + 24, en('tp @e[tag=v] ~ ~ ~'))
entre(T['espalda'] + 1, T['buscar'], 'execute as @a at @s run tp @s ^ ^ ^0.006')

# ---------------- 6. buscar: los intrusos desaparecen ----------------
# Lejos, fuera del alcance de persecucion: asi pierde la presa al momento.
# Se quedan en chunks sin cargar y vuelven en la siguiente toma; por eso todos
# los /damage eligen al actor MAS CERCANO al plato, nunca uno cualquiera.
a(T['buscar'], en('tp @e[tag=actor,distance=..30] ~ ~ ~120'))
a(T['buscar'], en('tp @a ~ ~1.8 ~-6.2 facing ~ ~2.3 ~'))
a(T['buscar'], en('tp @e[tag=v] ~ ~ ~ 180 0'))
entre(T['buscar'] + 1, T['muerte'], 'execute as @a at @s run tp @s ^ ^ ^0.018')

# ---------------- 7. muerte: la ultima guardia ----------------
a(T['muerte'], en('tp @a ~-2.6 ~0.9 ~-4.6 facing ~ ~1.4 ~'))
a(T['muerte'], en('tp @e[tag=v] ~ ~ ~ 200 0'))
a(T['muerte'] + 10, en('damage @e[tag=v,sort=nearest,limit=1] 999 minecraft:player_attack by @a[limit=1]'))
entre(T['muerte'] + 1, T['botin'], 'execute as @a at @s run tp @s ^ ^ ^-0.006')

# ---------------- 8. botin: lo que deja en el suelo ----------------
# plano de producto: el ojo y el huevo flotando, girando, a plena luz
a(T['botin'], en('summon minecraft:item_display ~ ~1.25 ~ {item:{id:"atalaya:ojo_vigia",count:1},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.3f,1.3f,1.3f]},brightness:{sky:15,block:15},Tags:["disp"]}'))
a(T['botin'], en('summon minecraft:item_display ~1.15 ~0.95 ~0.5 {item:{id:"atalaya:huevo_vigia",count:1},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.75f,0.75f,0.75f]},brightness:{sky:15,block:15},Tags:["disp"]}'))
a(T['botin'], en('tp @a ~0.3 ~1.25 ~-2.5 facing ~0.3 ~1.15 ~'))
entre(T['botin'] + 1, T['fin'], 'execute as @e[tag=disp] at @s run tp @s ~ ~ ~ ~3 ~')

escribir('tick', tick)
print('datapack escrito:', BASE)
print('tomas (s):', {k: round(v / 20, 2) for k, v in T.items()})
