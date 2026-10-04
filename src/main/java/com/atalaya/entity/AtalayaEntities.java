package com.atalaya.entity;

import com.atalaya.Atalaya;
import com.atalaya.config.AtalayaConfig;
import com.atalaya.mixin.SpawnPlacementsInvoker;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.fabricmc.fabric.api.tag.convention.v2.ConventionalBiomeTags;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Creeper;

/**
 * Entidades propias del mod.
 *
 * Va aparte de los items porque el orden importa: el huevo generador necesita
 * que su tipo de entidad ya exista cuando se construye, asi que esto se registra
 * ANTES que {@link com.atalaya.item.AtalayaItems}.
 */
public final class AtalayaEntities {

    public static final ResourceKey<EntityType<?>> CLAVE_FULMINANTE = ResourceKey.create(
            Registries.ENTITY_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "fulminante"));

    public static EntityType<FulminanteEntity> FULMINANTE;

    public static final ResourceKey<EntityType<?>> CLAVE_VIGIA = ResourceKey.create(
            Registries.ENTITY_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "vigia"));

    public static EntityType<VigiaEntity> VIGIA;

    public static final ResourceKey<EntityType<?>> CLAVE_RAYO_VIGIA = ResourceKey.create(
            Registries.ENTITY_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "rayo_vigia"));

    /** El proyectil de la mirada. */
    public static EntityType<RayoVigiaEntity> RAYO_VIGIA;

    public static final ResourceKey<EntityType<?>> CLAVE_NEREA = clave("nerea");
    public static final ResourceKey<EntityType<?>> CLAVE_BURBUJA_NEREA = clave("burbuja_nerea");
    public static final ResourceKey<EntityType<?>> CLAVE_GANCHO_NEREA = clave("gancho_nerea");

    /** Nerea, Guardian de los Mares: el jefe elemental del agua. */
    public static EntityType<NereaEntity> NEREA;
    /** Burbuja bomba. */
    public static EntityType<BurbujaNereaEntity> BURBUJA_NEREA;
    /** El gancho del Arpon. */
    public static EntityType<GanchoNereaEntity> GANCHO_NEREA;

    private AtalayaEntities() {
    }

    private static ResourceKey<EntityType<?>> clave(String nombre) {
        return ResourceKey.create(Registries.ENTITY_TYPE, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, nombre));
    }

    public static void registrar() {
        // Las medidas son las del creeper clavadas, aunque el matojo asome por
        // encima. El arbusto es adorno: si la caja creciera con el, el bicho
        // chocaria con techos por los que un creeper pasa, y dejaria de moverse
        // como el original sin que se viera por que.
        FULMINANTE = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_FULMINANTE,
                EntityType.Builder.of(FulminanteEntity::new, MobCategory.MONSTER)
                        .sized(0.6F, 1.7F)
                        .eyeHeight(1.45F)
                        .clientTrackingRange(8)
                        .build(CLAVE_FULMINANTE));

        // Vida y demas, las del creeper. La velocidad NO: va un 50% mas rapido,
        // de 0,25 a 0,375. Con la mecha tan corta, que ademas corra es lo que lo
        // hace de verdad peligroso —un creeper normal te da tiempo a retroceder.
        FabricDefaultAttributeRegistry.register(FULMINANTE,
                Creeper.createAttributes().add(Attributes.MOVEMENT_SPEED, 0.375D));

        // Donde puede aparecer: en el suelo, y con las mismas condiciones de luz
        // que cualquier monstruo. Lo unico propio es la comprobacion del
        // interruptor.
        //
        // Aqui esta el truco para que el interruptor funcione EN CALIENTE. Las
        // apariciones por bioma se cierran al cargar el mundo y no se pueden
        // quitar luego, asi que el bicho queda apuntado en el desierto para
        // siempre. Lo que si se consulta cada vez que el juego se plantea sacar
        // uno es esta condicion, y ahi se mira la configuracion: apagar el
        // interruptor corta las apariciones al momento, sin reiniciar.
        SpawnPlacementsInvoker.atalaya$registrar(
                FULMINANTE,
                SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                (tipo, nivel, motivo, pos, azar) ->
                        AtalayaConfig.get().isFulminanteActivo()
                                && Monster.checkMonsterSpawnRules(tipo, nivel, motivo, pos, azar));

        // Y en que biomas. El peso es bajo a proposito: el desierto ya tiene sus
        // monstruos, y este pega mucho mas fuerte que cualquiera de ellos. En
        // grupos de uno a dos, que tres a la vez no habria quien los esquive.
        BiomeModifications.addSpawn(
                BiomeSelectors.tag(ConventionalBiomeTags.IS_DESERT),
                MobCategory.MONSTER, FULMINANTE, 12, 1, 2);

        registrarVigia();
        registrarNerea();
    }

    private static void registrarNerea() {
        // La caja es mas estrecha que los hombros (4,3 de lado a lado) y mas
        // baja que la corona de coral (9,7): lo que importa es que tape el
        // cuerpo para pegarle, no cada rama. Se ve desde lejos: con 30 o 40
        // jugadores alrededor, la pelea ocupa mucho.
        NEREA = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_NEREA,
                EntityType.Builder.of(NereaEntity::new, MobCategory.MONSTER)
                        .sized(3.4F, 8.8F)
                        .eyeHeight(7.8F)
                        .fireImmune()
                        .clientTrackingRange(20)
                        .build(CLAVE_NEREA));
        FabricDefaultAttributeRegistry.register(NEREA, NereaEntity.crearAtributos());

        // Las dos que se mueven, cada tick: la burbuja cambia de rumbo y el
        // gancho va pegado a quien arrastra.
        BURBUJA_NEREA = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_BURBUJA_NEREA,
                EntityType.Builder.<BurbujaNereaEntity>of(BurbujaNereaEntity::new, MobCategory.MISC)
                        .sized(0.9F, 0.9F)
                        .clientTrackingRange(10)
                        .updateInterval(1)
                        .build(CLAVE_BURBUJA_NEREA));
        GANCHO_NEREA = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_GANCHO_NEREA,
                EntityType.Builder.<GanchoNereaEntity>of(GanchoNereaEntity::new, MobCategory.MISC)
                        .sized(0.5F, 0.5F)
                        .clientTrackingRange(10)
                        .updateInterval(1)
                        .build(CLAVE_GANCHO_NEREA));
    }

    private static void registrarVigia() {
        // 2,9 de alto, como el enderman: NO cabe por un tunel de dos bloques.
        // Es a proposito y es la otra salida contra el, ademas de cortarle la
        // vista: meterse bajo techo bajo.
        VIGIA = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_VIGIA,
                EntityType.Builder.of(VigiaEntity::new, MobCategory.MONSTER)
                        .sized(0.9F, 2.9F)
                        .eyeHeight(2.45F)
                        .clientTrackingRange(10)
                        .build(CLAVE_VIGIA));

        FabricDefaultAttributeRegistry.register(VIGIA, VigiaEntity.crearAtributos());

        // El rayo: caja pequena para que acertar dependa de apuntar, y
        // actualizacion cada tick, que a 25 bloques por segundo cualquier
        // otra cosa se veria a saltos.
        RAYO_VIGIA = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_RAYO_VIGIA,
                EntityType.Builder.<RayoVigiaEntity>of(RayoVigiaEntity::new, MobCategory.MISC)
                        .sized(0.4F, 0.4F)
                        .clientTrackingRange(8)
                        .updateInterval(1)
                        .build(CLAVE_RAYO_VIGIA));

        // Igual que el fulminante: el interruptor se mira en cada intento de
        // aparicion, asi que apagarlo corta al momento sin reiniciar.
        SpawnPlacementsInvoker.atalaya$registrar(
                VIGIA,
                SpawnPlacementTypes.ON_GROUND,
                Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
                (tipo, nivel, motivo, pos, azar) ->
                        AtalayaConfig.get().isVigiaActivo()
                                && Monster.checkMonsterSpawnRules(tipo, nivel, motivo, pos, azar));

        // Todo el mundo normal, pero raro y de uno en uno: es un minijefe, no
        // un monstruo de relleno. Con peso 3 frente a los 100 del zombi sale
        // alguno por noche en una zona grande, no uno en cada colina.
        BiomeModifications.addSpawn(
                BiomeSelectors.foundInOverworld(),
                MobCategory.MONSTER, VIGIA, 3, 1, 1);
    }
}
