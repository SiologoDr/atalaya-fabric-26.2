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
 * Las quince particulas de Rajang en una clase (sprites de rajang_extras.py):
 * cada {@link Tipo} cambia como se mueve y como se dibuja.
 *
 * Las de suelo (la onda, la grieta, el aviso, la marca del Cataclismo, el
 * circulo del Sello y el lastre) van tumbadas y reciben su tamano en la X y
 * los ticks que duran en la Y; la onda sacude la camara de quien este cerca.
 * Las que son luz (chispa, llama, runa, oro y las de suelo) no se oscurecen de
 * noche. Las piedras y las astillas caen con su peso y rebotan.
 */
public class RajangParticula extends SingleQuadParticle {

    private static final int A_PLENA_LUZ = 0xF000F0;

    public enum Tipo {
        POLVO, ROCA, JADE, CHISPA, HOJA, ONDA, GRIETA, AVISO, MARCA, SELLO, RUNA, LLAMA, LASTRE, ORO, ZARPAZO
    }

    private final Tipo tipo;
    private final SpriteSet sprites;
    private final float tamanoInicial;
    private final float giro;
    private final float fase;
    /** Las de suelo: hasta que radio llegan (bloques). */
    private float radioFinal;
    /** El zarpazo tumbado: las marcas de las garras en el suelo. */
    private boolean enSuelo;

    protected RajangParticula(ClientLevel nivel, double x, double y, double z, double vx, double vy, double vz,
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
            case POLVO -> {
                this.lifetime = 22 + r.nextInt(18);
                this.quadSize = 0.35F + r.nextFloat() * 0.4F;
                this.friction = 0.9F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.06F;
            }
            case ROCA -> {
                this.lifetime = 30 + r.nextInt(25);
                this.quadSize = 0.1F + r.nextFloat() * 0.16F;
                this.gravity = 0.9F;
                this.friction = 0.98F;
                this.hasPhysics = true;
                giroInicial = (r.nextFloat() - 0.5F) * 0.4F;
                setSprite(sprites.get(r));
            }
            case JADE -> {
                this.lifetime = 24 + r.nextInt(18);
                this.quadSize = 0.07F + r.nextFloat() * 0.09F;
                this.gravity = 0.6F;
                this.friction = 0.97F;
                this.hasPhysics = true;
                giroInicial = (r.nextFloat() - 0.5F) * 0.5F;
                setSprite(sprites.get(r));
            }
            case CHISPA -> {
                this.lifetime = 20 + r.nextInt(22);
                this.quadSize = 0.06F + r.nextFloat() * 0.07F;
                this.friction = 0.96F;
            }
            case HOJA -> {
                // Cae revoloteando, como una hoja de la selva.
                this.lifetime = 80 + r.nextInt(50);
                this.quadSize = 0.11F + r.nextFloat() * 0.08F;
                this.gravity = 0.02F;
                this.friction = 0.97F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.2F;
                setSprite(sprites.get(r));
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
            case GRIETA, AVISO, MARCA, SELLO, LASTRE -> {
                // vx: radio; vy: ticks que dura.
                this.radioFinal = (float) Math.max(0.5, vx);
                this.lifetime = vy > 0 ? (int) vy : 40;
                this.quadSize = tipo == Tipo.MARCA || tipo == Tipo.GRIETA ? this.radioFinal : 0.2F;
                quieta();
                this.friction = 1.0F;
                this.roll = r.nextFloat() * Mth.TWO_PI;
                this.oRoll = this.roll;
                giroInicial = tipo == Tipo.SELLO ? 0.004F : tipo == Tipo.MARCA ? 0.02F : 0.0F;
            }
            case RUNA -> {
                this.lifetime = 18 + r.nextInt(14);
                this.quadSize = 0.14F + r.nextFloat() * 0.08F;
                this.friction = 0.9F;
                setSprite(sprites.get(r));
            }
            case LLAMA -> {
                this.lifetime = 10 + r.nextInt(10);
                this.quadSize = 0.22F + r.nextFloat() * 0.25F;
                this.friction = 0.9F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.2F;
            }
            case ORO -> {
                this.lifetime = 30 + r.nextInt(25);
                this.quadSize = 0.06F + r.nextFloat() * 0.06F;
                this.friction = 0.96F;
            }
            case ZARPAZO -> {
                // vx: tamano en bloques; vy: ticks; vz: giro (radianes), de cara a quien mira.
                // Con vz >= 50, tumbado en el suelo (las marcas de las garras) y girado vz - 100.
                this.lifetime = vy > 0 ? (int) vy : 8;
                this.quadSize = (float) Math.max(1.0, vx) * 0.5F;
                this.enSuelo = vz >= 50.0;
                quieta();
                this.friction = 1.0F;
                this.roll = (float) (enSuelo ? vz - 100.0 : vz);
                this.oRoll = this.roll;
            }
        }
        this.tamanoInicial = this.quadSize;
        this.giro = giroInicial;
        if (tipo == Tipo.POLVO || tipo == Tipo.CHISPA || tipo == Tipo.LLAMA || tipo == Tipo.ORO || tipo == Tipo.ONDA
                || tipo == Tipo.MARCA || tipo == Tipo.ZARPAZO) {
            setSpriteFromAge(sprites);
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
            case CHISPA, LLAMA, RUNA, ORO, ONDA, GRIETA, AVISO, MARCA, SELLO, LASTRE, ZARPAZO -> A_PLENA_LUZ;
            default -> super.getLightCoords(parcial);
        };
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += giro;
        float vida = this.age / (float) this.lifetime;
        switch (tipo) {
            case POLVO -> {
                this.quadSize = tamanoInicial * (1.0F + 1.4F * vida);
                this.yd += 0.002;
                setSpriteFromAge(sprites);
            }
            case ROCA, JADE -> {
                if (this.onGround) {
                    this.giroParado();
                }
            }
            case CHISPA -> {
                this.yd += 0.002;
                setSpriteFromAge(sprites);
            }
            case HOJA -> {
                this.xd += Mth.sin(this.age * 0.15F + fase) * 0.004;
                this.zd += Mth.cos(this.age * 0.13F + fase) * 0.004;
            }
            case ONDA -> {
                float k = 1.0F - (1.0F - vida) * (1.0F - vida);
                this.quadSize = 0.4F + this.radioFinal * k;
                setSpriteFromAge(sprites);
            }
            case GRIETA -> setSprite(sprites.get(Math.min(this.age, 6), 6));
            case AVISO, LASTRE -> {
                float k = Mth.clamp(this.age / 6.0F, 0.0F, 1.0F);
                this.quadSize = this.radioFinal * (1.0F - (1.0F - k) * (1.0F - k));
                setSprite(sprites.get((this.age / 5) % 2, 1));
            }
            case MARCA -> setSpriteFromAge(sprites);
            case SELLO -> {
                float k = Mth.clamp(this.age / 14.0F, 0.0F, 1.0F);
                this.quadSize = this.radioFinal * (1.0F - (1.0F - k) * (1.0F - k));
                setSprite(sprites.get((this.age / 10) % 2, 1));
            }
            case RUNA -> this.yd += 0.003;
            case LLAMA -> {
                this.quadSize = tamanoInicial * (1.0F - 0.6F * vida);
                this.yd += 0.006;
                setSpriteFromAge(sprites);
            }
            case ORO -> setSprite(sprites.get((this.age / 4) % 3, 2));
            case ZARPAZO -> {
                if (enSuelo) {
                    // Las marcas: se abren de golpe y se quedan hasta apagarse.
                    setSprite(sprites.get(this.age < 2 ? 0 : this.age < this.lifetime - 10 ? 1 : 2, 2));
                } else {
                    // Sale de golpe un poco pequeno, se abre y se deshace.
                    this.quadSize = tamanoInicial * (0.82F + 0.18F * Mth.clamp(this.age / 2.0F, 0.0F, 1.0F));
                    setSpriteFromAge(sprites);
                }
            }
        }
        switch (tipo) {
            case ONDA -> this.alpha = 1.0F - vida;
            case ZARPAZO -> this.alpha = enSuelo ? Mth.clamp((this.lifetime - this.age) / 20.0F, 0.0F, 1.0F) * 0.9F
                    : vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F;
            case GRIETA, AVISO, MARCA, SELLO, LASTRE -> {
                float entra = Mth.clamp(this.age / 4.0F, 0.0F, 1.0F);
                float sale = Mth.clamp((this.lifetime - this.age) / 12.0F, 0.0F, 1.0F);
                float late = tipo == Tipo.AVISO || tipo == Tipo.MARCA ? 0.8F + 0.2F * Mth.sin(this.age * 0.6F) : 1.0F;
                this.alpha = entra * sale * late;
            }
            default -> this.alpha = vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F;
        }
        super.tick();
    }

