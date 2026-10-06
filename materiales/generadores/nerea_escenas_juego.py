"""
El datapack de las escenas de prueba del remake de Nerea (octubre de 2026):
monta cada cosa nueva o cambiada delante de quien mira, desde varios angulos,
la dispara con /atalaya nerea <orden> y, si en run/ existe atalaya_fotos.flag,
saca una foto en el momento justo (FotosPrueba).

Funciona como el de Aeralis (aeralis_escenas_juego.py): todo va relativo a un
"ancla" en el suelo de un mundo plano; cada escena abre con su titulo y la
accion empieza cuando se va; cada comando corta lo que haya en marcha. Las
presas son maniquies.

  /function escenas_nerea:recorrido     todas, una detras de otra
  /function escenas_nerea:<escena>      solo esa (cuerpo, fases, rompeolas,
                                        remolino, burbujas, molino, arpon,
                                        mirada, mirada_rota, geiser, marea, furia)
  /function escenas_nerea:parar         lo quita todo y te deja en creativo

Uso: python nerea_escenas_juego.py <raiz del proyecto> [carpeta del mundo] [--auto[=escena]]
"""
import json, os, shutil, sys

AUTO = next((a.split('=', 1)[1] if '=' in a else 'recorrido' for a in sys.argv[1:] if a.startswith('--auto')), None)
ARGS = [a for a in sys.argv[1:] if not a.startswith('--auto')]
RAIZ = ARGS[0]
NS = 'escenas_nerea'
DESTINO = os.path.join(RAIZ, 'materiales/escenas/atalaya_escenas_nerea')
FN = os.path.join(DESTINO, f'data/{NS}/function')
ANCLA = f'execute at @e[type=minecraft:marker,tag=ancla_nerea,limit=1] run '
PAUSA = 45


def maniqui(x, z, nombre='presa', vida=1000, totem=False):
    mano = ',equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}' if totem else ''
    return (f'summon minecraft:mannequin ~{x} ~ ~{z} {{Tags:["escena"],CustomName:"{nombre}",'
            f'attributes:[{{id:"minecraft:max_health",base:{vida}}}],Health:{vida}f{mano}}}')


def nerea(x=0, z=0, giro=-90):
    """Nerea en el ancla mirando hacia +X (giro -90)."""
    return f'summon atalaya:nerea ~{x} ~ ~{z} {{Rotation:[{giro}f,0f]}}'


def camara(x, y, z, mx, my, mz):
    return f'tp @a ~{x} ~{y} ~{z} facing ~{mx} ~{my} ~{mz}'


def titulo(t, sub, color='#7FE6F2'):
    return [f'title @a times 5 {PAUSA - 5} 10',
            f'title @a subtitle {json.dumps({"text": sub, "color": "#E4ECF8"}, ensure_ascii=False)}',
            f'title @a title {json.dumps({"text": t, "color": color}, ensure_ascii=False)}']


def foto(nombre):
    return f'tellraw @a "FOTO nerea_{nombre}"'


def orden(o):
    return f'atalaya nerea {o}'


def ojos(n):
    """n impactos seguidos en los ojos (el izquierdo hasta romperlo, luego el derecho)."""
    return [orden('ojo')] * n


# Cada escena: (montar, [(tick, [ordenes])], duracion, la siguiente). Los ticks
# cuentan desde que se va el titulo. Nerea mide unos 15 bloques: las camaras
# van a 30-50.
ESCENAS = {}

ESCENAS['cuerpo'] = (
    [nerea(), camara(34, 9, 0, 0, 8, 0)] +
    titulo('Nerea, Guardiana de los Mares', 'El remake: 15 bloques, venera, capa de algas, ancla y tridente'),
    [(0, [orden('despertar')]),
     (90, [foto('cuerpo_frente')]),
     (100, [camara(3, 11, 34, 0, 8, 0)]), (110, [foto('cuerpo_perfil')]),
     (120, [camara(-30, 11, 4, 0, 8, 0)]), (130, [foto('cuerpo_espalda')]),
     (140, [camara(20, 2, -16, 0, 10, 0)]), (150, [foto('cuerpo_abajo')]),
     (160, [camara(24, 16, -24, 0, 8, 0)]), (170, [foto('cuerpo_tres_cuartos')])],
    195, 'fases')

