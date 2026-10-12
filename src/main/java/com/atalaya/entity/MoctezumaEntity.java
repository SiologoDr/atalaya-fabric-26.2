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
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Moctezuma, el Guerrero Aguila de Jade: el mini jefe de la tierra. Un guerrero
 * aguila de cinco bloques y medio con el chimalli en la izquierda y el
 * macuahuitl de jade con dientes de obsidiana en la derecha.
 *
 * <ul>
 *   <li><b>Corte de Obsidiana</b> (normal): un barrido de derecha a izquierda que
 *   barre todo lo que tiene delante y, con un paso al frente, un tajo de arriba
 *   abajo que raja el suelo en linea recta.</li>
 *   <li><b>Terremoto del Aguila</b> (area): salta tres bloques y medio y cae con
 *   el escudo y el arma contra el suelo; la onda se abre en tres coronas de
 *   pinchos de jade que brotan una tras otra.</li>
 *   <li><b>Tormenta de Obsidiana y Jade</b> (especial): alza el macuahuitl al
 *   cielo y lo hace girar; un remolino de esquirlas se forma sobre el y llueven
 *   tres tandas de fragmentos sobre cada jugador (el glifo de jade marca donde
 *   van a caer) y, al final, clava el arma: la tierra revienta en pilares de
 *   jade a su alrededor.</li>
 * </ul>
 */
public class MoctezumaEntity extends MiniJefeEntity {

    public static final float VIDA = 4200.0F;
    // Contra netherita P4 y manzana de Notch: unos 5 corazones el golpe fuerte, 4 el de area (como un jefe en su fase II).
    public static final float DANO_CORTE = 22.0F;
    public static final float DANO_TAJO = 25.0F;
    public static final float DANO_ONDA = 20.0F;
    public static final float DANO_PINCHOS = 18.0F;
    public static final float DANO_FRAGMENTO = 18.0F;
    public static final float DANO_ERUPCION = 26.0F;

    /**
     * Lo que ha crecido desde que se ajustaron sus ataques (con la escala 1,375; el 11-10-2026 crecio 4 bloques de
     * alto): lo que sale de su cuerpo (el alcance, las alturas, el remolino de encima) va por K y las zonas de los
     * ataques por KA, que crece menos para no cambiar tanto la pelea.
     */
    public static final float K = MoctezumaGeometria.ESCALA / 1.375F;
    public static final float KA = (float) Math.sqrt(K);

    /** Los radios de las tres coronas de pinchos del Terremoto, y cuando brota cada una (ticks tras la caida). */
    public static final float[] CORONAS = {5.5F * KA, 9.0F * KA, 12.5F * KA};
    public static final int[] CORONAS_TICK = {4, 9, 14};
    /** El radio de la onda del golpe y el ancho de cada corona. */
    public static final float ONDA_RADIO = 4.5F * KA;
    public static final float CORONA_ANCHO = 1.3F * KA;
    /** Lo que tarda un fragmento en caer desde que sale su glifo, y el radio de su golpe. */
    public static final int FRAGMENTO_CAE = 16;
    public static final float FRAGMENTO_RADIO = 2.6F;
    /** La erupcion del final de la Tormenta: hasta donde llega. */
    public static final float ERUPCION_RADIO = 7.5F * KA;

    private final Set<Integer> golpeados = new HashSet<>();

    public MoctezumaEntity(EntityType<? extends MoctezumaEntity> tipo, Level nivel) {
        super(tipo, nivel);
    }

    public static AttributeSupplier.Builder crearAtributos() {
        return atributosBase(16.0D, 0.27D);
    }

    @Override
    protected float vidaEfectiva() {
        return VIDA;
    }

    @Override
    protected int duracion(int estado) {
        return switch (estado) {
            case DESPERTAR -> MoctezumaGeometria.DURACION_DESPERTAR;
            case NORMAL -> MoctezumaGeometria.DURACION_NORMAL;
            case AREA -> MoctezumaGeometria.DURACION_AREA;
            case ESPECIAL -> MoctezumaGeometria.DURACION_ESPECIAL;
            default -> 20;
        };
    }

