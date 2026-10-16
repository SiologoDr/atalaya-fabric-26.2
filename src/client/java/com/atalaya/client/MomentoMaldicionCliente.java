package com.atalaya.client;

import com.atalaya.net.AtalayaRed;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.attribute.EnvironmentAttribute;
import net.minecraft.world.attribute.EnvironmentAttributes;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * El Momento Maldicion en el cliente (lo empieza y lo para el servidor:
 * MomentoMaldicion). Lleva el estado, el calendario de la cinematica (va a la
 * par de sus sonidos, momento_maldicion_sonidos.py), la musica en bucle, el
 * cielo maldito, el temblor de la camara, las particulas y los sonidos. Lo que
 * se pinta lo pintan MomentoMaldicionHud (la cinematica) y CieloRoto (el cielo
 * roto).
 *
 * La cinematica es EL SELLO, sin texto de ninguna clase (Juan: el texto solo
 * en el aviso del chat al acabar):
 * <pre>
 *   0      el mundo se apaga y el corazon late (cada vez mas seguido)
 *   18     en el centro se dibuja un sello: el doble anillo, el de dentro
 *   56     la estrella de siete puntas, punta a punta, y el heptagono
 *   80     los dieciseis sigilos, uno a uno; cada capa gira a su paso, el
 *          sello se echa hacia atras y se traga motas de luz en espiral
 *   126    en su centro nace el nucleo, que se carga y lanza rayos a las
 *          puntas; el sello se levanta y gira cada vez mas deprisa
 *   150    el sello se raja desde el nucleo
 *   168    SILENCIO: todo se congela, en blanco
 *   174    LA FRACTURA: el nucleo revienta, la pantalla salta en esquirlas,
 *          el sello se rompe en trozos, una onda barre la pantalla y el cielo
 *          se raja entero; entra la nana maldita
 *   224    el aviso del chat (MOMENTO FRACTURA: y el texto) y la campana
 * </pre>
 *
 * Despues, mientras dura, nada en el HUD (en la prueba, solo su contador): el
 * cielo de sangre roto como un cristal golpeado (un solo hueco en lo alto, con
 * sus ojos rojos), la niebla y las grietas que laten con
 * la musica (un corazon cada 3,7 s), motas rojas que suben y ceniza negra que
 * cae. Al pararlo: la luz que entra, las grietas que se cierran y el cielo que
 * vuelve.
 */
public final class MomentoMaldicionCliente {

    public enum Fase { NADA, INTRO, MALDITO, FIN }

    // El calendario de la cinematica (ticks desde que empieza), el mismo que el de sus sonidos.
    public static final int T_CIERRA = 14;
    public static final int T_CIRCULO = 18;
    public static final int T_CIRCULO2 = 40;
    public static final int T_ESTRELLA = 56;
    public static final int T_RUNAS = 80;
    public static final int T_RUNAS_FIN = 118;
    public static final int RUNAS = 16;
    public static final int T_TITULO = 126;
    public static final int T_GRIETAS = 150;
    public static final int T_SILENCIO = 168;
    public static final int T_FRACTURA = 174;
    public static final int T_ABRE = 196;
    public static final int T_FIN_INTRO = 224;
    /** Lo que dura la salida (ticks). */
    public static final int T_SALIDA = 120;
    /** El latido de la musica de los compañeros: su golpe grave va cada 3,7 s. */
    public static final int LATIDO = 74;
    /** Los latidos de la cinematica (ticks): cada vez mas seguidos hasta el silencio. */
    public static final int[] LATIDOS = {0, 30, 54, 74, 90, 104, 116, 126, 134, 142, 149, 155, 160, 164};

    private static Fase fase = Fase.NADA;
    /** Ticks en la fase. */
    private static int t;
    private static String titulo = "";
    private static String texto = "";
    /** Ticks que dura despues de la cinematica (0, sin reloj) y los que lleva maldito. */
    private static int duracion;
    private static int maldito;
    /** Lo que dura el contador de la prueba desde que acaba la cinematica (ticks; 0, sin prueba). */
    private static int contador;
    private static long semilla;
    /** El cielo maldito (0 a 1). */
    private static float cielo;
    private static float cieloAntes;
    private static @Nullable Pista musica;
    private static int reloj;

    private MomentoMaldicionCliente() {
    }

    // ------------------------------------------------------------------
    //  Lo que manda el servidor
    // ------------------------------------------------------------------

