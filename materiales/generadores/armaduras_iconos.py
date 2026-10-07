"""
Los iconos de las armaduras, las espadas y las armas de los jefes (octubre de
2026), pixel a pixel. Sustituyen a los de armaduras_jefes.py (la netherite
recoloreada): cada pieza tiene aqui su silueta y sus detalles, y las espadas
y las armas estan dibujadas nuevas y animadas.

  mareas    Nerea, el guardian del abismo: metal azul abisal, prismarina que
            brilla, nacar, coral y algas.
  jade      Rajang, el jaguar de jade del templo: metal verde casi negro, jade
            que brilla, oro de templo y marfil (colmillos y garras).
  vendaval  Aeralis, la reina polilla de la tormenta: metal anil, cielo y rayo,
            violeta de tormenta y pluma blanca.
  solar     Novilis, el caballero solar: acero quemado casi negro, lava, oro de
            sol, carmesi y obsidiana (sin espada: su arma es el mandoble).

Cada tema tiene ademas el arma de su papel:
  mareas_trident     el Tridente de las Mareas (el sanador)
  jade_hammer        el Martillo de Jade (el tanque)
  vendaval_bow       el Arco del Vendaval (el apoyo), con su flecha
  solar_greatsword   el Mandoble Solar (el dano)

Escribe, para cada tema, en textures/item/:
  <tema>_helmet|chestplate|leggings|boots.png   las piezas (16x16)
  <tema>_sword.png + .mcmeta                    la espada en el inventario
                                                (16x16, tira animada; no el solar)
  <tema>_sword_in_hand.png + .mcmeta            la espada en la mano (32x32,
                                                tira animada, mas detalle)
  <arma>.png + .mcmeta                          el arma en el inventario (16x16,
                                                tira de 12 cuadros)
  <arma>_in_hand.png + .mcmeta                  el arma en la mano (32x32, tira
                                                de 12 cuadros)
  vendaval_bow.png, vendaval_bow_pulling_0|1|2.png   el arco quieto y tensandose
                                                (16x16, fijos, sin version en la mano)
y textures/entity/projectiles/vendaval_arrow.png, la flecha del arco (32x32,
con el mismo reparto que la flecha del juego).

Como se dibuja (ver DISENO.md en la raiz):
  - Cada icono es un mapa de texto: cada caracter es un material y un tono de
    su rampa. '0'-'6' el metal (7 pasos); 'a'-'e', 'f'-'j', 'k'-'o' y 'p'-'t'
    los otros materiales del tema (5 pasos, de oscuro a claro). '.' es aire.
  - El contorno se calcula: todo pixel que toca el aire por uno de sus cuatro
    lados pasa al tono mas oscuro de su material (que lleva el tinte, nunca es
    negro). En mayuscula, el mismo tono sin contorno (para lo fino: un cuerno
    de coral de un pixel se pintaria entero de oscuro).
  - Luz de arriba a la izquierda, como los items de vanilla.

Rehechos en octubre de 2026 (segunda ronda, Juan: "los de tierra estan
chevere"): el vendaval entero (casco alado, pechera con alas en las
hombreras, faldones de pluma, botas con alas en el tobillo y una hoja ancha
con el filo dentado como un rayo) y un repaso a las mareas (venera con
costillas, coral, venera chica del pecho, conchas del cinturon y una hoja
curva con lomo de espuma y filo definido). El jade no se toca.

Tercera ronda (octubre de 2026): el cuarto tema (solar) y las armas de cada
papel. Lo de antes sale igual, pixel a pixel.

Uso: python armaduras_iconos.py <raiz> [hoja.png] [--temas=vendaval,mareas]
  --temas  escribe solo esos temas, con sus armas (la hoja de control sale
           con todos)
"""
import json, math, os, sys
from PIL import Image

_ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
SOLO = None
for _a in sys.argv[1:]:
    if _a.startswith('--temas='):
        SOLO = [t for t in _a.split('=', 1)[1].split(',') if t]
RAIZ = _ARGS[0]
HOJA = _ARGS[1] if len(_ARGS) > 1 else None
ITEM = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/item')