    @Override
    public int duracionMuerte() {
        return MoctezumaGeometria.DURACION_MUERTE;
    }

    @Override
    public int disolverDesde() {
        return MoctezumaGeometria.DISOLVER_DESDE;
    }

    @Override
    protected float zancada() {
        return MoctezumaGeometria.ZANCADA;
    }

    /**
     * Se planta a unos 5 bloques (antes casi 6): es un guerrero cuerpo a cuerpo y tiene que echarse encima
     * (revision del 11-10-2026, Juan: "haz todas las mejoras").
     */
    @Override
    protected double alcance() {
        return 2.9 * K;
    }

    @Override
    protected int pausa(int estado) {
        return estado == ESPECIAL ? 30 : estado == AREA ? 22 : 12;
    }

    // ------------------------------------------------------------------
    //  Cuando ataca
    // ------------------------------------------------------------------

    @Override
    protected int elegirAtaque(ServerLevel nivel, LivingEntity objetivo, double d) {
        if (listo(ESPECIAL) && d < 28.0) {
            enfriar(ESPECIAL, 20 * 24);
            enfriar(AREA, Math.max(enfriamiento[AREA - NORMAL], 60));
            return ESPECIAL;
        }
        int cerca = presasCerca(nivel, position(), 8.0 * KA, 4.0 * K).size();
        if (listo(AREA) && d < 9.0 * KA && (cerca >= 2 || d > 5.5 * K || random.nextInt(3) == 0)) {
            enfriar(AREA, 20 * 9);
            return AREA;
        }
        if (listo(NORMAL) && d < 5.2 * K) {
            enfriar(NORMAL, 20 * 2);
            return NORMAL;
        }
        return -1;
    }

    @Override
    protected void alIniciar(ServerLevel nivel, int estado, @Nullable LivingEntity objetivo) {
        golpeados.clear();
        if (estado == ESPECIAL) {
            sonido(AtalayaSonidos.MOCTEZUMA_TORMENTA, 5.0F);
        }
    }

