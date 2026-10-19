"""
Los iconos de los cambios de dificultad (cambio/<id>, 16 x 16): la pieza que dice de qué va y la marca que dice qué le
pasa. Se apuntan en catalogo_iconos.ICONOS al importar este módulo (lo hace catalogo.py).
"""
import numpy as np

import catalogo_iconos as ci
import catalogo_piezas as cp
import menus_cambios as mc
from catalogo_iconos import (ICONOS, OSCURO, R_AGUA, R_BLANCO, R_CREEPER, R_ENDER, R_FUEGO, R_GAS, R_HUESO, R_MORADO,
                             R_NOCHE, R_PIEDRA, R_ROJO, R_SCULK, R_VERDE, arana, bloque, boton, cactus, calavera, cama,
                             cara_creeper, cara_enderman, cara_zombi, corazon, flecha, gota, llama, luna, manzana, nube,
                             nuevo, ojo, perla, placa, por, puerta, rayo, reloj, sol, tachado, telarana, totem, cifras)
from ruleta import H, Lienzo, esfera, rampa, sd_caja, sd_circulo, sd_elipse, sd_poligono, sd_segmento, tono, union


def icono(nombre):
    def reg(fn):
        ICONOS['cambio/' + nombre] = fn
        return fn
    return reg


def capa(n):
    return Lienzo(n)


# ------------------------------------------------------------------------------------------------------------
#  Al jugador
# ------------------------------------------------------------------------------------------------------------
@icono('pies_de_cristal')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.bota(L, x, y, k, rampa_=rampa('3a6a8a', '6aa0c0', 'a8d4ea', 'dcf2fc', 'ffffff'))
    cp.grietas(L, x, y, 'ffffff')
    por(L, 3)
    return L


@icono('estomago_sin_fondo')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.muslo(L, x, y, k)
    por(L, 2)
    return L


@icono('pulmones_de_papel')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.pulmones(L, x, y, k)
    cp.burbujas(L, x, y, k, puntos=((25, 9, 3.0), (27, 16, 2.0)))
    por(L, 5)
    return L


@icono('sin_bolsas_de_aire')
def _(n=16):
    x, y, k, L = nuevo(n)
    puerta(L, x, y, k, cx=12)
    cp.burbujas(L, x, y, k, puntos=((23, 10, 4.0), (25, 20, 3.0)))
    tachado(L, x, y)
    return L


@icono('heridas_abiertas')
def _(n=16):
    x, y, k, L = nuevo(n)
    corazon(L, x, y, k)
    T = capa(n)
    cp.venda(T, x, y, k, cy=17)
    L.encima(T)
    tachado(L, x, y)
    return L


@icono('el_nether_no_perdona')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.persona(L, x, y, k, esc=0.95)
    T = capa(n)
    llama(T, x, y, k, cx=16, base=31, alto=22, ancho=12)
    T.a *= 0.85
    L.encima(T)
    return L


@icono('brasas_voraces')
def _(n=16):
    x, y, k, L = nuevo(n)
    llama(L, x, y, k)
    por(L, 10)
    return L


@icono('el_mundo_contraataca')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.montana(L, x, y, k)
    por(L, 3)
    return L


@icono('mal_aguero')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.estandarte(L, x, y, k)
    return L


@icono('la_plaga')
def _(n=16):
    x, y, k, L = nuevo(n)
    calavera(L, x, y, k, rampa_=rampa('1e4a14', '3a7a22', '5aae34', '9ad864', 'd8ffb0'), ojos='0e1a08')
    T = capa(n)
    reloj(T, x, y, k, cx=25, cy=25, r=6.5)
    L.encima(T)
    return L


@icono('insomnio')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.ojo_insomne(L, x, y, k)
    return L


@icono('no_mires_al_sol')
def _(n=16):
    x, y, k, L = nuevo(n)
    sol(L, x, y, k, cx=16, cy=16, r=7)
    T = capa(n)
    ojo(T, x, y, k, cx=16, cy=16, r=4.5, iris=rampa('5a3a04', 'a87a1e', 'e0b040', 'f8d870', 'fff2b8'))
    L.encima(T)
    tachado(L, x, y)
    return L


