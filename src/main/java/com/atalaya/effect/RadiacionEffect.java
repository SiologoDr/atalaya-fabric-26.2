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

    /** Fraccion de velocidad que resta cada nivel (nivel 1 = 10%). */
    private static final double LENTITUD_POR_NIVEL = -0.10;

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
