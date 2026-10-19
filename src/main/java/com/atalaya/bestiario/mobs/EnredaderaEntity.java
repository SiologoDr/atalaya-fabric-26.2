package com.atalaya.bestiario.mobs;

import com.atalaya.Atalaya;
import com.atalaya.bestiario.Atrapado;
import com.atalaya.bestiario.Bestia;
import com.atalaya.bestiario.CreeperBestia;
import com.atalaya.bestiario.Fichas;
import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

import java.util.EnumSet;
import java.util.UUID;

/**
 * El Creeper Enredadera (el «Creeper de Raiz de Azalea» del DEDsafio): no espera a tenerte al lado. Desde unos bloques
 * te lanza las lianas; si te alcanzan, te atrapan: te arrastran hasta el, no puedes andar ni saltar y, en cuanto te
 * tiene pegado, se le enciende la mecha (tres segundos). Para soltarte hay que aporrear la tecla que sale en la pantalla (cada vez una: saltar,
 * adelante, atras, izquierda o derecha; siete veces); al soltarte te aparta de un tiron y se le apaga la mecha del todo
 * (tres segundos sin poder encenderla: hay que correr). Bajo el agua, mientras te tiene, te ahogas mucho antes.
 *
 * Sale de dia y de noche en las llanuras, los prados y el bosque de flores, y en las cuevas frondosas.
 */
public class EnredaderaEntity extends CreeperBestia {

