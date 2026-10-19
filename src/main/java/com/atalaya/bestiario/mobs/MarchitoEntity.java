package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.CreeperBestia;
import com.atalaya.bestiario.Fichas;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

/**
 * El Creeper Marchito (el «Creeper de Wither Rose» del DEDsafio): la rosa marchita hecha creeper. Su estallido deja el
 * Wither a todo lo que pilla cerca (diez segundos, nivel II: lo que no se cura a tiempo se seca) y siembra rosas
 * marchitas alrededor, que siguen secando a quien las pisa. No le afecta el Wither.
 *
 * Sale en el Nether: en el valle de almas y en los yermos.
 */
public class MarchitoEntity extends CreeperBestia {

    /** Hasta donde llega el Wither del estallido (bloques). */
    private static final double ALCANCE_WITHER = 6.0;

    public MarchitoEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        mecha = 30;
        radio = 3.0F;
    }

    public static AttributeSupplier.Builder atributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 20.0)
                .add(Attributes.MOVEMENT_SPEED, 0.27)
                .add(Attributes.FOLLOW_RANGE, 20.0);
    }

    @Override
    public Bestia bestia() {
        return Fichas.MARCHITO;
    }

    @Override
    public boolean canBeAffected(MobEffectInstance efecto) {
        return !efecto.is(MobEffects.WITHER) && super.canBeAffected(efecto);
    }

    @Override
    public void tick() {
        super.tick();
        if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 14 == 0) {
            particulas(nivel, "ceniza", getX(), getY() + 1.7, getZ(), 1, 0.3, 0.2, 0.0);
        }
    }

    @Override
    protected void alEstallar(ServerLevel nivel) {
        particulas(nivel, "petalo", getX(), getY() + 1.0, getZ(), 70, 1.6, 1.0, 0.25);
        particulas(nivel, "ceniza", getX(), getY() + 1.0, getZ(), 40, 1.8, 1.0, 0.08);
        for (LivingEntity e : nivel.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(ALCANCE_WITHER),
                e -> e != this && e.isAlive() && e.distanceToSqr(this) < ALCANCE_WITHER * ALCANCE_WITHER)) {
            BestiaEntity.efecto(e, MobEffects.WITHER, 200, 1, this);
        }
        if (!puedeTocarElMundo(nivel)) {
            return;
        }
        // Las rosas: sobre tierra o arena de almas, donde haya hueco.
        int puestas = 0;
        for (int i = 0; i < 16 && puestas < 4; i++) {
            BlockPos p = blockPosition().offset(random.nextInt(7) - 3, random.nextInt(3) - 1, random.nextInt(7) - 3);
            if (nivel.getBlockState(p).isAir() && Blocks.WITHER_ROSE.defaultBlockState().canSurvive(nivel, p)
                    && (nivel.getBlockState(p.below()).is(BlockTags.DIRT) || nivel.getBlockState(p.below()).is(Blocks.SOUL_SAND)
                    || nivel.getBlockState(p.below()).is(Blocks.SOUL_SOIL) || nivel.getBlockState(p.below()).is(Blocks.NETHERRACK))) {
                nivel.setBlock(p, Blocks.WITHER_ROSE.defaultBlockState(), 3);
                puestas++;
            }
        }
    }
}