def hexc(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def rampa(*cs):
    return [hexc(c) for c in cs]


def mezclar(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


# ----------------------------------------------------------------------
#  Las paletas. Cada rampa va del contorno (oscuro, con el tinte) al nucleo
#  (claro, tirando al color). M es el metal (7 pasos); A B C D los demas;
#  H la hoja de la espada (6 pasos).
# ----------------------------------------------------------------------
TEMAS = {
    'mareas': {
        'M': rampa('0b161d', '13262f', '1c3843', '284c58', '386470', '527f8a', '7fa9b0'),
        'A': rampa('0e4e60', '1b8aa6', '3fe0ff', '9ff4ff', 'eaffff'),     # prismarina
        'B': rampa('5c3a54', 'a87a94', 'd6aac0', 'f0d4e2', 'fff4fa'),     # nacar
        'C': rampa('5e1029', '9e1a42', 'd8336a', 'f2618f', 'ffb3c8'),     # coral
        'D': rampa('123a2a', '1f5c40', '2f8058', '4aa872', '8ad89a'),     # alga (mas clara: el puno se leia negro)
        # hoja: agua honda (el cuerpo mas oscuro que antes, que se leia como
        # una mancha cian) y la espuma clara solo en el lomo
        'H': rampa('082a3a', '0d4f68', '177a96', '2fb8d8', '8ff0ff', 'e8ffff'),
    },
    'jade': {
        'M': rampa('0c140f', '142019', '1c2d22', '273c2e', '35503d', '4b6a53', '6f8f76'),
        'A': rampa('0c3a1e', '1d6b3a', '35a85a', '6fe08a', 'c8ffd0'),     # jade
        'B': rampa('5e4410', '9a7420', 'd4a83a', 'f8d97c', 'fff2c0'),     # oro
        'C': rampa('4a3a22', '8a7650', 'c8b488', 'ecdcb0', 'fff8e2'),     # marfil
        'D': rampa('0c3a1e', '1d6b3a', '35a85a', '6fe08a', 'c8ffd0'),
        'H': rampa('0a2e18', '145a30', '238a48', '3fbf68', '7fe89a', 'd0ffd8'),  # hoja: jade tallado
    },
    # El vendaval era gris lila y plano: ahora el metal es anil de verdad
    # (mas saturado, con la misma luminancia que el metal del jade), el
    # violeta de los ribetes sube para recortar como el oro del jade y la
    # pluma lleva el contorno anil, para que cada pluma se separe.
    'vendaval': {
        'M': rampa('0b0a20', '141636', '1d214c', '272d62', '343c7c', '46529a', '6c7cc4'),
        'A': rampa('0f3a6a', '1b6fbf', '35b2ff', '98e4ff', 'e6faff'),     # cielo y rayo
        'B': rampa('2a1460', '5b2fb4', '8e5cff', 'bf9cff', 'eee2ff'),     # violeta
        'C': rampa('2c3168', '6a74ac', 'a6b0da', 'd6def4', 'f6f9ff'),     # pluma
        'D': rampa('241c5c', '40389c', '6c6ad8', 'a4b4ff', 'e4ecff'),     # ala de polilla
        'H': rampa('10123a', '222c6c', '36479a', '5670c4', '93aee8', 'e0ecff'),  # hoja: acero de tormenta
    },
    # (Octubre de 2026) El cuarto: Novilis, el caballero solar. Las rampas
    # salen de las suyas (novilis_extras.py, fuego_modelo.py y el nucleo
    # solar): acero quemado casi negro, la lava de las grietas, el oro de sol,
    # el carmesi de la capa y la obsidiana de los cuernos. La hoja del mandoble
    # arde: de la brasa honda del alma al blanco caliente del filo.
    'solar': {
        'M': rampa('110b0d', '1c1518', '292023', '382c2e', '4a3b3b', '62504c', '836b64'),
        'A': rampa('6a1e06', 'b84a0c', 'ff8a1e', 'ffc070', 'fff0d0'),     # lava
        'B': rampa('5a3410', '8a5418', 'c07c22', 'e8a83a', 'ffd77a'),     # oro de sol
        'C': rampa('3c0a0e', '6e1418', 'a02420', 'd23c2c', 'ff7a5c'),     # carmesi
        'D': rampa('120a1c', '23163a', '352458', '4e3a7a', '6e58a4'),     # obsidiana
        'H': rampa('4a1206', '96300a', 'd85a10', 'ff9228', 'ffcc66', 'fff6dc'),  # hoja que arde
    },
}

# El caracter -> (material, tono)
LEYENDA = {}
for _i in range(7):
    LEYENDA[str(_i)] = ('M', _i)
for _m, _letras in (('A', 'abcde'), ('B', 'fghij'), ('C', 'klmno'), ('D', 'pqrst'), ('H', 'uvwxyz')):
    for _i, _ch in enumerate(_letras):
        LEYENDA[_ch] = (_m, _i)


def limpia(fila):
    """Las filas se escriben en dos mitades de 8 separadas por '|' (para contar)."""
    return fila.replace('|', '')


def leer(filas):
    """El mapa de texto -> {(x, y): (material, tono, libre)}; libre = sin contorno."""
    out = {}
    for y, fila in enumerate(filas):
        for x, ch in enumerate(limpia(fila)):
            if ch in '. ':
                continue
            libre = ch.isupper()
            m, t = LEYENDA[ch.lower()] if libre else LEYENDA[ch]
            out[(x, y)] = (m, t, libre)
    return out


def contorno(celdas, w, h):
    """Todo lo que toca el aire por uno de sus cuatro lados pasa al tono 0."""
    out = dict(celdas)
    for (x, y), (m, t, libre) in celdas.items():
        if libre:
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) not in celdas:
                out[(x, y)] = (m, 0, libre)
                break
    return out


def pintar(filas, tema, w=None, h=None, dx=0, dy=0):
    w = w or len(limpia(filas[0]))
    h = h or len(filas)
    T = TEMAS[tema]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for (x, y), (m, t, _) in contorno(leer(filas), w, h).items():
        if 0 <= x + dx < w and 0 <= y + dy < h:
            px[x + dx, y + dy] = T[m][t]
    return im


def comprobar(nombre, filas, ancho):
    """Que cada fila mida lo que debe y no lleve caracteres sin leyenda."""
    malas = []
    if len(filas) != ancho:
        malas.append(f'{nombre}: {len(filas)} filas, no {ancho}')
    for i, f in enumerate(filas):
        f = limpia(f)
        if len(f) != ancho:
            malas.append(f'{nombre}: la fila {i} mide {len(f)}: "{f}"')
        for ch in f:
            if ch not in '. ' and ch.lower() not in LEYENDA:
                malas.append(f'{nombre}: caracter raro "{ch}" en la fila {i}')
    return malas


# ----------------------------------------------------------------------
#  Las piezas (16x16). Cada fila en dos mitades de 8 (x 0-7 | x 8-15).
# ----------------------------------------------------------------------
PIEZAS = {}

# MAREAS -- 0-6 metal abisal; a-e prismarina; f-j nacar; k-o coral; p-t alga
# (segunda ronda) La venera del casco con sus costillas en abanico y la perla
# de prismarina en el gozne; astas de coral a los lados. La pechera, simetrica:
# aletas en los hombros, la venera chica con su perla en el pecho y una
# costura de prismarina. Las grebas con las dos conchas del cinturon y aletas
# en las rodillas. Menos damero en las escamas (metia ruido).
PIEZAS['mareas_helmet'] = [
    ".O...j.j|j.i...N.",
    ".Nmhgjgj|jgigglM.",
    "ONmjggjj|jiggilMN",
    "NMmgjgje|digiglLM",
    ".Mm45666|55433lL.",
    "..m45666|55443l..",
    "...45655|54432...",
    "...bcdde|dccbb...",
    "...45555|44332...",
    "...41bcd|dcb12...",
    "...43111|11122...",
    "...432..|..222...",
    "...32...|...22...",
    "........|........",
    "........|........",
    "........|........",
]
PIEZAS['mareas_chestplate'] = [
    "J.......|.......I",
    "BJ......|......IB",
    "BCJ..j..|..i..ICB",
    "jjjjji5.|.4iiiiih",
    "j655445j|i443332h",
    "j554434i|h433322h",
    "jhhhhhh5|4hhhhhhg",
    "...54j5j|i4i43...",
    "...45jgj|ifi33...",
    "...545je|di433...",
    "...4545h|g4343...",
    "...55454|44333...",
    "...4bcdc|cdcb3...",
    "...54544|43433...",
    "...jiiii|hhhhg...",
    "....4444|3332....",
]
PIEZAS['mareas_leggings'] = [
    "........|........",
    "........|........",
    "..jjjjie|diiiih..",
    "..55554d|c44333..",
    "..4jij55|44iig3..",
    "..5hjh54|43gig3..",
    "..55g54.|.43g33..",
    "..55544.|.44333..",
    ".b55454.|.43433b.",
    "bc4bccb.|.bccb3cb",
    ".bc5544.|.4433cb.",
    "..b5454.|.4343b..",
    "...5544.|.4433...",
    "...hihi.|.ihih...",
    "...4444.|.3333...",
    "........|........",
]
PIEZAS['mareas_boots'] = [
    "........|........",
    "........|........",
    "........|........",
    "B..jjih.|.hiig..B",
    "CB.5544.|.4433.BC",
    ".DB5454.|.3434BD.",
    "BCD5544.|.4433DCB",
    ".CB4bc4.|.3cb3BC.",
    "..D5544.|.4433D..",
    "...4545.|.3434...",
    "..55444.|.34433..",
    ".jjihh4.|.3hhijj.",
    ".jJjih3.|.3hijJj.",
    ".000000.|.000000.",
    "........|........",
    "........|........",
]

# JADE -- 0-6 metal verde; a-e jade; f-j oro; k-o marfil
PIEZAS['jade_helmet'] = [
    "........|........",
    "..00...E|C...00..",
    ".0h50..E|C..05h0.",
    ".0h550.D|C.044h0.",
    ".055655d|b444330.",
    ".0565256|5424430.",
    ".05cde56|54edc30.",
    ".054bd45|43db330.",
    ".0444551|1433320.",
    "..hiiiij|iiiihh..",
    "..04O111|111O30..",
    "..03N111|111N20..",
    "..030...|...020..",
    "........|........",
    "........|........",
    "........|........",
]
PIEZAS['jade_chestplate'] = [
    "......E.|.D......",
    ".....Ed.|.cB.....",
    "iiiiiiC.|.Biiiiii",
    "ijjjji5.|.3ijjjji",
    "igggji54|43ijgggi",
    "ijigji45|43ijgiji",
    "ijjjji54|43ijjjji",
    "iiiiii45|43iiiiii",
    "...4544i|h4443...",
    "...544ij|ih443...",
    "...44iie|dhh43...",
    "...54hid|chg33...",
    "...444hh|hg432...",
    "...4444h|g4332...",
    "....ihih|ihih....",
    ".....444|333.....",
]
PIEZAS['jade_leggings'] = [
    "........|........",
    "........|........",
    "...hhhhh|hhhhh...",
    "...hihid|eihih...",
    "..iiiii4|4iiiii..",
    "..ijjji5|4ijjji..",
    "..iggji.|.ijggi..",
    "..ijjji.|.ijjji..",
    "..iiiii.|.iiiii..",
    "...5454.|.4543...",
    "...5dc4.|.4cd3...",
    "...4cb5.|.5bc3...",
    "...5454.|.4543...",
    "...hihi.|.ihih...",
    "...4444.|.4444...",
    "........|........",
]
PIEZAS['jade_boots'] = [
    "........|........",
    "........|........",
    "........|........",
    "...4554.|.4554...",
    "...5243.|.4523...",
    "...4543.|.4243...",
    "..hiiih.|.hiiih..",
    "..ghdhg.|.ghdhg..",
    "...5523.|.4553...",
    "..55443.|.32455..",
    ".555443.|.344555.",
    "O524433.|.334425O",
    "N000000.|.000000N",
    ".O......|......O.",
    "........|........",
    "........|........",
]

# VENDAVAL -- 0-6 metal anil; a-e cielo; f-j violeta; k-o pluma
# (rehecho) Las alas son el motivo del juego: plumas en diagonal, cada una con
# su tono claro, el medio y una raya de contorno (K) que la separa de la
# siguiente; en mayuscula para que el contorno calculado no se las coma. El
# ala de la derecha va un tono por debajo (la luz viene de la izquierda).
#   casco     alas que suben de las sienes, antenas de polilla con la punta
#             de rayo, ojo de la tormenta en la frente, ojos de cian
#   pechera   hombreras con ribete violeta y un ala en cada una (la V que la
#             hace imponente), gola violeta, el ojo de la tormenta y un rayo
#   grebas    cinturon violeta con la hebilla de cian, plumas en las caderas,
#             rayo en zigzag por cada pierna y rodilleras violeta
#   botas     alas en el tobillo, la costura de cian, el pie hacia fuera
PIEZAS['vendaval_helmet'] = [
    "K.......|.......K",
    "OK...D..|..D...KN",
    "NOK...G.|.G...KNM",
    "LNOK.666|554.KNML",
    "KLNOK655|554KNMLK",
    "OKLNO555|d54NMLKN",
    "NOKLN55d|ed4MLKNM",
    ".NOKLiii|hhhLKNM.",
    "..KKjiii|hhhgKK..",
    "...45555|44433...",
    "...5D111|111C2...",
    "...54011|11032...",
    "...43...|...22...",
    "...32...|...21...",
    "........|........",
    "........|........",
]
PIEZAS['vendaval_chestplate'] = [
    "K.......|.......K",
    "OK......|......KN",
    "NOK..j..|..h..KNM",
    "LNOK.ji.|.ih.KNML",
    "jjjjjj6.|.4iiiiih",
    "j666655j|i444433h",
    "jiiiiii5|4hhhhhhg",
    "k65555ih|hg44433k",
    "...554id|ch433...",
    "...545ie|dh433...",
    "...5444h|g4433...",
    "...5444c|c4332...",
    "...4544b|44332...",
    "...44544|43322...",
    "...jiiii|hhhhg...",
    "....4444|3332....",
]
PIEZAS['vendaval_leggings'] = [
    "........|........",
    "........|........",
    "..jjiiid|chhhhg..",
    "..jiiiie|dhhhhg..",
    ".K555544|4444333K",
    "KOK55554|4444KNMK",
    "KNOK555.|.443KNMK",
    "KLNOK54.|.43KMNLK",
    ".KLNO54.|.43MLKK.",
    "..KK5c4.|.4c3KK..",
    "...54c4.|.4c43...",
    "...jiii.|.hhhg...",
    "...5c54.|.45c3...",
    "...45c4.|.4c43...",
    "...4c54.|.45c3...",
    "...jiih.|.hhhg...",
]
PIEZAS['vendaval_boots'] = [
    "........|........",
    "K.......|.......K",
    "OK.jiih.|.hhhg.KN",
    "NOKjiih.|.hhhgKNM",
    "LNOK543.|.344KNML",
    "KLNO543.|.34NMLK.",
    ".KKK5c3.|.3c4KK..",
    "...5543.|.3455...",
    "...5443.|.3445...",
    "..55443.|.34455..",
    ".555443.|.344555.",
    "jiiiiih.|.hhhhhhg",
    "0000000.|.0000000",
    "........|........",
    "........|........",
    "........|........",
]

# SOLAR -- 0-6 acero quemado; a-e lava; f-j oro; k-o carmesi; p-t obsidiana
#   casco     el yelmo cerrado con la T que arde, la frente de oro, los cuernos
#             de obsidiana con la punta de oro y la llama de la cresta
#   pechera   hombreras de oro con su llama, el nucleo solar en el pecho (el
#             disco de oro y el alma de lava) y una grieta; la capa asoma
#   grebas    el cinturon con la hebilla de sol, los faldones de oro como
#             rayos y las rodilleras con su gema de lava
#   botas     ribetes y puntera de oro, una grieta y la llama del talon
PIEZAS['solar_helmet'] = [
    "........|D.......",
    "..J....C|d....J..",
    ".S.....c|eC....S.",
    ".R....bd|ec....R.",
    ".rq.fhii|iihf.qr.",
    "..q45566|65543q..",
    "...45566|65543...",
    "...4dddd|eedd3...",
    "...4555e|d5443...",
    "...hi55e|d44ih...",
    "...4555d|c4443...",
    "...45555|44443...",
    "...hiiii|iiihh...",
    "........|........",
    "........|........",
    "........|........",
]
PIEZAS['solar_chestplate'] = [
    ".D......|......C.",
    ".dC.....|.....Cc.",
    "jcdjjj5.|.4iiicbi",
    "j6555j54|43i4443i",
    "j55b5j45|43i4b33i",
    "jjjjjj54|43iiiiih",
    "...5545i|i4443...",
    "...545ii|ih443...",
    "...55iid|eih43...",
    "...54iie|dih43...",
    "...545ii|ih443...",
    "...5b45i|h4433...",
    "...ihihi|hihih...",
    "...54545|44433...",
    "...ihihi|hihih...",
    "....4444|3333....",
]
PIEZAS['solar_leggings'] = [
    "........|........",
    "........|........",
    "..jjjjjd|ejjjjh..",
    "..iiiiic|dhhhhg..",
    "..5554ji|ih4433..",
    "..555jij|hih433..",
    "..5545ji|ih.433..",
    "..5554.j|i.4433..",
    "..5545..|..4433..",
    "..jiiij.|.ihhig..",
    "..icdci.|.hcdcg..",
    "..jiiij.|.ihhig..",
    "...5b54.|.4543...",
    "...54b4.|.4b43...",
    "...hihi.|.ihih...",
    "........|........",
]
PIEZAS['solar_boots'] = [
    "........|........",
    "........|........",
    ".C......|......B.",
    ".DCjiih.|.hiigBC.",
    "BED5554.|.4543CDA",
    ".CD5b54.|.45b3CB.",
    "..B5544.|.4433A..",
    "...5554.|.4443...",
    "...jiih.|.hiig...",
    "...5554.|.4543...",
    "..55444.|.34433..",
    ".jiiih4.|.3hiiih.",
    ".jJiih4.|.3hiiJh.",
    ".000000.|.000000.",
    "........|........",
    "........|........",
]


# ----------------------------------------------------------------------
#  Las espadas. En la mano (32x32) la hoja se calcula: una curva de Bezier
#  del arranque a la punta y su semianchura a cada lado, escritas como datos;
#  la guarda, el puno y el pomo van en mapas de texto. En el inventario
#  (16x16) la espada entera va a mano. La animacion se pinta encima de cada
#  cuadro, solo por dentro del contorno (y alguna chispa suelta fuera).
# ----------------------------------------------------------------------
CUADROS = 12


def bezier(puntos, n=240):
    out = []
    for i in range(n + 1):
        t = i / n
        pts = list(puntos)
        while len(pts) > 1:
            pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(pts, pts[1:])]
        out.append(pts[0])
    return out


