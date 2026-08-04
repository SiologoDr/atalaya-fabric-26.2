package com.atalaya.hidratacion;

import com.atalaya.config.AtalayaConfig;
import com.atalaya.effect.InsolacionEffect;
import net.fabricmc.fabric.api.tag.convention.v2.ConventionalBiomeTags;
import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

import java.util.List;

/**
 * Gasta la hidratacion de quien esta en el desierto.
 *
 * Reparte a los jugadores en ranuras igual que hace RadiationManager, pero aqui
 * el reparto sale gratis: como cada jugador debe perder un punto cada
 * {@link Hidratacion#TICKS_POR_PUNTO} ticks, basta con que el intervalo del
 * reparto SEA ese mismo numero. Cada jugador cae en una ranura, se le procesa
 * una vez por vuelta y se le quita un punto. Ni contadores por jugador ni un
 * pico cada siete segundos con todo el servidor a la vez.
 */
public final class HidratacionManager {

    private static long contador = 0;

    private HidratacionManager() {
    }

    public static void tick(MinecraftServer servidor) {
        long ranura = contador % Hidratacion.TICKS_POR_PUNTO;
        contador++;

        if (!AtalayaConfig.get().isHidratacionActiva()) {
            return;
        }

        List<ServerPlayer> jugadores = servidor.getPlayerList().getPlayers();
        int total = jugadores.size();
        if (total == 0) {
            return;
        }

        // Solo el tramo de esta ranura. Con el intervalo en 140 ticks y pocos
        // jugadores, la mayoria de ticks no tocan a nadie y el bucle sale
        // enseguida.
        //
        // Al entrar o salir alguien la lista se desplaza y algun jugador puede
        // repetir vuelta o saltarsela. Aqui eso es un punto de mas o de menos
        // muy de vez en cuando, sobre un deposito de cien: no merece la pena
        // llevar un contador por jugador para arreglarlo.
        int desde = (int) (total * ranura / Hidratacion.TICKS_POR_PUNTO);
        int hasta = (int) (total * (ranura + 1) / Hidratacion.TICKS_POR_PUNTO);
        for (int i = desde; i < hasta; i++) {
            procesar(jugadores.get(i));
        }
    }

    private static void procesar(ServerPlayer jugador) {
        // Creativo y espectador no se deshidratan, igual que son inmunes a la
        // radiacion.
        if (jugador.isCreative() || jugador.isSpectator()) {
            return;
        }
        if (!bajoElSol(jugador)) {
            return; // a la sombra o de noche el nivel se queda como esta
        }

        int actual = Hidratacion.de(jugador);
        if (actual <= 0) {
            // Vacio. Por ahora no pasa nada mas: el item que rellena y lo que
            // ocurra al llegar a cero son el siguiente paso.
            return;
        }
        Hidratacion.poner(jugador, actual - 1);
    }

    /**
     * Si el jugador pisa un bioma de desierto.
     *
     * Se pregunta por la etiqueta de convencion y no por el bioma concreto de
     * vanilla, asi que los desiertos que anadan otros mods cuentan solos, sin
     * tocar nada aqui.
     */
    public static boolean enDesierto(Player jugador) {
        Level nivel = jugador.level();
        return nivel.getBiome(jugador.blockPosition()).is(ConventionalBiomeTags.IS_DESERT);
    }

    /**
     * Por encima de esta oscuridad del cielo se considera que el sol ya no
     * aprieta.
     *
     * {@code getSkyDarken()} vale 0 a pleno dia y sube hasta 11 de noche, y
     * ademas sube con la tormenta. Un solo numero cubre asi las dos cosas: ni de
     * noche ni bajo un chaparron te insolas.
     */
    private static final int OSCURIDAD_SIN_SOL = 4;

    /**
     * Si al jugador le esta dando el sol de verdad. Son tres condiciones:
     * desierto, cielo despejado sobre su cabeza y de dia.
     *
     * Esto es lo que gasta el agua y lo que insola. Meterse en una casa, en una
     * cueva o bajo un arbol te protege, igual que esperar a que caiga la noche:
     * es la forma real de cruzar un desierto, y el juego la premia sola sin que
     * haya que explicarla en ningun sitio.
     */
    public static boolean bajoElSol(Player jugador) {
        if (!enDesierto(jugador)) {
            return false;
        }
        Level nivel = jugador.level();
        // Cualquier precipitacion tapa el sol. isRaining() cubre la lluvia y la
        // tormenta de una vez, porque en vanilla no hay tormenta sin lluvia.
        if (nivel.isRaining()) {
            return false;
        }
        if (nivel.getSkyDarken() >= OSCURIDAD_SIN_SOL) {
            return false; // de noche
        }
        // Cuenta desde los ojos y no desde los pies: asi un bloque a la altura
        // de la cabeza ya da sombra, que es lo que espera quien se cobija.
        return nivel.canSeeSkyFromBelowWater(jugador.blockPosition().above());
    }

