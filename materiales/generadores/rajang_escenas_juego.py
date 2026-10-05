"""
El datapack de las escenas de prueba de Rajang: monta cada cosa nueva o
cambiada en octubre de 2026 delante de quien mira, la dispara con
/atalaya rajang <orden> y, si en run/ existe atalaya_fotos.flag, saca una foto
en el momento justo (FotosPrueba).

Todo va relativo a un "ancla" (un marker) en el suelo: hace falta un sitio
llano y despejado de unos 80 x 80 bloques (un mundo plano). El recorrido la
pone donde estas, o a 120 bloques del pueblo si tienes aldeanos cerca (Rajang
iria a por ellos); una escena suelta reusa la que haya. Las escenas usan
maniquies (minecraft:mannequin) como presas, y tu las ves en espectador, desde
un sitio elegido para cada una. Cada una abre con su titulo y la accion empieza
cuando se va, para que no tape las fotos.

  /function escenas:recorrido     todas, una detras de otra (unos 3 minutos)
  /function escenas:<escena>      solo esa (paso, garra, terremoto, embestida,
                                  estampado, tumba, sello, furia, cataclismo)
  /function escenas:parar         lo quita todo y te deja en creativo

Uso: python rajang_escenas_juego.py <raiz del proyecto> [carpeta del mundo] [--auto[=escena]]
     (con la carpeta del mundo, lo copia en su datapacks/; con --auto, el
     recorrido (o solo esa escena) arranca solo al abrir el mundo, para verlo sin
     escribir nada: vuelve a generarlo sin --auto despues, o arrancara cada vez)
"""
import json, os, shutil, sys

AUTO = next((a.split('=', 1)[1] if '=' in a else 'recorrido' for a in sys.argv[1:] if a.startswith('--auto')), None)
ARGS = [a for a in sys.argv[1:] if not a.startswith('--auto')]
RAIZ = ARGS[0]
DESTINO = os.path.join(RAIZ, 'materiales/escenas/atalaya_escenas')
FN = os.path.join(DESTINO, 'data/escenas/function')
ANCLA = 'execute at @e[type=minecraft:marker,tag=ancla,limit=1] run '
# Lo que dura el titulo de cada escena; los pasos cuentan desde que se va.
PAUSA = 45


def maniqui(x, z, nombre='presa', tags=(), vida=None):
    """Un maniqui de presa; con vida, aguanta golpes (para ver un empujon)."""
    etiquetas = ','.join(json.dumps(t) for t in ('escena', *tags))
    extra = f',attributes:[{{id:"minecraft:max_health",base:{vida}}}],Health:{vida}f' if vida else ''
    return f'summon minecraft:mannequin ~{x} ~ ~{z} {{Tags:[{etiquetas}],CustomName:"{nombre}"{extra}}}'


def rajang(x=0, z=0, giro=-90):
    """Rajang en el ancla mirando hacia +X (giro -90)."""
    return f'summon atalaya:rajang ~{x} ~ ~{z} {{Rotation:[{giro}f,0f]}}'


def camara(x, y, z, mx, my, mz):
    return f'tp @a ~{x} ~{y} ~{z} facing ~{mx} ~{my} ~{mz}'


def titulo(t, sub, color='#8CFF5A'):
    return [f'title @a times 5 {PAUSA - 5} 10',
            f'title @a subtitle {json.dumps({"text": sub, "color": "#E3ECDF"}, ensure_ascii=False)}',
            f'title @a title {json.dumps({"text": t, "color": color}, ensure_ascii=False)}']


def foto(nombre):
    return f'tellraw @a "FOTO rajang_{nombre}"'


# Cada escena: (montar, [(tick, [ordenes])], duracion, la siguiente del recorrido).
# Los ticks cuentan desde que se va el titulo (PAUSA).
ESCENAS = {}

# El cebo va 8 bloques por delante a su paso (0,33 bloques por tick, lo que anda
# el): entre 6 y 10 bloques anda sin parar. Luego salta 36 bloques atras y el
# da la vuelta y galopa hasta el.
CEBO = 'execute as @e[type=minecraft:mannequin,tag=cebo] at @s run tp @s ~0.33 ~ ~'
ESCENAS['paso'] = (
    [rajang(), maniqui(8, 0, 'cebo', ['cebo']), camara(10, 6, -20, 10, 3, 0)] +
    titulo('El paso y el galope', 'Paso lateral con la cabeza baja; galope con tiempo en el aire'),
    [(0, ['atalaya rajang perseguir']),
     (30, ['atalaya rajang perseguir', 'scoreboard players set #cebo escenas 90', 'function escenas:paso/cebo']),
     (85, [foto('paso')]),
     (130, ['tp @e[type=minecraft:mannequin,tag=cebo] ~-36 ~ ~0', camara(-4, 9, -32, -4, 3, 0),
            'atalaya rajang perseguir']),
     (160, [foto('galope')])],
    230, 'garra')
