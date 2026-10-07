# Atalaya

Mod de **Fabric** para Minecraft **26.2** · versión **1.1.7**.

**Un mundo que se pone más difícil por fases.** Cada fase vuelve invivible una
parte del mundo y desbloquea a la vez lo que hace falta para volver a entrar:
aparece el peligro, aparece la herramienta. Las fases las abre un operador desde
el menú, así que se pueden anunciar como evento.

El primer ejemplo del patrón fue la radiación: las geodas de amatista queman, y
para entrar hace falta un traje Hazmat que se gasta y se mantiene con filtros.
Detrás vinieron el desierto, la lluvia, la nieve, dos monstruos propios y los
jefes elementales.

> ¿Vas a dibujar una textura? Empieza por **[DISEÑO.md](DISEÑO.md)**: proporciones,
> rampas de color y sombreado, para que lo nuevo parezca del mismo mod.
>
> ¿Vas a hacer un jefe? Empieza por **[Cómo se hace un jefe](#cómo-se-hace-un-jefe)**:
> la ficha de diseño, los generadores, el póster y el teaser.

> **Estado: contenido jugable y probado en el cliente de desarrollo.**
>
> - **El mundo:** radiación en las geodas (con el traje Hazmat y tres mejoras de
>   herrería), insolación e hidratación en el desierto, corrosión y empapado bajo
>   la lluvia, hipotermia en la nieve.
> - **Monstruos:** el Fulminante (el creeper del desierto, con su aturdimiento y
>   la fulgurita) y el Vigía.
> - **Jefes elementales:** **Nerea** (agua), **Aeralis** (aire) y **Rajang**
>   (tierra). Son tres de cuatro: falta el del fuego.
> - **13 efectos propios** registrados y un panel de configuración con **25
>   interruptores**.
>
> **Nada está encendido de fábrica.** Un mundo recién puesto se comporta como
> vanilla hasta que un operador abre cada mecánica. Los jefes no tienen
> interruptor porque no aparecen solos: solo salen con su huevo o con `/summon`.

---

## Contenido

### Radiación

Un efecto de estado **registrado de verdad** (`atalaya:radiacion`), con su icono,
su nombre y su color. No es un efecto de vanilla renombrado.

El nivel depende de lo cerca que estés de una *amatista en gemación*, hasta 12
bloques:

| Nivel | Daño | Golpea cada | Lentitud | Equivale a |
|---|---|---|---|---|
| 1 (borde) | ½ corazón | 2 s | −15 % | Lentitud I |
| 2 | 1 corazón | 1 s | −30 % | Lentitud II |
| 3 | 1½ corazones | 0,5 s | −45 % | Lentitud III |
| 4 (pegado) | 2 corazones | 0,5 s | −60 % | Lentitud IV |

Sin traje, el nivel 4 mata en unos 2,5 segundos. Creativo y espectador son inmunes.

> ⚠️ El daño es de tipo **mágico**, que en vanilla está en la etiqueta
> `bypasses_armor`. **La armadura no protege de la radiación**: solo cuenta el
> número de piezas del traje puestas.

### Traje Hazmat

Cuatro piezas, cada una con **250** de durabilidad. En conjunto dan **17** puntos
de protección (el hierro da 15, el diamante 20).

- Cada pieza puesta anula un **25 %** del daño de radiación. Las cuatro te hacen
  inmune al daño, aunque el efecto sigue activo.
- Una pieza por debajo del **20 %** de durabilidad **deja de proteger** aunque
  siga puesta: es la "brecha" del traje.
- El casco lleva **visor**, que oscurece la pantalla mientras lo llevas.
- **No se repara en yunque** a propósito: el yunque encarece cada reparación y a
  los 40 niveles se planta con "Demasiado caro", lo que dejaría inservible un
  traje pensado para repararse de continuo.

Cuánto aguanta dentro de una geoda antes de dejar de proteger:

| Nivel | Aguanta |
|---|---|
| 1 | 6,7 min |
| 2 | 3,3 min |
| 3 y 4 | 1,7 min |

### Filtros

El **Filtro de Carbón** se usa con clic derecho y devuelve **100** de durabilidad
a la pieza más gastada que lleves puesta. Se puede cambiar *dentro* de la geoda,
que es donde la mecánica tiene gracia.

Los 250 de durabilidad cuadran con esto: al caer al umbral en que deja de
proteger, la pieza lleva 200 puntos de daño, así que **dos filtros la dejan
exactamente nueva** sin desperdiciar nada.

### Aviso en pantalla

Un triángulo abajo a la derecha, **solo en el cliente** (no gasta red ni CPU del
servidor):

- **Amarillo intermitente** por debajo del 30 % de durabilidad
- **Rojo, más rápido** por debajo del 21,5 % — último margen antes de perder la protección

### Mejoras (mesa de herrería)

Las tres se acumulan: una pieza puede llevar las tres a la vez, y la herrería
conserva la durabilidad y los encantamientos.

| Mejora | Item | Efecto |
|---|---|---|
| **Antiveneno** | Colmillo Venenoso | −25 % de daño de veneno **por pieza** (las 4 = inmune) |
| **Visor excelente** | Lente de Mar | El casco deja de oscurecer la pantalla |
| **Amortiguación** | Pata Alada | −25 % de la lentitud de radiación **por pieza** (las 4 = velocidad normal) |

Las tres se montan igual: **dos ingredientes en la mesa de herrería, sin
plantilla**. Y las tres se fabrican antes juntando dos mitades que ninguna sirve
suelta, así que cada mejora obliga a recorrer dos fuentes distintas.

### Drops

Todos **solo si mata un jugador**, para que las granjas automáticas no los
produzcan en masa. Con los pollos importa el doble: una granja los mata por
caída o lava, así que **no da ni un alón**.

| Mob | Suelta | Prob. |
|---|---|---|
| Araña común | Colmillo | 15 % |
| Araña de cueva | Veneno | 15 % |
| Abeja | Miel Cristalizada | 15 % |
| Conejo | Pata Ligera | 20 % |
| Pollo | Alón | 5 % |

El conejo va más alto porque es escaso y huidizo: encontrarlo ya es medio
trabajo. El pollo va más bajo justo por lo contrario — sobra por todas partes,
así que el freno tiene que estar en el drop y no en buscarlo.

### Pesca

El **Espejo de Mar** es lo único del mod que no se fabrica ni lo suelta un mob
al morir: sale pescando.

| Caña | Prob. por picada |
|---|---|
| Sin encantar | 5 % |
| Suerte del Mar I | 7,5 % |
| Suerte del Mar II | 10 % |
| Suerte del Mar III | 12,5 % |

Es el mismo 5 % que vanilla le da a su categoría de tesoro, pero **sin exigir
aguas abiertas**: también pica en una charca bajo tierra, donde el tesoro de
vanilla no sale nunca.

Va en una piscina propia enganchada a la tabla de pesca, así que sale *además*
de lo que pique y no toca en nada las probabilidades de vanilla. Y no usa una
probabilidad plana sino pesos con `quality`, que es la única vía por la que la
suerte del jugador entra en el reparto.

### Recetas

**El traje:**

```
4 Cobre + 3 Panal                    -->  Miel Cristalizada
Miel Cristalizada + 8 Papel          -->  Plantilla de Sellado
5 Oro + 4 Hierro                     -->  Lingote Blindado

HERRERÍA:  Plantilla + Armadura de hierro + Lingote Blindado  -->  Pieza Hazmat
```

**El cartucho:**

```
Carbón             --(horno)-->      Carbón Activado
Carbón Activado + 2 Hierro           -->  Filtro de Carbón
```

**Las tres mejoras.** Cada una junta dos mitades en la herrería, y luego se monta
en la pieza también en la herrería:

```
Colmillo (araña)  + Veneno (araña de cueva)   --(herrería)-->  Colmillo Venenoso
Espejo de Mar (pesca) + Alga Vitrificada      --(herrería)-->  Lente de Mar
Pata Ligera (conejo)  + Alón (pollo)          --(herrería)-->  Pata Alada

Bloque de alga seca  --(horno)-->  Alga Vitrificada

HERRERÍA:  Pieza Hazmat + (Colmillo Venenoso | Lente de Mar | Pata Alada)
```

> El alga parte del **bloque** y no del alga suelta por una razón técnica:
> vanilla ya funde el alga suelta para secarla, y dos recetas de horno con la
> misma entrada se pisan — solo una de las dos sería alcanzable.

Las recetas de herrería a **dos ingredientes** (sin plantilla) son válidas
porque en 26.2 el campo `template` es `Optional` en el códec.

La plantilla **no se puede duplicar**: cada pieza consume la suya. Coste del traje
completo: 40 hierro, 20 oro, 16 cobre, 12 panal, 32 papel.

Y el coste del traje entero con las tres mejoras en las cuatro piezas, matando a
mano: ~27 arañas, ~27 arañas de cueva, ~27 abejas, ~20 conejos, ~80 pollos y
4 espejos pescados.

---

## Hidratación

La segunda mecánica, y la primera que no tiene nada que ver con la radiación:
**el desierto deshidrata**.

Cada jugador lleva **50 puntos** de hidratación y pierde **uno cada 7 segundos**,
así que el depósito lleno da para **5 min 50 s** de sol seguido.

### Solo baja al sol

Hacen falta **tres condiciones a la vez** para que el nivel caiga:

1. Estar en un bioma de **desierto**
2. Tener el **cielo despejado** encima
3. Que sea **de día** y no esté lloviendo

El cielo se mira **desde los ojos y no desde los pies**, así que un bloque a la
altura de la cabeza ya da sombra: es lo que espera quien se cobija.

Lo de "de día" cubre también la lluvia y la tormenta, con dos comprobaciones
separadas — la precipitación por un lado y la oscuridad del cielo por otro,
porque la lluvia normal no oscurece lo suficiente para detectarla solo por brillo.

De aquí sale gratis una consecuencia que vale la pena: **cruzar el desierto de
noche o por la sombra pasa a ser la forma correcta de hacerlo**, que es lo que se
hace en un desierto real. El juego lo premia sin explicarlo en ningún sitio.

Comparado con lo que ya había:

| | Aguanta |
|---|---|
| Traje Hazmat, geoda nivel 1 | 6,7 min |
| Traje Hazmat, geoda nivel 3 y 4 | 1,7 min |
| Hidratación al sol | 5,8 min |

### No se reinicia

Fuera del sol el nivel **se congela**: ni baja ni se rellena. Si te metes a la
sombra con 37, al salir sigues con 37, hayan pasado dos minutos o dos días. Se
guarda pegado al jugador, así que aguanta desconexiones y reinicios del servidor.

Al morir vuelve al máximo, como la comida y la vida. Sin eso, reaparecer seco
sería volver a morir.

Quien no lo tenga aún entra con el depósito lleno, así que activar la mecánica en
un mundo en marcha no deja a nadie tirado.

### El medidor

Una gota celeste centrada, encima del número de experiencia, con una **flecha roja
al lado mientras el nivel está cayendo**.

La flecha distingue lo que la gota sola no puede: **estar seco no es lo mismo que
estarse secando**. A la sombra el medidor se queda quieto, y sin ese aviso el
jugador no sabría si le vale con esperar o tiene que buscar agua ya.

Se ve en dos casos: **dentro del desierto**, donde puede bajar, y **con la
insolación encima**, donde afecta aunque estés fuera. No basta con "has perdido
algo de agua": por encima de la mitad del depósito no hay castigo, así que fuera
del desierto ese medidor solo sería un adorno.

Con la mecánica apagada no se dibuja nada.

> El cliente **no ve la configuración del servidor**: si el HUD la leyera por su
> cuenta, en una partida en red cada jugador leería la suya propia. Por eso el
> interruptor viaja al cliente como dato del jugador, y solo cuando cambia.

Se vacía de arriba abajo. Son 12 píxeles de alto para 50 puntos, o sea que cada
píxel vale unos 4: informa de un vistazo, no al detalle.

> El **degradado no lo pinta el código**. El relleno de la textura es una rampa
> de gris, y como el tinte multiplica, pintarla de un solo celeste conserva la
> rampa sola. Por lo mismo el contorno negro sigue negro con cualquier tinte, y
> una sola imagen sirve para el agua y para el hueco vacío.

Y **no choca con el triángulo del traje**: son dos elementos de HUD distintos,
cada uno con su registro, y viven en sitios opuestos de la pantalla — el aviso
pegado a la esquina inferior derecha y la gota centrada.

### Agua Purificada

Lo que rellena el depósito. Se hace **hirviendo una botella de agua**, en horno o
en fogata:

```
Botella de agua  --(horno o fogata)-->  Agua Purificada
```

Cada botella devuelve **10 puntos**, así que cinco llenan el depósito vacío y
cada una son **1 min 10 s** más de sol.

Se bebe con la animación de siempre y deja la botella vacía, porque el item lleva
los componentes `CONSUMABLE` y `USE_REMAINDER` de vanilla: el trago, el sonido,
las partículas y el vidrio devuelto salen solos.

A diferencia del filtro —que se usa de golpe, porque hay que poder cambiarlo con
la radiación encima— esta **sí hace esperar**: beber en mitad del desierto no es
una urgencia. Y con el depósito lleno no se bebe siquiera: el uso se corta antes
de empezar la animación, para no tirar una botella a la basura.

> La receta acepta **solo la botella de agua**, no cualquier poción. Distinguirlas
> exige un ingrediente por componentes (`fabric:components`), porque todas las
> pociones son el mismo item y solo se diferencian en su contenido.

---

## Insolación

Lo que pasa cuando el depósito baja. Es un efecto registrado propio
(`atalaya:insolacion`), con su icono y su color.

Solo tiene **dos escalones**: uno que avisa y otro que mata. Con un depósito de 50
puntos, más tramos habrían quedado tan cortos que no se distinguirían.

| Nivel | Puntos | Llega a los | Qué hace |
|---|---|---|---|
| **I** | 25 o menos | 2 min 55 s | minería, ataque, movimiento y fuerza **−25 %**; hambre al doble; la vista falla |
| **II** | 0 | 5 min 50 s | lo mismo **+ 1 corazón cada 2 s** |

En el nivel II se muere en **20 segundos** desde vida llena. El daño va como
inanición y no como sequedad porque `starve` está en la etiqueta
`bypasses_armor` y `dry_out` no: morirse de sed con la armadura puesta tiene que
doler igual.

### Depende de los puntos, no del sol

Esta es la diferencia importante con la hidratación. **El sol decide si pierdes
agua; los puntos deciden lo mal que estás.** Meterte a la sombra deja de secarte,
pero no te rehidrata, así que la insolación sigue ahí —de noche, bajo techo y
fuera del desierto— hasta que bebas.

### La vista

Dos cosas a la vez, gobernadas por un solo número de la tabla:

- Un **halo naranja** que cierra la pantalla por los bordes
- Un **mareo suave**, al 35 % del de vanilla

Lo segundo tiene truco. La náusea de vanilla tiene **una sola intensidad**: el
amplificador no la toca, o la pones entera o no la pones, y entera marea de verdad
a bastante gente. Pero esa intensidad no la decide el efecto sino
`getEffectBlendFactor`, que devuelve un 0 a 1 y es lo que consultan el
renderizador y el propio efecto.

Así que la insolación **no aplica la náusea de vanilla**: un mixin de cliente
intercepta ese número y le dice al renderizador que hay un mareo leve. Ventajas:
se gradúa a voluntad, no aparece un icono de Náusea que no viene a cuento, y si el
jugador tiene un mareo auténtico se queda el más fuerte de los dos.

### La tabla

Todos los castigos viven en un bloque, en `InsolacionEffect`:

```
              minería  ataque  movim.  fuerza  hambre  visión  daño
  nivel 0:      0.00    0.00    0.00    0.00    0.0f    0.0f   0.0f
  nivel 1:     -0.25   -0.25   -0.25   -0.25    0.1f    0.5f   0.0f
  nivel 2:     -0.25   -0.25   -0.25   -0.25    0.1f    0.5f   2.0f
```

Cada fila es **el total del nivel**, no lo que añade sobre el anterior. Sale más
largo, pero deja ver la progresión entera de un vistazo y permite aflojar un
castigo en un escalón concreto sin arrastrar a los demás. No cuesta más: el
manager toca los mismos atributos en todos los niveles, poniendo cero donde no hay
castigo.

La fuerza va en **fracción** y no en valor absoluto como la Debilidad de vanilla,
para que el castigo pese lo mismo con la mano vacía que con una espada de
netherita.

> Los castigos no van dentro del efecto. Los modificadores de un `MobEffect`
> escalan de forma lineal sobre *un mismo* atributo, y aquí cada escalón toca
> atributos distintos. El registro sirve para el icono, el nombre y la barra; el
> reparto lo hace quien conoce los puntos exactos.

---

## Lluvia corrosiva

La tercera mecánica: **mojarse cuesta la armadura**. Un efecto propio registrado
(`atalaya:corrosion`) que se come cualquier pieza puesta.

### Funde igual el cuero que la netherita

Quince segundos a la intemperie **derriten una pieza entera**, sin importar de
qué esté hecha:

| Pieza | Durabilidad | Pierde por segundo | Aguanta |
|---|---|---|---|
| Botas de cuero | 65 | 5 | 13 s |
| Casco de oro | 77 | 6 | 13 s |
| Pechera de hierro | 240 | 16 | 15 s |
| Pieza Hazmat | 250 | 17 | 15 s |
| Pechera de diamante | 528 | 36 | 15 s |
| Pechera de netherita | 592 | 40 | 15 s |

El desgaste es **proporcional al máximo de cada pieza**, no una cantidad fija, y
ahí está toda la idea. Con un desgaste plano la netherita aguantaría nueve veces
más que unas botas de cuero, y la lluvia dejaría de dar miedo en cuanto tuvieras
buen equipo. Así **la amenaza no se compra con material**.

Se redondea hacia arriba, así que las piezas baratas caen algo *antes* de los
quince segundos, nunca después.

> ⚠️ El traje Hazmat **no es inmune**. Son 250 de durabilidad, y como no se
> repara en yunque hacen falta **10 filtros de carbón** para recuperar el traje
> entero después de una lluvia. Refugiarse deja de ser opcional.

### Cubrirse basta

Igual que la sombra protege de la insolación: un techo, una cueva o un alero y la
lluvia deja de tocarte.

Se resuelve con `isRainingAt(pos)` de vanilla, que comprueba tres cosas de una
vez: que esté lloviendo, que el jugador vea el cielo desde donde está, y que su
bioma reciba **lluvia**. Ese último detalle sale gratis y viene muy bien: en el
desierto no llueve y en los biomas helados cae nieve, así que **ninguno de los dos
corroe** sin tener que nombrarlos en el código.

### Sin niveles

La radiación mide *lo cerca* que estás y la insolación *lo seco*. Aquí no hay
grados: o te cae encima o no. Un solo escalón dice exactamente eso.

El efecto se pone **aunque no lleves armadura**, para que el aviso llegue antes de
que te juegues nada.

---

## Empapado

La misma lluvia, otro castigo: **la ropa calada pesa**. Un efecto propio
(`atalaya:empapado`) que deja al **50 % de velocidad** mientras te está lloviendo
encima, tanto como una Lentitud IV.

Sin niveles y con el mismo remedio que la corrosión: **cubrirse**.

Va con **interruptor propio** aunque comparta disparador con la corrosión, porque
son mecánicas distintas: una come armadura y la otra frena. Se pueden encender por
separado, y con las dos activas una tormenta hace las dos cosas a la vez.

> Aquí **sí** se usa el modificador del propio efecto, al contrario que en la
> insolación. Esta tiene una sola penalización sobre un solo atributo, que es
> justo para lo que sirve el mecanismo de vanilla; la insolación suma castigos
> distintos en cada escalón y eso el efecto no lo sabe expresar. Además se retira
> sola al quitar el efecto, sin que nadie tenga que acordarse.

Las dos mecánicas de lluvia comparten un solo bucle (`LluviaManager`): la
pregunta *¿te está lloviendo?* se hace una vez por jugador y sirve para ambas.

---

## Frío e hipotermia

La contraparte del desierto. Un **copo de nieve** que se **llena** según te
enfrías, de 0 a **50 puntos**, y a mitad de camino empieza a doler.

Se lee al revés que la gota a propósito: aquella vacía avisa de que falta algo,
este lleno avisa de que sobra. En los dos casos **mucho color es peligro**.

Ocupa **la misma ranura que la gota**, justo encima de los corazones. Los dos
medidores pueden coincidir —se sale de la nieve todavía helado y se entra en un
desierto—, pero eso es la rareza: por cubrirla, el copo estaba antes veinte
píxeles más arriba y quedaba flotando lejos del resto del HUD el resto del
tiempo. Ahora ocupa el sitio bueno y **solo se aparta si la gota está puesta**.

### El frío es el sitio, no el cielo

Aquí está la diferencia de fondo con la hidratación. El desierto solo seca **con
sol**: una sombra, un bloque encima o que se haga de noche te salvan. La nieve no
perdona nada de eso. Da igual que sea de noche, que estés bajo tierra o metido en
una cueva.

La pregunta que se hace no es *"¿en qué bioma estás?"* sino **"¿aquí cuaja la
nieve?"**, que es la que el juego ya sabe responder mirando la temperatura real
del punto.

> Las etiquetas de bioma se probaron primero y dejaban huecos absurdos: un **río
> helado** —con el hielo bajo los pies— no entraba en `IS_SNOWY`, así que se podía
> cruzar a pie sin pasar frío.

Preguntar por la temperatura lo arregla de una vez y cubre el río helado, los
picos, las laderas, la arboleda y el océano congelado, sin ir apuntando biomas a
mano ni volver a esto cada vez que Mojang añada uno.

Y trae dos cosas de propina que encajan justo con la idea:

- **La altura cuenta.** Arriba de una montaña hace frío aunque abajo no.
- **Bajo tierra también.** La temperatura solo baja con la altura, nunca sube al
  enterrarse.

Lo único que lo para es el **calor de verdad**. Se lleva en una **etiqueta de datos**
(`atalaya:fuentes_de_calor`), no escrita en el código, así que un servidor puede
añadir las suyas sin tocar el mod:

> hoguera y hoguera de almas · antorcha y antorcha de almas (también en pared) ·
> farol y farol de almas · fuego y fuego de almas · lava y caldero de lava ·
> bloque de magma · horno, alto horno y ahumador · calabaza iluminada · vela

Y tienen que estar **encendidas**. La etiqueta no sabe expresar eso, así que la
regla va en código y es genérica: cualquier bloque de la lista con estado de
encendido tiene que estarlo. Una hoguera apagada no calienta a nadie, y lo que
añada un servidor mañana se comportará igual sin tocar nada.

Hay que **arrimarse**: cuatro bloques. No basta con tenerla en la misma habitación.

### Los tres ritmos

| | Cada cuánto | De 0 al tope |
|---|---|---|
| Enfriarse a la intemperie | 7 s por punto | 5 min 50 s |
| Deshelarse **solo por irte** | 3 s por punto | 2 min 30 s |
| Deshelarse **junto al fuego** | 1 s por punto | 50 s |

Enfriarse cuesta **lo mismo que secarse en el desierto**: aguantar fuera vale igual
en los dos sitios.

Los otros dos son la parte interesante. Salir de la nieve **tiene** que servir, o
el jugador se sentiría atrapado. Pero si sirviera igual que una hoguera, encenderla
no valdría para nada: **la recompensa de pararse a hacer fuego es justo que va tres
veces más rápido que largarse.**

### Dos niveles

| Puntos | Nivel | Qué pasa |
|---|---|---|
| 0 – 24 | — | Nada |
| 25 – 49 | **1 · aterido** | −25 % a minería, ataque, movimiento y fuerza · hambre doble · la vista falla |
| 50 | **2 · congelándose** | Lo anterior **y 1 corazón cada 2 s** |

Son los **mismos números que la insolación**, y no por pereza: el cuerpo agarrotado
de frío y el cocido por el sol fallan igual.

El daño va como **congelación**, que además de ser lo suyo está en `bypasses_armor`:
morirse de frío con la armadura puesta duele igual.

### La flecha, en los dos sentidos

La hidratación solo necesita una flecha: el nivel baja o se queda quieto. Aquí se
mueve **solo en ambos sentidos**, así que hay dos, y son la misma imagen y su
reflejo para que las dos mecánicas hablen el mismo idioma:

- **Roja hacia arriba** — te estás helando ahora mismo
- **Verde hacia abajo** — estás entrando en calor

Distingue lo que el copo solo no puede: **estar helado no es lo mismo que estarse
helando**. Junto a una hoguera el medidor baja, y sin el aviso no sabrías si te vale
con quedarte quieto o tienes que encender algo ya.

### El medidor no se esconde hasta llegar a 0

Al contrario que la gota, que desaparece al salir del desierto. Allí tiene sentido
—la hidratación se queda quieta fuera, no hay nada que mirar—, pero aquí el frío
**se está yendo solo mientras andas**.

Esconderlo al cruzar la frontera del bioma se leía como que te lo habían quitado de
golpe, cuando en realidad quedaban dos minutos y medio de deshielo. **Ver la cuenta
atrás es la información**: te dice si ya puedes darte la vuelta o todavía no.

### Los dos dibujos

Son distintos a propósito, para que el medidor y el efecto no se confundan:

- **El medidor** es un copo de reja fina con contorno negro, a **17 × 17**. Se
  dibuja al mismo tamaño que su textura, así que cada téxel cae en un píxel de
  interfaz y no hay reescalado.
- **El efecto** es una **estrella maciza de seis puntas**, con el núcleo casi
  blanco y seis tonos escalonados. Va a 18 × 18 y no más: el juego pinta los
  iconos de efecto en un cuadro de ese tamaño, así que una textura mayor se
  remuestrea y sale peor.

Mismo motivo, distinto peso: uno es el indicador y el otro el estado.

### El color va en la textura, no en el tinte

Los dos medidores —la gota y el copo— se pintan dos veces: una con el depósito
entero apagado y otra con la parte llena. El color lo ponía el tinte, que
*multiplica*, y eso ahorra una imagen pero **encierra el degradado en un solo
matiz**: solo puede ir de claro a oscuro del mismo tono. Con un celeste pálido
encima, la diferencia entre la punta y la base no se veía.

Ahora el degradado vive dentro de la imagen y el relleno se tiñe de **blanco**,
que la deja tal cual:

| | Arriba | Abajo |
|---|---|---|
| Gota | `#D6F4FF` | `#2E9CED` — azul de agua |
| Copo | `#F3FDFF` | `#3FC2FF` — cian de hielo |

Los matices se separan a propósito: los dos ocupan **la misma ranura del HUD**,
así que tienen que distinguirse aunque solo se vea uno.

El truco de las dos pasadas sigue en pie, porque el hueco se tiñe de un gris
oscuro que apaga la imagen entera, y el contorno se queda negro —negro por
cualquier tinte sigue siendo negro—.

### La viñeta

El mismo halo de la insolación teñido de **azul hielo** en vez de naranja. La
textura es blanca y el color lo pone el tinte, así que una sola imagen sirve para
los dos. Se llama `vineta.png` a secas: nació como `insolacion_vineta` y ese
nombre decía **para qué** se hizo en vez de **qué** es, así que en cuanto la
hipotermia empezó a usarla se volvió engañoso.

Y es **un solo elemento de HUD** para calor y frío. Los dos efectos pueden coincidir
—se sale de la nieve todavía helado y se entra en un desierto— y pintar los dos
encima sumaría las opacidades hasta cerrar la pantalla. Se dibuja el que más
aprieta.

---

---

## Fulminante

El creeper del desierto, y la primera **entidad** propia del mod. Hereda de
`Creeper` entera —IA, acercarse en silencio, silbido, hincharse, explotar— y solo
cambia cómo se ve y tres números.

Heredar en vez de copiar es deliberado: un creeper lleva media docena de
comportamientos atados entre sí, y reescribirlos para cambiar la piel sería
garantizar que el día que Mojang toque uno, el nuestro se quede atrás.

### El nombre

Un **fulminante** es el pistón detonador, la carga pequeña que enciende la
grande. Y viene del latín *fulmen*, rayo — la misma familia que *fulgur* y de ahí
**fulgurita**, la arena que un rayo funde en vidrio.

> El bicho y lo que deja comparten raíz en el idioma, no porque se haya forzado.

### Los tres números

| | Vanilla | Fulminante |
|---|---|---|
| Mecha | 30 ticks (1,5 s) | **8 ticks (0,4 s)** |
| Velocidad | 0,25 | **0,375** |
| Daño de explosión | — | **×1,25** |

Dos apuntes sobre por qué son esos y no otros:

**La mecha no puede ser 7,5.** Un 75 % más rápido salen 7,5 ticks y el campo es
entero, así que se queda en 8. Es el paso más cercano que existe.

**El +25 % va al golpe, no al radio.** El radio también es entero: de 3 solo se
puede pasar a 4, y eso es un tercio más de radio y bastante más de un cuarto de
daño, porque el daño de una explosión no crece en línea recta con el radio.
Tocando el número del golpe sale el 25 % clavado **y la explosión sigue rompiendo
los mismos bloques** — sube lo que duele, no lo que destroza.

`maxSwell` y `explosionRadius` son privados en `Creeper`; los abre un accesor.

### Cómo se ve

**La piel es el bloque de arena, literalmente.** No es una paleta parecida: se
muestrea el `sand.png` de vanilla y se copia píxel a píxel, repitiendo cada 16
para que el grano sea el mismo y no se note corte entre piezas.

| | Colores | Luminancia |
|---|---|---|
| Bloque de arena | 6 | 187–232 |
| Cuerpo del fulminante | 6 | 187–232 |

Idénticos. **La cara es lo único que no se camufla** — sin ella no sería un
creeper, y es lo único que lo delata cuando está quieto.

Encima lleva **hierba seca**, dos planos cruzados de grosor cero colgados de la
cabeza, así que giran con ella sin escribir una línea. La paleta sale del
`tall_dry_grass.png` de vanilla, y ahí está la gracia: **dos de sus cuatro tonos
son colores del bloque de arena**. Camufla de verdad, no de nombre.

La caja de colisión es la del creeper clavada aunque la mata asome. Si creciera
con ella, chocaría con techos por los que un creeper pasa.

---

## Aturdimiento

Lo que deja la explosión del fulminante a quien alcanza. **30 segundos clavado.**

Se pone cuando la explosión **hace daño de verdad**, no por estar cerca:
cubrirse tras un bloque o llevar buena armadura también libra.

### Qué bloquea

Moverse, saltar, **usar objetos, colocar bloques, pegar, abrir el inventario,
cambiar de ranura, tirar el objeto y cambiar de mano.**

Y dónde se corta cada cosa importa:

- **Usar, colocar y pegar → en el servidor**, con los eventos de interacción de
  Fabric. Bloquear una tecla solo esconde el botón; bloquear la acción la impide.
  Un cliente modificado no se libra.
- **Cambiar de ranura → en `Inventory.setSelectedSlot`.** A la ranura se llega
  por tres caminos —rueda, teclas 1-9 y coger bloque— y los tres acaban ahí.
- **Abrir el inventario → en el cliente**, y ahí no hay alternativa: el
  inventario propio se abre sin preguntarle nada al servidor.

**Escape y el chat siguen funcionando.** Quien está clavado medio minuto tiene
que poder pausar, salir o pedir ayuda.

### Soltarse a pulsaciones

Cada toque de **espacio** descuenta medio segundo. Sin tocar nada son 30 s;
aporreando, unos sesenta toques.

Se cuentan **flancos**, no ticks con la tecla abajo: si valiera tenerla apretada,
bastaría con dejar algo encima del teclado.

La cuenta vive en un dato propio, no en la duración del efecto. La duración de un
`MobEffect` no se puede recortar sin quitarlo y volverlo a poner, y eso
reiniciaría parpadeos y sonidos cada medio segundo.

Y hace falta **un paquete del cliente al servidor**, porque al anular el salto no
hay movimiento que delate la tecla. Solo se manda si de verdad estás aturdido.

### Lo que se ve

Un dibujo de la **barra espaciadora** con dos fotogramas apilados en la misma
imagen —suelta y pulsada—, así que cambiar de uno a otro es mover la V del blit
dieciséis píxeles. Responde en el mismo fotograma en que aprietas. Debajo, el
texto *"Pulsa la tecla espacio"*.

Y **tres estrellas girando** sobre la cabeza. Se mandan desde el servidor, así
que **también las ven los demás**: que se note desde fuera quién está aturdido es
parte de la gracia en un servidor con gente.

---

## Fulgurita

```
Fulminante explota
      ↓  funde la arena del cráter
Arena sospechosa
      ↓  pincel
20 % Fulgurita  /  80 % nada
```

**Es arena sospechosa de vanilla**, no un bloque propio. Lo único que hacía falta
era colgarle otra tabla de botín, y eso se le puede hacer igual al de vanilla —
es exactamente como reparten los pozos del desierto y las pirámides.

### Se siembra después de estallar

Lo natural parecía lo contrario, pero sembrar antes no servía: **la explosión
alcanza lo mismo que el corro donde se ponen los bloques**, así que se los
llevaba casi todos al instante. Y un cráter deja más arena a la vista, no menos —
el suelo y las paredes del hoyo quedan al descubierto.

Solo la superficie con el cielo despejado encima, y **una de cada tres**: una
placa perfecta se leería como algo puesto a mano; un reguero irregular parece un
impacto.

### No sabes si te toca hasta la última pasada

Vanilla enseña el objeto asomando desde el primer cepillazo, y en la arqueología
eso *es* la gracia. Con un botín del 20 % lo estropea: en cuanto asoma ya sabes
si has ganado, y las otras cuatro veces ni te molestas en terminar. La tirada
deja de costar nada.

El cliente lo dibuja porque **le llega en el paquete de sincronización**. Si el
objeto no viaja, no hay nada que enseñar; en el servidor sigue estando y al
acabar cae igual.

**Solo afecta a los bloques que deja el fulminante.** La arqueología de vanilla
se queda tal cual.

### Si la picas, no sale nada

La arena sospechosa de vanilla tiene la tabla de botín vacía. Ese es el castigo
por no traer el pincel.

---

## Criolita — item suelto, sin conectar

En `materiales/criolita.png` queda el dibujo de un mineral que **no está
registrado en el mod**: ni item, ni bloque, ni receta, ni interruptor.

**Qué era.** El material del frío, pensado como pareja de la fulgurita para un
*forro aislante* que frenara la insolación y la hipotermia a la vez. La criolita
es real —del griego *piedra de hielo*, explotada solo en Ivigtut, Groenlandia— y
su papel encajaba solo: es un **fundente**, baja el punto de fusión y hace que el
vidrio fluya. Sin ella la fulgurita no se puede hilar; sin fulgurita ella no
funde nada. Ninguna de las dos sobraba, y eso obligaba a pisar los dos biomas.

**Por qué se quitó.** Se llegó a construir entera —bloque con dos caras según el
interruptor, geoda de hielo con la veta en el suelo, generación por bioma— y se
retiró: el cliente empezó a caerse con crashes nativos sin informe al generar
terreno, y no se pudo descartar la característica de generación.

**Qué se piensa hacer.** Que la suelte una **entidad al morir**, en vez de
generarse en el mundo. Eso evita de raíz el problema —no hay generación que
falle— y encaja mejor con cómo consigue el mod casi todo lo demás: la miel, el
colmillo, el veneno, la pata y el alón salen de matar algo.

Hasta entonces el PNG se queda guardado y nada más.

## El Vigía

El centinela de la atalaya, y el primer bicho del mod **hecho entero a mano**:
malla, textura, animaciones, sonidos y partículas propias. No hereda de ningún
mob de vanilla ni usa nada suyo para verse u oírse.

Alto (2,9 bloques), encorvado, sobre zancos, con brazos que le llegan a las
rodillas y un **farol con un solo ojo** por cabeza. El ojo va en **ámbar** mientras
vigila y en **rojo** en cuanto te tiene.

| | |
|---|---|
| Vida | 60 (30 corazones) |
| Armadura | 8 |
| Daño del cepo | 9 |
| Velocidad | 0,24 patrullando a 0,6 · persiguiendo a ×1,35 |
| Aparece | de noche, en todo el mundo normal, raro y de uno en uno |

### Cómo pelea

| Estado | Qué hace | La salida |
|---|---|---|
| **Vigilar** | Barre el horizonte con el farol, se para a escuchar, mira al cielo | Que no te vea |
| **Alerta** | Al verte se yergue y ruge (1,2 s) | Es el aviso: decide si huir |
| **Persecución** | Bajo, zancadas largas, los brazos estirados agarrando el aire | Corriendo se le saca distancia |
| **Cepo** | Abre los brazos en cruz y los cierra delante: 9 de daño y 1 s atrapado | Medio segundo de anticipación: retroceder dos pasos |
| **Mirada** | De 5 a 24 bloques: carga 2 s y **dispara un rayo** que te marca | Romper la línea de visión al cargar, o apartarse cuando sale |
| **Tambaleo** | Por la espalda recibe +50 % y pierde el turno; corta la mirada | Rodearlo, en equipo |
| **Buscar** | Si te pierde, escudriña a los lados 2,5 s antes de rendirse | Quedarse escondido |

**Marcado** es la maldición: 30 s en los que brillas a través de las paredes y
cada monstruo libre a 24 bloques va a por ti. No tiene niveles ni daño propio —
lo que duele es lo que atrae.

No cabe por un túnel de dos bloques: meterse bajo techo bajo también salva.

### La muerte

Tres segundos propios en vez del tumbado de vanilla: acusa el golpe, cae de
rodillas, alza el farol en una **última mirada** con la garra tendida, el ojo se
encoge y **se apaga**, se desploma y **el farol se le desprende y rueda**. Vanilla
retira el cuerpo a los 20 ticks; aquí se retiene hasta los 60.

Suelta el **Ojo del Vigía** (solo si lo mata un jugador): 8 usos, un minuto de
espera, y hace brillar 10 s a los monstruos a 32 bloques. Además, siempre, 1-3
huesos (más con Botín) y 2-5 pepitas de hierro.

### Todo propio

- **Animaciones:** keyframes de vanilla (el sistema del warden), sin librerías.
  Once: vigilar, acecho, patrulla, persecución, alerta, cepo, mirada,
  tambaleo, buscar y muerte, más la cabeza siguiendo a la presa.
- **Sonidos:** 19 eventos y 27 `.ogg` **sintetizados** por script con lo que el
  bicho lleva encima —el hierro del farol, el cristal, las cadenas, una garganta
  y la llama—. Ninguno es de vanilla.
- **El rayo** es un proyectil propio con malla y renderer propios: núcleo
  incandescente, dos halos cruzados que laten, punta y estela de geometría,
  apuntado a su velocidad como una flecha. Una pared lo para.
- **Partículas:** ocho dibujadas para él (chispa, rayo, maldición, marca,
  zarpa, esquirla, humo y alma). Los efectos de vanilla que pone
  (brillo, lentitud) van sin partículas para que solo se vean las suyas.

Interruptor propio en el panel: **El Vigía**, apagado de fábrica.

### Los generadores

Todo lo del Vigía sale de scripts en `materiales/generadores/`, para poder
retocarlo cambiando un número y regenerar:

| Script | Genera |
|---|---|
| `vigia_tex.py` | la piel y las dos capas de brillo (calma y caza) |
| `vigia_iconos.py` | Ojo del Vigía e icono de Marcado |
| `huevos_jefes.py` | el huevo (junto con los de los tres jefes) |
| `vigia_particulas.py` | las ocho partículas |
| `vigia_rayo_tex.py` | la textura del proyectil |
| `vigia_sonidos.py` | los 27 `.ogg`; el argumento es la carpeta de salida, y su bloque de `sounds.json` se mantiene a mano |
| `vigia_render.py` + `vigia_poster.py` | `materiales/promo/vigia_poster_atalaya.png` |

`vigia_render.py` es un **renderizador 3D por software** (numpy, sin GPU) y acabó
siendo la base de todo el arte del mod: lo usan las fichas, las hojas de
animación, los pósters y los teasers de los jefes. Para el Vigía lleva la malla
**copiada a mano** de `VigiaModel`: si se toca el Java, hay que tocar también el
script. Los jefes ya no tienen ese problema, porque su malla sale de Python.

---

## Los jefes elementales

Cuatro jefes, uno por elemento, cada uno consumido por su maldición. Están
pensados para **un servidor grande en hardcore**: 30-40 jugadores con netherita
entera, Protección IV y manzana de Notch. Con ese equipo, un golpe fuerte quita
3,5 / 5 / 7,5 / 11 corazones según la fase.

Ninguno muere: al final **se libera**, deja una bendición a todo el que esté
cerca y entrega su pieza.

| Jefe | Elemento | Vida | Armadura / dureza | XP | Suelta |
|---|---|---|---|---|---|
| **Nerea**, Guardián de los Mares | agua | 12 500 | 14 / 8 | 300 | Lágrima de Nerea |
| **Aeralis**, la Mariposa del Vendaval | aire | 13 500 | 14 / 8 | 400 | Escama del Vendaval |
| **Rajang**, el Jaguar de Jade | tierra | 15 000 | 16 / 10 | 450 | Colmillo de Jade |
| **Novilis**, el Caballero Solar | fuego | 16 500 | 16 / 10 | 500 | Núcleo Solar |

Las cuatro piezas **todavía no hacen nada**: no tienen receta ni uso. Caen
siempre, sin pedir que mate un jugador, y no se apilan.

### Lo que comparten

No hay clase base. Cada jefe es una clase de unas 1 800 líneas que hereda de
`Monster` y copia y adapta la del anterior. Lo que se repite en los cuatro:

**Solo contra jugadores.** Sus ataques, sus persecuciones y lo que dejan por ahí
(burbujas, ráfagas, pilares...) solo van a por **jugadores** en supervivencia o
aventura, y a por los **maniquíes**, que hacen de jugador en las escenas de prueba
(`PresasJefe.presa`). Ni animales, ni aldeanos, ni otros bichos. Y entre ellos no
se hacen nada: lo de un jefe no le quita vida a otro (`PresasJefe.esJefe`).

**Uno de cada jefe por mundo.** Si ya hay una Nerea, no se puede poner otra
(`JefesUnicos`, guardado con el mundo en `data/atalaya/jefes_unicos.dat`):

- el huevo no la suelta ni se gasta, y dice dónde está la que hay («Solo uno de
  cada jefe: Nerea, Guardián de los Mares ya está en 3, -31»);
- si llega por otro lado (`/summon`, un dispensador), se va en su primer tick con
  el mismo aviso;
- en cuanto muere (ya durante la liberación) o la quitan, se puede poner otra;
- si la que hay está lejos, en un trozo sin cargar, cuenta como viva. Si su trozo
  está cargado y no aparece (la borraron de otra forma), ya no cuenta.

**Nacen dormidos.** Nerea encadenado, Aeralis posada con las alas cerradas,
Rajang tumbado como una esfinge, Novilis de rodilla sobre su espada. Despiertan al ver a un jugador a 40 bloques, o
al recibir un golpe, que no hace daño. Al despertar cuentan los jugadores que hay
a 80 bloques. Ese número **no cambia la vida**: escala cuántos proyectiles salen
y cuánto aguanta lo que hay que romper.

**La vida pasa del tope de vanilla.** `MAX_HEALTH` no puede pasar de 1024, así
que se queda en 1024 y todo el daño que entra se multiplica por `1024 / VIDA`.

**Cuatro fases por la vida que queda**: 75, 50 y 25 %. Solo suben, nunca bajan.
Cada fase:

- acelera los ataques: `ritmo()`, de ×1,0 a ×1,45;
- acorta los enfriamientos y el respiro entre un ataque y otro;
- cambia la piel y el brillo.

El daño de cada ataque es una tabla con un valor por fase. Al cambiar de fase hay
un **tambaleo** de unos 3 s que corta lo que estuviera haciendo.

**La presentación.** Al despertar, cada jugador a menos de 96 bloques ve una
toma de cine (`PresentacionJefe`, todo en el cliente):

- entran **bandas negras** arriba y abajo, con un filo de luz del color del jefe,
  y se esconde el resto del HUD;
- el despertar dura **9,5 s** y los cuatro siguen el mismo guion (cada uno con
  su animación nueva): duerme, abre los ojos, se levanta, muestra su poder y
  ruge. La cámara (`CamaraPresentacionMixin`) corta a una toma distinta en
  cada parte, siguiendo su cabeza y su pecho de verdad:
  1. **dormido**: plano general, alto y de tres cuartos, que se acerca;
  2. **abre los ojos**: primer plano de la cara;
  3. **se levanta**: contrapicado a ras de suelo, de lado, que sube con él;
  4. **su poder**: gira por detrás hasta su costado;
  5. **el grito**: de frente, mirándole a la cara.

  Cada jefe ajusta las distancias a su forma (`PresentacionJefe.Tomas`: las
  alas de Aeralis, Rajang largo y bajo);
- con el rugido sale su **cartel**, en el estilo de los pósters: un destello
  que cruza, el **NOMBRE** que se abre desde el centro, lo que es («JEFE DEL
  FUEGO») y su epíteto con el lema, con el acento grande de su música. Los
  PNG (`presentacion_jefes.py`) vienen en cuatro anchos y se pintan píxel a
  píxel de pantalla, así salen limpios a cualquier resolución;
- tras el grito el jefe sigue **en escena** unos 5 s más
  (`PresasJefe.ESCENA`), quieto y con el cartel, para que se lea;
- al acabar, la cámara vuelve sola a los ojos del jugador, que ya le mira.

Mientras dura no se anda ni se salta, y **no se puede saltar** (Juan quiere que
se vea entera). Durante toda la
presentación el jefe **no golpea**: el grito ya no empuja, no se mueve, no
ataca y no se le hace daño (hasta que la cámara ha vuelto,
`PresasJefe.ESCENA_QUIETO`). Después espera aún 1,5 s antes del primer golpe
(`PresasJefe.RESPIRO_PRESENTACION`).

**Corazones de batalla.** En la batalla, los corazones del jugador son los del
jefe (`CorazonesJefe`, con un mixin en `Hud$HeartType.getSprite`): una gema
roja engastada en un aro de sus colores, que se mueve con su elemento.

| Jefe | Aro | Movimiento |
|---|---|---|
| Nerea | de cian a morado | una ola que baja |
| Aeralis | plata y lila | una ráfaga que cruza |
| Rajang | oro y jade | un pulso lento |
| Novilis | oro quemado | brasas que parpadean |

- Empiezan cuando hay un jefe despierto a menos de 120 bloques (lo mismo que
  saca su barra) y duran **toda la batalla**, aunque el jugador se aleje.
  Acaban cuando el jefe muere; si deja de verse sin morir, se esperan 5
  minutos, y si el jugador vuelve a su sitio y ya no está, se acaban.
- Solo cambian el lleno, el medio y el vacío. El **rojo sigue siendo la vida**;
  los de veneno, congelado, absorción y wither se quedan como en vanilla,
  porque su color avisa de algo. El parpadeo, el temblor y el salto al
  regenerar también son los de vanilla.
- Salen de `corazones_jefes.py` (9 × 9, la silueta de vanilla, animados con
  `.mcmeta`). Se eligió la opción C de tres; `--ficha=carpeta` vuelve a pintar
  las tres sobre fotos del HUD.

**Avisos antes de cada golpe.** Salen de las opiniones de los testers
(07-10-2026: «el giro te pega sin avisar», «no sabía de dónde venían los
golpes»):

- **La alerta «¡!».** Al empezar un ataque peligroso suena desde el jefe un
  sonido común a los cuatro (`jefes/alerta.ogg`, dos campanadas que suben),
  así se aprende una vez y avisa aunque no se esté mirando. Los ataques que
  matan llevan otro (`jefes/alerta_mortal.ogg`, un acorde de metal con el
  «¡!» encima). Salen de `alerta_jefes_sonidos.py`.

  | Jefe | Alerta | Alerta mortal |
  |---|---|---|
  | Nerea | Rompeolas, Remolino, Burbujas, Molino, Arpón, Géiser | Mirada, Gran Marea |
  | Aeralis | Aleteo, Tornados, Marca, Escamas | Picado, Juicio |
  | Rajang | Garra, Terremoto, Rugido, Salto | Cataclismo, Embestida, Tumba, el rugido tras el Sello |
  | Novilis | Barrido, Castigo, Sol, Trompetas, Fuentes | Ofrenda, Dios |

- **Una espera de aviso.** Los golpes que llegaban antes de 0,8 s empiezan
  ahora con el jefe **quieto en el primer fotograma** del ataque mientras sale
  el aviso. La espera va en ticks reales: no se acorta con la fase ni con la
  Furia. Así, del aviso al golpe hay siempre al menos 0,8 s, también en la
  fase IV con Furia.

  | Ataque | Espera | Lo que se ve |
  |---|---|---|
  | Rompeolas (Nerea) | 0,45 s | una **calle roja con flechas** por cada ola, del ancho exacto de la pared de agua (`aviso_calle.py`) |
  | Molino (Nerea) | 0,55 s | el aro sale ya en la espera, **rojo y latiendo**; se pone blanco al empezar a barrer |
  | Garra (Rajang) | 0,55 s | la grieta en la zarpa y el aro donde sale el último pico |
  | Barrido (Novilis) | 0,5 s | un **arco de llamas** en el suelo, hasta donde llega la hoja |
  | Aleteo (Aeralis) | 0,3 s | el viento se le junta alrededor y en la punta de las alas |

  El **Salto** de Rajang, que no avisaba de dónde caía, pinta ahora el aro
  de 6,5 bloques donde va a aterrizar, desde que se agacha.

- **De dónde vino el golpe.** Cualquier daño que venga de algún sitio (jefe,
  mob, flecha) pinta un **arco rojo** alrededor de la mira, girado hacia allí,
  que se apaga en 1,5 s; si te giras, sigue apuntando al sitio
  (`IndicadorGolpe`, con un mixin en `LivingEntity.handleDamageEvent`). La
  textura sale de `indicador_golpe.py`. Se esconde en la presentación.

**Un golpe cooperativo por jefe.** En cada combate hay un momento en que el jefe
es inmune y lo único que sirve es que el grupo rompa algo a la vez:

- a Nerea, los **dos ojos**;
- a Aeralis, los **cuatro núcleos**;
- a Rajang, los **cuatro tótems**;
- a Novilis, las **tres fuentes solares**.

Si sale bien, cae aturdido con **daño doble**. Si sale mal, el castigo es gordo:
los atrapados mueren salvo tótem y el jefe entra en **Furia**: más rápido, más
daño y menos espera, pero solo **30 s** y siendo **inmune**, así que toca esquivar
(`PresasJefe.FURIA_TICKS`). Si lo derriban antes, se acaba antes. Una franja clara
por dentro de su barra, arriba, se va acortando (`FuriaHud`), y la barra de
acción avisa al empezar y al acabar. Antes duraba hasta que lo derribaran, y en
Rajang podían ser minutos (testers, 07-10-2026). Los tótems de Rajang y las fuentes
de Novilis aguantan **10 golpes**, sean cuantos sean los jugadores. Los ojos de
Nerea y los núcleos de Aeralis, desde los testers (07-10-2026), van de **5** (hasta
11 jugadores) a 12 y 10: uno más por cada 6.

**Daño propio.** Cada ataque tiene su tipo de daño en `data/atalaya/damage_type/`.

- Todos llevan `"scaling": "never"`. En hardcore la dificultad es Difícil, y
  vanilla multiplicaría por 1,5 todo lo que pega un monstruo.
- Casi todos van en `no_knockback`, porque el empujón lo da cada ataque a su
  manera.
- Los que **matan salvo tótem** (10 000 de daño) van en todas las etiquetas
  `bypasses_*`: armadura, escudo, encantamientos, efectos y resistencia. Todas
  menos `bypasses_invulnerability`, que es la única que anula el tótem.

**El tótem avisa.** `AvisoTotemMixin` lo anuncia a todo el servidor:
"**Nombre** ha usado un tótem de la inmortalidad", con el icono en el chat. Va
siempre encendido, porque es un aviso y no una mecánica.

**Un templo sin estructura.** El sitio donde aparece es su `centro`, y se queda
atado a él:

- no se aleja más de una correa: 28 / 40 / 40 bloques;
- suelta al objetivo que se vaya a más de 64 / 72 / 72;
- vuelve al centro cuando no tiene a nadie.

No se genera ninguna arena. Lo que levanta Rajang son entidades temporales.

**Persistentes.** No desaparecen por distancia, no cruzan portales, no se empujan
ni se atan. `/kill` los borra **sin liberación ni botín**: es una orden de
administrador, no el final del combate.

**La liberación**, en lugar de la muerte, dura 200 ticks propios en vez de los 20
de vanilla:

| Tick | Qué pasa |
|---|---|
| 1 | suena la liberación |
| 70 (80 en Rajang) | los ojos pasan a oro; piel, brillo y barra de liberado |
| 150 | **bendición de 10 minutos** para todos los jugadores a ±80 bloques |
| 150-160 → 200 | se deshace con la máscara `<jefe>_disolver.png`, el mismo efecto que el dragón del End |
| 200 | estallido final, y se retira |

| Bendición | Efecto |
|---|---|
| de las Mareas (Nerea) | +1,0 de eficiencia en el agua, +0,8 a picar sumergido, el aire se rellena |
| de los Vientos (Aeralis) | +20 % de velocidad, −35 % de gravedad, +7 de caída segura |
| de la Tierra (Rajang) | +6 de armadura, +3 de dureza, +1,0 de resistencia al empuje |
| del Sol (Novilis) | +3 de daño de ataque, y el fuego no prende: te apaga cada tick (y quita la Quemadura al darla) |

**Presencia.** Hay dos cosas, y las lleva `NereaPresencia`, que a pesar del
nombre es compartido por los cuatro jefes:

- **Temblor de cámara.** Lo aplica `TemblorCamaraMixin` en `bobHurt` y respeta la
  opción de accesibilidad "efectos de pantalla". Las ondas en el suelo sacuden la
  cámara solas al nacer.
- **Viñeta de miedo.** Es una por jefe, y la pinta `MiedoHud`: el fondo marino,
  las nubes de tormenta, la selva con grietas de jade y el borde de la pantalla
  que se quema.

**Barra de jefe propia.** No usan la de vanilla: no hay `ServerBossEvent`. Cada
barra lleva:

- marco de 208×26 pintado a mano;
- relleno en grises que se tiñe con el color de la fase y corre en bucle;
- tres muescas que se rompen al 75, 50 y 25 %;
- emblema que tiembla al recibir daño;
- nombre y "FASE I-IV" en letras de píxel;
- rastro blanco del daño.

La de **Aeralis** y la de **Nerea** cambiaron con sus remakes (octubre de 2026).
La de Aeralis mide 240×44, lleva un
marco, un relleno y un emblema por fase con el color ya pintado, un ala que sale
del emblema por encima, el frente del relleno encendido, ojos de tormenta en las
muescas y, debajo, una raya fina que se llena con el **viento de vuelta**. En el
Juicio, en su lugar, lo mismo que Rajang en el Sello: los **cuatro núcleos**
(encendidos los que siguen en pie, partidos los rotos) y la **losa del tiempo**
que le queda al ciclón, roja al final.
La de Nerea, del mismo tamaño: una ola que rompe por encima, el marco de
prismarina con percebes y corales, el corazón de la fase entre costillas y
eslabones en las muescas. En la Mirada cambia de vista: en el emblema, su
**calavera con los dos ojos**, que se rajan con cada impacto, y debajo la **marea**
que baja con el tiempo que le queda al chorro. Con la Furia, todo en verde abismo.
La de Rajang al mismo estilo está **solo en propuesta**
(`rajang_remake_hud.py`, ficha en `materiales/fichas/rajang_barra/`).

La de **Novilis** es del mismo estilo desde el principio: lenguas de fuego que
salen del emblema (su yelmo ante el sol), lava del color de la fase y muescas
que son rayos de sol. Debajo, lo que esté haciendo: los **cuatro ángeles** de
las Trompetas (enteros, rajados o en cascotes) y la melodía que avanza; las
**tres fuentes** y la **carga** de su sol, del oro al rojo; o el **sol** de la
Ofrenda con lo que lleva el atrapado. Los ángeles se ven mientras suene la
melodía (no solo mientras los llama), y junto a los ángeles y las fuentes va la
cuenta: «Rotas 1/4». Con la Furia, todo en fuego azul; con el
Grito de guerra, un cuerno carmesí junto al rótulo.

Las barras **se apilan**: Nerea arriba, Aeralis debajo, Rajang debajo de las
dos y Novilis la última (cada una usa el `ALTO` de las de encima). Cada una enseña el jefe despierto
más cercano.

**Lo que se ve y lo que pega van juntos.** `<Jefe>Geometria.java` guarda los ticks
de cada golpe y los puntos del cuerpo (ojos, manos, puntas). Se genera desde las
mismas poses que las animaciones, y `ritmo()` da el mismo número en el servidor y
en el cliente.

**Sin paquetes propios.** Todo viaja por `SynchedEntityData` (estado, fase,
objetivo…), por partículas y por sonidos. El cliente arranca la animación al ver
cambiar el estado. Para pasar datos se usa la velocidad de las partículas, con
`count 0`: el radio y el temblor de una onda, o la duración de una marca.

**Todo propio:** malla, pieles por fase, animaciones horneadas en keyframes de
vanilla, partículas, sonidos sintetizados, barra, iconos y huevo. Nada sale de
vanilla.

**Música propia.** Cada uno tiene la suya mientras pelea cerca (a menos de 96
bloques): Nerea, el mar; Aeralis, la tormenta; Rajang, la tierra; Novilis, la
fragua (yunques, taikos, coro y metales en fa menor). La compone
`musica_jefes.py` (`sounds/musica/`), la pone `MusicaJefes` en el cliente, en la
categoría de **ambiente** (no en la de música: con la música baja o quitada se
quedaban sin ella), y entra y sale fundiéndose. Mientras suena, la de vanilla
calla (`MusicaJefesMixin`); al liberarlo, se apaga.

Cada jefe tiene un comando para probarlo por partes: `/atalaya <jefe> <orden>`
(ver [Comandos](#comandos)).

### Nerea, Guardián de los Mares

> *Rompe sus cadenas. Libera su corazón.*

Un gigante de hueso y prismarina. Desde el **remake de octubre de 2026** mide
unos **15 bloques** (antes, 10):

- cráneo con corona de coral, y detrás una **venera** de nácar con su perla;
- barba y capa de algas, espinas de hueso en el lomo y una caracola de hombrera;
- en el pecho, una cavidad cerrada por costillas, con el **corazón maldito**
  dentro y cuatro cadenas oxidadas cruzándolo;
- en la derecha, el tridente, más largo y con una espiral de espuma;
- en la izquierda, una cadena-látigo con un **ancla** (antes, un gancho de hueso).

Con cada fase salta una cadena y el corazón se raja y se apaga. En la IV las
costillas se abren.

Se dibujaron tres versiones:

- **A, "El Guardián Ahogado"**, el de las referencias;
- **B, "La Marea Encadenada"**, una armadura de buzo llena de mar, sin piernas;
- **C, "La Leyenda de las Mareas"**, una deidad con cola de serpiente.

Ganó la A.

| | |
|---|---|
| Vida | 12 500 · armadura 14, dureza 8 |
| Caja | 5,1 × 13,2. A propósito, más estrecha que los hombros y más baja que la corona: tiene que tapar el cuerpo, no cada rama |
| Velocidad | 0,27, menos que un jugador andando; ×1,3 en la fase IV; ×1,1 con la Furia |
| Correa | 28 bloques |

| Fase | Vida | Ritmo | Qué se añade |
|---|---|---|---|
| I | 100-75 % | ×1,0 | Rompeolas (1 ola), Remolino, Burbujas bomba |
| II | 75-50 % | ×1,12 | Molino de anclas, Arpón, **Géiser del Abismo**, **Canto de Sirena**, **Encadenados**; el Rompeolas lanza 3 olas |
| III | 50-25 % | ×1,25 | Mirada del Abismo, **Gran Marea**, **Marea Alta**; Rompeolas de 5 olas; un ancla más |
| IV | 25-0 % | ×1,4 | las costillas se abren; cada 25 s cae **agotado** (daño doble) |

Los ojos van de cian a violeta, a magenta y a rojo.

Todo lo que hace **se ve de mar**: paredes de agua, remolinos en el suelo,
géiseres, espuma y burbujas. Nada de chispas ni rayos: eso es de los otros.

El daño de cada ataque va en el orden de las fases, I / II / III / IV:

| Ataque | Qué hace | Daño | Cómo se sale |
|---|---|---|---|
| **Rompeolas** | clava el tridente y lanza **paredes de agua** en abanico, a ras de suelo, hasta 34 bloques | 44 / 55 / 69 / 91 | apartarse de la línea, o el escudo. **Saltar no vale** |
| **Remolino** | 4,4 s tirando de todo hacia él, con un remolino de 26 bloques en el suelo; deja **Corriente Abismal** (−20 % de velocidad por nivel) | 7 / 10 / 14 / 21 por segundo, atraviesa la armadura | **llevar una antorcha** en la mano: hace inmune (se ve una burbuja de aire dorada) |
| **Burbujas bomba** | una por jugador, hasta 40; salen del corazón (que se ve dentro), persiguen y explotan en 5,5-7,75 bloques; un aro de espuma marca hasta dónde | 36 / 48 / 58 / 72, cuenta como explosión | **cualquier proyectil** la pincha sin daño (su caja mide 1,4; antes 0,9, y costaba acertar). De un espadazo te explota encima |
| **Molino de anclas** | dos cadenas de 21 bloques con un ancla al final dan dos vueltas; un aro de espuma marca hasta dónde llegan | 48 / 58 / 72, el escudo no la para | **saltarla**, pegarse a sus pies o irse lejos |
| **Arpón** | un ancla por cada 10 jugadores (hasta 5) a los más lejanos, con estela y un aro bajo el blanco; los arrastra hasta el tridente y remata con la Estocada | 48 / 58 / 72, y la estocada 55 / 69 / 91 | escudo de cara al ancla, o romper la línea de visión |
| **Géiser del Abismo** | desde la II. Clava el tridente y bajo cada jugador se abre un remolino oscuro; a los 1,5 s revienta una columna de agua de 14 bloques que lanza a unos 12 (y la caída duele) | 36 / 44 / 58 | **salir del remolino** a tiempo |
| **Gran Marea** | desde la III. Alza el tridente 2 s y una ola de 9 bloques cruza la arena de lado a lado (80 bloques) hacia donde hay más gente. Solo deja **un hueco** de 5 bloques, marcado antes en el suelo | **mata** (10 000) y arrastra: solo salva un tótem | correr al **hueco** o ponerse detrás de ella |
| **Mirada del Abismo** | carga 4 s un chorro de agua del abismo desde cada ojo hacia **la mitad** de los que pelean (de 30, 15): los de menos vida que tiene a la vista | **mata** (10 000): solo salva un tótem | **esconderse tras un bloque** o **romperle los dos ojos** a flechazos: **5 impactos** cada uno hasta 11 jugadores, uno más por cada 6 (de 30, 9), hasta 12. Así cae aturdida, con daño doble |

**Mecánicas cooperativas (octubre de 2026).** Juan: «que cada jefe haga cooperar a
los jugadores con mecánicas suyas, que los otros no tengan». De la ficha
(`nerea_mecanicas_escenas.py`) eligió tres; las tres afectan a **un tercio** de los
que pelean (con dos, a uno o a la pareja; jugando solo, a ti):

| Mecánica | Qué hace | Daño | Cómo se sale |
|---|---|---|---|
| **Canto de Sirena** (II) | abre los brazos y canta 8 s (sin rayo: las notas le salen de la boca). Los **más lejanos** caen en **trance**: andan solos hacia ella, no pueden atacar, la pantalla se les tuerce (náusea) y pierden vida cada segundo. Mientras canta, **no se le puede pegar** | 3 / 3 / 4 / 5 por segundo, pasa la armadura | **darle clics** al hechizado: cada clic de un compañero vale 3 de los 12 que hacen falta (no le hace daño). El hechizado también puede hacer clic (al aire vale), pero cada uno vale 1. `TranceSirena`, con un mixin en el clic izquierdo (`TranceClicMixin`) |
| **Encadenados** (II) | lanza sus cadenas: ata por parejas durante 15 s (el que sobra, o si juegas solo, a un **ancla** clavada en el suelo). Una cadena de eslabones con un hilo de agua que se pone **rojo** al tensarse (`CadenaNereaEntity`) | si se separan más de **10 bloques**, tirón que los junta y 10 / 10 / 12 / 14 a cada uno (como mucho uno por segundo) | moverse **con tu pareja**, esquivando a la vez lo que siga lanzando |
| **Marea Alta** (III) | alza el tridente 10 s: salen **cúpulas de refugio** celestes (`RefugioNereaEntity`, Juan: «celeste y como una cúpula») repartidas por la arena, las justas: una por cada 2 jugadores (3 con más de 8, 4 con más de 24). Encima de cada una, cuántos caben («1/2»; roja si está llena). Cuenta atrás en la barra de acción | al acabar, a quien no esté en una cúpula con sitio, **la muerte salvo tótem** | **repartirse**: si entra uno de más, ese no está a salvo (cuentan los primeros en entrar) |

Cada una lleva su alerta «¡!» (la Marea Alta, la mortal) y su pista en la barra de
acción la primera vez. Sonidos de `nerea_cooperativas_sonidos.py` (el canto es una
vocalización de sirena de 8 s en re menor con una segunda voz y el coro del
abismo); la textura de la cúpula, de `nerea_cupula.py`; las animaciones (CANTO,
MAREA_ALTA, ENCADENAR), de `nerea_juego_anim.py`.

Mientras mira es inmune, y romper un solo ojo no salva: el disparo sale del punto
medio entre los dos. Cada ojo lleva un aro de agua que gira y se va rajando con
los impactos. Al empezar, a todos los que pelean les sale en la barra de acción
cómo pararla («¡Rómpele los dos ojos a flechazos o escóndete tras un bloque!») y
bajo el emblema de su barra se cuentan los impactos de cada ojo («3/5  0/5»).

**Respiro.** Tras un ataque fuerte (Remolino, Molino, Mirada, Géiser, Gran
Marea) espera al menos 2 s antes del siguiente, y nunca encadena dos ataques de
área seguidos (Rompeolas, Remolino, Molino, Géiser, Gran Marea) si tiene otro a
mano. Antes, tras el Molino podía salir el Rompeolas de 3 olas casi a la vez.

**Furia de las Mareas.** Si la Mirada sale (no le rompen los ojos a tiempo), entra
en Furia: un aura de luz bajo el agua (cáusticas en verde abismo) y burbujas que
le suben por el cuerpo. Ataques un 25 % más rápidos (menos la Mirada), un 35 % más
de daño y un 35 % menos de espera. Dura **30 s** y mientras es inmune; se le
quita antes al **derribarla**: romperle los dos ojos en otra Mirada.

### Aeralis, la Mariposa del Vendaval

> *Calma la tormenta. Apaga el ojo de su pecho.*

Una polilla de tormenta erguida. Desde el **remake de octubre de 2026** mide
unos 24 bloques de alto y **38 de envergadura** (antes, 17 y 22):

- alas de tormenta, oscuras junto al cuerpo y claras hacia fuera, con ocelos de
  ciclón y el filo encendido en el color de la fase; la costa de cada ala es una
  vara de quitina;
- un halo de viento detrás de la espalda que gira;
- corona de siete púas, colmillos largos y antenas de pluma hacia atrás;
- melena de nubes en el cuello;
- patas de delante de presa, como una mantis;
- abdomen con juntas que brillan y cuatro cintas de viento (con física).

En el pecho lleva el **ojo de la tormenta**, con un marco de ocho púas, que gira
más deprisa en cada fase. Cuando se posa o cae, cierra las alas hacia arriba.

La malla sale de `vendaval_juego.py`; la de antes del remake está en
`vendaval_juego_v1.py` (la usa la ficha para el «antes»).

Se dibujaron tres versiones:

- **A, "Mariposa del Vendaval"**;
- **B, "Dragón mariposa"**;
- **C, "Polilla de rayos"**.

B y C salen de imágenes de referencia. Ganó la A.

**Vuela.** No tiene gravedad ni choques: con 22 bloques de alas, chocar con cada
árbol la frenaría.

- Va a unos 7,5 bloques del suelo (con 38 de alas, más bajo las arrastraba).
- Rodea al objetivo a 12 bloques y de vez en cuando hace una pasada rasante.
- Las alas no tienen caja de golpe, así que se le pega al cuerpo, sobre todo con
  arcos, ballestas y tridentes.
- Desde la III solo baja al alcance de la espada cuando está aturdida, agotada,
  **posada** después del Picado o en la **pasada rasante**: en todas las fases
  pasa a 2 bloques del suelo y, encima de su blanco, **planea 1 s** casi
  parada. No hace daño: es la ventana de la espada (testers, 07-10-2026).
  Se fuerza con `/atalaya aeralis rasante`.

| | |
|---|---|
| Vida | 13 500 · armadura 14, dureza 8 |
| Caja | 3,6 × 10, solo el cuerpo |
| Correa | 40 bloques |

**El viento se mete por las juntas.** Las cuchillas, los estallidos y las ráfagas
pegan hasta un **30 % más** cuanta más armadura lleves (`contraArmadura`). Rajang
lo heredó.

| Fase | Nombre | Color | Qué se añade |
|---|---|---|---|
| I | Brisa | cian | Aleteo Cortante, Tornados |
| II | Ráfaga | añil | la Cacería del Vendaval, el Picado; el viento de vuelta |
| III | Tempestad | violeta | Juicio del Ciclón, Escamas de Tormenta; rayos en las alas y truenos |
| IV | Ojo de la tormenta | magenta | todo más seguido; cada 25 s cae **agotada** (daño doble) |

| Ataque | Qué hace | Daño | Cómo se sale |
|---|---|---|---|
| **Aleteo Cortante** | de 3 a 10 cuchillas de viento en abanico, alternando **azules** a ras de suelo (hasta media pierna) y **blancas** a la altura de la cabeza; la del centro, blanca, va derecha al blanco | 31 / 39 / 49 / 61 | **saltar las azules y agacharse ante las blancas**: de pie (o saltando) te dan; agachado pasan por encima. El escudo la para de frente |
| **Tornados** | de 3 a 9 tornados que nacen junto a los jugadores y los persiguen 12 s. Atrapan, suben en espiral y revientan a los 3 s | 7 / 10 / 14 / 21 por segundo, más el estallido: 27 / 37 / 44 / 55 | **3 golpes** de lo que sea lo deshacen y sueltan a la víctima con suavidad, pero **la caída duele** |
| **Cacería del Vendaval** | marca a una presa 15 s y le tira ráfagas que la persiguen. La marca no se quita: si la leche la borra, vuelve. Si nadie se queda cerca de la presa, acelera | 34 / 42 / 53 / 70, explota en 3,5 bloques | **reventar la ráfaga** en el aire (1 + jugadores/12 golpes) o ponerse delante |
| **Juicio del Ciclón** | sale poco, como el Sello de Rajang: el primero **nada más entrar en la III** (al acabar el tambaleo) y luego no vuelve hasta 1,5 min después de acabar (1,3 en la IV). Se hace el silencio (corta todos sus sonidos) y sube al centro. **Un solo ciclón** atrapa a **un tercio de los que pelean** (los de menos vida: de 30, 10; redondea hacia arriba), los arrastra hasta él y aparecen **cuatro núcleos que giran alrededor del ciclón**, despacio y a la altura de los atrapados | si no los rompen: a cada atrapado, **la muerte salvo tótem** (y luego la caída); a quien esté a 8 bloques, 70 / 70 / 70 / 87, menos un 25 % por núcleo roto; y ella entra en la **Furia del Vendaval** | **romper los cuatro núcleos**: los atrapados, a espadazos cuando les pasan al lado; los de fuera, a flechazos. Aguantan **5 golpes** hasta 11 jugadores, uno más por cada 6, hasta 10. Así cae aturdida 5 s, con daño doble |
| **Picado del Vendaval** (nuevo) | sube y marca en el suelo la línea por donde se va a lanzar (36 a 60 bloques, galones que se encienden). Se lanza en picado a 45 bloques/s | a quien pille, **la muerte salvo tótem** (pasa armadura, escudo, encantamientos y efectos) y lo **lanza al cielo** (unos 24 bloques): la caída duele | **salir de la línea**. Al final **se posa 5 s** y recibe **daño doble**: la ventana de la espada |
| **Escamas de Tormenta** (nuevo) | sacude las alas y suelta escamas en un círculo de 15 bloques. Cada mancha se carga y descarga cada 1,5 s durante 6 s | 20 / 20 / 20 / 28 por descarga y **Parálisis 2 s**: ni andar ni saltar, pero sí pegar, el inventario y usar objetos. No te vuelve a paralizar hasta 1 s después de soltarte, para que puedas salir de la mancha | **no pisar las manchas** mientras brillan |
| **Viento de vuelta** (nuevo) | desde la fase II, cada tornado roto le devuelve su viento: un orbe de luz que vuela a su pecho. Una raya bajo su barra lo cuenta, con la cifra al lado («Viento 3/6»): con **dos tandas de tornados rotas** (6 en grupos pequeños, 8 en la IV; sube con el grupo) **cae aturdida 10 s** con daño doble (el doble que tras el Juicio; mientras, se retuerce en el suelo), con un trueno y el aviso en la barra de acción (se le corta lo que hacía; en el Juicio, el suelo o el Picado espera a acabar) | ninguno | **romper tornados** |

Mientras dura el Juicio es inmune.

**Pistas.** La primera vez que hace cada cosa, la barra de acción dice cómo se
sale: el Aleteo («Cuchillas azules: ¡salta! · Blancas: ¡agáchate!»), los
tornados desde la II (cuántos rotos la derriban) y el Juicio (dónde están los
núcleos y cómo se rompen). Salen de las opiniones de los testers (07-10-2026):
el aturdimiento por tornados casi no se notaba y el Juicio, jugando solo, no
tenía salida.

**La Furia del Vendaval.** Es la Furia de Jade de Rajang en Aeralis: si el
Juicio sale mal, a los que queden se la encuentran con un aura de rayos violetas
en zigzag que le corren por encima (`AeralisFuriaLayer`). No usa la capa del
creeper como Rajang, porque sus alas son láminas recortadas y esa capa pintaba
rectángulos: va sobre el mismo atlas que su piel, en cuatro cuadros que se
alternan. Con la Furia ataca un 25 % más rápido, pega un 35 % más, espera un 35 %
menos entre ataques y vuela un 10 % más deprisa; en la barra, el rótulo dice
FURIA y la tormenta late. Dura **30 s** y mientras es inmune; **se le va antes
si la derriban**: los cuatro núcleos de otro Juicio o el viento de vuelta lleno.

**En todos sus ataques la caída duele.** Antes, el tornado roto y el Juicio
dejaban caer a la víctima sin daño; ahora la caída cuenta desde donde te suelta o
desde lo más alto al que te lanza (el Picado, el estallido del tornado, el
Juicio, las cuchillas altas). En Rajang ya era así: ningún ataque quita el daño
de caída; solo las plataformas del Sello, al bajar, no dejan que te rompas las
piernas.

**Cómo se ven los ataques desde el remake.** Las cuchillas del Aleteo son medias
lunas grandes: las bajas del color de la fase y las altas blancas. Los tornados
tienen embudo de aire (no una red) en el color de la fase, el aro del suelo hasta
donde atrapan y tres anillos de luz, uno por golpe que les falta; desde la III
llevan rayos dentro. Las ráfagas de la Cacería son polillas de viento. Los
núcleos del Juicio son cristales de ocho caras con una columna de luz que sube y
un rayo que los ata a su pecho. La Marca del Vendaval tiene icono de polilla.

### Rajang, el Jaguar de Jade

> *Resiste el cataclismo. Arranca la raíz de su pecho.*

Un dientes de sable colosal, tallado en jade y oro por un pueblo que ya no existe:

- unos 8 bloques hasta la cruz y 25 de largo con la cola;
- sables de 2 bloques y rosetas de jaguar;
- máscara y hombreras de oro con grecas;
- una cresta de cristales que **crecen en cada fase**;
- un **sol de jade** en el pecho, tapado por un peto de oro que **revienta en la
  fase IV**.

Las grietas de la maldición nacen del sol y se extienden por el cuerpo fase a
fase.

**El primer jefe que corre.** Anda y galopa a cuatro patas. Mezcla el paso y el
galope según la velocidad, con relojes que avanzan al ritmo del suelo para que
las zarpas no resbalen. Lo que corre cada zarpa al apoyar lo mide
`rajang_juego_anim.py` y lo deja en `RajangGeometria` (`ZANCADA_ANDAR`,
`ZANCADA_CORRER`), así que tocar una animación no hace patinar los pies. El galope
está hecho para 1 bloque/tick y él va a 0,86, así que su reloj nunca baja del 80 %
(a la mitad se veía pesado); las zarpas resbalan un poco. Lo que hace depende de
lo lejos que esté su objetivo:

- a más de 10 bloques, galopa: unos 17 bloques/s (20 en la fase IV);
- entre 6 y 10, lo acecha a paso vivo y largo, a unos 6,5 bloques/s;
- a menos de 6, se planta.

El paso es el **lateral** de los felinos de verdad: atrás izquierda, delante
izquierda, atrás derecha, delante derecha. Lleva la cabeza baja de acecho, y los
hombros suben y bajan con cada mano. El galope es rotatorio y tiene tiempo en el
aire.

**Varias cajas de golpe.** Con 17 bloques de largo, una sola caja o deja la
cabeza fuera o le ocupa media plaza. Por eso la caja principal tapa el pecho y
las patas delanteras, y la cabeza y la grupa llevan cajas propias
(`RajangParteEntity`) que le pasan el daño. La de la grupa va **del suelo al
lomo** y tapa también las patas de atrás: antes empezaba a 3,75 bloques y por
detrás, a la altura de las patas, no se le daba (testers, 07-10-2026).

| | |
|---|---|
| Vida | 15 000 · armadura 16, dureza 10 |
| Caja | 6 × 7,6, más la cabeza (3,6) y la grupa (5 × 8,6, desde el suelo) |
| Correa | 40 bloques |

| Fase | Nombre | Qué se añade |
|---|---|---|
| I | Selva | Garra Terrestre, Terremoto Ancestral, **Embestida de Jade** |
| II | Grieta | Sello de la Tierra, **Tumba de Raíces**, **Ídolo de Oro** |
| III | Raíz | Cataclismo de Jade |
| IV | Corazón | el peto revienta; **Salto**; el Cataclismo vuelve antes |

Desde la prueba de octubre de 2026, en las fases II, III y IV pega un 8, un 12 y
un 15 % más, ataca más rápido (`ritmo()` ×1,22, ×1,4 y ×1,56) y espera menos
entre un ataque y otro (enfriamientos ×0,84, ×0,72 y ×0,6).

| Ataque | Qué hace | Daño | Cómo se sale |
|---|---|---|---|
| **Garra Terrestre** | zarpazo en abanico de 125° que te **empuja unos 6 bloques** y una fila de picos de roca que corre hasta la presa. La avisan una grieta y un hexágono. Cada pico te **lanza unos 10 bloques** y te deja el **Peso 3 s** | 34 / 45 / 59 / 80 | salir del frente y del hexágono. El escudo para el zarpazo |
| **Terremoto Ancestral** | golpea con las dos zarpas: **Peso de la Tierra** 8 s a 40 bloques (−35 % de velocidad, −50 % de salto) y pilares bajo los jugadores (pegan a 2,5–3,2 bloques de su centro), que **lanzan unos 10 bloques** y dejan el Peso 3 s. Él se cubre de **Piel de Jade** 10 s (−40 % de daño) | pilares 27 / 40 / 49 / 63 | apartarse del hexágono y no pegarle con la Piel puesta |
| **Embestida de Jade** | va a por el jugador **más lejano** que tenga a tiro (de 10 a 36 bloques, con camino libre): los arqueros de lejos salían casi ilesos. Se agazapa y rasca el suelo mientras una **flecha** en el suelo marca por dónde va a cargar (1,15 s en la fase I, 0,75 s en la IV; al llenarse, el rumbo queda fijo). Carga a 26 bloques/s y **se pasa de largo otro tanto**: la flecha mide el doble de lo que hay hasta la presa (24 a 72 bloques, sin salir de 64 de su sitio). A su paso revientan **pinchos a 4,2 bloques de cada lado**. Su cuerpo y los pinchos **matan** y te lanzan unos **15 bloques**. Frena derrapando y jadea 1 s | **mata** (solo salva un tótem) | apartarse unos 7 bloques de la flecha (la franja mortal mide unos 13 de ancho) o ponerse tras un muro: si choca, **se estampa** y queda 2 s aturdido con daño doble |
| **Sello de la Tierra** | ruge y levanta **cuatro columnas de 26 bloques**, cada una con una escalera de piedras en espiral y un **tótem** arriba. Dura 45 s, y él es inmune. Cada 1,5 s **tiembla un escalón** (1 s), se cae y vuelve a los 3 s. Al romperse cada tótem, un **pulso de tierra** pega y te echa de la columna en horizontal | pulso 27 / 40 / 49 / 63 | **subir y romper los cuatro tótems** (**10 golpes** cada uno): cae aturdido 6 s con daño doble y nadie se hace daño al caer. Si no, el **Rugido de Jade** mata a todo lo vivo a unos 64 bloques (solo salva un tótem) y le deja la **Furia** |
| **Tumba de Raíces** | clava las garras y ruge contra el suelo. Un **círculo de 36 bloques** se llena desde él en **6 s**, siempre igual, con un segundo rugido a mitad, en cualquier fase. Es inmune mientras carga. **Una de cada dos va en anillo** (la segunda, la cuarta...): ruge más agudo, las flechas del borde apuntan hacia dentro, alrededor de él brilla un **círculo dorado de 10 bloques** y lo llenado avanza **del borde hacia él** | al llenarse, **mata** a todo lo que siga dentro (solo salva un tótem) y deja el Peso 5 s. En anillo, a quien esté fuera del círculo dorado | **en anillo, correr hacia él** y meterse en el dorado (desde el borde llegas igual que huyendo de la otra). En círculo, salir: desde el cuerpo a cuerpo hay que correr unos 32 bloques: esprintando sobran 0,3 s, y saltando al esprintar 1,5; quien dude más no llega. El círculo lo pinta su renderer, no una partícula, para que no desaparezca al mirar hacia fuera. No sale hasta 8 s después de un Terremoto, porque con su Peso nadie llegaría |
| **Cataclismo de Jade** | ruge al cielo y llueven **seis oleadas** de fragmentos grandes (×2,3 a ×2,7): uno sobre cada jugador y unos pocos al azar, con una marca que cuenta atrás 1,2 s (es de reflejos) | dentro de su marca (4,8 a 5,7 bloques): **mata**; fuera de la marca, nada | apartarse de la marca y separarse del grupo. Si muere alguien, él se cura un 5 %. Si no muere nadie, queda **paralizado** 10 s con daño doble |
| **Salto** (fase IV) | salta en parábola sobre el jugador **más lejano** a tiro (de 8 a 26 bloques); un aro marca dónde cae | 80 en 6,5 bloques | apartarse cuando despega |
| **Ídolo de Oro** (II, mecánica cooperativa de octubre de 2026) | ruge, arranca un **ídolo de oro** de su templo y lo lanza a un lado de la arena; al otro sale un **altar dorado** (columna de luz y aro). Quien lo recoge lo lleva (va más lento y brilla) y Rajang **solo persigue al portador**, al galope, sin otros ataques. Si está tirado, va a por él. 25 s | si alcanza al portador: zarpazo de 24 / 30 / 34 / 42, **recupera el ídolo y se cura un 3 %**; si lo recoge del suelo, también se cura | **llevarlo al altar**: revienta, le quita **un 5 % de vida** y cae **aturdido** con daño doble. Se pasa de mano en mano: **Q** para soltarlo o **un clic a un compañero** para dárselo (sin hacerle daño). El ídolo es un objeto de verdad (`IdoloOroItem`, textura de `idolo_oro.py`) que se deshace si ya no lo busca su Rajang |

**Las columnas del Sello son entidades, no bloques.** Son pisables a cualquier
altura gracias a un truco: el juego solo busca choques con entidades cuyo origen
esté a unos 4 bloques por debajo de quien se mueve, así que la columna crea
tramos invisibles apilados.

Un tótem roto se queda roto, y después de cada Sello hay 2 minutos de descanso.
Las tres piedras de abajo de cada espiral no caen nunca, y en cada columna se
cae como mucho una a la vez. Como cada piedra está un bloque más alta que la
anterior, si falta una el salto siguiente es de dos: toca esperar a que vuelva.

**La Furia de Jade.** Si el Sello falla, a los que sobrevivan al Rugido de Jade
se lo encuentran con un aura verde: la misma malla un poco hinchada con bandas
que le corren despacio por encima, como la carga del creeper pero a un quinto de
su velocidad (`RajangFuriaLayer`, sobre la capa de vanilla). Con la Furia:

- ataca un 25 % más rápido;
- pega un 35 % más en todo lo que no sea ya mortal;
- espera un 35 % menos entre ataques, y la mitad entre uno y otro;
- corre un 15 % más.

Le dura **30 s** y mientras es **inmune**: solo toca esquivar (antes, hasta que lo
derribaran). Un Sello superado o un Cataclismo sin muertes se la quitan antes. En
Furia persigue al jugador **más lejano** y la Garra va a por él: que el arquero
sienta el miedo. En la barra, el rótulo pasa a **FURIA** y la energía late en verde
vivo.

**Pistas.** La primera Tumba de cada tipo avisa en la barra de acción: «¡Sal del
círculo de raíces antes de que se llene!» o «¡Anillo de raíces! Corre hacia él: el
círculo dorado es seguro».

> Estas mejoras salen de las pruebas del grupo de octubre de 2026 («tosco y
> lento»). La ficha con los renders y las cifras está en
> `materiales/fichas/rajang_mejoras/`, con las hojas de control de las
> animaciones de antes y de después.

### Novilis, el Caballero Solar

> *Rompe sus fuentes. Apaga su sol.*

Un guerrero de leyenda con una armadura forjada en lava, que trae **su propio
sol** flotando sobre él y saca de él su poder:

- **16 bloques hasta el yelmo** y 18 con el halo;
- yelmo con **cuernos** y una **corona de púas** de oro, y detrás un **halo** de
  rayos que gira y late;
- hombreras por capas con aletas, peto en V, gola alta, tabardo y capa doble;
- una espada de fuego tan larga como medio cuerpo.

Las grietas de lava crecen fase a fase. Nace **de rodilla**, con la espada
clavada delante y la cabeza gacha.

| | |
|---|---|
| Vida | 16 500 · armadura 16, dureza 10 |
| Caja | 4,6 × 15 |
| Correa | 40 bloques |
| Inmune | dormido, al despertar, en la Ofrenda y mientras carga las Fuentes |

No le hace nada el fuego (ni lava ni llamas). En cada fase ataca más rápido
(`ritmo()` ×1,12, ×1,25 y ×1,4) y espera menos (×0,85, ×0,72 y ×0,6).

| Fase | Nombre | Qué se añade |
|---|---|---|
| I | Brasa | Barrido Solar, Castigo Divino |
| II | Llamarada | el Castigo acaba en **Onda de Fuego**; Sol Abrasador; **Trompetas del Apocalipsis** |
| III | Mediodía | **Fuentes Solares** (el golpe cooperativo); **Ofrenda al Sol** |
| IV | Dios de la Guerra | **Dios de la Guerra** |

**La Quemadura.** Casi todo su fuego la deja. Tiene tres niveles (I leve, II
fuerte, III grave) y cada golpe suma. Por sí sola no quita vida: es una marca,
y con la III el **Dios de la Guerra mata**. Baja sola un nivel cada 10 s. El
agua **no** la quita; **beberse una botella de agua, sí**
(`QuemaduraAguaMixin`). Se ve a la izquierda de los corazones: una llama con
su número, y la III con calavera.

| Ataque | Qué hace | Daño | Cómo se sale |
|---|---|---|---|
| **Barrido Solar** | solo si tiene a alguien a menos de 16 bloques: va a por el más cercano, se encara mientras carga el primer tajo y lo sigue entre tajo y tajo. Cuatro tajos seguidos; cada uno pega con la hoja a 12 bloques por delante y suelta **tres medias lunas de fuego** en abanico (una sola y grande en el tajo de arriba) que vuelan unos 28 bloques | hoja 18 / 23,5 / 25,5 / 32; media luna 13 / 17 / 18,7 / 23,2 y Quemadura I | salir del frente; las medias lunas, de lado |
| **Castigo Divino** | alza la espada y su sol le manda un haz. Marca con un sello a **cada jugador** a 48 bloques y, 1,1 s después, cae un rayo en cada sello | 19 / 24 / 26,4 / 32,8 y Quemadura I; no lo para el escudo | salir del sello |
| **Onda de Fuego** (II) | el Castigo acaba clavando la espada: un anillo de llamas corre por el suelo hasta 26 bloques | 12 / 16 / 17 / 21,6 y Quemadura I | **saltarla**: solo pega a quien esté en el suelo |
| **Sol Abrasador** (II) | se le forman tres soles en la mano y los lanza en arco, cada uno a un jugador (lo elige al formar el sol y se va girando hacia él). El sello del suelo marca dónde caen (1,4 s) | 27,5 / 35 / 37,4 / 44 en 4 bloques y **Quemadura II**; deja un charco de lava 5 s que prende | apartarse del sello |
| **Trompetas del Apocalipsis** (II) | alza la espada y salen del suelo **cuatro ángeles de mármol** a 15 bloques, cada uno sobre un **estrado** de dos escalones (desde el suelo no se le llega: hay que subirse). Tocan una melodía de 24 s y, mientras suena, **él no ataca ni se mueve**: se queda plantado y los dirige. Cada **5 s** cada ángel da un **pulso de fuego** por su estrado que tira abajo a quien esté encima; un segundo antes lo avisa (la trompeta se enciende y suena) | el pulso: 6 / 6 / 8 / 8 y unos 7 bloques de empujón. Si queda alguno en pie al acabar, entra en **Furia** | romper los cuatro (**10 golpes** cada uno), y **saltar el pulso** para no caerse (corre a ras del estrado) |
| **Fuentes Solares** (III) | se arrodilla, clava la espada y carga su sol, que crece. Salen **tres fuentes** a 13 bloques que le mandan fuego: con las tres llena la carga en 15 s, con dos en 20 y con una en 30 | si se llena: **Supernova** a 56 bloques, 56 / 56 / 57 / 67,2, **Quemadura III**, fuego y el **Grito de guerra** | romper las tres (**10 golpes** cada una): se le apaga el sol y cae **aturdido 6 s** con daño doble |
| **Ofrenda al Sol** (III) | el haz de su sol señala a uno (no se puede esquivar), lo agarra y lo alza al sol. Primero tiene **3 s para prepararse** (cuenta atrás 3, 2, 1; las teclas no cuentan) y luego tiene que seguir **10 letras en 8 s** (**12** en la fase IV); mientras, se quema un 4 % de su vida por segundo | si falla una o se acaba el tiempo: **la muerte salvo tótem**, y él entra en **Furia** | acertarlas todas: lo suelta y cae **aturdido 5 s** con daño doble |
| **Dios de la Guerra** (IV) | suelta la espada, se envuelve en llamas carmesí y marca **tres zonas** de 6 bloques (sobre los jugadores, al azar). Les lanza un sol a cada una y estallan en cadena | 174 y Quemadura I. Con **Quemadura III**, o con el **Grito de guerra** puesto, **mata a todos** los que pille (salvo tótem) | salir de las zonas, y no llegar con la Quemadura III (se gira hacia cada zona antes de lanzarle su sol) |

**Las teclas de la Ofrenda** (`OfrendaCliente`, `OfrendaTecladoMixin`). Son solo
letras de la A a la Z y salen de una semilla que el servidor manda al cliente.
Cada letra se comprueba en el cliente al momento, así que el lag no hace fallar,
y el servidor lleva la cuenta con medio segundo de margen. Vale la letra de la
distribución del teclado (en AZERTY, la A es la A) y solo al pulsar: mantener
no falla. Mientras dura, ninguna otra tecla llega al juego, salvo Escape y las
F. El atrapado lo ve en tercera persona, de cara a Novilis.

**La Furia del Sol** es **azul**: un 15 % más rápido, un 20 % más de daño y un
25 % menos de espera. Se le ve la armadura con las grietas en azul, la hoja y su
sol azules, y le salen **lenguas de fuego azul** del yelmo, las hombreras, el
puño, la espalda y la hoja (`NovilisLlamasLayer`: cada lengua va pegada a su
hueso y sube hacia arriba del mundo aunque él se doble). En el Dios de la Guerra
el mismo fuego es carmesí. Antes era la malla entera hinchada con bandas de fuego
encima: lo tapaba todo y no se le veía. **El Grito de guerra** (de la Supernova)
le deja llamas carmesí en el yelmo y las hombreras y hace que el Dios de la
Guerra mate a todos. Los dos se van cuando cae aturdido: una Ofrenda superada o
las Fuentes rotas a tiempo. La Furia, además, dura como mucho **30 s** y mientras
es inmune; el Grito se queda hasta que lo derriben.

**Los tajos dejan estela**: una cinta de fuego por donde pasó la hoja, que solo
sale cuando corta deprisa. El generador guarda por dónde pasan la base y la punta
de la hoja en cada animación (`NovilisEstelas`), y el haz del Castigo apunta a la
punta de verdad, que tiembla.

**Las animaciones** (segunda versión, octubre de 2026, porque se veían lentas y
pesadas y las piernas raras). Son más cortas, con anticipaciones breves y golpes
que llegan acelerando. Cada clave dice cómo se llega a ella: suave, acelerando
(el golpe), frenando (el impulso que se apaga) o pasándose un poco y volviendo.
Después, `novilis_fisica.py` añade lo que el cuerpo no puede dejar de hacer:

- **pies plantados**: las piernas salen de cinemática inversa; cada pie tiene su
  apoyo en el suelo y, si cambia de sitio, da el paso en arco;
- **peso**: la cabeza y el torso siguen a la pelvis con un muelle (la cadena de
  un golpe de verdad);
- **inercia**: la capa, el tabardo y las escarcelas se quedan atrás, se pasan y
  se asientan, sin meterse en el cuerpo ni en el suelo.

Todo se hornea en claves de vanilla (unas 8 000, como texto compacto para no
pasar del límite de Java). El paso no usa el reloj de andar de vanilla, que se
satura a 0,25 bloques por tick: la entidad lleva el suyo y avanza lo que anda,
así que los pies no patinan.

**Anda y corre.** Anda a unos 6 bloques/s y, si su presa se le aleja a más de 20
bloques, **corre** a unos 13 (15 en la fase IV; la Furia, un 10 % más), hasta
que la tiene a menos de 15. La carrera tiene su animación: zancada larga con
vuelo (cada pie pisa solo un tercio de la vuelta), el cuerpo echado adelante,
el brazo libre bombeando y la espada baja y hacia atrás. El cliente funde andar
y correr según lo rápido que va, cada uno con su reloj. Vanilla empuja con el
cuadrado de (atributo × lo que pide la IA), así que con 0,27 de atributo pide
1,37 para andar y 2,0 para correr. De pie tiene una postura propia (las rodillas algo
dobladas, un pie delante) que va horneada en la malla.

El generador del cuerpo es `novilis_juego.py` (149 piezas, 390 cajas, atlas de
512×512) y el de las 19 animaciones, `novilis_juego_anim.py`, con IK para que la
espada y las manos lleguen donde tienen que llegar. `novilis_hojas.py` saca las
hojas de control con dos vistas por fotograma (tres cuartos y de perfil, para
ver los pies contra el suelo). Las estatuas y las fuentes son mallas propias
(`novilis_props.py`).

### Las armaduras y las armas de rol

Cuatro juegos, uno por elemento, y cada uno es **un rol** del grupo: tanque,
sanador, soporte y DPS. **Por ahora no se fabrican: solo salen del inventario de
creativo** (pestaña de combate, detrás de la netherite). Están pensadas para un
jefe con **40 a 60 jugadores**: dan ventaja, pero poca, y nada se acumula (veinte
sanadores no curan veinte veces más; ver más abajo los topes por jugador).

| | Rol | Jefe | Lo suyo |
|---|---|---|---|
| **de Jade** | tanque | Rajang | metal verde negro y oro de templo en espiral cuadrada; casco de jaguar con hocico, colmillos, orejas y cresta de cristales; hombreras de oro con una esquirla de jade que flota y gira, cristales por la espalda; faldones de oro y garras en las botas |
| **de las Mareas** | sanador | Nerea | metal abisal con escamas y costuras de prismarina que brillan; la venera de nácar con su perla tras el casco, cuernos de coral y branquias que ondean; caracola y coral en los hombros, capa de algas que ondea y se levanta al correr, espinas de hueso; conchas en la cadera y aletas en rodillas y tobillos |
| **del Vendaval** | soporte | Aeralis | metal añil con rayos celestes y violeta de tormenta; alas de pluma en el casco que aletean y antenas de polilla; hombreras de pluma y **alas de polilla en la espalda** con su ocelo, que aletean; plumas en la cadera y alas en los talones |
| **Solar** | DPS | Novilis | acero quemado con grietas de lava y oro; yelmo cerrado con visera en T, cuernos de obsidiana, una llama de cresta y un **halo de sol** que gira tras la cabeza; un núcleo de sol en el pecho con su corona de llamas, llamas en los hombros y los talones, y una capa carmesí cuyo bajo arde |

**Protección.** Dureza, resistencia al empuje y durabilidad como la netherite
(la durabilidad, ×1,5); no se queman, se reparan con netherite y se encantan
como cualquier armadura (Protección, Irrompibilidad, Reparación…).

| | Casco | Coraza | Grebas | Botas | Total | Extra |
|---|---|---|---|---|---|---|
| Jade (tanque) | 4 | 9 | 7 | 4 | 24 | — |
| Mareas (sanador) | 3 | 8 | 6 | 3 | 20 | +1 corazón (medio por pieza) |
| Vendaval (soporte) | 3 | 8 | 6 | 3 | 20 | — |
| Solar (DPS) | 3 | 8 | 6 | 3 | 20 | — |

**Habilidades.** Con el juego **entero** puesto se tiene su pasiva y su activa.
La activa sale con la tecla **R** (se cambia en Controles, categoría Atalaya),
dura **30 s** y vuelve a estar lista **120 s** después de usarla. Un icono a la
derecha de la hotbar la muestra: limpio si está lista; latiendo y con una barra
que se gasta mientras dura; oscuro y con los segundos que faltan en recarga.
Las piezas lo explican al pasar el ratón.

| Rol | Pasiva | Activa (120 s, dura 30 s) |
|---|---|---|
| **Tanque** | **Guardián**: los aliados a 4 bloques reciben un 5 % menos de daño (no se acumula con otros tanques) | **Muralla de Jade**: los ataques a un solo objetivo de los jefes (Rompeolas, Aleteo, Garra, Barrido, Cacería) van al tanque si está a su alcance, y al acabar el jefe no se deja provocar otros 15 s; protege a sus **2 aliados más cercanos** (8 bloques): el **30 %** del daño que les hace un enemigo se lo lleva el tanque, con su armadura y sin empuje; y él recibe un **20 % menos** |
| **Sanador** | **Marea Viva**: cada 5 s, medio corazón al aliado más herido a 6 bloques | **Manantial**: al activarlo quita los efectos malos a los 3 aliados más heridos; luego, cada 3 s, medio corazón a los 3 más heridos a 8 bloques |
| **Soporte** | **Viento a Favor**: +10 % de velocidad a los aliados a 6 bloques (no se acumula); él recibe un 25 % menos de daño de caída | **Corriente Ascendente**: él y sus 4 aliados más cercanos (8 bloques) tienen **Velocidad I y 2 corazones dorados** durante 30 s (no se puede recibir otra mientras dura), y una ráfaga a su alrededor (4,5 bloques) aparta a los monstruos normales |
| **DPS** | **Corazón de Brasa**: +10 % de daño | **Furia Solar**: +20 % de daño, y sus 3 aliados más cercanos (8 bloques) pegan un **5 % más** durante 30 s (cada jugador, como mucho una vez cada 20 s) |

**Topes para 60 jugadores.** Cada jugador recibe como mucho medio corazón de
Marea Viva cada 5 s y medio del Manantial cada 3 s, tenga los sanadores que
tenga cerca; el Guardián y el Viento a Favor valen lo mismo con uno que con
veinte; la Corriente y la Furia no se renuevan mientras duran. Los golpes que
matan salvo tótem (la Mirada de Nerea, el Picado, el Rugido de Jade, el meteorito
y los demás de `bypasses_resistance`) no los toca ninguna habilidad: ni se
reparten con el tanque ni los baja la Muralla.

El daño que se lleva el tanque es un tipo propio, `atalaya:muralla_jade` (sin
empuje y con su armadura, aunque el golpe original la atraviese). Si muere de
eso, el chat dice que cayó protegiendo a sus aliados. Ni le da ni le gasta la
invulnerabilidad tras un golpe: si dos aliados reciben a la vez, se lleva las
dos partes.

**Las armas** son una por rol. Durabilidad, encantamientos y reparación como la
netherite; en la mano se ven grandes y animadas (sprite de 32×32, el arco no).
Lo que hacen a los monstruos normales (aturdir, provocar, quemar) no lo hacen a
jefes ni minijefes (los cuatro elementales, el Vigía, el Wither, el dragón, el
guardián anciano y el warden).

| Arma | Rol | Daño | Además |
|---|---|---|---|
| **Martillo de Jade** | tanque | 9, lento (0,8 golpes/s) | el golpe **cargado del todo** deja al monstruo aturdido 1 s y hace que vaya a por quien lo lleva |
| **Tridente de las Mareas** | sanador | 9, en la mano y lanzado | se lanza y vuelve (Lealtad III de serie); cada 8 s, un golpe cura medio corazón al aliado más herido a 8 bloques |
| **Arco del Vendaval** | soporte | como un arco de Poder III sin encantar; con Poder V, como un Poder VIII | las flechas van un **20 % más rápidas** (sin pegar más por eso); la que da a un aliado no le hace daño y le da Velocidad I y un 5 % más de velocidad 3 s (a cada jugador, como mucho una vez cada 20 s) |
| **Gran Espada Solar** | DPS | 10 (1,4 golpes/s) | prende fuego 4 s a los monstruos normales y suelta un tajo solar |

Todo lo de las habilidades está en `com.atalaya.habilidad` (`Habilidades`, la
provocación en `Provocacion`, quién es jefe en `Jefes`); el daño pasa por
`DanoHabilidadesMixin`. Los sonidos salen de `habilidades_sonidos.py`, los
iconos del HUD de `habilidades_iconos.py`.

**Se ven en 3D y con capas** (no la capa plana de vanilla): `ArmaduraJefeRender`
las pinta con Fabric `ArmorRenderer` en todo lo que lleva armadura (jugadores,
maniquíes, soportes, monstruos). Cada pieza es su propia malla, que copia la
postura del cuerpo de quien la lleva y tiene sus piezas por encima, y se pinta en
cuatro pasadas: lo opaco, lo translúcido (aletas, cristales, alas), lo que brilla
sin luz (en 8 cuadros que se funden: la luz corre por las costuras) y el destello
de los encantamientos. Las mallas, las animaciones y las texturas salen de
`armaduras_jefes.py` (genera `ArmaduraJefeMalla.java`); los iconos y las armas,
de `armaduras_iconos.py`.

**La barra de armadura con el conjunto entero.** Con las cuatro piezas del mismo
conjunto puestas, los iconos de armadura del HUD pasan a ser la pechera de ese
conjunto, con sus colores, y un brillo los cruza cada 2,4 s. Vale para las
cuatro armaduras de los jefes y para el traje Hazmat:

| Conjunto | Icono |
|---|---|
| Mareas | hombreras de perla, peto verde azulado, cinto cian |
| Jade | hombreras de oro, peto de jade, gema verde con marco de oro |
| Vendaval | hombreras lila, peto añil, gema celeste |
| Solar | hombreras de oro, peto de hierro quemado, el sol en el pecho |
| Hazmat | amarillo de aviso con las correas negras |

Con piezas sueltas o mezcladas se ven los de vanilla. Cuántos iconos salen y
dónde lo sigue decidiendo vanilla; solo cambia el dibujo (`IconosArmadura`, con
un mixin en `Hud.extractArmor`). Salen de `iconos_armadura_hud.py`, con la
silueta de vanilla (9 × 9) y los colores sacados de la pechera de cada uno.

Las tres espadas de antes (de las Mareas, de Jade y del Vendaval, 16 de daño)
siguen existiendo para no romper mundos, pero ya no salen en creativo: las
sustituyen las armas de rol.

---

## Cómo se hace un jefe

Un jefe nuevo sale en tres tiempos:

1. **Se decide con imágenes.**
2. **Se pasa al juego con scripts.**
3. **Se presenta con un póster y un teaser.**

Todo lo visual y sonoro sale de **Python** en `materiales/generadores/`: nada se
pinta en un editor ni se graba. Así un retoque es cambiar un número y regenerar.

### 1. La ficha de diseño, antes de una línea de Java

1. **Boceto** (`<elemento>_modelo.py`). Es un esqueleto de cajas al estilo
   Minecraft, en píxeles de modelo: 16 son 1 bloque, la Y va hacia abajo y el
   frente mira a −Z. Lleva **materiales en mosaico**, no un atlas, porque sirve
   para decidir la forma y el tamaño, no la textura.
   - Si hay varias propuestas, va una por opción: A, B, C.
   - Se apoya en `nerea_modelo.py`, que tiene los nodos, las losetas y las rampas.
2. **Ficha** (`<elemento>_escenas.py`). Lo renderiza con `vigia_render.py` en JPG
   de 1600×900, en una carpeta **fuera del repo**:
   - la escena heroica, en su templo;
   - las vistas de frente, perfil y espalda;
   - las cuatro fases;
   - una escena por ataque;
   - la **escala**, junto a un jugador, el Vigía y los jefes anteriores.

   La plantilla más completa es `tierra_escenas.py`. Las piezas de los ataques
   pueden ir aparte, como en `tierra_ataques.py`.
3. **Página de revisión.** La ficha se publica como **página privada de Claude**
   (un artifact) con las imágenes, la historia, las fases, los ataques y las
   preguntas abiertas. Ahí se elige el diseño, el tamaño y los ataques, **antes**
   de pasar nada al juego.

### 2. Al juego

4. **`<jefe>_juego.py`.** Pasa el boceto elegido a piezas animables, pinta el
   atlas de cada fase y escribe el Java de la malla. Es la **única fuente de la
   geometría**: `<Jefe>Malla.java` dice "GENERADO" y no se toca a mano.
5. **`<jefe>_juego_anim.py <raíz> [carpeta]`.** Las animaciones, pose a pose. Cada
   pose **se suma** a la de reposo.
   - Con `<jefe>_fisica.py` se añade lo que el cuerpo no puede dejar de hacer:
     pies plantados por cinemática inversa, inercia en cadenas y colgajos, y la
     cabeza que llega un poco tarde.
   - La física se simula a 80 Hz y se **hornea** en keyframes, así que en el
     juego no cuesta nada.

   **Al ejecutarlo escribe en el repo:**
   - `<Jefe>Malla.java`, `<Jefe>Animaciones.java` (un método por animación, por
     el límite de 64 KB de bytecode) y `<Jefe>Geometria.java`;
   - las pieles `_f1` a `_f4`, sus brillos y el liberado;
   - con carpeta, las **hojas de control**: una tira por animación con sus
     fotogramas clave, para revisarlas.
6. **El resto de recursos.** Son independientes entre sí:
   - `<jefe>_extras.py`: proyectiles, partículas y sus JSON, iconos de efectos,
     botín, viñeta de miedo y máscara de disolver;
   - `<jefe>_hud.py`: la barra;
   - `huevos_jefes.py`: los huevos de todos;
   - `<jefe>_sonidos.py`: **borra** sus `.ogg`, los sintetiza otra vez y reescribe
     su bloque de `sounds.json`. Los subtítulos de `lang/` y el registro en
     `AtalayaSonidos.java` se hacen a mano.
7. **El Java a mano.** Lista de lo que tocó Rajang:

   | Dónde | Qué |
   |---|---|
   | `entity/` | `<Jefe>Entity`, `<Jefe>Danos`, los proyectiles, y el registro en `AtalayaEntities` |
   | `effect/` | el castigo y la bendición; se registran en `Atalaya.java` |
   | `item/AtalayaItems` | el huevo y la pieza; el huevo va a la pestaña en `Atalaya.java` |
   | `sonido/`, `particula/` | los eventos y las partículas |
   | `command/AtalayaCommand` | `/atalaya <jefe> <orden>` → `<Jefe>Entity.forzar` |
   | `client/` | `Renderer`, `RenderState`, `Model`, `BrilloLayer`, `Particula`, `EfectosCliente`, `BarraHud`, los renderers de proyectiles; y el registro en `AtalayaClient` |
   | compartido | `MiedoHud` (su textura), `NereaPresencia` (su miedo), la barra anterior (para apilarse) |
   | `lang/` | `es_es.json` y `en_us.json` con las **mismas claves** |
   | `data/` | `damage_type/<jefe>_*.json`, las etiquetas de `minecraft/tags/damage_type/`, `loot_table/entities/<jefe>.json` |

**El orden para regenerar:**

1. `<jefe>_juego_anim.py`, que genera el Java: va antes de compilar.
2. `_extras`, `_hud`, `_sonidos` y `huevos_jefes`, en cualquier orden.
3. El póster y el teaser, al final, porque leen las texturas, la barra y los
   `.ogg` ya hechos.

Las fichas y las hojas de control no hacen falta para compilar.

Los scripts de cada jefe:

| Jefe | Boceto y ficha | Juego | Recursos | Promo |
|---|---|---|---|---|
| Nerea | `nerea_modelo`, `nerea_b_modelo`, `nerea_c_modelo`, `nerea_escenas`, `nerea_v2`, `nerea_c_escenas` | `nerea_juego`, `nerea_fisica`, `nerea_juego_anim` | `nerea_extras`, `nerea_hud`, `nerea_sonidos` | `nerea_poster`, `video/nerea_teaser` |
| Aeralis | `viento_modelo`, `viento_bc_modelo`, `viento_escenas`, `viento_remake_escenas`, `viento_remake_hud`, `viento_remake_iconos` | `vendaval_juego` (y `vendaval_juego_v1`, el de antes), `vendaval_fisica`, `vendaval_juego_anim` | `aeralis_extras`, `aeralis_mejoras_extras`, `aeralis_hud`, `aeralis_sonidos`, `aeralis_mejoras_sonidos` | `aeralis_poster`, `video/aeralis_teaser` |
| Rajang | `tierra_modelo`, `tierra_piel`, `tierra_ataques`, `tierra_escenas`, `rajang_mejoras_escenas` | `rajang_juego`, `rajang_juego_anim` | `rajang_piezas`, `rajang_extras`, `rajang_mejoras_extras`, `rajang_hud`, `rajang_sonidos`, `rajang_mejoras_sonidos` | `rajang_poster`, `video/rajang_teaser` |
| Novilis | `fuego_modelo`, `fuego_escenas`, `fuego_hud_propuesta` | `novilis_juego`, `novilis_fisica`, `novilis_juego_anim` | `novilis_extras`, `novilis_props`, `novilis_hud`, `novilis_sonidos` | aún no |

Los nombres de los scripts del boceto van por **elemento** (`viento_`,
`tierra_`, `fuego_`) y los del juego por **jefe**, porque el nombre se decidió después del
diseño.

**Cómo se añade algo a un jefe que ya existe** (lo que se hizo con las mejoras
de Rajang), sin regenerar lo que ya está:

- **Texturas nuevas**: en un script aparte (`rajang_mejoras_extras.py`) que
  solo escribe ficheros nuevos. Volver a pasar `rajang_extras.py` reescribiría
  todos los PNG, y otra versión de Pillow puede cambiar los bytes aunque los
  píxeles sean los mismos.
- **Sonidos nuevos**: al **final** de `rajang_sonidos.py`, con **su propia
  semilla**, para que los de antes no cambien. Como ese script borra la carpeta
  y los rehace todos, `rajang_mejoras_sonidos.py` toma de él las herramientas y
  solo el bloque nuevo, y añade sus eventos a `sounds.json` sin quitar los
  demás. Una pasada entera da el mismo resultado.
- **Animaciones**: en `rajang_juego_anim.py`, y se regenera con
  `RAJANG_SIN_TEXTURAS=1` para no reescribir las pieles. Las hojas de control de
  antes y de después se guardan junto a la ficha.

> **Ojo con los imports.** Los `*_escenas.py` leen `sys.argv` y crean carpetas
> **al importarse**. Por eso los pósters y los teasers cambian `sys.argv` un
> momento antes de importarlos. Y `NEREA_SIN_FISICA=1` o `VENDAVAL_SIN_FISICA=1`
> se saltan el horneado de la física, que es lento y no hace falta para una pose
> fija.

### Los sonidos

Los cinco `*_sonidos.py` sintetizan desde cero con numpy y scipy, a partir de
**la física de lo que el bicho lleva encima**:

| Jefe | De qué salen |
|---|---|
| Nerea | burbujas (la resonancia de Minnaert), chapuzones y olas; hueso, coral y cadenas mojadas; una garganta de leviatán con un lamento de sirena |
| Aeralis | turbulencia, tonos eólicos que silban, aletazos de membrana, tornados y truenos; la voz de una cigarra del tamaño de una tormenta |
| Rajang | la resonancia de una barra de jade, piedra que muele, grava; una voz felina |
| Novilis | fragua: yunques, metal al rojo, fuelles, lava; trompetas de bronce para la melodía de los ángeles; una voz de yelmo |

Todos producen OGG Vorbis **mono** a 44,1 kHz, que es lo que hace falta para que
el juego los coloque en 3D. Las semillas son fijas, pero **añadir un sonido
cambia el azar de todos los que vienen detrás**.

Con un segundo argumento sacan además una hoja de espectrogramas, para revisarlos
con la vista.

| | Eventos | `.ogg` |
|---|---|---|
| Vigía | 19 | 27 |
| Nerea | 34 | 67 |
| Aeralis | 33 | 70 |
| Rajang | 42 | 77 |
| Novilis | 44 | 75 |

### 3. El póster

`python <jefe>_poster.py <raíz> <salida.png> [escala]`

Sale en **1920×1080**: se pinta al doble y se reduce, para suavizar bordes. Con
escala `0.5` da una vista previa rápida, y con `2`, un 4K.

Los cuatro tienen la misma composición, y eso es lo que los hace una serie:

- **el jefe, grande a la derecha**, con la cámara baja mirándolo desde abajo, y
  la malla y las texturas reales del juego;
- **a la izquierda**:
  - el antetítulo «ATALAYA · JEFE DEL …» en Montserrat Bold 22, espaciado;
  - el **NOMBRE** en Oswald Bold 196, con halo;
  - el epíteto, en Montserrat SemiBold Italic 34;
  - el lema, en Montserrat Medium 24;
  - una raya de acento;
- **arriba**, la barra de jefe tal como sale en el juego, ampliada ×2;
- **en las esquinas**, el sello «HARDCORE» arriba a la derecha y «Minecraft 26.2 ·
  Fabric» abajo;
- **la escena**: el suelo y el decorado en 3D, el efecto propio del jefe en
  espiral (por delante solo pasa por debajo de la cintura, para no taparle la
  cara), sus partículas reales delante y detrás, resplandor, contraluz de borde,
  viñeta y grano.

| | Antetítulo | Lema | Acentos | Fase |
|---|---|---|---|---|
| Vigía | NUEVA AMENAZA | Lo que mira, lo maldice. | ámbar y rojo | — |
| Nerea | JEFE DEL MAR | Rompe sus cadenas. Libera su corazón. | cian y magenta | I |
| Aeralis | JEFE DEL AIRE | Calma la tormenta. Apaga el ojo de su pecho. | celeste y violeta | III |
| Rajang | JEFE DE LA TIERRA | Resiste el cataclismo. Arranca la raíz de su pecho. | jade y oro | IV |

El encuadre se ajusta sin tocar código, con variables de entorno: `GUINADA` (el
giro del jefe), `OBJ_X` (hacia dónde mira la cámara) y `BARRA_X` (dónde va la
barra).

Para uno nuevo, se copia `rajang_poster.py`, que es el más completo, o
`nerea_poster.py`, que es el más corto.

### 4. El teaser

`python materiales/video/<jefe>_teaser.py <raíz ABSOLUTA> <carpeta de trabajo> <salida.mp4> [escala]`

Es un vídeo de **14-15 s** a 1920×1080 y 24 fps, en H.264 con audio AAC. Se
**pinta fotograma a fotograma** con un render propio de cada teaser, sin grabar
el juego.

El esquema es siempre el mismo:

1. negro;
2. la amenaza, que va creciendo:

   | Jefe | La amenaza |
   |---|---|
   | Nerea | las cadenas que caen al abismo |
   | Aeralis | el tornado y su interior |
   | Rajang | la selva, el templo y la estatua dormida |
3. **la cara**, que abre los ojos;
4. negro;
5. **el cierre**: el nombre en letras de píxel de la barra, su emblema latiendo y
   «P R Ó X I M A M E N T E».

- **Sin voz ni música.** El audio es una mezcla de los `.ogg` del propio jefe.
- **Codificación.** Usa el ffmpeg que trae el paquete `imageio-ffmpeg`, sin
  instalar nada más.
- **Se puede reanudar.** Se salta los fotogramas que ya están en
  `<trabajo>/cuadros`. Por eso, **si cambias el código, vacía esa carpeta**.
- **Revisión.** Con `--muestras`, una salida `.png` y `TIEMPOS=1.0,2.5,…` saca una
  hoja con esos instantes en vez del vídeo.
- **En varios procesos.** `rajang_teaser.py` se puede repartir con `PARTE=k/n` y
  luego lanzar uno sin `PARTE` que codifica. Es la plantilla para el siguiente.

> Hubo un vídeo del Vigía de 62 s **grabado del juego**, con un datapack de
> rodaje, narrador y música. Se quitó al día siguiente: dependía de una grabación
> de pantalla, de tiempos medidos a mano y de un servicio de voz en la nube, y no
> se podía regenerar. Los teasers sintéticos sí se pueden. El mp4 de aquel vídeo
> sigue en el historial de git: 36 MB.

## Comandos

| Comando | Permiso | Qué hace |
|---|---|---|
| `/atalaya menu` | Operador | Abre el panel de configuración |
| `/atalaya hidratacion <0-50>` | Operador | Fija tu hidratación. Para probar: llegar al nivel 2 esperando al sol son casi seis minutos |
| `/atalaya frio <0-50>` | Operador | Fija tu frío. Igual: helarse del todo a la intemperie son casi seis minutos |
| `/atalaya diagnostico` | Operador | Por qué no aparece el fulminante donde estás: interruptor, bioma, lista de monstruos y regla de sitio |
| `/atalaya nerea <orden>` | Operador | Fuerza a la Nerea más cercana (64 bloques): `despertar`, `rompeolas`, `remolino`, `burbujas`, `molino`, `arpon`, `lejano` (arpón al más lejano), `mirada`, `aturdido`, `agotado`, `canto`, `clic` (un clic de compañero al primer hechizado), `cadenas`, `marea_alta`, `fase`, `liberar` |
| `/atalaya aeralis <orden>` | Operador | Igual con la Aeralis más cercana (80 bloques): `despertar`, `aleteo`, `tornados`, `caceria`, `rafaga`, `doble`, `juicio`, `picado`, `posada`, `escamas`, `rasante` (la pasada rasante ya), `romper` (rompe sus tornados), `viento` (le devuelve el viento que le falta), `mancha` (una mancha de escamas bajo cada presa), `nucleo` (rompe un núcleo del Juicio), `furia` (pone o quita la Furia), `aturdida`, `agotada`, `fase`, `liberar` |
| `/atalaya rajang <orden>` | Operador | Igual con el Rajang más cercano (80 bloques): `despertar`, `perseguir` (corre 8 s sin atacar, para ver el paso y el galope), `garra`, `terremoto`, `embestida`, `tumba` (en círculo), `anillo` (la Tumba en anillo), `sello`, `romper` (rompe los tótems), `escalon` (hace temblar ya un escalón del Sello), `cataclismo`, `salto`, `idolo`, `altar` (lleva al jugador más cercano al altar del ídolo), `aturdido`, `paralizado`, `estampado`, `furia` (se la pone o se la quita), `fase`, `liberar` |
| `/atalaya novilis <orden>` | Operador | Igual con el Novilis más cercano (80 bloques): `despertar`, `barrido`, `castigo`, `onda`, `sol`, `trompetas`, `estatua` (un golpe a un ángel), `fuentes`, `fuente` (un golpe a una fuente), `ofrenda`, `dios`, `aturdido`, `furia` y `grito` (se los pone o se los quita), `perseguir` (va 8 s tras el blanco sin atacar, andando o corriendo segun lo lejos que este, para ver el paso), `fase`, `liberar` |
| `/atalaya habilidad` | Operador | Usa la activa de tu armadura de rol, como la tecla R (con el juego entero puesto) |
| `/repair [jugadores]` | Operador | Deja como nueva la armadura puesta, la tuya o la de otros. También el traje Hazmat, que por diseño no se repara: es una herramienta de pruebas |

En las órdenes de los jefes:

- `fase` deja la vida justo por debajo del siguiente umbral.
- `liberar` lo mata de verdad, con la liberación entera y el botín.
- Los ataques apuntan al ser vivo más cercano, maniquíes incluidos.

El traje no tiene comando para conseguirlo: se craftea, o se coge de la pestaña de
**Combate** en creativo. Los materiales están en **Ingredientes**. Los jefes y el
Vigía se invocan con su **huevo**, en la pestaña de huevos.

## Configuración

Dos formas, equivalentes: el menú en el juego o `config/atalaya.json`.

Son **25 interruptores** en cuatro grupos, cada uno en su propia fila:

```
[Radiación][Hidratación][Fulminante][Vigía][Frío][Corrosión][Empapado]  lo que hace el MUNDO
[Miel][Colmillo][Veneno][Espejo][Pata][Alón][Fulgurita]                lo que sueltan los MOBS
[Lingote][Miel cr.][Plantilla][Herrería]                               la cadena del TRAJE
[Carbón][Filtro][Alga][Lente][C.Venenoso][P.Alada][Agua]               ITEMS y mejoras
```

**Los jefes no tienen interruptor.** No aparecen solos (solo con su huevo o
`/summon`), así que no hay nada que apagar. El Vigía y el Fulminante sí lo
necesitan, porque aparecen de forma natural.

### Nada se coloca a mano

Los interruptores se **declaran como datos** y la posición se calcula. Antes cada
uno tenía su constante de ranura y añadir uno obligaba a recolocar los demás:
eso es lo que no escalaba.

Ahora **añadir una mecánica es escribir una línea** al final de su grupo. Cada
grupo empieza en fila nueva por su cuenta, y si alguno pasa de nueve se parte
solo a la siguiente.

El panel tiene **seis filas: cinco de contenido y una de navegación**. Cuando el
contenido no cabe se abre una página nueva, y las flechas solo aparecen si hay
adónde ir. Con 25 interruptores caben en cuatro filas, así que ahora mismo es una
sola página con una fila de margen.

Los huecos van **vacíos, sin cristal de relleno**: los clics en la zona del panel
nunca mueven items y el shift-clic está desactivado, así que el relleno solo era
decoración.

### Se corta por donde interese

Cada cadena está partida en sus pasos, así que puedes permitir el material y
bloquear la herrería, o al contrario. Apagar una receta **también la quita del
libro de recetas** de todos los jugadores conectados, al instante.

Los drops no son recetas, así que no tocan el libro: se filtran sobre el botín ya
generado y el cambio es inmediato, sin recargar datapacks.

### Todo arranca apagado

Un mundo o servidor recién puesto **se comporta como vanilla**. Ninguna mecánica
está activa hasta que un operador la enciende desde el panel.

Es lo que permite **anunciarlas como evento** en vez de que aparezcan solas, y
evita que nadie se encuentre con la lluvia comiéndole la armadura sin haberlo
pedido.

Vale también para lo que se añada más adelante: un campo nuevo entra en `false`
aunque el fichero de configuración sea viejo y no lo mencione, así que actualizar
el mod nunca enciende nada por su cuenta.

---

## Requisitos

- **JDK 25** — obligatorio, ver el aviso de abajo
- **Git**
- No hace falta instalar Gradle: el proyecto trae el *Gradle Wrapper*.
- No hace falta instalar Fabric para desarrollar: `runClient` levanta un cliente
  con el mod ya cargado.
- **Python 3.14**, solo para regenerar texturas, mallas, animaciones, sonidos,
  pósters y teasers. Para compilar no hace falta: todo lo generado está subido.

### Python para los generadores

```powershell
python -m pip install numpy scipy soundfile pillow imageio-ffmpeg
```

| Paquete | Para qué |
|---|---|
| `numpy`, `pillow` | todo: texturas, el renderizador 3D, las fichas y los pósters |
| `scipy`, `soundfile` | los sonidos. `soundfile` trae libsndfile con Vorbis, así que escribe `.ogg` sin nada más |

> Si Windows rechaza una DLL de scipy al importarla («Una directiva de Control de
> aplicaciones bloqueó este archivo», en `scipy.spatial._qhull`), instala
> `scipy==1.16.3`: en la máquina del trabajo la 1.18 estaba bloqueada y esa no.
| `imageio-ffmpeg` | los teasers. Trae su propio ffmpeg: no hace falta instalarlo aparte |

Y las **fuentes**: los pósters, las fichas y los teasers las cargan de
`C:/Windows/Fonts/` por su nombre de fichero. Sin ellas fallan con `OSError`.

| Familia | Ficheros |
|---|---|
| Montserrat | `Montserrat-Bold.ttf`, `-Medium.ttf`, `-SemiBold.ttf`, `-SemiBoldItalic.ttf` |
| Oswald | `Oswald-Bold.ttf` |

Están en Google Fonts. Se instalan los ficheros estáticos (no los variables) con
clic derecho → **«Instalar para todos los usuarios»**. Si se instalan solo para
el usuario, van a otra carpeta y los scripts no los encuentran.

### ⚠️ `JAVA_HOME` tiene que apuntar al JDK 25

Loom ejecuta las herramientas de Minecraft en el mismo proceso que Gradle, así
que **no basta con tener el JDK 25 instalado**: la propia JVM de Gradle tiene que
ser la 25. Si `JAVA_HOME` apunta a otra, el build falla con:

```
Failed to setup Minecraft: Minecraft 26.2 requires Java 25 but Gradle is using 24
```

En Windows, para dejarlo fijo:

```powershell
[Environment]::SetEnvironmentVariable("JAVA_HOME","C:\Program Files\Eclipse Adoptium\jdk-25.0.4.7-hotspot","User")
```

(hay que reabrir la terminal después). Comprobar con `echo $env:JAVA_HOME`.

## Puesta en marcha en otra máquina

```bash
git clone https://github.com/SiologoDr/atalaya-fabric-26.2.git
cd atalaya-fabric-26.2

# Comprobar que Gradle usa el JDK 25 ANTES de compilar
./gradlew -version        # Windows: .\gradlew.bat -version

# Compilar. La primera vez descarga Minecraft y lo remapea: varios minutos.
./gradlew build
```

El `.jar` queda en `build/libs/atalaya-1.1.7.jar`. La versión sale de
`mod_version` en `gradle.properties`.

Nada más hace falta para compilar: las versiones están fijadas en
`gradle.properties` y las dependencias las resuelve Gradle. Las carpetas `build/`,
`run/` y `.gradle/` no se suben y se regeneran solas.

**`entrega/`** guarda el `.jar` ya compilado de la última versión, para pasárselo
a jugadores y servidores sin tener que compilar. Va en git porque `build/` no.
Al subir de versión: cambiar `mod_version`, compilar, y **sustituir** el `.jar`
de `entrega/` en vez de añadir otro al lado.

Para regenerar materiales hace falta además el
[Python de los generadores](#python-para-los-generadores).

## Desarrollo

```bash
./gradlew runClient      # cliente de desarrollo con el mod cargado
./gradlew runServer      # servidor de desarrollo (para probar en red)
./gradlew build          # compilar y empaquetar
./gradlew clean          # si algo se queda raro tras cambiar versiones
```

Los mundos, opciones, configuración y logs de esas tareas viven en `run/`, que no
se sube. La configuración del mod en desarrollo está en `run/config/atalaya.json`.

Para comprobar que el mod carga, buscar estas líneas en el log:

```
Loading NN mods:
	- atalaya 1.1.7
(atalaya) Atalaya iniciado (Minecraft 26.2 / Fabric).
(atalaya) Atalaya (cliente) iniciado.
```

> **Editar siempre en `src/`, nunca en `build/`.** `build/` es salida generada y
> se sobrescribe en la siguiente compilación.

> **Tampoco en los ficheros generados de `src/`.** `NereaMalla`, `NereaAnimaciones`,
> `NereaGeometria` y sus equivalentes de Aeralis y Rajang los escriben los
> `*_juego_anim.py`, igual que las pieles de los jefes. Un cambio a mano se pierde
> en la siguiente regeneración. Además descuadra la textura o separa lo que se ve
> de lo que pega.

### Fotos de prueba

`FotosPrueba` es una herramienta de desarrollo del cliente. Sirve para hacer
capturas en el tick exacto desde una función de un datapack, aunque la ventana
esté tapada o sin foco.

1. Crea un fichero vacío `run/atalaya_fotos.flag`.
2. Desde la función, manda un `tellraw` con `FOTO nombre`.
3. La captura se guarda en `run/screenshots/nombre.png` y el mensaje no sale en
   el chat.

Sin el fichero no hace nada.

### Escenas de prueba en el juego

`materiales/generadores/rajang_escenas_juego.py` escribe un datapack
(`materiales/escenas/atalaya_escenas/`) que monta cada ataque de Rajang delante
de la cámara, con maniquíes de presa, y saca una foto en el momento justo.

```bash
python materiales/generadores/rajang_escenas_juego.py . run/saves/<mundo> [--auto]
```

- En el juego: `/function escenas:recorrido` (todas, unos 2 minutos),
  `/function escenas:<escena>` (una) y `/function escenas:parar`.
- Necesita un mundo plano. Si hay un pueblo cerca, el recorrido se monta a 120
  bloques de él, porque Rajang iría a por los aldeanos.
- Con `--auto`, el recorrido arranca solo al abrir el mundo. Después hay que
  generarlo otra vez sin `--auto`.
- Para entrar directo al mundo:
  `gradlew runClient --args="--quickPlaySingleplayer <mundo>"`.

Las de **Aeralis** van igual, con `aeralis_escenas_juego.py`
(`materiales/escenas/atalaya_escenas_aeralis/`):

```bash
python materiales/generadores/aeralis_escenas_juego.py . run/saves/<mundo> [--auto[=escena]]
```

- `/function escenas_aeralis:recorrido` (todas, unos 2 minutos y medio),
  `/function escenas_aeralis:<escena>` y `/function escenas_aeralis:parar`.
- Escenas: `cuerpo` (la cámara la rodea: frente, perfil, espalda, abajo, arriba
  y tres cuartos), `fases`, `aleteo`, `tornados`, `viento`, `caceria`,
  `picado`, `escamas`, `juicio` (9 maniquíes: el ciclón atrapa a 3; se deja
  fallar para ver los tótems y la Furia) y `furia` (el aura desde tres lados).
- Las cámaras de los ataques van a 40-55 bloques: con 38 bloques de alas se come
  el plano. Los cambios de fase van separados, porque mientras se tambalea no se
  puede forzar otro.
- Cada comando corta lo que haya en marcha de su pack; las escenas de Rajang
  no las toca.

---

## ⚠️ Mappings de Mojang, no Yarn

Yarn **no publica mappings para la serie 26.x** (el último es 1.21.11), así que
este proyecto usa los **mappings oficiales de Mojang**, que es lo que aplica Loom
por defecto.

Consecuencia práctica: casi toda la documentación y los tutoriales de Fabric usan
nombres de Yarn, que **no coinciden** con los de aquí.

| Los tutoriales dicen (Yarn) | Aquí se llama (Mojang) |
|---|---|
| `Item.Settings` | `Item.Properties` |
| `World` | `Level` |
| `Identifier` | `Identifier` (¡igual! en 26.2 ya no es `ResourceLocation`) |

Ojo con la última: en versiones anteriores el nombre Mojang era `ResourceLocation`,
y mucha documentación todavía lo dice. En 26.2 la clase es
`net.minecraft.resources.Identifier`.

Para traducir nombres: **[linkie.shedaniel.dev/mappings](https://linkie.shedaniel.dev/mappings)**.

**No añadir** `mappings loom.officialMojangMappings()` a `build.gradle`: este Loom
ya los usa por defecto y declararlos explícitamente rompe el build con
`Failed to find official mojang mappings for 26.2`.

## Cambios de API en 26.2 que cuesta encontrar

Los tutoriales (incluso los de 1.21) usan las versiones viejas de todo esto. La
forma fiable de comprobar una firma es `javap` sobre el jar remapeado, en
`~/.gradle/caches/fabric-loom/26.2/minecraft-merged.jar`.

| Antes | En 26.2 |
|---|---|
| `hasPermission(2)` | `Commands.LEVEL_GAMEMASTERS.check(fuente.permissions())` |
| `ClickType` | `ContainerInput` |
| `displayClientMessage(...)` | `sendSystemMessage(...)` / `sendOverlayMessage(...)` |
| `id().location()` | `id().identifier()` |
| `ChunkPos.toLong()` | `ChunkPos.pack()` |
| `getMinBlockY()` | `getMinY()` |
| `Items.GRAY_STAINED_GLASS_PANE` | `Items.STAINED_GLASS_PANE.gray()` |
| `ServerPlayer.getServer()` | `jugador.level().getServer()` |
| `TooltipDisplay.DEFAULT.withHideTooltip()` | `new TooltipDisplay(true, new LinkedHashSet<>())` |
| `Options.hideGui` | ya no existe: el F1 lo lleva el propio pipeline del HUD |
| `LevelReader.getBiome(pos)` | sigue ahí, pero **no** en `Level`: está en `LevelReader` |

Aparte, **una receta no puede pedir "una botella de agua" sin más**: todas las
pociones son el mismo item y solo se distinguen por su componente de contenido.
Hay que usar un ingrediente por componentes, que aporta Fabric:

```json
"ingredient": {
  "fabric:type": "fabric:components",
  "base": "minecraft:potion",
  "components": { "minecraft:potion_contents": { "potion": "minecraft:water" } }
}
```

Y tres trampas de dibujado que costaron una sesión cada una:

- **`blit` corto repite la textura en mosaico.** La firma corta usa el ancho de
  dibujo *también* como región de origen, así que pedir 850 píxeles de una textura
  de 256 la repite en vez de agrandarla. Para estirar hace falta la variante que
  separa el tamaño de dibujo de la región de origen.
- **El HUD estira con vecino más cercano**, así que una textura pequeña a pantalla
  completa se ve a bloques. La viñeta es de 256 por eso.
- **Vanilla hace parpadear el icono de todo efecto a punto de caducar.** Un efecto
  que se renueva cada dos segundos con poca cuerda parpadea sin parar aunque nunca
  se vaya. Hay que darle duración de sobra y renovarlo antes de entrar en esa
  franja.

Y seis cosas que solo se descubren mirando el bytecode:

- Los modificadores de atributo de tipo `ADD_MULTIPLIED_TOTAL` **se multiplican
  entre sí** (`valor *= 1 + cantidad`), no se suman. Por eso la compensación de la
  Pata Alada se despeja como `c = L·r / (1 − L)` y no como un simple +25 %.
- La herrería copia `getComponentsPatch()` de la pieza base, es decir **solo lo que
  se cambió en ese objeto concreto**, no los componentes por defecto. Por eso el
  casco Hazmat conserva su visor y sus 250 de durabilidad al mejorar un casco de
  hierro, en vez de heredar los 165 del hierro.
- El contexto de botín de la **pesca no tiene `LAST_DAMAGE_PLAYER`**, porque ahí
  no muere nadie. Pedir "matado por un jugador" en esa tabla no es que no filtre:
  revienta al tirarla. Por lo mismo, la condición de probabilidad con bonus por
  encantamiento tampoco sirve — lee `ATTACKING_ENTITY`, que la pesca tampoco
  aporta, así que se quedaría en la base para siempre **y sin dar ningún error**.
- El peso efectivo de una entrada de botín es
  `max(floor(peso + calidad · suerte), 0)`. Dándole al hueco vacío la misma
  calidad en negativo que al item, el total no se mueve y el porcentaje sube en
  línea recta con la suerte, sin la deriva que saldría si el denominador
  cambiara.
- **Dónde pinta vanilla el HUD de abajo**, que es lo que hay que esquivar para
  colocar cualquier medidor propio. Sale de `ContextualBar` y del HUD:

  | Y | Qué hay |
  |---|---|
  | `guiHeight - 29` | arriba de la barra de experiencia |
  | `guiHeight - 35` | el número de nivel, centrado |
  | `guiHeight - 39` | la fila de corazones y muslos |
  | `guiHeight - 49` | armadura (izquierda) y burbujas (derecha) |

  Los corazones acaban en `centerX - 11` y los muslos empiezan en `centerX + 10`,
  así que en el centro queda un **pasillo de unos 21 píxeles** libre de barras.
  Es donde va la gota.
- **Por qué parpadea el icono de un efecto.** `Hud` llama a `endsWithin(200)`: a
  todo efecto al que le queden 200 ticks o menos le desvanece el icono. Un efecto
  que se renueva sin cortes pero con cuerda corta **parpadea igualmente**, porque
  lo que mira vanilla es la cuerda que le queda, no si va a renovarse.

  De ahí salen los dos números que comparten los tres efectos del mod: cuerda de
  **600** y renovación al bajar de **400**, que deja 200 ticks de margen aunque el
  reparto por ranuras se salte varias vueltas.

  La contrapartida es que ninguno puede dejarse caducar solo: con esa cuerda, la
  radiación seguiría puesta medio minuto después de salir de la geoda. Los tres
  se **retiran a mano** en cuanto dejan de tocar.

## Versiones

Fijadas en `gradle.properties`:

| Componente | Versión |
|---|---|
| Minecraft | 26.2 |
| Fabric Loom | 1.17-SNAPSHOT |
| Fabric Loader | 0.19.3 |
| Fabric API | 0.156.0+26.2 |
| Java | 25 |

## Estructura

```
build.gradle            Loom, dependencias y generación de los idiomas
gradle.properties       versiones del toolchain y datos del mod

src/main/               código común (servidor + cliente)
├── java/com/atalaya/
│   ├── Atalaya.java                entrada común: registros y eventos
│   ├── command/AtalayaCommand      /atalaya (menú, pruebas, jefes) y /repair
│   ├── config/AtalayaConfig        interruptores, persistidos en JSON
│   ├── config/LibroRecetas         sincroniza el libro con los interruptores
│   ├── effect/RadiacionEffect      el efecto registrado y su lentitud
│   ├── effect/InsolacionEffect     el efecto y su tabla de escalones
│   ├── effect/CorrosionEffect      el efecto y el desgaste proporcional
│   ├── effect/EmpapadoEffect       el efecto y su lentitud
│   ├── effect/HipotermiaEffect     el efecto y su tabla de escalones
│   ├── effect/AturdimientoEffect   la cara visible de estar clavado
│   ├── effect/MarcadoEffect        la maldición del Vigía
│   ├── effect/CorrienteAbismal, BendicionMareas    los de Nerea
│   ├── effect/MarcaVendaval, BendicionVientos, Paralisis   los de Aeralis
│   ├── effect/PesoTierra, BendicionTierra          los de Rajang
│   ├── lluvia/LluviaManager        las DOS mecánicas de lluvia, en un bucle
│   ├── hidratacion/Hidratacion     el dato pegado al jugador (persiste y sincroniza)
│   ├── hidratacion/HidratacionManager   lo gasta en el desierto, por ranuras
│   ├── frio/Frio                   el dato pegado al jugador, al revés que la gota
│   ├── frio/FrioManager            lo sube en la nieve y lo baja junto al fuego
│   ├── aturdimiento/Aturdimiento   los ticks que quedan, pegados al jugador
│   ├── aturdimiento/AturdimientoManager  los descuenta, clava y bloquea
│   ├── entity/AtalayaEntities      los 18 tipos: atributos, aparición y bioma
│   ├── entity/FulminanteEntity     el creeper del desierto y su vitrificado
│   ├── entity/VigiaEntity          el Vigía, y RayoVigiaEntity su rayo
│   ├── entity/<Jefe>Entity         Nerea, Aeralis y Rajang: IA, ataques, fases, liberación
│   ├── entity/<Jefe>Geometria      GENERADO: ticks de golpe y puntos del cuerpo
│   ├── entity/<Jefe>Danos          las claves de sus tipos de daño
│   ├── entity/  (de Nerea)         BurbujaNerea, GanchoNerea
│   ├── entity/  (de Aeralis)       CuchillaViento, TornadoAeralis, RafagaAeralis, NucleoViento
│   ├── entity/  (de Rajang)        RajangParte (cajas de cabeza y grupa), PicoTierra,
│   │                               PilarTierra, TotemSello, PlataformaSello, FragmentoJade
│   ├── net/AtalayaRed              el paquete de espacio, cliente → servidor
│   ├── particula/AtalayaParticulas la estrella de aturdido y las del Vigía y los jefes
│   ├── sonido/AtalayaSonidos       los 128 eventos de sonido del Vigía y los jefes
│   ├── util/BotinSecreto           marca la arena que no enseña su premio
│   ├── item/AtalayaItems           items que no son armadura (huevos y piezas de jefe incluidos)
│   ├── item/OjoVigiaItem           el botín del Vigía
│   ├── item/AtalayaComponents      componentes de datos propios
│   ├── item/HazmatArmor            las cuatro piezas y sus umbrales
│   ├── item/HazmatArmorItem        tooltip generado al mostrarse
│   ├── item/FiltroCarbonItem       recarga el traje con clic derecho
│   ├── item/AguaPurificadaItem     se bebe y devuelve hidratación
│   ├── loot/AtalayaLoot            los cinco drops de mobs y el de la pesca
│   ├── menu/ConfigMenu             el panel de interruptores
│   ├── mixin/                      BlockItem, PoisonMobEffect, RecipeManager,
│   │                               Creeper, daño, vitrificado, ranura, botín,
│   │                               SpawnPlacements, y AvisoTotem (el tótem
│   │                               avisa a todo el servidor)
│   └── radiation/                  GeodeIndex (índice) y RadiationManager (tick)
└── resources/
    ├── fabric.mod.json             manifiesto
    ├── atalaya.mixins.json         mixins comunes
    ├── assets/atalaya/             texturas, modelos, equipo, idiomas
    └── data/atalaya/               recetas, avances, etiquetas

src/client/             código SOLO de cliente
├── java/com/atalaya/
│   ├── AtalayaClient.java          entrada de cliente
│   ├── client/AvisoTrajeHud        el triángulo de aviso
│   ├── client/HidratacionHud       la gota y la flecha
│   ├── client/FrioHud              el copo y las dos flechas
│   ├── client/VinetaHud            el halo, de calor o de frío
│   ├── client/AturdimientoHud      la barra espaciadora y su texto
│   ├── client/AturdimientoTeclado  cuenta flancos y se traga las teclas
│   ├── client/FulminanteModel      la malla del creeper más la hierba seca
│   ├── client/FulminanteRenderer   reusa el render del creeper con otra malla
│   ├── client/EstrellaParticula    la estrella que gira sobre la cabeza
│   ├── client/Vigia*, RayoVigia*   modelo, animaciones, ojos, partículas y rayo del Vigía
│   ├── client/<Jefe>Malla          GENERADO: la malla
│   ├── client/<Jefe>Animaciones    GENERADO: los keyframes, un método por animación
│   ├── client/<Jefe>Model          mezcla las animaciones, cadenas, cristales, latido
│   ├── client/<Jefe>Renderer       piel por fase, liberado y disolverse
│   ├── client/<Jefe>BrilloLayer    lo que brilla, por fase
│   ├── client/<Jefe>BarraHud       su barra de jefe, apilada
│   ├── client/<Jefe>EfectosCliente temblor, miedo y viento según lo que haga
│   ├── client/<Jefe>Particula      sus partículas, en una clase
│   ├── client/AeralisDibujo, RajangDibujo   geometría a mano de los proyectiles
│   ├── client/*Renderer            los de cada proyectil y pieza de ataque
│   ├── client/NereaPresencia       COMPARTIDO: temblor y miedo de los tres jefes
│   ├── client/MiedoHud             la viñeta de miedo, con la textura de cada jefe
│   ├── client/CadenaRender         los eslabones de las cadenas de Nerea
│   ├── client/FotosPrueba          capturas desde un datapack (desarrollo)
│   └── mixin/client/               visor translúcido, mareo suave y temblor de cámara
└── resources/atalaya.client.mixins.json

materiales/             todo lo que NO va al jar
├── generadores/        los scripts de Python de texturas, mallas, animaciones,
│                       sonidos, fichas y pósters (ver "Cómo se hace un jefe")
├── video/              los scripts de los teasers
├── promo/              pósters (.png) y teasers (.mp4) ya generados
├── plantillas/         plantillas para pintar la armadura
└── criolita.png        guardada sin conectar a nada

entrega/                el .jar compilado de la última versión
```

La separación `main` / `client` la impone `splitEnvironmentSourceSets()` en
`build.gradle`, y evita referenciar por error una clase de renderizado desde el
servidor.

### Idiomas

Minecraft tiene **siete variantes de español sin herencia entre ellas**: un jugador
con "Español (México)" no ve `es_es`. `processResources` genera las seis restantes
a partir de `es_es.json` en cada compilación, así que solo hay que mantener ese
fichero y `en_us.json`.

Los dos tienen **las mismas claves** (214), y todo lo de los jefes está traducido:
nombres, piezas, efectos, mensajes de muerte y los subtítulos de cada sonido. Al
añadir algo, va en los dos. Lo único que no pasa por los idiomas son los textos
del panel de configuración y de los comandos, que están escritos en español en el
código.

## Notas de rendimiento

Pensado para un servidor con aforo alto (~100 jugadores):

- **El bucle de radiación** reparte a los jugadores por tramos: cada tick procesa
  la fracción que le toca en vez de recorrer la lista entera, así que el coste no
  crece con el aforo.
- **El índice de geodas** se llena al cargar el chunk usando el descarte por
  paleta de la sección (`maybeHas`), que salta las secciones sin amatista sin
  mirar un solo bloque. Consultar "qué tengo cerca" solo mira los chunks vecinos y
  corta en cuanto encuentra algo lo bastante próximo.
- **El efecto solo se reenvía** cuando cambia de nivel o va a caducar, no cada
  segundo.
- **La hidratación reparte igual**, y ahí el reparto sale gratis: como cada
  jugador debe perder un punto cada 140 ticks, el intervalo del reparto *es* ese
  mismo número. Una vuelta por jugador, un punto, sin contadores propios ni un
  pico con todo el servidor a la vez.
- **La insolación lleva su propio bucle**, más rápido (40 ticks), porque de ella
  dependen cosas que se tienen que notar al momento. Y ese intervalo *es* el del
  daño: como cada jugador se procesa una vez por vuelta, el golpe cae solo cada
  2 s sin llevar ningún contador.
- **La lluvia hace lo mismo** con un intervalo de 20 ticks, que es a la vez su
  ritmo de mordisco: una vuelta por jugador y por segundo, una mordida por vuelta.
- **Corrosión y empapado comparten bucle.** La pregunta *¿te está lloviendo?* se
  hace una vez por jugador y sirve para las dos: separarlas sería pagar dos veces
  por lo mismo.
- **El frío lo hace todo en un bucle**, subir, bajar y repartir castigos. Puede
  porque tiene **dos ritmos**: se toma el rápido (1 s, entrar en calor) como
  intervalo y el lento (7 s, enfriarse) sale **contando vueltas**, una de cada
  siete. Sigue sin haber contadores por jugador.
- **Buscar una hoguera se descarta por la luz.** El barrido son casi mil bloques,
  así que antes se mira la luz de bloque, que es **una** consulta: si está oscuro
  no puede haber nada que caliente y se acaba ahí, que es el caso normal de
  alguien perdido en la nieve. Es la misma idea que el descarte por paleta del
  índice de geodas.
- **Los topes se comprueban antes de escribir.** El nivel se sincroniza, así que
  reescribir el mismo número sería un paquete por jugador y segundo para todo el
  que no pase frío, que van a ser casi todos.
- **El interruptor solo se manda al cliente cuando cambia**, no cada vuelta.

Las cuatro mecánicas comparten la misma forma: **el intervalo del reparto ES el
ritmo del efecto**, así que ninguna necesita un contador por jugador. Al añadir la
siguiente, conviene seguir el patrón.
- **Los medidores del HUD son del cliente**: al servidor no le cuestan nada. El
  del frío **cachea medio segundo** lo que le cuesta caro, porque se dibuja en cada
  fotograma y la respuesta solo puede cambiar una vez por segundo.
- **Los jefes no tienen bucle de servidor propio.** Cada uno se mueve en su
  `customServerAiStep`, sin goals de movimiento. Las animaciones se hornean en
  Python, así que en el juego no se calcula física ninguna. Lo que el jugador ve
  y no afecta al combate —el viento, las hojas, el temblor, el miedo— se calcula
  en el cliente.

## Jugar de verdad (no desarrollo)

Cada jugador necesita las tres cosas, con versiones que cuadren:

1. **Fabric Loader** para 26.2, desde [fabricmc.net/use](https://fabricmc.net/use/)
2. **Fabric API** `0.156.0+26.2` → carpeta `mods/`
3. **`atalaya-1.1.7.jar`** (el de `entrega/`) → carpeta `mods/`

El servidor necesita Fabric Loader y los mismos dos jars en su `mods/`. El mod es
obligatorio en cliente y servidor: el efecto de radiación, el visor, los jefes y
sus barras necesitan código de cliente.

## Pendientes y cosas que no cuadran

Lo que se encontró al repasar el proyecto entero (05-10-2026). No rompe nada
jugable, pero conviene saberlo antes de tocar cerca.

**Dependencias escondidas**

- **`NereaPresencia.tick()` solo se llama desde `NereaEfectosCliente`.** Si se
  quitara Nerea, el temblor y el miedo de Aeralis y Rajang no se apagarían nunca.
- **Las barras se apilan leyendo un campo estático** de la barra anterior
  (`NereaBarraHud.visible`, `AeralisBarraHud.visible`). El quinto jefe tiene que
  leer el de Rajang.

**Restos sin usar**

- **Sonido `rajang.totem_rehace`.** Sigue registrado, pero desde que los tótems
  del Sello dejaron de rehacerse nadie lo usa.
- **Las mejoras de Rajang de octubre de 2026 no se han probado en una partida.**
  Compilan y sus recursos cargan sin errores en el cliente de desarrollo, pero
  los números (velocidades, radios, lanzamientos) y las animaciones nuevas
  están por ajustar jugando.
- **Partícula `rajang_sello`.** Tiene sprites, pero el servidor no la emite nunca.
- **`rajang_coloso.png`.** El docstring de `rajang_juego.py` lo promete, pero no
  se genera. El "Coloso de Tierra" del Sello se quedó en la ficha de diseño.
- **`ATTACK_DAMAGE` de los jefes.** Ninguno pega cuerpo a cuerpo, así que no se
  usa.

**Comentarios desfasados** (los números buenos son los del código, los `DANO_*`):

- La cabecera de `NereaEntity` dice que la vida crece con el grupo. Es fija.
- En Nerea, los comentarios de "tres olas" y de la burbuja (8 de daño en 4
  bloques) son de antes del pase de balance.
- `AeralisEntity` cita a "Nerea, 11 250"; son 12 500.
- Varios comentarios de daño en `TornadoAeralis`, `CuchillaViento` y
  `NucleoViento` también son anteriores al balance.
- `AtalayaClient` dice que Nerea tiene "diez" partículas y Rajang "catorce"; son
  13 y 15.
- `fabric.mod.json` describe el mod sin Aeralis ni Rajang.
- `DISEÑO.md` dice que los scripts viven en el scratchpad. Hoy están en
  `materiales/generadores/`.

**Fallos pequeños**

- **`aeralis_teaser.py` invierte `xx` e `yy`** al leer la caché de la viñeta. La
  viñeta sale descentrada desde el plano del interior del tornado. Nerea y Rajang
  lo hacen bien.

**Repositorio**

- **`__pycache__/` está subido** (22 `.pyc`) y no está en `.gitignore`. Cambia
  cada vez que se ejecuta un script.
- **El `.git` pesa unos 125 MB.** Lo engordan los mp4, los jar y los pósters, y
  sigue dentro el vídeo borrado del Vigía. No se usa Git LFS.

## Enlaces útiles

- [Documentación de Fabric](https://docs.fabricmc.net/)
- [Mod de ejemplo oficial](https://github.com/FabricMC/fabric-example-mod)
- [Linkie (traductor de mappings)](https://linkie.shedaniel.dev/mappings)
- [Fabric API en Modrinth](https://modrinth.com/mod/fabric-api)
- [API de versiones de Fabric](https://meta.fabricmc.net/)
