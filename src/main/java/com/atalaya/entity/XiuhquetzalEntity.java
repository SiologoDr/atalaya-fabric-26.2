package com.atalaya.entity;

import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
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
 * Xiuhquetzal, el Fenix de Llamas: el mini jefe del fuego. Vuela de verdad:
 * se cierne a dos bloques y medio del suelo rodeando a su presa, con once
 * bloques de ala a ala. Duerme posado, envuelto en sus alas como un capullo de
 * brasa, y al despertar renace: las alas se abren de golpe y despega.
 *
 * <ul>
 *   <li><b>Picotazo de Llamas</b> (normal): se encabrita, pliega las alas y se
 *   lanza en picado sobre su presa con el pico por delante: revienta en fuego
 *   y remonta.</li>
 *   <li><b>Tormenta de Plumas Igneas</b> (area): tres batidas enormes; de cada
 *   una sale una corona de plumas de fuego que caen en anillos cada vez mas
 *   anchos alrededor de su presa y arden al tocar el suelo.</li>
 *   <li><b>Llamarada del Renacimiento</b> (especial): sube, se envuelve en sus
 *   alas y se vuelve un sol; al abrirlas estalla: un anillo de fuego barre el
 *   suelo y una columna de llamas cae bajo el mientras se cierne.</li>
 * </ul>
 */
public class XiuhquetzalEntity extends MiniJefeEntity {

    public static final float VIDA = 3900.0F;
    public static final float DANO_PICOTAZO = 24.0F;
    public static final float DANO_PLUMA = 16.0F;
    public static final float DANO_NOVA = 28.0F;
    public static final float DANO_COLUMNA = 6.0F;

    /**
     * Lo que ha crecido desde que se ajustaron sus ataques (con la escala 1; el 11-10-2026 crecio 4 bloques de alto y
     * ahora mide unos 22 de ala a ala): lo que sale de su cuerpo va por K y las zonas de los ataques por KA, que crece
     * menos para no cambiar tanto la pelea.
     */
    public static final float K = XiuhquetzalGeometria.ESCALA;
    public static final float KA = (float) Math.sqrt(K);

    /**
     * A cuanto del suelo se cierne (bloques, sus garras) y lo deprisa que vuela. Con su tamano, en lo mas bajo de la
     * batida las puntas de las alas bajan unos 3,5 bloques por debajo de las garras: que no rocen el suelo.
     */
    public static final double ALTURA = 2.6 * KA * 1.15;
    public static final double VEL_MAX = 0.5;
    /** El picotazo: el radio del golpe. */
    public static final float PICOTAZO_RADIO = 3.0F * KA;
    /** Las plumas: cuantas por batida, lo que tardan en caer y el radio de cada una. */
    public static final int PLUMAS = 9;
    public static final int PLUMA_VUELA = 14;
    public static final float PLUMA_RADIO = 1.8F * KA;
    /** La Llamarada: lo que sube, el anillo (lo que crece por tick y hasta donde) y el radio de la columna. */
    public static final double LLAMARADA_SUBE = 3.0 * KA;
    public static final float NOVA_CRECE = 1.0F * KA;
    public static final float NOVA_HASTA = 15.0F * KA;
    public static final float COLUMNA_RADIO = 3.6F * KA;

    private final Set<Integer> golpeados = new HashSet<>();
    private Vec3 picadoDesde = Vec3.ZERO;
    private Vec3 picadoHasta = Vec3.ZERO;
    private double rodeo;

    public XiuhquetzalEntity(EntityType<? extends XiuhquetzalEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return atributosBase(12.0D, 0.3D).add(net.minecraft.world.entity.ai.attributes.Attributes.FLYING_SPEED, 0.6D);
    }

    @Override
    protected float vidaEfectiva() {
        return VIDA;
    }

    @Override
    protected int duracion(int estado) {
        return switch (estado) {
            case DESPERTAR -> XiuhquetzalGeometria.DURACION_DESPERTAR;
            case NORMAL -> XiuhquetzalGeometria.DURACION_NORMAL;
            case AREA -> XiuhquetzalGeometria.DURACION_AREA;
            case ESPECIAL -> XiuhquetzalGeometria.DURACION_ESPECIAL;
            default -> 20;
        };
    }

    @Override
    public int duracionMuerte() {
        return XiuhquetzalGeometria.DURACION_MUERTE;
    }

