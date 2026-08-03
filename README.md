# Atalaya

Mod de **Fabric** para Minecraft **26.2**.

Las geodas de amatista emiten radiación. Sobrevivir cerca de ellas exige un traje
Hazmat que se desgasta con la exposición y hay que mantener con filtros.

> **Esto es la primera fase, no el mod.** La idea es una dificultad que sube por
> etapas: cada una vuelve invivible una parte del mundo y desbloquea a la vez lo
> que hace falta para volver a entrar. La radiación y el traje son el patrón en
> pequeño — aparece el peligro, aparece la herramienta. Las fases las abre un
> operador desde el menú, así que se pueden anunciar como evento.

> **Estado: contenido jugable y probado en el cliente de desarrollo.**
> Traje Hazmat completo, tres mejoras de herrería, y **dos efectos propios
> registrados**: radiación en las geodas e insolación en el desierto, esta última
> con su hidratación y su agua purificada. Todo bajo un menú de configuración con
> 19 interruptores.

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

## Comandos

| Comando | Permiso | Qué hace |
|---|---|---|
| `/atalaya menu` | Operador | Abre el panel de configuración |
| `/atalaya hidratacion <0-50>` | Operador | Fija tu hidratación. Para probar: llegar al nivel 2 esperando al sol son casi seis minutos |

El traje no tiene comando para conseguirlo: se craftea, o se coge de la pestaña de
**Combate** en creativo. Los materiales están en **Ingredientes**.

## Configuración

Dos formas, equivalentes: el menú en el juego o `config/atalaya.json`.

El menú son 19 interruptores en tres filas, agrupados por lo que hacen:

```
[Radiación][Hidratación][ ][Abejas][Colmillo][Veneno][Espejo][Pata][Alón]   el MUNDO
[ ][Lingote][ ][Miel][ ][Plantilla][ ][Herrería][ ]                         el TRAJE
[Carbón][Filtro][ ][Alga][Lente][C.Venenoso][P.Alada][ ][Agua]              ITEMS
```

El reparto de cada fila dice algo:

- **Arriba** el hueco separa las dos *mecánicas* (radiación e hidratación) de los
  *seis drops*, que ya no caben espaciados.
- **Abajo** los pares pegados son las dos cadenas de dos pasos —
  carbón→filtro y alga→lente — y las sueltas son de un solo paso. Con siete
  interruptores solo quedan dos separadores, y se gastan en aislar la cadena del
  cartucho y en apartar el agua purificada, que es de la sed y no del traje.

Cada cadena está partida en sus pasos, así que puedes permitir el material y
bloquear la herrería, o al contrario. Apagar una receta **también la quita del
libro de recetas** de todos los jugadores conectados, al instante.

Los drops no son recetas, así que no tocan el libro: se filtran sobre el botín ya
generado y el cambio es inmediato, sin recargar datapacks.

Los campos que falten en el JSON entran activados, así que añadir mecánicas no
rompe una configuración existente.

---

## Requisitos

- **JDK 25** — obligatorio, ver el aviso de abajo
- **Git**
- No hace falta instalar Gradle: el proyecto trae el *Gradle Wrapper*.
- No hace falta instalar Fabric para desarrollar: `runClient` levanta un cliente
  con el mod ya cargado.

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

El `.jar` queda en `build/libs/atalaya-1.0.0.jar`.

Nada más hace falta: las versiones están fijadas en `gradle.properties` y las
dependencias las resuelve Gradle. Las carpetas `build/`, `run/` y `.gradle/` no se
suben y se regeneran solas.

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
	- atalaya 1.0.0
(atalaya) Atalaya iniciado (Minecraft 26.2 / Fabric).
(atalaya) Atalaya (cliente) iniciado.
```

> **Editar siempre en `src/`, nunca en `build/`.** `build/` es salida generada y
> se sobrescribe en la siguiente compilación.

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

Y cinco cosas que solo se descubren mirando el bytecode:

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
│   ├── command/AtalayaCommand      /atalaya menu
│   ├── config/AtalayaConfig        interruptores, persistidos en JSON
│   ├── config/LibroRecetas         sincroniza el libro con los interruptores
│   ├── effect/RadiacionEffect      el efecto registrado y su lentitud
│   ├── effect/InsolacionEffect     el efecto y su tabla de escalones
│   ├── hidratacion/Hidratacion     el dato pegado al jugador (persiste y sincroniza)
│   ├── hidratacion/HidratacionManager   lo gasta en el desierto, por ranuras
│   ├── item/AtalayaItems           items que no son armadura
│   ├── item/AtalayaComponents      componentes de datos propios
│   ├── item/HazmatArmor            las cuatro piezas y sus umbrales
│   ├── item/HazmatArmorItem        tooltip generado al mostrarse
│   ├── item/FiltroCarbonItem       recarga el traje con clic derecho
│   ├── item/AguaPurificadaItem     se bebe y devuelve hidratación
│   ├── loot/AtalayaLoot            los cinco drops de mobs y el de la pesca
│   ├── menu/ConfigMenu             el panel de interruptores
│   ├── mixin/                      BlockItem, PoisonMobEffect, RecipeManager
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
│   ├── client/InsolacionHud        el halo de calor
│   └── mixin/client/               visor translúcido y mareo suave
└── resources/atalaya.client.mixins.json

materiales/             plantillas de diseño de texturas (no van al jar)
```

La separación `main` / `client` la impone `splitEnvironmentSourceSets()` en
`build.gradle`, y evita referenciar por error una clase de renderizado desde el
servidor.

### Idiomas

Minecraft tiene **siete variantes de español sin herencia entre ellas**: un jugador
con "Español (México)" no ve `es_es`. `processResources` genera las seis restantes
a partir de `es_es.json` en cada compilación, así que solo hay que mantener ese
fichero y `en_us.json`.

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
- **El interruptor solo se manda al cliente cuando cambia**, no cada vuelta.
- **Los dos medidores del HUD son del cliente**: al servidor no le cuestan nada.

## Jugar de verdad (no desarrollo)

Cada jugador necesita las tres cosas, con versiones que cuadren:

1. **Fabric Loader** para 26.2, desde [fabricmc.net/use](https://fabricmc.net/use/)
2. **Fabric API** `0.156.0+26.2` → carpeta `mods/`
3. **`atalaya-1.0.0.jar`** → carpeta `mods/`

El servidor necesita Fabric Loader y los mismos dos jars en su `mods/`. El mod es
obligatorio en cliente y servidor: el efecto de radiación y el visor necesitan
código de cliente.

## Enlaces útiles

- [Documentación de Fabric](https://docs.fabricmc.net/)
- [Mod de ejemplo oficial](https://github.com/FabricMC/fabric-example-mod)
- [Linkie (traductor de mappings)](https://linkie.shedaniel.dev/mappings)
- [Fabric API en Modrinth](https://modrinth.com/mod/fabric-api)
- [API de versiones de Fabric](https://meta.fabricmc.net/)
