package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaRed;
import com.atalaya.bestiario.CreeperBestia;
import com.atalaya.bestiario.Fichas;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WallClimberNavigation;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

/**
 * El Creeper Gelatina (el «Creeper de Fluido» del DEDsafio): de gel, translucido (se le ve el nucleo). Trepa por las
 * paredes como una arana (no hay muro que lo pare) y su estallido es mas flojo pero te deja SIN SENAL ocho segundos: la
 * pantalla se llena de estatica y no ves nada, y mientras tanto vas lento y sin fuerza para picar.
 *
 * Sale en los pantanos y en los manglares.
 */
public class GelatinaEntity extends CreeperBestia {

    /** Hasta donde llega la estatica (bloques). */
    private static final double ALCANCE_SENAL = 7.0;
    /** Lo que dura (ticks). */
    private static final int SIN_SENAL = 160;

    private boolean trepando;

    public GelatinaEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        mecha = 30;
        radio = 2.5F;
    }

    public static AttributeSupplier.Builder atributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 18.0)
                .add(Attributes.MOVEMENT_SPEED, 0.25)
                .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    @Override
    public Bestia bestia() {
        return Fichas.GELATINA;
    }

    @Override
    protected PathNavigation createNavigation(Level nivel) {
        return new WallClimberNavigation(this, nivel);
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide()) {
            trepando = horizontalCollision;
            if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 12 == 0) {
                particulas(nivel, "burbuja", getX(), getY() + 1.2, getZ(), 1, 0.25, 0.4, 0.01);
            }
        }
    }

    @Override
    public boolean onClimbable() {
        return trepando || super.onClimbable();
    }

    @Override
    protected void alEstallar(ServerLevel nivel) {
        particulas(nivel, "gota", getX(), getY() + 1.0, getZ(), 50, 1.2, 0.8, 0.4);
        particulas(nivel, "burbuja", getX(), getY() + 1.0, getZ(), 30, 1.4, 0.8, 0.1);
        for (ServerPlayer p : nivel.players()) {
            if (!p.isSpectator() && !p.isCreative() && p.distanceToSqr(this) < ALCANCE_SENAL * ALCANCE_SENAL) {
                BestiaRed.pantalla(p, BestiaRed.SIN_SENAL, SIN_SENAL);
                BestiaEntity.efecto(p, MobEffects.SLOWNESS, SIN_SENAL, 1, this);
                BestiaEntity.efecto(p, MobEffects.MINING_FATIGUE, SIN_SENAL, 1, this);
            }
        }
    }
}
