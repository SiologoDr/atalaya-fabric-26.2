package com.atalaya.client;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;

/**
 * Las ocho particulas del Vigia en una sola clase: comparten casi todo (un
 * cuadrado de cara a la camara que se apaga al final) y solo cambia COMO se
 * mueven y COMO se dibujan. Cada {@link Tipo} es una linea de esa tabla.
 *
 * Las que son luz —el ojo, el rayo, la marca, la zarpa, el alma— van a brillo
 * completo e ignoran la oscuridad, igual que la capa de ojos del bicho: de
 * noche son lo que se ve. El humo y las esquirlas son materia y se iluminan
 * como cualquier cosa del mundo.
 */
public class VigiaParticula extends SingleQuadParticle {

    /** Brillo completo: el maximo de luz de bloque y de cielo. */
    private static final int A_PLENA_LUZ = 0xF000F0;

    public enum Tipo {
        CHISPA, RAYO, MALDICION, MARCA, ZARPA, ESQUIRLA, HUMO, ALMA
    }

    private final Tipo tipo;
    private final SpriteSet sprites;
    private final float tamanoInicial;
    private final float giro;
    private final float fase;

    protected VigiaParticula(ClientLevel nivel, double x, double y, double z,
                             double vx, double vy, double vz, Tipo tipo, SpriteSet sprites) {
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
            case CHISPA -> {
                // La velocidad la trae: va hacia el ojo.
                this.lifetime = 10 + r.nextInt(5);
                this.quadSize = 0.09F;
                this.friction = 0.9F;
                giroInicial = 0.15F;
            }
            case RAYO -> {
                // vx no es velocidad: es la carga de 0 a 1. Del ambar del ojo
                // en calma al rojo del disparo, igual que el propio ojo.
                float carga = Mth.clamp((float) vx, 0.0F, 1.0F);
                setColor(1.0F, Mth.lerp(carga, 0.71F, 0.13F), Mth.lerp(carga, 0.23F, 0.06F));
                this.xd = 0.0;
                this.yd = 0.0;
                this.zd = 0.0;
                this.lifetime = 5 + r.nextInt(2);
                this.quadSize = 0.1F + 0.05F * carga;
            }
            case MALDICION -> {
                this.lifetime = 26 + r.nextInt(10);
                this.quadSize = 0.2F + r.nextFloat() * 0.08F;
                this.yd = 0.02 + r.nextFloat() * 0.02;
                giroInicial = (r.nextBoolean() ? 1 : -1) * 0.05F;
            }
            case MARCA -> {
                this.lifetime = 20 + r.nextInt(10);
                this.quadSize = 0.07F;
                this.xd = (r.nextFloat() - 0.5) * 0.01;
                this.yd = 0.012;
                this.zd = (r.nextFloat() - 0.5) * 0.01;
            }
            case ZARPA -> {
                // Quieta donde se cierra el cepo: el tajo se ve, no vuela.
                this.xd = 0.0;
                this.yd = 0.0;
                this.zd = 0.0;
                this.lifetime = 6;
                this.quadSize = 0.85F;
                this.roll = (r.nextFloat() - 0.5F) * 0.5F;
            }
            case ESQUIRLA -> {
                this.hasPhysics = true;
                this.gravity = 1.0F;
                this.friction = 0.98F;
                this.lifetime = 25 + r.nextInt(12);
                this.quadSize = 0.05F + r.nextFloat() * 0.03F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.25;
                this.yd = vy + 0.1 + r.nextFloat() * 0.2;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.25;
                giroInicial = (r.nextFloat() - 0.5F) * 0.6F;
                setSprite(sprites.get(r));
            }
            case HUMO -> {
                this.lifetime = 30 + r.nextInt(16);
                this.quadSize = 0.15F;
                this.friction = 0.94F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.02;
                this.yd = 0.03 + r.nextFloat() * 0.02;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.02;
                giroInicial = (r.nextFloat() - 0.5F) * 0.08F;
            }
            case ALMA -> {
                this.lifetime = 35 + r.nextInt(20);
                this.quadSize = 0.1F;
                this.friction = 0.98F;
                this.yd = 0.035 + r.nextFloat() * 0.02;
            }
        }
        this.tamanoInicial = this.quadSize;
        this.giro = giroInicial;
        if (tipo != Tipo.ESQUIRLA && tipo != Tipo.ALMA) {
            setSpriteFromAge(sprites);
        }
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    @Override
    protected int getLightCoords(float parcial) {
        return switch (tipo) {
            case HUMO, ESQUIRLA -> super.getLightCoords(parcial);
            default -> A_PLENA_LUZ;
        };
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += giro;
        float vida = this.age / (float) this.lifetime;

        switch (tipo) {
            case HUMO -> {
                // Crece y se deshace: una bocanada, no una bola que sube.
                this.quadSize = tamanoInicial * (1.0F + 1.4F * vida);
                setSpriteFromAge(sprites);
            }
            case ALMA -> {
                // Sube ondulando, y la llama parpadea entre sus tres dibujos.
                this.xd += Mth.sin(this.age * 0.25F + fase) * 0.004;
                this.zd += Mth.cos(this.age * 0.21F + fase) * 0.004;
                setSprite(sprites.get((this.age / 3) % 3, 2));
            }
            case CHISPA -> {
                this.quadSize = tamanoInicial * (1.0F - 0.6F * vida);
                setSpriteFromAge(sprites);
            }
            case RAYO -> this.alpha = 0.75F + 0.25F * Mth.sin(this.age * 2.1F + fase);
            case MARCA, MALDICION, ZARPA -> setSpriteFromAge(sprites);
            case ESQUIRLA -> {
            }
        }

        // Todas se apagan en el ultimo tercio en vez de desaparecer de golpe.
        if (tipo != Tipo.RAYO) {
            this.alpha = vida < 0.65F ? 1.0F : 1.0F - (vida - 0.65F) / 0.35F;
        }
        super.tick();
    }

    /** Lo que el juego usa para fabricarlas, una por tipo. */
    public record Fabrica(SpriteSet sprites, Tipo tipo) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipoParticula, ClientLevel nivel,
                                       double x, double y, double z,
                                       double vx, double vy, double vz,
                                       RandomSource azar) {
            return new VigiaParticula(nivel, x, y, z, vx, vy, vz, tipo, sprites);
        }
    }
}
