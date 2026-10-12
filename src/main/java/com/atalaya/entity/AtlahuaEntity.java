package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.HashSet;
import java.util.Set;

/**
 * Atlahua, el Triton de las Profundidades: el mini jefe del agua. El rey del
 * mar, de seis bloques, lento y pesado, con el tridente de coral a plomo.
 * El agua de sus ataques es de verdad solo para la vista: no deja bloques.
 *
 * <ul>
 *   <li><b>Estocada del Tridente</b> (normal): recoge el tridente y lo clava al
 *   frente con un paso largo; de las puntas sale un chorro de agua de ocho
 *   bloques que empuja.</li>
 *   <li><b>Olas del Abismo</b> (area): hace girar el tridente sobre la cabeza y
 *   lo clava en el suelo: dos olas en anillo salen de el una tras otra.</li>
 *   <li><b>Tsunami del Abismo</b> (especial): alza el tridente con las dos
 *   manos y ruge mientras una ola enorme crece a su espalda; al bajarlo
 *   apuntando al frente, la ola pasa por encima de el y barre la arena.</li>
 * </ul>
 */
public class AtlahuaEntity extends MiniJefeEntity {

    public static final float VIDA = 4800.0F;
    public static final float DANO_ESTOCADA = 24.0F;
    public static final float DANO_OLA = 19.0F;
    public static final float DANO_TSUNAMI = 28.0F;

    /**
     * Lo que ha crecido desde que se ajustaron sus ataques (con la escala 1,31; el 11-10-2026 crecio 4 bloques de
     * alto): lo que sale de su cuerpo (el tridente, las alturas) va por K y las zonas de los ataques por KA, que
     * crece menos para no cambiar tanto la pelea.
     */
    public static final float K = AtlahuaGeometria.ESCALA / 1.31F;
    public static final float KA = (float) Math.sqrt(K);

    /** El chorro de la Estocada: lo largo (el tridente llega mas lejos) y lo ancho. */
    public static final float CHORRO_LARGO = 8.5F * K;
    public static final float CHORRO_ANCHO = 1.8F * KA;
    /** Las olas en anillo: cuando sale cada una (ticks tras el golpe), lo que crecen por tick y hasta donde. */
    public static final int[] OLAS_TICK = {1, 11};
    public static final float OLA_CRECE = 0.78F * KA;
    public static final float OLA_HASTA = 14.0F * KA;
    public static final float OLA_ALTO = 1.6F * KA;
    /** El tsunami: lo ancho, lo alto, lo deprisa que avanza y cuanto. */
    public static final float TSUNAMI_ANCHO = 24.0F;
    public static final float TSUNAMI_ALTO = 7.0F;
    public static final float TSUNAMI_VEL = 0.75F;
    public static final int TSUNAMI_TICKS = 50;
    /** Donde crece el tsunami, detras de el (bloques). */
    public static final float TSUNAMI_DETRAS = 3.0F * K;

    private final Set<Long> golpeados = new HashSet<>();

    public AtlahuaEntity(EntityType<? extends AtlahuaEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return atributosBase(18.0D, 0.24D);
    }

    @Override
    protected float vidaEfectiva() {
        return VIDA;
    }

    @Override
    protected int duracion(int estado) {
        return switch (estado) {
            case DESPERTAR -> AtlahuaGeometria.DURACION_DESPERTAR;
            case NORMAL -> AtlahuaGeometria.DURACION_NORMAL;
            case AREA -> AtlahuaGeometria.DURACION_AREA;
            case ESPECIAL -> AtlahuaGeometria.DURACION_ESPECIAL;
            default -> 20;
        };
    }

    @Override
    public int duracionMuerte() {
        return AtlahuaGeometria.DURACION_MUERTE;
    }

    @Override
    public int disolverDesde() {
        return AtlahuaGeometria.DISOLVER_DESDE;
    }

    @Override
    protected float zancada() {
        return AtlahuaGeometria.ZANCADA;
    }

    @Override
    protected double alcance() {
        return 4.5 * K;
    }

    @Override
    protected int pausa(int estado) {
        return estado == ESPECIAL ? 30 : 16;
    }

    // ------------------------------------------------------------------
    //  Cuando ataca
    // ------------------------------------------------------------------

