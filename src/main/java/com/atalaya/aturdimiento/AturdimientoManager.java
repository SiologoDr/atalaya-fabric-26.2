package com.atalaya.aturdimiento;

import com.atalaya.effect.AturdimientoEffect;
import com.atalaya.entity.FulminanteEntity;
import com.atalaya.particula.AtalayaParticulas;
import net.fabricmc.fabric.api.event.player.AttackBlockCallback;
import net.fabricmc.fabric.api.event.player.AttackEntityCallback;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.fabricmc.fabric.api.event.player.UseEntityCallback;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.world.InteractionResult;
import net.minecraft.core.Holder;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

import java.util.List;

/**
 * Lleva la cuenta atras del aturdimiento y clava a quien lo tiene.
 *
 * Mismo reparto por tramos que el resto del mod, y otra vez el intervalo ES el
 * ritmo: cada jugador se procesa una vez cada cinco ticks y ahi se le descuentan
 * cinco. No hace falta contador por jugador.
 *
 * Cinco ticks —un cuarto de segundo— y no uno, porque no hay nada que mirar
 * entre medias: en pantalla solo esta el icono de la tecla, que no cuenta
 * segundos. Procesar a todo el mundo cada tick para eso seria tirar trabajo.
 */
public final class AturdimientoManager {

    private static final int INTERVALO = 5;

    /**
     * Cuerda del efecto y cuando se renueva. Vanilla hace parpadear el icono de
     * todo efecto al que le queden 200 ticks o menos, asi que se mantiene bien
     * por encima aunque el aturdimiento real se este acabando.
     */
    private static final int DURACION_EFECTO = 600;
    private static final int RENOVAR_BAJO = 400;

    private static long contador = 0;

    private AturdimientoManager() {
    }

    public static void tick(MinecraftServer servidor) {
        long ranura = contador % INTERVALO;
        contador++;

        List<ServerPlayer> jugadores = servidor.getPlayerList().getPlayers();
        int total = jugadores.size();
        if (total == 0) {
            return;
        }

        int desde = (int) (total * ranura / INTERVALO);
        int hasta = (int) (total * (ranura + 1) / INTERVALO);
        for (int i = desde; i < hasta; i++) {
            procesar(jugadores.get(i));
        }
    }

    private static void procesar(ServerPlayer jugador) {
        int quedan = Aturdimiento.de(jugador);

        // Creativo y espectador no se aturden: uno vuela y el otro atraviesa
        // paredes, asi que clavarlos no significaria nada.
        if (jugador.isCreative() || jugador.isSpectator()) {
            quedan = 0;
        }

        if (quedan <= 0) {
            soltar(jugador);
            return;
        }

        Aturdimiento.poner(jugador, quedan - INTERVALO);
        clavar(jugador);
        estrellas(jugador);

        MobEffectInstance actual = jugador.getEffect(AturdimientoEffect.ATURDIMIENTO);
        if (actual == null || actual.getDuration() <= RENOVAR_BAJO) {
            jugador.addEffect(new MobEffectInstance(
                    AturdimientoEffect.ATURDIMIENTO, DURACION_EFECTO, 0,
                    false, false, true));
        }
    }

    /**
     * Las estrellitas dando vueltas sobre la cabeza.
     *
     * El corro se calcula AQUI y no en la particula: se reparten tres por vuelta
     * en circulo, girando un poco cada vez. Asi cada estrella nace ya en su
     * sitio, no necesita saber de quien es ni perseguirlo, y el cliente no tiene
     * que seguir nada.
     *
     * Se mandan desde el servidor con sendParticles para que las vean TAMBIEN
     * los demas: que se note desde fuera quien esta aturdido es parte de la
     * gracia en un servidor con gente.
     */
    private static void estrellas(ServerPlayer jugador) {
        double radio = 0.42;
        double alto = jugador.getBbHeight() + 0.25;
        // El angulo avanza con el reloj del mundo, asi que el corro gira solo.
        double base = (jugador.level().getGameTime() % 80) / 80.0 * Math.PI * 2;
        for (int i = 0; i < 3; i++) {
            double ang = base + i * (Math.PI * 2 / 3);
            jugador.level().sendParticles(
                    AtalayaParticulas.ESTRELLA,
                    jugador.getX() + Math.cos(ang) * radio,
                    jugador.getY() + alto,
                    jugador.getZ() + Math.sin(ang) * radio,
                    1, 0.0, 0.0, 0.0, 0.0);
        }
    }