    @Override
    public int disolverDesde() {
        return XiuhquetzalGeometria.DISOLVER_DESDE;
    }

    @Override
    protected float zancada() {
        return XiuhquetzalGeometria.ZANCADA;
    }

    @Override
    protected int pausa(int estado) {
        return estado == ESPECIAL ? 30 : 14;
    }

    // ------------------------------------------------------------------
    //  El vuelo
    // ------------------------------------------------------------------

    /** Hacia un punto, con inercia: la velocidad va hacia la que toca sin pasar de VEL_MAX. */
    private void volarHacia(Vec3 meta, double vmax, double acel) {
        Vec3 quiere = meta.subtract(position());
        double l = quiere.length();
        Vec3 deseada = l < 1.0E-3 ? Vec3.ZERO : quiere.scale(Math.min(vmax, l * 0.18) / l);
        Vec3 v = getDeltaMovement();
        setDeltaMovement(v.add(deseada.subtract(v).scale(acel)));
    }

    /** Se cierne a ALTURA del suelo rodeando a su presa a unos diez bloques; sin presa, sobre su sitio. */
    @Override
    protected void moverse(ServerLevel nivel, @Nullable LivingEntity objetivo, double d) {
        Vec3 c = Vec3.atBottomCenterOf(centro);
        Vec3 meta;
        if (objetivo == null) {
            meta = c;
        } else {
            rodeo += 0.012;
            Vec3 o = objetivo.position();
            meta = o.add(Math.cos(rodeo) * 7.0 * KA, 0, Math.sin(rodeo) * 7.0 * KA);
            Vec3 rel = new Vec3(meta.x - c.x, 0, meta.z - c.z);
            if (rel.length() > CORREA) {
                meta = c.add(rel.normalize().scale(CORREA));
            }
            girarHacia(o, 9.0F);
        }
        double y = suelo(nivel, meta.x, Math.max(getY(), meta.y) + 2.0, meta.z) + ALTURA;
        volarHacia(new Vec3(meta.x, y, meta.z), VEL_MAX, 0.12);
        if (tickCount % XiuhquetzalGeometria.PERIODO_BATIDA == 0) {
            sonido(AtalayaSonidos.XIUHQUETZAL_ALETEO, 2.5F, 0.95F + random.nextFloat() * 0.1F);
        }
    }

    /** Quieto en el aire (frenando) a ALTURA del suelo, o "sube" bloques mas. */
    private void cernerse(ServerLevel nivel, double sube) {
        double y = suelo(nivel, getX(), getY() + 1.0, getZ()) + ALTURA + sube;
        volarHacia(new Vec3(getX(), y, getZ()), 0.25, 0.25);
    }

    @Override
    protected void quieto() {
        getNavigation().stop();
        if (!isNoGravity()) {
            super.quieto();
        }
    }

    @Override
    protected void customServerAiStep(ServerLevel nivel) {
        int e = getEstado();
        // Duerme posado (con su peso) y vuela despierto.
        setNoGravity(!isDeadOrDying() && (e != DORMIDO && !(e == DESPERTAR && t < XiuhquetzalGeometria.DESPERTAR_SE_ALZA)));
        super.customServerAiStep(nivel);
        // Mira a su presa (la cabeza; el cuerpo va a donde vuela).
        LivingEntity presa = getTarget();
        mirarA(presa != null && !isDeadOrDying() ? presa.getEyePosition() : null, XiuhquetzalGeometria.CABEZA);
        if (isDeadOrDying()) {
            return;
        }
        e = getEstado();
        if (e == DESPERTAR && t >= XiuhquetzalGeometria.DESPERTAR_SE_ALZA) {
            // Despega: sube hasta su altura mientras bate las alas.
            float k = Mth.clamp((t - XiuhquetzalGeometria.DESPERTAR_SE_ALZA) / 28.0F, 0.0F, 1.0F);
            double y = suelo(nivel, getX(), getY() + 1.0, getZ()) + ALTURA * k;
            volarHacia(new Vec3(getX(), y, getZ()), 0.2, 0.3);
        }
        if (e == LIBRE && escena > 0) {
            cernerse(nivel, 0.0);
        }
    }

    // ------------------------------------------------------------------
    //  Cuando ataca
    // ------------------------------------------------------------------

