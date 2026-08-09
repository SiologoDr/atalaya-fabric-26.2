package com.atalaya.frio;

import com.atalaya.Atalaya;
import com.atalaya.config.AtalayaConfig;
import com.atalaya.effect.HipotermiaEffect;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

import java.util.List;

/**
 * Enfria a quien anda por la nieve y le quita el frio a quien se arrima al fuego.
 *
 * Es la contraparte de {@link com.atalaya.hidratacion.HidratacionManager}, pero
 * con dos diferencias de fondo:
 *
 *   - El desierto solo seca CON SOL. Aqui basta el bioma: bajo tierra, de noche
 *     o dentro de una cueva sigues en la nieve.
 *   - La hidratacion se gasta y se rellena bebiendo. El frio se acumula, y lo
 *     unico que lo baja es el calor.
 *
 * El reparto por tramos es el mismo de siempre, pero aqui el intervalo NO puede
 * ser a la vez el ritmo, porque hay dos: enfriarse tarda 7 s por punto y
 * calentarse 1 s. Se toma el rapido como intervalo y la subida se limita
 * contando VUELTAS: una de cada siete.
 */
public final class FrioManager {

    /** Una vuelta = un segundo. Es el ritmo de calentarse. */
    private static final int INTERVALO = Frio.TICKS_POR_PUNTO_CALOR;

    /** Cada cuantas vueltas se gana un punto de frio: 140 / 20 = 7. */
    private static final int VUELTAS_POR_PUNTO = Frio.TICKS_POR_PUNTO / INTERVALO;

    /** Cada cuantas vueltas se pierde un punto solo por salir del frio. */
    private static final int VUELTAS_POR_PUNTO_FUERA = Frio.TICKS_POR_PUNTO_FUERA / INTERVALO;

    /** El dano cae cada dos vueltas, o sea cada 2 s, igual que la insolacion. */
    private static final int VUELTAS_POR_DANO = 2;

    /**
     * Cuerda del efecto y cuando se renueva.
     *
     * Vanilla desvanece el icono de todo efecto al que le queden 200 ticks o
     * menos. Con 400 sobre 600 nunca baja de esa franja y el icono no parpadea.
     */
    private static final int DURACION_EFECTO = 600;
    private static final int RENOVAR_BAJO = 400;