    @Override
    protected void tickDespertar(ServerLevel nivel, int t) {
        if (t == 2) {
            sonido(AtalayaSonidos.MOCTEZUMA_DESPERTAR, 5.0F);
        }
        if (t == MoctezumaGeometria.DESPERTAR_ARRANCA) {
            sonido(AtalayaSonidos.MOCTEZUMA_ARRANCA, 4.0F);
            Vec3 p = puntoMundo(new Vec3(-0.7, 0.2, 2.4).scale(K));
            particulas(nivel, AtalayaParticulas.MJ_POLVO, p, 14, 0.6 * K, 0.2 * K, 0.6 * K, 0.04);
            particulas(nivel, AtalayaParticulas.MJ_OBSIDIANA, p, 12, 0.4 * K, 0.3 * K, 0.4 * K, 0.25);
        }
        if (t == MoctezumaGeometria.DESPERTAR_CHOQUE_1 || t == MoctezumaGeometria.DESPERTAR_CHOQUE_2) {
            sonido(AtalayaSonidos.MOCTEZUMA_CHOQUE, 4.0F, t == MoctezumaGeometria.DESPERTAR_CHOQUE_1 ? 0.95F : 1.05F);
            Vec3 p = puntoMundo(new Vec3(0.6, 3.3, 1.6).scale(K));
            particulas(nivel, AtalayaParticulas.MJ_JADE, p, 10, 0.3, 0.3, 0.3, 0.25);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, p, 1.6, 0, 0);
        }
        if (t == MoctezumaGeometria.DESPERTAR_RUGE) {
            sonido(AtalayaSonidos.MOCTEZUMA_GRITO, 6.0F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, position().add(0, 0.1, 0), 0.5, 9.0 * KA, 0);
            particulas(nivel, AtalayaParticulas.MJ_PLUMA, puntoMundo(MoctezumaGeometria.CABEZA).add(0, 1.0 * K, 0), 24, 1.6 * K, 0.8 * K,
                    1.6 * K, 0.06);
        }
    }

    // ------------------------------------------------------------------
    //  Los ataques
    // ------------------------------------------------------------------

    @Override
    protected void tickAtaque(ServerLevel nivel, int estado, int t, @Nullable LivingEntity objetivo) {
        switch (estado) {
            case NORMAL -> corte(nivel, t, objetivo);
            case AREA -> terremoto(nivel, t);
            case ESPECIAL -> tormenta(nivel, t);
            default -> {
            }
        }
    }

    /** Corte de Obsidiana: el barrido (golpe 1, en arco por delante) y el tajo (golpe 2, en linea). */
    private void corte(ServerLevel nivel, int t, @Nullable LivingEntity objetivo) {
        if (t <= MoctezumaGeometria.NORMAL_CARGA && objetivo != null) {
            girarHacia(objetivo.position(), 14.0F);
        }
        if (t == MoctezumaGeometria.NORMAL_CARGA) {
            sonido(AtalayaSonidos.MOCTEZUMA_CORTE, 3.5F, 0.95F);
        }
        if (t == MoctezumaGeometria.NORMAL_GOLPE_1) {
            // El barrido: todo lo que tiene delante a su alcance (5,8 bloques antes de crecer, unos 10 ahora), en 150
            // grados.
            Vec3 c = position();
            boolean dio = false;
            for (LivingEntity v : presasCerca(nivel, c, 5.8 * K, 3.5 * K)) {
                if (Math.abs(anguloHacia(c, getYRot(), v.position())) < 75.0F) {
                    // Lo empuja hacia su izquierda (el barrido va de derecha a izquierda).
                    Vec3 izq = puntoMundo(new Vec3(1, 0, 0)).subtract(position());
                    if (golpear(nivel, v, MiniJefeDanos.MOCTEZUMA_CORTE, DANO_CORTE, v.position().subtract(izq), 0.7, 0.3)) {
                        dio = true;
                    }
                }
            }
            Vec3 p = puntoMundo(MoctezumaGeometria.ARMA_BARRIDO);
            particulas(nivel, AtalayaParticulas.MJ_OBSIDIANA, p, 14, 1.2 * K, 0.3 * K, 1.2 * K, 0.3);
            particulas(nivel, AtalayaParticulas.MJ_JADE, p, 10, 1.0 * K, 0.3 * K, 1.0 * K, 0.3);
            sonido(dio ? AtalayaSonidos.MOCTEZUMA_CORTE_GOLPE : AtalayaSonidos.MOCTEZUMA_CORTE, 3.0F, dio ? 1.0F : 1.15F);
        }
        if (t == MoctezumaGeometria.NORMAL_GOLPE_2 - 4) {
            sonido(AtalayaSonidos.MOCTEZUMA_CORTE, 3.5F, 0.8F);
        }
        if (t == MoctezumaGeometria.NORMAL_GOLPE_2) {
            // El tajo: raja el suelo en linea recta por delante (siete bloques antes de crecer, unos doce ahora).
            Vec3 f = frente();
            Vec3 o = position();
            int largo = Math.round(7 * K);
            for (LivingEntity v : presasCerca(nivel, o.add(f.scale(largo * 0.5)), largo * 0.5 + 1.5, 3.0 * K)) {
                Vec3 rel = v.position().subtract(o);
                double a = rel.x * f.x + rel.z * f.z;
                double lado = Math.abs(rel.x * f.z - rel.z * f.x);
                if (a > -0.5 && a < largo + 0.5 && lado < 1.8 * KA) {
                    golpear(nivel, v, MiniJefeDanos.MOCTEZUMA_CORTE, DANO_TAJO, o, 0.4, 0.55);
                }
            }
            for (int i = 1; i <= largo; i++) {
                Vec3 p = o.add(f.scale(i * 1.05));
                p = new Vec3(p.x, suelo(nivel, p.x, getY() + 1.5, p.z) + 0.06, p.z);
                particula(nivel, AtalayaParticulas.MJ_GRIETA, p, 0.9, 40 + i * 2, getYRot() * Mth.DEG_TO_RAD + i);
                particulas(nivel, AtalayaParticulas.MJ_POLVO, p, 2, 0.3, 0.1, 0.3, 0.03);
                particulas(nivel, AtalayaParticulas.MJ_OBSIDIANA, p, 2, 0.2, 0.1, 0.2, 0.22);
            }
            Vec3 g = puntoMundo(MoctezumaGeometria.ARMA_TAJO);
            particula(nivel, AtalayaParticulas.MJ_ONDA, new Vec3(g.x, getY() + 0.1, g.z), 0.35, 3.0 * KA, 0);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, g, 2.0, 0, 0);
            sonido(AtalayaSonidos.MOCTEZUMA_CORTE_GOLPE, 4.0F, 0.8F);
        }
    }

    /** Terremoto del Aguila: el salto, la caida (la onda) y las tres coronas de pinchos de jade. */
    private void terremoto(ServerLevel nivel, int t) {
        Vec3 c = centroTerremoto();
        if (t == MoctezumaGeometria.AREA_DESPEGA) {
            sonido(AtalayaSonidos.MOCTEZUMA_SALTO, 3.5F);
            particulas(nivel, AtalayaParticulas.MJ_POLVO, position(), 18, 1.2 * K, 0.1, 1.2 * K, 0.05);
        }
        if (t == MoctezumaGeometria.AREA_CAE) {
            // Cae del cielo: un golpe que se oye lejos y sacude la camara de quien este cerca (la onda la sacude,
            // con la fuerza de los golpes grandes de los jefes), y un segundo temblor que rueda tras el.
            sonido(AtalayaSonidos.MOCTEZUMA_TERREMOTO, 9.0F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, c.add(0, 0.1, 0), 2.8, 14.0 * KA, 0);
            programar(5, nv -> particula(nv, AtalayaParticulas.MJ_ONDA, c.add(0, 0.12, 0), 1.2, 20.0 * KA, 0));
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, c.add(0, 0.6 * K, 0), 3.0 * K, 0, 0);
            particulas(nivel, AtalayaParticulas.MJ_POLVO, c, 40, 3.0 * KA, 0.3, 3.0 * KA, 0.08);
            particulas(nivel, AtalayaParticulas.MJ_OBSIDIANA, c, 26, 1.5 * KA, 0.3, 1.5 * KA, 0.45);
            particulas(nivel, AtalayaParticulas.MJ_JADE, c, 20, 1.5 * KA, 0.3, 1.5 * KA, 0.4);
            for (LivingEntity v : presasCerca(nivel, c, ONDA_RADIO, 3.0)) {
                golpeados.add(v.getId());
                golpear(nivel, v, MiniJefeDanos.MOCTEZUMA_TERREMOTO, DANO_ONDA, c, 0.9, 0.75);
            }
        }
        for (int i = 0; i < CORONAS.length; i++) {
            if (t == MoctezumaGeometria.AREA_CAE + CORONAS_TICK[i]) {
                corona(nivel, c, CORONAS[i], i);
            }
        }
    }

    /** Una corona de pinchos de jade a "radio" del golpe: le da a quien este en su anillo (y no le dio otra). */
    private void corona(ServerLevel nivel, Vec3 c, float radio, int i) {
        sonido(AtalayaSonidos.MOCTEZUMA_PINCHOS, 4.5F, 1.1F - i * 0.1F);
        int n = Math.round(radio * 3.0F);
        for (int k = 0; k < n; k++) {
            double a = Mth.TWO_PI * k / n + i * 0.4;
            Vec3 p = c.add(Math.cos(a) * radio, 0, Math.sin(a) * radio);
            p = new Vec3(p.x, suelo(nivel, p.x, c.y + 2.0, p.z), p.z);
            particulas(nivel, AtalayaParticulas.MJ_JADE, p.add(0, 0.6, 0), 2, 0.2, 0.4, 0.2, 0.2);
            if (k % 2 == 0) {
                particulas(nivel, AtalayaParticulas.MJ_POLVO, p, 1, 0.3, 0.1, 0.3, 0.03);
            }
        }
        for (LivingEntity v : presasCerca(nivel, c, radio + CORONA_ANCHO, 3.5)) {
            double d = horizontal(c, v.position());
            if (d > radio - CORONA_ANCHO && !golpeados.contains(v.getId())) {
                golpeados.add(v.getId());
                golpear(nivel, v, MiniJefeDanos.MOCTEZUMA_TERREMOTO, DANO_PINCHOS, c, 0.5, 0.95);
            }
        }
    }

    /** Donde cae el Terremoto (el escudo contra el suelo), en el mundo. */
    public Vec3 centroTerremoto() {
        Vec3 g = MiniJefeEntity.puntoMundo(MoctezumaGeometria.GOLPE_AREA, position(), getRumbo());
        return new Vec3(g.x, getY(), g.z);
    }

    /** Tormenta de Obsidiana y Jade: las tres lluvias de fragmentos y la erupcion final. */
    private void tormenta(ServerLevel nivel, int t) {
        if (t == MoctezumaGeometria.ESPECIAL_ALZA) {
            Vec3 p = puntoMundo(MoctezumaGeometria.PUNTA_ALZADA);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, p, 2.4 * K, 0, 0);
        }
        if (t > MoctezumaGeometria.ESPECIAL_ALZA && t < MoctezumaGeometria.ESPECIAL_CLAVA && t % 3 == 0) {
            // Las esquirlas suben en espiral hacia el remolino de encima.
            double a = t * 0.5;
            Vec3 p = position().add(Math.cos(a) * 2.5 * K, 1.0 * K, Math.sin(a) * 2.5 * K);
            particulas(nivel, AtalayaParticulas.MJ_OBSIDIANA, p, 2, 0.3, 0.3, 0.3, 0.05);
        }
        if (t == MoctezumaGeometria.ESPECIAL_LLUVIA_1 || t == MoctezumaGeometria.ESPECIAL_LLUVIA_2
                || t == MoctezumaGeometria.ESPECIAL_LLUVIA_3) {
            lluvia(nivel, t == MoctezumaGeometria.ESPECIAL_LLUVIA_3 ? 2 : 1);
        }
        if (t == MoctezumaGeometria.ESPECIAL_CLAVA) {
            Vec3 c = MiniJefeEntity.puntoMundo(MoctezumaGeometria.CLAVA, position(), getRumbo());
            c = new Vec3(c.x, getY(), c.z);
            sonido(AtalayaSonidos.MOCTEZUMA_ERUPCION, 6.5F);
            particula(nivel, AtalayaParticulas.MJ_ONDA, c.add(0, 0.1, 0), 1.2, 18.0 * KA, 0);
            particula(nivel, AtalayaParticulas.MJ_DESTELLO, c.add(0, 1.0 * K, 0), 4.0 * K, 0, 0);
            particulas(nivel, AtalayaParticulas.MJ_JADE, c, 60, 3.5 * KA, 1.0 * K, 3.5 * KA, 0.5);
            particulas(nivel, AtalayaParticulas.MJ_OBSIDIANA, c, 40, 3.0 * KA, 0.5 * K, 3.0 * KA, 0.5);
            particulas(nivel, AtalayaParticulas.MJ_POLVO, c, 50, 4.0 * KA, 0.4, 4.0 * KA, 0.08);
            for (LivingEntity v : presasCerca(nivel, position(), ERUPCION_RADIO, 4.0)) {
                golpear(nivel, v, MiniJefeDanos.MOCTEZUMA_TORMENTA, DANO_ERUPCION, position(), 1.0, 1.05);
            }
        }
    }

    /** Una tanda de fragmentos: uno (o mas) por jugador cerca, donde va a estar; el glifo avisa y luego cae. */
    private void lluvia(ServerLevel nivel, int porJugador) {
        sonido(AtalayaSonidos.MOCTEZUMA_FRAGMENTO, 5.0F);
        List<Player> js = jugadores(nivel, 30.0);
        int n = 0;
        for (Player p : js) {
            if (!esPresa(p)) {
                continue;
            }
            for (int k = 0; k < porJugador && n < 16; k++, n++) {
                Vec3 lleva = p.getDeltaMovement().multiply(1, 0, 1).scale(FRAGMENTO_CAE * 0.6);
                Vec3 q = p.position().add(lleva).add((random.nextDouble() - 0.5) * 2.4 * k, 0, (random.nextDouble() - 0.5) * 2.4 * k);
                caerFragmento(nivel, q);
            }
        }
        // Y algunos sueltos alrededor de el, para que la plaza entera tiemble.
        for (int k = 0; k < 4; k++) {
            double a = random.nextDouble() * Mth.TWO_PI;
            double r = (5 + random.nextDouble() * 10) * KA;
            caerFragmento(nivel, position().add(Math.cos(a) * r, 0, Math.sin(a) * r));
        }
    }

    private void caerFragmento(ServerLevel nivel, Vec3 donde) {
        Vec3 s = new Vec3(donde.x, suelo(nivel, donde.x, donde.y + 3.0, donde.z) + 0.05, donde.z);
        particula(nivel, AtalayaParticulas.MJ_MARCA, s, FRAGMENTO_RADIO, FRAGMENTO_CAE + 6, 0);
        // El fragmento sale de lo alto 12 ticks antes de llegar.
        programar(FRAGMENTO_CAE - 12, nv -> particula(nv, AtalayaParticulas.MJ_FRAGMENTO, s.add(0, 13.8, 0), 0, -1.15, 0));
        programar(FRAGMENTO_CAE, nv -> {
            nv.playSound(null, s.x, s.y, s.z, AtalayaSonidos.MOCTEZUMA_FRAGMENTO_GOLPE, SoundSource.HOSTILE, 3.0F,
                    0.9F + random.nextFloat() * 0.25F);
            particula(nv, AtalayaParticulas.MJ_ONDA, s.add(0, 0.05, 0), 0.25, 3.0, 0);
            particulas(nv, AtalayaParticulas.MJ_OBSIDIANA, s.add(0, 0.3, 0), 12, 0.6, 0.3, 0.6, 0.35);
            particulas(nv, AtalayaParticulas.MJ_JADE, s.add(0, 0.3, 0), 8, 0.6, 0.3, 0.6, 0.3);
            particulas(nv, AtalayaParticulas.MJ_POLVO, s, 6, 0.6, 0.1, 0.6, 0.04);
            for (LivingEntity v : presasCerca(nv, s, FRAGMENTO_RADIO, 3.0)) {
                golpear(nv, v, MiniJefeDanos.MOCTEZUMA_TORMENTA, DANO_FRAGMENTO, s, 0.4, 0.45);
            }
        });
    }

    // ------------------------------------------------------------------
    //  Lo que ve el cliente
    // ------------------------------------------------------------------

    @Override
    protected void efectosCliente(int estado, int tiempo) {
        Level l = level();
        switch (estado) {
            case DORMIDO -> {
                // Unas motas de jade suben de la gema mientras duerme.
                if (tickCount % 9 == 0) {
                    Vec3 p = puntoMundo(new Vec3(0, 1.8, 0.9).scale(K));
                    l.addParticle(AtalayaParticulas.MJ_JADE, p.x + (random.nextDouble() - 0.5), p.y, p.z + (random.nextDouble() - 0.5),
                            0, 0.06, 0);
                }
            }
            case DESPERTAR -> {
                if (tiempo > MoctezumaGeometria.DESPERTAR_ABRE && tiempo < MoctezumaGeometria.DESPERTAR_SE_ALZA && tickCount % 3 == 0) {
                    Vec3 p = puntoMundo(new Vec3(0, 0.2, 0));
                    l.addParticle(AtalayaParticulas.MJ_POLVO, p.x + (random.nextDouble() - 0.5) * 3 * K, p.y,
                            p.z + (random.nextDouble() - 0.5) * 3 * K,
                            0, 0.02, 0);
                }
            }
            case LIBRE -> {
                if (velocidad > 0.04F && tickCount % 4 == 0) {
                    l.addParticle(AtalayaParticulas.MJ_POLVO, getX() + (random.nextDouble() - 0.5) * 1.5 * K, getY() + 0.1,
                            getZ() + (random.nextDouble() - 0.5) * 1.5 * K, 0, 0.01, 0);
                }
            }
            case ESPECIAL -> {
                // El remolino de esquirlas sobre el, del alza a la erupcion.
                if (tiempo > MoctezumaGeometria.ESPECIAL_ALZA && tiempo < MoctezumaGeometria.ESPECIAL_CLAVA) {
                    for (int i = 0; i < 2; i++) {
                        double a = (tickCount * 0.35 + i * Math.PI) % Mth.TWO_PI;
                        double r = (3.0 + Math.sin(tickCount * 0.1 + i) * 1.2) * K;
                        ParticleOptions o = i == 0 ? AtalayaParticulas.MJ_OBSIDIANA : AtalayaParticulas.MJ_JADE;
                        l.addParticle(o, getX() + Math.cos(a) * r, getY() + 9.0 * K + Math.sin(a * 2) * 0.6, getZ() + Math.sin(a) * r,
                                -Math.sin(a) * 0.3, 0.2, Math.cos(a) * 0.3);
                    }
                }
            }
            default -> {
            }
        }
    }

    @Override
    protected void efectosMuerte(int tiempo) {
        if (tiempo > disolverDesde() && tiempo % 2 == 0) {
            // Se deshace en astillas de jade y plumas.
            for (int i = 0; i < 3; i++) {
                double y = getY() + random.nextDouble() * 4.0 * K;
                level().addParticle(i == 0 ? AtalayaParticulas.MJ_PLUMA : AtalayaParticulas.MJ_JADE,
                        getX() + (random.nextDouble() - 0.5) * 3.0 * K, y, getZ() + (random.nextDouble() - 0.5) * 3.0 * K,
                        (random.nextDouble() - 0.5) * 0.05, 0.05, (random.nextDouble() - 0.5) * 0.05);
            }
        }
    }

    @Override
    protected void tickMuerte(ServerLevel nivel, int tiempo) {
        if (tiempo == MoctezumaGeometria.MUERTE_RODILLAS) {
            particulas(nivel, AtalayaParticulas.MJ_POLVO, position(), 16, 1.2 * K, 0.1, 1.2 * K, 0.04);
        }
        if (tiempo == MoctezumaGeometria.MUERTE_CAE) {
            sonido(AtalayaSonidos.MOCTEZUMA_PASO, 4.0F, 0.6F);
            particulas(nivel, AtalayaParticulas.MJ_POLVO, puntoMundo(new Vec3(0, 0.2, 2.0).scale(K)), 22, 1.6 * K, 0.1, 1.6 * K, 0.05);
        }
        if (tiempo == duracionMuerte() - 1) {
            particulas(nivel, AtalayaParticulas.MJ_JADE, position().add(0, 1.5 * K, 0), 40, 1.5 * K, 1.2 * K, 1.5 * K, 0.2);
            particulas(nivel, AtalayaParticulas.MJ_PLUMA, position().add(0, 2.0 * K, 0), 30, 1.8 * K, 1.2 * K, 1.8 * K, 0.05);
        }
    }

    // ------------------------------------------------------------------
    //  Sonidos de vanilla
    // ------------------------------------------------------------------

    @Override
    protected @Nullable SoundEvent getAmbientSound() {
        return getEstado() == DORMIDO ? null : AtalayaSonidos.MOCTEZUMA_AMBIENTE;
    }

    @Override
    public int getAmbientSoundInterval() {
        return 220;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource fuente) {
        return AtalayaSonidos.MOCTEZUMA_HERIDO;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return AtalayaSonidos.MOCTEZUMA_MUERTE;
    }

    @Override
    protected float getSoundVolume() {
        return 3.0F;
    }

    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState bloque) {
        playSound(AtalayaSonidos.MOCTEZUMA_PASO, 1.6F, 0.9F + random.nextFloat() * 0.2F);
    }

    @Override
    protected @Nullable SoundEvent sonidoInmune() {
        return AtalayaSonidos.MOCTEZUMA_INMUNE;
    }

    @Override
    protected ParticleOptions particulaInmune() {
        return AtalayaParticulas.MJ_JADE;
    }
}
