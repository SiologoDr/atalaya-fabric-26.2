package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.AtlahuaEntity;
import com.atalaya.entity.AtlahuaGeometria;
import com.atalaya.entity.MiniJefeEntity;
import com.atalaya.entity.MoctezumaEntity;
import com.atalaya.entity.MoctezumaGeometria;
import com.atalaya.entity.RajangEntity;
import com.atalaya.entity.XiuhquetzalEntity;
import com.atalaya.entity.XiuhquetzalGeometria;
import com.atalaya.entity.YiatzoEntity;
import com.atalaya.entity.YiatzoGeometria;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.renderer.RenderPipelines;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * La barra de vida de los mini jefes (minijefes_extras.py): una sola, sin fases,
 * como la de los jefes pero mas baja (Juan: "quiero que sea como los boses pero
 * en cambio la altura va ser mas pequeno"): 220x32 frente a 240x44.
 *
 * Como la de los jefes: el medallon con su emblema a la izquierda (el yelmo de
 * aguila, el orbe, el tridente, la cabeza del fenix), la barra larga de bloques
 * de su material con su punta (dientes de obsidiana, la punta de plata con el
 * orbe, el tridente, una llama), la cresta de su elemento que sale del medallon
 * (plumas de quetzal, losas de glifos con el viento, coral, plumas de fuego), su
 * nombre encima en letras de pixel, la energia de su elemento que corre por
 * dentro con el frente encendido, el rastro claro del dano y tres muescas de su
 * material que se parten al pasarlas.
 *
 * Van debajo de las barras de los jefes que esten a la vista, una por mini jefe
 * despierto (hasta tres, los mas cercanos, a menos de 80 bloques).
 */
public class MiniJefeBarraHud implements HudElement {

    public static final int ANCHO = 220;
    public static final int ALTO = 32;
    private static final int HUECO_X = 34;
    private static final int HUECO_Y = 19;
    private static final int HUECO_ANCHO = 178;
    private static final int HUECO_ALTO = 6;
    private static final int NOMBRE_X = 90;
    private static final int NOMBRE_Y = 4;
    private static final int MUESCA_ANCHO = 5;
    private static final int MUESCA_ALTO = 11;
    private static final int NOMBRE_ANCHO = 96;
    private static final int NOMBRE_ALTO = 11;
    private static final int RELLENO = 64;
    private static final double LEJOS = 80.0;

    private record Tema(String id, int claro, int rastro, int despertar) {
    }

    private static final Tema MOCTEZUMA = new Tema("moctezuma", 0xE8FFF0, 0xD8F0FFE0, MoctezumaGeometria.DURACION_DESPERTAR);
    private static final Tema YIATZO = new Tema("yiatzo", 0xF4FDFF, 0xD8E8FAFF, YiatzoGeometria.DURACION_DESPERTAR);
    private static final Tema ATLAHUA = new Tema("atlahua", 0xE8FFFF, 0xD8E0FFFF, AtlahuaGeometria.DURACION_DESPERTAR);
    private static final Tema XIUHQUETZAL = new Tema("xiuhquetzal", 0xFFF4D8, 0xD8FFF0D8, XiuhquetzalGeometria.DURACION_DESPERTAR);

    /** El rastro de cada mini jefe a la vista (su vida de hace un momento). */
    private final Map<Integer, Float> fantasmas = new HashMap<>();

    private static Identifier tex(String nombre) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "textures/gui/minijefes/" + nombre + ".png");
    }

    private static Tema tema(MiniJefeEntity e) {
        if (e instanceof MoctezumaEntity) {
            return MOCTEZUMA;
        }
        if (e instanceof YiatzoEntity) {
            return YIATZO;
        }
        if (e instanceof AtlahuaEntity) {
            return ATLAHUA;
        }
        return XIUHQUETZAL;
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, DeltaTracker delta) {
        Minecraft mc = Minecraft.getInstance();
        List<MiniJefeEntity> cerca = cercanos(mc);
        if (cerca.isEmpty()) {
            fantasmas.clear();
            return;
        }
        float parcial = delta.getGameTimeDeltaPartialTick(false);
        int x0 = (g.guiWidth() - ANCHO) / 2;
        int y0 = 5 + arriba(mc);
        Map<Integer, Float> vivos = new HashMap<>();
        for (MiniJefeEntity e : cerca) {
            barra(g, e, x0, y0, parcial, vivos);
            y0 += ALTO + 4;
        }
        fantasmas.clear();
        fantasmas.putAll(vivos);
    }

    private void barra(GuiGraphicsExtractor g, MiniJefeEntity e, int x0, int y0, float parcial, Map<Integer, Float> vivos) {
        Tema t = tema(e);
        boolean muerto = e.isDeadOrDying();
        float vida = muerto ? 0.0F : Mth.clamp(e.getHealth() / e.getMaxHealth(), 0.0F, 1.0F);
        if (e.getEstado() == MiniJefeEntity.DESPERTAR) {
            // Al despertar la barra se llena, como la de los jefes.
            vida *= Mth.clamp(e.tiempoEstado(parcial) / t.despertar(), 0.0F, 1.0F);
        }
        float fantasma = fantasmas.getOrDefault(e.getId(), vida);
        fantasma = vida > fantasma ? vida : fantasma + (vida - fantasma) * 0.04F;
        vivos.put(e.getId(), fantasma);

        int sacude = !muerto && e.hurtTime > 0 ? (e.hurtTime % 2 == 0 ? 1 : -1) : 0;
        g.blit(RenderPipelines.GUI_TEXTURED, tex(t.id() + "_marco"), x0 + sacude, y0, 0.0F, 0.0F, ANCHO, ALTO, ANCHO, ALTO, ANCHO, ALTO,
                0xFFFFFFFF);
        int hx = x0 + HUECO_X + sacude;
        int hy = y0 + HUECO_Y;
        int lleno = Math.round(HUECO_ANCHO * vida);
        int rastro = Math.round(HUECO_ANCHO * fantasma);
        if (rastro > lleno) {
            g.fill(hx + lleno, hy, hx + rastro, hy + HUECO_ALTO, t.rastro());
        }
        // La energia de su elemento corre despacio hacia la derecha.
        int desplaza = RELLENO - (int) ((e.tickCount + parcial) * 0.7F) % RELLENO;
        Identifier relleno = tex(t.id() + "_relleno");
        for (int x = 0; x < lleno; ) {
            int u = (x + desplaza) % RELLENO;
            int w = Math.min(RELLENO - u, lleno - x);
            g.blit(RenderPipelines.GUI_TEXTURED, relleno, hx + x, hy, u, 0.0F, w, HUECO_ALTO, w, HUECO_ALTO, RELLENO, HUECO_ALTO,
                    0xFFFFFFFF);
            x += w;
        }
        if (lleno >= 2) {
            g.fill(hx + lleno - 2, hy, hx + lleno, hy + HUECO_ALTO, 0xFF000000 | t.claro());
        }
        // Tres muescas de su material: se parten al pasarlas la vida.
        for (float corte : new float[]{0.25F, 0.5F, 0.75F}) {
            int ex = hx + Math.round(HUECO_ANCHO * corte) - MUESCA_ANCHO / 2;
            g.blit(RenderPipelines.GUI_TEXTURED, tex(t.id() + (vida < corte ? "_muesca_rota" : "_muesca")), ex, hy - 3, 0.0F, 0.0F,
                    MUESCA_ANCHO, MUESCA_ALTO, MUESCA_ANCHO, MUESCA_ALTO, MUESCA_ANCHO, MUESCA_ALTO, 0xFFFFFFFF);
        }
        g.blit(RenderPipelines.GUI_TEXTURED, tex(t.id() + "_nombre"), x0 + NOMBRE_X + sacude, y0 + NOMBRE_Y, 0.0F, 0.0F,
                NOMBRE_ANCHO, NOMBRE_ALTO, NOMBRE_ANCHO, NOMBRE_ALTO, NOMBRE_ANCHO, NOMBRE_ALTO, 0xFFFFFFFF);
    }

    /** Lo que ocupan las barras de los jefes que esten a la vista (las de los mini jefes van debajo). */
    private static int arriba(Minecraft mc) {
        int y = 0;
        if (NereaBarraHud.visible) {
            y += NereaBarraHud.ALTO + 6;
        }
        if (AeralisBarraHud.visible) {
            y += AeralisBarraHud.ALTO + 6;
        }
        if (rajangALaVista(mc)) {
            y += RajangBarraHud.ALTO + 6;
        }
        if (NovilisBarraHud.visible) {
            y += NovilisBarraHud.ALTO + 6;
        }
        return y;
    }

    private static boolean rajangALaVista(Minecraft mc) {
        if (mc.level == null || mc.player == null) {
            return false;
        }
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof RajangEntity r && r.getEstado() != RajangEntity.DORMIDO && !r.isRemoved()
                    && r.distanceToSqr(mc.player) < 120 * 120) {
                return true;
            }
        }
        return false;
    }

    /** Los mini jefes despiertos a menos de LEJOS bloques, del mas cercano al mas lejano (hasta tres). */
    private static List<MiniJefeEntity> cercanos(Minecraft mc) {
        List<MiniJefeEntity> out = new ArrayList<>();
        if (mc.level == null || mc.player == null) {
            return out;
        }
        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof MiniJefeEntity m && m.getEstado() != MiniJefeEntity.DORMIDO && !m.isRemoved()
                    && m.distanceToSqr(mc.player) < LEJOS * LEJOS) {
                out.add(m);
            }
        }
        out.sort((a, b) -> Double.compare(a.distanceToSqr(mc.player), b.distanceToSqr(mc.player)));
        return out.size() > 3 ? out.subList(0, 3) : out;
    }
}
