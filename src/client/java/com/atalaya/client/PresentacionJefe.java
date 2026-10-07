package com.atalaya.client;

import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.AeralisGeometria;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.NereaGeometria;
import com.atalaya.entity.NovilisEntity;
import com.atalaya.entity.NovilisGeometria;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.RajangGeometria;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.HashMap;
import java.util.Map;

/**
 * La presentacion de un jefe al despertar: una toma de cine alrededor de el
 * mientras se levanta, con las bandas negras arriba y abajo, y al rugir su
 * cartel (el nombre, lo que es y su lema, como en los posters). Luego la
 * camara vuelve sola a los ojos del jugador, mirandole.
 *
 * Todo es del cliente: cada uno la ve si estaba a menos de CERCA bloques cuando
 * el jefe paso de dormido a despertando. Mientras dura no se anda (el jefe es
 * inmune y no ataca: esta despertando, y al acabar espera un poco mas antes del
 * primer golpe, PresasJefe.RESPIRO_PRESENTACION). No se puede saltar: se ve entera.
 *
 * La camara la mueve CamaraPresentacionMixin (despues de que vanilla la ponga
 * en los ojos, asi la vuelta acaba justo donde estaria); el cartel y las bandas,
 * PresentacionHud; mientras, el resto del HUD se esconde (ocultaHud).
 *
 * El despertar dura 9,5 s y tiene el mismo guion en los cuatro (lo comparten
 * sus animaciones: DESPERTAR_ABRE, _SE_ALZA, _ALZADO y _RUGE en cada Geometria),
 * y cada parte tiene su toma, cortando de una a otra:
 *   0        dormido: plano general, alto y de tres cuartos, que se acerca;
 *   ABRE     abre los ojos: primer plano de la cara;
 *   SE_ALZA  se levanta: contrapicado a ras de suelo, de lado, que sube con el;
 *   ALZADO   muestra su poder: gira por detras hasta su costado;
 *   RUGE     su grito final, de frente, con el cartel; al acabar, la camara
 *            vuelve a los ojos del jugador.
 * La camara sigue la cabeza y el pecho de verdad (las tablas CABEZA_DESPERTAR y
 * PECHO_DESPERTAR de cada Geometria, sacadas de la misma animacion).
 */
public final class PresentacionJefe {

    /** Hasta donde se ve la presentacion (bloques). */
    private static final double CERCA = 96.0;
    /** Lo que dura la vuelta de la camara a los ojos (ticks). */
    public static final int VUELTA = 20;
    /** Lo que sigue la toma despues de acabar de despertar (ticks): el cartel aun se lee. */
    private static final int TRAS_DESPERTAR = 6 + com.atalaya.entity.PresasJefe.ESCENA;

    /** Donde estan la cabeza y el pecho del jefe a los tantos ticks de despertar (en su espacio, bloques). */
    public interface Puntos {
        Vec3 en(float ticks);
    }

    /** Lo de cada jefe para su presentacion. */
    public record Ficha(String id, int color, int color2, Vec3 cabezaReposo, Puntos cabeza, Puntos pecho, int abre,
                        int seAlza, int alzado, int ruge, int duracion, SoundEvent acento, float lejos, Tomas tomas) {
    }

    /**
     * Lo que se aparta la camara en las tomas que dependen de su forma (1 = lo
     * normal): "cara", el primer plano, y "caraAlta", lo alto que se pone en el
     * (para ver los ojos por encima de lo que los tapa: las patas de Aeralis, los
     * colmillos de Rajang); "poder", la vuelta por detras (las alas de Aeralis
     * llenan el plano); "cierre", el grito final, y "cierreBaja", lo que se
     * mira por debajo de la cabeza en el (de su alto: asi sube en el plano y el
     * cartel no le tapa el pecho a Rajang, que es bajo).
     */
    public record Tomas(float cara, float caraAlta, float poder, float cierre, float cierreBaja) {
    }

    private static final Tomas NORMALES = new Tomas(1.0F, 0.02F, 1.0F, 1.0F, 0.0F);

