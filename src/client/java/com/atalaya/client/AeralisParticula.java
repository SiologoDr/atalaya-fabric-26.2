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
import org.joml.Vector3fc;

/**
 * Las once particulas de Aeralis en una clase: cada {@link Tipo} cambia como
 * se mueve y como se dibuja.
 *
 * La estela de viento se tumba en la direccion en que va (vista desde la
 * camara), la onda, el remolino y el circulo del Juicio van tumbados en el
 * suelo, y las que son luz (rayo, marca, luz, oro, onda, circulo) no se
 * oscurecen de noche.
 */
public class AeralisParticula extends SingleQuadParticle {

    private static final int A_PLENA_LUZ = 0xF000F0;

    public enum Tipo {
        VIENTO, ESCAMA, REMOLINO, RAYO, MARCA, LUZ, ORO, ONDA, CIRCULO, POLVO, JIRON
    }

    private final Tipo tipo;
    private final SpriteSet sprites;
    private final float tamanoInicial;
    private final float giro;
    private final float fase;
    /** La onda y el circulo: hasta que radio llegan (bloques). */
    private float radioFinal;

    protected AeralisParticula(ClientLevel nivel, double x, double y, double z, double vx, double vy, double vz,
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
            case VIENTO -> {
                this.lifetime = 10 + r.nextInt(8);
                this.quadSize = 0.35F + r.nextFloat() * 0.25F;
                this.friction = 0.94F;
            }
            case ESCAMA -> {
                // Cae revoloteando, como una escama de polilla.
                this.lifetime = 50 + r.nextInt(30);
                this.quadSize = 0.07F + r.nextFloat() * 0.06F;
                this.gravity = 0.04F;
                this.friction = 0.96F;
                this.xd = vx + (r.nextFloat() - 0.5) * 0.08;
                this.zd = vz + (r.nextFloat() - 0.5) * 0.08;
                giroInicial = (r.nextFloat() - 0.5F) * 0.35F;
                setSprite(sprites.get(r));
            }
            case REMOLINO -> {
                // El polvo que gira en el suelo. vx: escala (0 = 1).
                float esc = vx > 0 ? (float) vx : 1.0F;
                this.lifetime = 16;
                this.quadSize = 1.0F * esc;
                this.xd = 0.0;
                this.yd = 0.0;
                this.zd = 0.0;
                giroInicial = 0.5F;
            }
            case RAYO -> {
                this.lifetime = 3 + r.nextInt(3);
                this.quadSize = 0.6F + r.nextFloat() * 0.8F;
                this.xd = 0.0;
                this.yd = 0.0;
                this.zd = 0.0;
                this.roll = r.nextFloat() * Mth.TWO_PI;
                this.oRoll = this.roll;
                setSprite(sprites.get(r));
            }
            case MARCA -> {
                this.lifetime = 20 + r.nextInt(12);
                this.quadSize = 0.2F + r.nextFloat() * 0.08F;
                this.yd = Math.max(vy, 0.02);
                this.friction = 0.92F;
                giroInicial = 0.12F;
            }
            case LUZ, ORO -> {
                this.lifetime = 30 + r.nextInt(25);
                this.quadSize = 0.07F + r.nextFloat() * 0.05F;
                this.friction = 0.97F;
            }
            case ONDA -> {
                // vx: fuerza del temblor; vy: radio final. Sacude la camara de quien este cerca.
                NereaPresencia.sacudir(x, y, z, (float) vx, 28.0F + (float) vy * 3.0F);
                this.radioFinal = (float) Math.max(1.0, vy);
                this.lifetime = 12 + (int) (vy * 0.7);
                this.quadSize = 0.4F;
                this.xd = 0.0;
                this.yd = 0.0;
                this.zd = 0.0;
                this.friction = 1.0F;
            }
            case CIRCULO -> {
                // vx: radio; vy: ticks que dura.
                this.radioFinal = (float) Math.max(1.0, vx);
                this.lifetime = vy > 0 ? (int) vy : 80;
                this.quadSize = 0.2F;
                this.xd = 0.0;
                this.yd = 0.0;
                this.zd = 0.0;
                this.friction = 1.0F;
                giroInicial = 0.004F;
            }
            case POLVO -> {
                this.lifetime = 20 + r.nextInt(16);
                this.quadSize = 0.3F + r.nextFloat() * 0.3F;
                this.friction = 0.9F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.06F;
            }
            case JIRON -> {
                this.lifetime = 16 + r.nextInt(14);
                this.quadSize = 0.35F + r.nextFloat() * 0.4F;
                this.friction = 0.9F;
                giroInicial = (r.nextFloat() - 0.5F) * 0.05F;
                setSprite(sprites.get(r));
            }
        }
        this.tamanoInicial = this.quadSize;
        this.giro = giroInicial;
        if (tipo != Tipo.ESCAMA && tipo != Tipo.RAYO && tipo != Tipo.JIRON) {
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
            case RAYO, MARCA, LUZ, ORO, ONDA, CIRCULO -> A_PLENA_LUZ;
            default -> super.getLightCoords(parcial);
        };
    }

    @Override
    public void tick() {
        this.oRoll = this.roll;
        this.roll += giro;
        float vida = this.age / (float) this.lifetime;
        switch (tipo) {
            case VIENTO -> setSpriteFromAge(sprites);
            case ESCAMA -> {
                this.xd += Mth.sin(this.age * 0.3F + fase) * 0.006;
                this.zd += Mth.cos(this.age * 0.27F + fase) * 0.006;
            }
            case REMOLINO -> {
                this.quadSize = tamanoInicial * (0.6F + 0.7F * vida);
                setSpriteFromAge(sprites);
            }
            case RAYO -> {
                if (this.random.nextInt(2) == 0) {
                    setSprite(sprites.get(this.random));
                }
            }
            case MARCA -> {
                this.xd += Mth.sin(this.age * 0.4F + fase) * 0.01;
                this.zd += Mth.cos(this.age * 0.4F + fase) * 0.01;
                setSprite(sprites.get((this.age / 5) % 2, 1));
            }
            case LUZ, ORO -> setSprite(sprites.get((this.age / 4) % 3, 2));
            case ONDA -> {
                float k = 1.0F - (1.0F - vida) * (1.0F - vida);
                this.quadSize = 0.4F + this.radioFinal * k;
                setSpriteFromAge(sprites);
            }
            case CIRCULO -> {
                // Se abre en un momento y luego se queda, latiendo.
                float k = Mth.clamp(this.age / 12.0F, 0.0F, 1.0F);
                this.quadSize = this.radioFinal * (1.0F - (1.0F - k) * (1.0F - k));
                setSprite(sprites.get((this.age / 10) % 2, 1));
            }
            case POLVO -> {
                this.quadSize = tamanoInicial * (1.0F + 1.3F * vida);
                this.yd += 0.002;
                setSpriteFromAge(sprites);
            }
            case JIRON -> this.quadSize = tamanoInicial * (1.0F + 1.1F * vida);
        }
        this.alpha = vida < 0.6F ? 1.0F : 1.0F - (vida - 0.6F) / 0.4F;
        if (tipo == Tipo.ONDA) {
            this.alpha = 1.0F - vida;
        } else if (tipo == Tipo.CIRCULO) {
            float entra = Mth.clamp(this.age / 10.0F, 0.0F, 1.0F);
            float sale = Mth.clamp((this.lifetime - this.age) / 20.0F, 0.0F, 1.0F);
            this.alpha = entra * sale * (0.75F + 0.25F * Mth.sin(this.age * 0.25F));
        } else if (tipo == Tipo.RAYO) {
            this.alpha = this.random.nextFloat() < 0.3F ? 0.4F : 1.0F;
        } else if (tipo == Tipo.JIRON) {
            this.alpha = 0.75F * (1.0F - vida);
        }
        super.tick();
    }

    @Override
    public void extract(QuadParticleRenderState estado, Camera camara, float parcial) {
        switch (tipo) {
            case ONDA, REMOLINO, CIRCULO -> {
                // Tumbadas en el suelo, vistas por las dos caras.
                float r = Mth.lerp(parcial, this.oRoll, this.roll);
                extractRotatedQuad(estado, camara, new Quaternionf().rotationX(-Mth.HALF_PI).rotateZ(r), parcial);
                extractRotatedQuad(estado, camara, new Quaternionf().rotationX(Mth.HALF_PI).rotateZ(-r), parcial);
            }
            case VIENTO -> {
                // La estela, a lo largo de su velocidad tal como se ve en pantalla.
                Vector3fc izq = camara.leftVector();
                Vector3fc arriba = camara.upVector();
                double enX = -(this.xd * izq.x() + this.yd * izq.y() + this.zd * izq.z());
                double enY = this.xd * arriba.x() + this.yd * arriba.y() + this.zd * arriba.z();
                Quaternionf giroEstela = new Quaternionf(camara.rotation());
                giroEstela.rotateZ((float) Math.atan2(enY, enX));
                extractRotatedQuad(estado, camara, giroEstela, parcial);
            }
            default -> super.extract(estado, camara, parcial);
        }
    }

    public record Fabrica(SpriteSet sprites, Tipo tipo) implements ParticleProvider<SimpleParticleType> {

        @Override
        public Particle createParticle(SimpleParticleType tipoParticula, ClientLevel nivel,
                                       double x, double y, double z, double vx, double vy, double vz,
                                       RandomSource azar) {
            return new AeralisParticula(nivel, x, y, z, vx, vy, vz, tipo, sprites);
        }
    }
}
