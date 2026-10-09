package com.atalaya.client;

import com.atalaya.particula.ParticulaSiguiente;

import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.state.level.QuadParticleRenderState;
import org.joml.Quaternionf;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;

/**
 * Las trece particulas de Nerea en una clase: cada
 * {@link Tipo} cambia como se mueve y como se dibuja.
 *
 * La velocidad que llega se respeta en las que la usan como direccion (la
 * ola avanza, el destello va hacia los ojos, la espuma del anillo se abre).
 * Las que son luz (ojo, luz, corazon, chispa, sello) ignoran la oscuridad.
 */
public class NereaParticula extends SingleQuadParticle {

    private static final int A_PLENA_LUZ = 0xF000F0;

    public enum Tipo {
        BURBUJA, ESPUMA, GOTA, OLA, REMOLINO, CHISPA, OJO, SELLO, CORAZON, LUZ, ONDA, ROCA, POLVO, NOTA, HUMO, FOGONAZO
    }

    /** Las notas de su canto, si nadie dice otra cosa: cian, violeta, magenta y rosa (los carriles del Duelo). */
    public static final int[] COLORES_NOTA = {0x4FD8F0, 0x9A7BFF, 0xD45AF0, 0xF06AA8};

    private final Tipo tipo;
    private final SpriteSet sprites;
    private final float tamanoInicial;
    private final float giro;
    private final float fase;
    /** Solo la onda: hasta que radio crece (en bloques). */
    private float radioFinal;

