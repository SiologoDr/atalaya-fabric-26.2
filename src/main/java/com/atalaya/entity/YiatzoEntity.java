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
 * Yiatzo, el Mago del Viento: el mini jefe del aire. No anda: flota medio
 * bloque sobre el suelo con sus cinco losas de glifos dandole vueltas, y no se
 * deja acercar (guarda de 9 a 14 bloques con su presa y la rodea).
 *
 * <ul>
 *   <li><b>Rafaga de Viento</b> (normal): descarga el baston en diagonal y salen
 *   tres cuchillas de viento en abanico (1,4 bloques por tick, 22 de alcance) que
 *   cortan y empujan a quien atraviesan.</li>
 *   <li><b>Tormenta de Viento</b> (area): sube con los brazos abiertos (las losas
 *   se apartan girando) y los baja de golpe: un anillo de viento sale de el hasta
 *   doce bloques y medio y lanza por los aires a quien alcanza.</li>
 *   <li><b>Ciclon Devastador</b> (especial): alza el baston y gira sobre si
 *   mismo; donde estaba su presa crece un ciclon que arrastra hacia dentro, alza
 *   y golpea a quien atrapa, y al final estalla y lo lanza todo lejos.</li>
 * </ul>
 */
public class YiatzoEntity extends MiniJefeEntity {

    public static final float VIDA = 3600.0F;
    public static final float DANO_CUCHILLA = 19.0F;
    public static final float DANO_TORMENTA = 20.0F;
    public static final float DANO_CICLON = 5.0F;
    public static final float DANO_ESTALLIDO = 25.0F;

    /**
     * Lo que ha crecido desde que se ajustaron sus ataques (con la escala 1,24; el 11-10-2026 crecio 4 bloques de
     * alto): lo que sale de su cuerpo va por K y las zonas y distancias de la pelea por KA, que crece menos.
     */
    public static final float K = YiatzoGeometria.ESCALA / 1.24F;
    public static final float KA = (float) Math.sqrt(K);

    /** Las cuchillas: cuantas, lo que se abren (grados), lo deprisa que van y hasta donde. */
    public static final int CUCHILLAS = 3;
    public static final float ABANICO = 18.0F;
    public static final float VEL_CUCHILLA = 1.4F;
    public static final float ALCANCE_CUCHILLA = 22.0F;
    /** El anillo de la Tormenta: de donde sale, lo que crece por tick y hasta donde. */
    public static final float ANILLO_DESDE = 1.5F * K;
    public static final float ANILLO_CRECE = 0.85F * KA;
    public static final float ANILLO_HASTA = 12.5F * KA;
    /** El ciclon: lo que arrastra, lo que atrapa (alza y golpea) y el estallido. */
    public static final float CICLON_ARRASTRA = 11.0F;
    public static final float CICLON_ATRAPA = 4.5F;
    public static final float CICLON_ESTALLA = 7.5F;
    public static final float CICLON_ALTO = 14.0F;

    private final Set<Integer> golpeados = new HashSet<>();
    private Vec3 origenCuchillas = Vec3.ZERO;
    private double piesCuchillas;
    private int sueltaCuchillas = -1;
    private final Set<Long> cortados = new HashSet<>();
    private int rodeo = 1;

    public YiatzoEntity(EntityType<? extends YiatzoEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return atributosBase(10.0D, 0.26D);
    }

    @Override
    protected float vidaEfectiva() {
        return VIDA;
    }

    @Override
    protected int duracion(int estado) {
        return switch (estado) {
            case DESPERTAR -> YiatzoGeometria.DURACION_DESPERTAR;
            case NORMAL -> YiatzoGeometria.DURACION_NORMAL;
            case AREA -> YiatzoGeometria.DURACION_AREA;
            case ESPECIAL -> YiatzoGeometria.DURACION_ESPECIAL;
            default -> 20;
        };
    }

    @Override
    public int duracionMuerte() {
        return YiatzoGeometria.DURACION_MUERTE;
    }

