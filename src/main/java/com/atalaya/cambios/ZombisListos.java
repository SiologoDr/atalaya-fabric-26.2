package com.atalaya.cambios;

import com.atalaya.mixin.MobAccessor;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.zombie.Zombie;
import net.minecraft.world.entity.projectile.throwableitemprojectile.ThrownEnderpearl;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.Path;

import java.util.EnumSet;

/**
 * ZOMBIS LISTOS (DEDsafio 3, «Zombis listos»; DEDsafio 4, los de pico de diamante y los de bajo la capa 40): un zombi
 * que no llega hasta ti hace lo que haria un jugador. Si estas mas alto, sube poniendo bloques bajo sus pies; si hay una
 * pared en medio, la pica (lo que tarde segun lo duro que sea, con las grietas que se ven); y si estas lejos y a la vista,
 * te tira una perla de ender y aparece a tu lado. Salen con pico de diamante, alguna pieza de armadura de hierro, unas
 * perlas y, a veces, un totem en la otra mano.
 */
public final class ZombisListos {

    private static final String MARCA = "atalaya_zombi_listo";
    /** Los que ya llevan la cabeza de picar y poner (se olvidan solos al descargarse). */
    private static final java.util.Set<Zombie> CON_CABEZA =
            java.util.Collections.newSetFromMap(new java.util.WeakHashMap<>());

    private ZombisListos() {
    }

