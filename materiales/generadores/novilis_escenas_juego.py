"""
El datapack de las escenas de prueba de Novilis, el Caballero Solar (octubre de
2026): monta cada ataque delante de quien mira, lo dispara con
/atalaya novilis <orden> y, si en run/ existe atalaya_fotos.flag, saca una foto
en el momento justo (FotosPrueba).

Funciona como el de Aeralis (aeralis_escenas_juego.py): todo va relativo a un
"ancla" en el suelo de un mundo plano, despejado unos 100 x 100 bloques; el
recorrido la pone donde estas, o a 120 bloques del pueblo si hay aldeanos
cerca; cada escena abre con su titulo y la accion empieza cuando se va; cada
comando corta lo que haya en marcha. Las presas son maniquies.

  /function escenas_novilis:recorrido     todas, una detras de otra
  /function escenas_novilis:<escena>      solo esa (cuerpo, fases, barrido,
                                          castigo, onda, sol, trompetas, fuentes,
                                          supernova, ofrenda, dios, furia,
                                          liberacion)
  /function escenas_novilis:ofrenda_tu    te agarra a ti: la secuencia de teclas
  /function escenas_novilis:sol_tu        te cae un sol: la Quemadura (bebe agua)
  /function escenas_novilis:parar         lo quita todo y te deja en creativo

Las dos "_tu" no van en el recorrido: te dejan en supervivencia con un totem.

Uso: python novilis_escenas_juego.py <raiz del proyecto> [carpeta del mundo] [--auto[=escena]]
"""
import json, os, shutil, sys

AUTO = next((a.split('=', 1)[1] if '=' in a else 'recorrido' for a in sys.argv[1:] if a.startswith('--auto')), None)
ARGS = [a for a in sys.argv[1:] if not a.startswith('--auto')]
RAIZ = ARGS[0]
NS = 'escenas_novilis'
DESTINO = os.path.join(RAIZ, 'materiales/escenas/atalaya_escenas_novilis')
FN = os.path.join(DESTINO, f'data/{NS}/function')
ANCLA = f'execute at @e[type=minecraft:marker,tag=ancla_novilis,limit=1] run '
PAUSA = 45
# Lo que tarda en cambiar de fase (se tambalea 60 ticks) y un poco mas.
CAMBIO = 75


def maniqui(x, z, nombre='presa', vida=1000, totem=False):
    mano = ',equipment:{mainhand:{id:"minecraft:totem_of_undying",count:1}}' if totem else ''
    return (f'summon minecraft:mannequin ~{x} ~ ~{z} {{Tags:["escena"],CustomName:"{nombre}",'
            f'attributes:[{{id:"minecraft:max_health",base:{vida}}}],Health:{vida}f{mano}}}')


def novilis(x=0, z=0, giro=-90):
    """Novilis en el ancla mirando hacia +X (giro -90)."""
    return f'summon atalaya:novilis ~{x} ~ ~{z} {{Rotation:[{giro}f,0f]}}'


def camara(x, y, z, mx, my, mz):
    return f'tp @a ~{x} ~{y} ~{z} facing ~{mx} ~{my} ~{mz}'


def titulo(t, sub, color='#FFC23A'):
    return [f'title @a times 5 {PAUSA - 5} 10',
            f'title @a subtitle {json.dumps({"text": sub, "color": "#F4E9D8"}, ensure_ascii=False)}',
            f'title @a title {json.dumps({"text": t, "color": color}, ensure_ascii=False)}']


def foto(nombre):
    return f'tellraw @a "FOTO novilis_{nombre}"'


def orden(o):
    return f'atalaya novilis {o}'


def subir(hasta, desde=0):
    """Las ordenes de fase para llegar a la fase dada, una cada CAMBIO ticks."""
    return [(desde + CAMBIO * i, [orden('fase')]) for i in range(1, hasta)]


# Cada escena: (montar, [(tick, [ordenes])], duracion, la siguiente). Los ticks
# cuentan desde que se va el titulo. Mide 16 bloques (18 con el halo): las
# camaras del cuerpo van a unos 30 y las de los ataques a 40-50.
ESCENAS = {}