    @Override
    public int disolverDesde() {
        return YiatzoGeometria.DISOLVER_DESDE;
    }

    @Override
    protected float zancada() {
        return YiatzoGeometria.ZANCADA;
    }

    @Override
    protected int pausa(int estado) {
        return estado == ESPECIAL ? 34 : 14;
    }

    /** Guarda la distancia: se aleja si le comen terreno, se acerca si se le escapan y si no, rodea a su presa. */
    @Override
    protected void moverse(ServerLevel nivel, @Nullable LivingEntity objetivo, double d) {
        if (objetivo == null) {
            super.moverse(nivel, null, d);
            return;
        }
        Vec3 o = objetivo.position();
        Vec3 fuera = horizontalHacia(o, position());
        Vec3 lado = new Vec3(-fuera.z, 0, fuera.x).scale(rodeo);
        if (tickCount % 120 == 0) {
            rodeo = random.nextBoolean() ? 1 : -1;
        }
        Vec3 meta;
        if (d < 8.0 * KA) {
            meta = position().add(fuera.scale(5.0)).add(lado.scale(2.0));
        } else if (d > 15.0 * KA) {
            meta = o.add(fuera.scale(12.0 * KA));
        } else {
            meta = position().add(lado.scale(4.0));
        }
        Vec3 c = Vec3.atBottomCenterOf(centro);
        Vec3 rel = new Vec3(meta.x - c.x, 0, meta.z - c.z);
        if (rel.length() > CORREA) {
            meta = c.add(rel.normalize().scale(CORREA));
        }
        getMoveControl().setWantedPosition(meta.x, getY(), meta.z, paso());
        girarHacia(o, 10.0F);
    }

    // ------------------------------------------------------------------
    //  Cuando ataca
    // ------------------------------------------------------------------

    @Override
    protected int elegirAtaque(ServerLevel nivel, LivingEntity objetivo, double d) {
        if (listo(ESPECIAL) && d < 26.0) {
            enfriar(ESPECIAL, 20 * 22);
            return ESPECIAL;
        }
        if (listo(AREA) && presasCerca(nivel, position(), 7.0 * KA, 4.0 * K).size() >= 1) {
            enfriar(AREA, 20 * 8);
            return AREA;
        }
        if (listo(NORMAL) && d < ALCANCE_CUCHILLA) {
            enfriar(NORMAL, 20 * 2 + 10);
            return NORMAL;
        }
        return -1;
    }

    @Override
    protected void alIniciar(ServerLevel nivel, int estado, @Nullable LivingEntity objetivo) {
        golpeados.clear();
        if (estado == ESPECIAL && objetivo != null) {
            // El ciclon nace donde esta su presa, en el suelo.
            Vec3 o = objetivo.position();
            ponerPunto(new Vec3(o.x, suelo(nivel, o.x, o.y + 1.0, o.z), o.z));
        }
        if (estado == AREA) {
            sonido(AtalayaSonidos.YIATZO_TORMENTA, 4.0F);
        }
    }

    @Override
    protected void tickDespertar(ServerLevel nivel, int t) {
        if (t == 2) {
            sonido(AtalayaSonidos.YIATZO_DESPERTAR, 5.0F);
        }
        if (t == YiatzoGeometria.DESPERTAR_SE_ALZA) {
            sonido(AtalayaSonidos.YIATZO_LOSAS, 4.0F);
            particulas(nivel, AtalayaParticulas.MJ_POLVO, position(), 20, 2.5 * K, 0.1, 2.5 * K, 0.04);
        }
        if (t == YiatzoGeometria.DESPERTAR_ALZADO) {
            sonido(AtalayaSonidos.YIATZO_GRITO, 6.0F);
        }
        if (t == YiatzoGeometria.DESPERTAR_RUGE) {
            sonido(AtalayaSonidos.YIATZO_GOLPE, 5.0F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, position().add(0, 0.1, 0), 0.6, 10.0 * KA, 1);
            particulas(nivel, AtalayaParticulas.MJ_VIENTO, position().add(0, 1.0 * K, 0), 40, 3.0 * K, 0.5 * K, 3.0 * K, 0.3);
        }
    }

