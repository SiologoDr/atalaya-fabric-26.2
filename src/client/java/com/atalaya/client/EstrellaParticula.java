package com.atalaya.client;

import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleProvider;
import net.minecraft.client.particle.SingleQuadParticle;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.util.RandomSource;

/**
 * La estrellita que da vueltas sobre la cabeza del aturdido.
 *
 * Ni sube ni cae: se queda flotando y GIRA. Ese es todo el truco del dibujo de
 * "ver las estrellas" — si se movieran como chispas o como humo, se leerian
 * como cualquier otra particula del juego.
 *
 * La orbita tampoco se calcula aqui: la posicion inicial se la da quien la
 * lanza, repartiendo las estrellas en circulo. Asi la particula no necesita
 * saber de quien es ni seguirlo, y sale mucho mas barata.
 */
public class EstrellaParticula extends SingleQuadParticle {

    /** Vueltas por tick. Lento: mareado, no un ventilador. */
    private static final float GIRO = 0.09F;

    protected EstrellaParticula(ClientLevel nivel, double x, double y, double z,
                                net.minecraft.client.renderer.texture.TextureAtlasSprite sprite) {
        super(nivel, x, y, z, sprite);
        // Quieta en el sitio. La gravedad a cero y sin velocidad: las estrellas
        // no caen, se quedan dando vueltas donde estan.
        this.gravity = 0.0F;
        this.xd = 0.0;
        this.yd = 0.0;
        this.zd = 0.0;
        this.quadSize = 0.10F;
        this.lifetime = 18 + nivel.getRandom().nextInt(10);
        this.hasPhysics = false;
    }

    @Override
    protected Layer getLayer() {
        return Layer.TRANSLUCENT;
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += GIRO;
        // Se apaga hacia el final en vez de desaparecer de golpe: un corte seco
        // se nota como un parpadeo raro.
        float vida = this.age / (float) this.lifetime;
        this.alpha = vida < 0.7F ? 1.0F : 1.0F - ((vida - 0.7F) / 0.3F);
        super.tick();
    }

    /** Lo que el juego usa para fabricarlas. */
    public record Fabrica(SpriteSet sprites) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipo, ClientLevel nivel,
                                       double x, double y, double z,
                                       double vx, double vy, double vz,
                                       RandomSource azar) {
            return new EstrellaParticula(nivel, x, y, z, this.sprites.get(azar));
        }
    }
}
