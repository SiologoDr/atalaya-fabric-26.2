# Atalaya

Plugin **server-side** para Minecraft **26.2** (servidor [Paper](https://papermc.io/)).
Todo el contenido (items, mecánicas, efectos) corre en el servidor: los jugadores
entran con su Minecraft normal, **sin instalar ningún mod**. Las texturas custom
se envían con un **resource pack** automático.

## Contenido

- **Radiación de geodas naturales:** al acercarte a la *amatista en gemación*
  (solo generada por el mundo) recibes daño y **lentitud**, escalados por nivel
  (más cerca = más fuerte). El efecto se muestra como un ícono en el HUD.
- **Traje Hazmat:** armadura (base hierro) que **protege de la radiación**
  (−25% por pieza, traje completo = inmune). Íconos y textura custom, recetas
  de crafteo (hierro recubierto de oro) y **no se puede renombrar** en yunque.
- **Menú de administración:** `/atalaya menu` para activar/desactivar mecánicas.

## Requisitos

- **JDK 25** (necesario para la 26.2)
- **Git**
- **Python 3** (solo para servir el resource pack en desarrollo)
- **Minecraft Java 26.2** (cliente, para probar)
- No necesitas instalar Gradle: el proyecto trae el *Gradle Wrapper*.

> Nota: en Git viaja el **código** y la carpeta **`resourcepack/`**.
> La carpeta **`run/`** (servidor de pruebas, EULA, ops, mundo) es local y NO se sube.

## Puesta en marcha (incluye otra máquina)

```bash
git clone https://github.com/SiologoDr/atalaya-plugin-26.2.git
cd atalaya-plugin-26.2

# 1) Compilar (baja Gradle + paper-api automáticamente)
./gradlew build          # Windows: .\gradlew.bat build

# 2) Primera vez: genera run/ y descarga Paper
./gradlew runServer      # Windows: .\gradlew.bat runServer
#    (deténlo con Ctrl+C tras el primer arranque)
```

El `.jar` compilado queda en `build/libs/atalaya-1.0.0.jar` (para un servidor real,
cópialo a la carpeta `plugins/`).

## Flujo de desarrollo (con resource pack)

Necesitas **dos terminales**:

```bash
# Terminal 1 — empaqueta el pack, configura y lo sirve (dejar abierta)
python dev.py

# Terminal 2 — compila el plugin y arranca el servidor de pruebas
./gradlew runServer      # Windows: .\gradlew.bat runServer
```

Luego en Minecraft: **Multijugador → Conexión directa → `localhost`** y acepta el pack.

- Para ser **admin**: en la consola del servidor escribe `op TU_USUARIO`
  (o edita `run/ops.json`).
- **Cada vez que cambies texturas** del `resourcepack/`: vuelve a correr
  `python dev.py` (regenera el zip y el SHA1) y reinicia el servidor.

> `dev.py` acepta el EULA, empaqueta `resourcepack/` en `run/pack-host/atalaya.zip`,
> configura `run/server.properties` y sirve el pack en `http://127.0.0.1:8765`.
> Si aún no existe `run/server.properties`, corre `runServer` una vez primero.

## Comandos

| Comando | Descripción | Permiso |
|---|---|---|
| `/atalaya traje` | Te da el traje Hazmat completo | — |
| `/atalaya menu` | Panel para activar/desactivar mecánicas | `atalaya.admin` (op) |
| `/atalaya reload` | Recarga `config.yml` | — |

## Configuración (`config.yml`)

```yaml
radiacion:
  activa: true            # on/off de la radiación (también desde /atalaya menu)
  intervalo-ticks: 20     # cada cuánto se revisa (20 = 1 s)
  distancia-maxima: 12    # radio de la radiación
  dano-por-nivel: {1:1.0, 2:2.0, 3:3.0, 4:4.0}       # daño (2 = 1 corazón)
  lentitud-por-nivel: {1:0.10, 2:0.20, 3:0.30, 4:0.50}  # % de velocidad restada
  escaneo-y-min: -64      # rango de altura donde se buscan geodas (optimización)
  escaneo-y-max: 40
hazmat:
  crafteo-activo: true    # on/off del crafteo del traje (también desde el menú)
```

## Estructura

```
src/main/java/com/atalaya/
├── Atalaya.java                  # Clase principal (onEnable / onDisable)
├── Settings.java                 # Estado persistente (toggles)
├── commands/AtalayaCommand       # Comando /atalaya (+ autocompletado)
├── items/
│   ├── HazmatArmor               # Piezas del traje (item + equipment + protección)
│   └── HazmatRecipes             # Recetas + libro de recetas
├── listeners/
│   ├── PlayerJoinListener        # Bienvenida + desbloqueo de recetas
│   └── AnvilListener             # Bloquea renombrar piezas Hazmat
├── menu/                         # Menú GUI de configuración
└── radiation/
    ├── RadiationManager          # Daño + lentitud por nivel (consulta el índice)
    ├── GeodeIndex                # Caché de geodas (escaneo async, escala a 100+)
    ├── GeodeListener             # Mantiene el índice al día
    └── RadiationSources          # Qué bloque emite radiación (budding_amethyst)
resourcepack/                     # Texturas, modelos y equipment del pack
dev.py                            # Empaqueta y sirve el resource pack (desarrollo)
```

## Servidor real (producción)

`dev.py` usa `localhost` solo para desarrollo. En un servidor público:
sube el `atalaya.zip` a una **URL permanente** y pon `resource-pack` y
`resource-pack-sha1` en tu `server.properties`.

## Nota sobre el "secreto" del contenido

Cualquier item con **textura nueva** vive en el resource pack, que se cachea en
el cliente y puede extraerse (dataminear). Para contenido que deba ser sorpresa,
usa apariencia vanilla + comportamiento custom. La **radiación** en cambio es
100% server-side (nada que espiar).
