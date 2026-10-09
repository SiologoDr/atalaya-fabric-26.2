package com.atalaya.entity;

import com.atalaya.item.AtalayaItems;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La pila de balas de un Canon del Naufragio: un monton de balas de hierro
 * negras junto al canon. Con la mano libre, clic derecho: coges una (la Bala
 * de canon, que se mete en el canon con otro clic derecho).
 */
public class PilaBalasEntity extends Entity {

    private @Nullable NereaEntity duena;
    private @Nullable CanonNaufragioEntity canon;

    public PilaBalasEntity(EntityType<? extends PilaBalasEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    static PilaBalasEntity poner(ServerLevel nivel, NereaEntity duena, CanonNaufragioEntity canon, Vec3 donde) {
        PilaBalasEntity p = new PilaBalasEntity(AtalayaEntities.PILA_BALAS, nivel);
        p.duena = duena;
        p.canon = canon;
        p.setPos(donde.x, donde.y, donde.z);
        nivel.addFreshEntity(p);
        return p;
    }

    @Override
    protected void defineSynchedData(net.minecraft.network.syncher.SynchedEntityData.Builder datos) {
    }

    @Override
    public void tick() {
        super.tick();
        if (!level().isClientSide() && (duena == null || duena.isRemoved() || canon == null || canon.isRemoved() || canon.hunde() >= 0)) {
            discard();
        }
    }

    @Override
    public InteractionResult interact(Player p, InteractionHand mano, Vec3 donde) {
        if (mano != InteractionHand.MAIN_HAND) {
            return InteractionResult.PASS;
        }
        if (!level().isClientSide() && duena != null) {
            if (!p.getMainHandItem().isEmpty()) {
                p.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.bala_mano_libre").withStyle(ChatFormatting.GRAY));
                return InteractionResult.SUCCESS;
            }
            p.setItemInHand(InteractionHand.MAIN_HAND, MinijuegosNerea.crear(duena, AtalayaItems.BALA_CANON));
            level().playSound(null, getX(), getY() + 0.5, getZ(), AtalayaSonidos.NEREA_BALA_COGER, SoundSource.PLAYERS, 1.2F, 1.0F);
            p.sendOverlayMessage(Component.translatable("hud.atalaya.nerea.bala_cogida").withStyle(ChatFormatting.GOLD));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        return false;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 128 * 128;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