EXTRA = {'paso/cebo': [CEBO, 'scoreboard players remove #cebo escenas 1',
                       'execute if score #cebo escenas matches 1.. run schedule function escenas:paso/cebo 1t replace']}

ESCENAS['garra'] = (
    [rajang(), maniqui(16, 0), camara(8, 6, -18, 10, 2, 0)] +
    titulo('Garra Terrestre', 'El zarpazo empuja 6 bloques; los picos lanzan a 10 y dejan el Peso 3 s'),
    # El de cerca, despues de elegir presa: el zarpazo lo empuja y los picos van al de lejos.
    [(0, ['atalaya rajang garra']),
     (2, [maniqui(9, 3, 'cerca', vida=1000)]),
     (20, [foto('garra')]),
     (30, [foto('garra_empuje')])],
    90, 'terremoto')

ESCENAS['terremoto'] = (
    [rajang(), maniqui(10, 6), maniqui(14, -8), maniqui(-8, 10), maniqui(18, 2), camara(-6, 14, -22, 6, 0, 2)] +
    titulo('Terremoto Ancestral', 'Los pilares lanzan a 10 bloques'),
    [(0, ['atalaya rajang terremoto']),
     (48, [foto('terremoto')])],
    130, 'embestida')

ESCENAS['embestida'] = (
    [rajang(), maniqui(20, 0, 'presa'), camara(20, 24, -26, 24, 0, 2)] +
    titulo('Embestida de Jade', 'La flecha marca por donde carga. Su cuerpo y los pinchos matan'),
    [(0, ['atalaya rajang embestida']),
     # Los de los lados, despues de elegir presa (si no, iria a por el mas cercano).
     # La flecha mide el doble que hasta la presa: el de los 32 tambien cae.
     (2, [maniqui(6, 4.2, 'izquierda'), maniqui(11, -4.2, 'derecha'), maniqui(32, 4.2, 'pasada'),
          maniqui(12, 10, 'a salvo')]),
     (14, [foto('embestida_aviso')]),
     (30, [foto('embestida_carga')]),
     (40, [foto('embestida_lanzados')]),
     (58, [foto('embestida_final')])],
    150, 'estampado')

ESCENAS['estampado'] = (
    ['fill ~13 ~ ~-6 ~14 ~7 ~6 minecraft:stone_bricks', rajang(), maniqui(20, 0), camara(4, 8, -20, 10, 3, 0)] +
    titulo('Estampado', 'Si la Embestida da contra un muro, se queda 2 s aturdido'),
    [(0, ['atalaya rajang embestida']),
     (38, [foto('estampado')]),
     (90, ['fill ~13 ~ ~-6 ~14 ~7 ~6 minecraft:air'])],
    110, 'tumba')

ESCENAS['tumba'] = (
    [rajang(), maniqui(5, 4, 'pegado'), maniqui(16, -4, 'dentro'), maniqui(26, -12, 'dentro'), maniqui(0, -33, 'dentro'),
     maniqui(40, 3, 'fuera'), maniqui(-30, 25, 'fuera'), camara(-12, 52, -56, 0, 0, 0)] +
    titulo('Tumba de Raíces', 'Sal del círculo de 36 bloques antes de que se llene (6 s)'),
    [(0, ['atalaya rajang tumba']),
     (70, [foto('tumba_llenando')]),
     (122, [foto('tumba_estalla')])],
    180, 'sello')

