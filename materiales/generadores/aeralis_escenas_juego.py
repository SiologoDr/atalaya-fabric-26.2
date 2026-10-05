"""
El datapack de las escenas de prueba del remake de Aeralis (octubre de 2026):
monta cada cosa nueva o cambiada delante de quien mira, desde varios angulos,
la dispara con /atalaya aeralis <orden> y, si en run/ existe atalaya_fotos.flag,
saca una foto en el momento justo (FotosPrueba).

Funciona como el de Rajang (rajang_escenas_juego.py): todo va relativo a un
"ancla" en el suelo de un mundo plano, despejado unos 90 x 90 bloques; el
recorrido la pone donde estas, o a 120 bloques del pueblo si hay aldeanos
cerca; cada escena abre con su titulo y la accion empieza cuando se va; cada
comando corta lo que haya en marcha. Las presas son maniquies.

  /function escenas_aeralis:recorrido     todas, una detras de otra
  /function escenas_aeralis:<escena>      solo esa (cuerpo, fases, aleteo,
                                          tornados, viento, caceria, picado,
                                          escamas, juicio, furia)
  /function escenas_aeralis:parar         lo quita todo y te deja en creativo

Uso: python aeralis_escenas_juego.py <raiz del proyecto> [carpeta del mundo] [--auto[=escena]]
"""
import json, os, shutil, sys

AUTO = next((a.split('=', 1)[1] if '=' in a else 'recorrido' for a in sys.argv[1:] if a.startswith('--auto')), None)
ARGS = [a for a in sys.argv[1:] if not a.startswith('--auto')]
RAIZ = ARGS[0]
NS = 'escenas_aeralis'
DESTINO = os.path.join(RAIZ, 'materiales/escenas/atalaya_escenas_aeralis')
FN = os.path.join(DESTINO, f'data/{NS}/function')
ANCLA = f'execute at @e[type=minecraft:marker,tag=ancla_aeralis,limit=1] run '
PAUSA = 45


def maniqui(x, z, nombre='presa', vida=1000, totem=False):
    mano = ',equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}' if totem else ''
    return (f'summon minecraft:mannequin ~{x} ~ ~{z} {{Tags:["escena"],CustomName:"{nombre}",'
            f'attributes:[{{id:"minecraft:max_health",base:{vida}}}],Health:{vida}f{mano}}}')


def aeralis(x=0, z=0, giro=-90):
    """Aeralis en el ancla mirando hacia +X (giro -90)."""
    return f'summon atalaya:aeralis ~{x} ~ ~{z} {{Rotation:[{giro}f,0f]}}'


def camara(x, y, z, mx, my, mz):
    return f'tp @a ~{x} ~{y} ~{z} facing ~{mx} ~{my} ~{mz}'


def titulo(t, sub, color='#9FE8FF'):
    return [f'title @a times 5 {PAUSA - 5} 10',
            f'title @a subtitle {json.dumps({"text": sub, "color": "#E4ECF8"}, ensure_ascii=False)}',
            f'title @a title {json.dumps({"text": t, "color": color}, ensure_ascii=False)}']


def foto(nombre):
    return f'tellraw @a "FOTO aeralis_{nombre}"'


def orden(o):
    return f'atalaya aeralis {o}'


# Cada escena: (montar, [(tick, [ordenes])], duracion, la siguiente). Los ticks
# cuentan desde que se va el titulo.
ESCENAS = {}

# El cuerpo: despierta sin presa y se queda en su sitio; la camara la rodea.
ESCENAS['cuerpo'] = (
    [aeralis(), camara(30, 12, 0, 0, 13, 0)] +
    titulo('Aeralis, Reina del Vendaval', 'El remake: alas de 38 bloques, halo, corona y melena'),
    [(0, [orden('despertar')]),
     (95, [foto('cuerpo_frente')]),
     (105, [camara(2, 14, 34, 0, 13, 0)]), (115, [foto('cuerpo_perfil')]),
     (125, [camara(-30, 14, 4, 0, 13, 0)]), (135, [foto('cuerpo_espalda')]),
     (145, [camara(16, 2, -18, 0, 14, 0)]), (155, [foto('cuerpo_abajo')]),
     (165, [camara(10, 40, 8, 0, 10, 0)]), (175, [foto('cuerpo_arriba')]),
     (185, [camara(26, 22, -22, 0, 12, 0)]), (195, [foto('cuerpo_tres_cuartos')])],
    220, 'fases')