ESCENAS['cuerpo'] = (
    [novilis(), camara(30, 9, 0, 0, 9, 0)] +
    titulo('Novilis, el Caballero Solar', '16 bloques hasta el yelmo, 18 con el halo'),
    [(4, [foto('dormido')]),
     (6, [orden('despertar')]), (30, [foto('despertar')]), (56, [foto('despertar_ruge')]),
     (85, [foto('frente')]),
     (95, [camara(0, 10, 30, 0, 9, 0)]), (105, [foto('perfil')]),
     (115, [camara(-30, 10, 0, 0, 9, 0)]), (125, [foto('espalda')]),
     (135, [camara(12, 2, -14, 0, 12, 0)]), (145, [foto('abajo')]),
     (155, [camara(20, 18, -20, 0, 10, 0)]), (165, [foto('tres_cuartos')]),
     (175, [camara(9, 15, 3, 0, 15, 0)]), (185, [foto('cabeza')])],
    205, 'andar')

# El paso: el cebo se aleja 0,3 bloques por tick y el lo sigue sin atacar
# (perseguir), visto de lado y de tres cuartos.
CEBO = 'execute as @e[type=minecraft:mannequin,tag=cebo] at @s run tp @s ~0.3 ~ ~'
ESCENAS['andar'] = (
    [novilis(), 'summon minecraft:mannequin ~14 ~ ~ {Tags:["escena","cebo"],CustomName:"cebo",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}',
     camara(20, 7, -34, 20, 6, 0)] +
    titulo('El paso', 'Los pies van con el suelo; la capa y el tabardo con el peso'),
    [(0, [orden('despertar')]), (60, [orden('perseguir')])] +
    [(60 + k, [CEBO]) for k in range(0, 150)] +
    [(62 + 40 * k, [orden('perseguir')]) for k in range(4)] +
    [(110, [foto('lado')]), (118, [foto('lado_2')]), (126, [foto('lado_3')]),
     (140, [camara(70, 9, -26, 48, 6, 0)]), (160, [foto('frente')]), (170, [foto('frente_2')])],
    220, 'fases')

# La carrera: el cebo empieza a 40 bloques y se aleja a 0,7 bloques por tick
# (mas deprisa que el): el lo persigue corriendo, visto de lado.
CEBO_RAPIDO = 'execute as @e[type=minecraft:mannequin,tag=cebo] at @s run tp @s ~0.7 ~ ~'
ESCENAS['correr'] = (
    [novilis(), 'summon minecraft:mannequin ~40 ~ ~ {Tags:["escena","cebo"],CustomName:"cebo",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}',
     camara(30, 8, -40, 30, 6, 0)] +
    titulo('La carrera', 'Si su presa se aleja, corre: zancada larga con vuelo'),
    [(0, [orden('despertar')]), (60, [orden('perseguir')])] +
    [(60 + k, [CEBO_RAPIDO]) for k in range(0, 110)] +
    [(62 + 40 * k, [orden('perseguir')]) for k in range(3)] +
    [(80, [camara(40, 8, -40, 40, 6, 0)]), (100, [foto('lado'), camara(55, 8, -40, 55, 6, 0)]),
     (106, [foto('lado_2')]), (112, [foto('lado_3')]), (118, [foto('lado_4')]),
     (125, [camara(100, 10, -18, 70, 6, 0)]), (140, [foto('frente')]), (146, [foto('frente_2')])],
    190, 'fases')

ESCENAS['fases'] = (
    [novilis(), camara(32, 9, 0, 0, 9, 0)] +
    titulo('Las cuatro fases', 'Brasa, Llama, Sol blanco y Sol carmesi'),
    [(0, [orden('despertar')]), (75, [foto('fase1')])] +
    [(75 + CAMBIO * i + 10, [orden('fase')]) for i in range(3)] +
    [(75 + CAMBIO * i + 10 + 30, [foto(f'tambaleo{i + 2}')]) for i in range(3)] +
    [(75 + CAMBIO * (i + 1) + 5, [foto(f'fase{i + 2}')]) for i in range(3)] +
    [(330, [camara(-28, 12, 14, 0, 9, 0)]), (340, [foto('fase4_espalda')])],
    360, 'barrido')