# Mirando hacia +X, sus columnas quedan en las diagonales, a 18 bloques: la
# camara enfoca la de (12,7, -12,7) desde fuera. Cuando ya esta todo arriba,
# hace temblar un escalon en cada columna.
ESCENAS['sello'] = (
    [rajang(), maniqui(10, 0), camara(30, 14, -34, 12.7, 13, -12.7)] +
    titulo('Sello de la Tierra', 'Los escalones tiemblan, se caen y vuelven'),
    [(0, ['atalaya rajang sello']),
     (220, ['atalaya rajang escalon'] * 4),
     (230, [foto('sello_tiembla')]),
     (265, [foto('sello_cae')]),
     (280, [camara(0, 18, -50, 0, 13, 0)]),
     (300, ['atalaya rajang romper']),
     (303, [foto('sello_pulso')])],
    400, 'furia')

ESCENAS['furia'] = (
    [rajang(), maniqui(14, 0), camara(10, 5, -16, 2, 4, 0)] +
    titulo('Furia de Jade', 'Si el Sello falla: aura verde, más rápido y más daño'),
    [(0, ['atalaya rajang garra']),
     (30, ['atalaya rajang furia']),
     (42, [foto('furia')]),
     (60, ['atalaya rajang terremoto'])],
    180, 'cataclismo')

ESCENAS['cataclismo'] = (
    [rajang(), maniqui(12, 6), maniqui(-10, 8), maniqui(6, -14), camara(-28, 22, -28, 2, 0, 2)] +
    titulo('Cataclismo de Jade', 'Fragmentos más grandes y menos'),
    [(0, ['atalaya rajang cataclismo']),
     (84, [foto('cataclismo')]),
     (165, [foto('cataclismo_2')])],
    400, None)


def escribir(ruta, lineas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lineas) + '\n')


if os.path.isdir(DESTINO):
    shutil.rmtree(DESTINO)
escribir(os.path.join(DESTINO, 'pack.mcmeta'), [json.dumps(
    {'pack': {'description': 'Atalaya: escenas de prueba de Rajang', 'min_format': 107, 'max_format': 107}}, indent=2)])
escribir(os.path.join(DESTINO, 'data/minecraft/tags/function/load.json'), [json.dumps({'values': ['escenas:cargar']}, indent=2)])

escribir(os.path.join(FN, 'cargar.mcfunction'), [
    'scoreboard objectives add escenas dummy',
    'tellraw @a {"text":"[Atalaya] Escenas de Rajang listas: /function escenas:recorrido (todas) o /function escenas:<escena>","color":"#8CFF5A"}',
    *(['schedule function escenas:auto 200t replace'] if AUTO else []),
])
if AUTO:
    # Espera a que haya alguien en el mundo y lanza el recorrido como el
    escribir(os.path.join(FN, 'auto.mcfunction'), [
        'execute unless entity @a run schedule function escenas:auto 20t replace',
        f'execute as @a[limit=1] at @s run function escenas:{AUTO}',
    ])
# Fuera todo bicho del escenario: las ordenes van a por el ser vivo mas cercano
# (o el mas lejano, perseguir), y en un mundo plano salen slimes y ovejas. Se
# respetan los aldeanos y los adornos; mientras hay escenas no aparece nada (parar
# lo devuelve). Los slimes, antes a tamano minimo: muertos se parten en otros.
ENCOGER = 'execute as @e[type=minecraft:slime,distance=..72] run data merge entity @s {Size:0}'
VECINOS = ('kill @e[distance=..72,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,'
           'type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,'
           'type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]')
# El muro del Estampado: fuera tambien al cambiar de escena a medias.
MURO = 'fill ~13 ~ ~-6 ~14 ~7 ~6 minecraft:air replace minecraft:stone_bricks'
LIMPIAR = ['kill @e[type=atalaya:rajang]', 'kill @e[type=minecraft:mannequin,tag=escena]', ENCOGER, VECINOS, MURO,
           'time set noon', 'weather clear', 'difficulty normal']