    public static void recibir(AtalayaRed.Momento m) {
        Minecraft mc = Minecraft.getInstance();
        switch (m.accion()) {
            case AtalayaRed.Momento.EMPIEZA -> {
                titulo = m.titulo();
                texto = m.texto();
                duracion = m.duracion();
                contador = m.contador();
                maldito = 0;
                semilla = m.semilla();
                fase = Fase.INTRO;
                t = 0;
                MomentoMaldicionHud.preparar(semilla, titulo);
                sonar(mc, AtalayaSonidos.MOMENTO_ANIMACION, 1.0F);
            }
            case AtalayaRed.Momento.SIGUE -> {
                titulo = m.titulo();
                texto = m.texto();
                duracion = m.duracion();
                contador = m.contador();
                semilla = m.semilla();
                MomentoMaldicionHud.preparar(semilla, titulo);
                if (m.pasado() < T_FIN_INTRO) {
                    // Entra a media cinematica: la ve desde donde va.
                    fase = Fase.INTRO;
                    t = m.pasado();
                    maldito = 0;
                } else {
                    fase = Fase.MALDITO;
                    t = 0;
                    maldito = m.pasado() - T_FIN_INTRO;
                    cielo = 1.0F;
                    empezarMusica(mc, 40);
                }
            }
            case AtalayaRed.Momento.PARA -> {
                if (fase == Fase.NADA || fase == Fase.FIN) {
                    return;
                }
                fase = Fase.FIN;
                t = 0;
                if (musica != null) {
                    musica.apagar(70);
                }
                sonar(mc, AtalayaSonidos.MOMENTO_FIN, 1.0F);
            }
            default -> {
            }
        }
    }

    /** Al salir del mundo: se olvida todo. */
    public static void olvidar() {
        fase = Fase.NADA;
        t = 0;
        contador = 0;
        cielo = 0.0F;
        cieloAntes = 0.0F;
        if (musica != null) {
            musica.apagar(1);
            musica = null;
        }
    }

    // ------------------------------------------------------------------
    //  Cada tick
    // ------------------------------------------------------------------

    public static void tick(Minecraft mc) {
        reloj++;
        if (mc.level == null || mc.player == null) {
            if (fase != Fase.NADA) {
                olvidar();
            }
            return;
        }
        if (musica != null && musica.isStopped()) {
            musica = null;
        }
        cieloAntes = cielo;
        if (fase == Fase.NADA) {
            return;
        }
        if (mc.isPaused()) {
            return;
        }
        t++;
        switch (fase) {
            case INTRO -> {
                if (t == T_TITULO) {
                    sonar(mc, AtalayaSonidos.MOMENTO_TITULO, 1.0F);
                }
                if (t == T_FRACTURA) {
                    sonar(mc, AtalayaSonidos.MOMENTO_FRACTURA, 1.0F);
                    // La onda tambien en el mundo: un anillo de motas que sale de quien mira.
                    onda(mc);
                }
                if (t == T_FRACTURA + 6) {
                    // El cielo que se raja entero, de lo alto al horizonte.
                    sonar(mc, AtalayaSonidos.MOMENTO_CIELO, 1.0F);
                }
                if (t == T_ABRE - 10) {
                    empezarMusica(mc, 60);
                }
                // El cielo: se apaga un poco al empezar y se vuelve del todo con la fractura.
                float quiere = t < T_FRACTURA ? 0.3F * Mth.clamp(t / 60.0F, 0.0F, 1.0F) : 1.0F;
                cielo += (quiere - cielo) * (t < T_FRACTURA ? 0.05F : 0.12F);
                if (t >= T_FIN_INTRO) {
                    sonar(mc, AtalayaSonidos.MOMENTO_AVISO, 1.0F);
                    fase = Fase.MALDITO;
                    t = 0;
                    maldito = 0;
                }
                if (t > T_FRACTURA) {
                    particulas(mc, 0.6F);
                }
            }
            case MALDITO -> {
                maldito++;
                cielo += (1.0F - cielo) * 0.05F;
                if (musica == null) {
                    empezarMusica(mc, 40);
                }
                particulas(mc, 1.0F);
            }
            case FIN -> {
                cielo = Math.max(0.0F, cielo - 1.0F / T_SALIDA);
                if (t >= T_SALIDA) {
                    fase = Fase.NADA;
                    t = 0;
                    cielo = 0.0F;
                }
            }
            default -> {
            }
        }
    }