    @Override
    protected int elegirAtaque(ServerLevel nivel, LivingEntity objetivo, double d) {
        if (listo(ESPECIAL) && d < 26.0) {
            enfriar(ESPECIAL, 20 * 24);
            return ESPECIAL;
        }
        if (listo(AREA) && d < 10.0 * KA && (presasCerca(nivel, position(), 9.0 * KA, 4.0 * K).size() >= 2 || random.nextInt(2) == 0)) {
            enfriar(AREA, 20 * 9);
            return AREA;
        }
        if (listo(NORMAL) && d < 7.5 * K) {
            enfriar(NORMAL, 20 * 2 + 6);
            return NORMAL;
        }
        return -1;
    }

    @Override
    protected void alIniciar(ServerLevel nivel, int estado, @Nullable LivingEntity objetivo) {
        golpeados.clear();
    }

    @Override
    protected void tickDespertar(ServerLevel nivel, int t) {
        if (t == 2) {
            sonido(AtalayaSonidos.ATLAHUA_DESPERTAR, 5.0F);
        }
        if (t == AtlahuaGeometria.DESPERTAR_RUGE) {
            sonido(AtalayaSonidos.ATLAHUA_RUGIDO, 6.0F);
        }
        if (t == AtlahuaGeometria.DESPERTAR_CLAVA) {
            sonido(AtalayaSonidos.ATLAHUA_CLAVA, 5.0F);
            Vec3 p = MiniJefeEntity.puntoMundo(AtlahuaGeometria.PUNTA_CLAVA, position(), getYRot());
            p = new Vec3(p.x, getY() + 0.1, p.z);
            particula(nivel, AtalayaParticulas.MJ_ONDA, p, 0.6, 10.0 * KA, 2);
            particulas(nivel, AtalayaParticulas.MJ_GOTA, p.add(0, 0.5, 0), 40, 1.5 * K, 0.5 * K, 1.5 * K, 0.45);
            particulas(nivel, AtalayaParticulas.MJ_ESPUMA, p, 20, 2.0 * K, 0.2, 2.0 * K, 0.05);
        }
    }

    // ------------------------------------------------------------------
    //  Los ataques
    // ------------------------------------------------------------------

    @Override
    protected void tickAtaque(ServerLevel nivel, int estado, int t, @Nullable LivingEntity objetivo) {
        switch (estado) {
            case NORMAL -> estocada(nivel, t, objetivo);
            case AREA -> olas(nivel, t);
            case ESPECIAL -> tsunami(nivel, t);
            default -> {
            }
        }
    }

