package com.atalaya.client;

import com.atalaya.particula.AtalayaParticulas;
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
 * Las particulas de los cuatro mini jefes en una clase (sprites de
 * minijefes_extras.py): cada {@link Tipo} cambia como se mueve y como se dibuja.
 *
 * Las de suelo (la marca, la onda y la grieta) van tumbadas; la onda sacude la
 * camara de quien este cerca y toma el color de su elemento (la Z), igual que el
 * destello. Las que son luz (jade, runas, brasas, llamas, plumas de fuego,
 * fragmentos y las de suelo) no se oscurecen de noche. Las astillas, las gotas y
 * las esquirlas caen con su peso y rebotan.
 */
public class MiniJefeParticula extends SingleQuadParticle {

    private static final int A_PLENA_LUZ = 0xF000F0;
    /** El color de cada elemento (onda y destello): tierra (jade), viento, agua y fuego. */
    private static final float[][] ELEMENTOS = {{0.45F, 1.0F, 0.66F}, {0.78F, 0.96F, 1.0F}, {0.5F, 0.92F, 1.0F},
            {1.0F, 0.62F, 0.22F}};

    public enum Tipo {
        JADE, OBSIDIANA, POLVO, PLUMA, FRAGMENTO, MARCA, ONDA, VIENTO, RUNA, GOTA, ESPUMA, BURBUJA, BRASA, LLAMA,
        PLUMA_FUEGO, CENIZA, DESTELLO, GRIETA
    }

    private final Tipo tipo;
    private final SpriteSet sprites;
    private final float tamanoInicial;
    private final float fase;
    private float giro;
    private float radioFinal;