ESCENAS['barrido'] = (
    [novilis(), maniqui(8, 0), maniqui(10, -5), camara(10, 14, -34, 8, 5, 0)] +
    titulo('Barrido Solar', 'Cuatro tajos; cada uno suelta una media luna de fuego'),
    [(0, [orden('despertar')]),
     (75, [orden('barrido')]), (83, [foto('tajo1')]), (95, [foto('tajo2')]), (105, [foto('tajo3')]),
     (117, [foto('tajo4')]), (128, [foto('tajos_vuelan')]),
     (165, [camara(40, 6, 12, 0, 6, 0), orden('barrido')]), (173, [foto('barrido_frente')]),
     (185, [foto('barrido_frente_2')])],
    250, 'castigo')

ESCENAS['castigo'] = (
    [novilis()] + [maniqui(x, z, totem=True) for x, z in ((14, 6), (10, -8), (-6, 10), (4, -14))] +
    [camara(-10, 24, -42, 4, 2, 0)] +
    titulo('Castigo Divino', 'Alza la espada y marca a cada uno: el rayo cae donde estaba'),
    [(0, [orden('despertar')]),
     (75, [orden('castigo')]), (91, [foto('alza')]), (99, [foto('marcas')]), (119, [foto('rayos')]),
     (126, [foto('rayos_2')]),
     (140, [camara(24, 4, -10, 10, 3, 0), orden('castigo')]), (186, [foto('rayos_cerca')])],
    230, 'onda')

ESCENAS['onda'] = (
    [novilis(), maniqui(10, 0), maniqui(16, 8), camara(0, 20, -46, 0, 0, 0)] +
    titulo('Onda de Fuego', 'Clava la espada: un anillo de fuego a ras de suelo (saltalo)'),
    [(0, [orden('despertar')])] + subir(2, 0) +
    [(150, [orden('onda')]), (196, [foto('clava')]), (208, [foto('onda_1')]), (220, [foto('onda_2')]),
     (232, [camara(22, 3, -14, 8, 1, 0), orden('onda')]), (288, [foto('onda_cerca')])],
    320, 'sol')

ESCENAS['sol'] = (
    [novilis(), maniqui(18, 4, totem=True), maniqui(14, -10, totem=True), maniqui(24, -2, totem=True),
     camara(4, 22, -48, 12, 2, 0)] +
    titulo('Sol Abrasador', 'Tres soles; el sello marca donde caen y dejan lava'),
    [(0, [orden('despertar')])] + subir(2, 0) +
    [(150, [orden('sol')]), (164, [foto('forma')]), (174, [foto('lanza1')]), (196, [foto('lanza2')]),
     (216, [foto('lanza3')]), (234, [foto('charcos')]),
     (240, [camara(30, 8, -18, 18, 1, 0)]), (250, [foto('charcos_cerca')])],
    300, 'trompetas')

ESCENAS['trompetas'] = (
    [novilis(), camara(-30, 16, -32, 0, 5, 0)] +
    titulo('Trompetas del Apocalipsis', 'Cuatro angeles tocan su melodia: rompedlos antes de que acabe'),
    [(0, [orden('despertar')])] + subir(2, 0) +
    [(150, [orden('trompetas')]), (176, [foto('alza')]), (192, [foto('salen')]), (215, [foto('estatuas')]),
     (225, [camara(0, 34, -34, 0, 0, 0)]), (235, [foto('estatuas_arriba')]),
     (245, [camara(-24, 6, -10, 0, 5, 0)]), (255, [foto('estatua_cerca')])] +
    [(270 + 3 * i, [orden('estatua')]) for i in range(10)] +
    [(305, [foto('estatua_rota'), camara(0, 34, -34, 0, 0, 0)]), (315, [foto('rota_arriba')]),
     (325, [camara(-30, 16, -32, 0, 5, 0)]),
     (640, [foto('melodia_acaba')]), (670, [foto('furia')]), (700, [foto('furia_2')])],
    740, 'fuentes')