    // ------------------------------------------------------------------
    //  Los ataques
    // ------------------------------------------------------------------

    @Override
    protected void tickAtaque(ServerLevel nivel, int estado, int t, @Nullable LivingEntity objetivo) {
        switch (estado) {
            case NORMAL -> rafaga(nivel, t, objetivo);
            case AREA -> tormenta(nivel, t);
            case ESPECIAL -> ciclon(nivel, t);
            default -> {
            }
        }
    }

    /** Donde salen las cuchillas (el orbe al descargar) y hacia donde va cada una. */
    public static Vec3 origenCuchillas(Vec3 pies, float rumbo) {
        return MiniJefeEntity.puntoMundo(YiatzoGeometria.ORBE_SUELTA, pies, rumbo);
    }

    public static Vec3 rumboCuchilla(float rumbo, int i) {
        return frente(rumbo + (i - (CUCHILLAS - 1) / 2.0F) * ABANICO);
    }

    /**
     * Donde va la cuchilla i k ticks despues de salir: sale del orbe (que con su tamano queda alto) y en cuatro ticks
     * baja a la altura del pecho, 1,2 bloques sobre sus pies (piesY), y sigue recta.
     */
    public static Vec3 cuchilla(Vec3 origen, double piesY, float rumbo, int i, float k) {
        Vec3 q = origen.add(rumboCuchilla(rumbo, i).scale(k * VEL_CUCHILLA));
        return new Vec3(q.x, Mth.lerp(Math.min(1.0, k / 4.0), origen.y, piesY + 1.2), q.z);
    }

