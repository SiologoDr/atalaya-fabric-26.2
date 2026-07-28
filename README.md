# Atalaya

Mod de **Fabric** para Minecraft **26.2**.

> **Estado: base montada y validada. Todavía no hay contenido jugable.**
> El mod compila, Fabric lo carga, sus dos puntos de entrada arrancan y sus
> recursos se cargan dentro del juego. El traje Hazmat y la radiación aún no
> están implementados.

## Qué será

- **Radiación de geodas naturales:** acercarse a la *amatista en gemación* hace
  daño y ralentiza, escalado por cercanía.
- **Traje Hazmat:** armadura que protege de la radiación, con visor propio.
- **Guardián de Amatista:** un boss que defiende las geodas.

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

## Puesta en marcha (incluye otra máquina)

```bash
git clone https://github.com/SiologoDr/atalaya-fabric-26.2.git
cd atalaya-fabric-26.2

# Compilar. La primera vez descarga Minecraft y lo remapea: tarda varios minutos.
./gradlew build          # Windows: .\gradlew.bat build
```

El `.jar` queda en `build/libs/atalaya-1.0.0.jar`.

## Desarrollo

Una sola terminal, sin resource pack que servir ni que aceptar:

```bash
./gradlew runClient      # cliente de desarrollo con el mod cargado
./gradlew runServer      # servidor de desarrollo (para probar en red)
```

Los mundos, opciones y logs de esas tareas viven en `run/`, que no se sube.

Para comprobar que el mod carga, buscar estas líneas en el log:

```
Loading NN mods:
	- atalaya 1.0.0
(atalaya) Atalaya iniciado (Minecraft 26.2 / Fabric).
(atalaya) Atalaya (cliente) iniciado.
```

## ⚠️ Mappings de Mojang, no Yarn

Yarn **no publica mappings para la serie 26.x** (el último es 1.21.11), así que
este proyecto usa los **mappings oficiales de Mojang**, que es lo que aplica Loom
por defecto.

Consecuencia práctica: casi toda la documentación y los tutoriales de Fabric usan
nombres de Yarn, que **no coinciden** con los de aquí.

| Los tutoriales dicen (Yarn) | Aquí se llama (Mojang) |
|---|---|
| `Item.Settings` | `Item.Properties` |
| `Identifier` | `ResourceLocation` |
| `World` | `Level` |

Para traducir nombres: **[linkie.shedaniel.dev/mappings](https://linkie.shedaniel.dev/mappings)**.

**No añadir** `mappings loom.officialMojangMappings()` a `build.gradle`: este Loom
ya los usa por defecto y declararlos explícitamente rompe el build con
`Failed to find official mojang mappings for 26.2`.

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
build.gradle            Loom + dependencias
gradle.properties       versiones del toolchain y datos del mod
src/
├── main/               código común (servidor + cliente)
│   ├── java/com/atalaya/Atalaya.java          entrada común
│   └── resources/
│       ├── fabric.mod.json                    manifiesto del mod
│       └── assets/atalaya/                    texturas, modelos, fuente
└── client/             código SOLO de cliente (render, HUD, modelos)
    └── java/com/atalaya/AtalayaClient.java    entrada de cliente
materiales/plantillas/  plantillas de diseño de las texturas (no van al jar)
```

La separación `main` / `client` la impone `splitEnvironmentSourceSets()` en
`build.gradle`, y evita referenciar por error una clase de renderizado desde el
servidor.

## Jugar de verdad (no desarrollo)

Cada jugador necesita las tres cosas, con versiones que cuadren:

1. **Fabric Loader** para 26.2, desde [fabricmc.net/use](https://fabricmc.net/use/)
2. **Fabric API** `0.156.0+26.2` → carpeta `mods/`
3. **`atalaya-1.0.0.jar`** → carpeta `mods/`

El servidor necesita Fabric Loader y los mismos dos jars en su `mods/`.

## Enlaces útiles

- [Documentación de Fabric](https://docs.fabricmc.net/)
- [Mod de ejemplo oficial](https://github.com/FabricMC/fabric-example-mod)
- [Linkie (traductor de mappings)](https://linkie.shedaniel.dev/mappings)
- [Fabric API en Modrinth](https://modrinth.com/mod/fabric-api)
- [API de versiones de Fabric](https://meta.fabricmc.net/)