    protected MiniJefeParticula(ClientLevel nivel, double x, double y, double z, double vx, double vy, double vz,
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
        switch (tipo) {
            case JADE -> {
                this.lifetime = 26 + r.nextInt(16);
                this.quadSize = 0.07F + r.nextFloat() * 0.09F;
                this.gravity = 0.7F;
                this.friction = 0.97F;
                this.hasPhysics = true;
                this.giro = (r.nextFloat() - 0.5F) * 0.5F;
                setSprite(sprites.get(r));
            }
            case OBSIDIANA -> {
                this.lifetime = 30 + r.nextInt(22);
                this.quadSize = 0.1F + r.nextFloat() * 0.12F;
                this.gravity = 0.95F;
                this.friction = 0.98F;
                this.hasPhysics = true;
                this.giro = (r.nextFloat() - 0.5F) * 0.45F;
                setSprite(sprites.get(r));
            }
            case POLVO -> {
                this.lifetime = 24 + r.nextInt(16);
                this.quadSize = 0.4F + r.nextFloat() * 0.45F;
                this.friction = 0.88F;
                this.giro = (r.nextFloat() - 0.5F) * 0.05F;
            }
            case PLUMA -> {
                this.lifetime = 70 + r.nextInt(40);
                this.quadSize = 0.16F + r.nextFloat() * 0.1F;
                this.gravity = 0.03F;
                this.friction = 0.96F;
                this.giro = (r.nextFloat() - 0.5F) * 0.15F;
                setSprite(sprites.get(r));
            }
            case FRAGMENTO -> {
                this.lifetime = 16;
                this.quadSize = 0.55F + r.nextFloat() * 0.2F;
                this.friction = 1.0F;
                this.giro = (r.nextFloat() - 0.5F) * 0.3F;
                setSprite(sprites.get(r));
            }
            case MARCA -> {
                // vx: radio; vy: ticks.
                this.radioFinal = (float) Math.max(0.5, vx);
                this.lifetime = vy > 0 ? (int) vy : 30;
                this.quadSize = 0.2F;
                quieta();
                this.roll = r.nextFloat() * Mth.TWO_PI;
                this.oRoll = this.roll;
                this.giro = 0.03F;
            }
            case ONDA -> {
                // vx: fuerza del temblor; vy: radio final; vz: elemento.
                NereaPresencia.sacudir(x, y, z, (float) vx, 26.0F + (float) vy * 3.0F);
                this.radioFinal = (float) Math.max(1.0, vy);
                this.lifetime = 12 + (int) (vy * 0.7);
                this.quadSize = 0.4F;
                color((int) vz);
                quieta();
                this.roll = r.nextFloat() * Mth.TWO_PI;
                this.oRoll = this.roll;
            }
            case VIENTO -> {
                this.lifetime = 14 + r.nextInt(10);
                this.quadSize = 0.3F + r.nextFloat() * 0.35F;
                this.friction = 0.93F;
                this.giro = (r.nextFloat() - 0.5F) * 0.3F;
            }
            case RUNA -> {
                this.lifetime = 20 + r.nextInt(14);
                this.quadSize = 0.14F + r.nextFloat() * 0.1F;
                this.friction = 0.9F;
                setSprite(sprites.get(r));
            }
            case GOTA -> {
                this.lifetime = 22 + r.nextInt(14);
                this.quadSize = 0.06F + r.nextFloat() * 0.07F;
                this.gravity = 0.85F;
                this.friction = 0.98F;
                this.hasPhysics = true;
                setSprite(sprites.get(r));
            }
            case ESPUMA -> {
                this.lifetime = 18 + r.nextInt(12);
                this.quadSize = 0.3F + r.nextFloat() * 0.35F;
                this.friction = 0.9F;
                this.giro = (r.nextFloat() - 0.5F) * 0.08F;
            }
            case BURBUJA -> {
                this.lifetime = 30 + r.nextInt(20);
                this.quadSize = 0.07F + r.nextFloat() * 0.1F;
                this.friction = 0.92F;
            }
            case BRASA -> {
                this.lifetime = 24 + r.nextInt(20);
                this.quadSize = 0.05F + r.nextFloat() * 0.06F;
                this.friction = 0.95F;
            }
            case LLAMA -> {
                this.lifetime = 10 + r.nextInt(9);
                this.quadSize = 0.25F + r.nextFloat() * 0.3F;
                this.friction = 0.9F;
                this.giro = (r.nextFloat() - 0.5F) * 0.25F;
            }
            case PLUMA_FUEGO -> {
                this.lifetime = 50 + r.nextInt(30);
                this.quadSize = 0.2F + r.nextFloat() * 0.1F;
                this.gravity = 0.04F;
                this.friction = 0.95F;
                this.giro = (r.nextFloat() - 0.5F) * 0.2F;
                setSprite(sprites.get(r));
            }
            case CENIZA -> {
                this.lifetime = 60 + r.nextInt(30);
                this.quadSize = 0.06F + r.nextFloat() * 0.05F;
                this.gravity = 0.015F;
                this.friction = 0.96F;
                this.giro = (r.nextFloat() - 0.5F) * 0.1F;
                setSprite(sprites.get(r));
            }
            case DESTELLO -> {
                // vx: tamano; vz: elemento.
                this.lifetime = 7;
                this.quadSize = (float) Math.max(0.5, vx);
                color((int) vz);
                quieta();
            }
            case GRIETA -> {
                // vx: tamano; vy: ticks; vz: giro (radianes).
                this.radioFinal = (float) Math.max(0.5, vx);
                this.lifetime = vy > 0 ? (int) vy : 40;
                this.quadSize = this.radioFinal;
                quieta();
                this.roll = (float) vz;
                this.oRoll = this.roll;
            }
        }
        this.tamanoInicial = this.quadSize;
        if (tipo == Tipo.POLVO || tipo == Tipo.ONDA || tipo == Tipo.VIENTO || tipo == Tipo.ESPUMA || tipo == Tipo.BRASA
                || tipo == Tipo.LLAMA || tipo == Tipo.DESTELLO || tipo == Tipo.BURBUJA) {
            setSpriteFromAge(sprites);
        }
    }