@icono('encogidos')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.persona(L, x, y, k, cx=10, esc=1.0)
    T = capa(n)
    cp.persona(T, x, y, k, cx=24, esc=0.5)
    L.encima(T)
    return L


@icono('protagonista')
def _(n=16):
    x, y, k, L = nuevo(n)
    for i, cx in enumerate((7, 16, 25)):
        cp.corazon_mini(L, x, y, k, cx, 8, esc=7)
    T = capa(n)
    cp.espada(T, x, y, k, a=(6, 30), b=(26, 14))
    L.encima(T)
    return L


# ------------------------------------------------------------------------------------------------------------
#  Al mundo
# ------------------------------------------------------------------------------------------------------------
@icono('lava_desbocada')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.onda(L, x, y, k, cy=18, rampa_=R_FUEGO, contorno='3a0a02')
    for yy in (7, 12):
        L.pintar(sd_segmento(x, y, 6, yy, 22, yy, 1.1) < 0, H('ffc84a')[:3])
        L.pintar(sd_poligono(x, y, [(22, yy - 3), (28, yy), (22, yy + 3)]) < 0, H('ffc84a')[:3])
    return L


@icono('extincion')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.cara_vaca(L, x, y, k, cy=18)
    T = capa(n)
    nube(T, x, y, k, cx=16, cy=8, rampa_=R_GAS, esc=0.75)
    L.encima(T)
    return L


@icono('tierra_yerma')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.trigo(L, x, y, k, rampa_=rampa('2a2418', '4a4030', '6a5e44', '8a7e5e', 'aa9e7e'))
    tachado(L, x, y)
    return L


@icono('espinas_mortales')
def _(n=16):
    x, y, k, L = nuevo(n)
    cactus(L, x, y, k)
    T = capa(n)
    calavera(T, x, y, k, cx=24, cy=24, esc=0.42)
    L.encima(T)
    return L


@icono('no_toques_ese_boton')
def _(n=16):
    x, y, k, L = nuevo(n)
    boton(L, x, y, k)
    T = capa(n)
    calavera(T, x, y, k, cx=25, cy=7, esc=0.42)
    L.encima(T)
    return L


@icono('puertas_malditas')
def _(n=16):
    x, y, k, L = nuevo(n)
    puerta(L, x, y, k)
    T = capa(n)
    calavera(T, x, y, k, cx=24, cy=24, esc=0.42)
    L.encima(T)
    return L


@icono('placas_trampa')
def _(n=16):
    x, y, k, L = nuevo(n)
    placa(L, x, y, k, cy=24)
    T = capa(n)
    calavera(T, x, y, k, cx=16, cy=10, esc=0.6)
    L.encima(T)
    return L


@icono('piedra_ardiente')
def _(n=16):
    x, y, k, L = nuevo(n)
    bloque(L, x, y, k, rampa('2a0a04', '5a1a08', 'a83a0e', 'f07a1a', 'ffc84a'),
           vetas=lambda x, y: ((np.floor(x / 5) + np.floor(y / 5)) % 2) * 0.25)
    T = capa(n)
    calavera(T, x, y, k, cx=24, cy=24, esc=0.42)
    L.encima(T)
    return L


@icono('lava_sin_tregua')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.onda(L, x, y, k, cy=20, rampa_=R_FUEGO, contorno='3a0a02')
    T = capa(n)
    gota(T, x, y, k, cx=16, cy=11, r=6, rampa_=rampa('5a2a04', 'a84a0a', 'e88a1a', 'ffc84a', 'fff2b0'))
    L.encima(T)
    tachado(L, x, y)
    return L


@icono('bosques_sin_futuro')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.brote(L, x, y, k)
    tachado(L, x, y)
    return L


@icono('vacas_secas')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.cara_vaca(L, x, y, k)
    T = capa(n)
    gota(T, x, y, k, cx=25, cy=24, r=4.5, rampa_=R_BLANCO)
    L.encima(T)
    tachado(L, x, y)
    return L


@icono('panales_trampa')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.panal(L, x, y, k)
    T = capa(n)
    for i in range(8):
        a = i * np.pi / 4
        T.pintar(sd_segmento(x, y, 16 + np.cos(a) * 9, 16 + np.sin(a) * 9, 16 + np.cos(a) * 14, 16 + np.sin(a) * 14, 1.2) < 0,
                 H('ff7a20')[:3])
    L.encima(T)
    return L


