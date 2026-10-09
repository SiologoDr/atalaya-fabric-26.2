package com.atalaya.client;

import com.atalaya.entity.BalaCanonEntity;
import com.atalaya.entity.CanonNaufragioEntity;
import com.atalaya.entity.NereaEntity;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import net.minecraft.client.Minecraft;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

/**
 * La mira del Canon del Naufragio (Juan: "al estar en el canon deberia mostrar
 * como una mira"): para quien va subido, el camino que haria la bala si
 * disparara ahora, con la misma cuenta que la bala de verdad (gravedad, luego
 * el roce del aire, luego avanza), hasta donde choca. Lo pinta
 * CanonNaufragioRenderer (los puntos y la marca del impacto) y CanonMiraHud (la
 * mira en el centro y "EN EL BLANCO" si el camino da en Nerea).
 */
public final class CanonMira {

    /** Lo que se mira hacia delante (ticks de vuelo). */
    private static final int VUELO = 90;

    private static boolean activo;
    private static boolean enNerea;
    private static boolean cargado;
    private static List<Vec3> puntos = List.of();
    private static @Nullable Vec3 impacto;
    private static long calculado = -10;

    private CanonMira() {
    }

    /** Si quien juega va subido en un canon (y se acaba de calcular su camino). */
    public static boolean activo() {
        Minecraft mc = Minecraft.getInstance();
        return activo && mc.player != null && mc.player.getVehicle() instanceof CanonNaufragioEntity
                && mc.level != null && mc.level.getGameTime() - calculado < 5;
    }

    public static boolean enNerea() {
        return enNerea;
    }

    public static boolean cargado() {
        return cargado;
    }

    public static List<Vec3> puntos() {
        return puntos;
    }

    public static @Nullable Vec3 impacto() {
        return impacto;
    }

    /** Calcula el camino de la bala desde este canon, apuntando a donde mira p. */
    static void calcular(CanonNaufragioEntity c, Player p, float parcial) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) {
            return;
        }
        float rumbo = p.getViewYRot(parcial) * Mth.DEG_TO_RAD;
        float alza = Mth.clamp(-p.getViewXRot(parcial), CanonNaufragioEntity.ALZA_MIN, CanonNaufragioEntity.ALZA_MAX) * Mth.DEG_TO_RAD;
        Vec3 dir = new Vec3(-Mth.sin(rumbo) * Mth.cos(alza), Mth.sin(alza), Mth.cos(rumbo) * Mth.cos(alza));
        Vec3 pos = c.getPosition(parcial).add(0, CanonNaufragioEntity.BOCA_ALTO, 0).add(dir.scale(CanonNaufragioEntity.BOCA_LARGO));
        Vec3 v = dir.scale(BalaCanonEntity.VELOCIDAD);
        List<NereaEntity> nereas = mc.level.getEntitiesOfClass(NereaEntity.class, new AABB(pos, pos).inflate(96), NereaEntity::isAlive);
        List<Vec3> out = new ArrayList<>();
        out.add(pos);
        Vec3 choque = null;
        boolean nerea = false;
        for (int i = 0; i < VUELO && choque == null; i++) {
            v = v.add(0, -BalaCanonEntity.GRAVEDAD, 0).scale(0.99);
            Vec3 sig = pos.add(v);
            double mejor = Double.MAX_VALUE;
            for (NereaEntity n : nereas) {
                Optional<Vec3> d = n.getBoundingBox().clip(pos, sig);
                if (d.isPresent() && d.get().distanceToSqr(pos) < mejor) {
                    mejor = d.get().distanceToSqr(pos);
                    choque = d.get();
                    nerea = true;
                }
            }
            BlockHitResult b = mc.level.clip(new ClipContext(pos, sig, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
            if (b.getType() != HitResult.Type.MISS && b.getLocation().distanceToSqr(pos) < mejor) {
                choque = b.getLocation();
                nerea = false;
            }
            pos = choque != null ? choque : sig;
            out.add(pos);
        }
        puntos = out;
        impacto = choque;
        enNerea = nerea;
        cargado = c.cargado();
        activo = true;
        calculado = mc.level.getGameTime();
    }
}
