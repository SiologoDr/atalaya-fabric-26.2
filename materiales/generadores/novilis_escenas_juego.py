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
                                          castigo, espada, onda, sol, trompetas,
                                          infernal, ofrenda, mar, dios, furia,
                                          liberacion)
  /function escenas_novilis:ofrenda_tu    te agarra a ti: la secuencia de teclas
  /function escenas_novilis:sol_tu        te cae un sol: la Quemadura (bebe agua)
  /function escenas_novilis:parar         lo quita todo y te deja en creativo

Las dos "_tu" no van en el recorrido: te dejan en supervivencia con un totem.

Uso: python novilis_escenas_juego.py <raiz del proyecto> [carpeta del mundo] [--auto[=escena]] [--jefes=a,b]
"""
import json, os, shutil, sys

AUTO = next((a.split('=', 1)[1] if '=' in a else 'recorrido' for a in sys.argv[1:] if a.startswith('--auto')), None)
# --jefes=a,b: las presentaciones solo de esos jefes.
JEFES = next((a.split('=', 1)[1].split(',') for a in sys.argv[1:] if a.startswith('--jefes=')), None)
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
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
    230, 'espada')

# La embestida: 3 s cargando (el carril en el suelo), 20 bloques a la carrera,
# el remate y el camino de llamas que se queda ardiendo.
ESCENAS['espada'] = (
    [novilis(), maniqui(20, 0, totem=True), maniqui(24, 5, totem=True), camara(4, 16, -34, 14, 2, 0)] +
    titulo('Espada del Fuego', 'Carga 3 s, embiste 20 bloques y deja un camino de llamas'),
    [(0, [orden('despertar')]),
     (75, [orden('espada')]), (95, [foto('planta')]), (125, [foto('carga')]), (133, [foto('carril')]),
     (137, [foto('sale')]), (141, [foto('corre')]), (151, [foto('remata')]), (165, [foto('camino')]),
     (175, [camara(26, 6, -14, 12, 2, 0)]), (185, [foto('camino_cerca')])],
    240, 'onda')

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
    titulo('Sol Abrasador', 'Tres soles y la Supernova, el cuarto: mas grande y mas lento'),
    [(0, [orden('despertar')])] + subir(2, 0) +
    [(150, [orden('sol')]), (158, [foto('forma')]), (163, [foto('lanza1')]), (175, [foto('lanza2')]),
     (187, [foto('lanza3')]), (200, [foto('nova_forma')]), (214, [foto('nova_alta')]), (222, [foto('nova_vuela')]),
     (262, [foto('nova_revienta')]), (275, [foto('charcos')]),
     (285, [camara(30, 8, -18, 18, 1, 0)]), (295, [foto('charcos_cerca')])],
    340, 'trompetas')

# Los angeles en lo alto de sus estrados de cinco escalones: uno con un maniqui
# arriba (el pulso lo tira), y Novilis plantado en medio sin atacar mientras
# suena la melodia.
ESCENAS['trompetas'] = (
    [novilis(), maniqui(26, 0), camara(-30, 16, -32, 0, 5, 0)] +
    titulo('Trompetas del Apocalipsis', 'Cada angel en su estrado: cada 5 s un pulso de fuego tira a quien este encima'),
    [(0, [orden('despertar')])] + subir(2, 0) +
    [(150, [orden('trompetas')]), (176, [foto('alza')]), (192, [foto('salen')]), (215, [foto('estatuas')]),
     # un maniqui en lo alto del estrado del segundo angel (a -10,6 / +10,6 del centro)
     (212, ['summon minecraft:mannequin ~-10.6 ~5.1 ~8.8 {Tags:["escena"],CustomName:"en el estrado",attributes:[{id:"minecraft:max_health",base:1000}],Health:1000f}']),
     (220, [camara(-26, 9, -8, -10.6, 5, 10.6)]), (230, [foto('estrado')]),
     (276, [foto('aviso')]), (296, [foto('pulso')]), (302, [foto('pulso_2')]), (312, [foto('pulso_3')]),
     (330, [camara(0, 34, -34, 0, 0, 0)]), (340, [foto('estatuas_arriba')]), (360, [foto('novilis_quieto')])] +
    [(380 + 3 * i, [orden('estatua')]) for i in range(15)] +
    [(430, [foto('estatua_rota')]),
     (640, [camara(-30, 16, -32, 0, 5, 0)]), (650, [foto('melodia_acaba')]), (680, [foto('furia')])],
    740, 'infernal')

# El salto: el sello marca donde cae; cae clavando la espada, tres grietas
# escupen lava y, al arrancarla, revienta en el centro y en sus puntas.
ESCENAS['infernal'] = (
    [novilis(), maniqui(18, 4, totem=True), maniqui(22, -3, totem=True), camara(-6, 20, -40, 14, 3, 0)] +
    titulo('Furia Infernal', 'Salta sobre uno y cae clavando la espada: la grieta escupe lava y revienta'),
    [(0, [orden('despertar')])] + subir(3, 0) +
    [(225, [orden('infernal')]), (232, [foto('agacha')]), (238, [foto('salta')]), (245, [foto('vuelo')]),
     (252, [foto('cae')]), (260, [foto('grietas')]), (268, [foto('lava')]), (273, [foto('revienta')]),
     (278, [foto('revienta_2')]),
     (320, [camara(30, 6, -16, 18, 2, 0), orden('infernal')]), (347, [foto('cae_cerca')]), (368, [foto('revienta_cerca')])],
    420, 'ofrenda')

ESCENAS['ofrenda'] = (
    [novilis(), maniqui(10, 0, totem=True), camara(16, 12, -28, 4, 9, 0)] +
    titulo('Ofrenda al Sol', 'Te agarra y te alza al sol: 15 letras en 8 s (20 en la fase IV)'),
    [(0, [orden('despertar')])] + subir(3, 0) +
    [(225, [orden('ofrenda')]), (235, [foto('marca')]), (253, [foto('agarra')]), (275, [foto('alzado')]),
     (285, [camara(12, 15, 6, 0, 14, 3)]), (300, [foto('alzado_cerca')]),
     (310, [camara(16, 12, -28, 4, 9, 0)]), (425, [foto('fallo')]), (450, [foto('furia')])],
    490, 'mar')

# El suelo en llamas: hunde la espada, la arena se raja (una boca bajo cada uno
# y otras sueltas), sale el fuego y se queda; cada 4,5 s, otra tanda.
ESCENAS['mar'] = (
    [novilis()] + [maniqui(x, z, totem=True) for x, z in ((14, 6), (-10, 10), (16, -12), (-14, -8), (22, 0))] +
    [camara(-24, 34, -56, 0, 0, 0)] +
    titulo('Mar de Llamas', 'Hunde la espada: el suelo se raja y salen bocas de fuego que no se apagan'),
    [(0, [orden('despertar')])] + subir(4, 0) +
    [(300, [orden('mar')]), (312, [foto('alza')]), (319, [foto('clava')]), (335, [foto('grietas')]), (352, [foto('fuego')]),
     (412, [foto('segunda')]), (440, [foto('mar')]), (500, [foto('tercera')]),
     (520, [camara(20, 6, -20, 6, 2, 0)]), (530, [foto('cerca')]), (600, [foto('apaga')])],
    640, 'dios')

ESCENAS['dios'] = (
    [novilis()] + [maniqui(x, z, totem=True) for x, z in ((12, 6), (-8, 8), (14, -10), (-12, -6))] +
    [camara(-20, 28, -48, 0, 6, 0)] +
    titulo('Dios de la Guerra', 'Fase IV: suelta la espada y llena las zonas carmesi de soles'),
    [(0, [orden('despertar')])] + subir(4, 0) +
    [(300, [orden('dios')]), (312, [foto('suelta')]), (322, [foto('marcas')]), (334, [foto('lanza1')]),
     (356, [foto('lanza2')]), (376, [foto('lanza3')]), (392, [foto('explosiones')]),
     (400, [camara(28, 10, -16, 0, 9, 0)]), (420, [foto('recoge')])],
    450, 'furia')

# La punteria: Novilis empieza de espaldas a su presa y tiene que encararla
# (el Barrido) y lanzarle los soles de frente.
ESCENAS['punteria'] = (
    [novilis(giro=90), maniqui(10, 0), maniqui(16, 10), maniqui(18, -10), camara(6, 20, -40, 6, 4, 0)] +
    titulo('Punteria', 'Empieza de espaldas: tiene que encarar a su presa antes de pegar'),
    [(0, [orden('despertar')]), (60, [orden('barrido')]), (64, [foto('barrido_gira')]), (70, [foto('barrido_tajo1')]),
     (82, [foto('barrido_tajo2')])] + [(130 + CAMBIO * i, [orden('fase')]) for i in range(1)] +
    [(220, ['tp @e[type=atalaya:novilis] ~ ~ ~ 90 0', orden('sol')]), (228, [foto('sol_gira')]), (232, [foto('sol_1')]),
     (244, [foto('sol_2')]), (256, [foto('sol_3')])],
    300, 'furia')

ESCENAS['furia'] = (
    [novilis(), camara(24, 10, -6, 0, 10, 0)] +
    titulo('Furia', 'Furia: aura azul, mas rapido e inmune 30 s'),
    [(0, [orden('despertar')]),
     (75, [orden('furia')]), (90, [foto('furia_prende')]), (125, [foto('furia')]),
     (135, [camara(-22, 12, 12, 0, 10, 0)]), (145, [foto('furia_espalda')]),
     (150, [camara(10, 15, -8, 0, 13, 0)]), (152, [foto('furia_cerca')]),
     (185, [orden('furia'), camara(24, 10, -6, 0, 10, 0), orden('dios')]), (210, [foto('dios')]), (235, [foto('dios_2')])],
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
     (250, [foto('tu_agarra')]), (262, [foto('tu_cuenta_3')]), (282, [foto('tu_cuenta_2')]), (302, [foto('tu_cuenta_1')]),
     (330, [foto('tu_teclas')]), (370, [foto('tu_teclas_2')]),
     (480, [foto('tu_fin')]), (496, [foto('tu_fin_2')])],
    540)
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

# Para probar el dano a mano: lo que lleva un jugador del servidor (netherita
# con Proteccion IV, 4 totems, manzanas de Notch) y los huevos de los cuatro.
escribir(os.path.join(FN, 'kit.mcfunction'), [
    'clear @s',
    'gamemode survival @s',
    'effect clear @s',
    *[f'item replace entity @s armor.{hueco} with minecraft:netherite_{pieza}{PROTE}'
      for hueco, pieza in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))],
    'item replace entity @s weapon.mainhand with minecraft:netherite_sword[minecraft:enchantments={"minecraft:sharpness":5}]',
    'item replace entity @s weapon.offhand with minecraft:totem_of_undying',
    'give @s minecraft:totem_of_undying 3',
    'give @s minecraft:enchanted_golden_apple 8',
    'give @s minecraft:golden_apple 16',
    'give @s minecraft:bow[minecraft:enchantments={"minecraft:power":5,"minecraft:infinity":1}]',
    'give @s minecraft:arrow 1',
    'give @s minecraft:torch 8',
    'give @s minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}] 4',
    *[f'give @s atalaya:huevo_{j}' for j in ('nerea', 'aeralis', 'rajang', 'novilis')],
    'effect give @s minecraft:instant_health 1 9 true',
    'effect give @s minecraft:saturation 1 9 true',
    'gamerule spawn_mobs false',
    'time set noon',
    'weather clear',
    'tellraw @s {"text":"[Atalaya] Kit de prueba: netherita Prot IV, 4 totems, manzanas de Notch y los huevos de los 4 jefes. /function escenas_novilis:kit para repetirlo.","color":"#FFC23A"}',
])

# Prueba del icono de la habilidad (y su tecla) con cada conjunto puesto: una foto de cada.
_hab = ['gamemode survival @a', 'clear @a', 'effect clear @a', 'time set noon', 'weather clear']
for k, tema in enumerate(('mareas', 'jade', 'vendaval', 'solar')):
    _hab += [f'schedule function {NS}:habilidad_{tema} {20 + 30 * k}t append']
    escribir(os.path.join(FN, f'habilidad_{tema}.mcfunction'), [
        *[f'item replace entity @a armor.{hueco} with atalaya:{tema}_{pieza}'
          for hueco, pieza in (('head', 'helmet'), ('chest', 'chestplate'), ('legs', 'leggings'), ('feet', 'boots'))],
        f'schedule function {NS}:habilidad_foto_{tema} 10t append'])
    escribir(os.path.join(FN, f'habilidad_foto_{tema}.mcfunction'), [f'tellraw @a "FOTO novilis_habilidad_{tema}"'])
escribir(os.path.join(FN, 'habilidad.mcfunction'), _hab)

# La presentacion de cada jefe al despertar, uno detras de otro, con fotos de la toma
# (en ticks desde que empieza a despertar). El jugador, a 26 bloques delante de el.
PRESENTA = [('nerea', 190, 145), ('aeralis', 190, 145), ('rajang', 190, 145), ('novilis', 190, 145)]
PRESENTA = [p for p in PRESENTA if JEFES is None or p[0] in JEFES]
_pre = [ANCLA + c for c in ('kill @e[type=atalaya:nerea]', 'kill @e[type=atalaya:aeralis]', 'kill @e[type=atalaya:rajang]',
                            'kill @e[type=atalaya:novilis]', 'kill @e[type=minecraft:mannequin,tag=escena]',
                            'time set noon', 'weather clear')] + ['gamemode spectator @a', 'gamerule spawn_mobs false']
desde = 20
for jefe, dura, ruge in PRESENTA:
    escribir(os.path.join(FN, f'presenta_{jefe}.mcfunction'), [
        ANCLA + f'kill @e[type=atalaya:{j}]' for j in ('nerea', 'aeralis', 'rajang', 'novilis')] + [
        ANCLA + f'summon atalaya:{jefe} ~ ~ ~ {{Rotation:[180f,0f]}}',
        ANCLA + 'tp @a ~ ~3 ~-28 facing ~ ~8 ~',
        f'schedule function {NS}:presenta_{jefe}_despierta 40t replace'])
    # Tras despertar sigue en escena 5 s (PresasJefe.ESCENA = 100 ticks) con el cartel; luego la
    # camara vuelve, y en la ultima foto, en supervivencia, se ven los corazones del combate.
    momentos = {'1_dormido': 20, '2_ojos': 55, '3_se_alza': 95, '4_poder': 135, '5_ruge': ruge + 6, '6_cartel': ruge + 18,
                '7_cartel2': ruge + 36, '8_escena': dura + 80, '9_vuelta': dura + 116, '10_jugador': dura + 140,
                '11_corazones': dura + 165}
    lineas = [ANCLA + f'atalaya {jefe} despertar']
    for nombre, t in momentos.items():
        foto = [f'tellraw @a "FOTO presenta_{jefe}_{nombre}"']
        if nombre == '11_corazones':
            # A supervivencia con algo de dano (para ver llenos, medios y vacios), la foto
            # cuando ya se pinta su HUD. Luego los corazones duran la batalla: lejos del
            # jefe (12_lejos) siguen; muerto mientras, al volver a su sitio (13_vuelve)
            # ya son los de siempre. Y de vuelta a espectador.
            pre = f'{NS}:presenta_{jefe}_{nombre}'
            escribir(os.path.join(FN, f'presenta_{jefe}_{nombre}_foto.mcfunction'),
                     foto + [f'schedule function {pre}_lejos 5t replace'])
            escribir(os.path.join(FN, f'presenta_{jefe}_{nombre}_lejos.mcfunction'),
                     [ANCLA + 'tp @a ~ ~3 ~-260', f'schedule function {pre}_lejos_foto 60t replace'])
            escribir(os.path.join(FN, f'presenta_{jefe}_{nombre}_lejos_foto.mcfunction'),
                     [f'tellraw @a "FOTO presenta_{jefe}_12_lejos"',
                      ANCLA + f'damage @e[type=atalaya:{jefe},limit=1,sort=nearest] 1000000 minecraft:out_of_world',
                      f'schedule function {pre}_vuelve 120t replace'])
            escribir(os.path.join(FN, f'presenta_{jefe}_{nombre}_vuelve.mcfunction'),
                     [ANCLA + 'tp @a ~ ~3 ~-28 facing ~ ~8 ~', f'schedule function {pre}_vuelve_foto 70t replace'])
            escribir(os.path.join(FN, f'presenta_{jefe}_{nombre}_vuelve_foto.mcfunction'),
                     [f'tellraw @a "FOTO presenta_{jefe}_13_vuelve"', f'schedule function {pre}_fin 10t replace'])
            escribir(os.path.join(FN, f'presenta_{jefe}_{nombre}_fin.mcfunction'), ['gamemode spectator @a', 'effect clear @a'])
            foto = ['gamemode survival @a', 'damage @p 5 minecraft:generic', 'effect give @a minecraft:resistance 20 4 true',
                    f'schedule function {NS}:presenta_{jefe}_{nombre}_foto 30t replace']
        escribir(os.path.join(FN, f'presenta_{jefe}_{nombre}.mcfunction'), foto)
        lineas.append(f'schedule function {NS}:presenta_{jefe}_{nombre} {t}t append')
    escribir(os.path.join(FN, f'presenta_{jefe}_despierta.mcfunction'), lineas)
    _pre.append(f'schedule function {NS}:presenta_{jefe} {desde}t append')
    desde += 40 + dura + 480
_pre.append(f'schedule function {NS}:presenta_fin {desde}t append')
escribir(os.path.join(FN, 'presenta_fin.mcfunction'), [ANCLA + f'kill @e[type=atalaya:{j}]' for j in ('nerea', 'aeralis', 'rajang', 'novilis')]
         + ['gamemode creative @a', 'gamerule spawn_mobs true'])
escribir(os.path.join(FN, 'presentaciones.mcfunction'), ['function ' + NS + ':ancla'] + _pre)

total = 80 + sum(dura + PAUSA for _, _, dura, _ in ESCENAS.values())
print('datapack en', DESTINO, '|', len(ESCENAS), 'escenas +', len(TU), 'contigo |', f'recorrido de {total / 20:.0f} s',
      f'| arranca solo: {AUTO}' if AUTO else '')
if len(ARGS) > 1:
    dp = os.path.join(ARGS[1], 'datapacks', 'atalaya_escenas_novilis')
    if os.path.isdir(dp):
        shutil.rmtree(dp)
    shutil.copytree(DESTINO, dp)
    print('copiado en', dp)
