package com.atalaya.loot;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.item.AtalayaItems;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemKilledByPlayerCondition;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;

/**
 * Los drops que el mod anade al botin de mobs de vanilla.
 *
 * No se reescribe ninguna tabla: a cada una se le engancha una piscina propia,
 * asi que los mobs siguen soltando lo suyo con normalidad y otros mods pueden
 * anadir lo que quieran sin pisarse.
 */
public final class AtalayaLoot {

    private static final Identifier ARANA =
            Identifier.withDefaultNamespace("entities/spider");

    private static final Identifier ARANA_DE_CUEVA =
            Identifier.withDefaultNamespace("entities/cave_spider");

    private static final Identifier ABEJA =
            Identifier.withDefaultNamespace("entities/bee");

    /**
     * Probabilidad del colmillo en la arana comun.
     *
     * De referencia: el ojo de arana cae un 33% del tiempo, asi que el colmillo
     * es notablemente mas raro (1 de cada 5 frente a 1 de cada 3).
     */
    private static final float PROB_COLMILLO = 0.20f;

    /**
     * Probabilidad del veneno en la arana de cueva.
     *
     * Va en la de cueva y no en la comun porque es la unica de las dos que
     * envenena al morder. El colmillo venenoso necesita las dos aranas, asi que
     * cada una aporta lo que de verdad tiene.
     */
    private static final float PROB_VENENO = 0.20f;

    /** Probabilidad de la miel cristalizada en la abeja. */
    private static final float PROB_MIEL = 0.20f;

    private AtalayaLoot() {
    }

    public static void registrar() {
        LootTableEvents.MODIFY.register((clave, constructor, origen, registros) -> {
            Identifier id = clave.identifier();
            if (ARANA.equals(id)) {
                constructor.pool(piscina(AtalayaItems.COLMILLO, PROB_COLMILLO));
            } else if (ARANA_DE_CUEVA.equals(id)) {
                constructor.pool(piscina(AtalayaItems.VENENO, PROB_VENENO));
            } else if (ABEJA.equals(id)) {
                constructor.pool(piscina(AtalayaItems.MIEL_CRISTALIZADA, PROB_MIEL));
            }
        });

        // Los interruptores se aplican AQUI y no como condicion de la tabla: una
        // condicion propia habria que registrarla con su codec, y ademas las
        // tablas solo se releen al recargar datapacks. Filtrando los drops ya
        // generados, apagarlos tiene efecto inmediato.
        //
        // Solo afecta a lo que sale de una tabla de botin, asi que apagar el drop
        // de la miel no impide fabricarla: eso lo lleva su propio interruptor.
        LootTableEvents.MODIFY_DROPS.register((tabla, contexto, drops) -> {
            AtalayaConfig cfg = AtalayaConfig.get();
            if (!cfg.isDropColmilloActivo()) {
                drops.removeIf(pila -> pila.is(AtalayaItems.COLMILLO));
            }
            if (!cfg.isDropVenenoActivo()) {
                drops.removeIf(pila -> pila.is(AtalayaItems.VENENO));
            }
            if (!cfg.isDropMielActivo()) {
                drops.removeIf(pila -> pila.is(AtalayaItems.MIEL_CRISTALIZADA));
            }
        });
    }

    /**
     * Una piscina que suelta el item con la probabilidad dada, y solo si lo mata
     * un jugador.
     *
     * La condicion de jugador va en todas a proposito, como hace vanilla con el
     * ojo de arana: sin ella una granja automatica los produciria en masa y el
     * drop dejaria de significar nada. Con las abejas importa el doble, porque
     * las granjas de abejas son de lo mas comun.
     */
    private static LootPool piscina(Item item, float probabilidad) {
        return LootPool.lootPool()
                .setRolls(ConstantValue.exactly(1))
                .add(LootItem.lootTableItem(item))
                .when(LootItemRandomChanceCondition.randomChance(probabilidad))
                .when(LootItemKilledByPlayerCondition.killedByPlayer())
                .build();
    }
}