    // ------------------------------------------------------------------
    //  Insolacion
    // ------------------------------------------------------------------

    /**
     * Cada cuanto se revisa el estado de insolacion de un jugador.
     *
     * Va aparte del gasto de hidratacion y mucho mas rapido, porque de esto
     * dependen cosas que se tienen que notar al momento: el dano del nivel 4 y
     * que al salir del desierto se te quite todo. Siete segundos de retraso ahi
     * se notarian como un fallo.
     *
     * Y ES el intervalo del dano: como cada jugador se procesa una vez por
     * vuelta, el golpe del nivel 4 cae solo cada 2 s sin llevar ningun contador.
     */
    private static final int INTERVALO_INSOLACION = 40;

    /**
     * Cuerda que se le da al efecto al ponerlo, y cuando se renueva.
     *
     * MUY por encima del intervalo a proposito. El HUD de vanilla desvanece el
     * icono de todo efecto al que le queden 200 ticks o menos ({@code Hud} llama
     * a {@code endsWithin(200)}), asi que con una cuerda corta el icono parpadea
     * sin parar aunque el efecto no se vaya nunca.
     *
     * Renovando en 400 sobre 600, nunca baja de 400 y quedan 200 ticks de
     * margen: aunque el reparto por ranuras se salte varias vueltas seguidas, no
     * llega a la franja del parpadeo. Son los mismos numeros que usan la
     * radiacion y la corrosion, por el mismo motivo.
     *
     * No alarga el efecto de mas: cuando deja de tocar se retira a mano.
     */
    private static final int DURACION_EFECTO = 600;
    private static final int RENOVAR_BAJO = 400;

    private static long contadorInsolacion = 0;

    /**
     * Reparte la insolacion. Va en su propio bucle, con el mismo reparto por
     * tramos que usa el gasto de hidratacion.
     */
    public static void tickInsolacion(MinecraftServer servidor) {
        long ranura = contadorInsolacion % INTERVALO_INSOLACION;
        contadorInsolacion++;

        List<ServerPlayer> jugadores = servidor.getPlayerList().getPlayers();
        int total = jugadores.size();
        if (total == 0) {
            return;
        }

        // El bucle corre AUNQUE la mecanica este apagada, por dos razones: hay
        // que avisar al cliente del cambio, y hay que retirar lo que quedara
        // puesto al apagarla.
        boolean activa = AtalayaConfig.get().isHidratacionActiva();

        int desde = (int) (total * ranura / INTERVALO_INSOLACION);
        int hasta = (int) (total * (ranura + 1) / INTERVALO_INSOLACION);
        for (int i = desde; i < hasta; i++) {
            ServerPlayer jugador = jugadores.get(i);
            // Solo se escribe cuando cambia: escribirlo cada dos segundos
            // mandaria un paquete por jugador sin que hubiera nada nuevo.
            if (Hidratacion.activa(jugador) != activa) {
                jugador.setAttached(Hidratacion.ACTIVA, activa);
            }
            revisarInsolacion(jugador, activa);
        }
    }