    /**
     * Bloques que dan calor. Va como etiqueta de datos y no escrito en el
     * codigo, asi que un servidor puede anadir los suyos sin tocar el mod.
     */
    public static final TagKey<Block> FUENTES_DE_CALOR = TagKey.create(
            Registries.BLOCK, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "fuentes_de_calor"));

    /**
     * Radio en el que se busca una fuente de calor.
     *
     * Cuatro bloques: hay que ARRIMARSE a la hoguera, no basta con tenerla en la
     * misma habitacion.
     */
    private static final int RADIO_CALOR = 4;

    /**
     * Luz de bloque por debajo de la cual ni se mira si hay una fuente cerca.
     *
     * Es un descarte rapido, la misma idea que la paleta de las secciones en el
     * indice de geodas: una antorcha da 14 y pierde 1 por bloque, asi que a
     * cuatro de distancia deja al menos 10. Si hay menos de 8 no puede haber
     * nada que caliente en el radio, y la comprobacion se acaba en una consulta
     * en vez de en setecientas.
     */
    private static final int LUZ_MINIMA = 8;

    private static long contador = 0;

    private FrioManager() {
    }

    public static void tick(MinecraftServer servidor) {
        long vuelta = contador / INTERVALO;
        long ranura = contador % INTERVALO;
        contador++;

        List<ServerPlayer> jugadores = servidor.getPlayerList().getPlayers();
        int total = jugadores.size();
        if (total == 0) {
            return;
        }

        // El bucle corre aunque este apagada: hay que avisar al cliente del
        // cambio y retirar lo que quedara puesto.
        boolean activa = AtalayaConfig.get().isFrioActivo();

        int desde = (int) (total * ranura / INTERVALO);
        int hasta = (int) (total * (ranura + 1) / INTERVALO);
        for (int i = desde; i < hasta; i++) {
            ServerPlayer jugador = jugadores.get(i);
            // Solo se escribe cuando cambia: si no, seria un paquete por
            // jugador y segundo sin que hubiera nada nuevo.
            if (Frio.activa(jugador) != activa) {
                jugador.setAttached(Frio.ACTIVA, activa);
            }
            procesar(jugador, activa, vuelta);
        }
    }

    private static void procesar(ServerPlayer jugador, boolean activa, long vuelta) {
        boolean cuenta = activa && !jugador.isCreative() && !jugador.isSpectator();

        int puntos = Frio.de(jugador);
        if (cuenta) {
            boolean frio = haceFrio(jugador);
            // Buscar fuego es lo caro, asi que solo se pregunta cuando la
            // respuesta cambia algo: o estas donde hace frio, o llevas frio
            // encima que quitarte. Al resto del servidor no le cuesta nada.
            boolean calor = (frio || puntos > 0) && cercaDeCalor(jugador);

            if (frio && !calor) {
                // Sube despacio: una vuelta de cada siete
                if (vuelta % VUELTAS_POR_PUNTO == 0 && puntos < Frio.MAXIMO) {
                    Frio.poner(jugador, puntos + 1);
                    puntos++;
                }
            } else if (puntos > 0) {
                // Baja de dos maneras, y a proposito no al mismo ritmo:
                //
                //   junto al fuego  1 s por punto  -> 50 s desde congelado
                //   solo por irte   3 s por punto  -> 2 min 30 s
                //
                // Salir de la nieve TIENE que servir, o el jugador se sentiria
                // atrapado. Pero si sirviera igual que una hoguera, encenderla
                // no valdria para nada: la recompensa de pararse a hacer fuego
                // es justo que va tres veces mas rapido que largarse.
                int cada = calor ? 1 : VUELTAS_POR_PUNTO_FUERA;
                if (vuelta % cada == 0) {
                    Frio.poner(jugador, puntos - 1);
                    puntos--;
                }
            }
            // Los topes se comprueban ANTES de escribir, no despues de recortar.
            // El attachment se sincroniza, asi que reescribir el mismo numero
            // seria un paquete por jugador y segundo para todo el que no pase
            // frio, que van a ser casi todos.
        }

        int nivel = cuenta ? HipotermiaEffect.nivelPorFrio(puntos) : 0;
        HipotermiaEffect.Escalon escalon = HipotermiaEffect.escalon(nivel);

        aplicarModificadores(jugador, escalon);

        if (nivel <= 0) {
            jugador.removeEffect(HipotermiaEffect.HIPOTERMIA);
            return;
        }

        MobEffectInstance actual = jugador.getEffect(HipotermiaEffect.HIPOTERMIA);
        if (actual == null
                || actual.getAmplifier() != nivel - 1
                || actual.getDuration() <= RENOVAR_BAJO) {
            jugador.addEffect(new MobEffectInstance(
                    HipotermiaEffect.HIPOTERMIA, DURACION_EFECTO, nivel - 1,
                    false, false, true));
        }

        // Tiritar quema lo comido, igual que sudar
        if (escalon.hambre() > 0) {
            jugador.causeFoodExhaustion(escalon.hambre() * (INTERVALO / 20f));
        }

        // La vista NO se toca desde aqui: el halo y el mareo los dibuja el
        // cliente leyendo el nivel del efecto, que ya le llega solo.

        // Congelarse cuesta vida. Va como dano de congelacion, que ademas de
        // ser lo suyo esta en la etiqueta bypasses_armor: morirse de frio con
        // la armadura puesta tiene que doler igual.
        if (escalon.dano() > 0 && vuelta % VUELTAS_POR_DANO == 0) {
            jugador.hurtServer(jugador.level(),
                    jugador.level().damageSources().freeze(),
                    escalon.dano());
        }
    }

    // ------------------------------------------------------------------
    //  Cuando se pasa frio
    // ------------------------------------------------------------------

    /**
     * Si en ese punto hace frio de verdad.
     *
     * NO se usan las etiquetas de bioma. Se probaron y dejaban huecos absurdos:
     * un rio helado —con el agua congelada bajo los pies— no entraba en
     * IS_SNOWY, asi que se podia cruzar un rio de hielo sin pasar frio.
     *
     * La pregunta que de verdad se quiere hacer es "aqui cuaja la nieve", y el
     * juego ya la sabe responder: {@code coldEnoughToSnow} mira la temperatura
     * REAL del sitio. Eso cubre de una vez el rio helado, los picos, las
     * laderas, la arboleda y el oceano congelado, sin tener que ir apuntando
     * biomas a mano ni volver a esto cada vez que Mojang anada uno.
     *
     * Y trae de propina dos cosas que encajan con la idea de "el frio es el
     * sitio": la altura cuenta —arriba de una montana hace frio aunque abajo no—
     * y bajo tierra sigue contando, porque la temperatura solo baja con la
     * altura, nunca sube al enterrarse.
     */
    public static boolean haceFrio(Player jugador) {
        Level nivel = jugador.level();
        BlockPos pos = jugador.blockPosition();
        return nivel.getBiome(pos).value().coldEnoughToSnow(pos, nivel.getSeaLevel());
    }

    /**
     * Si el jugador se esta enfriando ahora mismo: donde hace frio y sin calor
     * cerca.
     *
     * A diferencia del desierto, aqui NO cuenta el cielo. El frio no viene de
     * arriba, viene del sitio, asi que meterse bajo tierra o esperar a la noche
     * no sirve de nada. Lo unico que lo para es el fuego.
     */
    public static boolean seEnfria(Player jugador) {
        return haceFrio(jugador) && !cercaDeCalor(jugador);
    }

    /**
     * Si hay una fuente de calor a mano.
     *
     * Dos pasos a proposito. Primero se mira la luz de bloque, que es UNA
     * consulta: si esta oscuro no puede haber nada que caliente y se acaba ahi,
     * que es el caso normal de alguien perdido en la nieve. Solo si hay luz se
     * recorren los bloques del radio para comprobar que es fuego de verdad y no
     * una lampara de piedra luminosa.
     */
    public static boolean cercaDeCalor(Player jugador) {
        Level nivel = jugador.level();
        BlockPos pos = jugador.blockPosition();

        if (nivel.getLightEngine().getLayerListener(LightLayer.BLOCK).getLightValue(pos) < LUZ_MINIMA) {
            return false;
        }

        for (BlockPos p : BlockPos.betweenClosed(
                pos.offset(-RADIO_CALOR, -RADIO_CALOR, -RADIO_CALOR),
                pos.offset(RADIO_CALOR, RADIO_CALOR, RADIO_CALOR))) {
            if (calienta(nivel.getBlockState(p))) {
                return true;
            }
        }
        return false;
    }

    /**
     * Si ese bloque da calor de verdad.
     *
     * La etiqueta dice cuales VALEN, pero no puede decir si estan encendidos, y
     * una hoguera apagada o un horno sin fuego no calientan a nadie. La regla es
     * generica a proposito: cualquier bloque de la lista que tenga estado de
     * encendido tiene que estarlo. Asi vale igual para lo que anada un servidor
     * mas adelante.
     */
    private static boolean calienta(BlockState estado) {
        if (!estado.is(FUENTES_DE_CALOR)) {
            return false;
        }
        if (estado.hasProperty(BlockStateProperties.LIT)) {
            return estado.getValue(BlockStateProperties.LIT);
        }
        return true;
    }

    // ------------------------------------------------------------------
    //  Los castigos
    // ------------------------------------------------------------------

    private static void aplicarModificadores(ServerPlayer jugador, HipotermiaEffect.Escalon escalon) {
        // Los cuatro se tocan siempre: la tabla trae cero donde no hay castigo,
        // y un cero se traduce en quitar el modificador.
        modificador(jugador, Attributes.BLOCK_BREAK_SPEED, HipotermiaEffect.ID_MINERIA,
                escalon.mineria(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        modificador(jugador, Attributes.ATTACK_SPEED, HipotermiaEffect.ID_ATAQUE,
                escalon.ataque(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        modificador(jugador, Attributes.MOVEMENT_SPEED, HipotermiaEffect.ID_MOVIMIENTO,
                escalon.movimiento(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
        modificador(jugador, Attributes.ATTACK_DAMAGE, HipotermiaEffect.ID_FUERZA,
                escalon.fuerza(), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    /**
     * Pone el modificador, o lo quita si la cantidad es cero.
     *
     * Se comprueba antes de quitar para no marcar el atributo como
     * "recalculame" cada segundo a todo el que no pase frio, que van a ser casi
     * todos.
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
