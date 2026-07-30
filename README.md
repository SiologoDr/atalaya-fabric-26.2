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
> Traje Hazmat completo, radiación como efecto propio registrado, tres mejoras de
> herrería y un menú de configuración con 17 interruptores.

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

## Comandos

| Comando | Permiso | Qué hace |
|---|---|---|
| `/atalaya menu` | Operador | Abre el panel de configuración |

El traje no tiene comando para conseguirlo: se craftea, o se coge de la pestaña de
**Combate** en creativo. Los materiales están en **Ingredientes**.

## Configuración

Dos formas, equivalentes: el menú en el juego o `config/atalaya.json`.

El menú son 17 interruptores en tres filas, agrupados por lo que hacen:

```
[Radiación][ ][ ][Abejas][Colmillo][Veneno][Espejo][Pata][Alón]   lo que da el MUNDO
[ ][Lingote][ ][Miel][ ][Plantilla][ ][Herrería][ ]               fabricar el TRAJE
[Carbón][Filtro][ ][Alga][Lente][ ][C.Venenoso][ ][P.Alada]       ITEMS y mejoras
```

El reparto de cada fila dice algo:

- **Arriba** el hueco doble separa la *mecánica* (radiación) de los *seis drops*,
  que ya no caben espaciados.
- **Abajo** los pares pegados son las dos cadenas de dos pasos —
  carbón→filtro y alga→lente — y las sueltas son de un solo paso.

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

Y cuatro cosas que solo se descubren mirando el bytecode:

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
│   ├── item/AtalayaItems           items que no son armadura
│   ├── item/AtalayaComponents      componentes de datos propios
│   ├── item/HazmatArmor            las cuatro piezas y sus umbrales
│   ├── item/HazmatArmorItem        tooltip generado al mostrarse
│   ├── item/FiltroCarbonItem       recarga con clic derecho
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
│   └── mixin/client/               visor translúcido
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
- **El aviso del HUD es del cliente**: al servidor no le cuesta nada.

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