ESCENAS['fases'] = (
    [nerea(), camara(30, 10, 6, 0, 8, 0)] +
    titulo('Las cuatro fases', 'Una cadena menos y el corazon mas rajado en cada una'),
    [(0, [orden('despertar')]),
     (85, [foto('fase1')]),
     (95, [orden('fase')]), (150, [foto('fase2')]),
     (160, [orden('fase')]), (215, [foto('fase3')]),
     (225, [orden('fase')]), (280, [foto('fase4')])],
    300, 'rompeolas')

ESCENAS['rompeolas'] = (
    [nerea(), maniqui(24, 0), maniqui(32, 8), camara(16, 16, -38, 22, 1, 0)] +
    titulo('Rompeolas', 'Paredes de agua: tres desde la fase II'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (140, [orden('rompeolas')]), (152, [foto('rompeolas')]), (158, [foto('rompeolas_2')]), (166, [foto('rompeolas_3')]),
     (180, [camara(54, 5, 4, 10, 2, 0), orden('rompeolas')]), (194, [foto('rompeolas_frente')]),
     (200, [foto('rompeolas_frente_2')])],
    230, 'remolino')

ESCENAS['remolino'] = (
    [nerea(), maniqui(26, 4), maniqui(-20, 14), maniqui(12, -30), camara(-8, 36, -34, 0, 0, 0)] +
    titulo('Remolino', 'El agua del suelo arrastra; con una antorcha, burbuja de aire'),
    [(0, [orden('despertar')]),
     (80, [orden('remolino')]), (106, [foto('remolino')]), (130, [foto('remolino_2')]),
     (140, [camara(30, 8, -20, 0, 2, 0)]), (150, [foto('remolino_lado')])],
    190, 'burbujas')

ESCENAS['burbujas'] = (
    [nerea(), maniqui(16, 6), maniqui(14, -8), maniqui(22, 0), camara(8, 14, -30, 12, 4, 0)] +
    titulo('Burbujas bomba', 'El corazon dentro y en el suelo hasta donde revientan'),
    [(0, [orden('despertar')]),
     (80, [orden('burbujas')]), (92, [foto('burbujas')]), (100, [foto('burbujas_2')]),
     (110, [camara(30, 6, -10, 14, 4, 0)]), (116, [foto('burbujas_cerca')])],
    150, 'molino')

ESCENAS['molino'] = (
    [nerea(), maniqui(14, 6), maniqui(-10, 12), maniqui(8, -16), camara(-6, 34, -36, 0, 0, 0)] +
    titulo('Molino de anclas', 'Dos cadenas con un ancla al final; el aro marca hasta donde barren'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (140, [orden('molino')]), (162, [foto('molino')]), (176, [foto('molino_2')]),
     (186, [camara(32, 6, -22, 0, 4, 0)]), (192, [foto('molino_lado')])],
    220, 'arpon')

ESCENAS['arpon'] = (
    [nerea(), maniqui(30, 4), maniqui(26, -10), camara(10, 14, -30, 22, 4, 0)] +
    titulo('Arpon', 'El ancla vuela con su estela y un aro bajo a quien va'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (140, [orden('lejano')]), (157, [foto('arpon_ancla')]), (161, [foto('arpon_ancla_2')]),
     (168, [foto('arpon_engancha')]), (182, [foto('arpon_tira')]), (190, [foto('arpon_estocada')])],
    220, 'mirada')

MIRADOS = [maniqui(x, z, totem=True) for x, z in ((16, 6), (-14, 8), (20, -10), (-18, -6), (8, 18), (-6, -20),
                                                  (24, 2), (-24, 0), (2, 24))]

ESCENAS['mirada'] = (
    [nerea()] + MIRADOS + [camara(-26, 20, -36, 0, 9, 0)] +
    titulo('Mirada del Abismo', 'Mira a un tercio (de 9, 3); 10 impactos por ojo; si sale: totem fuera y Furia'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]), (140, [orden('fase')]),
     (200, [orden('mirada')]), (222, [foto('mirada_chorros')]),
     (226, ojos(4)), (232, [camara(26, 10, -14, 0, 10, 0)]), (238, [foto('mirada_ojos')]),
     (242, ojos(9)), (250, [foto('mirada_ojos_2')]),
     (252, [camara(13, 11, -5, 0, 10.5, 0)]), (255, [foto('mirada_ojos_cerca')]),
     (258, [camara(-26, 20, -36, 0, 9, 0)]), (262, [foto('mirada_barra')]),
     (290, [foto('mirada_sale')]), (300, [foto('mirada_furia')]),
     (310, [camara(30, 12, -20, 0, 9, 0)]), (322, [foto('mirada_furia_cerca')])],
    350, 'mirada_rota')