    /** Lo arma y le pone su cabeza (una vez). */
    static void preparar(Zombie z) {
        boolean nuevo = !z.entityTags().contains(MARCA);
        if (nuevo) {
            z.addTag(MARCA);
            RandomSource r = z.getRandom();
            if (z.getMainHandItem().isEmpty()) {
                z.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.DIAMOND_PICKAXE));
                z.setDropChance(EquipmentSlot.MAINHAND, 0.04F);
            }
            EquipmentSlot[] piezas = {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET};
            ItemStack[] hierro = {new ItemStack(Items.IRON_HELMET), new ItemStack(Items.IRON_CHESTPLATE),
                    new ItemStack(Items.IRON_LEGGINGS), new ItemStack(Items.IRON_BOOTS)};
            for (int i = 0; i < 4; i++) {
                if (z.getItemBySlot(piezas[i]).isEmpty() && r.nextFloat() < 0.45F) {
                    z.setItemSlot(piezas[i], hierro[i]);
                    z.setDropChance(piezas[i], 0.05F);
                }
            }
            if (z.getOffhandItem().isEmpty()) {
                if (r.nextFloat() < 0.05F) {
                    z.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(Items.TOTEM_OF_UNDYING));
                    z.setDropChance(EquipmentSlot.OFFHAND, 1.0F);
                } else {
                    z.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(Items.ENDER_PEARL, 1 + r.nextInt(3)));
                    z.setDropChance(EquipmentSlot.OFFHAND, 0.5F);
                }
            }
        }
        // La cabeza no se guarda con el mob: se pone cada vez que se carga (una sola vez por carga).
        if (CON_CABEZA.add(z)) {
            ((MobAccessor) z).atalaya$objetivos().addGoal(2, new Picar(z));
            ((MobAccessor) z).atalaya$objetivos().addGoal(3, new Perla(z));
        }
    }

    /** Si su presa esta fuera de su alcance andando. */
    private static boolean atascado(Zombie z, LivingEntity presa) {
        Path camino = z.getNavigation().getPath();
        if (camino == null) {
            camino = z.getNavigation().createPath(presa, 1);
        }
        return camino == null || !camino.canReach();
    }

    /** Picar la pared que tiene delante o subir poniendo bloques. */
    private static final class Picar extends Goal {

        private final Zombie z;
        private BlockPos picando;
        private int progreso;
        private int necesita;
        private int espera;

        Picar(Zombie z) {
            this.z = z;
            setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            if (!CambiosDificultad.activo(Cambio.ZOMBIS_LISTOS) || --espera > 0) {
                return false;
            }
            espera = 10;
            LivingEntity presa = z.getTarget();
            return presa != null && presa.isAlive() && z.distanceToSqr(presa) < 24 * 24 && z.onGround() && atascado(z, presa);
        }

        @Override
        public boolean canContinueToUse() {
            LivingEntity presa = z.getTarget();
            return CambiosDificultad.activo(Cambio.ZOMBIS_LISTOS) && presa != null && presa.isAlive()
                    && z.distanceToSqr(presa) < 26 * 26 && (picando != null || atascado(z, presa));
        }

        @Override
        public void stop() {
            if (picando != null) {
                z.level().destroyBlockProgress(z.getId(), picando, -1);
            }
            picando = null;
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            LivingEntity presa = z.getTarget();
            if (presa == null || !(z.level() instanceof ServerLevel nivel)) {
                return;
            }
            z.getLookControl().setLookAt(presa, 30.0F, 30.0F);
            double dy = presa.getY() - z.getY();
            double dx = presa.getX() - z.getX();
            double dz = presa.getZ() - z.getZ();
            double horizontal = Math.sqrt(dx * dx + dz * dz);
            // Mas alto y casi encima: sube poniendo tierra bajo sus pies.
            if (picando == null && dy > 1.5 && horizontal < 3.5) {
                BlockPos pies = z.blockPosition();
                if (z.onGround() && nivel.getBlockState(pies.above(2)).isAir()) {
                    z.getJumpControl().jump();
                } else if (!z.onGround() && z.getDeltaMovement().y < 0.05 && nivel.getBlockState(pies).isAir()
                        && z.getY() - pies.getY() > 0.9) {
                    nivel.setBlockAndUpdate(pies, Blocks.COBBLESTONE.defaultBlockState());
                    z.setPos(z.getX(), pies.getY() + 1.0, z.getZ());
                    z.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                }
                return;
            }
            // Si no, pica lo que tiene delante (a la altura de los pies o de la cabeza), camino de su presa.
            if (picando == null) {
                Direction hacia = Direction.getApproximateNearest(dx, 0, dz);
                BlockPos frente = z.blockPosition().relative(hacia);
                BlockPos[] candidatos = dy > 0.5 ? new BlockPos[]{frente.above(), frente, frente.above(2)}
                        : dy < -0.5 ? new BlockPos[]{frente, frente.below(), frente.above()} : new BlockPos[]{frente.above(), frente};
                for (BlockPos q : candidatos) {
                    BlockState estado = nivel.getBlockState(q);
                    float dureza = estado.getDestroySpeed(nivel, q);
                    if (!estado.isAir() && dureza >= 0.0F && dureza < 30.0F && estado.getFluidState().isEmpty()) {
                        picando = q;
                        progreso = 0;
                        necesita = Mth.clamp((int) (dureza * 22.0F) + 10, 10, 220);
                        break;
                    }
                }
                if (picando == null) {
                    return;
                }
            }
            z.getNavigation().stop();
            z.getLookControl().setLookAt(picando.getX() + 0.5, picando.getY() + 0.5, picando.getZ() + 0.5);
            if (progreso % 6 == 0) {
                z.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            }
            progreso++;
            nivel.destroyBlockProgress(z.getId(), picando, (int) (progreso * 10.0F / necesita));
            if (progreso >= necesita) {
                nivel.destroyBlockProgress(z.getId(), picando, -1);
                nivel.destroyBlock(picando, true, z);
                picando = null;
            }
        }
    }

    /** Lejos y a la vista: una perla de ender hacia su presa. */
    private static final class Perla extends Goal {

        private final Zombie z;
        private int espera = 60;

        Perla(Zombie z) {
            this.z = z;
        }

        @Override
        public boolean canUse() {
            if (!CambiosDificultad.activo(Cambio.ZOMBIS_LISTOS) || --espera > 0) {
                return false;
            }
            espera = 40;
            LivingEntity presa = z.getTarget();
            if (presa == null || !z.getOffhandItem().is(Items.ENDER_PEARL)) {
                return false;
            }
            double d = z.distanceToSqr(presa);
            return d > 14 * 14 && d < 40 * 40 && z.hasLineOfSight(presa);
        }

        @Override
        public void start() {
            LivingEntity presa = z.getTarget();
            if (presa == null) {
                return;
            }
            ItemStack perlas = z.getOffhandItem();
            ThrownEnderpearl perla = new ThrownEnderpearl(z.level(), z, new ItemStack(Items.ENDER_PEARL));
            double dx = presa.getX() - z.getX();
            double dy = presa.getY(0.3) - perla.getY();
            double dz = presa.getZ() - z.getZ();
            double h = Math.sqrt(dx * dx + dz * dz);
            perla.shoot(dx, dy + h * 0.2, dz, 1.5F, 4.0F);
            z.level().addFreshEntity(perla);
            z.swing(net.minecraft.world.InteractionHand.OFF_HAND);
            perlas.shrink(1);
            espera = 160;
        }

        @Override
        public boolean canContinueToUse() {
            return false;
        }
    }
}
