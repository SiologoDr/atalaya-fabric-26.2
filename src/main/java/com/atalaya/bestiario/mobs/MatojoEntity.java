package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.Bestiario;
import com.atalaya.bestiario.CreeperBestia;
import com.atalaya.bestiario.Fichas;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * El Creeper Matojo (el «Creeper de Pasto» del DEDsafio 4): pequeno y muy rapido, con una mecha cortisima. No sale de
 * noche como los demas: salta de los matojos al romperlos (la hierba, los helechos, los arbustos), y tambien a veces al
 * gastar un totem (el cambio TOTEM CON TRAMPA).
 */
public class MatojoEntity extends CreeperBestia {

    public MatojoEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        mecha = 12;
        radio = 2.5F;
        alcanceMecha = 2.6;
    }

    public static AttributeSupplier.Builder atributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 10.0)
                .add(Attributes.MOVEMENT_SPEED, 0.42)
                .add(Attributes.FOLLOW_RANGE, 24.0);
    }

    @Override
    public Bestia bestia() {
        return Fichas.MATOJO;
    }

    @Override
    protected void alEstallar(ServerLevel nivel) {
        particulas(nivel, "brizna", getX(), getY() + 0.6, getZ(), 40, 0.6, 0.5, 0.35);
    }

    /** Si ese bloque es un matojo (de donde salta). */
    private static boolean esMatojo(BlockState b) {
        return b.is(Blocks.SHORT_GRASS) || b.is(Blocks.TALL_GRASS) || b.is(Blocks.FERN) || b.is(Blocks.LARGE_FERN)
                || b.is(Blocks.BUSH) || b.is(Blocks.DEAD_BUSH) || b.is(Blocks.SHORT_DRY_GRASS) || b.is(Blocks.TALL_DRY_GRASS)
                || b.getBlock() instanceof net.minecraft.world.level.block.SaplingBlock;
    }

    /** Salta uno de ahi, hacia quien lo ha despertado. */
    public static void saltar(ServerLevel nivel, BlockPos pos, Player quien) {
        MatojoEntity m = (MatojoEntity) Fichas.MATOJO.tipo.create(nivel, EntitySpawnReason.EVENT);
        if (m == null) {
            return;
        }
        m.snapTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5);
        m.setYRot(nivel.getRandom().nextFloat() * 360.0F);
        m.setTarget(quien);
        nivel.addFreshEntity(m);
        m.animar(EV_APARECE);
        m.sonar("aparece", 1.0F);
    }

    public static void registrarEventos() {
        PlayerBlockBreakEvents.AFTER.register((mundo, jugador, pos, estado, be) -> {
            if (mundo instanceof ServerLevel nivel && !jugador.isCreative() && esMatojo(estado)
                    && Bestiario.suelto(Fichas.MATOJO) && nivel.getRandom().nextFloat() < 0.04F) {
                saltar(nivel, pos, jugador);
            }
        });
    }
}
