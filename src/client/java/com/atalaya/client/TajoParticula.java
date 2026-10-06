package com.atalaya.client;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.RandomSource;

/**
 * El tajo de una espada de jefe al golpear: una media luna del color del tema
 * (agua, jade o viento) delante de quien golpea, que se abre y se deshace en
 * cuatro cuadros, como el barrido de vanilla. Brilla sin luz.
 */
public class TajoParticula extends SingleQuadParticle {

    private final SpriteSet sprites;

    protected TajoParticula(ClientLevel nivel, double x, double y, double z, SpriteSet sprites) {
        super(nivel, x, y, z, sprites.first());
        this.sprites = sprites;
        this.gravity = 0.0F;
        this.xd = 0.0;
        this.yd = 0.0;
        this.zd = 0.0;
        this.hasPhysics = false;
        this.lifetime = 5;
        this.quadSize = 0.85F;
        setSpriteFromAge(sprites);
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    @Override
    protected int getLightCoords(float parcial) {
        return 0xF000F0;
    }

    @Override
    public void tick() {
        super.tick();
        setSpriteFromAge(sprites);
    }

    public record Fabrica(SpriteSet sprites) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipo, ClientLevel nivel, double x, double y, double z,
                                       double vx, double vy, double vz, RandomSource azar) {
            return new TajoParticula(nivel, x, y, z, sprites);
        }
    }
}
