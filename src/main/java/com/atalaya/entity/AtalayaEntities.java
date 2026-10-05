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

    public static final ResourceKey<EntityType<?>> CLAVE_AERALIS = clave("aeralis");
    public static final ResourceKey<EntityType<?>> CLAVE_CUCHILLA_VIENTO = clave("cuchilla_viento");
    public static final ResourceKey<EntityType<?>> CLAVE_TORNADO_AERALIS = clave("tornado_aeralis");
    public static final ResourceKey<EntityType<?>> CLAVE_RAFAGA_AERALIS = clave("rafaga_aeralis");
    public static final ResourceKey<EntityType<?>> CLAVE_NUCLEO_VIENTO = clave("nucleo_viento");
    public static final ResourceKey<EntityType<?>> CLAVE_RAJANG = clave("rajang");
    public static final ResourceKey<EntityType<?>> CLAVE_RAJANG_PARTE = clave("rajang_parte");
    public static final ResourceKey<EntityType<?>> CLAVE_PICO_TIERRA = clave("pico_tierra");
    public static final ResourceKey<EntityType<?>> CLAVE_PILAR_TIERRA = clave("pilar_tierra");
    public static final ResourceKey<EntityType<?>> CLAVE_TOTEM_SELLO = clave("totem_sello");
    public static final ResourceKey<EntityType<?>> CLAVE_PLATAFORMA_SELLO = clave("plataforma_sello");
    public static final ResourceKey<EntityType<?>> CLAVE_FRAGMENTO_JADE = clave("fragmento_jade");

    /** Aeralis, la Mariposa del Vendaval: el jefe elemental del aire. */
    public static EntityType<AeralisEntity> AERALIS;
    /** Las cuchillas del Aleteo Cortante. */
    public static EntityType<CuchillaVientoEntity> CUCHILLA_VIENTO;
    /** Los tornados (y el ciclon del Juicio). */
    public static EntityType<TornadoAeralisEntity> TORNADO_AERALIS;
    /** Las rafagas de La Caceria. */
    public static EntityType<RafagaAeralisEntity> RAFAGA_AERALIS;
    /** Los cuatro nucleos del Juicio. */
    public static EntityType<NucleoVientoEntity> NUCLEO_VIENTO;

    /** Rajang, el Jaguar de Jade: el jefe elemental de la tierra. */
    public static EntityType<RajangEntity> RAJANG;
    /** Sus cajas de golpe de la cabeza y la grupa. */
    public static EntityType<RajangParteEntity> RAJANG_PARTE;
    /** Los picos de la Garra Terrestre. */
    public static EntityType<PicoTierraEntity> PICO_TIERRA;
    /** Los pilares del Terremoto Ancestral. */
    public static EntityType<PilarTierraEntity> PILAR_TIERRA;
    /** Los totems del Sello de la Tierra. */
    public static EntityType<TotemSelloEntity> TOTEM_SELLO;
    /** Las plataformas de roca del Sello y sus piedras para subir saltando. */
    public static EntityType<PlataformaSelloEntity> PLATAFORMA_SELLO;
    /** Los fragmentos del Cataclismo de Jade. */
    public static EntityType<FragmentoJadeEntity> FRAGMENTO_JADE;

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
        registrarAeralis();
        registrarRajang();
    }

    private static void registrarAeralis() {
        // La caja tapa el cuerpo, de la punta del abdomen a la cabeza (10
        // bloques): las alas (22 de punta a punta) y las antenas quedan fuera,
        // las flechas las atraviesan. Se ve desde muy lejos.
        AERALIS = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_AERALIS,
                EntityType.Builder.of(AeralisEntity::new, MobCategory.MONSTER)
                        .sized(3.6F, 10.0F)
                        .eyeHeight(9.0F)
                        .fireImmune()
                        .clientTrackingRange(24)
                        .updateInterval(1)
                        .build(CLAVE_AERALIS));
        FabricDefaultAttributeRegistry.register(AERALIS, AeralisEntity.crearAtributos());

        // Lo que vuela o se mueve, cada tick. Nada de esto se guarda con el
        // mundo: es del ataque que lo lanzo.
        CUCHILLA_VIENTO = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_CUCHILLA_VIENTO,
                EntityType.Builder.<CuchillaVientoEntity>of(CuchillaVientoEntity::new, MobCategory.MISC)
                        .sized(2.0F, 0.8F)
                        .clientTrackingRange(10)
                        .updateInterval(1)
                        .build(CLAVE_CUCHILLA_VIENTO));
        TORNADO_AERALIS = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_TORNADO_AERALIS,
                EntityType.Builder.<TornadoAeralisEntity>of(TornadoAeralisEntity::new, MobCategory.MISC)
                        .sized(2.6F, 7.0F)
                        .fireImmune()
                        .clientTrackingRange(12)
                        .updateInterval(1)
                        .build(CLAVE_TORNADO_AERALIS));
        RAFAGA_AERALIS = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_RAFAGA_AERALIS,
                EntityType.Builder.<RafagaAeralisEntity>of(RafagaAeralisEntity::new, MobCategory.MISC)
                        .sized(1.2F, 1.2F)
                        .clientTrackingRange(10)
                        .updateInterval(1)
                        .build(CLAVE_RAFAGA_AERALIS));
        NUCLEO_VIENTO = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_NUCLEO_VIENTO,
                EntityType.Builder.<NucleoVientoEntity>of(NucleoVientoEntity::new, MobCategory.MISC)
                        .sized(1.6F, 1.6F)
                        .fireImmune()
                        .clientTrackingRange(12)
                        .build(CLAVE_NUCLEO_VIENTO));
    }

    private static void registrarRajang() {
        // La caja tapa el pecho y las patas de delante (el origen va al pecho):
        // la cabeza y la grupa llevan cajas propias. Se ve desde muy lejos. Su
        // posicion se manda cada tick: a 17-20 bloques/s, cada dos se veia a saltos.
        RAJANG = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_RAJANG,
                EntityType.Builder.of(RajangEntity::new, MobCategory.MONSTER)
                        .sized(6.0F, 7.6F)
                        .eyeHeight(6.2F)
                        .fireImmune()
                        .clientTrackingRange(24)
                        .updateInterval(1)
                        .build(CLAVE_RAJANG));
        FabricDefaultAttributeRegistry.register(RAJANG, RajangEntity.crearAtributos());

        // Lo suyo: nada se guarda con el mundo, es del ataque que lo saco.
        RAJANG_PARTE = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_RAJANG_PARTE,
                EntityType.Builder.<RajangParteEntity>of(RajangParteEntity::new, MobCategory.MISC)
                        .sized(3.0F, 3.0F)
                        .fireImmune()
                        .noSummon()
                        .clientTrackingRange(24)
                        .updateInterval(1)
                        .build(CLAVE_RAJANG_PARTE));
        PICO_TIERRA = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_PICO_TIERRA,
                EntityType.Builder.<PicoTierraEntity>of(PicoTierraEntity::new, MobCategory.MISC)
                        .sized(2.6F, 6.0F)
                        .fireImmune()
                        .noSummon()
                        .clientTrackingRange(16)
                        .updateInterval(20)
                        .build(CLAVE_PICO_TIERRA));
        PILAR_TIERRA = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_PILAR_TIERRA,
                EntityType.Builder.<PilarTierraEntity>of(PilarTierraEntity::new, MobCategory.MISC)
                        .sized(4.4F, 5.4F)
                        .fireImmune()
                        .noSummon()
                        .clientTrackingRange(16)
                        .updateInterval(20)
                        .build(CLAVE_PILAR_TIERRA));
        TOTEM_SELLO = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_TOTEM_SELLO,
                EntityType.Builder.<TotemSelloEntity>of(TotemSelloEntity::new, MobCategory.MISC)
                        .sized(1.6F, 4.9F)
                        .fireImmune()
                        .noSummon()
                        .clientTrackingRange(16)
                        .build(CLAVE_TOTEM_SELLO));
        PLATAFORMA_SELLO = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_PLATAFORMA_SELLO,
                EntityType.Builder.<PlataformaSelloEntity>of(PlataformaSelloEntity::new, MobCategory.MISC)
                        .sized(3.0F, 13.0F)
                        .fireImmune()
                        .noSummon()
                        .clientTrackingRange(16)
                        .updateInterval(1)
                        .build(CLAVE_PLATAFORMA_SELLO));
        FRAGMENTO_JADE = Registry.register(BuiltInRegistries.ENTITY_TYPE, CLAVE_FRAGMENTO_JADE,
                EntityType.Builder.<FragmentoJadeEntity>of(FragmentoJadeEntity::new, MobCategory.MISC)
                        .sized(1.0F, 1.0F)
                        .fireImmune()
                        .noSummon()
                        .clientTrackingRange(16)
                        .updateInterval(1)
                        .build(CLAVE_FRAGMENTO_JADE));
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