    private static final Ficha NEREA = new Ficha("nerea", 0x3FE0FF, 0xD43CFF,
            NereaGeometria.OJO_IZQ.add(NereaGeometria.OJO_DER).scale(0.5), NereaGeometria::cabezaDespertar,
            NereaGeometria::pechoDespertar, NereaGeometria.DESPERTAR_ABRE, NereaGeometria.DESPERTAR_SE_ALZA,
            NereaGeometria.DESPERTAR_ALZADO, NereaGeometria.DESPERTAR_RUGE, NereaGeometria.DURACION_DESPERTAR,
            AtalayaSonidos.MUSICA_NEREA_GRANDE, 1.0F, NORMALES);
    private static final Ficha AERALIS = new Ficha("aeralis", 0x9FE8FF, 0xC9A6FF,
            AeralisGeometria.CABEZA, AeralisGeometria::cabezaDespertar, AeralisGeometria::pechoDespertar,
            AeralisGeometria.DESPERTAR_ABRE, AeralisGeometria.DESPERTAR_SE_ALZA, AeralisGeometria.DESPERTAR_ALZADO,
            AeralisGeometria.DESPERTAR_RUGE, AeralisGeometria.DURACION_DESPERTAR, AtalayaSonidos.MUSICA_AERALIS_GRANDE, 1.0F,
            new Tomas(1.8F, 0.2F, 1.6F, 1.0F, 0.0F));
    private static final Ficha RAJANG = new Ficha("rajang", 0x5BE38A, 0xE8C25A,
            RajangGeometria.CABEZA, RajangGeometria::cabezaDespertar, RajangGeometria::pechoDespertar,
            RajangGeometria.DESPERTAR_ABRE, RajangGeometria.DESPERTAR_SE_ALZA, RajangGeometria.DESPERTAR_ALZADO,
            RajangGeometria.DESPERTAR_RUGE, RajangGeometria.DURACION_DESPERTAR, AtalayaSonidos.MUSICA_RAJANG_GRANDE, 1.75F,
            new Tomas(1.6F, 0.12F, 1.0F, 0.78F, 0.25F));
    private static final Ficha NOVILIS = new Ficha("novilis", 0xFFC23A, 0xFF2A3A,
            NovilisGeometria.CABEZA, NovilisGeometria::cabezaDespertar, NovilisGeometria::pechoDespertar,
            NovilisGeometria.DESPERTAR_ABRE, NovilisGeometria.DESPERTAR_SE_ALZA, NovilisGeometria.DESPERTAR_ALZADO,
            NovilisGeometria.DESPERTAR_RUGE, NovilisGeometria.DURACION_DESPERTAR, AtalayaSonidos.MUSICA_NOVILIS_GRANDE, 1.0F, NORMALES);

    private static final int DORMIDO = 1;
    private static final int DESPERTAR = 2;

    /** El ultimo estado visto de cada jefe (para pillar el paso de dormido a despertando). */
    private static final Map<Integer, Integer> VISTO = new HashMap<>();

    private static @Nullable Ficha ficha;
    private static int jefe = -1;
    /** El tick de juego (cliente) en que empezo a despertar. */
    private static long inicio;
    /** Cuando empieza la vuelta de la camara (ticks desde el inicio): al acabar la toma. */
    private static float vuelta;
    private static boolean revelado;
    /** El rumbo del jefe con el que se calcula la toma: sigue al suyo, pero despacio. */
    private static float rumbo;
    private static float rumboAnt;

    private PresentacionJefe() {
    }

    // ------------------------------------------------------------------
    //  Lo que preguntan los demas
    // ------------------------------------------------------------------

    public static boolean activa() {
        return ficha != null;
    }

    public static @Nullable Ficha ficha() {
        return ficha;
    }

    /** Ticks desde que empezo (con la fraccion del fotograma). */
    public static float tiempo(float parcial) {
        Minecraft mc = Minecraft.getInstance();
        return mc.level == null ? 0.0F : mc.level.getGameTime() - inicio + parcial;
    }