    /** Lo que hace al jugador quedarse quieto. */
    private static void clavar(ServerPlayer jugador) {
        modificador(jugador, Attributes.MOVEMENT_SPEED,
                AturdimientoEffect.ID_MOVIMIENTO, -1.0);
        // Tambien el salto, o se escaparia dando brincos. Y de paso hace que
        // pulsar espacio no mueva nada: la unica respuesta a la tecla es que la
        // cuenta baje, que es justo lo que se quiere ensenar.
        modificador(jugador, Attributes.JUMP_STRENGTH,
                AturdimientoEffect.ID_SALTO, -1.0);
    }

    private static void soltar(ServerPlayer jugador) {
        if (Aturdimiento.de(jugador) != 0) {
            Aturdimiento.poner(jugador, 0);
        }
        quitar(jugador, Attributes.MOVEMENT_SPEED, AturdimientoEffect.ID_MOVIMIENTO);
        quitar(jugador, Attributes.JUMP_STRENGTH, AturdimientoEffect.ID_SALTO);
        if (jugador.hasEffect(AturdimientoEffect.ATURDIMIENTO)) {
            jugador.removeEffect(AturdimientoEffect.ATURDIMIENTO);
        }
    }

    private static void modificador(ServerPlayer jugador, Holder<Attribute> atributo,
                                    net.minecraft.resources.Identifier id, double cantidad) {
        AttributeInstance instancia = jugador.getAttribute(atributo);
        if (instancia != null) {
            instancia.addOrUpdateTransientModifier(new AttributeModifier(
                    id, cantidad, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
        }
    }

    private static void quitar(ServerPlayer jugador, Holder<Attribute> atributo,
                               net.minecraft.resources.Identifier id) {
        AttributeInstance instancia = jugador.getAttribute(atributo);
        // Se comprueba antes de quitar para no marcar el atributo como
        // "recalculame" a todo el que no este aturdido, que van a ser todos.
        if (instancia != null && instancia.getModifier(id) != null) {
            instancia.removeModifier(id);
        }
    }

    // ------------------------------------------------------------------
    //  Entradas
    // ------------------------------------------------------------------

    /**
     * Lo llama el evento de dano: si a un jugador le ha alcanzado la explosion
     * de un fulminante, se lleva el aturdimiento.
     *
     * Se exige que el dano haya PASADO de verdad —no basta con estar cerca—,
     * asi que cubrirse detras de un bloque o llevar la armadura suficiente
     * tambien libra de quedarse clavado.
     */
    public static void alRecibirDano(LivingEntity victima, DamageSource fuente, float dano) {
        if (dano <= 0 || !(victima instanceof ServerPlayer jugador)) {
            return;
        }
        if (jugador.isCreative() || jugador.isSpectator()) {
            return;
        }
        if (!fuente.is(DamageTypes.EXPLOSION) && !fuente.is(DamageTypes.PLAYER_EXPLOSION)) {
            return;
        }
        if (!(fuente.getEntity() instanceof FulminanteEntity)) {
            return;
        }
        // Se pone entero, no se suma: dos explosiones seguidas no deben
        // encadenar un minuto clavado.
        Aturdimiento.poner(jugador, Aturdimiento.DURACION);
    }

    /**
     * Deja quieto todo lo que el jugador podria hacer con las manos.
     *
     * Se cuelga de los eventos de interaccion de Fabric en vez de bloquear
     * teclas en el cliente, y esa es la diferencia importante: estos eventos
     * corren TAMBIEN en el servidor, asi que un cliente tocado no se libra.
     * Bloquear la tecla solo esconde el boton; bloquear la accion la impide.
     */
    public static void registrarBloqueos() {
        UseItemCallback.EVENT.register((jugador, nivel, mano) ->
                Aturdimiento.aturdido(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);

        UseBlockCallback.EVENT.register((jugador, nivel, mano, golpe) ->
                Aturdimiento.aturdido(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);

        UseEntityCallback.EVENT.register((jugador, nivel, mano, entidad, golpe) ->
                Aturdimiento.aturdido(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);

        // Tambien pegar. "Aturdido" no es "solo no puedes andar": si pudieras
        // repartir mandobles mientras dura, el efecto no significaria nada.
        AttackBlockCallback.EVENT.register((jugador, nivel, mano, pos, cara) ->
                Aturdimiento.aturdido(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);

        AttackEntityCallback.EVENT.register((jugador, nivel, mano, entidad, golpe) ->
                Aturdimiento.aturdido(jugador) ? InteractionResult.FAIL : InteractionResult.PASS);
    }

    /** Lo llama la red cuando el cliente avisa de que ha pulsado saltar. */
    public static void alSaltar(ServerPlayer jugador) {
        int quedan = Aturdimiento.de(jugador);
        if (quedan <= 0) {
            return;
        }
        Aturdimiento.poner(jugador, quedan - Aturdimiento.POR_SALTO);
    }
}
