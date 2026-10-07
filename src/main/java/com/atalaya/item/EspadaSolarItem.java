package com.atalaya.item;

import com.atalaya.habilidad.Jefes;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

/**
 * La Gran Espada Solar, el arma del DPS (fuego, Novilis): 10 de dano, algo mas
 * por segundo que la netherita, y prende fuego a los monstruos normales (a
 * minijefes y jefes no). Cada golpe suelta su tajo de sol.
 */
public class EspadaSolarItem extends Item {

    /** Lo que arde un monstruo normal al recibir un golpe. */
    private static final float SEGUNDOS_FUEGO = 4.0F;

    public EspadaSolarItem(Properties props) {
        super(props);
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity blanco, LivingEntity atacante) {
        super.postHurtEnemy(stack, blanco, atacante);
        if (!(atacante.level() instanceof ServerLevel nivel)) {
            return;
        }
        Vec3 tajo = atacante.getEyePosition().add(atacante.getLookAngle().scale(1.3)).add(0, -0.35, 0);
        nivel.sendParticles(AtalayaParticulas.SOLAR_TAJO, tajo.x, tajo.y, tajo.z, 1, 0.0, 0.0, 0.0, 0.0);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_BRASA, blanco.getX(), blanco.getY() + blanco.getBbHeight() * 0.5, blanco.getZ(),
                6, 0.3, 0.4, 0.3, 0.04);
        nivel.playSound(null, blanco.getX(), blanco.getY() + 1.0, blanco.getZ(), AtalayaSonidos.ESPADA_SOLAR_GOLPE, SoundSource.PLAYERS,
                0.8F, 0.95F + nivel.getRandom().nextFloat() * 0.1F);
        if (!Jefes.esJefeOMinijefe(blanco)) {
            blanco.igniteForSeconds(SEGUNDOS_FUEGO);
        }
    }
}