ESCENAS['fuentes'] = (
    [novilis(), maniqui(22, 0, totem=True), camara(-14, 22, -44, 0, 5, 0)] +
    titulo('Fuentes Solares', 'Tres fuentes le dan fuego; rotas, cae aturdido'),
    [(0, [orden('despertar')])] + subir(3, 0) +
    [(225, [orden('fuentes')]), (243, [foto('clava')]), (260, [foto('fuentes')]), (300, [foto('carga')]),
     (310, [camara(16, 9, -18, 0, 8, 0)]), (320, [foto('fuente_cerca')]),
     (330, [camara(-14, 22, -44, 0, 5, 0)])] +
    [(340 + 3 * i, [orden('fuente')]) for i in range(30)] +
    [(372, [foto('una_rota')]), (436, [foto('aturdido')]),
     (446, [camara(26, 5, 12, 0, 4, 0)]), (456, [foto('aturdido_cerca')])],
    520, 'supernova')

ESCENAS['supernova'] = (
    [novilis(), maniqui(16, 6, totem=True), maniqui(-10, 12, totem=True), camara(-20, 30, -56, 0, 6, 0)] +
    titulo('Supernova', 'Si las fuentes siguen en pie al acabar la carga'),
    [(0, [orden('despertar')])] + subir(3, 0) +
    # Con las tres fuentes en pie carga en 300 ticks (CARGA_CON): estalla hacia el 541.
    [(225, [orden('fuentes')]), (390, [foto('carga_media')]), (530, [foto('carga_llena')]),
     (544, [foto('supernova')]), (552, [foto('supernova_2')]), (566, [foto('supernova_3')]),
     (600, [foto('despues')])],
    640, 'ofrenda')

ESCENAS['ofrenda'] = (
    [novilis(), maniqui(10, 0, totem=True), camara(16, 12, -28, 4, 9, 0)] +
    titulo('Ofrenda al Sol', 'Te agarra y te alza al sol: 15 letras en 8 s (20 en la fase IV)'),
    [(0, [orden('despertar')])] + subir(3, 0) +
    [(225, [orden('ofrenda')]), (235, [foto('marca')]), (253, [foto('agarra')]), (275, [foto('alzado')]),
     (285, [camara(12, 15, 6, 0, 14, 3)]), (300, [foto('alzado_cerca')]),
     (310, [camara(16, 12, -28, 4, 9, 0)]), (425, [foto('fallo')]), (450, [foto('furia')])],
    490, 'dios')

ESCENAS['dios'] = (
    [novilis()] + [maniqui(x, z, totem=True) for x, z in ((12, 6), (-8, 8), (14, -10), (-12, -6))] +
    [camara(-20, 28, -48, 0, 6, 0)] +
    titulo('Dios de la Guerra', 'Fase IV: suelta la espada y llena las zonas carmesi de soles'),
    [(0, [orden('despertar')])] + subir(4, 0) +
    [(300, [orden('dios')]), (312, [foto('suelta')]), (322, [foto('marcas')]), (334, [foto('lanza1')]),
     (356, [foto('lanza2')]), (376, [foto('lanza3')]), (392, [foto('explosiones')]),
     (400, [camara(28, 10, -16, 0, 9, 0)]), (420, [foto('recoge')])],
    450, 'furia')

ESCENAS['furia'] = (
    [novilis(), camara(24, 10, -6, 0, 10, 0)] +
    titulo('Furia y Grito', 'Furia: aura azul, mas rapido. Grito: el aura carmesi'),
    [(0, [orden('despertar')]),
     (75, [orden('furia')]), (90, [foto('furia_grito')]), (125, [foto('furia')]),
     (135, [camara(-22, 12, 12, 0, 10, 0)]), (145, [foto('furia_espalda')]),
     (150, [camara(10, 15, -8, 0, 13, 0)]), (152, [foto('furia_cerca')]),
     (155, [orden('furia'), orden('grito'), camara(24, 10, -6, 0, 10, 0)]), (175, [foto('grito')]),
     (185, [orden('grito'), orden('dios')]), (210, [foto('dios')]), (235, [foto('dios_2')])],
    290, 'liberacion')