    private void color(int elemento) {
        float[] c = ELEMENTOS[Mth.clamp(elemento, 0, ELEMENTOS.length - 1)];
        setColor(c[0], c[1], c[2]);
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
        return switch (tipo) {
            case JADE, FRAGMENTO, MARCA, ONDA, RUNA, BRASA, LLAMA, PLUMA_FUEGO, DESTELLO, GRIETA -> A_PLENA_LUZ;
            default -> super.getLightCoords(parcial);
        };
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += giro;
        float vida = this.age / (float) this.lifetime;
        switch (tipo) {
            case POLVO, ESPUMA -> {
                this.quadSize = tamanoInicial * (1.0F + 1.3F * vida);
                this.yd += tipo == Tipo.POLVO ? 0.002 : 0.004;
                setSpriteFromAge(sprites);
            }
            case JADE, OBSIDIANA, GOTA -> {
                if (this.onGround) {
                    this.xd *= 0.6;
                    this.zd *= 0.6;
                    this.giro *= 0.6F;
                }
            }
            case PLUMA, PLUMA_FUEGO, CENIZA -> {
                // Cae meciendose, como una pluma de verdad.
                this.xd += Mth.sin(this.age * 0.16F + fase) * 0.004;
                this.zd += Mth.cos(this.age * 0.13F + fase) * 0.004;
                if (tipo == Tipo.PLUMA_FUEGO && this.age % 3 == 0) {
                    this.level.addParticle(AtalayaParticulas.MJ_BRASA, this.x, this.y, this.z,
                            (this.random.nextFloat() - 0.5F) * 0.02, 0.03, (this.random.nextFloat() - 0.5F) * 0.02);
                }
            }
            case FRAGMENTO -> {
                // Deja una estela de jade al caer.
                this.level.addParticle(AtalayaParticulas.MJ_JADE, this.x, this.y + 0.3, this.z,
                        (this.random.nextFloat() - 0.5F) * 0.1, 0.05, (this.random.nextFloat() - 0.5F) * 0.1);
            }
            case MARCA -> {
                float k = Mth.clamp(this.age / 6.0F, 0.0F, 1.0F);
                this.quadSize = this.radioFinal * (1.0F - (1.0F - k) * (1.0F - k));
                setSprite(sprites.get((this.age / 4) % 2, 1));
            }
            case ONDA -> {
                float k = 1.0F - (1.0F - vida) * (1.0F - vida);
                this.quadSize = 0.4F + this.radioFinal * k;
                setSpriteFromAge(sprites);
            }
            case VIENTO -> {
                this.quadSize = tamanoInicial * (1.0F + 0.8F * vida);
                setSpriteFromAge(sprites);
            }
            case RUNA -> this.yd += 0.004;
            case BURBUJA -> {
                this.yd += 0.012;
                this.xd += Mth.sin(this.age * 0.4F + fase) * 0.003;
                setSpriteFromAge(sprites);
            }
            case BRASA -> {
                this.yd += 0.003;
                this.xd += Mth.sin(this.age * 0.3F + fase) * 0.002;
                setSpriteFromAge(sprites);
            }
            case LLAMA -> {
                this.quadSize = tamanoInicial * (1.0F - 0.55F * vida);
                this.yd += 0.007;
                setSpriteFromAge(sprites);
            }
            case DESTELLO -> {
                this.quadSize = tamanoInicial * (0.7F + 0.6F * vida);
                setSpriteFromAge(sprites);
            }
            case GRIETA -> setSprite(sprites.get(Math.min(this.age, 4), 4));
        }
        switch (tipo) {
            case ONDA, DESTELLO -> this.alpha = 1.0F - vida;
            case MARCA, GRIETA -> {
                float entra = Mth.clamp(this.age / 4.0F, 0.0F, 1.0F);
                float sale = Mth.clamp((this.lifetime - this.age) / 10.0F, 0.0F, 1.0F);
                float late = tipo == Tipo.MARCA ? 0.8F + 0.2F * Mth.sin(this.age * 0.7F) : 1.0F;
                this.alpha = entra * sale * late;
            }
            case BRASA -> this.alpha = (vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F) * (0.75F + 0.25F * Mth.sin(this.age * 1.3F + fase));
            default -> this.alpha = vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F;
        }
        super.tick();
    }

    @Override
    public void extract(QuadParticleRenderState estado, Camera camara, float parcial) {
        switch (tipo) {
            case ONDA, MARCA, GRIETA -> {
                // Tumbadas en el suelo, vistas por las dos caras.
                float r = Mth.lerp(parcial, this.oRoll, this.roll);
                extractRotatedQuad(estado, camara, new Quaternionf().rotationX(-Mth.HALF_PI).rotateZ(r), parcial);
                extractRotatedQuad(estado, camara, new Quaternionf().rotationX(Mth.HALF_PI).rotateZ(-r), parcial);
            }
            default -> super.extract(estado, camara, parcial);
        }
    }

    public record Fabrica(SpriteSet sprites, Tipo tipo) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipoParticula, ClientLevel nivel,
                                       double x, double y, double z, double vx, double vy, double vz,
                                       RandomSource azar) {
            return new MiniJefeParticula(nivel, x, y, z, vx, vy, vz, tipo, sprites);
        }
    }
}
