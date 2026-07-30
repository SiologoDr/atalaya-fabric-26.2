package com.atalaya.effect;

import com.atalaya.Atalaya;
import com.atalaya.item.HazmatArmor;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/**
 * Efecto de estado "Radiacion".
 *
 * Esto es un efecto REGISTRADO de verdad, con su entrada en el registro, su
 * icono en el inventario y su propio nombre. En la version de plugin habia que
 * secuestrar el efecto vanilla de Mala Suerte y renombrarlo en TODO el juego,
 * porque un cliente vanilla no sabe dibujar un efecto que no conoce. Es una de
 * las razones por las que el proyecto se paso a Fabric.
 *
 * El nivel (amplificador) sale de lo cerca que estes de la geoda: nivel 1 al
 * borde del alcance, nivel 4 pegado a la amatista.
 *
 * La lentitud NO se aplica aparte: va integrada como modificador de atributo del
 * propio efecto, asi que sube y baja sola con el nivel.
 */
public class RadiacionEffect extends MobEffect {

    /** Color de las particulas y de la barra del efecto: lila amatista. */
    private static final int COLOR = 0xB980FF;

    /**
     * Fraccion de velocidad que resta cada nivel (nivel 1 = 15%).
     *
     * Al nivel 4 son 60 puntos, o sea tanto como una Lentitud IV de vanilla.
     * Con el maximo de niveles no llega a 100, que es lo que importa: si algun
     * dia se subiera hasta ahi, la compensacion de la pata ligera dividiria por
     * cero. Por eso {@link #compensacionPorAmortiguacion} lo comprueba.
     */
    private static final double LENTITUD_POR_NIVEL = -0.15;

    public static final ResourceKey<MobEffect> CLAVE = ResourceKey.create(
            Registries.MOB_EFFECT,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "radiacion"));

    public static Holder<MobEffect> RADIACION;

    protected RadiacionEffect() {
        super(MobEffectCategory.HARMFUL, COLOR);
    }

    public static void registrar() {
        MobEffect efecto = new RadiacionEffect()
                .addAttributeModifier(
                        Attributes.MOVEMENT_SPEED,
                        Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "radiacion_lentitud"),
                        LENTITUD_POR_NIVEL,
                        AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);

        RADIACION = Registry.registerForHolder(BuiltInRegistries.MOB_EFFECT, CLAVE, efecto);
    }

    // ------------------------------------------------------------------
    //  Amortiguacion (mejora "pata ligera")
    // ------------------------------------------------------------------

    /**
     * Identificador del modificador que devuelve velocidad a quien lleva piezas
     * amortiguadas. Lo pone y lo quita RadiationManager, jugador a jugador.
     */
    public static final Identifier ID_AMORTIGUACION =
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "amortiguacion");

    /**
     * Cuanta velocidad hay que devolver para recortar la lentitud en la
     * fraccion indicada. Devuelve 0 si no hay nada que compensar.
     *
     * La lentitud NO se puede tocar por jugador: el efecto es un singleton del
     * registro y su modificador es el mismo para todo el mundo. Asi que en vez
     * de bajarla se anade un segundo modificador que tira en sentido contrario.
     *
     * Y no vale con "sumar un 25%": los modificadores de este tipo se
     * MULTIPLICAN entre si (el juego hace {@code valor *= 1 + cantidad} por
     * cada uno), no se suman. La lentitud deja la velocidad en (1 - L), y se
     * busca que acabe en (1 - L(1-r)), asi que hay que multiplicar ademas por
     * (1 + c) con:
     *
     * <pre>  c = L*r / (1 - L)</pre>
     *
     * Con las cuatro piezas y la radiacion al maximo sale 0.6 * 1.667 = 1.0: la
     * lentitud se anula clavada, ni un poco de mas.
     *
     * @param amplificador nivel del efecto menos uno, tal cual lo guarda el juego
     * @param piezas       cuantas piezas amortiguadas lleva puestas (0 a 4)
     */
    public static double compensacionPorAmortiguacion(int amplificador, int piezas) {
        if (piezas <= 0) {
            return 0;
        }
        double lentitud = -LENTITUD_POR_NIVEL * (amplificador + 1);
        if (lentitud <= 0 || lentitud >= 1.0) {
            // Con la lentitud actual no se llega ni de lejos, pero si algun dia
            // se sube, aqui es donde se evitaria dividir por cero o por negativo.
            return 0;
        }
        double recorte = Math.min(1.0, HazmatArmor.REDUCCION_LENTITUD * piezas);
        return lentitud * recorte / (1.0 - lentitud);
    }

    // ------------------------------------------------------------------
    //  Dano
    // ------------------------------------------------------------------

    /**
     * Cada cuantos ticks hace dano. Se reparte por nivel: cuanto mas fuerte la
     * radiacion, mas seguido pega.
     */
    @Override
    public boolean shouldApplyEffectTickThisTick(int duracionRestante, int amplificador) {
        int intervalo = Math.max(10, 40 >> amplificador); // nivel 1: 40t, nivel 4: 10t
        return duracionRestante % intervalo == 0;
    }

    @Override
    public boolean applyEffectTick(ServerLevel nivel, LivingEntity entidad, int amplificador) {
        // Desgastar y contar en un solo recorrido de las ranuras: siempre se
        // necesitan juntos y esto corre hasta dos veces por segundo y jugador.
        //
        // El desgaste no lleva interruptor propio: este metodo solo corre
        // mientras el efecto esta activo, asi que apagar la radiacion ya lo apaga.
        // Solo cuentan las piezas que aun filtran: una por debajo del umbral
        // sigue puesta pero ya no protege.
        int piezas = HazmatArmor.desgastarYContarProtectoras(entidad, 1);
        if (piezas >= 4) {
            return true; // inmune, pero el efecto sigue vivo mientras estes cerca
        }

        double dano = (amplificador + 1) * (1.0 - 0.25 * piezas);
        if (dano > 0) {
            entidad.hurtServer(nivel, nivel.damageSources().magic(), (float) dano);
        }
        return true;
    }
}