    /** Cuando empieza la vuelta de la camara (ticks desde el inicio). */
    public static float vuelta() {
        return vuelta;
    }

    /** Cuando sale el cartel (ticks desde el inicio): con el rugido. */
    public static float revela() {
        return ficha == null ? 0.0F : ficha.ruge() + 2.0F;
    }

    /** Si el resto del HUD se esconde (mientras la camara esta lejos). */
    public static boolean ocultaHud() {
        return ficha != null && tiempo(0.0F) < vuelta + VUELTA * 0.6F;
    }

    // ------------------------------------------------------------------
    //  Cada tick (al principio, antes de que el juego mire las teclas)
    // ------------------------------------------------------------------

    public static void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            ficha = null;
            VISTO.clear();
            return;
        }
        // Quien despierta: el paso de dormido a despertando, cerca.
        for (Entity e : mc.level.entitiesForRendering()) {
            Ficha f = fichaDe(e);
            if (f == null) {
                continue;
            }
            int est = estado(e);
            Integer antes = VISTO.put(e.getId(), est);
            if (ficha == null && antes != null && antes == DORMIDO && est == DESPERTAR
                    && e.distanceToSqr(mc.player) < CERCA * CERCA && mc.player.isAlive()) {
                empezar(mc, e, f);
            }
        }
        if (VISTO.size() > 64) {
            VISTO.keySet().removeIf(id -> mc.level.getEntity(id) == null);
        }
        if (ficha == null) {
            return;
        }
        Entity e = mc.level.getEntity(jefe);
        float t = tiempo(0.0F);
        if (e == null || !e.isAlive() || !mc.player.isAlive()) {
            ficha = null;
            return;
        }
        // No se puede saltar (Juan, 07-10-2026): la tecla de saltar no hace nada mientras dura.
        while (mc.options.keyJump.consumeClick()) {
            // nada
        }
        // El rumbo de la toma sigue al del jefe, despacio (si se gira, la camara no da tumbos).
        rumboAnt = rumbo;
        float objetivo = cuerpo(e);
        rumbo += Mth.wrapDegrees(objetivo - rumbo) * 0.08F;
        // El jugador mira al jefe: la camara vuelve a sus ojos ya mirandole.
        Vec3 cara = enMundo(e, ficha.cabezaReposo(), 1.0F);
        Vec3 ojo = mc.player.getEyePosition();
        Vec3 d = cara.subtract(ojo);
        float yaw = (float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90.0F;
        float pitch = (float) -(Mth.atan2(d.y, d.horizontalDistance()) * Mth.RAD_TO_DEG);
        mc.player.setYRot(yaw);
        mc.player.setXRot(Mth.clamp(pitch, -60.0F, 60.0F));
        mc.player.yRotO = mc.player.getYRot();
        mc.player.xRotO = mc.player.getXRot();
        mc.player.setYHeadRot(yaw);
        // El cartel, con el rugido: su acento de la musica.
        if (!revelado && t >= revela() && t < vuelta + VUELTA) {
            revelado = true;
            mc.getSoundManager().play(SimpleSoundInstance.forAmbientAddition(ficha.acento()));
        }
        if (t >= vuelta + VUELTA) {
            ficha = null;
        }
    }

    private static void empezar(Minecraft mc, Entity e, Ficha f) {
        ficha = f;
        jefe = e.getId();
        inicio = mc.level.getGameTime() - Math.max(0, e.tickCount - inicioEstado(e));
        vuelta = f.duracion() + TRAS_DESPERTAR;
        revelado = false;
        rumbo = cuerpo(e);
        rumboAnt = rumbo;
        while (mc.options.keyJump.consumeClick()) {
            // la pulsacion de antes no cuenta
        }
    }

    // ------------------------------------------------------------------
    //  La camara (la llama CamaraPresentacionMixin cada fotograma)
    // ------------------------------------------------------------------

    /** Donde va la camara y hacia donde mira. */
    public record Toma(Vec3 pos, float yRot, float xRot, boolean fuera) {
    }

    /**
     * La toma de este fotograma, o null si no hay presentacion. pos, yRot y xRot
     * son los de vanilla (los ojos del jugador): la vuelta acaba en ellos.
     */
    public static @Nullable Toma toma(float parcial, Vec3 pos, float yRot, float xRot) {
        Minecraft mc = Minecraft.getInstance();
        Ficha f = ficha;
        if (f == null || mc.level == null) {
            return null;
        }
        Entity e = mc.level.getEntity(jefe);
        if (e == null) {
            return null;
        }
        float t = tiempo(parcial);
        float b = Mth.lerp(parcial, rumboAnt, rumboAnt + Mth.wrapDegrees(rumbo - rumboAnt));
        Vec3 pies = e.getPosition(parcial);
        float s = Math.min(t, vuelta);
        Vec3 cabeza = enMundo(pies, b, f.cabeza().en(s));
        Vec3 pecho = enMundo(pies, b, f.pecho().en(s));
        // La escala de las tomas: lo alto que tiene la cabeza de pie (Rajang, largo y bajo, de mas lejos).
        float alto = (float) Math.max(5.0, f.cabezaReposo().y) * f.lejos();
        Vec3 base = new Vec3(cabeza.x, pies.y, cabeza.z);
        Tomas tm = f.tomas();
        Vec3 cam;
        Vec3 mira;
        if (s < f.abre()) {
            // 1. Dormido: plano general, alto y de tres cuartos, que se acerca y gira un poco.
            float k = suave(s / f.abre());
            cam = orbita(base, b, Mth.lerp(k, 38.0F, 28.0F), Mth.lerp(k, 2.15F, 1.8F) * alto, Mth.lerp(k, 0.85F, 0.7F) * alto);
            mira = pecho;
        } else if (s < f.seAlza()) {
            // 2. Abre los ojos: primer plano de la cara, que se acerca despacio.
            float k = suave((s - f.abre()) / (f.seAlza() - f.abre()));
            Vec3 frente = frente(b, 0.0F);
            Vec3 lado = frente(b, 90.0F);
            float cerca = alto * tm.cara();
            cam = cabeza.add(frente.scale(Mth.lerp(k, 0.36F, 0.28F) * cerca)).add(lado.scale(0.07F * cerca))
                    .add(0, tm.caraAlta() * alto, 0);
            mira = cabeza;
        } else if (s < f.alzado()) {
            // 3. Se levanta: contrapicado a ras de suelo, de lado, que sube con el.
            float k = suave((s - f.seAlza()) / (f.alzado() - f.seAlza()));
            cam = orbita(base, b, Mth.lerp(k, -62.0F, -44.0F), 0.82F * alto, Mth.lerp(k, 0.04F, 0.12F) * alto);
            mira = pecho.lerp(cabeza, k);
        } else if (s < f.ruge()) {
            // 4. Muestra su poder: gira por detras hasta su costado.
            float k = suave((s - f.alzado()) / (f.ruge() - f.alzado()));
            cam = orbita(base, b, Mth.lerp(k, 155.0F, 100.0F), 1.3F * alto * tm.poder(), 0.45F * alto * tm.poder());
            mira = cabeza;
        } else {
            // 5. El grito final, de frente, con el cartel: se le acerca despacio.
            float k = suave(Mth.clamp((s - f.ruge()) / Math.max(1.0F, vuelta - f.ruge()), 0.0F, 1.0F));
            cam = orbita(base, b, Mth.lerp(k, -9.0F, 5.0F), Mth.lerp(k, 1.4F, 1.12F) * alto * tm.cierre(),
                    0.42F * alto * tm.cierre());
            mira = cabeza.subtract(0, tm.cierreBaja() * alto, 0);
        }
        // Si hay un muro entre los dos, la camara se pone delante del muro.
        cam = sinMuros(mc, mira, cam, e);
        Vec3 d = mira.subtract(cam);
        float cy = (float) (Mth.atan2(d.z, d.x) * Mth.RAD_TO_DEG) - 90.0F;
        float cx = (float) -(Mth.atan2(d.y, d.horizontalDistance()) * Mth.RAD_TO_DEG);
        // La vuelta a los ojos del jugador.
        float v = suave(Mth.clamp((t - vuelta) / VUELTA, 0.0F, 1.0F));
        if (v > 0.0F) {
            cam = cam.lerp(pos, v);
            cy = cy + Mth.wrapDegrees(yRot - cy) * v;
            cx = Mth.lerp(v, cx, xRot);
        }
        return new Toma(cam, cy, cx, v < 0.7F);
    }

    /** Hacia donde queda "ang" grados desde su frente (en horizontal). */
    private static Vec3 frente(float rumbo, float ang) {
        float rad = (rumbo + ang) * Mth.DEG_TO_RAD;
        return new Vec3(-Mth.sin(rad), 0, Mth.cos(rad));
    }

    /** Un punto a "dist" de la base, a "ang" grados de su frente y "alt" de alto. */
    private static Vec3 orbita(Vec3 base, float rumbo, float ang, float dist, float alt) {
        return base.add(frente(rumbo, ang).scale(dist)).add(0, alt, 0);
    }

    private static Vec3 sinMuros(Minecraft mc, Vec3 desde, Vec3 hasta, Entity e) {
        HitResult h = mc.level.clip(new ClipContext(desde, hasta, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, e));
        if (h.getType() == HitResult.Type.MISS) {
            return hasta;
        }
        Vec3 hacia = desde.subtract(h.getLocation());
        double l = hacia.length();
        return l < 1.0E-3 ? h.getLocation() : h.getLocation().add(hacia.scale(Math.min(0.6, l) / l));
    }

    // ------------------------------------------------------------------
    //  Ayudas
    // ------------------------------------------------------------------

    private static float suave(float k) {
        return k * k * (3.0F - 2.0F * k);
    }


    /** Del espacio del jefe (x a su izquierda, y arriba, z delante; bloques) al mundo. */
    private static Vec3 enMundo(Vec3 pies, float rumboCuerpo, Vec3 local) {
        float b = rumboCuerpo * Mth.DEG_TO_RAD;
        double c = Mth.cos(b);
        double s = Mth.sin(b);
        return new Vec3(pies.x + local.x * c - local.z * s, pies.y + local.y, pies.z + local.x * s + local.z * c);
    }

    private static Vec3 enMundo(Entity e, Vec3 local, float parcial) {
        return enMundo(e.getPosition(parcial), cuerpo(e), local);
    }

    private static float cuerpo(Entity e) {
        return e instanceof net.minecraft.world.entity.LivingEntity v ? v.yBodyRot : e.getYRot();
    }

    private static @Nullable Ficha fichaDe(Entity e) {
        if (e instanceof NereaEntity) {
            return NEREA;
        }
        if (e instanceof AeralisEntity) {
            return AERALIS;
        }
        if (e instanceof RajangEntity) {
            return RAJANG;
        }
        if (e instanceof NovilisEntity) {
            return NOVILIS;
        }
        return null;
    }

    private static int estado(Entity e) {
        if (e instanceof NereaEntity n) {
            return n.getEstado();
        }
        if (e instanceof AeralisEntity a) {
            return a.getEstado();
        }
        if (e instanceof RajangEntity r) {
            return r.getEstado();
        }
        if (e instanceof NovilisEntity n) {
            return n.getEstado();
        }
        return -1;
    }

    private static int inicioEstado(Entity e) {
        if (e instanceof NereaEntity n) {
            return n.inicioEstado;
        }
        if (e instanceof AeralisEntity a) {
            return a.inicioEstado;
        }
        if (e instanceof RajangEntity r) {
            return r.inicioEstado;
        }
        if (e instanceof NovilisEntity n) {
            return n.inicioEstado;
        }
        return e.tickCount;
    }
}