    private void rafaga(ServerLevel nivel, int t, @Nullable LivingEntity objetivo) {
        if (t <= YiatzoGeometria.NORMAL_CARGA && objetivo != null) {
            girarHacia(objetivo.position(), 12.0F);
            ponerRumbo(getYRot());
        }
        if (t == YiatzoGeometria.NORMAL_CARGA) {
            sonido(AtalayaSonidos.YIATZO_RAFAGA, 3.5F, 0.85F);
        }
        if (t == YiatzoGeometria.NORMAL_SUELTA) {
            sonido(AtalayaSonidos.YIATZO_RAFAGA, 4.0F, 1.1F);
            origenCuchillas = origenCuchillas(position(), getRumbo());
            piesCuchillas = getY();
            sueltaCuchillas = tickCount;
            cortados.clear();
            particulas(nivel, AtalayaParticulas.MJ_VIENTO, origenCuchillas, 14, 0.4, 0.4, 0.4, 0.3);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, origenCuchillas, 1.6, 0, 1);
        }
    }

    /** Las cuchillas en vuelo (siguen aunque acabe el ataque): cortan a quien atraviesan, una vez cada una. */
    private void moverCuchillas(ServerLevel nivel) {
        if (sueltaCuchillas < 0) {
            return;
        }
        int k = tickCount - sueltaCuchillas;
        float hasta = ALCANCE_CUCHILLA / VEL_CUCHILLA;
        if (k > hasta) {
            sueltaCuchillas = -1;
            return;
        }
        for (int i = 0; i < CUCHILLAS; i++) {
            Vec3 d = rumboCuchilla(getRumbo(), i);
            Vec3 a = cuchilla(origenCuchillas, piesCuchillas, getRumbo(), i, Math.max(0, k - 1));
            Vec3 b = cuchilla(origenCuchillas, piesCuchillas, getRumbo(), i, k);
            for (LivingEntity v : presasCerca(nivel, b, VEL_CUCHILLA + 1.6, 3.0)) {
                long clave = ((long) v.getId() << 4) | i;
                if (cortados.contains(clave) || distanciaSegmento(v.position().add(0, v.getBbHeight() * 0.5, 0), a, b) > 1.5) {
                    continue;
                }
                cortados.add(clave);
                golpear(nivel, v, MiniJefeDanos.YIATZO_RAFAGA, DANO_CUCHILLA, v.position().subtract(d), 1.1, 0.4);
                particulas(nivel, AtalayaParticulas.MJ_VIENTO, v.position().add(0, 1, 0), 10, 0.4, 0.5, 0.4, 0.25);
                nivel.playSound(null, v.getX(), v.getY(), v.getZ(), AtalayaSonidos.YIATZO_CUCHILLA,
                        net.minecraft.sounds.SoundSource.HOSTILE, 2.5F, 0.9F + random.nextFloat() * 0.2F);
            }
        }
    }

    private static double distanciaSegmento(Vec3 p, Vec3 a, Vec3 b) {
        Vec3 ab = b.subtract(a);
        double l2 = ab.lengthSqr();
        double k = l2 < 1.0E-6 ? 0 : Mth.clamp(p.subtract(a).dot(ab) / l2, 0, 1);
        return p.distanceTo(a.add(ab.scale(k)));
    }

    /** Tormenta de Viento: el anillo que sale de el y lanza por los aires. */
    private void tormenta(ServerLevel nivel, int t) {
        if (t < YiatzoGeometria.AREA_SUELTA && t % 2 == 0) {
            // El viento se le junta mientras carga.
            for (int i = 0; i < 3; i++) {
                double a = random.nextDouble() * Mth.TWO_PI;
                Vec3 p = position().add(Math.cos(a) * 7 * KA, (0.5 + random.nextDouble() * 3) * K, Math.sin(a) * 7 * KA);
                Vec3 v = position().add(0, 2 * K, 0).subtract(p).scale(0.08);
                nivel.sendParticles(AtalayaParticulas.MJ_VIENTO, true, true, p.x, p.y, p.z, 0, v.x, v.y, v.z, 1.0);
            }
        }
        if (t == YiatzoGeometria.AREA_SUELTA) {
            sonido(AtalayaSonidos.YIATZO_ESTALLIDO, 6.0F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, position().add(0, 0.1, 0), 0.9, ANILLO_HASTA, 1);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, position().add(0, 1.5 * K, 0), 3.0 * K, 0, 1);
        }
        int k = t - YiatzoGeometria.AREA_SUELTA;
        if (k >= 0) {
            float r = ANILLO_DESDE + k * ANILLO_CRECE;
            if (r <= ANILLO_HASTA + 1.0F) {
                for (LivingEntity v : presasCerca(nivel, position(), r + 1.0, 4.0)) {
                    double d = horizontal(position(), v.position());
                    if (d > r - ANILLO_CRECE - 1.0 && !golpeados.contains(v.getId())) {
                        golpeados.add(v.getId());
                        golpear(nivel, v, MiniJefeDanos.YIATZO_TORMENTA, DANO_TORMENTA, position(), 1.7, 0.75);
                    }
                }
            }
        }
    }

    /** Ciclon Devastador: crece donde estaba su presa, arrastra, alza y golpea, y estalla. */
    private void ciclon(ServerLevel nivel, int t) {
        Vec3 c = getPunto();
        if (t == YiatzoGeometria.ESPECIAL_FORMA) {
            sonido(AtalayaSonidos.YIATZO_CICLON, 6.0F);
            nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.YIATZO_CICLON, net.minecraft.sounds.SoundSource.HOSTILE, 5.0F, 0.9F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, c.add(0, 0.1, 0), 0.4, 6.0, 1);
        }
        if (t > YiatzoGeometria.ESPECIAL_FORMA && t < YiatzoGeometria.ESPECIAL_ESTALLA) {
            float crece = Mth.clamp((t - YiatzoGeometria.ESPECIAL_FORMA) / 24.0F, 0.0F, 1.0F);
            for (LivingEntity v : presasCerca(nivel, c, CICLON_ARRASTRA, CICLON_ALTO)) {
                Vec3 rel = v.position().subtract(c);
                double d = Math.sqrt(rel.x * rel.x + rel.z * rel.z);
                Vec3 dentro = d < 1.0E-3 ? Vec3.ZERO : new Vec3(-rel.x / d, 0, -rel.z / d);
                Vec3 gira = new Vec3(-dentro.z, 0, dentro.x);
                double fuerza = crece * (0.07 + 0.08 * (1.0 - d / CICLON_ARRASTRA));
                double alto = v.getY() - c.y;
                double sube = d < CICLON_ATRAPA && alto < 6.0 ? 0.11 * crece : (d < CICLON_ATRAPA ? 0.02 : 0.0);
                Vec3 vel = v.getDeltaMovement();
                v.setDeltaMovement(vel.x * 0.8 + dentro.x * fuerza + gira.x * fuerza * 1.6,
                        Math.max(vel.y, sube > 0 ? sube : vel.y), vel.z * 0.8 + dentro.z * fuerza + gira.z * fuerza * 1.6);
                v.hurtMarked = true;
                v.fallDistance = 0;
                if (d < CICLON_ATRAPA && (t + v.getId()) % 10 == 0) {
                    golpear(nivel, v, MiniJefeDanos.YIATZO_CICLON, DANO_CICLON, c, 0.0, 0.0);
                }
            }
            if (t % 2 == 0) {
                double a = t * 0.6;
                double h = random.nextDouble() * CICLON_ALTO * crece;
                double r = 1.0 + h * 0.35;
                Vec3 p = c.add(Math.cos(a) * r, h, Math.sin(a) * r);
                particulas(nivel, AtalayaParticulas.MJ_POLVO, p, 2, 0.4, 0.4, 0.4, 0.05);
            }
        }
        if (t == YiatzoGeometria.ESPECIAL_ESTALLA) {
            sonido(AtalayaSonidos.YIATZO_CICLON_ESTALLA, 6.5F);
            nivel.playSound(null, c.x, c.y, c.z, AtalayaSonidos.YIATZO_CICLON_ESTALLA, net.minecraft.sounds.SoundSource.HOSTILE,
                    6.0F, 1.0F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, c.add(0, 0.1, 0), 1.2, 16.0, 1);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, c.add(0, 3.0, 0), 5.0, 0, 1);
            particulas(nivel, AtalayaParticulas.MJ_VIENTO, c.add(0, 3, 0), 60, 3.0, 3.0, 3.0, 0.5);
            particulas(nivel, AtalayaParticulas.MJ_POLVO, c, 40, 4.0, 1.0, 4.0, 0.1);
            for (LivingEntity v : presasCerca(nivel, c, CICLON_ESTALLA, CICLON_ALTO)) {
                golpear(nivel, v, MiniJefeDanos.YIATZO_CICLON, DANO_ESTALLIDO, c, 2.0, 0.9);
            }
        }
    }

    @Override
    protected void customServerAiStep(ServerLevel nivel) {
        super.customServerAiStep(nivel);
        if (!isDeadOrDying()) {
            moverCuchillas(nivel);
        }
    }

    // ------------------------------------------------------------------
    //  Lo que ve el cliente
    // ------------------------------------------------------------------

    @Override
    protected void efectosCliente(int estado, int tiempo) {
        Level l = level();
        if (estado != DORMIDO && tickCount % 3 == 0) {
            // Jirones de viento que le rodean y alguna runa que sube del libro.
            double a = random.nextDouble() * Mth.TWO_PI;
            l.addParticle(AtalayaParticulas.MJ_VIENTO, getX() + Math.cos(a) * 1.6 * K, getY() + (0.4 + random.nextDouble() * 1.5) * K,
                    getZ() + Math.sin(a) * 1.6 * K, -Math.sin(a) * 0.08, 0.02, Math.cos(a) * 0.08);
        }
        if (estado != DORMIDO && tickCount % 11 == 0) {
            Vec3 p = puntoMundo(new Vec3(0.9, 3.2, 1.6).scale(K));
            l.addParticle(AtalayaParticulas.MJ_RUNA, p.x, p.y, p.z, (random.nextDouble() - 0.5) * 0.03, 0.04,
                    (random.nextDouble() - 0.5) * 0.03);
        }
        if (estado == ESPECIAL && tiempo > YiatzoGeometria.ESPECIAL_FORMA && tiempo < YiatzoGeometria.ESPECIAL_ESTALLA) {
            Vec3 c = getPunto();
            float crece = Mth.clamp((tiempo - YiatzoGeometria.ESPECIAL_FORMA) / 24.0F, 0.0F, 1.0F);
            for (int i = 0; i < 4; i++) {
                double h = random.nextDouble() * CICLON_ALTO * crece;
                double r = 0.8 + h * 0.38;
                double a = random.nextDouble() * Mth.TWO_PI;
                l.addParticle(AtalayaParticulas.MJ_VIENTO, c.x + Math.cos(a) * r, c.y + h, c.z + Math.sin(a) * r,
                        -Math.sin(a) * 0.4, 0.08, Math.cos(a) * 0.4);
            }
        }
        if (estado == AREA && tiempo < YiatzoGeometria.AREA_SUELTA) {
            Vec3 p = puntoMundo(YiatzoGeometria.ORBE_AREA);
            l.addParticle(AtalayaParticulas.MJ_RUNA, p.x, p.y, p.z, (random.nextDouble() - 0.5) * 0.2, 0.05,
                    (random.nextDouble() - 0.5) * 0.2);
        }
    }

    @Override
    protected void efectosMuerte(int tiempo) {
        if (tiempo > disolverDesde() && tiempo % 2 == 0) {
            for (int i = 0; i < 3; i++) {
                level().addParticle(i == 0 ? AtalayaParticulas.MJ_RUNA : AtalayaParticulas.MJ_VIENTO,
                        getX() + (random.nextDouble() - 0.5) * 2.5 * K, getY() + random.nextDouble() * 4.0 * K,
                        getZ() + (random.nextDouble() - 0.5) * 2.5 * K, (random.nextDouble() - 0.5) * 0.1, 0.08,
                        (random.nextDouble() - 0.5) * 0.1);
            }
        }
    }

    @Override
    protected void tickMuerte(ServerLevel nivel, int tiempo) {
        if (tiempo == YiatzoGeometria.MUERTE_CAE) {
            sonido(AtalayaSonidos.YIATZO_LOSAS, 4.0F, 0.7F);
            particulas(nivel, AtalayaParticulas.MJ_POLVO, position(), 26, 2.5 * K, 0.1, 2.5 * K, 0.04);
        }
        if (tiempo == duracionMuerte() - 1) {
            particulas(nivel, AtalayaParticulas.MJ_VIENTO, position().add(0, 2 * K, 0), 50, 1.5 * K, 1.5 * K, 1.5 * K, 0.3);
            particulas(nivel, AtalayaParticulas.MJ_RUNA, position().add(0, 2 * K, 0), 30, 1.5 * K, 1.5 * K, 1.5 * K, 0.1);
        }
    }

    // ------------------------------------------------------------------
    //  Sonidos de vanilla
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        return getEstado() == DORMIDO ? null : AtalayaSonidos.YIATZO_AMBIENTE;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 200;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.YIATZO_HERIDO;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return AtalayaSonidos.YIATZO_MUERTE;
    }

    @Override
    protected float getSoundVolume() {
        return 3.0F;
    }

    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState bloque) {
        // Flota: no pisa.
    }

    @Override
    protected @Nullable SoundEvent sonidoInmune() {
        return AtalayaSonidos.YIATZO_INMUNE;
    }

    @Override
    protected ParticleOptions particulaInmune() {
        return AtalayaParticulas.MJ_RUNA;
    }
}