    /** Una piedra en el suelo deja de girar y se frena. */
    private void giroParado() {
        this.xd *= 0.7;
        this.zd *= 0.7;
    }

    @Override
    public void extract(QuadParticleRenderState estado, Camera camara, float parcial) {
        switch (tipo) {
            case ONDA, GRIETA, AVISO, MARCA, SELLO, LASTRE -> {
                // Tumbadas en el suelo, vistas por las dos caras.
                float r = Mth.lerp(parcial, this.oRoll, this.roll);
                extractRotatedQuad(estado, camara, new Quaternionf().rotationX(-Mth.HALF_PI).rotateZ(r), parcial);
                extractRotatedQuad(estado, camara, new Quaternionf().rotationX(Mth.HALF_PI).rotateZ(-r), parcial);
            }
            case ZARPAZO -> {
                if (enSuelo) {
                    float r = Mth.lerp(parcial, this.oRoll, this.roll);
                    extractRotatedQuad(estado, camara, new Quaternionf().rotationX(-Mth.HALF_PI).rotateZ(r), parcial);
                    extractRotatedQuad(estado, camara, new Quaternionf().rotationX(Mth.HALF_PI).rotateZ(-r), parcial);
                } else {
                    super.extract(estado, camara, parcial);
                }
            }
            default -> super.extract(estado, camara, parcial);
        }
    }

    public record Fabrica(SpriteSet sprites, Tipo tipo) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipoParticula, ClientLevel nivel,
                                       double x, double y, double z, double vx, double vy, double vz,
                                       RandomSource azar) {
            return new RajangParticula(nivel, x, y, z, vx, vy, vz, tipo, sprites);
        }
    }
}
