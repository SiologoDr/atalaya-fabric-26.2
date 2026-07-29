package com.atalaya.loot;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.item.AtalayaItems;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemKilledByPlayerCondition;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;

/**
 * Anade el colmillo venenoso al botin de las aranas de cueva.
 *
 * No se reescribe la tabla de vanilla: se le engancha una piscina propia, asi
 * que sigue soltando su hilo y su ojo de arana con normalidad y otros mods
 * pueden anadir lo suyo sin pisarse.
 */
public final class ColmilloLoot {

    private static final Identifier ARANA_DE_CUEVA =
            Identifier.withDefaultNamespace("entities/cave_spider");

    /**
     * Probabilidad de que suelte el colmillo.
     *
     * De referencia: el ojo de arana cae un 33% del tiempo, asi que el colmillo
     * sigue siendo notablemente mas raro (1 de cada 5 frente a 1 de cada 3).
     */
    private static final float PROBABILIDAD = 0.20f;

    private ColmilloLoot() {
    }

    public static void registrar() {
        LootTableEvents.MODIFY.register((clave, constructor, origen, registros) -> {
            if (!ARANA_DE_CUEVA.equals(clave.identifier())) {
                return;
            }
            constructor.pool(LootPool.lootPool()
                    .setRolls(ConstantValue.exactly(1))
                    .add(LootItem.lootTableItem(AtalayaItems.COLMILLO_VENENOSO))
                    .when(LootItemRandomChanceCondition.randomChance(PROBABILIDAD))
                    // Solo si la mata un jugador, como hace vanilla con el ojo
                    // de arana. Sin esto una granja automatica los produciria
                    // en masa y el colmillo dejaria de ser raro.
                    .when(LootItemKilledByPlayerCondition.killedByPlayer())
                    .build());
        });

        // El interruptor se aplica AQUI y no como condicion de la tabla: una
        // condicion propia habria que registrarla con su codec, y ademas las
        // tablas solo se releen al recargar datapacks. Filtrando los drops ya
        // generados, apagarlo tiene efecto inmediato.
        LootTableEvents.MODIFY_DROPS.register((tabla, contexto, drops) -> {
            if (!AtalayaConfig.get().isColmilloActivo()) {
                drops.removeIf(pila -> pila.is(AtalayaItems.COLMILLO_VENENOSO));
            }
        });
    }
}