@icono('techo_de_gas')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=16, cy=10, rampa_=R_GAS)
    T = capa(n)
    cp.persona(T, x, y, k, cx=16, base=31, esc=0.45)
    L.encima(T)
    cifras(L, '150', 2, 11, 'e0ff9a')
    return L


@icono('el_gas_baja')
def _(n=16):
    x, y, k, L = nuevo(n)
    nube(L, x, y, k, cx=14, cy=12, rampa_=R_GAS)
    flecha(L, x, y, arriba=False, cx=26, cy=22, color='e0ff9a')
    cifras(L, '130', 2, 11, 'e0ff9a')
    return L


@icono('la_noche_se_llena')
def _(n=16):
    x, y, k, L = nuevo(n)
    luna(L, x, y, k, cx=10, cy=10, r=8)
    T = capa(n)
    for cx, cy in ((14, 24), (22, 20), (27, 27)):
        T.pintar(sd_circulo(x, y, cx - 1.6, cy, 1.2) < 0, H('ff3a2a')[:3])
        T.pintar(sd_circulo(x, y, cx + 1.6, cy, 1.2) < 0, H('ff3a2a')[:3])
    L.encima(T)
    por(L, 2)
    return L


@icono('techos_que_caen')
def _(n=16):
    x, y, k, L = nuevo(n)
    L.pintar(sd_caja(x, y, 16, 2, 16, 2.5) < 0, R_PIEDRA[1])
    cp.estalactita(L, x, y, k, cx=10, arriba=3, abajo=17, ancho=4)
    T = capa(n)
    cp.estalactita(T, x, y, k, cx=21, arriba=12, abajo=29, ancho=4.5)
    L.encima(T)
    return L


@icono('spawners_eternos')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.jaula(L, x, y, k)
    T = capa(n)
    escudo = sd_poligono(x, y, [(21, 18), (30, 18), (30, 25), (25.5, 30), (21, 25)])
    T.pintar(escudo < 0, ci.ORO[3])
    T.contorno(OSCURO)
    L.encima(T)
    return L


@icono('calabazas_dormidas')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.calabaza(L, x, y, k)
    cifras(L, 'x', 11, 1, 'c8e0ff')
    return L


# ------------------------------------------------------------------------------------------------------------
#  Lo que sale al hacer algo
# ------------------------------------------------------------------------------------------------------------
@icono('nidos_ocultos')
def _(n=16):
    x, y, k, L = nuevo(n)
    telarana(L, x, y, k)
    T = capa(n)
    arana(T, x, y, k, cx=20, cy=21, esc=0.6, rampa_=rampa('062026', '0a3a44', '125a66', '1e8090', '4ac0d0'))
    L.encima(T)
    return L


@icono('tratos_malditos')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.cara_aldeano(L, x, y, k, cx=11, cy=19, lado=9)
    T = capa(n)
    cp.sombrero_bruja(T, x, y, k, cx=22, base=14)
    L.encima(T)
    return L


@icono('cada_muerte_cuenta')
def _(n=16):
    x, y, k, L = nuevo(n)
    calavera(L, x, y, k, cx=11, cy=13, esc=0.65)
    T = capa(n)
    cara_creeper(T, x, y, k, cx=22, cy=22, lado=8, cargado=True)
    L.encima(T)
    return L


# ------------------------------------------------------------------------------------------------------------
#  A los mobs de siempre
# ------------------------------------------------------------------------------------------------------------
@icono('golpes_triples')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.espada(L, x, y, k)
    por(L, 3)
    return L


@icono('piel_mas_gruesa')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.escudo(L, x, y, k)
    cifras(L, '+', 11, 1, 'b8f08a')
    return L


@icono('la_ira_del_end')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_enderman(L, x, y, k, cy=15)
    por(L, 4)
    return L


@icono('cien_de_un_golpe')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_enderman(L, x, y, k, cy=12, lado=10)
    cifras(L, '100', 2, 10, 'ff7a60')
    return L


