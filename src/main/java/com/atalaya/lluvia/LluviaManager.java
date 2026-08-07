package com.atalaya.lluvia;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.effect.CorrosionEffect;
import com.atalaya.effect.EmpapadoEffect;
import net.minecraft.core.Holder;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

import java.util.List;

/**
 * Lo que le hace la lluvia a quien se moja.
 *
 * Son DOS mecanicas con el mismo disparador y cada una con su interruptor:
 *
 *   - Corrosion: se come la armadura
 *   - Empapado:  te deja a la mitad de velocidad
 *
 * Van juntas aqui porque comparten la condicion —te esta lloviendo encima— y una
 * sola vuelta por jugador resuelve las dos. Separarlas en dos bucles seria pagar
 * dos veces por la misma pregunta.
 *
 * Reparte a los jugadores en tramos igual que el resto de bucles del mod, y el
 * intervalo del reparto ES el ritmo del desgaste: como cada jugador se procesa
 * una vez por vuelta y la vuelta dura un segundo, cada pasada quita justo el
 * desgaste de un segundo sin llevar ningun contador aparte.
 */
public final class LluviaManager {

    /** Una vuelta = un segundo = una mordida a la armadura. */
    private static final int INTERVALO = 20;

    /**
     * Cuerda de los efectos, y cuando se renuevan.
     *
     * Los dos numeros salen de un detalle de vanilla: el HUD desvanece el icono
     * de cualquier efecto al que le queden 200 ticks o menos ({@code Hud} llama
     * a {@code endsWithin(200)}). Con una cuerda corta el icono parpadea sin
     * parar aunque el efecto se renueve sin cortes.
     *
     * Renovando en 400 sobre 600, nunca baja de 400 y quedan 200 ticks de
     * margen. Que la cuerda sea larga no alarga el efecto: cuando deja de
     * llover se retira a mano en la siguiente vuelta.
     */
    private static final int DURACION_EFECTO = 600;
    private static final int RENOVAR_BAJO = 400;

    private static final EquipmentSlot[] RANURAS = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET
    };

    private static long contador = 0;

    private LluviaManager() {
    }

    public static void tick(MinecraftServer servidor) {
        long ranura = contador % INTERVALO;
        contador++;

        List<ServerPlayer> jugadores = servidor.getPlayerList().getPlayers();
        int total = jugadores.size();
        if (total == 0) {
            return;
        }

        // El bucle corre AUNQUE las mecanicas esten apagadas: hay que retirar el
        // efecto que quedara puesto a quien lo llevara al apagarlas.
        AtalayaConfig cfg = AtalayaConfig.get();
        boolean corroe = cfg.isCorrosionActiva();
        boolean empapa = cfg.isEmpapadoActivo();

        int desde = (int) (total * ranura / INTERVALO);
        int hasta = (int) (total * (ranura + 1) / INTERVALO);
        for (int i = desde; i < hasta; i++) {
            revisar(jugadores.get(i), corroe, empapa);
        }
    }

    private static void revisar(ServerPlayer jugador, boolean corroe, boolean empapa) {
        boolean mojado = !jugador.isCreative()
                && !jugador.isSpectator()
                && bajoLluvia(jugador);

        // Los efectos se ponen aunque no lleve armadura: son el aviso de que
        // esta lluvia muerde, y llegan ANTES de que el jugador se juegue nada.
        efecto(jugador, CorrosionEffect.CORROSION, mojado && corroe);
        efecto(jugador, EmpapadoEffect.EMPAPADO, mojado && empapa);

        if (mojado && corroe) {
            corroer(jugador);
        }
    }

    /**
     * Pone o quita un efecto, renovandolo antes de que entre en la franja del
     * parpadeo.
     *
     * El de empapado no necesita nada mas: su lentitud va como modificador del
     * propio efecto, asi que se aplica y se retira sola con el.
     */
    private static void efecto(ServerPlayer jugador, Holder<MobEffect> cual, boolean debe) {
        if (!debe) {
            jugador.removeEffect(cual);
            return;
        }
        MobEffectInstance actual = jugador.getEffect(cual);
        if (actual == null || actual.getDuration() <= RENOVAR_BAJO) {
            jugador.addEffect(new MobEffectInstance(
                    cual, DURACION_EFECTO, 0, false, false, true));
        }
    }

    /**
     * Si al jugador le esta cayendo la lluvia encima de verdad.
     *
     * {@code isRainingAt} resuelve las tres cosas de una vez: que este
     * lloviendo, que el jugador vea el cielo desde donde esta, y que su bioma
     * reciba LLUVIA. Ese ultimo detalle sale gratis y viene muy bien: en el
     * desierto no llueve y en los biomas helados cae nieve, asi que ninguno de
     * los dos moja sin tener que nombrarlos aqui.
     *
     * Y como mira el cielo, cubrirse ya protege — igual que la sombra protege de
     * la insolacion. Un alero, una cueva o un techo bastan.
     */
    public static boolean bajoLluvia(Player jugador) {
        return jugador.level().isRainingAt(jugador.blockPosition());
    }

    /**
     * Muerde una vez cada pieza de armadura puesta.
     *
     * Se cuenta por RANURA y no por inventario: la armadura de la mochila no se
     * moja. Y solo las piezas con durabilidad, asi que una calabaza en la cabeza
     * o un elemento sin desgaste se quedan como estan.
     */
    private static void corroer(ServerPlayer jugador) {
        for (EquipmentSlot ranura : RANURAS) {
            ItemStack pieza = jugador.getItemBySlot(ranura);
            if (pieza.isEmpty() || !pieza.isDamageableItem()) {
                continue;
            }
            pieza.hurtAndBreak(
                    CorrosionEffect.desgastePorSegundo(pieza.getMaxDamage()),
                    jugador, ranura);
        }
    }
}