    @Override
    protected int elegirAtaque(ServerLevel nivel, LivingEntity objetivo, double d) {
        if (listo(ESPECIAL) && d < 26.0 * KA) {
            enfriar(ESPECIAL, 20 * 24);
            return ESPECIAL;
        }
        if (listo(AREA) && d < 18.0 * KA && random.nextInt(3) != 0) {
            enfriar(AREA, 20 * 9);
            return AREA;
        }
        if (listo(NORMAL) && d < 15.0 * KA) {
            enfriar(NORMAL, 20 * 3);
            return NORMAL;
        }
        return -1;
    }

    @Override
    protected void alIniciar(ServerLevel nivel, int estado, @Nullable LivingEntity objetivo) {
        golpeados.clear();
        if (objetivo != null) {
            Vec3 o = objetivo.position();
            ponerPunto(new Vec3(o.x, suelo(nivel, o.x, o.y + 1.0, o.z), o.z));
        }
        if (estado == ESPECIAL) {
            sonido(AtalayaSonidos.XIUHQUETZAL_CARGA, 5.0F);
        }
    }

    @Override
    protected void tickDespertar(ServerLevel nivel, int t) {
        if (t == 2) {
            sonido(AtalayaSonidos.XIUHQUETZAL_AMBIENTE, 3.0F, 0.8F);
        }
        if (t == XiuhquetzalGeometria.DESPERTAR_SE_ALZA) {
            // Renace: las alas se abren de golpe en una explosion de fuego.
            sonido(AtalayaSonidos.XIUHQUETZAL_DESPERTAR, 6.0F);
            Vec3 p = position().add(0, 1.5 * K, 0);
            particula(nivel, AtalayaParticulas.MJ_ONDA, position().add(0, 0.1, 0), 0.7, 10.0 * KA, 3);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, p, 5.0 * K, 0, 3);
            particulas(nivel, AtalayaParticulas.MJ_LLAMA, p, 50, 2.5 * K, 1.2 * K, 2.5 * K, 0.12);
            particulas(nivel, AtalayaParticulas.MJ_BRASA, p, 60, 3.0 * K, 2.0 * K, 3.0 * K, 0.2);
            particulas(nivel, AtalayaParticulas.MJ_PLUMA_FUEGO, p.add(0, 1 * K, 0), 18, 3.0 * K, 1.0 * K, 3.0 * K, 0.08);
        }
        if (t > XiuhquetzalGeometria.DESPERTAR_SE_ALZA && (t - XiuhquetzalGeometria.DESPERTAR_SE_ALZA) % 15 == 5
                && t < XiuhquetzalGeometria.DESPERTAR_RUGE) {
            sonido(AtalayaSonidos.XIUHQUETZAL_ALETEO, 3.5F);
        }
        if (t == XiuhquetzalGeometria.DESPERTAR_RUGE) {
            sonido(AtalayaSonidos.XIUHQUETZAL_CHILLIDO, 6.5F);
            particulas(nivel, AtalayaParticulas.MJ_BRASA, puntoMundo(XiuhquetzalGeometria.CABEZA), 30, 1.0, 1.0, 1.0, 0.2);
        }
    }

    // ------------------------------------------------------------------
    //  Los ataques
    // ------------------------------------------------------------------

    @Override
    protected void tickAtaque(ServerLevel nivel, int estado, int t, @Nullable LivingEntity objetivo) {
        switch (estado) {
            case NORMAL -> picotazo(nivel, t, objetivo);
            case AREA -> plumas(nivel, t);
            case ESPECIAL -> llamarada(nivel, t);
            default -> {
            }
        }
    }

    /** Picotazo de Llamas: el picado hasta su presa (el pico llega a ella en NORMAL_GOLPE) y el remonte. */
    private void picotazo(ServerLevel nivel, int t, @Nullable LivingEntity objetivo) {
        int carga = XiuhquetzalGeometria.NORMAL_CARGA;
        int golpe = XiuhquetzalGeometria.NORMAL_GOLPE;
        if (t < carga) {
            if (objetivo != null) {
                girarHacia(objetivo.position(), 15.0F);
                ponerRumbo(getYRot());
            }
            cernerse(nivel, 1.0);
        }
        if (t == carga) {
            sonido(AtalayaSonidos.XIUHQUETZAL_PICADO, 4.5F);
            Vec3 p = objetivo != null ? objetivo.position().add(0, 1.4, 0) : getPunto().add(0, 1.4, 0);
            // La entidad va a donde el pico llega a su presa (a la altura de la cabeza).
            Vec3 pico = MiniJefeEntity.puntoMundo(XiuhquetzalGeometria.PICO_GOLPE, Vec3.ZERO, getYRot());
            picadoDesde = position();
            picadoHasta = p.subtract(pico);
            // Nunca por debajo del suelo: el pico del picado va casi a la altura de sus garras, asi que llega igual.
            double suelo = suelo(nivel, picadoHasta.x, p.y + 1.0, picadoHasta.z);
            if (picadoHasta.y < suelo + 0.2) {
                picadoHasta = new Vec3(picadoHasta.x, suelo + 0.2, picadoHasta.z);
            }
            ponerPunto(p);
        }
        if (t > carga && t <= golpe) {
            float k = (t - carga) / (float) (golpe - carga);
            Vec3 a = picadoDesde.lerp(picadoHasta, k * k);
            setDeltaMovement(a.subtract(position()));
            if (t % 1 == 0) {
                particulas(nivel, AtalayaParticulas.MJ_LLAMA, position().add(0, 1.5 * K, 0), 4, 0.6 * K, 0.6 * K, 0.6 * K, 0.04);
            }
        }
        if (t == golpe) {
            Vec3 p = getPunto();
            sonido(AtalayaSonidos.XIUHQUETZAL_PICOTAZO, 6.0F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, new Vec3(p.x, suelo(nivel, p.x, p.y + 1, p.z) + 0.1, p.z), 0.8, 6.0 * KA, 3);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, p, 3.2 * KA, 0, 3);
            particulas(nivel, AtalayaParticulas.MJ_LLAMA, p, 40, 1.5 * KA, 0.8, 1.5 * KA, 0.12);
            particulas(nivel, AtalayaParticulas.MJ_BRASA, p, 40, 1.5, 1.0, 1.5, 0.3);
            for (LivingEntity v : presasCerca(nivel, p, PICOTAZO_RADIO, 3.5)) {
                if (golpear(nivel, v, MiniJefeDanos.XIUHQUETZAL_PICOTAZO, DANO_PICOTAZO, p, 1.0, 0.55)) {
                    v.igniteForTicks(80);
                }
            }
        }
        if (t > golpe) {
            // Remonta batiendo fuerte.
            cernerse(nivel, 0.5);
            if ((t - golpe) % 8 == 2) {
                sonido(AtalayaSonidos.XIUHQUETZAL_ALETEO, 3.5F, 1.1F);
            }
        }
    }

    /**
     * Donde cae cada pluma de una batida: en un anillo alrededor del punto del
     * ataque, mas ancho en cada batida y girado (el cliente las pinta igual).
     */
    public static Vec3 caidaPluma(Vec3 punto, int batida, int i) {
        double r = (1.6 + batida * 2.6) * KA;
        double a = Mth.TWO_PI * i / PLUMAS + batida * 0.55;
        return punto.add(Math.cos(a) * r, 0, Math.sin(a) * r);
    }

    private void plumas(ServerLevel nivel, int t) {
        cernerse(nivel, 1.5);
        int[] batidas = {XiuhquetzalGeometria.AREA_BATIDA_1, XiuhquetzalGeometria.AREA_BATIDA_2, XiuhquetzalGeometria.AREA_BATIDA_3};
        for (int b = 0; b < batidas.length; b++) {
            if (t == batidas[b] - 3) {
                sonido(AtalayaSonidos.XIUHQUETZAL_ALETEO, 4.5F, 0.85F);
            }
            if (t == batidas[b]) {
                sonido(AtalayaSonidos.XIUHQUETZAL_PLUMA, 5.0F, 1.0F + b * 0.06F);
                particulas(nivel, AtalayaParticulas.MJ_BRASA, position().add(0, 2 * K, 0), 20, 3.0 * K, 0.5 * K, 3.0 * K, 0.2);
                Vec3 punto = getPunto();
                final int batida = b;
                for (int i = 0; i < PLUMAS; i++) {
                    Vec3 s = caidaPluma(punto, batida, i);
                    Vec3 suelo = new Vec3(s.x, suelo(nivel, s.x, punto.y + 3.0, s.z) + 0.05, s.z);
                    programar(PLUMA_VUELA, nv -> {
                        particulas(nv, AtalayaParticulas.MJ_LLAMA, suelo.add(0, 0.3, 0), 8, 0.5, 0.3, 0.5, 0.05);
                        particulas(nv, AtalayaParticulas.MJ_BRASA, suelo.add(0, 0.3, 0), 8, 0.5, 0.4, 0.5, 0.15);
                        particula(nv, AtalayaParticulas.MJ_ONDA, suelo, 0.15, 2.2, 3);
                        for (LivingEntity v : presasCerca(nv, suelo, PLUMA_RADIO, 3.0)) {
                            if (golpear(nv, v, MiniJefeDanos.XIUHQUETZAL_PLUMAS, DANO_PLUMA, suelo, 0.45, 0.35)) {
                                v.igniteForTicks(60);
                            }
                        }
                    });
                }
                programar(PLUMA_VUELA, nv -> nv.playSound(null, punto.x, punto.y, punto.z, AtalayaSonidos.XIUHQUETZAL_PLUMA_GOLPE,
                        SoundSource.HOSTILE, 4.0F, 0.9F + batida * 0.08F));
            }
        }
    }

    private void llamarada(ServerLevel nivel, int t) {
        int estalla = XiuhquetzalGeometria.ESPECIAL_ESTALLA;
        int fin = XiuhquetzalGeometria.ESPECIAL_FIN;
        cernerse(nivel, t < fin ? LLAMARADA_SUBE * Mth.clamp(t / 24.0, 0, 1) : LLAMARADA_SUBE * (1 - Mth.clamp((t - fin) / 20.0, 0, 1)));
        if (t > XiuhquetzalGeometria.ESPECIAL_ENVUELVE && t < estalla && t % 2 == 0) {
            // Las brasas acuden a el en espiral: se esta volviendo un sol.
            double a = t * 0.7;
            Vec3 c = position().add(0, 2.0 * K, 0);
            Vec3 p = c.add(Math.cos(a) * 5 * K, Math.sin(a * 0.5) * 2 * K, Math.sin(a) * 5 * K);
            Vec3 v = c.subtract(p).scale(0.1);
            nivel.sendParticles(AtalayaParticulas.MJ_BRASA, true, true, p.x, p.y, p.z, 0, v.x, v.y, v.z, 1.0);
        }
        Vec3 g = new Vec3(getX(), suelo(nivel, getX(), getY() + 1.0, getZ()), getZ());
        if (t == estalla) {
            sonido(AtalayaSonidos.XIUHQUETZAL_NOVA, 7.0F);
            sonido(AtalayaSonidos.XIUHQUETZAL_CHILLIDO, 6.0F, 1.1F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, g.add(0, 0.1, 0), 1.3, NOVA_HASTA, 3);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, position().add(0, 2.0 * K, 0), 7.0 * K, 0, 3);
            particulas(nivel, AtalayaParticulas.MJ_LLAMA, position().add(0, 2 * K, 0), 80, 4.0 * K, 2.0 * K, 4.0 * K, 0.2);
            particulas(nivel, AtalayaParticulas.MJ_PLUMA_FUEGO, position().add(0, 2 * K, 0), 30, 5.0 * K, 2.0 * K, 5.0 * K, 0.1);
        }
        int k = t - estalla;
        if (k >= 0) {
            float r = 1.0F + k * NOVA_CRECE;
            if (r <= NOVA_HASTA + 1.0F) {
                for (LivingEntity v : presasCerca(nivel, g, r + 1.0, 4.0)) {
                    double d = horizontal(g, v.position());
                    if (d > r - NOVA_CRECE - 1.0 && !golpeados.contains(v.getId())) {
                        golpeados.add(v.getId());
                        if (golpear(nivel, v, MiniJefeDanos.XIUHQUETZAL_LLAMARADA, DANO_NOVA, g, 1.4, 0.6)) {
                            v.igniteForTicks(120);
                        }
                    }
                }
            }
            if (t < fin && t % 6 == 0) {
                for (LivingEntity v : presasCerca(nivel, g, COLUMNA_RADIO, 6.0)) {
                    if (golpear(nivel, v, MiniJefeDanos.XIUHQUETZAL_LLAMARADA, DANO_COLUMNA, g, 0.0, 0.0)) {
                        v.igniteForTicks(60);
                    }
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
        // Brasas que se le desprenden siempre, y mas al batir.
        int cada = estado == DORMIDO ? 6 : 2;
        if (tickCount % cada == 0) {
            l.addParticle(AtalayaParticulas.MJ_BRASA, getX() + (random.nextDouble() - 0.5) * 2.0 * K,
                    getY() + (1.0 + random.nextDouble() * 2.0) * K, getZ() + (random.nextDouble() - 0.5) * 2.0 * K,
                    (random.nextDouble() - 0.5) * 0.04, 0.04, (random.nextDouble() - 0.5) * 0.04);
        }
        if (estado != DORMIDO && tickCount % 5 == 0) {
            for (Vec3 ala : new Vec3[]{XiuhquetzalGeometria.ALA_IZQ, XiuhquetzalGeometria.ALA_DER}) {
                Vec3 p = puntoMundo(ala);
                l.addParticle(AtalayaParticulas.MJ_LLAMA, p.x, p.y, p.z, 0, 0.02, 0);
            }
        }
        if (estado != DORMIDO && tickCount % 13 == 0) {
            l.addParticle(AtalayaParticulas.MJ_PLUMA_FUEGO, getX() + (random.nextDouble() - 0.5) * 3 * K, getY() + 1.5 * K,
                    getZ() + (random.nextDouble() - 0.5) * 3 * K, 0, -0.02, 0);
        }
        if (estado == ESPECIAL && tiempo > XiuhquetzalGeometria.ESPECIAL_ESTALLA && tiempo < XiuhquetzalGeometria.ESPECIAL_FIN) {
            // La columna de fuego que cae bajo el.
            for (int i = 0; i < 5; i++) {
                double a = random.nextDouble() * Mth.TWO_PI;
                double r = random.nextDouble() * COLUMNA_RADIO;
                l.addParticle(AtalayaParticulas.MJ_LLAMA, getX() + Math.cos(a) * r, getY() + random.nextDouble() * 2.5 * K,
                        getZ() + Math.sin(a) * r, 0, -0.25, 0);
            }
        }
    }

    @Override
    protected void efectosMuerte(int tiempo) {
        if (tiempo % 2 == 0) {
            for (int i = 0; i < (tiempo > disolverDesde() ? 4 : 1); i++) {
                level().addParticle(i % 2 == 0 ? AtalayaParticulas.MJ_BRASA : AtalayaParticulas.MJ_CENIZA,
                        getX() + (random.nextDouble() - 0.5) * 4.0 * K, getY() + random.nextDouble() * 2.0 * K,
                        getZ() + (random.nextDouble() - 0.5) * 4.0 * K, 0, 0.05, 0);
            }
        }
    }

    @Override
    protected void tickMuerte(ServerLevel nivel, int tiempo) {
        setNoGravity(false);
        if (tiempo == XiuhquetzalGeometria.MUERTE_SUELO) {
            sonido(AtalayaSonidos.XIUHQUETZAL_PICOTAZO, 4.0F, 0.6F);
            particulas(nivel, AtalayaParticulas.MJ_LLAMA, position().add(0, 0.5, 0), 30, 2.0 * K, 0.4, 2.0 * K, 0.06);
            particulas(nivel, AtalayaParticulas.MJ_CENIZA, position().add(0, 1 * K, 0), 30, 2.0 * K, 0.6 * K, 2.0 * K, 0.03);
        }
        if (tiempo == duracionMuerte() - 1) {
            particulas(nivel, AtalayaParticulas.MJ_BRASA, position().add(0, 1.0 * K, 0), 60, 2.0 * K, 1.0 * K, 2.0 * K, 0.2);
            particulas(nivel, AtalayaParticulas.MJ_CENIZA, position().add(0, 1.0 * K, 0), 40, 2.0 * K, 1.0 * K, 2.0 * K, 0.05);
        }
    }

    // ------------------------------------------------------------------
    //  Sonidos de vanilla
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        return getEstado() == DORMIDO ? null : AtalayaSonidos.XIUHQUETZAL_AMBIENTE;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 160;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.XIUHQUETZAL_HERIDO;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return AtalayaSonidos.XIUHQUETZAL_MUERTE;
    }

    @Override
    protected float getSoundVolume() {
        return 3.0F;
    }

    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState bloque) {
    }

    @Override
    protected @Nullable SoundEvent sonidoInmune() {
        return AtalayaSonidos.XIUHQUETZAL_INMUNE;
    }

    @Override
    protected ParticleOptions particulaInmune() {
        return AtalayaParticulas.MJ_BRASA;
    }

    @Override
    public boolean isOnFire() {
        return false;
    }
}
