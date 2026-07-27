/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  com.github.L_Ender.lionfishapi.server.animation.Animation
 *  com.github.L_Ender.lionfishapi.server.animation.IAnimatedEntity
 *  javax.annotation.Nullable
 *  net.minecraft.ChatFormatting
 *  net.minecraft.core.BlockPos
 *  net.minecraft.core.particles.BlockParticleOption
 *  net.minecraft.core.particles.ParticleOptions
 *  net.minecraft.core.particles.ParticleTypes
 *  net.minecraft.nbt.CompoundTag
 *  net.minecraft.network.syncher.SynchedEntityData$Builder
 *  net.minecraft.sounds.SoundEvent
 *  net.minecraft.sounds.SoundEvents
 *  net.minecraft.sounds.SoundSource
 *  net.minecraft.tags.DamageTypeTags
 *  net.minecraft.util.Mth
 *  net.minecraft.util.RandomSource
 *  net.minecraft.util.TimeUtil
 *  net.minecraft.util.valueproviders.UniformInt
 *  net.minecraft.world.damagesource.DamageSource
 *  net.minecraft.world.entity.Entity
 *  net.minecraft.world.entity.EntitySelector
 *  net.minecraft.world.entity.EntityType
 *  net.minecraft.world.entity.LivingEntity
 *  net.minecraft.world.entity.Mob
 *  net.minecraft.world.entity.MobSpawnType
 *  net.minecraft.world.entity.NeutralMob
 *  net.minecraft.world.entity.PathfinderMob
 *  net.minecraft.world.entity.ai.attributes.AttributeSupplier$Builder
 *  net.minecraft.world.entity.ai.attributes.Attributes
 *  net.minecraft.world.entity.ai.control.BodyRotationControl
 *  net.minecraft.world.entity.ai.goal.Goal
 *  net.minecraft.world.entity.ai.goal.Goal$Flag
 *  net.minecraft.world.entity.ai.goal.LookAtPlayerGoal
 *  net.minecraft.world.entity.ai.goal.RandomLookAroundGoal
 *  net.minecraft.world.entity.ai.goal.RandomStrollGoal
 *  net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal
 *  net.minecraft.world.entity.ai.navigation.PathNavigation
 *  net.minecraft.world.entity.monster.Monster
 *  net.minecraft.world.entity.player.Player
 *  net.minecraft.world.level.Level
 *  net.minecraft.world.level.LevelAccessor
 *  net.minecraft.world.level.LevelReader
 *  net.minecraft.world.level.block.RenderShape
 *  net.minecraft.world.level.block.SoundType
 *  net.minecraft.world.level.block.state.BlockState
 *  net.minecraft.world.level.pathfinder.Path
 *  net.minecraft.world.level.pathfinder.PathType
 *  org.jetbrains.annotations.Nullable
 */
package com.github.L_Ender.cataclysm.entity.AnimationMonster.BossMonsters;

import com.github.L_Ender.cataclysm.client.particle.Options.RingParticleOptions;
import com.github.L_Ender.cataclysm.config.CMCommonConfig;
import com.github.L_Ender.cataclysm.entity.AnimationMonster.AI.SimpleAnimationGoal;
import com.github.L_Ender.cataclysm.entity.AnimationMonster.BossMonsters.LLibrary_Boss_Monster;
import com.github.L_Ender.cataclysm.entity.effect.ScreenShake_Entity;
import com.github.L_Ender.cataclysm.entity.etc.CMEntityMoveHelper;
import com.github.L_Ender.cataclysm.entity.etc.SmartBodyHelper2;
import com.github.L_Ender.cataclysm.entity.etc.path.CMPathNavigateGround;
import com.github.L_Ender.cataclysm.entity.projectile.Amethyst_Cluster_Projectile_Entity;
import com.github.L_Ender.cataclysm.entity.projectile.EarthQuake_Entity;
import com.github.L_Ender.cataclysm.init.ModEntities;
import com.github.L_Ender.cataclysm.init.ModSounds;
import com.github.L_Ender.cataclysm.util.EntityUtil;
import com.github.L_Ender.lionfishapi.server.animation.Animation;
import com.github.L_Ender.lionfishapi.server.animation.IAnimatedEntity;
import java.util.EnumSet;
import java.util.List;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.util.TimeUtil;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySelector;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.BodyRotationControl;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.level.pathfinder.PathType;
import org.jetbrains.annotations.Nullable;