@icono('aranas_de_guerra')
def _(n=16):
    x, y, k, L = nuevo(n)
    arana(L, x, y, k, cy=18)
    T = capa(n)
    cp.espada(T, x, y, k, a=(20, 14), b=(30, 2))
    L.encima(T)
    return L


@icono('telarana_en_los_pies')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.bota(L, x, y, k)
    T = capa(n)
    telarana(T, x, y, k, cx=18, cy=22, r=10)
    L.encima(T)
    return L


@icono('las_aranas_suben')
def _(n=16):
    x, y, k, L = nuevo(n)
    luna(L, x, y, k, cx=9, cy=9, r=7)
    T = capa(n)
    arana(T, x, y, k, cx=19, cy=20, esc=0.8, rampa_=rampa('062026', '0a3a44', '125a66', '1e8090', '4ac0d0'))
    L.encima(T)
    return L


@icono('zombis_trepadores')
def _(n=16):
    x, y, k, L = nuevo(n)
    L.pintar(sd_caja(x, y, 4, 16, 4, 16) < 0, tono(R_PIEDRA, np.clip(0.4 + ((np.floor(y / 6)) % 2) * 0.15, 0, 1)))
    L.contorno(OSCURO)
    T = capa(n)
    cara_zombi(T, x, y, k, cx=19, cy=13, lado=9)
    L.encima(T)
    flecha(L, x, y, arriba=True, cx=26, cy=26, color='b8f08a')
    return L


@icono('zombis_listos')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_zombi(L, x, y, k, cx=13, cy=18, lado=10)
    T = capa(n)
    cp.pico(T, x, y, k)
    L.encima(T)
    return L


@icono('mordisco_putrido')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_zombi(L, x, y, k)
    T = capa(n)
    calavera(T, x, y, k, cx=24, cy=24, esc=0.42, rampa_=rampa('1e4a14', '3a7a22', '5aae34', '9ad864', 'd8ffb0'))
    L.encima(T)
    return L


@icono('los_muertos_bajan')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_zombi(L, x, y, k, cy=13, lado=10)
    T = capa(n)
    llama(T, x, y, k, cx=16, base=32, alto=12, ancho=14)
    T.a *= 0.9
    L.encima(T)
    return L


@icono('creepers_cargados')
def _(n=16):
    x, y, k, L = nuevo(n)
    cara_creeper(L, x, y, k, cargado=True)
    T = capa(n)
    rayo(T, x, y, k, cx=25, cy=8, esc=0.55)
    L.encima(T)
    return L


@icono('phantoms_ladrones')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.phantom(L, x, y, k, cy=12)
    T = capa(n)
    T.pintar(sd_caja(x, y, 16, 25, 5, 4.5, 1) < 0, ci.ORO[2])
    T.pintar(sd_caja(x, y, 16, 25, 3, 2.5, 0.5) < 0, ci.ORO[4])
    T.contorno(OSCURO)
    L.encima(T)
    return L


@icono('el_abismo_despierta')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.cara_warden(L, x, y, k)
    return L


@icono('wardens_en_la_superficie')
def _(n=16):
    x, y, k, L = nuevo(n)
    luna(L, x, y, k, cx=24, cy=7, r=6)
    T = capa(n)
    cp.cara_warden(T, x, y, k, cx=13, cy=20, lado=9)
    L.encima(T)
    return L


@icono('aldeas_vigiladas')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.cara_aldeano(L, x, y, k, cx=10, cy=12, lado=7)
    T = capa(n)
    cp.cara_warden(T, x, y, k, cx=21, cy=21, lado=8.5)
    L.encima(T)
    return L


@icono('polvora_en_las_ballestas')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.ballesta(L, x, y, k)
    T = capa(n)
    cp.cohete(T, x, y, k)
    L.encima(T)
    return L


@icono('piglins_generosos')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.cara_piglin(L, x, y, k, cy=14, lado=10)
    T = capa(n)
    cp.pepita(T, x, y, k)
    L.encima(T)
    return L


@icono('blazes_sueltos')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.cara_blaze(L, x, y, k)
    return L


@icono('huesos_negros')
def _(n=16):
    x, y, k, L = nuevo(n)
    calavera(L, x, y, k, rampa_=rampa('0a0a0e', '18181e', '2a2a32', '3e3e48', '5a5a66'), ojos='e8e8f0')
    return L