ESCENAS['mirada_rota'] = (
    [nerea()] + MIRADOS + [camara(26, 10, -14, 0, 10, 0)] +
    titulo('Mirada rota', 'Con los dos ojos rotos cae aturdida y se le va la Furia'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]), (140, [orden('fase')]),
     (200, [orden('furia')]),
     (210, [orden('mirada')]), (230, ojos(20)), (236, [foto('mirada_rota')]),
     (250, [camara(-26, 20, -36, 0, 9, 0)]), (260, [foto('mirada_rota_barra')])],
    300, 'geiser')

ESCENAS['geiser'] = (
    [nerea(), maniqui(14, 4), maniqui(18, -8), maniqui(22, 10), maniqui(-12, 8), camara(4, 16, -36, 14, 2, 0)] +
    titulo('Geiser del Abismo', 'Un remolino bajo cada uno; a los 1,5 s, una columna que lanza al cielo'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (140, [orden('geiser')]), (160, [foto('geiser_aviso')]), (172, [foto('geiser_aviso_2')]),
     (184, [foto('geiser_chorro')]), (190, [foto('geiser_chorro_2')]),
     (192, [camara(36, 10, -26, 16, 8, 0)]), (195, [foto('geiser_lanza')])],
    240, 'marea')

ESCENAS['marea'] = (
    [nerea()] + [maniqui(20, z, totem=(z % 24 == 0)) for z in (-24, -12, 0, 12, 24)] + [camara(-14, 30, -44, 22, 0, 0)] +
    titulo('Gran Marea', 'Una ola de lado a lado; solo el hueco se libra. Si te pilla: totem fuera'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]), (140, [orden('fase')]),
     (200, [orden('marea')]), (220, [foto('marea_hueco')]), (236, [foto('marea_alza')]),
     (250, [foto('marea_ola')]), (262, [foto('marea_ola_2')]),
     (270, [camara(62, 6, -30, 30, 4, 0)]), (282, [foto('marea_frente')]), (300, [foto('marea_pasa')])],
    330, 'furia')

ESCENAS['furia'] = (
    [nerea(), camara(32, 10, 0, 0, 8, 0)] +
    titulo('Furia de las Mareas', 'Si la Mirada sale: mas rapida, mas dano y menos espera hasta que la derriben'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]), (140, [orden('fase')]),
     (200, [orden('furia')]), (225, [foto('furia_frente')]),
     (235, [camara(4, 12, 32, 0, 8, 0)]), (245, [foto('furia_perfil')]),
     (255, [camara(-26, 16, -20, 0, 8, 0)]), (265, [foto('furia_espalda')])],
    290, None)


def escribir(ruta, lineas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lineas) + '\n')


ENCOGER = 'execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}'
VECINOS = ('kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,'
           'type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,'
           'type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]')
LIMPIAR = ['kill @e[type=atalaya:nerea]', 'kill @e[type=atalaya:ola_nerea]', 'kill @e[type=atalaya:geiser_nerea]', 'kill @e[type=minecraft:mannequin,tag=escena]', ENCOGER, VECINOS,
           'time set noon', 'weather clear', 'difficulty normal']
PROGRAMADAS = [f'{n}/montar' for n in ESCENAS] + [f'{n}/fin' for n in ESCENAS] + \
              [f'{n}/t{t:04d}' for n, (_, pasos, _, _) in ESCENAS.items() for t, _ in pasos]
CORTAR = [f'schedule clear {NS}:{f}' for f in PROGRAMADAS]

if os.path.isdir(DESTINO):
    shutil.rmtree(DESTINO)
escribir(os.path.join(DESTINO, 'pack.mcmeta'), [json.dumps(
    {'pack': {'description': 'Atalaya: escenas de prueba de Nerea', 'min_format': 107, 'max_format': 107}}, indent=2)])
