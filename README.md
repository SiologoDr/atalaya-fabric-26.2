# Atalaya

Plugin **server-side** para Minecraft **26.2** (servidor [Paper](https://papermc.io/)).
Todo el contenido (items, eventos, mecánicas) corre en el servidor: los jugadores
entran con su Minecraft normal, **sin instalar nada**.

## Requisitos

- **Java 25** (JDK) — necesario para la 26.2.
- Un servidor **Paper 26.2** para probar.
- No necesitas instalar Gradle: el proyecto trae el *Gradle Wrapper*.

## Compilar

```bash
./gradlew build       # Linux / macOS / Git Bash
.\gradlew.bat build   # Windows (PowerShell / CMD)
```

El `.jar` final queda en `build/libs/atalaya-1.0.0.jar`.
Cópialo a la carpeta `plugins/` de tu servidor Paper y reinícialo.

## Contenido de ejemplo incluido

- **Item custom:** *Bastón de la Atalaya* (click derecho → invoca un rayo).
- **Comando:** `/atalaya baston` — te entrega el ítem.
- **Evento:** mensaje de bienvenida al entrar al servidor.

## Estructura

```
src/main/java/com/atalaya/
├── Atalaya.java              # Clase principal (onEnable / onDisable)
├── commands/AtalayaCommand   # Comando /atalaya
├── items/CustomItems         # Fábrica de items custom
└── listeners/                # Eventos (join, interacción con items)
src/main/resources/plugin.yml # Metadatos del plugin
```

## Nota sobre "secreto" del contenido

Cualquier item con **textura nueva** requiere un resource pack en el cliente,
que puede extraerse (dataminear). Para contenido que deba ser sorpresa, usa
apariencia vanilla + comportamiento custom (como el Bastón): así **no hay nada**
en la máquina del jugador que se pueda espiar.
