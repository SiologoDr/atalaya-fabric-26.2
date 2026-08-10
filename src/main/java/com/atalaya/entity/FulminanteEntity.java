package com.atalaya.entity;

import com.atalaya.Atalaya;
import com.atalaya.config.AtalayaConfig;
import com.atalaya.mixin.CreeperAccessor;
import com.atalaya.util.BotinSecreto;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BrushableBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.level.Level;

/**
 * Fulminante: el creeper del desierto.
 *
 * De momento es un creeper y nada mas. Hereda de {@link Creeper} entero —la IA,
 * el acercarse en silencio, el silbido, el hincharse y la explosion— y lo unico
 * que cambia es como se ve.
 *
 * Se hereda en vez de copiar a proposito. Un creeper lleva media docena de
 * comportamientos atados entre si, y reescribirlos para cambiar la piel seria
 * garantizarse que el dia que Mojang toque uno, el nuestro se quede atras.
 *
 * El nombre viene de donde tiene que venir: un fulminante es el piston que
 * enciende la carga, y sale del latin FULMEN, rayo. La misma familia que FULGUR
 * y de ahi la fulgurita, que es la arena que un rayo funde en vidrio. Cuando
 * este montada la mecanica, su explosion hara justo eso con la arena.
 */
public class FulminanteEntity extends Creeper {

    /**
     * Ticks de mecha, contra los 30 de un creeper.
     *
     * "Un 75% mas rapido" salen 7,5 ticks, y el campo es entero, asi que se
     * queda en 8: de segundo y medio a cuatro decimas. No da tiempo a apartarse
     * andando; o lo ves venir de lejos o te alcanza.
     */
    private static final int MECHA = 8;

    public FulminanteEntity(EntityType<? extends Creeper> tipo, Level nivel) {
        super(tipo, nivel);
        // Los dos campos son privados en Creeper; el accesor los abre.
        //
        // El radio se deja en el de vanilla a proposito. El +25% de dano se
        // aplica al golpe, no al radio, para que rompa los mismos bloques que un
        // creeper normal: lo que sube es lo que duele, no lo que destroza.
        ((CreeperAccessor) (Object) this).atalaya$ponerMecha(MECHA);
    }

    /** Hasta donde alcanza a fundir la arena. */
    private static final int RADIO_VITRIFICADO = 3;

    /**
     * Lo que puede salir al cepillar. La probabilidad vive en el JSON.
     *
     * Se le cuelga a CADA bloque que deja el fulminante, que es como el propio
     * juego reparte el botin de los pozos y las piramides: el bloque es el mismo
     * de vanilla y lo que cambia es la tabla que lleva pegada.
     */
    public static final ResourceKey<LootTable> BOTIN_CEPILLADO = ResourceKey.create(
            Registries.LOOT_TABLE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "brushing/fulgurita"));

    /**
     * Funde en vidrio la arena del crater, justo despues de reventar.
     *
     * DESPUES y no antes, aunque lo natural pareciera lo contrario. Sembrar los
     * bloques primero no servia de nada: la explosion alcanza lo mismo que el
     * corro donde se ponen, asi que se los llevaba casi todos al instante. Y un
     * crater deja mas arena a la vista, no menos — el suelo y las paredes del
     * hoyo quedan al descubierto y son justo donde tiene sentido que aparezca.
     *
     * Solo se toca la superficie —arena con el cielo despejado encima— porque un
     * rayo funde lo que toca, no lo que hay tres metros bajo tierra. Ademas asi
     * los bloques quedan a la vista y no enterrados.
     */
    public void vitrificar() {
        if (!(level() instanceof ServerLevel nivel)) {
            return;
        }
        // Con el interruptor apagado no se siembra NADA, en vez de sembrar
        // bloques vacios. Cepillar veinte veces para no sacar nunca nada seria
        // peor que no encontrar bloques: parece roto, no apagado.
        if (!AtalayaConfig.get().isFulguritaActiva()) {
            return;
        }
        BlockPos centro = blockPosition();
        // El hoyo baja, asi que se mira tambien por debajo: tras el estallido la
        // arena buena esta en el suelo del crater, no a la altura de las patas.
        for (BlockPos pos : BlockPos.betweenClosed(
                centro.offset(-RADIO_VITRIFICADO, -3, -RADIO_VITRIFICADO),
                centro.offset(RADIO_VITRIFICADO, 1, RADIO_VITRIFICADO))) {
            BlockState estado = nivel.getBlockState(pos);
            if (!estado.is(Blocks.SAND) && !estado.is(Blocks.RED_SAND)) {
                continue;
            }
            if (!nivel.getBlockState(pos.above()).isAir()) {
                continue;
            }
            // No toda la arena del corro: si no, quedaria una placa perfecta y
            // se leeria como algo puesto a mano. Una de cada tres deja un
            // reguero irregular, que es como se ve un impacto.
            if (nivel.getRandom().nextInt(3) != 0) {
                continue;
            }
            BlockPos fijo = pos.immutable();
            // Arena sospechosa de vanilla, no un bloque propio.
            //
            // Lo unico que hacia falta de un bloque nuevo era colgarle otra
            // tabla de botin, y eso se le puede hacer igual al de vanilla: es
            // exactamente como reparten los pozos y las piramides. Un bloque
            // menos que mantener, y ademas el jugador ya sabe que hacer con el
            // en cuanto lo ve.
            nivel.setBlock(fijo, Blocks.SUSPICIOUS_SAND.defaultBlockState(), 3);
            if (nivel.getBlockEntity(fijo) instanceof BrushableBlockEntity cepillable) {
                // La semilla va por posicion: dos bloques del mismo estallido dan
                // resultados distintos, y el mismo bloque siempre da lo mismo
                // aunque se recargue el mundo.
                cepillable.setLootTable(BOTIN_CEPILLADO, fijo.asLong());
                // Y que no se sepa lo que hay dentro hasta la ultima pasada.
                // Sin esto, el objeto asoma desde el primer cepillazo y las
                // cuatro veces de cada cinco que no toca ni te molestas en
                // terminar: la tirada dejaria de costar nada.
                if (cepillable instanceof BotinSecreto secreto) {
                    secreto.atalaya$guardarElSecreto();
                }
            }
        }
    }
}
