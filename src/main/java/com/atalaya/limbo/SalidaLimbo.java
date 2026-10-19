package com.atalaya.limbo;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/** La salida del Limbo: una losa de luz en el suelo. Quien la pisa vuelve a donde estaba antes de entrar. */
public class SalidaLimbo extends Block {

    public SalidaLimbo(Properties propiedades) {
        super(propiedades);
    }

    @Override
    public void stepOn(Level nivel, BlockPos pos, BlockState estado, Entity quien) {
        if (!nivel.isClientSide() && quien instanceof ServerPlayer p && !p.isSpectator()) {
            Limbo.salir(p);
        }
        super.stepOn(nivel, pos, estado, quien);
    }

    /** Las motas de luz que suben (en el cliente, de vez en cuando). */
    @Override
    public void animateTick(BlockState estado, Level nivel, BlockPos pos, RandomSource azar) {
        if (Limbo.LUZ != null && azar.nextInt(3) == 0) {
            nivel.addParticle(Limbo.LUZ, pos.getX() + azar.nextDouble(), pos.getY() + 1.05, pos.getZ() + azar.nextDouble(),
                    0.0, 0.04 + azar.nextDouble() * 0.04, 0.0);
        }
    }
}