ESCENAS['liberacion'] = (
    [novilis(), camara(6, 8, 30, 0, 7, 0)] +
    titulo('Liberacion', 'Libre del fuego: se arrodilla, se dora y se deshace en luz'),
    [(0, [orden('despertar')]),
     (75, [orden('liberar')]), (95, [foto('cae')]), (130, [foto('rodilla')]), (150, [foto('oro')]),
     (190, [foto('oro_2')]), (240, [foto('disuelve')]), (268, [foto('disuelve_2')])],
    300, None)

# Las que te tienen a ti de presa (no van en el recorrido): supervivencia, un
# totem en la otra mano, netherita con Proteccion IV y la camara en tus ojos.
PROTE = '[minecraft:enchantments={"minecraft:protection":4}]'
ARMADURA = f'function {NS}:armadura'
TU = {}
TU['ofrenda_tu'] = (
    [novilis(), 'tp @a ~12 ~ ~ facing ~0 ~10 ~0'] +
    titulo('Ofrenda al Sol (tu)', 'Pulsa las letras en orden: Escape no la para'),
    [(0, [orden('despertar')])] + subir(3, 0) +
    [(215, ['effect clear @a', 'tp @a ~12 ~ ~ facing ~0 ~10 ~0', 'gamemode survival @a', ARMADURA,
            'item replace entity @a weapon.offhand with minecraft:totem_of_undying']),
     (225, [orden('ofrenda')]), (240, [foto('tu_marca')]),
     (260, [foto('tu_agarra')]), (290, [foto('tu_teclas')]), (330, [foto('tu_teclas_2')]),
     (420, [foto('tu_fin')]), (436, [foto('tu_fin_2')])],
    480)
TU['sol_tu'] = (
    [novilis(), 'tp @a ~16 ~ ~ facing ~0 ~10 ~0'] +
    titulo('La Quemadura (tu)', 'Un sol te deja quemado; el agua no la apaga, una botella de agua si'),
    [(0, [orden('despertar')])] + subir(2, 0) +
    # Sin armadura, los tres soles (van los tres a por ti si estas solo) te
    # matan, y con netherita y Proteccion IV los tres juntos tambien (unos 23 de
    # vida): Resistencia IV para aguantarlos. Cuando caen, Novilis se va (kill,
    # sin liberacion) para que puedas ver la Quemadura y beber agua tranquilo.
    [(140, ['effect clear @a', 'tp @a ~16 ~ ~ facing ~0 ~10 ~0', 'gamemode survival @a', ARMADURA,
            'item replace entity @a weapon.offhand with minecraft:totem_of_undying',
            'effect give @a minecraft:resistance 40 3 true',
            'give @a minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}] 2']),
     (150, [orden('sol')]), (200, [foto('tu_sol')]), (240, [foto('tu_cae')]),
     (262, ['kill @e[type=atalaya:novilis]', 'tellraw @a {"text":"[Atalaya] Bebe una botella de agua para quitarte la Quemadura.","color":"#FFC23A"}']),
     (270, [foto('tu_quemado')]), (330, [foto('tu_quemado_2')])],
    600)


def escribir(ruta, lineas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lineas) + '\n')


ENCOGER = 'execute as @e[type=minecraft:slime,distance=..90] run data merge entity @s {Size:0}'
VECINOS = ('kill @e[distance=..90,type=!minecraft:player,type=!minecraft:marker,type=!minecraft:mannequin,'
           'type=!minecraft:villager,type=!minecraft:iron_golem,type=!minecraft:item_frame,'
           'type=!minecraft:glow_item_frame,type=!minecraft:painting,type=!minecraft:armor_stand]')