    private void estocada(ServerLevel nivel, int t, @Nullable LivingEntity objetivo) {
        if (t < AtlahuaGeometria.NORMAL_CARGA && objetivo != null) {
            girarHacia(objetivo.position(), 12.0F);
            ponerRumbo(getYRot());
        }
        if (t == AtlahuaGeometria.NORMAL_CARGA - 4) {
            sonido(AtalayaSonidos.ATLAHUA_ESTOCADA, 4.0F, 0.9F);
        }
        if (t == AtlahuaGeometria.NORMAL_GOLPE) {
            Vec3 f = frente();
            Vec3 o = position();
            for (LivingEntity v : presasCerca(nivel, o.add(f.scale(CHORRO_LARGO * 0.5)), CHORRO_LARGO * 0.6, 3.5 * K)) {
                Vec3 rel = v.position().subtract(o);
                double a = rel.x * f.x + rel.z * f.z;
                double lado = Math.abs(rel.x * f.z - rel.z * f.x);
                if (a > 0.0 && a < CHORRO_LARGO && lado < CHORRO_ANCHO) {
                    golpear(nivel, v, MiniJefeDanos.ATLAHUA_ESTOCADA, DANO_ESTOCADA, o, 1.3, 0.35);
                }
            }
            for (int i = 2; i <= Math.round(CHORRO_LARGO); i++) {
                Vec3 p = o.add(f.scale(i)).add(0, 1.8 * K - (1.8 * K - 1.0) * i / CHORRO_LARGO, 0);
                particulas(nivel, AtalayaParticulas.MJ_GOTA, p, 4, 0.3 * KA, 0.3 * KA, 0.3 * KA, 0.25);
                particulas(nivel, AtalayaParticulas.MJ_ESPUMA, p, 2, 0.3 * KA, 0.2, 0.3 * KA, 0.05);
            }
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, o.add(f.scale(4.0 * K)).add(0, 2.0 * K, 0), 1.8 * K, 0, 2);
        }
    }

    /** Donde clava el tridente en las Olas del Abismo (en el suelo). */
    public static Vec3 centroOlas(Vec3 pies, float rumbo) {
        Vec3 p = MiniJefeEntity.puntoMundo(AtlahuaGeometria.PUNTA_GOLPE, pies, rumbo);
        return new Vec3(p.x, pies.y, p.z);
    }

    private void olas(ServerLevel nivel, int t) {
        Vec3 c = centroOlas(position(), getRumbo());
        if (t == 4) {
            sonido(AtalayaSonidos.ATLAHUA_ESTOCADA, 3.0F, 0.7F);
        }
        if (t == AtlahuaGeometria.AREA_GOLPE) {
            sonido(AtalayaSonidos.ATLAHUA_GOLPE, 6.0F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, c.add(0, 0.1, 0), 0.9, 6.0 * KA, 2);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, c.add(0, 0.8 * K, 0), 2.5 * K, 0, 2);
            particulas(nivel, AtalayaParticulas.MJ_GOTA, c.add(0, 0.5, 0), 50, 1.5 * K, 0.6 * K, 1.5 * K, 0.55);
            particulas(nivel, AtalayaParticulas.MJ_ESPUMA, c, 24, 1.5 * K, 0.3, 1.5 * K, 0.06);
        }
        for (int i = 0; i < OLAS_TICK.length; i++) {
            int k = t - AtlahuaGeometria.AREA_GOLPE - OLAS_TICK[i];
            if (k == 0) {
                sonido(AtalayaSonidos.ATLAHUA_OLA, 5.0F, 1.0F - i * 0.08F);
            }
            if (k < 0) {
                continue;
            }
            float r = 1.0F + k * OLA_CRECE;
            if (r > OLA_HASTA + 1.0F) {
                continue;
            }
            for (LivingEntity v : presasCerca(nivel, c, r + 1.2, 4.0)) {
                double d = horizontal(c, v.position());
                long clave = ((long) v.getId() << 2) | i;
                if (d > r - OLA_CRECE - 1.0 && v.getY() - getY() < OLA_ALTO + 0.6 && !golpeados.contains(clave)) {
                    golpeados.add(clave);
                    golpear(nivel, v, MiniJefeDanos.ATLAHUA_OLAS, DANO_OLA, c, 1.15, 0.6);
                    particulas(nivel, AtalayaParticulas.MJ_GOTA, v.position().add(0, 0.8, 0), 12, 0.4, 0.4, 0.4, 0.3);
                }
            }
        }
    }

    /** El tsunami: donde esta su frente a los k ticks de soltarlo (en el suelo), con el rumbo del ataque. */
    public static Vec3 frenteTsunami(Vec3 pies, float rumbo, float k) {
        Vec3 f = frente(rumbo);
        return pies.add(f.scale(-TSUNAMI_DETRAS + k * TSUNAMI_VEL));
    }

    private void tsunami(ServerLevel nivel, int t) {
        if (t == 6) {
            sonido(AtalayaSonidos.ATLAHUA_TSUNAMI, 6.5F);
        }
        if (t == AtlahuaGeometria.ESPECIAL_RUGE) {
            sonido(AtalayaSonidos.ATLAHUA_RUGIDO, 6.0F, 0.9F);
        }
        if (t > 6 && t < AtlahuaGeometria.ESPECIAL_LANZA && t % 2 == 0) {
            // El agua sube a su espalda.
            Vec3 b = frenteTsunami(position(), getRumbo(), 0);
            Vec3 lado = new Vec3(frente().z, 0, -frente().x);
            for (int i = 0; i < 3; i++) {
                Vec3 p = b.add(lado.scale((random.nextDouble() - 0.5) * TSUNAMI_ANCHO)).add(0, random.nextDouble() * 3, 0);
                particulas(nivel, AtalayaParticulas.MJ_GOTA, p, 1, 0.2, 0.2, 0.2, 0.2);
            }
        }
        int k = t - AtlahuaGeometria.ESPECIAL_LANZA;
        if (k == 0) {
            sonido(AtalayaSonidos.ATLAHUA_OLA, 6.5F, 0.7F);
        }
        if (k >= 0 && k <= TSUNAMI_TICKS) {
            Vec3 f = frente(getRumbo());
            Vec3 fr = frenteTsunami(position(), getRumbo(), k);
            float alto = TSUNAMI_ALTO * Mth.clamp(1.15F - k / (float) TSUNAMI_TICKS * 0.6F, 0.0F, 1.0F);
            for (LivingEntity v : presasCerca(nivel, fr, TSUNAMI_ANCHO * 0.5 + 2.0, alto + 2.0)) {
                Vec3 rel = v.position().subtract(fr);
                double a = rel.x * f.x + rel.z * f.z;
                double lado = Math.abs(rel.x * f.z - rel.z * f.x);
                long clave = v.getId();
                if (Math.abs(a) < 1.8 && lado < TSUNAMI_ANCHO * 0.5 && v.getY() - fr.y < alto && !golpeados.contains(clave)) {
                    golpeados.add(clave);
                    golpear(nivel, v, MiniJefeDanos.ATLAHUA_TSUNAMI, DANO_TSUNAMI, v.position().subtract(f), 1.5, 0.6);
                }
            }
            if (k == TSUNAMI_TICKS) {
                sonido(AtalayaSonidos.ATLAHUA_TSUNAMI_ROMPE, 6.0F);
                nivel.playSound(null, fr.x, fr.y, fr.z, AtalayaSonidos.ATLAHUA_TSUNAMI_ROMPE, net.minecraft.sounds.SoundSource.HOSTILE,
                        6.0F, 1.0F);
                Vec3 lado = new Vec3(f.z, 0, -f.x);
                for (int i = -5; i <= 5; i++) {
                    Vec3 p = fr.add(lado.scale(i * TSUNAMI_ANCHO / 11.0)).add(0, 0.5, 0);
                    particulas(nivel, AtalayaParticulas.MJ_ESPUMA, p, 6, 1.0, 0.6, 1.0, 0.08);
                    particulas(nivel, AtalayaParticulas.MJ_GOTA, p.add(0, 1, 0), 6, 1.0, 1.0, 1.0, 0.4);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  Lo que ve el cliente
    // ------------------------------------------------------------------

    @Override
    protected void efectosCliente(int estado, int tiempo) {
        Level l = level();
        if (tickCount % 6 == 0) {
            // Burbujas que le suben del cuerpo y gotas que le caen de las algas.
            l.addParticle(AtalayaParticulas.MJ_BURBUJA, getX() + (random.nextDouble() - 0.5) * 2.0 * K,
                    getY() + (1.0 + random.nextDouble() * 3.0) * K, getZ() + (random.nextDouble() - 0.5) * 2.0 * K, 0, 0.02, 0);
        }
        if (estado != DORMIDO && tickCount % 4 == 0) {
            Vec3 p = puntoMundo(new Vec3((random.nextDouble() - 0.5) * 1.6, 2.0 + random.nextDouble() * 2.0, -0.9).scale(K));
            l.addParticle(AtalayaParticulas.MJ_GOTA, p.x, p.y, p.z, 0, -0.05, 0);
        }
        if (estado == LIBRE && velocidad > 0.03F && tickCount % 5 == 0) {
            l.addParticle(AtalayaParticulas.MJ_ESPUMA, getX() + (random.nextDouble() - 0.5) * 1.4 * K, getY() + 0.1,
                    getZ() + (random.nextDouble() - 0.5) * 1.4 * K, 0, 0.01, 0);
        }
        if (estado == ESPECIAL && tiempo > AtlahuaGeometria.ESPECIAL_LANZA) {
            int k = tiempo - AtlahuaGeometria.ESPECIAL_LANZA;
            if (k <= TSUNAMI_TICKS) {
                Vec3 f = frente(getRumbo());
                Vec3 fr = frenteTsunami(position(), getRumbo(), k);
                Vec3 lado = new Vec3(f.z, 0, -f.x);
                float alto = TSUNAMI_ALTO * Mth.clamp(1.15F - k / (float) TSUNAMI_TICKS * 0.6F, 0.0F, 1.0F);
                for (int i = 0; i < 6; i++) {
                    Vec3 p = fr.add(lado.scale((random.nextDouble() - 0.5) * TSUNAMI_ANCHO)).add(0, alto * (0.85 + random.nextDouble() * 0.2), 0);
                    l.addParticle(AtalayaParticulas.MJ_ESPUMA, p.x, p.y, p.z, f.x * 0.3, 0.05, f.z * 0.3);
                    l.addParticle(AtalayaParticulas.MJ_GOTA, p.x, p.y, p.z, f.x * 0.4 + (random.nextDouble() - 0.5) * 0.2, 0.3,
                            f.z * 0.4 + (random.nextDouble() - 0.5) * 0.2);
                }
            }
        }
        if (estado == AREA && tiempo > AtlahuaGeometria.AREA_GOLPE) {
            Vec3 c = centroOlas(position(), getRumbo());
            for (int i = 0; i < OLAS_TICK.length; i++) {
                int k = tiempo - AtlahuaGeometria.AREA_GOLPE - OLAS_TICK[i];
                float r = 1.0F + k * OLA_CRECE;
                if (k >= 0 && r < OLA_HASTA) {
                    for (int j = 0; j < 8; j++) {
                        double a = random.nextDouble() * Mth.TWO_PI;
                        l.addParticle(AtalayaParticulas.MJ_ESPUMA, c.x + Math.cos(a) * r, getY() + OLA_ALTO * 0.9, c.z + Math.sin(a) * r,
                                Math.cos(a) * 0.15, 0.05, Math.sin(a) * 0.15);
                    }
                }
            }
        }
    }

    @Override
    protected void efectosMuerte(int tiempo) {
        if (tiempo > disolverDesde() && tiempo % 2 == 0) {
            for (int i = 0; i < 3; i++) {
                level().addParticle(i == 0 ? AtalayaParticulas.MJ_BURBUJA : AtalayaParticulas.MJ_ESPUMA,
                        getX() + (random.nextDouble() - 0.5) * 3.0 * K, getY() + random.nextDouble() * 3.5 * K,
                        getZ() + (random.nextDouble() - 0.5) * 3.0 * K, 0, 0.04, 0);
            }
        }
    }

    @Override
    protected void tickMuerte(ServerLevel nivel, int tiempo) {
        if (tiempo == AtlahuaGeometria.MUERTE_RODILLA) {
            sonido(AtalayaSonidos.ATLAHUA_PASO, 4.0F, 0.7F);
            particulas(nivel, AtalayaParticulas.MJ_ESPUMA, position(), 16, 1.2 * K, 0.1, 1.2 * K, 0.04);
        }
        if (tiempo == AtlahuaGeometria.MUERTE_CAE) {
            sonido(AtalayaSonidos.ATLAHUA_GOLPE, 4.0F, 0.6F);
            particulas(nivel, AtalayaParticulas.MJ_GOTA, position().add(0, 0.5, 0), 30, 2.0 * K, 0.3, 2.0 * K, 0.3);
        }
        if (tiempo == duracionMuerte() - 1) {
            particulas(nivel, AtalayaParticulas.MJ_ESPUMA, position().add(0, 1.0 * K, 0), 40, 1.8 * K, 1.0 * K, 1.8 * K, 0.05);
            particulas(nivel, AtalayaParticulas.MJ_BURBUJA, position().add(0, 1.5 * K, 0), 30, 1.5 * K, 1.5 * K, 1.5 * K, 0.05);
        }
    }

    // ------------------------------------------------------------------
    //  Sonidos de vanilla
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        return getEstado() == DORMIDO ? null : AtalayaSonidos.ATLAHUA_AMBIENTE;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 220;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.ATLAHUA_HERIDO;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return AtalayaSonidos.ATLAHUA_MUERTE;
    }

    @Override
    protected float getSoundVolume() {
        return 3.0F;
    }

    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState bloque) {
        playSound(AtalayaSonidos.ATLAHUA_PASO, 1.6F, 0.85F + random.nextFloat() * 0.2F);
    }

    @Override
    protected @Nullable SoundEvent sonidoInmune() {
        return AtalayaSonidos.ATLAHUA_INMUNE;
    }

    @Override
    protected ParticleOptions particulaInmune() {
        return AtalayaParticulas.MJ_GOTA;
    }
}