    // ------------------------------------------------------------------
    //  Lo que preguntan los demas
    // ------------------------------------------------------------------

    public static Fase fase() {
        return fase;
    }

    /** Ticks en la fase, con la parte del tick que va. */
    public static float tiempo(float parcial) {
        return fase == Fase.NADA ? 0.0F : t + (Minecraft.getInstance().isPaused() ? 0.0F : parcial);
    }

    public static String titulo() {
        return titulo;
    }

    public static String texto() {
        return texto;
    }

    /** Lo que queda de reloj (ticks), o -1 si no hay. */
    public static int queda() {
        return duracion <= 0 ? -1 : Math.max(0, duracion - maldito);
    }

    /** Lo que dura el contador de la prueba desde que acaba la cinematica (ticks), o 0 si no hay prueba. */
    public static int contador() {
        return contador;
    }

    /** Los ticks maldito (para el latido de las venas y del cielo). */
    public static int maldito() {
        return maldito;
    }

    public static long semilla() {
        return semilla;
    }

    /** Si su musica manda (la de los jefes y la de vanilla callan). */
    public static boolean musicaManda() {
        return musica != null && !musica.apagando;
    }

    public static boolean musicaSuena() {
        return musica != null;
    }

    /**
     * El latido del momento (0 a 1), al golpe grave de la musica: dos golpes,
     * pum-pum, y se apaga.
     */
    public static float latido(float parcial) {
        if (fase != Fase.MALDITO) {
            return 0.0F;
        }
        float k = (maldito + parcial) % LATIDO;
        float uno = (float) Math.exp(-k / 6.0);
        float dos = k > 9 ? (float) Math.exp(-(k - 9) / 7.0) * 0.6F : 0.0F;
        return Mth.clamp(uno + dos, 0.0F, 1.0F);
    }

    /**
     * Lo abiertas que estan las grietas del cielo (CieloRoto), de 0 a 1: se
     * abren en un segundo con la fractura, siguen mientras dura y se cierran al
     * pararlo.
     */
    public static float grietasCielo(float parcial) {
        float tt = tiempo(parcial);
        return switch (fase) {
            case INTRO -> tt < T_FRACTURA ? 0.0F : Mth.clamp((tt - T_FRACTURA) / 20.0F, 0.0F, 1.0F);
            case MALDITO -> 1.0F;
            case FIN -> 1.0F - Mth.clamp(tt / 30.0F, 0.0F, 1.0F);
            default -> 0.0F;
        };
    }

    /** El reloj de las grietas del cielo (ticks, para los pulsos de luz que bajan por ellas). */
    public static float relojCielo(float parcial) {
        return reloj + parcial;
    }

    /** Los ticks maldito, con la parte del tick (para los ojos del cielo roto). */
    public static float malditoCielo(float parcial) {
        return maldito + (fase == Fase.MALDITO && !Minecraft.getInstance().isPaused() ? parcial : 0.0F);
    }

    /** El destello de las grietas del cielo (0 a 1): al abrirse con la fractura y al cerrarse. */
    public static float destelloCielo(float parcial) {
        float tt = tiempo(parcial);
        return switch (fase) {
            case INTRO -> tt < T_FRACTURA ? 0.0F : (float) Math.exp(-(tt - T_FRACTURA) / 10.0);
            case FIN -> 1.0F - Mth.clamp(tt / 14.0F, 0.0F, 1.0F);
            default -> 0.0F;
        };
    }

    /** El latido de la cinematica (0 a 1): sube con cada golpe del corazon y se apaga. */
    public static float latidoIntro(float tt) {
        float v = 0.0F;
        for (int l : LATIDOS) {
            float d = tt - l;
            if (d >= 0 && d < 16) {
                v = Math.max(v, (float) Math.exp(-d / 4.0));
            }
        }
        return v;
    }