# Las camaras de los ataques van lejos (40-55 bloques): con 38 bloques de alas
# se come el plano si se acerca. Los cambios de fase, separados: mientras se
# tambalea no se puede forzar otro.
ESCENAS['fases'] = (
    [aeralis(), camara(40, 14, 0, 0, 13, 0)] +
    titulo('Las cuatro fases', 'Brisa, Rafaga, Tempestad y Ojo de la tormenta'),
    [(0, [orden('despertar')]),
     (90, [foto('fase1')]),
     (100, [orden('fase')]), (150, [foto('fase2')]),
     (160, [orden('fase')]), (210, [foto('fase3')]),
     (220, [orden('fase')]), (270, [foto('fase4')]),
     (280, [camara(-34, 16, 12, 0, 13, 0)]), (290, [foto('fase4_espalda')])],
    310, 'aleteo')

ESCENAS['aleteo'] = (
    [aeralis(), maniqui(22, 0), camara(11, 20, -50, 11, 4, 0)] +
    titulo('Aleteo Cortante', 'Bajas del color de la fase (salta); altas blancas (apartate)'),
    [(0, [orden('despertar')]),
     (80, [orden('aleteo')]), (98, [foto('aleteo')]), (108, [foto('aleteo_2')]),
     (140, [camara(54, 8, 12, 10, 5, 0), orden('aleteo')]), (158, [foto('aleteo_frente')])],
    200, 'tornados')

ESCENAS['tornados'] = (
    [aeralis(), maniqui(14, 4), maniqui(10, -8), camara(8, 22, -52, 8, 6, 0)] +
    titulo('Tornados', 'El aro marca hasta donde atrapa; los tres anillos son sus tres golpes'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]), (130, [orden('fase')]),
     (180, [orden('tornados')]), (235, [foto('tornados')]), (265, [foto('tornados_2')]),
     (280, [camara(30, 10, -26, 10, 6, 0)]), (290, [foto('tornados_cerca')])],
    330, 'viento')

ESCENAS['viento'] = (
    [aeralis(), maniqui(14, 4), maniqui(10, -8), maniqui(-6, 10), camara(8, 22, -52, 8, 8, 0)] +
    titulo('Viento de vuelta', 'Cada tornado roto le devuelve su viento; con 10, 20 o 30 cae aturdida 5 s'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (130, [orden('tornados')]), (200, [orden('romper')]), (210, [foto('viento_orbes')]),
     (235, [foto('viento_barra')]),
     (245, [camara(24, 14, -30, 4, 13, 0), orden('viento')]), (258, [foto('viento_llega')]),
     (282, [foto('viento_aturdida')]),
     (290, [camara(30, 6, -22, 0, 4, 0)]), (305, [foto('viento_aturdida_2')])],
    360, 'caceria')

ESCENAS['caceria'] = (
    [aeralis(), maniqui(22, 6), camara(14, 16, -46, 14, 8, 3)] +
    titulo('Caceria del Vendaval', 'Las rafagas son polillas de viento'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (130, [orden('caceria')]), (152, [foto('caceria_marca')]),
     (180, [orden('doble')]), (195, [foto('caceria_polillas')]), (203, [foto('caceria_polillas_2')])],
    240, 'picado')

ESCENAS['picado'] = (
    [aeralis(), maniqui(26, 0, totem=True), maniqui(16, 3, 'en medio', totem=True), camara(16, 26, -52, 20, 2, 0)] +
    titulo('Picado del Vendaval', 'Si te pilla, te gasta el totem y te manda al cielo; luego se posa 3 s'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (130, [orden('picado')]), (150, [foto('picado_linea')]), (162, [foto('picado_lanza')]),
     (170, [camara(28, 16, -48, 28, 16, 0)]), (178, [foto('picado_cielo')]), (190, [foto('picado_cielo_2')]),
     (204, [foto('picado_caida')]),
     (212, [camara(56, 8, -24, 40, 4, 0)]), (222, [foto('posada')])],
    280, 'escamas')

ESCENAS['escamas'] = (
    [aeralis(), maniqui(12, 6), maniqui(14, 8), maniqui(-6, 8), camara(-10, 24, -44, 4, 2, 0)] +
    titulo('Escamas de Tormenta', 'Si te cae una descarga, 2 s paralizado: puedes pegar, pero no moverte'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]), (130, [orden('fase')]),
     (180, [orden('escamas')]), (215, [foto('escamas')]), (228, [orden('mancha')]), (245, [foto('escamas_2')]),
     (246, [camara(19, 3, 2, 13, 1, 7)]), (252, [foto('escamas_paralisis')]), (264, [foto('escamas_paralisis_2')])],
    300, 'juicio')

