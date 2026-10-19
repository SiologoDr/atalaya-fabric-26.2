package com.atalaya.client.bestiario;

import com.atalaya.bestiario.Bestia;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.renderer.state.level.QuadParticleRenderState;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import org.joml.Quaternionf;

/**
 * Las particulas de los mobs del bestiario (sprites de bestiario_juego.py, los suyos de cada mob): como se mueven lo dice
 * su {@link Bestia.Vuelo}. Las que son luz no se oscurecen de noche.
 *
 * <pre>
 *   CAE        cae con su peso y rebota (astillas, gotas, escamas); la velocidad es la del golpe
 *   SUBE       sube despacio meciendose y se apaga (chispas, esporas, ceniza encendida)
 *   FLOTA      flota casi quieta, crece un poco y se desvanece (polvo, humo, niebla)
 *   DERIVA     pequena: deriva meciendose y cae poco a poco (petalos, ceniza, chispas)
 *   ESTALLA    sale disparada y frena en seco (el estallido)
 *   SUELO      tumbada en el suelo, crece hasta su tamano y se apaga; vx es el tamano y vy los ticks
 *   DESTELLO   un fogonazo quieto que crece y se va en unos ticks; vx es el tamano
 * </pre>
 */
public class BestiaParticula extends SingleQuadParticle {

    private static final int A_PLENA_LUZ = 0xF000F0;

    private final Bestia.Vuelo vuelo;
    private final boolean luz;
    private final SpriteSet sprites;
    private final float tamanoInicial;
    private final float fase;
    private float giro;
    private float radioFinal;

    protected BestiaParticula(ClientLevel nivel, double x, double y, double z, double vx, double vy, double vz,
                              Bestia.Vuelo vuelo, boolean luz, SpriteSet sprites) {
        super(nivel, x, y, z, sprites.first());
        this.vuelo = vuelo;
        this.luz = luz;
        this.sprites = sprites;
        RandomSource r = this.random;
        this.fase = r.nextFloat() * Mth.TWO_PI;
        this.hasPhysics = false;
        this.gravity = 0.0F;
        this.friction = 0.95F;
        this.xd = vx;
        this.yd = vy;
        this.zd = vz;
        setSprite(sprites.get(r));
        switch (vuelo) {
            case CAE -> {
                this.lifetime = 26 + r.nextInt(18);
                this.quadSize = 0.06F + r.nextFloat() * 0.08F;
                this.gravity = 0.8F;
                this.friction = 0.97F;
                this.hasPhysics = true;
                this.giro = (r.nextFloat() - 0.5F) * 0.5F;
            }
            case SUBE -> {
                this.lifetime = 30 + r.nextInt(24);
                this.quadSize = 0.05F + r.nextFloat() * 0.07F;
                this.friction = 0.94F;
                this.giro = (r.nextFloat() - 0.5F) * 0.1F;
            }
            case FLOTA -> {
                this.lifetime = 34 + r.nextInt(26);
                this.quadSize = 0.25F + r.nextFloat() * 0.3F;
                this.friction = 0.9F;
                this.giro = (r.nextFloat() - 0.5F) * 0.04F;
            }
            case DERIVA -> {
                this.lifetime = 40 + r.nextInt(30);
                this.quadSize = 0.05F + r.nextFloat() * 0.06F;
                this.gravity = 0.06F;
                this.friction = 0.95F;
                this.giro = (r.nextFloat() - 0.5F) * 0.15F;
            }
            case ESTALLA -> {
                this.lifetime = 12 + r.nextInt(10);
                this.quadSize = 0.1F + r.nextFloat() * 0.12F;
                this.friction = 0.82F;
                this.giro = (r.nextFloat() - 0.5F) * 0.4F;
            }
            case SUELO -> {
                this.radioFinal = (float) Math.max(0.4, vx);
                this.lifetime = vy > 0 ? (int) vy : 40;
                this.quadSize = 0.2F;
                quieta();
                this.roll = r.nextFloat() * Mth.TWO_PI;
                this.oRoll = this.roll;
            }
            case DESTELLO -> {
                this.lifetime = 7;
                this.quadSize = (float) Math.max(0.4, vx);
                quieta();
            }
        }
        this.tamanoInicial = this.quadSize;
    }

    private void quieta() {
        this.xd = 0.0;
        this.yd = 0.0;
        this.zd = 0.0;
        this.friction = 1.0F;
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    @Override
    protected int getLightCoords(float parcial) {
        return luz ? A_PLENA_LUZ : super.getLightCoords(parcial);
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += giro;
        float vida = this.age / (float) this.lifetime;
        switch (vuelo) {
            case CAE -> {
                if (this.onGround) {
                    this.xd *= 0.6;
                    this.zd *= 0.6;
                    this.giro *= 0.6F;
                }
            }
            case SUBE -> {
                this.yd += 0.003;
                this.xd += Mth.sin(this.age * 0.3F + fase) * 0.002;
                this.zd += Mth.cos(this.age * 0.27F + fase) * 0.002;
            }
            case FLOTA -> {
                this.quadSize = tamanoInicial * (1.0F + 0.9F * vida);
                this.yd += 0.0015;
            }
            case DERIVA -> {
                this.xd += Mth.sin(this.age * 0.2F + fase) * 0.004;
                this.zd += Mth.cos(this.age * 0.23F + fase) * 0.004;
            }
            case ESTALLA -> this.quadSize = tamanoInicial * (1.0F - 0.5F * vida);
            case SUELO -> {
                float k = Mth.clamp(this.age / 6.0F, 0.0F, 1.0F);
                this.quadSize = this.radioFinal * (1.0F - (1.0F - k) * (1.0F - k));
            }
            case DESTELLO -> this.quadSize = tamanoInicial * (0.7F + 0.6F * vida);
        }
        switch (vuelo) {
            case DESTELLO -> this.alpha = 1.0F - vida;
            case SUELO -> {
                float entra = Mth.clamp(this.age / 4.0F, 0.0F, 1.0F);
                float sale = Mth.clamp((this.lifetime - this.age) / 10.0F, 0.0F, 1.0F);
                this.alpha = entra * sale;
            }
            default -> this.alpha = vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F;
        }
        super.tick();
    }

    @Override
    public void extract(QuadParticleRenderState estado, Camera camara, float parcial) {
        if (vuelo == Bestia.Vuelo.SUELO) {
            // Tumbada en el suelo, vista por las dos caras.
            float r = Mth.lerp(parcial, this.oRoll, this.roll);
            extractRotatedQuad(estado, camara, new Quaternionf().rotationX(-Mth.HALF_PI).rotateZ(r), parcial);
            extractRotatedQuad(estado, camara, new Quaternionf().rotationX(Mth.HALF_PI).rotateZ(-r), parcial);
        } else {
            super.extract(estado, camara, parcial);
        }
    }

    public record Fabrica(SpriteSet sprites, Bestia.Vuelo vuelo, boolean luz) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipoParticula, ClientLevel nivel, double x, double y, double z,
                                       double vx, double vy, double vz, RandomSource azar) {
            return new BestiaParticula(nivel, x, y, z, vx, vy, vz, vuelo, luz, sprites);
        }
    }
}