LIMPIAR = ['kill @e[type=atalaya:novilis]', 'kill @e[type=minecraft:mannequin,tag=escena]',
           'kill @e[type=atalaya:estatua_novilis]', 'kill @e[type=atalaya:fuente_solar]',
           'kill @e[type=atalaya:sol_novilis]', 'kill @e[type=atalaya:sello_sol]',
           'kill @e[type=atalaya:onda_fuego]', 'kill @e[type=atalaya:tajo_novilis]',
           ENCOGER, VECINOS, 'time set noon', 'weather clear', 'difficulty normal']
TODAS = {**{n: (m, p, d) for n, (m, p, d, _) in ESCENAS.items()}, **TU}
PROGRAMADAS = [f'{n}/montar' for n in TODAS] + [f'{n}/fin' for n in TODAS] + \
              [f'{n}/t{t:04d}' for n, (_, pasos, _) in TODAS.items() for t in sorted({t for t, _ in pasos})]
CORTAR = [f'schedule clear {NS}:{f}' for f in PROGRAMADAS]

if os.path.isdir(DESTINO):
    shutil.rmtree(DESTINO)
escribir(os.path.join(DESTINO, 'pack.mcmeta'), [json.dumps(
    {'pack': {'description': 'Atalaya: escenas de prueba de Novilis', 'min_format': 107, 'max_format': 107}}, indent=2)])
escribir(os.path.join(DESTINO, 'data/minecraft/tags/function/load.json'), [json.dumps({'values': [f'{NS}:cargar']}, indent=2)])
escribir(os.path.join(FN, 'cargar.mcfunction'), [
    f'scoreboard objectives add {NS} dummy',
    f'tellraw @a {{"text":"[Atalaya] Escenas de Novilis listas: /function {NS}:recorrido (todas) o /function {NS}:<escena>","color":"#FFC23A"}}',
    *([f'schedule function {NS}:auto 200t replace'] if AUTO else []),
])
if AUTO:
    # --auto=a,b,c: varias escenas seguidas (cada una cuando acaba la anterior).
    cola = AUTO.split(',')
    escribir(os.path.join(FN, 'auto.mcfunction'), [
        f'execute unless entity @a run schedule function {NS}:auto 20t replace',
        f'execute if entity @a as @a[limit=1] at @s run function {NS}:{cola[0]}',
        *[f'execute if entity @a run schedule function {NS}:auto_{k} '
          f'{sum(TODAS[c][2] + PAUSA + 40 for c in cola[:k])}t replace' for k in range(1, len(cola))],
    ])
    for k in range(1, len(cola)):
        # una escena de otro datapack (ns:escena) solo puede ir la ultima: no se sabe lo que dura
        fn = cola[k] if ':' in cola[k] else f'{NS}:{cola[k]}'
        escribir(os.path.join(FN, f'auto_{k}.mcfunction'), [f'execute as @a[limit=1] at @s run function {fn}'])
escribir(os.path.join(FN, 'parar.mcfunction'), [
    f'scoreboard players set #recorrido {NS} 0',
    *CORTAR,
    *[ANCLA + c for c in LIMPIAR],
    'kill @e[type=minecraft:marker,tag=ancla_novilis]',
    'effect clear @a',
    'gamerule spawn_mobs true',
    'gamemode creative @a',
])
escribir(os.path.join(FN, 'ancla.mcfunction'), [
    f'execute unless entity @e[type=minecraft:marker,tag=ancla_novilis] run function {NS}:ancla_nueva',
    'gamerule spawn_mobs false',
    'gamemode spectator @a',
    'difficulty normal',
])
escribir(os.path.join(FN, 'ancla_nueva.mcfunction'), [
    'execute at @s positioned over motion_blocking_no_leaves run summon minecraft:marker ~ ~ ~ {Tags:["ancla_novilis"]}',
])
escribir(os.path.join(FN, 'recorrido.mcfunction'), [
    '# El recorrido empieza donde estas; con un pueblo cerca, 120 bloques al otro lado',
    *CORTAR,
    'kill @e[type=minecraft:marker,tag=ancla_novilis]',
    'execute at @s if entity @e[type=minecraft:villager,distance=..90] facing entity '
    '@e[type=minecraft:villager,distance=..90,sort=nearest,limit=1] feet rotated ~180 0 run tp @s ^ ^ ^120',
    f'function {NS}:ancla',
    '# Fuera los maniquies de otras pruebas (la vitrina): serian presas',
    ANCLA + 'kill @e[type=minecraft:mannequin,distance=..90,tag=!escena]',
    f'scoreboard players set #recorrido {NS} 1',
    *titulo('Novilis, el Caballero Solar', 'El jefe del fuego, ataque a ataque'),
    f'schedule function {NS}:cuerpo/montar 80t replace',
])