public class Amethyst_Crab_Entity
extends LLibrary_Boss_Monster
implements NeutralMob {
    public static final Animation CRAB_SMASH = Animation.create((int)53);
    public static final Animation CRAB_SMASH_THREE = Animation.create((int)77);
    public static final Animation CRAB_DEATH = Animation.create((int)114);
    public static final Animation CRAB_BURROW = Animation.create((int)65);
    public static final Animation CRAB_BITE = Animation.create((int)48);
    private static final UniformInt PERSISTENT_ANGER_TIME = TimeUtil.rangeOfSeconds((int)20, (int)39);
    private int remainingPersistentAngerTime;
    private int despawnTime = 4000;
    public static final int BURROW_ATTACK_COOLDOWN = 240;
    private int burrow_cooldown = 0;
    @Nullable
    private UUID persistentAngerTarget;

    public Amethyst_Crab_Entity(EntityType entity, Level world) {
        super(entity, world);
        this.xpReward = 50;
        this.moveControl = new CMEntityMoveHelper((Mob)this, 45.0f);
        this.setPathfindingMalus(PathType.UNPASSABLE_RAIL, 0.0f);
        this.setPathfindingMalus(PathType.WATER, -1.0f);
        this.setConfigattribute((LivingEntity)this, CMCommonConfig.AmethystCrab.healthMultiplier, CMCommonConfig.AmethystCrab.attackMultiplier);
    }

    @Override
    public Animation[] getAnimations() {
        return new Animation[]{NO_ANIMATION, CRAB_SMASH, CRAB_SMASH_THREE, CRAB_DEATH, CRAB_BURROW, CRAB_BITE};
    }

    protected void registerGoals() {
        this.goalSelector.addGoal(2, (Goal)new CrabMoveGoal(this, false, 1.0));
        this.goalSelector.addGoal(0, (Goal)new CrabSmashGoal(this, CRAB_SMASH));
        this.goalSelector.addGoal(0, (Goal)new CrabAttack(this, CRAB_SMASH_THREE, 10));
        this.goalSelector.addGoal(0, (Goal)new CrabBurrow(this, CRAB_BURROW));
        this.goalSelector.addGoal(0, (Goal)new CrabAttack(this, CRAB_BITE, 17));
        this.goalSelector.addGoal(5, (Goal)new RandomStrollGoal((PathfinderMob)this, 1.0, 80));
        this.goalSelector.addGoal(7, (Goal)new LookAtPlayerGoal((Mob)this, Player.class, 8.0f));
        this.goalSelector.addGoal(8, (Goal)new RandomLookAroundGoal((Mob)this));
        this.targetSelector.addGoal(1, (Goal)new HurtByTargetGoal((PathfinderMob)this, new Class[0]));
    }

    public static AttributeSupplier.Builder amethyst_crab() {
        return Monster.createMonsterAttributes().add(Attributes.FOLLOW_RANGE, 20.0).add(Attributes.MOVEMENT_SPEED, (double)0.28f).add(Attributes.ATTACK_DAMAGE, 13.0).add(Attributes.MAX_HEALTH, 200.0).add(Attributes.ARMOR, 10.0).add(Attributes.STEP_HEIGHT, 1.5).add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
    }

    protected int decreaseAirSupply(int air) {
        return air;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder p_326229_) {
        super.defineSynchedData(p_326229_);
    }

    public boolean isKrusty() {
        String s = ChatFormatting.stripFormatting((String)this.getName().getString());
        return s != null && (s.toLowerCase().contains("eugene harold krabs") || s.toLowerCase().contains("mr.krabs"));
    }

    @Override
    public void addAdditionalSaveData(CompoundTag compound) {
        super.addAdditionalSaveData(compound);
        this.addPersistentAngerSaveData(compound);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag compound) {
        super.readAdditionalSaveData(compound);
        this.readPersistentAngerSaveData(this.level(), compound);
    }

    @Override
    public boolean hurt(DamageSource source, float damage) {
        if (this.getAnimation() == CRAB_BURROW && this.getAnimationTick() > 9 && this.getAnimationTick() < 52 && !source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            this.playSound(SoundEvents.ANVIL_LAND, 0.4f, 2.0f);
            return false;
        }
        return super.hurt(source, damage);
    }

    public boolean checkSpawnRules(LevelAccessor worldIn, MobSpawnType spawnReasonIn) {
        return ModEntities.rollSpawn(CMCommonConfig.Spawning.AmethystCrabSpawnRolls, this.getRandom(), spawnReasonIn);
    }

    public static boolean canCrabSpawnSpawnRules(EntityType<? extends Amethyst_Crab_Entity> p_219020_, LevelAccessor p_219021_, MobSpawnType p_219022_, BlockPos p_219023_, RandomSource p_219024_) {
        return Amethyst_Crab_Entity.checkAnyLightMonsterSpawnRules(p_219020_, (LevelAccessor)p_219021_, (MobSpawnType)p_219022_, (BlockPos)p_219023_, (RandomSource)p_219024_);
    }

    @Override
    public void tick() {
        super.tick();
        this.repelEntities(1.7f, 3.7f, 1.7f, 1.7f);
        if (this.burrow_cooldown > 0) {
            --this.burrow_cooldown;
        }
        if (this.getdespawnTimee() > 0) {
            this.setdespawnTime(this.getdespawnTimee() - 1);
        }
    }

    public void aiStep() {
        super.aiStep();
        if (!this.level().isClientSide && this.isAlive() && this.tickCount % 20 == 0) {
            this.heal(2.0f * (float)CMCommonConfig.AmethystCrab.healthMultiplier);
        }
        if (this.getAnimation() == CRAB_SMASH && this.getAnimationTick() == 22) {
            this.AreaAttack(4.0f, 4.0f, 70.0f, 1.25f, 120);
            this.playSound((SoundEvent)ModSounds.EXPLOSION.get(), 1.0f, 1.0f + this.getRandom().nextFloat() * 0.1f);
            this.Attackparticle(2.4f, -0.4f);
            ScreenShake_Entity.ScreenShake(this.level(), this.position(), 15.0f, 0.1f, 0, 20);
        }
        if (this.getAnimation() == CRAB_SMASH_THREE) {
            if (this.getAnimationTick() == 16) {
                this.Attackparticle(2.2f, -0.2f);
                this.EarthQuakeSummon(2.2f, -0.2f);
                this.playSound((SoundEvent)ModSounds.EXPLOSION.get(), 1.0f, 1.0f + this.getRandom().nextFloat() * 0.1f);
                ScreenShake_Entity.ScreenShake(this.level(), this.position(), 15.0f, 0.1f, 0, 20);
            }
            if (this.getAnimationTick() == 36) {
                this.Attackparticle(1.8f, -1.5f);
                this.EarthQuakeSummon(1.8f, -1.5f);
                this.playSound((SoundEvent)ModSounds.EXPLOSION.get(), 1.0f, 1.0f + this.getRandom().nextFloat() * 0.1f);
                ScreenShake_Entity.ScreenShake(this.level(), this.position(), 15.0f, 0.1f, 0, 20);
            }
            if (this.getAnimationTick() == 56) {
                this.Attackparticle(1.7f, 1.3f);
                this.EarthQuakeSummon(1.7f, 1.3f);
                this.playSound((SoundEvent)ModSounds.EXPLOSION.get(), 1.0f, 1.0f + this.getRandom().nextFloat() * 0.1f);
                ScreenShake_Entity.ScreenShake(this.level(), this.position(), 15.0f, 0.1f, 0, 20);
            }
        }
        if (this.getAnimation() == CRAB_BURROW) {
            if (this.getAnimationTick() == 1 || this.getAnimationTick() == 4 || this.getAnimationTick() == 7 || this.getAnimationTick() == 10) {
                this.BurrowSound();
                this.BurrowParticle(0.6f, 0.0f, 2.0f);
            }
            if (this.getAnimationTick() == 39 || this.getAnimationTick() == 42 || this.getAnimationTick() == 45 || this.getAnimationTick() == 48) {
                this.BurrowParticle(0.6f, 0.0f, 2.0f);
                this.BurrowSound();
            }
        }
        if (this.getAnimation() == CRAB_BITE) {
            if (this.getAnimationTick() == 14) {
                this.playSound((SoundEvent)ModSounds.CRAB_BITE.get(), 1.0f, 1.0f + this.getRandom().nextFloat() * 0.1f);
            }
            if (this.getAnimationTick() == 17) {
                this.AreaAttack(4.5f, 4.5f, 110.0f, 1.25f, 120);
            }
        }
    }

    private void AreaAttack(float range, float height, float arc, float damage, int shieldbreakticks) {
        List<LivingEntity> entitiesHit = this.getEntityLivingBaseNearby(range, height, range, range);
        if (!this.level().isClientSide) {
            DamageSource damagesource = this.damageSources().mobAttack((LivingEntity)this);
            for (LivingEntity entityHit : entitiesHit) {
                float entityHitAngle = (float)((Math.atan2(entityHit.getZ() - this.getZ(), entityHit.getX() - this.getX()) * 57.29577951308232 - 90.0) % 360.0);
                float entityAttackingAngle = this.yBodyRot % 360.0f;
                if (entityHitAngle < 0.0f) {
                    entityHitAngle += 360.0f;
                }
                if (entityAttackingAngle < 0.0f) {
                    entityAttackingAngle += 360.0f;
                }
                float entityRelativeAngle = entityHitAngle - entityAttackingAngle;
                float entityHitDistance = (float)Math.sqrt((entityHit.getZ() - this.getZ()) * (entityHit.getZ() - this.getZ()) + (entityHit.getX() - this.getX()) * (entityHit.getX() - this.getX()));
                if (!(entityHitDistance <= range && entityRelativeAngle <= arc / 2.0f && entityRelativeAngle >= -arc / 2.0f || entityRelativeAngle >= 360.0f - arc / 2.0f) && !(entityRelativeAngle <= -360.0f + arc / 2.0f) || entityHit instanceof Amethyst_Crab_Entity) continue;
                entityHit.hurt(damagesource, (float)this.getAttributeValue(Attributes.ATTACK_DAMAGE) * damage);
                if (!entityHit.isDamageSourceBlocked(damagesource) || !(entityHit instanceof Player)) continue;
                Player player = (Player)entityHit;
                if (shieldbreakticks <= 0) continue;
                EntityUtil.disableShield(player, shieldbreakticks);
            }
        }
    }

    private void Attackparticle(float vec, float math) {
        if (this.level().isClientSide) {
            float f = Mth.cos((float)(this.yBodyRot * ((float)Math.PI / 180)));
            float f1 = Mth.sin((float)(this.yBodyRot * ((float)Math.PI / 180)));
            double theta = (double)this.yBodyRot * (Math.PI / 180);
            double vecX = Math.cos(theta += 1.5707963267948966);
            double vecZ = Math.sin(theta);
            for (int i1 = 0; i1 < 80 + this.random.nextInt(12); ++i1) {
                double DeltaMovementX = this.getRandom().nextGaussian() * 0.07;
                double DeltaMovementY = this.getRandom().nextGaussian() * 0.07;
                double DeltaMovementZ = this.getRandom().nextGaussian() * 0.07;
                float angle = (float)Math.PI / 180 * this.yBodyRot + (float)i1;
                double extraX = 1.0 * (double)Mth.sin((float)((float)(Math.PI + (double)angle)));
                double extraY = 0.3f;
                double extraZ = 1.0 * (double)Mth.cos((float)angle);
                int hitX = Mth.floor((double)(this.getX() + (double)vec * vecX + extraX));
                int hitY = Mth.floor((double)this.getY());
                int hitZ = Mth.floor((double)(this.getZ() + (double)vec * vecZ + extraZ));
                BlockPos hit = new BlockPos(hitX, hitY, hitZ);
                BlockState block = this.level().getBlockState(hit.below());
                if (block.getRenderShape() == RenderShape.INVISIBLE) continue;
                this.level().addParticle((ParticleOptions)new BlockParticleOption(ParticleTypes.BLOCK, block), this.getX() + (double)vec * vecX + extraX + (double)(f * math), this.getY() + extraY, this.getZ() + (double)vec * vecZ + extraZ + (double)(f1 * math), DeltaMovementX, DeltaMovementY, DeltaMovementZ);
            }
            this.level().addParticle((ParticleOptions)new RingParticleOptions(0.0f, 1.5707964f, 25, 255, 255, 255, 1.0f, 25.0f, false, 2), this.getX() + (double)vec * vecX + (double)(f * math), this.getY() + (double)0.3f, this.getZ() + (double)vec * vecZ + (double)(f1 * math), 0.0, 0.0, 0.0);
        }
    }

    private void BurrowParticle(float vec, float math, float size) {
        if (this.level().isClientSide) {
            for (int i1 = 0; i1 < 80 + this.random.nextInt(12); ++i1) {
                double DeltaMovementX = this.getRandom().nextGaussian() * 0.07;
                double DeltaMovementY = this.getRandom().nextGaussian() * 0.1;
                double DeltaMovementZ = this.getRandom().nextGaussian() * 0.07;
                float angle = (float)Math.PI / 180 * this.yBodyRot + (float)i1;
                float f = Mth.cos((float)(this.yBodyRot * ((float)Math.PI / 180)));
                float f1 = Mth.sin((float)(this.yBodyRot * ((float)Math.PI / 180)));
                double extraX = size * Mth.sin((float)((float)(Math.PI + (double)angle)));
                double extraY = 0.3f;
                double extraZ = size * Mth.cos((float)angle);
                double theta = (double)this.yBodyRot * (Math.PI / 180);
                double vecX = Math.cos(theta += 1.5707963267948966);
                double vecZ = Math.sin(theta);
                int hitX = Mth.floor((double)(this.getX() + (double)vec * vecX + extraX));
                int hitY = Mth.floor((double)this.getY());
                int hitZ = Mth.floor((double)(this.getZ() + (double)vec * vecZ + extraZ));
                BlockPos hit = new BlockPos(hitX, hitY, hitZ);
                BlockState block = this.level().getBlockState(hit.below());
                this.level().addParticle((ParticleOptions)new BlockParticleOption(ParticleTypes.BLOCK, block), this.getX() + (double)vec * vecX + extraX + (double)(f * math), this.getY() + extraY, this.getZ() + (double)vec * vecZ + extraZ + (double)(f1 * math), DeltaMovementX, DeltaMovementY, DeltaMovementZ);
            }
        }
    }

    private void BurrowSound() {
        float angle = (float)Math.PI / 180 * this.yBodyRot;
        double extraX = 1.0 * (double)Mth.sin((float)((float)(Math.PI + (double)angle)));
        double extraZ = 1.0 * (double)Mth.cos((float)angle);
        int hitX = Mth.floor((double)(this.getX() + extraX));
        int hitY = Mth.floor((double)this.getY());
        int hitZ = Mth.floor((double)(this.getZ() + extraZ));
        BlockPos hit = new BlockPos(hitX, hitY, hitZ);
        BlockState block = this.level().getBlockState(hit.below());
        SoundType soundtype = block.getSoundType((LevelReader)this.level(), hit, (Entity)this);
        this.level().playSound((Player)null, (Entity)this, soundtype.getBreakSound(), SoundSource.HOSTILE, 3.0f, 0.8f + this.getRandom().nextFloat() * 0.1f);
    }

    private void EarthQuakeSummon(float vec, float math) {
        float f = Mth.cos((float)(this.yBodyRot * ((float)Math.PI / 180)));
        float f1 = Mth.sin((float)(this.yBodyRot * ((float)Math.PI / 180)));
        double theta = (double)this.yBodyRot * (Math.PI / 180);
        double vecX = Math.cos(theta += 1.5707963267948966);
        double vecZ = Math.sin(theta);
        int quakeCount = 16;
        float angle = 22.5f;
        for (int i = 0; i < 16; ++i) {
            EarthQuake_Entity peq = new EarthQuake_Entity(this.level(), (LivingEntity)this);
            peq.setDamage((float)CMCommonConfig.AmethystCrab.EarthQuakeDamage);
            peq.shootFromRotation((Entity)this, 0.0f, angle * (float)i, 0.0f, 0.25f, 0.0f);
            peq.setPos(this.getX() + (double)vec * vecX + (double)(f * math), this.getY(), this.getZ() + (double)vec * vecZ + (double)(f1 * math));
            this.level().addFreshEntity((Entity)peq);
        }
    }

    @Override
    protected void repelEntities(float x, float y, float z, float radius) {
        super.repelEntities(x, y, z, radius);
    }

    @Override
    public boolean canBePushedByEntity(Entity entity) {
        return false;
    }

    @Override
    @Nullable
    public Animation getDeathAnimation() {
        return CRAB_DEATH;
    }

    protected SoundEvent getHurtSound(DamageSource damageSourceIn) {
        return (SoundEvent)ModSounds.CRAB_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return (SoundEvent)ModSounds.CRAB_DEATH.get();
    }

    protected BodyRotationControl createBodyControl() {
        return new SmartBodyHelper2((Mob)this);
    }

    protected PathNavigation createNavigation(Level worldIn) {
        return new CMPathNavigateGround((Mob)this, worldIn);
    }

    public void setRemainingPersistentAngerTime(int p_32515_) {
        this.remainingPersistentAngerTime = p_32515_;
    }

    public int getRemainingPersistentAngerTime() {
        return this.remainingPersistentAngerTime;
    }

    public void setdespawnTime(int p_32515_) {
        this.despawnTime = p_32515_;
    }

    public int getdespawnTimee() {
        return this.despawnTime;
    }

    @Override
    public boolean removeWhenFarAway(double p_21542_) {
        return super.removeWhenFarAway(p_21542_) && this.despawnTime >= 0;
    }

    @Nullable
    public UUID getPersistentAngerTarget() {
        return this.persistentAngerTarget;
    }

    public void setPersistentAngerTarget(@javax.annotation.Nullable UUID p_32509_) {
        this.persistentAngerTarget = p_32509_;
    }

    public void startPersistentAngerTimer() {
        this.setRemainingPersistentAngerTime(PERSISTENT_ANGER_TIME.sample(this.random));
    }

    static class CrabMoveGoal
    extends Goal {
        private final Amethyst_Crab_Entity crab;
        private final boolean followingTargetEvenIfNotSeen;
        private Path path;
        private int delayCounter;
        protected final double moveSpeed;

        public CrabMoveGoal(Amethyst_Crab_Entity boss, boolean followingTargetEvenIfNotSeen, double moveSpeed) {
            this.crab = boss;
            this.followingTargetEvenIfNotSeen = followingTargetEvenIfNotSeen;
            this.moveSpeed = moveSpeed;
            this.setFlags(EnumSet.of(Goal.Flag.LOOK, Goal.Flag.MOVE));
        }

        public boolean canUse() {
            LivingEntity target = this.crab.getTarget();
            return target != null && target.isAlive() && this.crab.getAnimation() == IAnimatedEntity.NO_ANIMATION;
        }

        public void stop() {
            this.crab.getNavigation().stop();
            LivingEntity livingentity = this.crab.getTarget();
            if (!EntitySelector.NO_CREATIVE_OR_SPECTATOR.test(livingentity)) {
                this.crab.setTarget(null);
            }
            this.crab.setAggressive(false);
            this.crab.getNavigation().stop();
        }

        public boolean canContinueToUse() {
            LivingEntity target = this.crab.getTarget();
            if (target == null) {
                return false;
            }
            if (!target.isAlive()) {
                return false;
            }
            if (!this.followingTargetEvenIfNotSeen) {
                return !this.crab.getNavigation().isDone();
            }
            if (!this.crab.isWithinRestriction(target.blockPosition())) {
                return false;
            }
            return !(target instanceof Player) || !target.isSpectator() && !((Player)target).isCreative();
        }

        public void start() {
            this.crab.getNavigation().moveTo(this.path, this.moveSpeed);
            this.crab.setAggressive(true);
        }

        public boolean requiresUpdateEveryTick() {
            return true;
        }

        public void tick() {
            LivingEntity target = this.crab.getTarget();
            if (target != null) {
                this.crab.getLookControl().setLookAt((Entity)target, 30.0f, 30.0f);
                double distSq = this.crab.distanceToSqr(target.getX(), target.getBoundingBox().minY, target.getZ());
                if (--this.delayCounter <= 0) {
                    this.delayCounter = 4 + this.crab.getRandom().nextInt(7);
                    if (distSq > Math.pow(this.crab.getAttribute(Attributes.FOLLOW_RANGE).getValue(), 2.0)) {
                        if (!this.crab.isPathFinding() && !this.crab.getNavigation().moveTo((Entity)target, 1.0)) {
                            this.delayCounter += 5;
                        }
                    } else {
                        this.crab.getNavigation().moveTo((Entity)target, this.moveSpeed);
                    }
                }
                if (target.isAlive() && this.crab.getAnimation() == IAnimatedEntity.NO_ANIMATION) {
                    if (this.crab.burrow_cooldown <= 0 && this.crab.getRandom().nextFloat() * 100.0f < 6.0f && (double)this.crab.distanceTo((Entity)target) <= 8.0) {
                        this.crab.setAnimation(CRAB_BURROW);
                    } else if (this.crab.getRandom().nextFloat() * 100.0f < 24.0f && (double)this.crab.distanceTo((Entity)target) <= 3.75) {
                        if (this.crab.random.nextInt(2) == 0) {
                            this.crab.setAnimation(CRAB_BITE);
                        } else {
                            this.crab.setAnimation(CRAB_SMASH);
                        }
                    } else if (this.crab.getRandom().nextFloat() * 100.0f < 16.0f && (double)this.crab.distanceTo((Entity)target) <= 3.75 && target.onGround()) {
                        this.crab.setAnimation(CRAB_SMASH_THREE);
                    }
                }
            }
        }
    }

    static class CrabSmashGoal
    extends SimpleAnimationGoal<Amethyst_Crab_Entity> {
        public CrabSmashGoal(Amethyst_Crab_Entity entity, Animation animation) {
            super(entity, animation);
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.JUMP, Goal.Flag.LOOK));
        }

        public void start() {
            LivingEntity target = ((Amethyst_Crab_Entity)this.entity).getTarget();
            if (target != null) {
                ((Amethyst_Crab_Entity)this.entity).getLookControl().setLookAt((Entity)target, 30.0f, 90.0f);
            }
            super.start();
        }

        public void tick() {
            LivingEntity target = ((Amethyst_Crab_Entity)this.entity).getTarget();
            if (((Amethyst_Crab_Entity)this.entity).getAnimationTick() < 19 && target != null) {
                ((Amethyst_Crab_Entity)this.entity).lookAt((Entity)target, 30.0f, 30.0f);
                ((Amethyst_Crab_Entity)this.entity).getNavigation().moveTo((Entity)target, 1.0);
                ((Amethyst_Crab_Entity)this.entity).getLookControl().setLookAt((Entity)target, 30.0f, 30.0f);
            } else {
                ((Amethyst_Crab_Entity)this.entity).setYRot(((Amethyst_Crab_Entity)this.entity).yRotO);
            }
            if (((Amethyst_Crab_Entity)this.entity).getAnimationTick() == 19) {
                ((Amethyst_Crab_Entity)this.entity).getNavigation().stop();
            }
        }
    }

    static class CrabAttack
    extends SimpleAnimationGoal<Amethyst_Crab_Entity> {
        private final int look;

        public CrabAttack(Amethyst_Crab_Entity entity, Animation animation, int look) {
            super(entity, animation);
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.JUMP, Goal.Flag.LOOK));
            this.look = look;
        }

        public void start() {
            LivingEntity target = ((Amethyst_Crab_Entity)this.entity).getTarget();
            if (target != null) {
                ((Amethyst_Crab_Entity)this.entity).getLookControl().setLookAt((Entity)target, 30.0f, 90.0f);
            }
            super.start();
        }

        public void tick() {
            LivingEntity target = ((Amethyst_Crab_Entity)this.entity).getTarget();
            if (((Amethyst_Crab_Entity)this.entity).getAnimationTick() < this.look && target != null) {
                ((Amethyst_Crab_Entity)this.entity).lookAt((Entity)target, 30.0f, 30.0f);
                ((Amethyst_Crab_Entity)this.entity).getLookControl().setLookAt((Entity)target, 30.0f, 30.0f);
            } else {
                ((Amethyst_Crab_Entity)this.entity).setYRot(((Amethyst_Crab_Entity)this.entity).yRotO);
            }
        }
    }

    static class CrabBurrow
    extends SimpleAnimationGoal<Amethyst_Crab_Entity> {
        public CrabBurrow(Amethyst_Crab_Entity entity, Animation animation) {
            super(entity, animation);
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.JUMP, Goal.Flag.LOOK));
        }

        public void start() {
            LivingEntity target = ((Amethyst_Crab_Entity)this.entity).getTarget();
            if (target != null) {
                ((Amethyst_Crab_Entity)this.entity).getLookControl().setLookAt((Entity)target, 30.0f, 90.0f);
            }
            ((Amethyst_Crab_Entity)this.entity).burrow_cooldown = 240;
            super.start();
        }

        public void tick() {
            LivingEntity target = ((Amethyst_Crab_Entity)this.entity).getTarget();
            if (((Amethyst_Crab_Entity)this.entity).getAnimationTick() < 48 && target != null) {
                ((Amethyst_Crab_Entity)this.entity).lookAt((Entity)target, 30.0f, 30.0f);
                ((Amethyst_Crab_Entity)this.entity).getLookControl().setLookAt((Entity)target, 30.0f, 30.0f);
            } else {
                ((Amethyst_Crab_Entity)this.entity).setYRot(((Amethyst_Crab_Entity)this.entity).yRotO);
            }
            if (((Amethyst_Crab_Entity)this.entity).getAnimationTick() == 50) {
                for (int i = 0; i < 32; ++i) {
                    float throwAngle = (float)i * (float)Math.PI / 16.0f;
                    double sx = ((Amethyst_Crab_Entity)this.entity).getX() + (double)(Mth.cos((float)throwAngle) * 1.0f);
                    double sy = ((Amethyst_Crab_Entity)this.entity).getY() + (double)((Amethyst_Crab_Entity)this.entity).getBbHeight() * 0.2;
                    double sz = ((Amethyst_Crab_Entity)this.entity).getZ() + (double)(Mth.sin((float)throwAngle) * 1.0f);
                    double vx = Mth.cos((float)throwAngle);
                    double vy = 0.0f + ((Amethyst_Crab_Entity)this.entity).random.nextFloat() * 0.3f;
                    double vz = Mth.sin((float)throwAngle);
                    double v3 = Mth.sqrt((float)((float)(vx * vx + vz * vz)));
                    Amethyst_Cluster_Projectile_Entity projectile = new Amethyst_Cluster_Projectile_Entity((EntityType<Amethyst_Cluster_Projectile_Entity>)((EntityType)ModEntities.AMETHYST_CLUSTER_PROJECTILE.get()), ((Amethyst_Crab_Entity)this.entity).level(), (LivingEntity)this.entity, (float)CMCommonConfig.AmethystCrab.AmethystClusterDamage);
                    projectile.moveTo(sx, sy, sz, (float)i * 11.25f, ((Amethyst_Crab_Entity)this.entity).getXRot());
                    float speed = 0.8f;
                    projectile.shoot(vx, vy + v3 * (double)0.2f, vz, speed, 1.0f);
                    ((Amethyst_Crab_Entity)this.entity).level().addFreshEntity((Entity)projectile);
                }
            }
        }
    }
}