    /**
     * Pone o quita la insolacion de un jugador segun lo seco que este.
     *
     * El nivel sale SOLO de los puntos de hidratacion, no de si le esta dando el
     * sol. Es la diferencia importante: el sol decide si PIERDES agua, y los
     * puntos deciden lo mal que estas. Meterte a la sombra deja de secarte, pero
     * no te rehidrata, asi que la insolacion sigue ahi hasta que bebas.
     *
     * Se llama tambien fuera del desierto por lo mismo: si sales de la arena con
     * cinco puntos, sigues igual de seco que dentro.
     */
    private static void revisarInsolacion(ServerPlayer jugador, boolean activa) {
        // Con la mecanica apagada el nivel sale 0, que es lo que retira los
        // modificadores y el efecto de quien los llevara puesto.
        boolean cuenta = activa && !jugador.isCreative() && !jugador.isSpectator();

        int nivel = cuenta
                ? InsolacionEffect.nivelPorHidratacion(Hidratacion.de(jugador))
                : 0;
        InsolacionEffect.Escalon escalon = InsolacionEffect.escalon(nivel);

        aplicarModificadores(jugador, escalon);

        if (nivel <= 0) {
            jugador.removeEffect(InsolacionEffect.INSOLACION);
            return;
        }

        // Solo se reenvia si cambia de nivel o va a caducar, para no mandar un
        // paquete por jugador cada dos segundos sin que cambie nada.
        MobEffectInstance actual = jugador.getEffect(InsolacionEffect.INSOLACION);
        if (actual == null
                || actual.getAmplifier() != nivel - 1
                || actual.getDuration() <= RENOVAR_BAJO) {
            jugador.addEffect(new MobEffectInstance(
                    InsolacionEffect.INSOLACION, DURACION_EFECTO, nivel - 1,
                    false, false, true));
        }

        // Quema lo comido mas rapido. Se aplica el agotamiento de los dos
        // segundos que han pasado desde la ultima vuelta.
        if (escalon.hambre() > 0) {
            jugador.causeFoodExhaustion(escalon.hambre() * (INTERVALO_INSOLACION / 20f));
        }

        // La vista NO se toca desde aqui. El halo de calor y el mareo suave los
        // dibuja el cliente leyendo el nivel del propio efecto, que ya le llega
        // solo: son puro renderizado y al servidor no le constan.

        // El deposito esta a cero y empieza a costar vida.
        //
        // Va como inanicion y no como sequedad porque "starve" esta en la
        // etiqueta bypasses_armor y "dry_out" no: morirte de sed con la
        // armadura puesta tiene que doler igual. Y encaja mejor que el dano
        // magico de la radiacion, que es otra cosa: aqui te mata la privacion.
        if (escalon.dano() > 0) {
            jugador.hurtServer(jugador.level(),
                    jugador.level().damageSources().starve(),
                    escalon.dano());
        }
    }

    /**
     * Cuelga del jugador los modificadores que le tocan por su nivel, y retira
     * los que ya no.
     *
     * Son TRANSITORIOS: no se guardan en disco, asi que no pueden quedarse
     * pegados si alguien se desconecta o muere en mitad del desierto.
     */
    private static void aplicarModificadores(ServerPlayer jugador, InsolacionEffect.Escalon escalon) {
        // Los cuatro se tocan siempre: la tabla trae cero donde no hay castigo,
        // y un cero se traduce en quitar el modificador. Asi no hace falta
        // recordar cual habia puesto antes.
        modificador(jugador, Attributes.BLOCK_BREAK_SPEED, InsolacionEffect.ID_MINERIA,
                escalon.mineria(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        modificador(jugador, Attributes.ATTACK_SPEED, InsolacionEffect.ID_ATAQUE,
                escalon.ataque(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        modificador(jugador, Attributes.MOVEMENT_SPEED, InsolacionEffect.ID_MOVIMIENTO,
                escalon.movimiento(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        // La fuerza va en fraccion y no en valor absoluto como la Debilidad de
        // vanilla: asi el castigo pesa lo mismo con la mano vacia que con una
        // espada de netherita, en vez de arruinar solo a quien pega flojo.
        modificador(jugador, Attributes.ATTACK_DAMAGE, InsolacionEffect.ID_FUERZA,
                escalon.fuerza(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    /**
     * Pone el modificador, o lo quita si la cantidad es cero.
     *
     * Se comprueba antes de quitar para no marcar el atributo como
     * "recalculame" cada dos segundos a todo el que no tenga insolacion, que
     * van a ser casi todos.
     */
    private static void modificador(ServerPlayer jugador,
                                    Holder<Attribute> atributo,
                                    Identifier id,
                                    double cantidad,
                                    AttributeModifier.Operation operacion) {
        AttributeInstance instancia = jugador.getAttribute(atributo);
        if (instancia == null) {
            return;
        }
        if (cantidad == 0) {
            if (instancia.getModifier(id) != null) {
                instancia.removeModifier(id);
            }
            return;
        }
        instancia.addOrUpdateTransientModifier(new AttributeModifier(id, cantidad, operacion));
    }
}
