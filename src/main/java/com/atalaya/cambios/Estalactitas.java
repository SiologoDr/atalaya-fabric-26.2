package com.atalaya.cambios;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.item.FallingBlockEntity;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.SpeleothemThickness;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 * TECHOS QUE CAEN (DEDsafio 2, las estalactitas de la mazmorra de las aranas): en las cuevas, de vez en cuando, el techo
 * suelta una estalactita sobre quien pasa por debajo. Un segundo antes cruje (unas motas de piedra caen del techo), para
 * que el atento se aparte a tiempo.
 */
public final class Estalactitas {

    private record Pendiente(ServerLevel nivel, BlockPos punta, int cuando) {
    }

    private static final List<Pendiente> PENDIENTES = new ArrayList<>();

    private Estalactitas() {
    }

    /** Cada segundo, con algo de suerte, una estalactita sobre ese jugador (si esta en una cueva con techo). */
    static void quizas(ServerPlayer p, ServerLevel nivel) {
        RandomSource r = p.getRandom();
        if (r.nextFloat() > 0.025F) {
            return;
        }
        BlockPos pies = p.blockPosition();
        if (nivel.getBrightness(LightLayer.SKY, pies) > 0) {
            return;
        }
        BlockPos donde = pies.offset(r.nextInt(3) - 1, 0, r.nextInt(3) - 1);
        for (int dy = 3; dy <= 14; dy++) {
            BlockPos techo = donde.above(dy);
            if (nivel.getBlockState(techo).isAir()) {
                continue;
            }
            BlockPos punta = techo.below();
            if (!nivel.getBlockState(techo).isFaceSturdy(nivel, techo, Direction.DOWN) || !nivel.getBlockState(punta).isAir()) {
                return;
            }
            // El aviso: unas motas de piedra y el crujido.
            nivel.sendParticles(new BlockParticleOption(ParticleTypes.FALLING_DUST, nivel.getBlockState(techo)),
                    punta.getX() + 0.5, punta.getY() + 0.9, punta.getZ() + 0.5, 10, 0.25, 0.05, 0.25, 0.0);
            nivel.playSound(null, punta, SoundEvents.POINTED_DRIPSTONE_DRIP_LAVA, SoundSource.BLOCKS, 0.8F, 0.6F);
            PENDIENTES.add(new Pendiente(nivel, punta, nivel.getServer().getTickCount() + 20));
            return;
        }
    }

    /** Las que ya han crujido y les toca caer. */
    static void tick(int ahora) {
        if (PENDIENTES.isEmpty()) {
            return;
        }
        BlockState estalactita = Blocks.POINTED_DRIPSTONE.defaultBlockState()
                .setValue(BlockStateProperties.VERTICAL_DIRECTION, Direction.DOWN)
                .setValue(BlockStateProperties.SPELEOTHEM_THICKNESS, SpeleothemThickness.TIP);
        for (Iterator<Pendiente> it = PENDIENTES.iterator(); it.hasNext(); ) {
            Pendiente p = it.next();
            if (ahora < p.cuando()) {
                continue;
            }
            it.remove();
            if (p.nivel().getBlockState(p.punta()).isAir()) {
                FallingBlockEntity cae = FallingBlockEntity.fall(p.nivel(), p.punta(), estalactita);
                cae.setHurtsEntities(2.0F, 40);
            }
        }
    }
}
