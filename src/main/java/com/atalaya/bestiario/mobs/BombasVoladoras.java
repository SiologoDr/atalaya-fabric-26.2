package com.atalaya.bestiario.mobs;

import com.atalaya.bestiario.BestiaEntity;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.BombaBestia;
import com.atalaya.bestiario.Fichas;
import com.atalaya.bestiario.Oido;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * Las cuatro bombas voladoras (la base, BombaBestia): cada una con su estallido y lo suyo.
 *
 * <pre>
 *   Ambar     la amarilla: sale sola de noche (tambien en el aire y bajo tierra); su estallido seca el agua de alrededor
 *             (el agua, lo anegado y las plantas del agua), con su vapor
 *   Carmesi   la roja: la mas rapida; su estallido prende fuego
 *   Negra     la mas grande y la mas fuerte: no se la puede empujar; sale de noche al aire libre (no en las cuevas)
 *   Abismo    la del Warden: ciega, te busca por el ruido (como el Creeper Ciego) y su estallido deja la oscuridad;
 *             sale en la Oscuridad Profunda
 * </pre>
 */
public final class BombasVoladoras {

    private BombasVoladoras() {
    }

    private static AttributeSupplier.Builder base(double vida, double vuelo) {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, vida)
                .add(Attributes.FLYING_SPEED, vuelo)
                .add(Attributes.MOVEMENT_SPEED, vuelo * 0.6)
                .add(Attributes.FOLLOW_RANGE, 32.0);
    }

    // ------------------------------------------------------------------
    //  La Bomba Ambar
    // ------------------------------------------------------------------

    public static class Ambar extends BombaBestia {

        private static final int SECA = 5;

        public Ambar(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            radio = 3.0F;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(12.0, 0.45);
        }

        @Override
        public Bestia bestia() {
            return Fichas.AMBAR;
        }

        @Override
        protected void alEstallar(ServerLevel nivel) {
            particulas(nivel, "chispa", getX(), getY() + 0.5, getZ(), 30, 1.0, 0.6, 0.3);
            particulas(nivel, "cristal", getX(), getY() + 0.5, getZ(), 24, 0.8, 0.5, 0.35);
            if (!nivel.getGameRules().get(net.minecraft.world.level.gamerules.GameRules.MOB_GRIEFING)) {
                return;
            }
            BlockPos c = blockPosition();
            int secadas = 0;
            for (BlockPos p : BlockPos.betweenClosed(c.offset(-SECA, -SECA, -SECA), c.offset(SECA, SECA, SECA))) {
                if (p.distSqr(c) > SECA * SECA) {
                    continue;
                }
                BlockState b = nivel.getBlockState(p);
                if (!b.getFluidState().is(FluidTags.WATER)) {
                    continue;
                }
                if (b.hasProperty(BlockStateProperties.WATERLOGGED)) {
                    nivel.setBlock(p, b.setValue(BlockStateProperties.WATERLOGGED, false), 3);
                } else {
                    nivel.setBlock(p, Blocks.AIR.defaultBlockState(), 3);
                }
                if (secadas++ % 6 == 0) {
                    particulas(nivel, "vapor", p.getX() + 0.5, p.getY() + 0.6, p.getZ() + 0.5, 1, 0.2, 0.1, 0.02);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    //  La Bomba Carmesi
    // ------------------------------------------------------------------

    public static class Carmesi extends BombaBestia {

        public Carmesi(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            radio = 3.0F;
            fuego = true;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(10.0, 0.65);
        }

        @Override
        public Bestia bestia() {
            return Fichas.CARMESI;
        }

        @Override
        protected void alEstallar(ServerLevel nivel) {
            particulas(nivel, "brasa", getX(), getY() + 0.5, getZ(), 40, 1.2, 0.7, 0.25);
            particulas(nivel, "esquirla", getX(), getY() + 0.5, getZ(), 24, 0.8, 0.5, 0.35);
        }
    }

    // ------------------------------------------------------------------
    //  La Bomba Negra
    // ------------------------------------------------------------------

    public static class Negra extends BombaBestia {

        public Negra(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            radio = 4.5F;
            mecha = 24;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(24.0, 0.38).add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.ARMOR, 6.0);
        }

        /** Sale de noche al aire libre: no en las cuevas. */
        public static boolean alAireLibre(EntityType<?> tipo, ServerLevelAccessor nivel, EntitySpawnReason motivo,
                                          BlockPos pos, RandomSource azar) {
            return motivo != EntitySpawnReason.NATURAL || nivel.canSeeSky(pos);
        }

        @Override
        public Bestia bestia() {
            return Fichas.NEGRA;
        }

        @Override
        public boolean isPushable() {
            return false;
        }

        @Override
        protected void alEstallar(ServerLevel nivel) {
            particulas(nivel, "humo", getX(), getY() + 0.6, getZ(), 30, 1.6, 1.0, 0.08);
            particulas(nivel, "esquirla", getX(), getY() + 0.6, getZ(), 36, 1.0, 0.6, 0.45);
        }
    }

    // ------------------------------------------------------------------
    //  La Bomba del Abismo
    // ------------------------------------------------------------------

    public static class Abismo extends BombaBestia {

        private @Nullable Vec3 oido;
        private int sinOir = 1000;

        public Abismo(EntityType<? extends Monster> tipo, Level nivel) {
            super(tipo, nivel);
            radio = 3.0F;
        }

        public static AttributeSupplier.Builder atributos() {
            return base(16.0, 0.5);
        }

        @Override
        public Bestia bestia() {
            return Fichas.ABISMO;
        }

        @Override
        protected void objetivos() {
            // Ciega: no ve a nadie; la presa se la pone el oido.
        }

        @Override
        protected boolean aTiro(LivingEntity objetivo) {
            return sinOir < 20 || distanceToSqr(objetivo) < 2.0 * 2.0;
        }

        @Override
        public void tick() {
            super.tick();
            if (level() instanceof ServerLevel nivel && isAlive() && tickCount % 2 == 0) {
                escuchar(nivel);
            }
        }

        private void escuchar(ServerLevel nivel) {
            sinOir += 2;
            ServerPlayer mejor = null;
            double mejorD = Double.MAX_VALUE;
            for (ServerPlayer p : nivel.players()) {
                if (p.isSpectator() || p.isCreative() || !p.isAlive()) {
                    continue;
                }
                double d = p.distanceToSqr(this);
                double alcance = Math.max(Oido.alcance(p), d < 4.0 ? 2.0 : 0.0);
                if (alcance > 0 && d < alcance * alcance && d < mejorD) {
                    mejor = p;
                    mejorD = d;
                }
            }
            if (mejor == null) {
                if (sinOir > 100 && getTarget() != null && !encendida()) {
                    setTarget(null);
                    oido = null;
                }
                return;
            }
            if (getTarget() != mejor) {
                sonar("ambiente", 1.2F, 1.4F);
            }
            oido = mejor.position();
            sinOir = 0;
            setTarget(mejor);
        }

        @Override
        protected void alEstallar(ServerLevel nivel) {
            particulas(nivel, "alma", getX(), getY() + 0.5, getZ(), 40, 1.4, 0.8, 0.15);
            particulas(nivel, "sculk", getX(), getY() + 0.5, getZ(), 30, 1.0, 0.6, 0.35);
            for (ServerPlayer p : nivel.players()) {
                if (!p.isSpectator() && !p.isCreative() && p.distanceToSqr(this) < 10 * 10) {
                    BestiaEntity.efecto(p, MobEffects.DARKNESS, 200, 0, this);
                }
            }
        }
    }
}
