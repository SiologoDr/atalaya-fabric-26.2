package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BestiaRed;
import com.atalaya.bestiario.Bestiario;
import com.atalaya.bestiario.CreeperBestia;
import com.atalaya.bestiario.Fichas;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * El Creeper Tarta (el «Creeper Cake» del DEDsafio): una tarta de cumpleanos con patas, chiquita y rapidisima. Su mecha
 * dura un suspiro (menos de medio segundo) y su estallido es pequeno, pero te pringa de nata: la pantalla se te llena de
 * pegotes que chorrean y tardan en irse, y vas pegajoso un rato.
 *
 * Sale por los caminos de tierra (de dia y de noche) y, a veces, salta de la mesa de crafteo cuando la usas.
 */
public class TartaEntity extends CreeperBestia {

    private static final double ALCANCE_NATA = 5.0;
    /** Cuanto falta para que a ese jugador le pueda saltar otra de la mesa (ticks del mundo). */
    private static final Map<UUID, Long> ESPERA_MESA = new HashMap<>();

    public TartaEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        mecha = 8;
        radio = 2.2F;
        alcanceMecha = 2.2;
    }

    public static AttributeSupplier.Builder atributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 8.0)
                .add(Attributes.MOVEMENT_SPEED, 0.36)
                .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    @Override
    public Bestia bestia() {
        return Fichas.TARTA;
    }

    /** Sale sobre los caminos de tierra. */
    public static boolean puedeSalir(EntityType<?> tipo, ServerLevelAccessor nivel, EntitySpawnReason motivo, BlockPos pos,
                                     RandomSource azar) {
        return motivo != EntitySpawnReason.NATURAL || nivel.getBlockState(pos.below()).is(Blocks.DIRT_PATH);
    }

    @Override
    protected void alEstallar(ServerLevel nivel) {
        particulas(nivel, "nata", getX(), getY() + 0.8, getZ(), 60, 1.2, 0.8, 0.35);
        particulas(nivel, "miga", getX(), getY() + 0.8, getZ(), 30, 1.0, 0.6, 0.3);
        for (ServerPlayer p : nivel.players()) {
            if (!p.isSpectator() && !p.isCreative() && p.distanceToSqr(this) < ALCANCE_NATA * ALCANCE_NATA) {
                BestiaRed.pantalla(p, BestiaRed.NATA, 160);
                BestiaEntity.efecto(p, MobEffects.SLOWNESS, 80, 0, this);
            }
        }
    }

    /** Salta una de la mesa de crafteo, hacia quien la usa. */
    private static void saltar(ServerLevel nivel, BlockPos mesa, ServerPlayer quien) {
        TartaEntity t = (TartaEntity) Fichas.TARTA.tipo.create(nivel, EntitySpawnReason.EVENT);
        if (t == null) {
            return;
        }
        BlockPos sitio = mesa.above();
        if (!nivel.getBlockState(sitio).isAir()) {
            return;
        }
        t.snapTo(sitio.getX() + 0.5, sitio.getY(), sitio.getZ() + 0.5, nivel.getRandom().nextFloat() * 360.0F, 0.0F);
        t.setTarget(quien);
        nivel.addFreshEntity(t);
        t.animar(EV_APARECE);
        t.sonar("aparece", 1.2F);
        t.particulas(nivel, "miga", t.getX(), t.getY() + 0.3, t.getZ(), 12, 0.3, 0.2, 0.15);
    }

    public static void registrarEventos() {
        UseBlockCallback.EVENT.register((jugador, mundo, mano, golpe) -> {
            if (mundo instanceof ServerLevel nivel && jugador instanceof ServerPlayer p && !p.isCreative() && !p.isSpectator()
                    && nivel.getBlockState(golpe.getBlockPos()).is(Blocks.CRAFTING_TABLE) && Bestiario.suelto(Fichas.TARTA)) {
                long ahora = nivel.getGameTime();
                Long hasta = ESPERA_MESA.get(p.getUUID());
                if ((hasta == null || hasta <= ahora) && nivel.getRandom().nextFloat() < 0.05F) {
                    ESPERA_MESA.put(p.getUUID(), ahora + 600);
                    saltar(nivel, golpe.getBlockPos(), p);
                }
            }
            return InteractionResult.PASS;
        });
    }
}