    protected NereaParticula(ClientLevel nivel, double x, double y, double z, double vx, double vy, double vz,
                             Tipo tipo, SpriteSet sprites) {
        super(nivel, x, y, z, sprites.first());
        this.tipo = tipo;
        this.sprites = sprites;
        RandomSource r = this.random;
        this.fase = r.nextFloat() * Mth.TWO_PI;
        this.hasPhysics = false;
        this.gravity = 0.0F;
        this.friction = 0.96F;
        this.xd = vx;
        this.yd = vy;
        this.zd = vz;
        float giroInicial = 0.0F;
        switch (tipo) {
            case BURBUJA -> {
                this.lifetime = 18 + r.nextInt(14);
                this.quadSize = 0.06F + r.nextFloat() * 0.06F;
                this.yd = Math.max(vy, 0.03 + r.nextFloat() * 0.03);
                this.friction = 0.95F;
            }
            case ESPUMA -> {
                this.lifetime = 16 + r.nextInt(10);
                this.quadSize = 0.22F + r.nextFloat() * 0.12F;
                this.friction = 0.88F;
                this.yd = vy + 0.02;
                giroInicial = (r.nextFloat() - 0.5F) * 0.1F;
            }
            case GOTA -> {
                this.lifetime = 24 + r.nextInt(12);
                this.quadSize = 0.06F + r.nextFloat() * 0.04F;
                this.hasPhysics = true;
                this.gravity = 1.1F;
                this.friction = 0.98F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.15;
                this.yd = vy + 0.15 + r.nextFloat() * 0.2;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.15;
            }
            case OLA -> {
                // La cresta: grande, a ras de suelo, sigue avanzando un poco.
                this.lifetime = 12 + r.nextInt(4);
                this.quadSize = 0.75F + r.nextFloat() * 0.3F;
                this.friction = 0.85F;
            }
            case REMOLINO -> {
                this.lifetime = 14;
                this.quadSize = 0.7F;
                this.xd = 0.0;
                this.yd = 0.01;
                this.zd = 0.0;
                giroInicial = 0.45F;
            }
            case CHISPA -> {
                this.lifetime = 8 + r.nextInt(6);
                this.quadSize = 0.08F;
                this.hasPhysics = true;
                this.gravity = 0.9F;
                this.friction = 0.92F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.3;
                this.yd = vy + 0.1 + r.nextFloat() * 0.15;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.3;
            }
            case OJO -> {
                this.lifetime = 10 + r.nextInt(6);
                this.quadSize = 0.1F;
                this.friction = 0.92F;
                giroInicial = 0.2F;
            }
            case SELLO -> {
                this.lifetime = 22 + r.nextInt(14);
                this.quadSize = 0.07F + r.nextFloat() * 0.04F;
                this.hasPhysics = true;
                this.gravity = 1.0F;
                this.friction = 0.97F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.25;
                this.yd = vy + 0.1 + r.nextFloat() * 0.2;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.25;
                giroInicial = (r.nextFloat() - 0.5F) * 0.6F;
                setSprite(sprites.get(r));
            }
            case CORAZON -> {
                this.lifetime = 14;
                this.quadSize = 0.35F;
                this.friction = 0.9F;
            }
            case ONDA -> {
                // La onda expansiva de un golpe: un anillo plano que se abre
                // por el suelo. vx es la fuerza del temblor y vy el radio final.
                // Es lo que sacude la camara de quien este cerca.
                NereaPresencia.sacudir(x, y, z, (float) vx, 26.0F + (float) vy * 3.0F);
                this.radioFinal = (float) Math.max(1.0, vy);
                this.lifetime = 12 + (int) (vy * 0.8);
                this.quadSize = 0.4F;
                this.xd = 0.0;
                this.yd = 0.0;
                this.zd = 0.0;
                this.friction = 1.0F;
            }
            case ROCA -> {
                // Esquirlas de prismarina que salen volando y rebotan.
                this.hasPhysics = true;
                this.gravity = 1.4F;
                this.friction = 0.97F;
                this.lifetime = 40 + r.nextInt(25);
                this.quadSize = 0.09F + r.nextFloat() * 0.09F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.5F;
                setSprite(sprites.get(r));
            }
            case POLVO -> {
                this.lifetime = 22 + r.nextInt(14);
                this.quadSize = 0.3F + r.nextFloat() * 0.25F;
                this.friction = 0.9F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.06F;
            }
            case LUZ -> {
                this.lifetime = 40 + r.nextInt(30);
                this.quadSize = 0.09F;
                this.friction = 0.97F;
                this.yd = Math.max(vy, 0.03 + r.nextFloat() * 0.03);
            }
            case NOTA -> {
                // Vuela recta con la velocidad que trae (sin frenar): asi llega cuando toca.
                this.lifetime = ParticulaSiguiente.vida > 0 ? ParticulaSiguiente.vida : 18 + r.nextInt(10);
                this.quadSize = 0.22F;
                this.friction = 1.0F;
                int color = ParticulaSiguiente.color >= 0 ? ParticulaSiguiente.color : COLORES_NOTA[r.nextInt(COLORES_NOTA.length)];
                setColor(((color >> 16) & 255) / 255.0F, ((color >> 8) & 255) / 255.0F, (color & 255) / 255.0F);
                setSprite(sprites.get(ParticulaSiguiente.forma >= 0 ? ParticulaSiguiente.forma : r.nextInt(3), 3));
                giroInicial = (r.nextFloat() - 0.5F) * 0.08F;
            }
            case HUMO -> {
                this.lifetime = 30 + r.nextInt(16);
                this.quadSize = 0.35F + r.nextFloat() * 0.25F;
                this.friction = 0.9F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.05F;
            }
            case FOGONAZO -> {
                this.lifetime = 4 + r.nextInt(3);
                this.quadSize = 0.6F + r.nextFloat() * 0.35F;
                this.xd = vx * 0.3;
                this.yd = vy * 0.3;
                this.zd = vz * 0.3;
                this.friction = 0.7F;
            }
        }
        this.quadSize *= ParticulaSiguiente.escala;
        ParticulaSiguiente.olvidar();
        this.tamanoInicial = this.quadSize;
        this.giro = giroInicial;
        if (tipo != Tipo.SELLO && tipo != Tipo.GOTA && tipo != Tipo.ROCA && tipo != Tipo.NOTA) {
            setSpriteFromAge(sprites);
        } else if (tipo == Tipo.GOTA) {
            setSprite(sprites.get(0, 1));
        }
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    @Override
    protected int getLightCoords(float parcial) {
        return switch (tipo) {
            case OJO, LUZ, CORAZON, CHISPA, SELLO, ONDA, NOTA, FOGONAZO -> A_PLENA_LUZ;
            default -> super.getLightCoords(parcial);
        };
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += giro;
        float vida = this.age / (float) this.lifetime;
        switch (tipo) {
            case BURBUJA -> {
                // Sube haciendo eses y revienta en el ultimo fotograma.
                this.xd += Mth.sin(this.age * 0.5F + fase) * 0.004;
                this.zd += Mth.cos(this.age * 0.45F + fase) * 0.004;
                setSprite(sprites.get(vida < 0.85F ? (vida < 0.4F ? 0 : 1) : 2, 2));
            }
            case ESPUMA -> {
                this.quadSize = tamanoInicial * (1.0F + 0.9F * vida);
                setSpriteFromAge(sprites);
            }
            case GOTA -> {
                if (this.onGround) {
                    setSprite(sprites.get(1, 1));
                }
            }
            case OLA, OJO, CORAZON, REMOLINO -> {
                if (tipo == Tipo.CORAZON || tipo == Tipo.REMOLINO) {
                    this.quadSize = tamanoInicial * (0.7F + 0.6F * vida);
                }
                setSpriteFromAge(sprites);
            }
            case CHISPA -> {
                this.quadSize = tamanoInicial * (1.0F - 0.6F * vida);
                setSpriteFromAge(sprites);
            }
            case LUZ -> {
                this.xd += Mth.sin(this.age * 0.2F + fase) * 0.003;
                this.zd += Mth.cos(this.age * 0.17F + fase) * 0.003;
                setSprite(sprites.get((this.age / 4) % 3, 2));
            }
            case ONDA -> {
                // Se abre rapido al principio y frena: como una onda de verdad.
                float k = 1.0F - (1.0F - vida) * (1.0F - vida);
                this.quadSize = 0.4F + this.radioFinal * k;
                setSpriteFromAge(sprites);
            }
            case POLVO -> {
                this.quadSize = tamanoInicial * (1.0F + 1.2F * vida);
                this.yd += 0.002;
                setSpriteFromAge(sprites);
            }
            case NOTA -> {
                // Se mece un poco al volar.
                this.yd += Mth.sin(this.age * 0.6F + fase) * 0.006;
            }
            case HUMO -> {
                this.quadSize = tamanoInicial * (1.0F + 1.4F * vida);
                this.yd += 0.003;
                setSpriteFromAge(sprites);
            }
            case FOGONAZO -> {
                this.quadSize = tamanoInicial * (1.0F + 0.5F * vida);
                setSpriteFromAge(sprites);
            }
            case SELLO, ROCA -> {
            }
        }
        this.alpha = vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F;
        if (tipo == Tipo.ONDA) {
            this.alpha = 1.0F - vida;
        }
        super.tick();
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
            return new NereaParticula(nivel, x, y, z, vx, vy, vz, tipo, sprites);
        }
    }
}
