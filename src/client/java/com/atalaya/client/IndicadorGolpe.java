package com.atalaya.client;

import com.atalaya.Atalaya;
import java.util.ArrayDeque;
import java.util.Deque;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * De donde vino el golpe (testers, 07-10-2026: "no podia distinguir de donde
 * venian los golpes; me puse a ver las hitbox"): al recibir dano de algo que
 * tiene posicion, un arco rojo alrededor de la mira, girado hacia alli, que se
 * apaga en 1,5 s. Si te giras, el arco sigue apuntando al sitio (no a donde
 * mirabas). Varios golpes a la vez, varios arcos. Lo apunta GolpeRecibidoMixin.
 */
public class IndicadorGolpe implements HudElement {

    private static final Identifier ARCO = Identifier.fromNamespaceAndPath(Atalaya.MOD_ID,
            "textures/gui/indicador_golpe.png");
    /** Lo que dura cada arco (ticks). */
    private static final float DURA = 30.0F;
    /** Lo lejos de la mira que va el arco (pixeles de interfaz): el de la textura, a la mitad. */
    private static final int RADIO = 60;

    private record Golpe(Vec3 desde, long cuando) {
    }

    private static final Deque<Golpe> GOLPES = new ArrayDeque<>();

    /** Un golpe recibido desde ese punto del mundo. */
    public static void registrar(Vec3 desde) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null || desde.distanceToSqr(mc.player.position()) < 0.25) {
            return;
        }
        GOLPES.addLast(new Golpe(desde, mc.level.getGameTime()));
        while (GOLPES.size() > 6) {
            GOLPES.removeFirst();
        }
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null || GOLPES.isEmpty()) {
            return;
        }
        float ahora = mc.level.getGameTime() + delta.getGameTimeDeltaPartialTick(false);
        GOLPES.removeIf(gp -> ahora - gp.cuando() > DURA);
        int cx = g.guiWidth() / 2;
        int cy = g.guiHeight() / 2;
        Vec3 yo = mc.player.getPosition(delta.getGameTimeDeltaPartialTick(false));
        float giro = mc.player.getViewYRot(delta.getGameTimeDeltaPartialTick(false));
        for (Golpe gp : GOLPES) {
            float edad = (ahora - gp.cuando()) / DURA;
            float alfa = (float) Math.pow(1.0F - Mth.clamp(edad, 0.0F, 1.0F), 1.2);
            double dx = gp.desde().x - yo.x;
            double dz = gp.desde().z - yo.z;
            float rumbo = (float) (Mth.atan2(-dx, dz) * Mth.RAD_TO_DEG);
            float rel = Mth.wrapDegrees(rumbo - giro);
            g.pose().pushMatrix();
            g.pose().translate(cx, cy);
            g.pose().rotate(rel * Mth.DEG_TO_RAD);
            g.blit(RenderPipelines.GUI_TEXTURED, ARCO, -16, -RADIO, 0.0F, 0.0F, 32, 12, 64, 24, 64, 24,
                    (Math.round(alfa * 255) << 24) | 0xFFFFFF);
            g.pose().popMatrix();
        }
    }
}
