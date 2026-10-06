package com.atalaya.client;

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
 * Las once particulas de Novilis, el Caballero Solar, en una clase (sprites de
 * novilis_extras.py): cada {@link Tipo} cambia como se mueve y como se dibuja.
 *
 * La onda va tumbada en el suelo y, al nacer, sacude la camara de quien este
 * cerca, como las de Nerea y Rajang: lleva la fuerza del temblor en la
 * velocidad X y el radio final en la Y (se manda con count 0 y speed 1).
 * Las que son fuego o luz (brasa, chispa, llama, onda, nota, luz y las
 * lenguas azul y carmesi) no se oscurecen de noche; la ceniza, el humo y el
 * basalto, si. El basalto cae con su peso y rebota una vez.
 */
public class NovilisParticula extends SingleQuadParticle {

    private static final int A_PLENA_LUZ = 0xF000F0;

    public enum Tipo {
        BRASA, CHISPA, CENIZA, LLAMA, HUMO, ONDA, ROCA, NOTA, LUZ, AZUL, CARMESI
    }

    private final Tipo tipo;
    private final SpriteSet sprites;
    private final float tamanoInicial;
    private final float fase;
    private float giro;
    /** Solo la onda: hasta que radio crece (en bloques). */
    private float radioFinal;
    /** Solo el basalto: si ya ha rebotado (rebota una vez y luego se queda). */
    private boolean rebotado;

    protected NovilisParticula(ClientLevel nivel, double x, double y, double z, double vx, double vy, double vz,
                               Tipo tipo, SpriteSet sprites) {
        super(nivel, x, y, z, sprites.first());
        this.tipo = tipo;
        this.sprites = sprites;
        RandomSource r = this.random;
        this.fase = r.nextFloat() * Mth.TWO_PI;
        this.hasPhysics = false;
        this.gravity = 0.0F;
        this.friction = 0.95F;
        this.xd = vx;
        this.yd = vy;
        this.zd = vz;
        float giroInicial = 0.0F;
        switch (tipo) {
            case BRASA -> {
                // Sube despacio, con algo de deriva; el parpadeo va en tick().
                this.lifetime = 30 + r.nextInt(25);
                this.quadSize = 0.05F + r.nextFloat() * 0.06F;
                this.friction = 0.96F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.02;
                this.yd = Math.max(vy, 0.0) + 0.02 + r.nextFloat() * 0.03;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.02;
            }
            case CHISPA -> {
                // Un chispazo: sale disparada, cae con su peso y dura poco.
                this.lifetime = 8 + r.nextInt(7);
                this.quadSize = 0.07F + r.nextFloat() * 0.05F;
                this.hasPhysics = true;
                this.gravity = 1.0F;
                this.friction = 0.92F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.35;
                this.yd = vy + 0.12 + r.nextFloat() * 0.18;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.35;
            }
            case CENIZA -> {
                // Cae muy despacio, girando y meciendose.
                this.lifetime = 60 + r.nextInt(50);
                this.quadSize = 0.06F + r.nextFloat() * 0.06F;
                this.gravity = 0.015F;
                this.friction = 0.97F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.12F;
                setSprite(sprites.get(r));
            }
            case LLAMA, AZUL, CARMESI -> {
                // Una bocanada (o una lengua) que sube y se encoge.
                this.lifetime = 14 + r.nextInt(8);
                this.quadSize = tipo == Tipo.LLAMA ? 0.3F + r.nextFloat() * 0.35F : 0.2F + r.nextFloat() * 0.25F;
                this.friction = 0.9F;
                this.yd = vy + (tipo == Tipo.LLAMA ? 0.02 : 0.03);
                giroInicial = (r.nextFloat() - 0.5F) * 0.08F;
            }
            case HUMO -> {
                this.lifetime = 40 + r.nextInt(30);
                this.quadSize = 0.35F + r.nextFloat() * 0.4F;
                this.friction = 0.92F;
                this.yd = Math.max(vy, 0.0) + 0.015;
                giroInicial = (r.nextFloat() - 0.5F) * 0.04F;
            }
            case ONDA -> {
                // vx: fuerza del temblor; vy: radio final. Sacude la camara de quien este cerca.
                NereaPresencia.sacudir(x, y, z, (float) vx, 28.0F + (float) vy * 3.0F);
                this.radioFinal = (float) Math.max(1.0, vy);
                this.lifetime = 12 + (int) (vy * 0.7);
                this.quadSize = 0.4F;
                quieta();
                this.friction = 1.0F;
            }
            case ROCA -> {
                this.lifetime = 40 + r.nextInt(25);
                this.quadSize = 0.1F + r.nextFloat() * 0.14F;
                this.gravity = 1.0F;
                this.friction = 0.98F;
                this.hasPhysics = true;
                giroInicial = (r.nextFloat() - 0.5F) * 0.4F;
                setSprite(sprites.get(r));
            }
            case NOTA -> {
                // Sube flotando y se mece; el balanceo va en tick().
                this.lifetime = 40 + r.nextInt(25);
                this.quadSize = 0.22F + r.nextFloat() * 0.1F;
                this.friction = 0.94F;
                this.yd = Math.max(vy, 0.02 + r.nextFloat() * 0.02);
                setSprite(sprites.get(r));
            }
            case LUZ -> {
                this.lifetime = 50 + r.nextInt(30);
                this.quadSize = 0.08F + r.nextFloat() * 0.05F;
                this.friction = 0.97F;
                this.yd = Math.max(vy, 0.015 + r.nextFloat() * 0.02);
            }
        }
        this.tamanoInicial = this.quadSize;
        this.giro = giroInicial;
        switch (tipo) {
            case BRASA -> setSprite(sprites.get(0, 2));
            case CHISPA, LLAMA, AZUL, CARMESI, HUMO, ONDA, LUZ -> setSpriteFromAge(sprites);
            default -> {
            }
        }
    }

