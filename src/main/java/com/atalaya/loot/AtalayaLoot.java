package com.atalaya.loot;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.item.AtalayaItems;
import net.fabricmc.fabric.api.loot.v3.LootTableEvents;
import net.minecraft.resources.Identifier;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.EmptyLootItem;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemKilledByPlayerCondition;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;

/**
 * Los drops que el mod anade al botin de vanilla: tres mobs y la pesca.
 *
 * No se reescribe ninguna tabla: a cada una se le engancha una piscina propia,
 * asi que siguen soltando lo suyo con normalidad y otros mods pueden anadir lo
 * que quieran sin pisarse.
 *
 * Los mobs y la pesca se montan distinto a proposito, porque el contexto de
 * botin que reciben no es el mismo. Ver {@link #piscina} y
 * {@link #piscinaDePesca}.
 */
public final class AtalayaLoot {

    private static final Identifier ARANA =
            Identifier.withDefaultNamespace("entities/spider");

    private static final Identifier ARANA_DE_CUEVA =
            Identifier.withDefaultNamespace("entities/cave_spider");

    private static final Identifier ABEJA =
            Identifier.withDefaultNamespace("entities/bee");

    /**
     * Tabla RAIZ de la pesca, no la de tesoro ni la de basura.
     *
     * La de tesoro solo entra en aguas abiertas y con el cielo despejado sobre
     * la boya, asi que pescar en una cueva o bajo un alero no la tira nunca. La
     * de basura mete el espejo en la misma ruleta que las botas viejas, y ahi
     * competiria por un hueco en vez de sumarse. Enganchando una piscina propia
     * a la raiz, el espejo sale ADEMAS de lo que pique y en cualquier sitio
     * donde se pueda pescar.
     */
    private static final Identifier PESCA =
            Identifier.withDefaultNamespace("gameplay/fishing");

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

    /**
     * Peso total de la piscina de la pesca.
     *
     * Mil para que un punto porcentual sean diez de peso: peso y calidad solo
     * admiten enteros, y con esta escala los porcentajes que buscamos salen
     * clavados en vez de aproximados.
     */
    private static final int TOTAL_PESCA = 1000;

    /**
     * Peso del espejo de mar: 50 de 1000, o sea un 5% con la cana pelada.
     *
     * Es el mismo 5% que vanilla le da al TESORO de la pesca, que es el ancla
     * de la que se copia. Sale algo mas accesible que el tesoro de verdad
     * porque esta piscina no exige aguas abiertas, asi que tambien pica en una
     * charca bajo tierra.
     *
     * Al ser una piscina aparte no le quita sitio a nada: el espejo sale
     * ADEMAS del pescado o la basura que toque, no en su lugar.
     */
    private static final int PESO_ESPEJO = 50;

    /**
     * Cuanto sube el espejo por cada punto de suerte: 25 de 1000, o sea +2,5
     * puntos porcentuales por nivel de Suerte del Mar.
     *
     * El juego calcula el peso efectivo de cada entrada como
     * floor(peso + calidad * suerte). Dandole al hueco vacio esta MISMA calidad
     * en negativo, el total se queda fijo en {@link #TOTAL_PESCA} y el
     * porcentaje sube en linea recta, sin la deriva que saldria si el
     * denominador se moviera:
     *
     * <pre>
     *   sin encantar  5,0%      Suerte del Mar II   10,0%
     *   Suerte I      7,5%      Suerte del Mar III  12,5%  (tope: max_level 3)
     * </pre>
     *
     * Esto NO se puede hacer con una condicion de probabilidad con bonus por
     * encantamiento: esa mira el parametro ATTACKING_ENTITY, y la pesca no lo
     * aporta (solo pasa origen, cana y anzuelo). Se quedaria en la base para
     * siempre y sin dar ningun aviso.
     */
    private static final int CALIDAD_ESPEJO = 25;

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
            } else if (PESCA.equals(id)) {
                constructor.pool(piscinaDePesca());
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
            if (!cfg.isDropEspejoActivo()) {
                drops.removeIf(pila -> pila.is(AtalayaItems.ESPEJO_MAR));
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

    /**
     * La piscina de la pesca: el espejo contra un hueco vacio, repartidos por
     * PESO en vez de por una probabilidad plana.
     *
     * El peso no es un capricho de estilo, es la unica via por la que entra la
     * suerte del jugador. Una condicion de probabilidad la ignora entera, asi
     * que Suerte del Mar no haria nada aunque el jugador diera por hecho que si
     * (ver {@link #CALIDAD_ESPEJO}). Es tambien como lo hace vanilla con su
     * propio reparto de pescado, basura y tesoro.
     *
     * Tampoco lleva la condicion de "matado por un jugador" que si llevan los
     * mobs. No es un olvido: en la pesca no muere nadie, asi que ese parametro
     * no existe en su contexto y pedirlo reventaria al tirar la tabla. La
     * consecuencia es que una granja de pesca AFK puede producir espejos en
     * serie; se asume, porque acumularlos no da ninguna ventaja cuando de la
     * lente hace falta UNA por casco y no se vuelve a necesitar.
     */
    private static LootPool piscinaDePesca() {
        return LootPool.lootPool()
                .setRolls(ConstantValue.exactly(1))
                .add(LootItem.lootTableItem(AtalayaItems.ESPEJO_MAR)
                        .setWeight(PESO_ESPEJO)
                        .setQuality(CALIDAD_ESPEJO))
                // El hueco vacio es el "no ha salido nada". Su calidad va en
                // negativo para que lo que gana el espejo lo pierda este y el
                // total no se mueva.
                .add(EmptyLootItem.emptyItem()
                        .setWeight(TOTAL_PESCA - PESO_ESPEJO)
                        .setQuality(-CALIDAD_ESPEJO))
                .build();
    }
}