def perfil(tabla, u):
    """Interpolacion lineal en una tabla [(u, valor), ...]."""
    if u <= tabla[0][0]:
        return tabla[0][1]
    for (u0, v0), (u1, v1) in zip(tabla, tabla[1:]):
        if u <= u1:
            return v0 + (v1 - v0) * (u - u0) / max(1e-9, u1 - u0)
    return tabla[-1][1]


def proyectar(curva, pixeles):
    """{(x, y): (u, d, fuera)} de cada pixel sobre la curva: u de 0 (arranque)
    a 1 (punta) a lo largo de ella; d la distancia con signo (+ hacia el lomo,
    arriba a la izquierda); fuera, si cae por detras del arranque o mas alla
    de la punta."""
    import numpy as np
    P = np.array(curva, dtype=float)
    A, V = P[:-1], P[1:] - P[:-1]
    L2 = (V ** 2).sum(1)
    Ls = np.sqrt(L2)
    acum = np.concatenate([[0.0], np.cumsum(Ls)])
    total = acum[-1]
    out = {}
    for (x, y) in pixeles:
        p = np.array([x + 0.5, y + 0.5])
        t = ((p - A) * V).sum(1) / L2
        antes, despues = bool(t[0] < -0.05), bool(t[-1] > 1.05)
        t = np.clip(t, 0.0, 1.0)
        Q = A + t[:, None] * V
        dist = np.sqrt(((p - Q) ** 2).sum(1))
        i = int(np.argmin(dist))
        nx, ny = V[i, 1] / Ls[i], -V[i, 0] / Ls[i]
        d = (p[0] - Q[i, 0]) * nx + (p[1] - Q[i, 1]) * ny
        fuera = (antes and i == 0) or (despues and i == len(Ls) - 1)
        out[(x, y)] = (float((acum[i] + t[i] * Ls[i]) / total), float(d), fuera)
    return out


def hoja(curva, lomo, filo, w=32):
    """{(x, y): (u, s, d)} de los pixeles de la hoja: los que caen dentro de
    la semianchura de su lado (lomo(u) o filo(u)). s es d partido por esa
    semianchura: de -1 en el filo a +1 en el lomo."""
    out = {}
    todos = [(x, y) for y in range(w) for x in range(w)]
    for p, (u, d, fuera) in proyectar(curva, todos).items():
        if fuera:
            continue
        semi = perfil(lomo, u) if d >= 0 else perfil(filo, u)
        if abs(d) <= semi:
            out[p] = (u, d / max(0.01, semi), d)
    return out


def que_toca_aire(celdas):
    """Los pixeles que tocan el aire por alguno de sus cuatro lados."""
    return {p for p in celdas if any((p[0] + dx, p[1] + dy) not in celdas
                                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}


def a_imagen(celdas, tema, w, h):
    T = TEMAS[tema]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for (x, y), (m, t, _) in celdas.items():
        if 0 <= x < w and 0 <= y < h:
            px[x, y] = T[m][max(0, min(len(T[m]) - 1, t))]
    return im


def tira(cuadros):
    """Los cuadros de una animacion, uno debajo de otro (lo que lee el .mcmeta)."""
    w, h = cuadros[0].size
    out = Image.new('RGBA', (w, h * len(cuadros)), (0, 0, 0, 0))
    for k, c in enumerate(cuadros):
        out.paste(c, (0, h * k))
    return out


def seg(p, a, b):
    """(t, d, largo) de un punto respecto del segmento a-b: t de 0 a 1 a lo
    largo; d con signo (+ a la izquierda yendo de a a b: en algo que sube a la
    derecha, arriba a la izquierda)."""
    vx, vy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(vx, vy)
    t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / (L * L)
    d = ((p[0] - a[0]) * vy - (p[1] - a[1]) * vx) / L
    return t, d, L


def contornear(celdas):
    """El contorno calculado (lo que toca el aire, salvo lo libre, al tono 0).
    Devuelve los pixeles de contorno, que la animacion no toca."""
    borde = {p for p in que_toca_aire(celdas) if not celdas[p][2]}
    for p in borde:
        m, t, l = celdas[p]
        celdas[p] = (m, 0, l)
    return borde


def barra(celdas, a, b, ancho, tono, w=32, encima=False):
    """Lo que queda a menos de 'ancho' del segmento a-b (un puno, una barra de
    guarda). tono(t, d, largo) -> (material, tono)."""
    for y in range(w):
        for x in range(w):
            if (x, y) in celdas and not encima:
                continue
            t, d, L = seg((x + 0.5, y + 0.5), a, b)
            if -0.04 <= t <= 1.04 and abs(d) <= ancho:
                celdas[(x, y)] = tono(t, d, L) + (False,)


def bola(celdas, c, r, tono, w=32):
    """Un disco de radio r; tono(dx, dy, r) -> (material, tono)."""
    for y in range(w):
        for x in range(w):
            dx, dy = x + 0.5 - c[0], y + 0.5 - c[1]
            if math.hypot(dx, dy) <= r:
                celdas[(x, y)] = tono(dx, dy, math.hypot(dx, dy)) + (False,)


def calcar(celdas, filas, ox, oy):
    """Un mapa de texto encima, desde (ox, oy)."""
    for (x, y), v in leer(filas).items():
        celdas[(x + ox, y + oy)] = v


def destello(celdas, p, e, interior, m='H', alto=5, brazos=1, libres=False):
    """Un brillo que dura tres cuadros: punto, estrella, punto apagado."""
    if p is None:
        return
    x, y = p
    if e == 0:
        celdas[p] = (m, alto, celdas.get(p, (m, 0, False))[2])
    elif e == 1:
        celdas[p] = (m, alto, celdas.get(p, (m, 0, False))[2])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for i in range(1, brazos + 1):
                q = (x + dx * i, y + dy * i)
                if q in interior:
                    celdas[q] = (m, max(celdas[q][1], alto - i), False)
                elif libres and i == brazos and q not in celdas:
                    celdas[q] = (m, alto - 1, True)
    elif e == 2:
        celdas[p] = (m, alto - 1, celdas.get(p, (m, 0, False))[2])


def cerca(info, u_obj, s_min, s_max, interior):
    """El pixel de la hoja mas cerca de u_obj con s entre s_min y s_max."""
    c = [p for p, v in info.items() if s_min <= v[1] <= s_max and p in interior]
    return min(c, key=lambda p: abs(info[p][0] - u_obj)) if c else None


_CACHE = {}


def hoja_de(clave, curva, lomo, filo, w=32):
    if clave not in _CACHE:
        _CACHE[clave] = hoja(curva, lomo, filo, w)
    return _CACHE[clave]


# ---------------------------- Las Mareas -------------------------------
#  Una hoja curva como una ola que rompe: espuma en el lomo (arriba), agua
#  honda hacia el filo; crestas y senos que corren hacia la punta y destellos
#  de espuma. Guarda de venera de nacar (cinco costillas en lineas limpias de
#  pixel, a 0, 45 y 90 grados), puno envuelto en alga y una perla por pomo.
MAREAS_CURVA = bezier([(10, 22), (13, 12), (21, 3), (30.5, 1.5)])
MAREAS_LOMO = [(0, 2.2), (0.25, 3.2), (0.55, 3.8), (0.8, 3.0), (0.93, 2.0), (1.0, 0.4)]
MAREAS_FILO = [(0, 2.2), (0.3, 2.4), (0.6, 2.2), (0.85, 1.6), (0.95, 1.0), (1.0, 0.3)]
# Los destellos de espuma: (cuadro en que nace, por donde va de la hoja)
MAREAS_ESPUMA = [(0, 0.30), (4, 0.78), (8, 0.52)]


def agua(u, s, fase, olas=4.0):
    """El tono del agua: por bandas de lomo a filo, con la ola que corre.
    (Segunda ronda) La espuma clara se queda en el lomo y el cuerpo baja a
    agua honda: antes casi toda la hoja era cian claro y se leia como una
    mancha."""
    t = 5 if s > 0.8 else 4 if s > 0.58 else 3 if s > 0.2 else 2 if s > -0.35 else 1
    w = (u * olas - fase - 0.3 * s) % 1.0
    if t in (2, 3) and 0.5 <= w < 0.64:
        t -= 1                      # el seno de la ola
    elif w < 0.12:
        t = min(5, t + 1)           # la cresta
    return t


def filo_vivo(celdas, info, m='A', t=3, desde=0.0):
    """El filo (el lado de abajo de la hoja) que toca el aire se pinta claro y
    sin contorno: asi la hoja tiene un filo que se ve, no solo un borde.
    Devuelve sus pixeles."""
    filo = [p for p in que_toca_aire(celdas)
            if p in info and info[p][2] < 0 and celdas[p][0] == 'H' and info[p][0] > desde]
    for p in filo:
        celdas[p] = (m, t, True)
    return filo


def venera(celdas, H, R=6.0, bulto=0.35):
    """La venera de la guarda, abierta hacia la hoja desde el gozne H."""
    rayos = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]
    for y in range(32):
        for x in range(32):
            dx, dy = x - H[0], y - H[1]
            if dx - dy < 0:
                continue                         # del lado del puno no hay concha
            r = math.hypot(dx, dy)
            k = (math.atan2(-dy, dx) + math.pi / 4) / (math.pi / 4)
            if k < -0.05 or k > 4.05:
                continue
            frac = abs(k - round(k))             # 0 sobre una costilla, 0.5 en un surco
            if r > R + bulto * (1 - 2 * frac) + 0.3:
                continue
            costilla = any((dx, dy) == (a * i, b * i) for a, b in rayos for i in range(1, 9))
            t = 2 if r < 1.2 else 4 if costilla else 1 if frac > 0.3 else 3
            celdas[(x, y)] = ('B', t, False)
    celdas[H] = ('B', 2, False)


def mareas_mano(k):
    fase = k / CUADROS
    info = hoja_de('mareas', MAREAS_CURVA, MAREAS_LOMO, MAREAS_FILO)
    celdas = {p: ('H', agua(u, s, fase), False) for p, (u, s, d) in info.items()}
    venera(celdas, (8, 24), R=5.4)
    filo_vivo(celdas, info, desde=0.08)
    barra(celdas, (7.4, 25.6), (3.4, 29.0), 1.75,
          lambda t, d, L: ('D', 3 if (t * L / 1.5 + d * 0.6) % 2.0 < 0.9 else 2 if d > 0 else 1))
    bola(celdas, (2.6, 29.4), 2.35,
         lambda dx, dy, r: ('B', 4 if math.hypot(dx + 0.7, dy + 0.7) < 1.0 else 3 if math.hypot(dx + 0.7, dy + 0.7) < 1.9 else 2))
    borde = contornear(celdas)
    interior = {p for p in info if p not in borde and celdas[p][0] == 'H'}
    for nace, u in MAREAS_ESPUMA:
        e = (k - nace) % CUADROS
        if e < 3:
            destello(celdas, cerca(info, u, 0.45, 1.0, interior), e, interior)
    return a_imagen(celdas, 'mareas', 32, 32)


# ------------------------------ El Jade --------------------------------
#  Un montante de jade tallado: ancho, con la arista en medio (la cara de
#  arriba con luz, la de abajo en sombra), tres cortes de faceta y vetas que
#  laten con un pulso que sube hacia la punta. Un destello salta de faceta en
#  faceta. Guarda de oro con las dos puntas en espiral cuadrada y una gema;
#  puno de metal con anillas de oro; una cabeza de jaguar por pomo.
JADE_CURVA = bezier([(10, 22), (30.6, 1.4)])
JADE_ANCHO = [(0, 3.4), (0.72, 3.8), (1.0, 0.4)]
JADE_CORTES = (0.30, 0.55, 0.78)
JADE_FACETAS = [(0.30, 0.3), (0.55, -0.35), (0.78, 0.3), (0.93, 0.0)]   # por donde salta el destello
ESPIRAL = ["ffffff",
           "fjjjjf",
           "fgggjf",
           "fjigjf",
           "fjjjjf",
           "ffffff"]