def pasos_por_tick(pasos):
    juntos = {}
    for t, ordenes in pasos:
        juntos.setdefault(t, []).extend(ordenes)
    return sorted(juntos.items())


for nombre, (montar, pasos, dura) in TODAS.items():
    sigue = ESCENAS[nombre][3] if nombre in ESCENAS else None
    escribir(os.path.join(FN, nombre + '.mcfunction'), [
        f'# Solo la escena "{nombre}": en el ancla que haya, o donde estas',
        *CORTAR,
        f'function {NS}:ancla',
        ANCLA + 'kill @e[type=minecraft:mannequin,distance=..90,tag=!escena]',
        f'scoreboard players set #recorrido {NS} 0',
        f'function {NS}:{nombre}/montar',
    ])
    lineas = [ANCLA + c for c in LIMPIAR + montar]
    for t, _ in pasos_por_tick(pasos):
        lineas.append(f'schedule function {NS}:{nombre}/t{t:04d} {t + PAUSA}t append')
    lineas.append(f'schedule function {NS}:{nombre}/fin {dura + PAUSA}t append')
    escribir(os.path.join(FN, nombre, 'montar.mcfunction'), lineas)
    for t, ordenes in pasos_por_tick(pasos):
        # La foto lleva delante el nombre de la escena: alza, marcas, furia... se repiten.
        escribir(os.path.join(FN, nombre, f't{t:04d}.mcfunction'),
                 [ANCLA + c.replace('"FOTO novilis_', f'"FOTO novilis_{nombre}_') for c in ordenes])
    fin = [ANCLA + c for c in LIMPIAR[:8]]
    if sigue:
        fin.append(f'execute if score #recorrido {NS} matches 1 run function {NS}:{sigue}/montar')
        fin.append(f'execute unless score #recorrido {NS} matches 1 run gamemode creative @a')
        fin.append(f'execute unless score #recorrido {NS} matches 1 run gamerule spawn_mobs true')
    else:
        fin += [*titulo('Fin', f'Repite cualquiera: /function {NS}:<nombre>'), 'effect clear @a',
                'gamemode creative @a', 'gamerule spawn_mobs true']
    escribir(os.path.join(FN, nombre, 'fin.mcfunction'), fin)

# La netherita y la vida llena: si vienes de otra escena (o de gastar el
# totem en la Ofrenda) puedes llegar con un corazon.
escribir(os.path.join(FN, 'armadura.mcfunction'), [
    *[f'item replace entity @a armor.{hueco} with minecraft:netherite_{pieza}{PROTE}'
      for hueco, pieza in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))],
    'effect give @a minecraft:instant_health 1 9 true',
    'effect give @a minecraft:saturation 1 9 true'])

total = 80 + sum(dura + PAUSA for _, _, dura, _ in ESCENAS.values())
print('datapack en', DESTINO, '|', len(ESCENAS), 'escenas +', len(TU), 'contigo |', f'recorrido de {total / 20:.0f} s',
      f'| arranca solo: {AUTO}' if AUTO else '')
if len(ARGS) > 1:
    dp = os.path.join(ARGS[1], 'datapacks', 'atalaya_escenas_novilis')
    if os.path.isdir(dp):
        shutil.rmtree(dp)
    shutil.copytree(DESTINO, dp)
    print('copiado en', dp)
