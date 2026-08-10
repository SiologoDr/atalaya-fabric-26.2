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

    private AtalayaEntities() {
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
    }
}