    private void quieta() {
        this.xd = 0.0;
        this.yd = 0.0;
        this.zd = 0.0;
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    @Override
    protected int getLightCoords(float parcial) {
        return switch (tipo) {
            case CENIZA, HUMO, ROCA -> super.getLightCoords(parcial);
            default -> A_PLENA_LUZ;
        };
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += giro;
        float vida = this.age / (float) this.lifetime;
        switch (tipo) {
            case BRASA -> {
                this.xd += Mth.sin(this.age * 0.3F + fase) * 0.003;
                this.zd += Mth.cos(this.age * 0.27F + fase) * 0.003;
                this.yd += 0.001;
                // Parpadea: cuando baja, se enrojece y pasa al fotograma pequeno.
                float brillo = 0.75F + 0.25F * Mth.sin(this.age * 1.7F + fase) * Mth.sin(this.age * 0.9F + fase * 2.0F);
                setColor(1.0F, 0.7F + 0.3F * brillo, 0.45F + 0.55F * brillo);
                setSprite(sprites.get(vida > 0.75F ? 2 : brillo > 0.8F ? 0 : 1, 2));
            }
            case CHISPA -> {
                this.quadSize = tamanoInicial * (1.0F - 0.6F * vida);
                setSpriteFromAge(sprites);
            }
            case CENIZA -> {
                this.xd += Mth.sin(this.age * 0.12F + fase) * 0.003;
                this.zd += Mth.cos(this.age * 0.1F + fase) * 0.003;
            }
            case LLAMA, AZUL, CARMESI -> {
                this.quadSize = tamanoInicial * (1.0F - 0.5F * vida);
                this.yd += 0.004;
                setSpriteFromAge(sprites);
            }
            case HUMO -> {
                this.quadSize = tamanoInicial * (1.0F + 1.6F * vida);
                this.yd += 0.001;
                setSpriteFromAge(sprites);
            }
            case ONDA -> {
                // Se abre rapido al principio y frena, como una onda de verdad.
                float k = 1.0F - (1.0F - vida) * (1.0F - vida);
                this.quadSize = 0.4F + this.radioFinal * k;
                setSpriteFromAge(sprites);
            }
            case ROCA -> {
                if (this.rebotado && this.onGround) {
                    this.giro = 0.0F;
                }
            }
            case NOTA -> {
                this.xd += Mth.sin(this.age * 0.18F + fase) * 0.004;
                this.zd += Mth.cos(this.age * 0.16F + fase) * 0.004;
                this.roll = 0.3F * Mth.sin(this.age * 0.2F + fase);
            }
            case LUZ -> {
                this.xd += Mth.sin(this.age * 0.2F + fase) * 0.003;
                this.zd += Mth.cos(this.age * 0.17F + fase) * 0.003;
                setSprite(sprites.get((this.age / 4) % 3, 2));
            }
        }
        switch (tipo) {
            case ONDA -> this.alpha = 1.0F - vida;
            case NOTA, LUZ -> this.alpha = Mth.clamp(this.age / 4.0F, 0.0F, 1.0F)
                    * (vida < 0.7F ? 1.0F : 1.0F - (vida - 0.7F) / 0.3F);
            case HUMO -> this.alpha = 0.85F * (vida < 0.4F ? 1.0F : 1.0F - (vida - 0.4F) / 0.6F);
            default -> this.alpha = vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F;
        }
        super.tick();
        if (tipo == Tipo.ROCA && !this.rebotado && this.onGround) {
            // El primer golpe contra el suelo: rebota con algo menos de la mitad
            // de lo que caia y se frena de lado. El segundo ya lo para el juego.
            this.rebotado = true;
            this.yd = Math.abs(this.yd) * 0.45;
            this.xd *= 0.6;
            this.zd *= 0.6;
            this.giro *= 0.5F;
        }
    }

    /** La onda va tumbada en el suelo y se ve por las dos caras; el resto, de cara a la camara. */
    @Override
    public void extract(QuadParticleRenderState estado, Camera camara, float parcial) {
        if (tipo != Tipo.ONDA) {
            super.extract(estado, camara, parcial);
            return;
        }
        extractRotatedQuad(estado, camara, new Quaternionf().rotationX(-Mth.HALF_PI), parcial);
        extractRotatedQuad(estado, camara, new Quaternionf().rotationX(Mth.HALF_PI), parcial);
    }

    public record Fabrica(SpriteSet sprites, Tipo tipo) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipoParticula, ClientLevel nivel,
                                       double x, double y, double z, double vx, double vy, double vz,
                                       RandomSource azar) {
            return new NovilisParticula(nivel, x, y, z, vx, vy, vz, tipo, sprites);
        }
    }
}