    /** El temblor de la camara (yaw, pitch, roll en grados), o null si no tiembla. */
    public static float @Nullable [] angulos(float parcial) {
        if (fase != Fase.INTRO) {
            return null;
        }
        float tt = t + parcial;
        if (tt >= T_SILENCIO && tt < T_FRACTURA) {
            // En el silencio no se mueve nada.
            return null;
        }
        // Cada latido mueve un poco la vista (mas cuanto mas cerca del final), y al rajarse el sello tiembla todo.
        float fuerza = latidoIntro(tt) * (0.15F + 0.45F * Mth.clamp(tt / T_SILENCIO, 0.0F, 1.0F));
        if (tt >= T_GRIETAS && tt < T_SILENCIO) {
            fuerza = Math.max(fuerza, 0.9F * (tt - T_GRIETAS) / (T_SILENCIO - T_GRIETAS));
        }
        float d = tt - T_FRACTURA;
        if (d >= 0 && d < 34) {
            fuerza = Math.max(fuerza, 3.2F * (float) Math.exp(-d / 9.0));
        }
        if (fuerza <= 0.01F) {
            return null;
        }
        float a = tt * 2.7F;
        return new float[]{Mth.sin(a * 1.3F) * fuerza, Mth.sin(a * 1.7F + 1.0F) * fuerza * 0.8F, Mth.sin(a * 0.9F + 2.0F) * fuerza * 0.6F};
    }

    // ------------------------------------------------------------------
    //  El cielo maldito (lo pide CieloJefesMixin, despues del de los jefes)
    // ------------------------------------------------------------------

    /** Lo maldito que esta el cielo (0 a 1), con la parte del tick: SolMomentoMixin esconde con esto el sol y la luna. */
    public static float cielo(float parcial) {
        return fase == Fase.NADA ? 0.0F : Mth.clamp(Mth.lerp(parcial, cieloAntes, cielo), 0.0F, 1.0F);
    }

    public static boolean cieloActivo() {
        return fase != Fase.NADA && Math.max(cielo, cieloAntes) > 0.0F;
    }

    public static @Nullable Object mezclar(EnvironmentAttribute<?> atributo, Object valor) {
        float parcial = Minecraft.getInstance().getDeltaTracker().getGameTimeDeltaPartialTick(false);
        float k = Mth.clamp(Mth.lerp(parcial, cieloAntes, cielo), 0.0F, 1.0F);
        if (k <= 0.0F) {
            return null;
        }
        float late = latido(parcial) * k;
        if (atributo == EnvironmentAttributes.SKY_COLOR) {
            return rgb(rgb((Integer) valor, 0x24040A, k), 0x6A0A14, late * 0.6F);
        }
        if (atributo == EnvironmentAttributes.FOG_COLOR) {
            return rgb(rgb((Integer) valor, 0x30060C, k), 0x5A0A12, late * 0.5F);
        }
        if (atributo == EnvironmentAttributes.CLOUD_COLOR) {
            // Las nubes se van: oscuras, se veian por detras del cielo roto como barras de bloques (16-10-2026).
            int c = (Integer) valor;
            int al = (int) Mth.lerp(k, (c >>> 24) & 255, 0);
            return (al << 24) | (rgb(c, 0x3A0A0E, k) & 0xFFFFFF);
        }
        if (atributo == EnvironmentAttributes.SUNRISE_SUNSET_COLOR) {
            int c = (Integer) valor;
            int al = (int) Mth.lerp(k, (c >>> 24) & 255, 0xE8);
            return (al << 24) | (rgb(c, 0xB01418, k) & 0xFFFFFF);
        }
        if (atributo == EnvironmentAttributes.SKY_LIGHT_COLOR) {
            return rgb((Integer) valor, 0xFF6A60, k);
        }
        if (atributo == EnvironmentAttributes.SKY_LIGHT_FACTOR) {
            float f = (Float) valor;
            return Mth.clamp(Mth.lerp(k, f, f * (0.55F + 0.1F * late)), 0.0F, 1.0F);
        }
        if (atributo == EnvironmentAttributes.STAR_BRIGHTNESS) {
            return Math.max((Float) valor, 0.45F * k);
        }
        if (atributo == EnvironmentAttributes.FOG_START_DISTANCE) {
            float f = (Float) valor;
            return Mth.lerp(k, f, Math.min(f, 6.0F));
        }
        if (atributo == EnvironmentAttributes.FOG_END_DISTANCE) {
            float f = (Float) valor;
            return Mth.lerp(k, f, Math.min(f, 110.0F - 12.0F * late));
        }
        return null;
    }

