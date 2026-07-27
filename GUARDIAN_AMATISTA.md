# Guardián de Amatista — plan para continuar

> Documento para retomar el trabajo del **boss que protege las geodas**, basado en el
> *Amethyst Crab* del mod **Cataclysm**. Léelo al empezar en la otra PC.

## Contexto del proyecto

Plugin **Atalaya** (Paper 26.2), server-side, cliente vanilla + resource pack.
Ya está hecho (ver [README.md](README.md)): radiación de geodas, traje Hazmat,
menú de config, recetas, etc.

**Objetivo nuevo:** una entidad **"Guardián de Amatista"** que protege las geodas.

## Decisión técnica (IMPORTANTE — ya definida)

- ❌ **NO** usamos ModelEngine (descartado por el usuario).
- Consecuencia: **no se puede mostrar el modelo custom del cangrejo** a clientes
  vanilla (limitación técnica; los modelos de item/bloque no soportan las
  rotaciones libres de un cangrejo orgánico → saldría cuadrado/feo).
- ✅ **Ruta elegida:** **comportamiento fiel** + **cuerpo de un mob vanilla
  reskineado** (textura morada/amatista) + **animaciones mínimas** (telegrafía
  de ataques con movimiento y partículas). El usuario pidió "lo mínimo de
  animación, que se vea que ataca".
- Fidelidad: **comportamiento = fiel**; **visual = mob vanilla reskineado**
  (no la forma del crab).

## Assets extraídos → carpeta `crab_export/`

- `amethyst_crab.png` (256×256) — textura del modelo original. **Referencia**
  (no se usa directo sin ModelEngine; está mapeada al modelo del crab).
- `crab_bite.ogg`, `crab_death.ogg` — **sonidos** (sí usables en el resource pack).
- `referencia/Amethyst_Crab_Model.java` — geometría decompilada (por si algún día
  se usa ModelEngine).
- `referencia/Amethyst_Crab_Entity.java` — comportamiento decompilado (fuente de
  la spec de abajo).

## Spec del boss (del mod original, ya decompilada)

| Stat | Valor |
|---|---|
| Vida (MAX_HEALTH) | **200** |
| Daño (ATTACK_DAMAGE) | 13 |
| Armadura (ARMOR) | 10 |
| Velocidad (MOVEMENT_SPEED) | 0.28 |
| Resistencia a empuje (KNOCKBACK_RESISTANCE) | **1.0 (inmune)** |
| Step height | 1.5 |
| Follow range | 20 |

**Ataques / animaciones (ticks):**
- **CRAB_SMASH** (53t) — golpe de pinza; daño en el tick 22.
- **CRAB_SMASH_THREE** (77t) — combo/triple smash.
- **CRAB_BURROW** (65t) — se entierra; **invulnerable** en ticks 9–52; cooldown
  240t (**12s**).
- **CRAB_BITE** — mordida melee.
- **CRAB_DEATH**.

**Goals (IA original):** `CrabMoveGoal`, `CrabSmashGoal`, `CrabAttack(smash_three)`,
`CrabBurrow` + vanilla (RandomStroll, LookAtPlayer, RandomLookAround, HurtByTarget).
Es un **Monster** hostil (boss).

## Plan de implementación (en nuestro plugin)

**Fase 1 — Comportamiento (no depende de nada de pago):**
1. Clase del guardián: spawnear un mob base con atributos custom (200 HP,
   armadura 10, KB resist 1.0, speed 0.28, daño 13). Marca con PDC como "guardián".
2. **Reskin:** textura morada/amatista para el mob base vía resource pack
   (hay que **crear una textura nueva** que mapee al mob base; la del crab no sirve).
3. **IA custom** (usando la spec):
   - Aggro a jugadores que se acerquen a la geoda / la dañen.
   - **Smash:** daño de área + partículas + sonido (`crab_bite.ogg`).
   - **Burrow:** invulnerable ~2s + reposicionar (teleport cerca del objetivo) +
     cooldown 12s + partículas de tierra.
   - **Bite:** melee.
4. **Integración con geodas:** usar `GeodeIndex`
   (`src/main/java/com/atalaya/radiation/GeodeIndex.java`) para saber dónde están
   las geodas; el guardián protege la más cercana / aparece ahí.
5. **Spawn:** definir cómo aparece (natural cerca de geodas grandes, o comando
   `/atalaya guardian` para pruebas). Empezar con comando de prueba.
6. (Opcional) **BossBar** con la vida del guardián.

**Fase 2 — Visual fiel (solo si algún día se consigue ModelEngine):**
usar el modelo/animaciones del crab (geometría ya extraída en `crab_export/referencia/`).

## Decisiones pendientes al retomar

1. ✅ Ruta confirmada: comportamiento fiel + reskin (animación mínima).
2. ⏳ **Elegir mob base** (candidato: **Ravager** — corpulento, embiste y muerde;
   alternativa: Warden). *(El usuario aún no confirmó cuál.)*
3. ⏳ Crear la **textura morada** para ese mob base.
4. ⏳ Definir el **spawn** (natural vs comando).

## Cómo retomar en la otra PC

1. `git clone` o `git pull` del repo.
2. Levantar el entorno según el [README.md](README.md): JDK 25, `gradlew build`,
   y para el pack `python dev.py` + `gradlew runServer`.
3. Los assets del crab están en `crab_export/`.
4. Continuar con la **Fase 1** (IA del boss).

## Notas

- La carpeta `mod/` (mod Cataclysm completo, decompilado) **NO** está en Git
  (es grande y no es nuestro código). Si se necesita, re-extraer del `.jar` del mod.
- Sin legalidad de por medio: es un server privado entre amigos.