# Todo lo que se deja programado. El juego lo guarda con el mundo: si se cierra a
# mitad de un recorrido, al volver sigue, y se pisaria con uno nuevo. Parar, el
# recorrido y cada escena suelta lo cortan antes de nada.
PROGRAMADAS = ['paso/cebo'] + [f'{n}/montar' for n in ESCENAS] + [f'{n}/fin' for n in ESCENAS] +               [f'{n}/t{t:04d}' for n, (_, pasos, _, _) in ESCENAS.items() for t, _ in pasos]
CORTAR = ['scoreboard players set #cebo escenas 0', *[f'schedule clear escenas:{f}' for f in PROGRAMADAS]]
escribir(os.path.join(FN, 'parar.mcfunction'), [
    'scoreboard players set #recorrido escenas 0',
    *CORTAR,
    *[ANCLA + c for c in LIMPIAR],
    'kill @e[type=minecraft:marker,tag=ancla]',
    'gamerule spawn_mobs true',
    'gamemode creative @a',
])
# El ancla se queda hasta parar: una escena suelta reusa la que haya (tras el
# recorrido estas en el aire, donde la ultima camara), y si no hay, va al suelo
# bajo tus pies.
escribir(os.path.join(FN, 'ancla.mcfunction'), [
    'execute unless entity @e[type=minecraft:marker,tag=ancla] run function escenas:ancla_nueva',
    'gamerule spawn_mobs false',
    'gamemode spectator @a',
    'difficulty normal',
])
escribir(os.path.join(FN, 'ancla_nueva.mcfunction'), [
    'execute at @s positioned over motion_blocking_no_leaves run summon minecraft:marker ~ ~ ~ {Tags:["ancla"]}',
    'execute at @s if entity @e[type=minecraft:villager,distance=..70] run tellraw @s {"text":"[Atalaya] Hay aldeanos cerca: '
    'Rajang puede ir a por ellos. Mejor lejos del pueblo (/function escenas:parar, alejate y vuelve a empezar).","color":"#E3B341"}',
])
escribir(os.path.join(FN, 'recorrido.mcfunction'), [
    '# El recorrido empieza donde estas; con un pueblo cerca, 120 bloques al otro lado',
    *CORTAR,
    'kill @e[type=minecraft:marker,tag=ancla]',
    'execute at @s if entity @e[type=minecraft:villager,distance=..90] facing entity '
    '@e[type=minecraft:villager,distance=..90,sort=nearest,limit=1] feet rotated ~180 0 run tp @s ^ ^ ^120',
    'function escenas:ancla',
    'scoreboard players set #recorrido escenas 1',
    *titulo('Rajang, segunda talla', 'Las mejoras de octubre, una a una'),
    'schedule function escenas:paso/montar 80t replace',
])
orden = list(ESCENAS)
for nombre, (montar, pasos, dura, sigue) in ESCENAS.items():
    escribir(os.path.join(FN, nombre + '.mcfunction'), [
        f'# Solo la escena "{nombre}": en el ancla que haya, o donde estas',
        *CORTAR,
        'function escenas:ancla',
        'scoreboard players set #recorrido escenas 0',
        f'function escenas:{nombre}/montar',
    ])
    lineas = [ANCLA + c for c in LIMPIAR + montar]
    for t, _ in pasos:
        lineas.append(f'schedule function escenas:{nombre}/t{t:04d} {t + PAUSA}t append')
    lineas.append(f'schedule function escenas:{nombre}/fin {dura + PAUSA}t append')
    escribir(os.path.join(FN, nombre, 'montar.mcfunction'), lineas)
    for t, ordenes in pasos:
        escribir(os.path.join(FN, nombre, f't{t:04d}.mcfunction'), [ANCLA + c for c in ordenes])
    fin = [ANCLA + c for c in LIMPIAR[:2]]
    if sigue:
        fin.append(f'execute if score #recorrido escenas matches 1 run function escenas:{sigue}/montar')
        fin.append(f'execute unless score #recorrido escenas matches 1 run gamemode creative @a')
        fin.append(f'execute unless score #recorrido escenas matches 1 run gamerule spawn_mobs true')
    else:
        fin += [*titulo('Fin', 'Repite cualquiera: /function escenas:<nombre>'), 'gamemode creative @a', 'gamerule spawn_mobs true',
                'scoreboard players set #recorrido escenas 0']
    escribir(os.path.join(FN, nombre, 'fin.mcfunction'), fin)

for ruta, ordenes in EXTRA.items():
    escribir(os.path.join(FN, ruta + '.mcfunction'), ordenes)

total = 80 + sum(dura + PAUSA for _, _, dura, _ in ESCENAS.values())
print('datapack en', DESTINO, '|', len(ESCENAS), 'escenas |', f'recorrido de {total / 20:.0f} s',
      f'| arranca solo: {AUTO}' if AUTO else '')
if len(ARGS) > 1:
    mundo = ARGS[1]
    dp = os.path.join(mundo, 'datapacks', 'atalaya_escenas')
    if os.path.isdir(dp):
        shutil.rmtree(dp)
    shutil.copytree(DESTINO, dp)
    print('copiado en', dp)