    private static int rgb(int a, int b, float k) {
        k = Mth.clamp(k, 0.0F, 1.0F);
        int r = (int) Mth.lerp(k, (a >> 16) & 255, (b >> 16) & 255);
        int g = (int) Mth.lerp(k, (a >> 8) & 255, (b >> 8) & 255);
        int bl = (int) Mth.lerp(k, a & 255, b & 255);
        return (a & 0xFF000000) | (r << 16) | (g << 8) | bl;
    }

    // ------------------------------------------------------------------
    //  Particulas, sonidos y musica
    // ------------------------------------------------------------------

    private static void particulas(Minecraft mc, float k) {
        RandomSource r = mc.level.getRandom();
        Vec3 o = mc.gameRenderer.mainCamera().position();
        // A partir de 6 bloques: mas cerca, una mota se veia como una mancha enorme pegada a la camara (16-10-2026).
        for (int i = 0; i < Math.round(3 * k); i++) {
            poner(mc, r, AtalayaParticulas.MALDICION_MOTA, o, 6.0, 16.0, -2.0, 6.0, 0.0, 0.02, 0.0);
        }
        if (r.nextFloat() < 1.6F * k) {
            poner(mc, r, AtalayaParticulas.MALDICION_CENIZA, o, 5.0, 15.0, 4.0, 12.0, 0.0, -0.02, 0.0);
        }
    }

    /** La onda de la fractura en el mundo: un anillo de motas que sale de quien mira, a ras de suelo. */
    private static void onda(Minecraft mc) {
        Vec3 o = mc.player.position();
        for (int i = 0; i < 90; i++) {
            double a = i / 90.0 * Math.PI * 2;
            double v = 0.55 + 0.1 * Math.sin(i * 1.7);
            mc.level.addParticle(AtalayaParticulas.MALDICION_MOTA, o.x + Math.cos(a) * 1.2, o.y + 0.2, o.z + Math.sin(a) * 1.2,
                    Math.cos(a) * v, 0.02, Math.sin(a) * v);
        }
    }

    private static void poner(Minecraft mc, RandomSource r, net.minecraft.core.particles.SimpleParticleType tipo, Vec3 o,
                              double rMin, double rMax, double yMin, double yMax, double vx, double vy, double vz) {
        double a = r.nextDouble() * Math.PI * 2;
        double d = rMin + r.nextDouble() * (rMax - rMin);
        mc.level.addParticle(tipo, o.x + Math.cos(a) * d, o.y + yMin + r.nextDouble() * (yMax - yMin), o.z + Math.sin(a) * d,
                vx, vy, vz);
    }

    /** Un sonido sin posicion, igual en los dos oidos, en la categoria general (que lo oigan todos). */
    private static void sonar(Minecraft mc, SoundEvent evento, float volumen) {
        mc.getSoundManager().play(new SimpleSoundInstance(evento.location(), SoundSource.MASTER, volumen, 1.0F,
                SoundInstance.createUnseededRandom(), false, 0, SoundInstance.Attenuation.NONE, 0.0, 0.0, 0.0, true));
    }

    private static void empezarMusica(Minecraft mc, int funde) {
        if (musica != null && !musica.apagando) {
            return;
        }
        musica = new Pista(funde);
        mc.getMusicManager().stopPlaying();
        mc.getSoundManager().play(musica);
    }

    /**
     * La musica de los compañeros en bucle, sin posicion. Va en AMBIENTE, como
     * la de los jefes (muchos juegan con la musica quitada); entra y sale
     * fundiendose.
     */
    private static final class Pista extends AbstractTickableSoundInstance {

        boolean apagando;
        private final int entra;
        private int sale = 70;
        private float fundido;

        Pista(int entra) {
            super(AtalayaSonidos.MOMENTO_MUSICA, SoundSource.AMBIENT, SoundInstance.createUnseededRandom());
            this.entra = Math.max(1, entra);
            this.looping = true;
            this.delay = 0;
            this.volume = 0.001F;
            this.pitch = 1.0F;
            this.relative = true;
            this.attenuation = Attenuation.NONE;
        }

        void apagar(int ticks) {
            apagando = true;
            sale = Math.max(1, ticks);
        }

        @Override
        public boolean canStartSilent() {
            return true;
        }

        @Override
        public void tick() {
            fundido = apagando ? fundido - 1.0F / sale : Math.min(1.0F, fundido + 1.0F / entra);
            if (fundido <= 0.0F) {
                stop();
                return;
            }
            volume = Math.max(0.001F, fundido * fundido * 0.9F);
        }
    }
}