@icono('la_noche_helada')
def _(n=16):
    x, y, k, L = nuevo(n)
    calavera(L, x, y, k, cx=12, cy=15, esc=0.75, rampa_=cp.R_NIEVE)
    T = capa(n)
    calavera(T, x, y, k, cx=23, cy=20, esc=0.6, rampa_=rampa('2a3a1a', '4a5e2a', '6a843a', '8aaa52', 'b8d07a'), ojos='0a1408')
    L.encima(T)
    return L


@icono('esqueletos_en_el_nether')
def _(n=16):
    x, y, k, L = nuevo(n)
    calavera(L, x, y, k, cy=13, esc=0.85)
    T = capa(n)
    llama(T, x, y, k, cx=16, base=32, alto=11, ancho=14)
    T.a *= 0.9
    L.encima(T)
    return L


@icono('nariz_de_sabueso')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.persona(L, x, y, k)
    L.a *= 0.35
    T = capa(n)
    ojo(T, x, y, k, cx=22, cy=9, r=5, iris=rampa('5a0a0a', 'a01a1a', 'e83a2a', 'ff7a60', 'ffd0c8'))
    L.encima(T)
    return L


# ------------------------------------------------------------------------------------------------------------
#  A los objetos y ayudas
# ------------------------------------------------------------------------------------------------------------
@icono('cara_o_cruz')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.moneda(L, x, y, k)
    T = capa(n)
    totem(T, x, y, k, esc=0.6)
    L.encima(T)
    return L


@icono('perlas_afiladas')
def _(n=16):
    x, y, k, L = nuevo(n)
    perla(L, x, y, k, cx=13, cy=17, r=8)
    T = capa(n)
    cp.espada(T, x, y, k, a=(16, 22), b=(30, 4))
    L.encima(T)
    return L


@icono('saltos_caros')
def _(n=16):
    x, y, k, L = nuevo(n)
    perla(L, x, y, k, cx=12, cy=12, r=8)
    T = capa(n)
    corazon(T, x, y, k, cx=23, abajo=31, esc=13, mitad=True)
    L.encima(T)
    return L


@icono('perlas_que_no_cruzan')
def _(n=16):
    x, y, k, L = nuevo(n)
    mc_portal = mc.icono_portal(n)
    L.encima(mc_portal)
    T = capa(n)
    perla(T, x, y, k, cx=24, cy=24, r=6)
    L.encima(T)
    tachado(L, x, y)
    return L


@icono('manzanas_vacias')
def _(n=16):
    x, y, k, L = nuevo(n)
    manzana(L, x, y, k)
    T = capa(n)
    corazon(T, x, y, k, cx=24, abajo=13, esc=10, rampa_=rampa('5a4a04', 'a88a10', 'e8c030', 'fff070', 'fffcd0'))
    L.encima(T)
    tachado(L, x, y)
    return L


@icono('se_pudre_la_carne')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.muslo(L, x, y, k, rampa_=rampa('2a3a14', '4a5e22', '6a8a34', '9ab85a', 'c8e08a'))
    T = capa(n)
    for cx, cy in ((9, 8), (14, 5), (20, 7)):
        T.pintar(sd_segmento(x, y, cx, cy + 3, cx + 1.5, cy - 1, 0.6) < 0, H('9ad864')[:3])
    L.encima(T)
    return L


@icono('piedra_sabia')
def _(n=16):
    x, y, k, L = nuevo(n)
    cp.piedra_afilar(L, x, y, k, cy=13)
    T = capa(n)
    cp.libro(T, x, y, k, cx=23, cy=23, brillo=True, rampa_=rampa('2a0a3a', '561a70', '8a3aa8', 'c27ae0', 'f0d0ff'))
    L.encima(T)
    return L


@icono('bolsa_del_vacio')
def _(n=16):
    import objetos_cambios as oc
    return oc.bolsa(n)


@icono('yunque_dorado')
def _(n=16):
    import objetos_cambios as oc
    return oc.yunque(n)


@icono('fruto_del_recuerdo')
def _(n=16):
    import objetos_cambios as oc
    return oc.fruto(n)


@icono('raiz_de_agua')
def _(n=16):
    import objetos_cambios as oc
    return oc.raiz(n)