escribir(os.path.join(DESTINO, 'data/minecraft/tags/function/load.json'), [json.dumps({'values': [f'{NS}:cargar']}, indent=2)])
escribir(os.path.join(FN, 'cargar.mcfunction'), [
    f'scoreboard objectives add {NS} dummy',
    f'tellraw @a {{"text":"[Atalaya] Escenas de Nerea listas: /function {NS}:recorrido (todas) o /function {NS}:<escena>","color":"#7FE6F2"}}',
    *([f'schedule function {NS}:auto 200t replace'] if AUTO else []),
])
if AUTO:
    escribir(os.path.join(FN, 'auto.mcfunction'), [
        f'execute unless entity @a run schedule function {NS}:auto 20t replace',
        f'execute as @a[limit=1] at @s run function {NS}:{AUTO}',
    ])
escribir(os.path.join(FN, 'parar.mcfunction'), [
    f'scoreboard players set #recorrido {NS} 0',
    *CORTAR,
    *[ANCLA + c for c in LIMPIAR],
    'kill @e[type=minecraft:marker,tag=ancla_nerea]',
    'gamerule spawn_mobs true',
    'gamemode creative @a',
])
escribir(os.path.join(FN, 'ancla.mcfunction'), [
    f'execute unless entity @e[type=minecraft:marker,tag=ancla_nerea] run function {NS}:ancla_nueva',
    'gamerule spawn_mobs false',
    'gamemode spectator @a',
    'difficulty normal',
])
escribir(os.path.join(FN, 'ancla_nueva.mcfunction'), [
    'execute at @s positioned over motion_blocking_no_leaves run summon minecraft:marker ~ ~ ~ {Tags:["ancla_nerea"]}',
])
escribir(os.path.join(FN, 'recorrido.mcfunction'), [
    '# El recorrido empieza donde estas; con un pueblo cerca, 120 bloques al otro lado',
    *CORTAR,
    'kill @e[type=minecraft:marker,tag=ancla_nerea]',
    'execute at @s if entity @e[type=minecraft:villager,distance=..90] facing entity '
    '@e[type=minecraft:villager,distance=..90,sort=nearest,limit=1] feet rotated ~180 0 run tp @s ^ ^ ^120',
    f'function {NS}:ancla',
    f'scoreboard players set #recorrido {NS} 1',
    *titulo('Nerea, el remake', 'Todo lo nuevo, desde varios angulos'),
    f'schedule function {NS}:cuerpo/montar 80t replace',
])
for nombre, (montar, pasos, dura, sigue) in ESCENAS.items():
    escribir(os.path.join(FN, nombre + '.mcfunction'), [
        f'# Solo la escena "{nombre}": en el ancla que haya, o donde estas',
        *CORTAR,
        f'function {NS}:ancla',
        f'scoreboard players set #recorrido {NS} 0',
        f'function {NS}:{nombre}/montar',
    ])
    lineas = [ANCLA + c for c in LIMPIAR + montar]
    for t, _ in pasos:
        lineas.append(f'schedule function {NS}:{nombre}/t{t:04d} {t + PAUSA}t append')
    lineas.append(f'schedule function {NS}:{nombre}/fin {dura + PAUSA}t append')
    escribir(os.path.join(FN, nombre, 'montar.mcfunction'), lineas)
    for t, ordenes in pasos:
        escribir(os.path.join(FN, nombre, f't{t:04d}.mcfunction'), [ANCLA + c for c in ordenes])
    fin = [ANCLA + c for c in LIMPIAR[:2]]
    if sigue:
        fin.append(f'execute if score #recorrido {NS} matches 1 run function {NS}:{sigue}/montar')
        fin.append(f'execute unless score #recorrido {NS} matches 1 run gamemode creative @a')
        fin.append(f'execute unless score #recorrido {NS} matches 1 run gamerule spawn_mobs true')
    else:
        fin += [*titulo('Fin', f'Repite cualquiera: /function {NS}:<nombre>'), 'gamemode creative @a', 'gamerule spawn_mobs true']
    escribir(os.path.join(FN, nombre, 'fin.mcfunction'), fin)

total = 80 + sum(dura + PAUSA for _, _, dura, _ in ESCENAS.values())
print('datapack en', DESTINO, '|', len(ESCENAS), 'escenas |', f'recorrido de {total / 20:.0f} s',
      f'| arranca solo: {AUTO}' if AUTO else '')
if len(ARGS) > 1:
    dp = os.path.join(ARGS[1], 'datapacks', 'atalaya_escenas_nerea')
    if os.path.isdir(dp):
        shutil.rmtree(dp)
    shutil.copytree(DESTINO, dp)
    print('copiado en', dp)