JAGUAR = [".f...f.",
          "fhf.fhf",
          "fiiiiif",
          "fiDiDif",
          ".fhghf.",
          "..fNf..",
          ]


def vena(u, s):
    """Las vetas del jade: dos lineas que serpentean por las dos caras."""
    return (abs(s - 0.42 * math.sin(u * 10.0 + 0.7)) < 0.13 or
            (0.12 < u < 0.72 and abs(s + 0.55 - 0.22 * math.sin(u * 15.0)) < 0.11))


def jade_tono(u, s):
    t = 4 if s > 0.62 else 3 if s > 0.0 else 2 if s > -0.62 else 1
    if abs(s) < 0.14 and u < 0.97:
        t = 4                                    # la arista
    for c in JADE_CORTES:
        if abs(u - c - 0.06 * abs(s)) < 0.016:
            t = max(1, t - 2)                    # el corte entre dos facetas
    return t


def jade_mano(k):
    fase = k / CUADROS
    info = hoja_de('jade', JADE_CURVA, JADE_ANCHO, JADE_ANCHO)
    celdas = {p: ('H', jade_tono(u, s), False) for p, (u, s, d) in info.items()}
    # La guarda: una barra de oro de punta a punta y las dos espirales.
    calcar(celdas, ESPIRAL, 3, 14)
    calcar(celdas, [f[::-1] for f in ESPIRAL[::-1]], 13, 24)
    barra(celdas, (7.6, 18.6), (13.4, 24.4), 1.9,
          lambda t, d, L: ('B', 4 if d > 0.7 else 3 if d > -0.5 else 2), encima=True)
    calcar(celdas, ["ed", "dc"], 10, 21)
    # El puno y el pomo.
    barra(celdas, (8.8, 24.2), (5.0, 28.0), 1.5,
          lambda t, d, L: ('B', 3) if (t * L) % 2.4 < 0.9 else ('M', 4 if d > 0.3 else 3 if d > -0.6 else 2))
    calcar(celdas, JAGUAR, 0, 26)
    borde = contornear(celdas)
    interior = {p for p in info if p not in borde and celdas[p][0] == 'H'}
    # Las vetas: un poco mas claras siempre; el pulso las enciende al pasar.
    for p in interior:
        u, s, d = info[p]
        if not vena(u, s):
            continue
        brillo = 1
        for j in (0.0, 0.5):
            du = (u - (fase + j)) % 1.0
            if du < 0.10 or du > 0.97:
                brillo = 2
        m, t, l = celdas[p]
        celdas[p] = ('H', min(5, max(t, 3) + brillo), l)
    # El destello que salta de faceta en faceta (tres cuadros en cada una).
    u, s = JADE_FACETAS[(k // 3) % len(JADE_FACETAS)]
    p = min(interior, key=lambda q: (info[q][0] - u) ** 2 * 900 + (info[q][1] - s) ** 2 * 9)
    destello(celdas, p, k % 3, interior, brazos=2, libres=True)
    return a_imagen(celdas, 'jade', 32, 32)


# ---------------------------- El Vendaval ------------------------------
#  (Rehecho) Una hoja ancha de acero de tormenta: el lomo con su brillo, el
#  cuerpo que se oscurece hacia el filo y el filo dentado como un rayo (cada
#  diente apunta a la punta), encendido de cian. Por dentro sube un rayo en
#  zigzag que deja estela; al llegar arriba descarga: el zigzag y el filo se
#  encienden un momento y saltan chispas de los dientes. Guarda de dos alas
#  de pluma blanca (plumas separadas, el borde de atras festoneado y su ojo
#  de polilla), puno violeta y el ojo de la tormenta por pomo.
VENDAVAL_CURVA = bezier([(11, 21), (31.3, 0.7)])
VENDAVAL_LOMO = [(0, 2.2), (0.8, 2.3), (0.93, 1.4), (1.0, 0.4)]
VENDAVAL_FILO = [(0, 2.2), (0.18, 2.0), (0.28, 4.0), (0.285, 2.0), (0.40, 2.0), (0.50, 3.8),
                 (0.505, 1.9), (0.62, 1.9), (0.72, 3.4), (0.725, 1.8), (0.86, 1.8), (0.95, 1.1),
                 (1.0, 0.3)]
VENDAVAL_DIENTES = (0.28, 0.50, 0.72)
VENDAVAL_DESCARGA = 8      # el cuadro en que el rayo llega a la punta y descarga


def zigzag(u, dientes=9.0, amplitud=0.62):
    """Por donde va el rayo a lo ancho de la hoja (s), a cada altura u."""
    f = (u * dientes) % 1.0
    return amplitud * (4 * abs(f - 0.5) - 1)


def tormenta(u, s):
    """El acero de la hoja: claro en el lomo, hondo hacia el filo."""
    return 5 if s > 0.8 else 4 if s > 0.45 else 3 if s > 0.0 else 2 if s > -0.5 else 1


def rayo(celdas, canal, info, k, filo, m='A'):
    """El rayo del zigzag en el cuadro k: sube con estela hasta la descarga;
    en la descarga el canal entero y el filo se encienden y luego se apagan.
    Devuelve por donde va la cabeza (None si ya descargo)."""
    D = VENDAVAL_DESCARGA
    if k < D:
        cabeza = -0.05 + 1.15 * (k + 1) / D
        for p in canal:
            atras = cabeza - info[p][0]
            if 0 <= atras < 0.45:
                t = 4 if atras < 0.1 else 3 if atras < 0.25 else 2
                celdas[p] = (m, t, celdas[p][2])
        return cabeza
    e = k - D
    for p in canal:
        if e < 3:
            celdas[p] = (m, 3 - e, celdas[p][2])
    for p in filo:
        if e < 2:
            celdas[p] = (m, 4, True)
    return None


def ala(celdas, raiz, direccion, largo=9.6, vuelo=3.4, sombra=0):
    """Un ala de pluma desde la guarda: su eje sale en 'direccion' y se curva
    hacia la punta de la espada ('vuelo'). El borde que mira a la punta es
    liso; el de atras, festoneado (una punta por pluma). Cinco plumas
    separadas por una raya, y el ojo de polilla en medio."""
    dx, dy = direccion
    n = math.hypot(dx, dy)
    dx, dy = dx / n, dy / n
    fx, fy = 1 / math.sqrt(2), -1 / math.sqrt(2)          # hacia la punta
    eje = [(raiz[0] + dx * largo * t + fx * vuelo * t * t,
            raiz[1] + dy * largo * t + fy * vuelo * t * t) for t in [i / 40 for i in range(41)]]
    liso = [(0, 1.3), (0.35, 2.7), (0.75, 2.3), (1.0, 0.5)]
    festoneado = [(0, 1.3), (0.2, 2.3), (0.21, 1.5), (0.4, 2.5), (0.41, 1.7), (0.6, 2.4),
                  (0.61, 1.6), (0.8, 2.0), (0.81, 1.2), (1.0, 0.4)]
    # Que lado mira a la punta: el de la normal (d > 0) o el contrario.
    hacia_punta = (dy * fx - dx * fy) > 0
    lomo, filo = (liso, festoneado) if hacia_punta else (festoneado, liso)
    for p, (u, s, d) in hoja(eje, lomo, filo).items():
        if p in celdas and celdas[p][0] != 'H':
            continue
        sp = s if hacia_punta else -s                    # +1 en el borde de la punta
        t = 4 if sp > 0.45 else 3 if sp > -0.25 else 2
        if (u * 5.0 - 0.45 * sp) % 1.0 < 0.17 and 0.15 < u < 0.95:
            t = 1                                        # la raya entre dos plumas
        if abs(u - 0.5) < 0.1 and abs(s) < 0.38:
            celdas[p] = ('A', 3, False) if abs(u - 0.5) < 0.045 else ('B', 2, False)
            continue
        celdas[p] = ('C', max(1, t - sombra), False)


def vendaval_mano(k):
    info = hoja_de('vendaval', VENDAVAL_CURVA, VENDAVAL_LOMO, VENDAVAL_FILO)
    celdas = {p: ('H', tormenta(u, s), False) for p, (u, s, d) in info.items()}
    raiz = (10.6, 21.4)
    ala(celdas, raiz, (-1, -1))
    ala(celdas, raiz, (1, 1), sombra=1)
    calcar(celdas, ["hi", "gh"], 10, 21)
    barra(celdas, (9.2, 22.8), (5.0, 27.0), 1.45,
          lambda t, d, L: ('B', 3 if (t * L + d * 0.7) % 2.0 < 0.9 else 2 if d > 0 else 1))
    bola(celdas, (3.3, 28.7), 2.45,
         lambda dx, dy, r: ('A', 4) if r < 0.9 else ('A', 2) if r < 1.5 else ('B', 3 if dx + dy < 0 else 2))
    filo = filo_vivo(celdas, info, desde=0.06)
    borde = contornear(celdas)
    interior = {p for p in info if p not in borde and celdas[p][0] == 'H'}
    canal = {p for p in interior if abs(info[p][1] - zigzag(info[p][0], 7.0, 0.5)) < 0.3}
    cabeza = rayo(celdas, canal, info, k, filo)
    # Chispas: junto a la cabeza mientras sube; de los dientes al descargar.
    if cabeza is not None and 0.08 < cabeza < 1.0 and k % 2 == 0:
        c = min(filo, key=lambda q: (info[q][0] - cabeza) ** 2)
        q = (c[0] + 2, c[1] + 2)
        if q not in celdas and 0 <= q[0] < 32 and 0 <= q[1] < 32:
            celdas[q] = ('A', 3, True)
    elif k == VENDAVAL_DESCARGA:
        for u in VENDAVAL_DIENTES:
            c = min(filo, key=lambda q: (info[q][0] - u) ** 2)
            for i in (2, 3):
                q = (c[0] + i, c[1] + i - 1)
                if q not in celdas and 0 <= q[0] < 32 and 0 <= q[1] < 32:
                    celdas[q] = ('A', 4 if i == 2 else 3, True)
    return a_imagen(celdas, 'vendaval', 32, 32)


MANO = {'mareas': mareas_mano, 'jade': jade_mano, 'vendaval': vendaval_mano}


# ----------------------------------------------------------------------
#  Las espadas del inventario (16x16), a mano. La misma idea que en la mano
#  con menos pixeles; la animacion sale de proyectar la hoja sobre la curva
#  de la espada a media escala (u a lo largo, s a lo ancho).
#  Leyenda: u-z la hoja (de contorno a nucleo); en mayuscula, sin contorno.
# ----------------------------------------------------------------------
ICONOS_ESPADA = {
    # (Segunda ronda; antes era una mancha azul.) Una hoja curva y estrecha
    # como una ola que rompe: contorno hondo por el lomo con la espuma justo
    # debajo, el cuerpo de agua honda y el filo claro (D, sin contorno). La
    # guarda, una media luna de nacar con las puntas vueltas hacia la hoja y
    # la perla en medio; el puno de alga y una perla por pomo.
    'mareas': [
        "........|....uuu.",
        "........|..uuzzyu",
        "........|.uzyvwwD",
        "........|uzyvwD..",
        ".......u|zyvwD...",
        ".......u|zyvD....",
        "......uz|yvD.....",
        "......uz|wD......",
        "...h..uz|vD..g...",
        "...hJIIJ|JHHHg...",
        ".....qS.|........",
        "....qT..|........",
        "...qS...|........",
        ".IJ.....|........",
        ".HG.....|........",
        "........|........",
    ],
    # El jade tallado (arista clara en medio), la guarda de oro con las
    # puntas vueltas, el puno oscuro y la cabeza de jaguar.
    'jade': [
        "........|......uu",
        "........|....uuzu",
        "........|...uyzxu",
        "........|..uyzxwu",
        "........|.uyzxwvu",
        "........|uyzxwvu.",
        ".......u|yzxwvu..",
        "..fff.uy|zxwvu...",
        "..fjf.yz|xwvu....",
        "..ffiiyz|wvu.....",
        "....ijji|vu......",
        ".....iij|i.......",
        "....2.ji|iff.....",
        ".f.f2...|fjf.....",
        ".fhf....|fff.....",
        ".fDf....|........",
    ],
    # (Rehecha; antes era fina y generica.) Hoja ancha de acero de tormenta:
    # contorno y brillo por el lomo, el cuerpo que se oscurece y el filo de
    # cian (D, sin contorno) con dos dientes de rayo; la hoja manda en la
    # diagonal. La guarda, corta y perpendicular a la hoja (dos pixeles por
    # lado: con alas largas en cruz se leia como dos espadas cruzadas), violeta
    # claro sin contorno (en contorno salia negra), con la gema de cian y una
    # punta de pluma en cada extremo; el puno violeta a dos tonos y el ojo de
    # la tormenta por pomo.
    'vendaval': [
        "........|......uE",
        "........|.....uyD",
        "........|....uywD",
        "........|...uywvD",
        "........|..uywvvD",
        "........|.uywvD..",
        "........|uywvD...",
        ".......u|ywvvD...",
        "...O..uy|wvD.....",
        "...NIuyw|vD......",
        "....Idwv|D.......",
        "....gHiD|........",
        "...hH.HG|........",
        "..gG...N|M.......",
        ".EH.....|........",
        ".a......|........",
    ],
}
ICONO_CURVA = {
    'mareas': bezier([(7.5, 9.0), (7.9, 4.5), (11.0, 1.4), (15.6, 1.2)]),
    'jade': bezier([(5, 11), (15.3, 0.7)]),
    'vendaval': bezier([(6.3, 10.7), (15.8, 1.2)]),
}
ICONO_SEMI = {'mareas': 1.5, 'jade': 2.4, 'vendaval': 1.8}


def icono_espada(tema, k):
    fase = k / CUADROS
    celdas = leer(ICONOS_ESPADA[tema])
    borde = contornear(celdas)
    dentro = {p for p, v in celdas.items() if v[0] == 'H' and p not in borde}
    info = {p: (u, d / ICONO_SEMI[tema], d)
            for p, (u, d, _) in proyectar(ICONO_CURVA[tema], dentro).items()}
    if tema == 'mareas':
        # La ola que corre hacia la punta y los destellos de espuma.
        for p, (u, s, d) in info.items():
            m, t, l = celdas[p]
            w = (u * 2.5 - fase - 0.3 * s) % 1.0
            if w < 0.16:
                t = min(5, t + 1)
            elif 0.5 <= w < 0.64:
                t = max(1, t - 1)
            celdas[p] = (m, t, l)
        for nace, u in MAREAS_ESPUMA:
            e = (k - nace) % CUADROS
            if e < 3:
                destello(celdas, cerca(info, u, 0.0, 1.0, dentro), e, dentro)
    elif tema == 'jade':
        # La arista descansa un tono por debajo; el pulso la enciende al subir.
        for p, (u, s, d) in info.items():
            m, t, l = celdas[p]
            if t == 5:
                t = 4
            for j in (0.0, 0.5):
                du = (u - (fase + j)) % 1.0
                if du < 0.14 or du > 0.95:
                    t = min(5, t + 1)
            celdas[p] = (m, t, l)
        u, s = JADE_FACETAS[(k // 3) % len(JADE_FACETAS)]
        p = min(info, key=lambda q: (info[q][0] - u) ** 2 * 400 + (info[q][1] - s) ** 2)
        destello(celdas, p, k % 3, dentro, libres=True)
    else:
        # El rayo, como en la mano: sube en zigzag por dentro de la hoja con
        # su estela y al llegar arriba descarga (el zigzag y el filo se
        # encienden, salta una chispa de cada diente) y se apaga.
        filo = [p for p, v in celdas.items() if v[0] == 'A' and v[2] and p[1] < 12]
        canal = {p for p, (u, s, d) in info.items() if abs(s - zigzag(u, 3.0, 0.55)) < 0.5}
        cabeza = rayo(celdas, canal, info, k, filo)
        if cabeza is not None and 0.1 < cabeza < 1.0 and k % 2 == 1:
            c = min(info, key=lambda q: (info[q][0] - cabeza) ** 2)
            q = (c[0] + 2, c[1] + 1)
            if q not in celdas and 0 <= q[0] < 16 and 0 <= q[1] < 16:
                celdas[q] = ('A', 3, True)
        elif k == VENDAVAL_DESCARGA:
            for q in ((15, 5), (13, 8)):                 # junto a los dientes
                if q not in celdas:
                    celdas[q] = ('A', 4, True)
    return a_imagen(celdas, tema, 16, 16)


ICONO = {t: (lambda k, t=t: icono_espada(t, k)) for t in ICONOS_ESPADA}


# ======================================================================
#  Las armas de cada papel (octubre de 2026). Cada tema da el arma de su
#  papel en vez de la espada:
#    mareas_trident    el Tridente de las Mareas   (agua, el sanador)
#    jade_hammer       el Martillo de Jade         (tierra, el tanque)
#    vendaval_bow      el Arco del Vendaval        (viento, el apoyo)
#    solar_greatsword  el Mandoble Solar           (fuego, el dano)
#  Como las espadas: en la mano (32x32) se calcula con las mismas piezas
#  (curvas, barras, discos, mapas) y se anima; en el inventario (16x16) va
#  a mano. Todas en la diagonal de las espadas: el puno abajo a la
#  izquierda y la cabeza arriba a la derecha (las coloca el mismo modelo).
#  El arco no: sigue el dibujo de los arcos del juego (ver mas abajo).
# ======================================================================
RAIZ2 = math.sqrt(2)
HACIA_PUNTA = (1 / RAIZ2, -1 / RAIZ2)       # a lo largo del arma, hacia arriba a la derecha
A_LO_ANCHO = (1 / RAIZ2, 1 / RAIZ2)         # de traves, hacia abajo a la derecha


def mas(a, *pasos):
    """a + v1*k1 + v2*k2...; pasos: (v, k)."""
    x, y = a
    for v, k in pasos:
        x, y = x + v[0] * k, y + v[1] * k
    return (x, y)


# ---------------------------- El Tridente ------------------------------
#  Tres puntas de agua que sube corriendo, con espuma en la punta y una
#  lengueta a cada lado (las puntas del tridente). Nacen de una media luna de
#  metal abisal con su filo de prismarina, encima de la venera de nacar (la de
#  la espada). El asta larga de metal abisal con anillas de prismarina, el
#  puno de alga y una perla por regaton. De las puntas de la media luna cae
#  una gota de vez en cuando.
TRI_VENERA = (13.5, 18.5)
TRI_MEDIO = mas(TRI_VENERA, (HACIA_PUNTA, 4.6))                  # el medio de la media luna
TRI_LUNA = bezier([mas(TRI_MEDIO, (A_LO_ANCHO, -6.4), (HACIA_PUNTA, 2.6)),
                   mas(TRI_MEDIO, (A_LO_ANCHO, -2.4), (HACIA_PUNTA, -0.8)),
                   mas(TRI_MEDIO, (A_LO_ANCHO, 2.4), (HACIA_PUNTA, -0.8)),
                   mas(TRI_MEDIO, (A_LO_ANCHO, 6.4), (HACIA_PUNTA, 2.6))])
TRI_LADO = [(0, 1.9), (0.6, 1.6), (0.68, 3.1), (0.73, 1.3), (1.0, 0.4)]   # la lengueta, a 2/3
TRI_PUNTAS = [   # (curva, semianchura): la del medio y las dos de los lados
    (bezier([mas(TRI_MEDIO, (HACIA_PUNTA, 0.5)), (30.8, 1.2)]),
     [(0, 2.3), (0.68, 1.8), (0.75, 3.4), (0.79, 1.5), (1.0, 0.4)]),
    (bezier([TRI_LUNA[0], mas(TRI_LUNA[0], (HACIA_PUNTA, 10.0))]), TRI_LADO),
    (bezier([TRI_LUNA[-1], mas(TRI_LUNA[-1], (HACIA_PUNTA, 10.0))]), TRI_LADO),
]
TRI_ESPUMA = [(0, 0, 0.55), (4, 1, 0.45), (8, 2, 0.5)]           # (cuadro, punta, por donde)


def tridente_mano(k):
    fase = k / CUADROS
    celdas = {}
    # El asta, del regaton a la venera: metal con anillas de prismarina y el puno de alga.
    def asta(t, d, L):
        if 0.24 < t < 0.5:
            return ('D', 3 if (t * L / 1.5 + d * 0.6) % 2.0 < 0.9 else 2 if d > 0 else 1)
        if (t * L) % 4.6 < 1.0 and t > 0.5:
            return ('A', 3 if d > 0 else 2)
        return ('M', 5 if d > 0.45 else 4 if d > -0.45 else 3)
    barra(celdas, (2.6, 29.4), mas(TRI_VENERA, (HACIA_PUNTA, -0.6)), 1.75, asta)
    bola(celdas, (2.4, 29.6), 2.0,
         lambda dx, dy, r: ('B', 4 if math.hypot(dx + 0.6, dy + 0.6) < 0.9 else 3 if r < 1.5 else 2))
    venera(celdas, (int(TRI_VENERA[0]), int(TRI_VENERA[1])), R=4.2, bulto=0.3)
    # La media luna: metal abisal, con su filo de prismarina por arriba.
    for p, (u, s, d) in hoja(TRI_LUNA, [(0, 1.6), (0.5, 2.0), (1, 1.6)], [(0, 1.3), (0.5, 1.6), (1, 1.3)]).items():
        celdas[p] = ('A', 3, False) if s > 0.55 else ('M', 5 if s > 0 else 4 if s > -0.5 else 3, False)
    # Las tres puntas: agua que sube por bandas, con la espuma en la punta.
    puntas = []
    for curva, semi in TRI_PUNTAS:
        info = hoja(curva, semi, semi)
        puntas.append(info)
        for p, (u, s, d) in info.items():
            t = 4 if s > 0.35 else 3 if s > -0.35 else 2
            w = (u * 2.2 - fase * 2.0) % 1.0
            if w < 0.18:
                t += 1                                   # la ola que sube
            elif 0.5 <= w < 0.62:
                t -= 1
            if u > 0.86:
                t = 5 if s > -0.3 else 4                 # la espuma de la punta
            celdas[p] = ('H', max(1, min(5, t)), False)
    borde = contornear(celdas)
    for i, info in enumerate(puntas):
        dentro = {p for p in info if p not in borde and celdas[p][0] == 'H'}
        for nace, j, u in TRI_ESPUMA:
            e = (k - nace) % CUADROS
            if j == i and e < 3:
                destello(celdas, cerca(info, u, -1.0, 1.0, dentro), e, dentro)
    # La gota que cae de una punta de la media luna (cada lado a su tiempo).
    for extremo, nace in ((TRI_LUNA[0], 2), (TRI_LUNA[-1], 8)):
        e = (k - nace) % CUADROS
        if e < 4:
            q = (int(extremo[0] - 0.5), int(extremo[1] + 1.5 + e * 1.4))
            if q not in celdas and 0 <= q[0] < 32 and 0 <= q[1] < 32:
                celdas[q] = ('H', 4 if e < 2 else 3, True)
    return a_imagen(celdas, 'mareas', 32, 32)


# ------------------------------ El Martillo ----------------------------
#  Un martillo de guerra a dos manos: la cabeza grande de metal verde de
#  traves al mango, con un bloque de jade tallado en cada boca, un ribete de
#  oro que los separa y, en medio, la placa de oro con la espiral cuadrada del
#  templo; encima una punta de jade. El mango largo con anillas de oro, el
#  puno envuelto y un pomo de oro con su jade. Las vetas del jade laten y un
#  destello salta de bloque en bloque.
MAR_PUNO = (2.6, 29.4)
MAR_CENTRO = mas(MAR_PUNO, (HACIA_PUNTA, 24.6))
MAR_LARGO, MAR_GRUESO, MAR_BOCA = 9.2, 4.6, 2.8     # media cabeza, media anchura, lo que mide cada jade


def martillo_mano(k):
    fase = k / CUADROS
    celdas = {}
    # El mango: metal verde con anillas de oro y el puno envuelto (la mano baja, a dos manos).
    def mango(t, d, L):
        x = t * L
        if 2.5 < x < 9.5:
            return ('M', 3 if (x + d * 0.8) % 2.2 < 1.0 else 2 if d > 0 else 1)
        if x % 4.4 < 1.1 or x > L - 1.4:
            return ('B', 4 if d > 0.3 else 3 if d > -0.6 else 2)
        return ('M', 5 if d > 0.5 else 4 if d > -0.4 else 3)
    barra(celdas, MAR_PUNO, mas(MAR_CENTRO, (HACIA_PUNTA, -MAR_GRUESO + 0.5)), 1.6, mango)
    bola(celdas, (2.5, 29.5), 2.3, lambda dx, dy, r: ('A', 4) if r < 0.8 else ('A', 2) if r < 1.3
         else ('B', 4 if dx + dy < -0.8 else 3 if dx + dy < 0.8 else 2))
    # La cabeza: de una boca a la otra (a, b), su grueso a lo largo del mango (d).
    a = mas(MAR_CENTRO, (A_LO_ANCHO, -MAR_LARGO))
    b = mas(MAR_CENTRO, (A_LO_ANCHO, MAR_LARGO))
    def cabeza(t, d, L):
        x = t * L
        boca = min(x, L - x)
        if boca < MAR_BOCA:
            # El jade tallado: la cara de la boca, la arista de arriba y las facetas.
            if boca < 0.9:
                return ('A', 4 if x < L / 2 else 3)
            return ('A', 4 if d > 1.8 else 3 if d > -1.2 else 2)
        if boca < MAR_BOCA + 1.0:
            return ('B', 4 if d > 1.2 else 3 if d > -1.6 else 2)          # el ribete de oro
        if abs(d) > MAR_GRUESO - 1.0:
            return ('B', 3 if d > 0 else 2)                                # los cantos de oro
        return ('M', 5 if d > 1.6 else 4 if d > -1.0 else 3)
    barra(celdas, a, b, MAR_GRUESO, cabeza, encima=True)
    # La placa de la espiral en medio.
    calcar(celdas, ESPIRAL, int(round(MAR_CENTRO[0] - 3)), int(round(MAR_CENTRO[1] - 3)))
    # La punta de jade de arriba, que sale del canto de la cabeza.
    for p, (u, s, d) in hoja(bezier([mas(MAR_CENTRO, (HACIA_PUNTA, MAR_GRUESO - 0.6)),
                                     mas(MAR_CENTRO, (HACIA_PUNTA, MAR_GRUESO + 5.4))]),
                             [(0, 2.0), (0.4, 1.7), (1, 0.3)], [(0, 2.0), (0.4, 1.7), (1, 0.3)]).items():
        celdas[p] = ('A', 4 if s > 0.25 else 3 if s > -0.35 else 2, False)
    borde = contornear(celdas)
    # Las vetas del jade laten: un pulso que va de una boca a la otra.
    jade = [p for p, v in celdas.items() if v[0] == 'A' and p not in borde]
    for p in jade:
        t, d, L = seg((p[0] + 0.5, p[1] + 0.5), a, b)
        if abs(d - 1.6 * math.sin(t * 9.0)) < 0.55:
            du = (t - fase) % 1.0
            m, tono, l = celdas[p]
            celdas[p] = ('A', 4 if du < 0.2 or du > 0.92 else max(tono, 3), l)
    # El destello: de un jade al otro y a la punta, tres cuadros en cada uno.
    sitios = [mas(a, (A_LO_ANCHO, 1.2), (HACIA_PUNTA, 1.6)), mas(MAR_CENTRO, (HACIA_PUNTA, MAR_GRUESO + 1.6)),
              mas(b, (A_LO_ANCHO, -1.4), (HACIA_PUNTA, 1.4))]
    s = sitios[(k // 4) % 3]
    p = min(jade, key=lambda q: (q[0] + 0.5 - s[0]) ** 2 + (q[1] + 0.5 - s[1]) ** 2)
    destello(celdas, p, k % 4 if k % 4 < 3 else 3, set(jade), m='A', alto=4, libres=True)
    return a_imagen(celdas, 'jade', 32, 32)


# ------------------------------ El Mandoble ----------------------------
#  El mandoble del caballero solar: una hoja ancha y recta que arde, con la
#  canal de brasa honda por la que sube la lava, el naranja hacia fuera y el
#  blanco caliente junto a los dos filos. La guarda de oro, ancha, con el sol
#  en medio (el disco de oro, el alma de lava y sus rayos); el puno largo de
#  obsidiana con anillas de oro (a dos manos) y un pomo de oro con su gema.
#  Una ola de calor sube por la hoja y se desprenden brasas de los filos.
MAN_GUARDA = (9.6, 22.4)
MAN_CURVA = bezier([MAN_GUARDA, (31.0, 1.0)])
MAN_ANCHO = [(0, 3.4), (0.07, 4.3), (0.72, 4.0), (0.9, 2.4), (1.0, 0.4)]
MAN_BRASAS = [(0, 0.35, 1), (3, 0.62, -1), (6, 0.48, 1), (9, 0.8, -1)]       # (cuadro, por donde, lado)


def mandoble_mano(k):
    fase = k / CUADROS
    info = hoja_de('solar', MAN_CURVA, MAN_ANCHO, MAN_ANCHO)
    celdas = {}
    for p, (u, s, d) in info.items():
        a = abs(s)
        if a < 0.16 and u < 0.82:
            celdas[p] = ('H', 1, False)                                    # la canal, brasa honda
        else:
            t = 5 if a > 0.64 else 4 if a > 0.42 else 3 if a > 0.24 else 2
            if s < 0 and t < 5:
                t = max(2, t - 1)                                          # el lado de la sombra
            w = (u * 1.6 - fase) % 1.0
            if w < 0.12 and t < 5:
                t += 1                                                     # la ola de calor
            celdas[p] = ('H', t, False)
    # La guarda: una barra de oro de traves con las puntas en llama.
    a, b = mas(MAN_GUARDA, (A_LO_ANCHO, -7.2)), mas(MAN_GUARDA, (A_LO_ANCHO, 7.2))
    barra(celdas, a, b, 1.35, lambda t, d, L: ('B', 4 if d > 0.5 else 3 if d > -0.5 else 2), encima=True)
    for punta, lado in ((a, -1), (b, 1)):
        for p, (u, s, d) in hoja(bezier([punta, mas(punta, (A_LO_ANCHO, lado * 1.6), (HACIA_PUNTA, 2.6))]),
                                 [(0, 1.5), (1, 0.3)], [(0, 1.5), (1, 0.3)]).items():
            celdas[p] = ('B', 4 if s > 0 else 3, False)
    # El puno de obsidiana con anillas de oro, y el pomo.
    barra(celdas, mas(MAN_GUARDA, (HACIA_PUNTA, -1.5)), (3.4, 28.6), 1.45,
          lambda t, d, L: ('B', 3 if d > 0 else 2) if (t * L) % 3.0 < 0.9 else ('D', 3 if d > 0.4 else 2 if d > -0.5 else 1))
    bola(celdas, (2.6, 29.4), 2.3, lambda dx, dy, r: ('A', 3) if r < 1.0 else ('B', 4 if dx + dy < -0.6 else 3 if dx + dy < 0.9 else 2))
    # El sol de la guarda: el disco de oro, el alma de lava y ocho rayos cortos.
    for i in range(8):
        ang = i * math.pi / 4
        for r in (3.2, 3.9):
            q = (int(MAN_GUARDA[0] + 0.5 + math.cos(ang) * r), int(MAN_GUARDA[1] + 0.5 - math.sin(ang) * r))
            if i % 2 == 0 or r < 3.5:
                celdas[q] = ('B', 4 if r < 3.5 else 3, False)
    bola(celdas, (MAN_GUARDA[0] + 0.5, MAN_GUARDA[1] + 0.5), 2.7,
         lambda dx, dy, r: ('A', 4 if r < 0.9 else 3 if r < 1.6 else 2) if r < 2.0 else ('B', 4 if dx + dy < 0 else 3))
    borde = contornear(celdas)
    dentro = {p for p in info if p not in borde and celdas[p][0] == 'H'}
    # La lava que sube por la canal (dos pulsos).
    for p in dentro:
        if abs(info[p][1]) >= 0.16 or info[p][0] >= 0.82:
            continue
        u = info[p][0]
        for j in (0.0, 0.5):
            du = (u - fase - j) % 1.0
            if du < 0.12:
                celdas[p] = ('A', 4 if du < 0.05 else 3, False)
            elif du > 0.9:
                celdas[p] = ('A', 2, False)
    # Las brasas: salen del filo y suben hacia la punta, apagandose.
    for nace, u, lado in MAN_BRASAS:
        e = (k - nace) % CUADROS
        if e >= 4:
            continue
        c = min((p for p in info if (info[p][1] > 0) == (lado > 0)),
                key=lambda q: abs(info[q][0] - u) + (1 - abs(info[q][1])) * 0.3)
        q = (c[0] + (1 + e if lado > 0 else 2 + e), c[1] - (2 + e if lado > 0 else e - 1))
        if q not in celdas and 0 <= q[0] < 32 and 0 <= q[1] < 32:
            celdas[q] = ('A', 4 - min(3, e), True)
    return a_imagen(celdas, 'solar', 32, 32)


# ----------------------------------------------------------------------
#  Las armas en el inventario (16x16), a mano y con la leyenda de las
#  piezas (u-z la hoja o el agua). La animacion se pinta encima, como en las
#  espadas: cada pixel se proyecta sobre el eje del arma (u de 0 en el pomo a
#  1 en la punta) y solo se toca por dentro del contorno.
# ----------------------------------------------------------------------
ICONOS_ARMA = {
    # Las tres puntas de agua (la del medio mas larga), la media luna de
    # metal con su filo de prismarina, la venera de nacar, el asta con el
    # puno de alga y la perla abajo.
    'mareas_trident': [
        "........|Zw.....Z",
        ".......Y|w...XxZw",
        "......Xw|....xyw.",
        "....CXw.|...xyw.w",
        "....4C..|..xxw...",
        ".....4D.|.xxw...Z",
        "......4D|xxw...Yv",
        ".....hJ4|D....Xv.",
        ".....giJ|4D..Xv..",
        ".....3gi|h4CXv...",
        "....353g|g.4C3...",
        "...bdb..|........",
        "..qsq...|........",
        ".qsq....|........",
        "J53.....|........",
        "hg......|........",
    ],
    # La cabeza grande de traves: un jade en cada boca, el ribete de oro, el
    # metal verde con sus cantos de oro y la placa de oro con su gema en
    # medio; la punta de jade arriba, el mango con anillas de oro y el pomo.
    'jade_hammer': [
        "........|........",
        ".......e|........",
        "......ee|d.......",
        ".....eed|jh...D..",
        "....cccj|55hdE...",
        ".....ci4|45ihc...",
        "......g3|ijE5h...",
        ".......g|3ihh5h..",
        "......hj|g34455j.",
        ".....454|.g344jdd",
        "....454.|..g3icdd",
        "...hjg..|...ibcc.",
        "..454...|....bb..",
        ".232....|........",
        "JD2.....|........",
        "hg......|........",
    ],
    # La hoja ancha que arde (el filo blanco caliente, la canal de brasa), la
    # guarda de oro con el sol en medio, el puno largo de obsidiana con sus
    # anillas y el pomo de oro.
    'solar_greatsword': [
        "........|.......Z",
        "........|.....zZy",
        "........|...uzyw.",
        "........|..uzywy.",
        "........|.uzywyu.",
        "........|uzywyu..",
        "..I....u|zywyu...",
        "......uz|ywyu....",
        ".hJ..uzy|wyu.....",
        "..hJuzyw|yu......",
        "...hijjy|u.......",
        "...ijEdi|........",
        "..hiidi.|........",
        ".qsr.hhJ|h.......",
        "Eir....h|........",
        "hg......|........",
    ],
}
EJE_ICONO = bezier([(0.5, 15.5), (15.5, 0.5)])


def icono_arma(nombre, k):
    tema = nombre.split('_')[0]
    fase = k / CUADROS
    celdas = leer(ICONOS_ARMA[nombre])
    borde = contornear(celdas)
    info = {p: (u, d) for p, (u, d, _) in proyectar(EJE_ICONO, list(celdas)).items()}
    dentro = {p for p in celdas if p not in borde}
    if nombre == 'mareas_trident':
        # El agua sube por las puntas; la espuma salta en una punta y luego
        # en otra, y cae una gota de la media luna.
        for p in dentro:
            m, t, l = celdas[p]
            if m != 'H':
                continue
            w = (info[p][0] * 3.0 - fase * 2.0) % 1.0
            if w < 0.2:
                t = min(5, t + 1)
            elif 0.5 <= w < 0.66:
                t = max(1, t - 1)
            celdas[p] = (m, t, l)
        for nace, p in ((0, (14, 1)), (4, (8, 1)), (8, (14, 6))):
            e = (k - nace) % CUADROS
            if e < 3 and p in celdas:
                destello(celdas, p, e, dentro)
        e = (k - 6) % CUADROS
        if e < 3 and (11, 11 + e) not in celdas:
            celdas[(11, 11 + e)] = ('H', 4 - e, True)
    elif nombre == 'jade_hammer':
        # El pulso cruza la cabeza de una boca a la otra encendiendo el jade, y
        # un destello salta de un jade a la punta y al otro jade.
        for p in dentro:
            m, t, l = celdas[p]
            if m != 'A':
                continue
            du = ((p[0] + p[1] - 8) / 18.0 - fase) % 1.0
            if du < 0.22:
                celdas[p] = (m, min(4, t + 1), l)
        sitio = ((5, 4), (12, 4), (13, 10))[(k // 4) % 3]
        destello(celdas, sitio, k % 4 if k % 4 < 3 else 3, dentro, m='A', alto=4, libres=True)
    elif nombre == 'solar_greatsword':
        # La ola de calor sube por la hoja, la lava sube por la canal y salta
        # una brasa del filo de vez en cuando.
        for p in dentro:
            m, t, l = celdas[p]
            if m != 'H':
                continue
            u = info[p][0]
            if p[0] + p[1] == 16 and u < 0.85:
                du = (u * 1.5 - fase) % 1.0
                if du < 0.18:
                    celdas[p] = ('A', 4 if du < 0.09 else 3, l)
                continue
            if (u * 1.6 - fase) % 1.0 < 0.14 and t < 5:
                celdas[p] = (m, t + 1, l)
        for nace, q in ((1, (13, 5)), (5, (8, 4)), (9, (15, 6))):
            e = (k - nace) % CUADROS
            r = (q[0] + e // 2, q[1] - e)
            if e < 3 and r not in celdas and 0 <= r[0] < 16 and 0 <= r[1] < 16:
                celdas[r] = ('A', 4 - e, True)
    return a_imagen(celdas, tema, 16, 16)


# ------------------------------- El Arco -------------------------------
#  El arco del vendaval (16x16, sin version en la mano: el modelo de arco del
#  juego lo coloca). Sigue el dibujo de los arcos de Minecraft para que el
#  modelo y la animacion de tensar casen: el arco es un cuarto de circulo con
#  la empunadura arriba a la izquierda y las palas hacia arriba a la derecha y
#  hacia abajo a la izquierda; la cuerda va en la diagonal entre las dos
#  puntas. Al tensar (etapas 0, 1 y 2), la cuerda se abre en V hacia abajo a la
#  derecha, las palas se cierran un poco y la flecha (la del vendaval: asta
#  anil, plumas de cielo y violeta, punta de acero de tormenta) va por la
#  diagonal con la punta hacia arriba a la izquierda.
#  Las palas son de metal anil por dentro y de pluma por fuera: el canto de
#  fuera alterna pluma blanca, cielo y violeta, y en cada pala salen dos
#  plumas sueltas. La empunadura, violeta con el ojo de la tormenta.
# El eje de las palas, de la punta de arriba a la de abajo (un cuarto de
# circulo de radio 13 alrededor de (15.5, 15.5)), y cuanto pesa cada tramo:
# 3 en casi toda la pala (canto de pluma, metal y vientre), 2 cerca de las
# puntas y 1 en ellas.
ARCO_EJE = [(15, 2, 1), (14, 2, 1), (13, 2, 2), (12, 2, 2), (11, 3, 3), (10, 3, 3), (9, 4, 3), (8, 4, 3),
            (8, 5, 3), (7, 5, 3), (6, 6, 3), (5, 7, 3), (5, 8, 3), (4, 8, 3), (4, 9, 3), (3, 10, 3),
            (3, 11, 3), (2, 12, 2), (2, 13, 2), (2, 14, 1), (2, 15, 1)]
ARCO_V = {None: None, 0: (10, 10), 1: (11, 11), 2: (12, 12)}       # el vertice de la cuerda
# Al tensar, las puntas se cierran un poco hacia la cuerda.
ARCO_PUNTAS = {None: ((15, 2), (2, 15)), 0: ((15, 3), (3, 15)), 1: ((14, 3), (3, 14)), 2: ((14, 4), (4, 14))}


def linea(a, b):
    """Los pixeles de una recta de a a b (Bresenham), en enteros."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    out = []
    while True:
        out.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return out
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def arco(etapa=None):
    celdas = {}
    arriba, abajo = ARCO_PUNTAS[etapa]
    eje = list(ARCO_EJE)
    # Las puntas: el ultimo tramo de cada pala va hasta su punta de esa etapa.
    eje = [e for e in eje if e[:2] not in ((15, 2), (14, 2), (2, 14), (2, 15))]
    eje = [(q[0], q[1], 1) for q in linea(arriba, (13, 2))[:-1]] + eje +           [(q[0], q[1], 1) for q in linea((2, 13), abajo)[1:]]
    for x, y, peso in eje:
        pala_alta = y < x                                   # la de arriba va tumbada, la de abajo de pie
        fuera = (x, y - 1) if pala_alta else (x - 1, y)
        dentro = (x, y + 1) if pala_alta else (x + 1, y)
        celdas[(x, y)] = ('M', 4, False)
        if peso >= 2:
            celdas.setdefault(fuera, ('C', 3, True))       # el canto de pluma
        if peso >= 3:
            celdas.setdefault(dentro, ('M', 2, False))      # el vientre
    # El canto de pluma alterna blanco, cielo y violeta por tramos.
    for (x, y), (m, t, l) in list(celdas.items()):
        if m == 'C':
            n = (x + y) // 3 % 3
            celdas[(x, y)] = (('C', 4, True), ('A', 3, True), ('B', 3, True))[n]
    # La empunadura violeta con el ojo de la tormenta.
    for q in ((6, 6), (7, 5), (5, 7), (6, 7), (7, 6)):
        if q in celdas:
            celdas[q] = ('B', 3, False)
    celdas[(6, 6)] = ('A', 4, True)
    # Los penachos de las puntas: dos plumas que salen hacia fuera.
    for (px, py), plumas in ((arriba, ((0, -1, 'C'), (1, -1, 'A'), (-1, -1, 'B'))),
                             (abajo, ((-1, 0, 'C'), (-1, 1, 'A'), (-1, -1, 'B')))):
        for dx, dy, m in plumas:
            q = (px + dx, py + dy)
            if 0 <= q[0] < 16 and 0 <= q[1] < 16 and q not in celdas:
                celdas[q] = (m, 4 if m == 'C' else 3, True)
    contornear(celdas)
    # La cuerda, fina y clara.
    v = ARCO_V[etapa]
    cuerda = linea(arriba, abajo) if v is None else linea(arriba, v) + linea(v, abajo)
    for q in cuerda:
        if q not in celdas and 0 <= q[0] < 16 and 0 <= q[1] < 16:
            celdas[q] = ('C', 2, True)
    if v is not None:
        # La flecha: de la cuerda hacia arriba a la izquierda, por la diagonal.
        for i in range(12):
            q = (v[0] - i, v[1] - i)
            if not (0 <= q[0] < 16 and 0 <= q[1] < 16):
                continue
            if i < 3:
                celdas[q] = ('M', 5, True)                              # el asta junto a las plumas
                if i > 0:
                    for r, mt in (((q[0] + 1, q[1]), ('A', 3)), ((q[0], q[1] + 1), ('B', 3))):
                        if 0 <= r[0] < 16 and 0 <= r[1] < 16:
                            celdas[r] = mt + (True,)                     # las plumas
            elif i < 10:
                celdas[q] = ('M', 6, True)
            else:
                celdas[q] = ('H', 5, True) if i == 11 else ('H', 4, True)    # la punta de acero
                if i == 10:
                    for r in ((q[0] + 1, q[1]), (q[0], q[1] + 1)):
                        if 0 <= r[0] < 16 and 0 <= r[1] < 16:
                            celdas[r] = ('H', 3, True)
    return a_imagen(celdas, 'vendaval', 16, 16)


def arcos():
    """El arco quieto y sus tres tensados."""
    return [arco(e) for e in (None, 0, 1, 2)]


# ------------------------- La flecha del vendaval -----------------------
#  La textura de la entidad (32x32), con el MISMO reparto que la flecha del
#  juego, para que su modelo (dos planos en cruz y la cola) la lea igual:
#    x 0-15,  y 0-4   un costado: la cola de plumas a la izquierda (x 0-4),
#                     el asta por la fila 2 y la punta a la derecha (x 12-15)
#    x 16-31, y 0-4   el otro costado, el mismo dibujo en espejo
#    x 0-4 y x 5-9, y 5-9   la cola vista desde atras: la cruz de las plumas
#  El dibujo es nuestro: asta anil, plumas de cielo (dentro) y violeta (las
#  puntas), el culatin de pluma blanca y la punta de cristal de cielo.
FLECHA_COSTADO = [          # leyenda de las piezas: h-i violeta, c-e cielo, o pluma, 4-6 metal
    "hii.............",
    ".ddde.......cd..",
    "o5i56565656cddee",
    ".ddde.......cd..",
    "hii.............",
]
FLECHA_COLA = [
    "..i..",
    "..d..",
    "idodi",
    "..d..",
    "..i..",
]


def flecha_entidad():
    T = TEMAS['vendaval']
    im = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    px = im.load()
    for y, fila in enumerate(FLECHA_COSTADO):
        for x, ch in enumerate(fila):
            if ch != '.':
                m, t = LEYENDA[ch]
                px[x, y] = T[m][t]
                px[31 - x, y] = T[m][t]                  # el otro costado, en espejo
    for y, fila in enumerate(FLECHA_COLA):
        for x, ch in enumerate(fila):
            if ch != '.':
                m, t = LEYENDA[ch]
                px[x, 5 + y] = T[m][t]
                px[5 + x, 5 + y] = T[m][t]
    return im


ARMAS = {
    'mareas_trident': ('mareas', lambda k: icono_arma('mareas_trident', k), tridente_mano),
    'jade_hammer': ('jade', lambda k: icono_arma('jade_hammer', k), martillo_mano),
    'solar_greatsword': ('solar', lambda k: icono_arma('solar_greatsword', k), mandoble_mano),
}


# === PRINCIPAL ===
# (los bancos de pruebas cortan el fichero aqui para no escribir nada)
PIEZAS_ORDEN = ('helmet', 'chestplate', 'leggings', 'boots')
ARMA_DE = {'mareas': 'mareas_trident', 'jade': 'jade_hammer', 'vendaval': 'vendaval_bow', 'solar': 'solar_greatsword'}
ARCO_NOMBRES = ('vendaval_bow', 'vendaval_bow_pulling_0', 'vendaval_bow_pulling_1', 'vendaval_bow_pulling_2')
FLECHA = os.path.join(RAIZ, 'src/main/resources/assets/atalaya/textures/entity/projectiles/vendaval_arrow.png')
malas = []
for _n, _f in list(PIEZAS.items()) + list(ICONOS_ESPADA.items()) + list(ICONOS_ARMA.items()):
    malas += comprobar(_n, _f, 16)
if malas:
    raise SystemExit('\n'.join(malas))

os.makedirs(ITEM, exist_ok=True)
MCMETA = json.dumps({'animation': {'frametime': 2}}, indent=2) + '\n'


def guardar_tira(cuadros, nombre):
    """Una tira animada y su .mcmeta (como las espadas)."""
    tira(cuadros).save(os.path.join(ITEM, f'{nombre}.png'))
    with open(os.path.join(ITEM, f'{nombre}.png.mcmeta'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(MCMETA)


SALIDAS = {}
ESCRITOS = [t for t in TEMAS if SOLO is None or t in SOLO]
for tema in TEMAS:
    escribe = tema in ESCRITOS
    for pieza in PIEZAS_ORDEN:
        im = pintar(PIEZAS[f'{tema}_{pieza}'], tema)
        if escribe:
            im.save(os.path.join(ITEM, f'{tema}_{pieza}.png'))
        SALIDAS[f'{tema}_{pieza}'] = im
    if tema not in ICONOS_ESPADA:
        continue                                    # el solar no tiene espada: su arma es el mandoble
    icono = [icono_espada(tema, k) for k in range(CUADROS)]
    mano = [MANO[tema](k) for k in range(CUADROS)]
    if escribe:
        tira(icono).save(os.path.join(ITEM, f'{tema}_sword.png'))
        tira(mano).save(os.path.join(ITEM, f'{tema}_sword_in_hand.png'))
        for nombre in (f'{tema}_sword.png.mcmeta', f'{tema}_sword_in_hand.png.mcmeta'):
            with open(os.path.join(ITEM, nombre), 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(MCMETA)
    SALIDAS[f'{tema}_sword'] = icono
    SALIDAS[f'{tema}_sword_in_hand'] = mano
# Las armas de cada papel: el icono (16x16) y en la mano (32x32), las dos animadas.
for nombre, (tema, icono_fn, mano_fn) in ARMAS.items():
    icono = [icono_fn(k) for k in range(CUADROS)]
    mano = [mano_fn(k) for k in range(CUADROS)]
    if tema in ESCRITOS:
        guardar_tira(icono, nombre)
        guardar_tira(mano, f'{nombre}_in_hand')
    SALIDAS[nombre] = icono
    SALIDAS[f'{nombre}_in_hand'] = mano
# El arco (quieto y sus tres tensados, fijos) y la textura de su flecha.
for nombre, im in zip(ARCO_NOMBRES, arcos()):
    if 'vendaval' in ESCRITOS:
        im.save(os.path.join(ITEM, f'{nombre}.png'))
    SALIDAS[nombre] = im
SALIDAS['vendaval_arrow'] = flecha_entidad()
if 'vendaval' in ESCRITOS:
    os.makedirs(os.path.dirname(FLECHA), exist_ok=True)
    SALIDAS['vendaval_arrow'].save(FLECHA)
print('ok:', ', '.join(ESCRITOS), '-', len(ESCRITOS) * 4, 'piezas,',
      len([t for t in ESCRITOS if t in ICONOS_ESPADA]), 'espadas y',
      len([t for t in ESCRITOS if ARMA_DE[t] in ARMAS]), 'armas de', CUADROS, 'cuadros (16x16 y 32x32)',
      '+ arco y flecha' if 'vendaval' in ESCRITOS else '')

# ----------------------------------------------------------------------
#  Hoja de control: por tema, las piezas, la espada (si la tiene) y el arma
#  de su papel a 8x sobre el gris del inventario y sobre oscuro; el arma en
#  la mano, grande; a tamano real (x1, x2 y x3) y en una barra de inventario
#  como la del juego; los doce cuadros de la espada y del arma (el icono a x4
#  y en la mano a x3). Del arco, sus cuatro dibujos y la flecha.
# ----------------------------------------------------------------------
if HOJA:
    from PIL import ImageDraw
    GRIS, OSCURO, FONDO = (139, 139, 139, 255), (30, 32, 40, 255), (48, 50, 58, 255)
    TEXTO = (235, 235, 240, 255)

    def ranura(d, x, y, e):
        """Una ranura del inventario de vanilla (18x18 a escala e)."""
        d.rectangle((x, y, x + 18 * e - 1, y + 18 * e - 1), fill=(139, 139, 139, 255))
        d.rectangle((x, y, x + 17 * e - 1, y + e - 1), fill=(55, 55, 55, 255))
        d.rectangle((x, y, x + e - 1, y + 17 * e - 1), fill=(55, 55, 55, 255))
        d.rectangle((x + e, y + 17 * e, x + 18 * e - 1, y + 18 * e - 1), fill=(255, 255, 255, 255))
        d.rectangle((x + 17 * e, y + e, x + 18 * e - 1, y + 18 * e - 1), fill=(255, 255, 255, 255))

    def grande(im, e):
        return im.resize((im.width * e, im.height * e), Image.NEAREST)

    def tiras_de(tema):
        """Las filas de cuadros de un tema: (cuadros, escala)."""
        out = []
        if f'{tema}_sword' in SALIDAS:
            out += [(SALIDAS[f'{tema}_sword'], 4), (SALIDAS[f'{tema}_sword_in_hand'], 3)]
        arma = ARMA_DE[tema]
        if arma in ARMAS:
            out += [(SALIDAS[arma], 4), (SALIDAS[f'{arma}_in_hand'], 3)]
        else:
            out += [([SALIDAS[n] for n in ARCO_NOMBRES] + [SALIDAS['vendaval_arrow'].crop((0, 0, 32, 16))], 6)]
        return out

    ANCHO = 1450
    altos = {t: 20 + 2 * 136 + 70 + sum(2 * (c[0].height * e + 8) for c, e in tiras_de(t)) + 20 for t in TEMAS}
    hoja = Image.new('RGBA', (ANCHO, 10 + sum(altos.values())), FONDO)
    d = ImageDraw.Draw(hoja)
    y0 = 10
    for tema in TEMAS:
        d.text((12, y0), tema.upper(), fill=TEXTO)
        y = y0 + 20
        arma = ARMA_DE[tema]
        cosas = [SALIDAS[f'{tema}_{p}'] for p in PIEZAS_ORDEN]
        if f'{tema}_sword' in SALIDAS:
            cosas.append(SALIDAS[f'{tema}_sword'][0])
        cosas.append(SALIDAS[arma][0] if arma in ARMAS else SALIDAS['vendaval_bow'])
        en_mano = SALIDAS[f'{arma}_in_hand'][0] if arma in ARMAS else SALIDAS['vendaval_bow_pulling_2']
        # A 8x, sobre gris y sobre oscuro; a la derecha el arma en la mano, grande.
        for fila, fondo in enumerate((GRIS, OSCURO)):
            for j, im in enumerate(cosas):
                x = 12 + j * 136
                d.rectangle((x, y + fila * 136, x + 131, y + fila * 136 + 131), fill=fondo)
                hoja.alpha_composite(grande(im, 8), (x + 2, y + fila * 136 + 2))
            x = 12 + 6 * 136 + 10
            d.rectangle((x, y + fila * 136, x + 131, y + fila * 136 + 131), fill=fondo)
            hoja.alpha_composite(grande(en_mano, 128 // en_mano.width), (x + 2, y + fila * 136 + 2))
        # A tamano real: x1, x2 y x3 sobre los dos fondos.
        xr = 12 + 7 * 136 + 30
        for fila, fondo in enumerate((GRIS, OSCURO)):
            yy = y + fila * 136
            d.rectangle((xr, yy, ANCHO - 12, yy + 131), fill=fondo)
            for j, im in enumerate(cosas):
                hoja.alpha_composite(im, (xr + 6 + j * 20, yy + 6))
                hoja.alpha_composite(grande(im, 2), (xr + 6 + j * 36, yy + 30))
                hoja.alpha_composite(grande(im, 3), (xr + 6 + j * 52, yy + 72))
        y += 2 * 136 + 6
        for j, im in enumerate(cosas):
            ranura(d, 12 + j * 18 * 3, y, 3)
            hoja.alpha_composite(grande(im, 3), (12 + j * 18 * 3 + 3, y + 3))
        for j, im in enumerate(cosas):
            ranura(d, 360 + j * 18 * 2, y + 8, 2)
            hoja.alpha_composite(grande(im, 2), (360 + j * 18 * 2 + 2, y + 10))
        d.text((600, y + 20), 'en una ranura del inventario, a escala 3 y 2', fill=TEXTO)
        y += 64
        # Los cuadros: espada y arma (icono x4, en la mano x3); el arco, sus dibujos y la flecha.
        for cuadros, e in tiras_de(tema):
            h = cuadros[0].height * e + 8
            for fila, fondo in enumerate((GRIS, OSCURO)):
                x = 12
                for im in cuadros:
                    w = im.width * e + 4
                    d.rectangle((x, y + fila * h, x + w - 1, y + fila * h + h - 5), fill=fondo)
                    hoja.alpha_composite(grande(im, e), (x + 2, y + fila * h + 2))
                    x += w + 4
            y += 2 * h
        y0 += altos[tema]
    os.makedirs(os.path.dirname(os.path.abspath(HOJA)), exist_ok=True)
    hoja.save(HOJA)
    print('hoja', HOJA)
