package com.atalaya.client;

import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.RajangEntity;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.client.Minecraft;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.attribute.EnvironmentAttribute;
import net.minecraft.world.attribute.EnvironmentAttributes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El cielo de cada jefe (10-10-2026, Juan: "que el cielo cambie segun el boss
 * que estemos peleando... debe volverse poco a poco el clima y si lo matas
 * desvanecerse poco a poco y volver al original; sorprendeme"). Mientras se
 * pelea con uno (despierto, a menos de 96 bloques y sin liberar, como su
 * musica: MusicaJefes), el cielo, la niebla, las nubes y la luz del mundo se
 * van volviendo los suyos en 8 s, y al liberarlo (o al irse) vuelven en 8 s.
 * Empeora con cada fase (la IV, del todo) y late con la Furia.
 *
 * <pre>
 *   Novilis  Apocalipsis Solar   cielo rojo sangre que late como un sol que
 *                                se muere, nubes de humo rojo, ocaso de fuego,
 *                                la luz del mundo roja; llueve ceniza y suben
 *                                brasas.
 *   Aeralis  Tormenta            cielo de pizarra, nubes negras, el mundo mas
 *                                oscuro y frio; relampagos: el cielo se enciende,
 *                                cae un rayo a lo lejos y retumba el trueno
 *                                (cada vez mas seguidos); rachas de viento.
 *   Nerea    Abismo              azul de fondo marino y niebla cerrada, las
 *                                estrellas como luces del abismo aun de dia, la
 *                                luz verdeazul que ondula; suben luces y burbujas.
 *   Rajang   Eclipse de Jade     cielo de jade oscuro con un ocaso de oro, las
 *                                estrellas de un eclipse, la luz verde dorada;
 *                                flota polen de oro y caen hojas. En la IV el
 *                                cielo respira hacia el oro.
 * </pre>
 *
 * Todo se hace en el cliente: se mezclan los atributos de ambiente que lee la
 * camara (CieloJefesMixin) y las particulas salen alrededor de ella. Los rayos
 * de la tormenta los pinta AeralisRenderer.
 */
public final class CieloJefes {

    /** Hasta donde se siente un jefe (bloques), como su musica. */
    private static final double CERCA = 96.0;
    /** Lo que tarda en volverse el cielo y en volver (ticks). */
    private static final float FUNDE = 160.0F;

    enum Tema {
        // cielo, niebla, nubes (ARGB), ocaso (ARGB), luz del mundo, lo que alumbra el cielo, estrellas, niebla: empieza, acaba
        NOVILIS(0x6A1206, 0x8C2A0E, 0xF0401008, 0xE8FF3010, 0xFFA080, 0.88F, 0.0F, 10.0F, 150.0F),
        AERALIS(0x3C424C, 0x4E555E, 0xF62A2E36, 0x00000000, 0xA8B4D8, 0.6F, 0.0F, 18.0F, 170.0F),
        NEREA(0x08303C, 0x0C4A55, 0xE8124048, 0x00000000, 0x78D0E0, 0.8F, 0.55F, 4.0F, 110.0F),
        RAJANG(0x123826, 0x5E6E2E, 0xE8203E2C, 0xD0E0B030, 0xD0E8A8, 0.85F, 0.35F, 16.0F, 160.0F);

        final int cielo, niebla, nubes, ocaso, luz;
        final float alumbra, estrellas, nieblaDesde, nieblaHasta;

        Tema(int cielo, int niebla, int nubes, int ocaso, int luz, float alumbra, float estrellas, float nieblaDesde,
             float nieblaHasta) {
            this.cielo = cielo;
            this.niebla = niebla;
            this.nubes = nubes;
            this.ocaso = ocaso;
            this.luz = luz;
            this.alumbra = alumbra;
            this.estrellas = estrellas;
            this.nieblaDesde = nieblaDesde;
            this.nieblaHasta = nieblaHasta;
        }
    }

    /** El cielo que hay ahora (o el que se va) y lo metido que esta (0 a 1). */
    private static @Nullable Tema actual;
    private static float mezcla;
    /** Lo fuerte que lo quiere la fase (y la Furia) del jefe: 0,8 en la I, 1 en la IV; se mueve despacio. */
    private static float fuerza = 0.8F;
    private static boolean furia;
    private static int fase = 1;
    private static float reloj;
    /** La tormenta: el relampago (de 1 a 0), cuando cae el siguiente y el rayo que se ve. */
    private static float relampago;
    private static int siguienteRayo = 120;
    private static int rayoEdad = -1;
    private static @Nullable Vec3 rayoArriba;
    private static @Nullable Vec3 rayoAbajo;
    private static long rayoSemilla;
    private static int truenoEn = -1;
    private static @Nullable Vec3 truenoDonde;

    private CieloJefes() {
    }

    // ------------------------------------------------------------------
    //  Cada tick: que cielo toca y cuanto
    // ------------------------------------------------------------------

    public static void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            actual = null;
            mezcla = 0.0F;
            return;
        }
        if (mc.isPaused()) {
            return;
        }
        reloj++;
        Entity jefe = jefeCercano(mc);
        Tema quiere = jefe == null ? null : tema(jefe);
        if (quiere != null && quiere == actual) {
            mezcla = Math.min(1.0F, mezcla + 1.0F / FUNDE);
        } else {
            mezcla = Math.max(0.0F, mezcla - 1.0F / FUNDE);
            if (mezcla <= 0.0F) {
                actual = quiere;
                relampago = 0.0F;
                rayoEdad = -1;
            }
        }
        if (jefe != null && quiere == actual) {
            fase = Mth.clamp(fase(jefe), 1, 4);
            furia = furia(jefe);
            float quiereFuerza = furia ? 1.0F : 0.8F + 0.2F * (fase - 1) / 3.0F;
            fuerza += (quiereFuerza - fuerza) * 0.02F;
        }
        if (actual == null || mezcla <= 0.0F) {
            return;
        }
        if (actual == Tema.AERALIS) {
            tormenta(mc);
        }
        particulas(mc);
    }

    /** Si hay cielo de jefe que mezclar ahora mismo. */
    public static boolean activo() {
        return actual != null && mezcla > 0.0F;
    }

    private static @Nullable Entity jefeCercano(Minecraft mc) {
        Entity mejor = null;
        double d = CERCA * CERCA;
        for (Entity e : mc.level.entitiesForRendering()) {
            if (tema(e) == null) {
                continue;
            }
            double dd = e.distanceToSqr(mc.player);
            if (dd < d) {
                d = dd;
                mejor = e;
            }
        }
        return mejor;
    }

    /** El cielo del jefe, si esta despierto y peleando; null si duerme, se libera o no es un jefe. */
    private static @Nullable Tema tema(Entity e) {
        if (e.isRemoved()) {
            return null;
        }
        if (e instanceof NereaEntity n) {
            return n.getEstado() != NereaEntity.DORMIDO && !n.isDeadOrDying() ? Tema.NEREA : null;
        }
        if (e instanceof AeralisEntity a) {
            return a.getEstado() != AeralisEntity.DORMIDA && !a.isDeadOrDying() ? Tema.AERALIS : null;
        }
        if (e instanceof RajangEntity r) {
            return r.getEstado() != RajangEntity.DORMIDO && !r.isDeadOrDying() ? Tema.RAJANG : null;
        }
        if (e instanceof NovilisEntity v) {
            return v.getEstado() != NovilisEntity.DORMIDO && !v.isDeadOrDying() ? Tema.NOVILIS : null;
        }
        return null;
    }

    private static int fase(Entity e) {
        return e instanceof NereaEntity n ? n.fase() : e instanceof AeralisEntity a ? a.fase()
                : e instanceof RajangEntity r ? r.fase() : e instanceof NovilisEntity v ? v.fase() : 1;
    }

    private static boolean furia(Entity e) {
        return e instanceof NereaEntity n ? n.tieneFuria() : e instanceof AeralisEntity a ? a.tieneFuria()
                : e instanceof RajangEntity r ? r.tieneFuria() : e instanceof NovilisEntity v && v.tieneFuria();
    }

    // ------------------------------------------------------------------
    //  La tormenta de Aeralis: relampagos, rayos y truenos
    // ------------------------------------------------------------------

    private static void tormenta(Minecraft mc) {
        RandomSource r = mc.level.getRandom();
        relampago *= 0.78F;
        if (rayoEdad >= 0) {
            rayoEdad++;
            if (rayoEdad == 3) {
                // El segundo fogonazo del mismo rayo.
                relampago = Math.max(relampago, 0.85F);
                rayoSemilla++;
            }
            if (rayoEdad > 8) {
                rayoEdad = -1;
            }
        }
        if (truenoEn >= 0 && --truenoEn == 0 && truenoDonde != null) {
            mc.level.playLocalSound(truenoDonde.x, truenoDonde.y, truenoDonde.z, AtalayaSonidos.AERALIS_TRUENO, SoundSource.WEATHER,
                    5.0F * mezcla, 0.7F + r.nextFloat() * 0.25F, false);
            truenoEn = -1;
        }
        if (mezcla < 0.6F || --siguienteRayo > 0) {
            return;
        }
        // Cada vez mas seguidos: de 7-13 s en la I a 3-6 s en la IV (y con la Furia).
        int base = furia ? 60 : 160 - 25 * (fase - 1);
        siguienteRayo = base + r.nextInt(base / 2 + 20);
        Vec3 ojo = mc.gameRenderer.mainCamera().position();
        double a = r.nextDouble() * Math.PI * 2;
        double d = 40.0 + r.nextDouble() * 50.0;
        double x = ojo.x + Math.cos(a) * d;
        double z = ojo.z + Math.sin(a) * d;
        double suelo = mc.level.getHeight(Heightmap.Types.MOTION_BLOCKING, Mth.floor(x), Mth.floor(z));
        if (suelo <= mc.level.getMinY() + 1) {
            suelo = ojo.y - 4.0;
        }
        rayoAbajo = new Vec3(x, suelo, z);
        rayoArriba = new Vec3(x + r.nextGaussian() * 6.0, Math.max(suelo + 60.0, ojo.y + 70.0), z + r.nextGaussian() * 6.0);
        rayoSemilla = r.nextLong();
        rayoEdad = 0;
        relampago = 1.0F;
        // El trueno llega despues, mas cuanto mas lejos (y algo de ruido).
        truenoEn = 6 + (int) (d / 9.0) + r.nextInt(8);
        truenoDonde = rayoAbajo;
    }

    /** Lo que alumbra el relampago ahora (0 a 1, ya con la mezcla). */
    public static float relampago() {
        return actual == Tema.AERALIS ? relampago * mezcla : 0.0F;
    }

    /** El rayo que se ve ahora (arriba, abajo y su semilla), o null. */
    public static @Nullable Vec3 rayoArriba() {
        return actual == Tema.AERALIS && rayoEdad >= 0 && rayoEdad <= 6 ? rayoArriba : null;
    }

    public static @Nullable Vec3 rayoAbajo() {
        return rayoAbajo;
    }

    public static long rayoSemilla() {
        return rayoSemilla;
    }

    public static float rayoAlfa() {
        return rayoEdad < 0 ? 0.0F : rayoEdad <= 1 ? 1.0F : rayoEdad == 2 ? 0.35F : rayoEdad <= 4 ? 0.9F : 0.5F;
    }

    // ------------------------------------------------------------------
    //  Las particulas alrededor de la camara
    // ------------------------------------------------------------------

    private static void particulas(Minecraft mc) {
        RandomSource r = mc.level.getRandom();
        Vec3 o = mc.gameRenderer.mainCamera().position();
        float k = mezcla * fuerza;
        switch (actual) {
            case NOVILIS -> {
                // Llueve ceniza, suben brasas y, a lo lejos, humo rojo.
                for (int i = 0; i < Math.round(4 * k); i++) {
                    poner(mc, r, AtalayaParticulas.NOVILIS_CENIZA, o, 3.0, 18.0, 4.0, 14.0, 0.0, -0.02, 0.0);
                }
                if (r.nextFloat() < 1.2F * k) {
                    poner(mc, r, AtalayaParticulas.NOVILIS_BRASA, o, 2.0, 12.0, -2.0, 3.0, 0.0, 0.03, 0.0);
                }
                if (r.nextFloat() < 0.35F * k) {
                    poner(mc, r, AtalayaParticulas.NOVILIS_HUMO, o, 14.0, 28.0, 0.0, 10.0, 0.0, 0.02, 0.0);
                }
            }
            case AERALIS -> {
                // Rachas de viento que cruzan siempre hacia el mismo lado, y jirones.
                double ang = reloj * 0.002;
                double vx = Math.cos(ang) * 0.6;
                double vz = Math.sin(ang) * 0.6;
                for (int i = 0; i < Math.round(3 * k); i++) {
                    poner(mc, r, AtalayaParticulas.AERALIS_VIENTO, o, 3.0, 16.0, -1.0, 8.0, vx, 0.0, vz);
                }
                if (r.nextFloat() < 0.4F * k) {
                    poner(mc, r, AtalayaParticulas.AERALIS_JIRON, o, 8.0, 22.0, 2.0, 12.0, vx * 0.5, 0.0, vz * 0.5);
                }
            }
            case NEREA -> {
                // Luces del abismo y burbujas que suben.
                for (int i = 0; i < Math.round(3 * k); i++) {
                    poner(mc, r, AtalayaParticulas.NEREA_LUZ, o, 2.0, 16.0, -2.0, 8.0, 0.0, 0.02, 0.0);
                }
                if (r.nextFloat() < 1.0F * k) {
                    poner(mc, r, AtalayaParticulas.NEREA_BURBUJA, o, 2.0, 10.0, -2.0, 2.0, 0.0, 0.04, 0.0);
                }
            }
            case RAJANG -> {
                // Polen de oro que flota y hojas que caen.
                for (int i = 0; i < Math.round(3 * k); i++) {
                    poner(mc, r, AtalayaParticulas.RAJANG_ORO, o, 2.0, 16.0, -1.0, 8.0, 0.0, 0.005, 0.0);
                }
                if (r.nextFloat() < 0.6F * k) {
                    poner(mc, r, AtalayaParticulas.RAJANG_HOJA, o, 3.0, 14.0, 4.0, 12.0, 0.0, -0.03, 0.0);
                }
            }
        }
    }

    /** Una particula en un anillo alrededor de o (de rMin a rMax en horizontal, de yMin a yMax de alto). */
    private static void poner(Minecraft mc, RandomSource r, SimpleParticleType tipo, Vec3 o, double rMin, double rMax, double yMin,
                              double yMax, double vx, double vy, double vz) {
        double a = r.nextDouble() * Math.PI * 2;
        double d = rMin + r.nextDouble() * (rMax - rMin);
        mc.level.addParticle(tipo, o.x + Math.cos(a) * d, o.y + yMin + r.nextDouble() * (yMax - yMin), o.z + Math.sin(a) * d,
                vx, vy, vz);
    }

    // ------------------------------------------------------------------
    //  Los atributos de ambiente (los pide CieloJefesMixin)
    // ------------------------------------------------------------------

    /**
     * Lo que ve la camara de este atributo con el cielo del jefe mezclado, o
     * null si este no se toca.
     */
    public static @Nullable Object mezclar(EnvironmentAttribute<?> atributo, Object valor) {
        Tema t = actual;
        if (t == null) {
            return null;
        }
        float k = mezcla * fuerza;
        float latido = latido(t);
        float rel = relampago();
        if (atributo == EnvironmentAttributes.SKY_COLOR) {
            int c = rgb((Integer) valor, t.cielo, k);
            c = rgb(c, t == Tema.NOVILIS ? 0xB0280A : t == Tema.RAJANG ? 0x4A5A14 : t.cielo, latido * mezcla);
            return rgb(c, 0xD8DCFF, rel);
        }
        if (atributo == EnvironmentAttributes.FOG_COLOR) {
            int c = rgb((Integer) valor, t.niebla, k);
            c = rgb(c, t == Tema.NOVILIS ? 0xC04010 : t.niebla, latido * mezcla * 0.7F);
            return rgb(c, 0xB8BCE8, rel);
        }
        if (atributo == EnvironmentAttributes.CLOUD_COLOR) {
            int c = argb((Integer) valor, t.nubes, k);
            return argb(c, 0xFFE0E4FF, rel * 0.7F);
        }
        if (atributo == EnvironmentAttributes.SUNRISE_SUNSET_COLOR) {
            return argb((Integer) valor, t.ocaso, k);
        }
        if (atributo == EnvironmentAttributes.SKY_LIGHT_COLOR) {
            int c = rgb((Integer) valor, t.luz, k);
            return rgb(c, 0xFFFFFF, rel);
        }
        if (atributo == EnvironmentAttributes.SKY_LIGHT_FACTOR) {
            float f = (Float) valor;
            float quiere = f * t.alumbra;
            if (t == Tema.NEREA) {
                // La luz del abismo ondula.
                quiere *= 1.0F + 0.05F * Mth.sin(reloj * 0.08F);
            }
            float v = Mth.lerp(k, f, quiere);
            return Mth.clamp(Mth.lerp(rel, v, 1.0F), 0.0F, 1.0F);
        }
        if (atributo == EnvironmentAttributes.STAR_BRIGHTNESS) {
            return Math.max((Float) valor, t.estrellas * k);
        }
        if (atributo == EnvironmentAttributes.FOG_START_DISTANCE) {
            float f = (Float) valor;
            return Mth.lerp(k, f, Math.min(f, t.nieblaDesde));
        }
        if (atributo == EnvironmentAttributes.FOG_END_DISTANCE) {
            float f = (Float) valor;
            return Mth.lerp(k, f, Math.min(f, t.nieblaHasta));
        }
        return null;
    }

    /**
     * El latido del cielo (0 a 1): el sol de Novilis se muere a golpes (mas
     * deprisa con la Furia), el jade de Rajang respira hacia el oro en la IV.
     */
    private static float latido(Tema t) {
        if (t == Tema.NOVILIS) {
            float v = Mth.sin(reloj * (furia ? 0.14F : 0.07F));
            return (float) Math.pow(Math.max(0.0F, v), 4) * (0.25F + 0.1F * fase);
        }
        if (t == Tema.RAJANG && (fase >= 4 || furia)) {
            return 0.5F + 0.5F * Mth.sin(reloj * 0.03F);
        }
        return 0.0F;
    }

    private static int rgb(int a, int b, float k) {
        k = Mth.clamp(k, 0.0F, 1.0F);
        int r = (int) Mth.lerp(k, (a >> 16) & 255, (b >> 16) & 255);
        int g = (int) Mth.lerp(k, (a >> 8) & 255, (b >> 8) & 255);
        int bl = (int) Mth.lerp(k, a & 255, b & 255);
        return (a & 0xFF000000) | (r << 16) | (g << 8) | bl;
    }

    private static int argb(int a, int b, float k) {
        k = Mth.clamp(k, 0.0F, 1.0F);
        int al = (int) Mth.lerp(k, (a >>> 24) & 255, (b >>> 24) & 255);
        return (al << 24) | (rgb(a, b, k) & 0xFFFFFF);
    }
}