ESCENAS['juicio'] = (
    [aeralis()] + [maniqui(x, z, totem=True) for x, z in ((10, 6), (-8, 8), (14, -10), (-12, -6), (4, 14), (-4, -14),
                                                       (18, 2), (-18, 0), (0, 20))] +
    [camara(-24, 24, -44, 0, 10, 0)] +
    titulo('Juicio del Ciclon', 'Un ciclon atrapa a un tercio (de 9, 3); si no rompen los 4 cristales: totem fuera y Furia'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]), (130, [orden('fase')]), (180, [orden('fase')]),
     (230, [orden('juicio')]), (300, [foto('juicio_atrapa')]), (330, [foto('juicio')]),
     (340, [camara(18, 6, -16, 0, 12, 0)]), (352, [foto('juicio_cerca')]),
     (500, [camara(-30, 22, -50, 0, 12, 0)]), (548, [foto('juicio_golpe')]),
     (580, [foto('juicio_furia')]),
     (590, [camara(30, 16, -34, 0, 13, 0)]), (610, [foto('juicio_furia_cerca')])],
    650, 'furia')

ESCENAS['furia'] = (
    [aeralis(), camara(36, 14, 0, 0, 13, 0)] +
    titulo('Furia del Vendaval', 'Juicio fallido: mas rapida, mas dano y menos espera hasta que la derriben'),
    [(0, [orden('despertar')]),
     (80, [orden('fase')]),
     (130, [orden('furia')]), (160, [foto('furia_frente')]),
     (170, [camara(4, 16, 36, 0, 13, 0)]), (180, [foto('furia_perfil')]),
     (190, [camara(-30, 20, -20, 0, 12, 0)]), (200, [foto('furia_espalda')])],
    230, None)


def escribir(ruta, lineas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lineas) + '\n')


ENCOGER = 'execute as @e[type=minecraft:slime,distance=..80] run data merge entity @s {Size:0}'
VECINOS = ('kill @e[distance=..80,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,'
           'type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,'
           'type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]')
LIMPIAR = ['kill @e[type=atalaya:aeralis]', 'kill @e[type=minecraft:mannequin,tag=escena]', ENCOGER, VECINOS,
           'time set noon', 'weather clear', 'difficulty normal']
PROGRAMADAS = [f'{n}/montar' for n in ESCENAS] + [f'{n}/fin' for n in ESCENAS] + \
              [f'{n}/t{t:04d}' for n, (_, pasos, _, _) in ESCENAS.items() for t, _ in pasos]
CORTAR = [f'schedule clear {NS}:{f}' for f in PROGRAMADAS]

if os.path.isdir(DESTINO):
    shutil.rmtree(DESTINO)
escribir(os.path.join(DESTINO, 'pack.mcmeta'), [json.dumps(
    {'pack': {'description': 'Atalaya: escenas de prueba de Aeralis', 'min_format': 107, 'max_format': 107}}, indent=2)])
escribir(os.path.join(DESTINO, 'data/minecraft/tags/function/load.json'), [json.dumps({'values': [f'{NS}:cargar']}, indent=2)])
escribir(os.path.join(FN, 'cargar.mcfunction'), [
    f'scoreboard objectives add {NS} dummy',
    f'tellraw @a {{"text":"[Atalaya] Escenas de Aeralis listas: /function {NS}:recorrido (todas) o /function {NS}:<escena>","color":"#9FE8FF"}}',
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
    'kill @e[type=minecraft:marker,tag=ancla_aeralis]',
    'gamerule spawn_mobs true',
    'gamemode creative @a',
])
escribir(os.path.join(FN, 'ancla.mcfunction'), [
    f'execute unless entity @e[type=minecraft:marker,tag=ancla_aeralis] run function {NS}:ancla_nueva',
    'gamerule spawn_mobs false',
    'gamemode spectator @a',
    'difficulty normal',
])
escribir(os.path.join(FN, 'ancla_nueva.mcfunction'), [
    'execute at @s positioned over motion_blocking_no_leaves run summon minecraft:marker ~ ~ ~ {Tags:["ancla_aeralis"]}',
])
escribir(os.path.join(FN, 'recorrido.mcfunction'), [
    '# El recorrido empieza donde estas; con un pueblo cerca, 120 bloques al otro lado',
    *CORTAR,
    'kill @e[type=minecraft:marker,tag=ancla_aeralis]',
    'execute at @s if entity @e[type=minecraft:villager,distance=..90] facing entity '
    '@e[type=minecraft:villager,distance=..90,sort=nearest,limit=1] feet rotated ~180 0 run tp @s ^ ^ ^120',
    f'function {NS}:ancla',
    f'scoreboard players set #recorrido {NS} 1',
    *titulo('Aeralis, el remake', 'Todo lo nuevo, desde varios angulos'),
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
    dp = os.path.join(ARGS[1], 'datapacks', 'atalaya_escenas_aeralis')
    if os.path.isdir(dp):
        shutil.rmtree(dp)
    shutil.copytree(DESTINO, dp)
    print('copiado en', dp)