    /** Hasta donde llegan las lianas. */
    private static final double ALCANCE_LIANAS = 6.0;
    private static final Identifier ID_MOVIMIENTO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "lianas_movimiento");
    private static final Identifier ID_SALTO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "lianas_salto");

    /** Los ticks que le faltan para poder lanzar otra vez las lianas. */
    private int espera;
    /** A quien tiene atrapado (o null). */
    private @Nullable UUID presa;

    public EnredaderaEntity(EntityType<? extends Monster> tipo, Level nivel) {
        super(tipo, nivel);
        mecha = 60;
        radio = 3.0F;
        alcanceMecha = 2.6;
    }

    public static AttributeSupplier.Builder atributos() {
        return Monster.createMonsterAttributes()
                .add(Attributes.MAX_HEALTH, 22.0)
                .add(Attributes.MOVEMENT_SPEED, 0.26)
                .add(Attributes.FOLLOW_RANGE, 24.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.4);
    }

    @Override
    public Bestia bestia() {
        return Fichas.ENREDADERA;
    }

    @Override
    protected void metas() {
        goalSelector.addGoal(3, new Lianas());
        super.metas();
    }

    @Override
    public void tick() {
        super.tick();
        if (level() instanceof ServerLevel nivel && isAlive()) {
            if (espera > 0) {
                espera--;
            }
            if (presa != null) {
                sujetar(nivel);
            }
        }
    }

    /** Las lianas: con su presa a unos bloques y a la vista, las lanza; en el golpe, si la alcanzan, la atrapan. */
    private final class Lianas extends Goal {
        Lianas() {
            setFlags(EnumSet.of(Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            LivingEntity t = presa();
            if (espera > 0 || presa != null || t == null || encendido() || !(t instanceof Player)) {
                return false;
            }
            double d = distanceToSqr(t);
            return d > 2.2 * 2.2 && d < ALCANCE_LIANAS * ALCANCE_LIANAS && getSensing().hasLineOfSight(t);
        }

        @Override
        public void start() {
            LivingEntity t = presa();
            if (t != null) {
                getLookControl().setLookAt(t, 60.0F, 60.0F);
            }
            animar(EV_ATAQUE);
            sonar("latigo", 1.2F);
            espera = 70;
            luego(6, EnredaderaEntity.this::agarrar);
        }

        @Override
        public boolean canContinueToUse() {
            return false;
        }
    }

    /** El fotograma en que las lianas llegan: si sigue a tiro, la atrapa. */
    private void agarrar() {
        if (!(presa() instanceof ServerPlayer p) || !(level() instanceof ServerLevel nivel) || p.isCreative()
                || p.isSpectator() || Atrapado.atrapado(p)) {
            return;
        }
        if (distanceToSqr(p) > (ALCANCE_LIANAS + 0.8) * (ALCANCE_LIANAS + 0.8) || !getSensing().hasLineOfSight(p)) {
            return;
        }
        presa = p.getUUID();
        Atrapado.poner(p, Atrapado.PULSACIONES, random.nextInt(Atrapado.TECLAS));
        setEstado(1);
        sonar("atrapa", 1.3F);
        particulas(nivel, "hoja", p.getX(), p.getY() + 1.0, p.getZ(), 14, 0.4, 0.5, 0.08);
    }

    /** Lo arrastra hasta delante de el y lo tiene quieto; si ya se ha soltado (o se ha ido lejos), lo suelta. */
    private void sujetar(ServerLevel nivel) {
        ServerPlayer p = presa == null ? null : nivel.getServer().getPlayerList().getPlayer(presa);
        if (p == null || !p.isAlive() || p.isSpectator() || p.isCreative() || p.level() != nivel
                || p.distanceToSqr(this) > 12 * 12) {
            soltar(false);
            return;
        }
        if (!Atrapado.atrapado(p)) {
            soltar(true);
            return;
        }
        float rumbo = getYRot() * ((float) Math.PI / 180.0F);
        Vec3 punto = position().add(-Math.sin(rumbo) * 1.4, 0.05, Math.cos(rumbo) * 1.4);
        Vec3 hacia = punto.subtract(p.position());
        double d = hacia.length();
        Vec3 v = d > 0.25 ? hacia.scale(Math.min(0.45, d * 0.5) / d) : Vec3.ZERO;
        p.setDeltaMovement(v.x, Math.min(p.getDeltaMovement().y, 0.08) + v.y * 0.5, v.z);
        p.hurtMarked = true;
        frenar(p, true);
        getNavigation().stop();
        getLookControl().setLookAt(p, 30.0F, 30.0F);
        if (p.isUnderWater()) {
            p.setAirSupply(p.getAirSupply() - 3);
        }
        if (tickCount % 10 == 0) {
            particulas(nivel, "hoja", p.getX(), p.getY() + 0.9, p.getZ(), 2, 0.35, 0.5, 0.02);
        }
    }

    /** Suelta a su presa: si se ha escapado, la aparta de un tiron y se le apaga la mecha. */
    private void soltar(boolean seEscapa) {
        if (presa == null || !(level() instanceof ServerLevel nivel)) {
            presa = null;
            return;
        }
        ServerPlayer p = nivel.getServer().getPlayerList().getPlayer(presa);
        presa = null;
        setEstado(0);
        if (p == null) {
            return;
        }
        Atrapado.soltar(p);
        frenar(p, false);
        if (seEscapa) {
            Vec3 lejos = p.position().subtract(position()).multiply(1, 0, 1);
            lejos = lejos.lengthSqr() < 1.0E-4 ? new Vec3(0, 0, 1) : lejos.normalize();
            p.setDeltaMovement(lejos.x * 0.9, 0.38, lejos.z * 0.9);
            p.hurtMarked = true;
            sonar("suelta", 1.2F);
            particulas(nivel, "hoja", p.getX(), p.getY() + 1.0, p.getZ(), 18, 0.5, 0.5, 0.15);
            desactivar(60);
            espera = 100;
        }
    }

    /** Lo deja sin andar ni saltar (o se lo devuelve). */
    private static void frenar(ServerPlayer p, boolean si) {
        modificador(p, Attributes.MOVEMENT_SPEED, ID_MOVIMIENTO, si);
        modificador(p, Attributes.JUMP_STRENGTH, ID_SALTO, si);
    }

    private static void modificador(ServerPlayer p, Holder<Attribute> atributo, Identifier id, boolean poner) {
        AttributeInstance a = p.getAttribute(atributo);
        if (a == null) {
            return;
        }
        if (poner) {
            a.addOrUpdateTransientModifier(new AttributeModifier(id, -1.0, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
        } else if (a.getModifier(id) != null) {
            a.removeModifier(id);
        }
    }

    /** El jugador ha pulsado la tecla que toca (BestiaRed.Forcejeo): una pulsacion menos para soltarse. */
    public static void alForcejear(ServerPlayer p) {
        int faltan = Atrapado.faltan(p);
        if (faltan <= 0) {
            return;
        }
        Atrapado.poner(p, faltan - 1, Atrapado.tecla(p));
        net.minecraft.sounds.SoundEvent cruje = Fichas.ENREDADERA.sonido("ambiente");
        if (cruje != null) {
            p.level().playSound(null, p.getX(), p.getY(), p.getZ(), cruje, net.minecraft.sounds.SoundSource.HOSTILE, 0.6F,
                    1.3F + p.getRandom().nextFloat() * 0.3F);
        }
    }

    /** Al entrar en el mundo, nadie esta atrapado (si se salio con las lianas encima, vuelve libre). */
    public static void alEntrar(ServerPlayer p) {
        if (Atrapado.atrapado(p)) {
            Atrapado.soltar(p);
        }
        frenar(p, false);
    }

    @Override
    public void die(DamageSource fuente) {
        soltar(false);
        super.die(fuente);
    }

    @Override
    public void remove(RemovalReason motivo) {
        if (!level().isClientSide()) {
            soltar(false);
        }
        super.remove(motivo);
    }
}
