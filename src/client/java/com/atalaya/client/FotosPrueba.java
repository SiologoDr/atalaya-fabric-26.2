package com.atalaya.client;

import com.atalaya.Atalaya;
import net.fabricmc.loader.api.FabricLoader;
import net.fabricmc.fabric.api.client.message.v1.ClientReceiveMessageEvents;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;

import java.io.File;

/**
 * Herramienta de desarrollo: capturas de pantalla a la orden de un datapack.
 *
 * Solo se activa si en la carpeta del juego existe "atalaya_fotos.flag" (en el
 * entorno de pruebas, run/). Entonces un mensaje de sistema "FOTO nombre" (un
 * tellraw desde una funcion) guarda el fotograma como screenshots/nombre.png y
 * no se muestra en el chat. Asi las escenas de prueba se fotografian en el
 * tick exacto, aunque la ventana este tapada o sin foco.
 */
public final class FotosPrueba {

    private static final String PREFIJO = "FOTO ";
    /** "VISTA 0|1|2": primera persona, tercera por detras o por delante (para ver lo que lleva uno encima). */
    private static final String VISTA = "VISTA ";
    /** "DUELO_AUTO 1|0": el Duelo de Canto se toca solo (acierta casi todas y falla una de cada cinco), para las fotos. */
    private static final String DUELO_AUTO = "DUELO_AUTO ";
    /** "FPS etiqueta": apunta en el registro los fotogramas del ultimo segundo (para medir el rendimiento). */
    private static final String FPS = "FPS ";
    /** "USAR 1|0": mantiene (o suelta) el clic derecho con lo que lleve en la mano (el Prisma de Jade de Rajang). */
    private static final String USAR = "USAR ";
    /** "TECLA n": elige la casilla n (0 a 8) de la barra (Piedra, Papel o Tijera de Novilis). */
    private static final String TECLA = "TECLA ";
    /** "AGACHAR 1|0" y "SALTAR 1|0": mantiene (o suelta) Shift o el salto (el Caballero Manda). */
    private static final String AGACHAR = "AGACHAR ";
    private static final String SALTAR = "SALTAR ";
    /** "FOV n": el campo de vision (30 a 110; para acercar la vista en las fotos). */
    private static final String FOV = "FOV ";
    /** "HUECO n": mira al centro del hueco n del cielo roto del Momento Fractura (0 a 4). */
    private static final String HUECO = "HUECO ";
    /** "COCO_HUD 1|0": muestra (o quita) la pantalla roja de dentro del Coco, para fotografiar el aviso de encima. */
    private static final String COCO_HUD = "COCO_HUD ";
    /** "CLIC x y": un clic izquierdo en la pantalla abierta, en coordenadas de la interfaz (los menus propios); "CERRAR", la cierra. */
    private static final String CLIC = "CLIC ";
    /** "GOLPEAR": un clic izquierdo a lo que tenga delante (un bloque o una entidad). */
    private static final String GOLPEAR = "GOLPEAR";
    /** "INTERACTUAR": un clic derecho a la entidad que tenga delante (las veletas de Aeralis). */
    private static final String INTERACTUAR = "INTERACTUAR";
    /** "MIRAR <tipo>": gira la camara (como el raton) hacia el pecho de la entidad mas cercana de ese tipo. */
    private static final String MIRAR = "MIRAR ";
    /** "FORJA_AUTO 1|0": golpea solo el yunque de la Forja que mira cuando el aro toca la hoja. */
    private static final String FORJA_AUTO = "FORJA_AUTO ";
    private static boolean forjaAuto;
    /** "MANDA_AUTO 1|0": obedece solo al Caballero Manda (solo las de verdad). */
    private static final String MANDA_AUTO = "MANDA_AUTO ";
    private static boolean mandaAuto;
    /**
     * "RULETA_FILM nombre t0 t1 paso": fotografia la Ruleta en marcha con su reloj parado en t0, t0+paso... hasta t1,
     * una foto por tiempo y solo cuando ya esta pintado (asi las fotos no dependen de lo deprisa que vaya el juego).
     * Mientras, el chat no se ve hasta el tick del aviso (124).
     */
    private static final String RULETA_FILM = "RULETA_FILM ";
    private static boolean filmando;
    private static String filmNombre = "";
    private static float filmT;
    private static float filmFin;
    private static float filmPaso;
    /** El aviso de la Ruleta que llega mientras se filma: se guarda y sale cuando la pelicula llega a su tick. */
    private static net.minecraft.network.chat.@org.jspecify.annotations.Nullable Component avisoGuardado;
    private static int mandaVista = -1;
    private static int mandaSuelta;

    private FotosPrueba() {
    }

    public static void registrar() {
        if (!new File(FabricLoader.getInstance().getGameDir().toFile(), "atalaya_fotos.flag").exists()) {
            return;
        }
        Atalaya.LOGGER.info("Fotos de prueba activadas (atalaya_fotos.flag).");
        net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents.END_CLIENT_TICK.register(FotosPrueba::forjar);
        net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents.END_CLIENT_TICK.register(FotosPrueba::filmar);
        ClientReceiveMessageEvents.ALLOW_GAME.register((mensaje, encima) -> {
            String texto = mensaje.getString();
            Minecraft cliente = Minecraft.getInstance();
            if (filmando && filmT < RuletaCliente.T_AVISO && texto.contains("ruleta_")) {
                avisoGuardado = mensaje;
                return false;
            }
            if (texto.startsWith(RULETA_FILM)) {
                String[] p = texto.substring(RULETA_FILM.length()).trim().split(" ");
                filmNombre = p[0];
                filmT = Float.parseFloat(p[1]);
                filmFin = Float.parseFloat(p[2]);
                filmPaso = Float.parseFloat(p[3]);
                filmando = true;
                RuletaCliente.pruebaT = filmT;
                RuletaHud.pintadoCon = -1;
                return false;
            }
            if (texto.startsWith(TECLA) && cliente.player != null) {
                cliente.player.getInventory().setSelectedSlot(Math.clamp(Integer.parseInt(texto.substring(TECLA.length()).trim()), 0, 8));
                return false;
            }
            if (texto.startsWith(AGACHAR)) {
                cliente.options.keyShift.setDown(texto.substring(AGACHAR.length()).trim().equals("1"));
                return false;
            }
            if (texto.startsWith(SALTAR)) {
                cliente.options.keyJump.setDown(texto.substring(SALTAR.length()).trim().equals("1"));
                return false;
            }
            if (texto.startsWith(MANDA_AUTO)) {
                mandaAuto = texto.substring(MANDA_AUTO.length()).trim().equals("1");
                return false;
            }
            if (texto.startsWith(FORJA_AUTO)) {
                forjaAuto = texto.substring(FORJA_AUTO.length()).trim().equals("1");
                return false;
            }
            if (texto.startsWith("BUSCA ")) {
                if (cliente.gui.screen() instanceof MenuCambiosScreen menu) {
                    menu.buscar(texto.substring(6));
                }
                return false;
            }
            if (texto.equals("CERRAR")) {
                cliente.gui.setScreen(null);
                return false;
            }
            if (texto.startsWith(CLIC)) {
                String[] xy = texto.substring(CLIC.length()).trim().split(" ");
                net.minecraft.client.gui.screens.Screen pantalla = cliente.gui.screen();
                if (pantalla != null) {
                    pantalla.mouseClicked(new net.minecraft.client.input.MouseButtonEvent(Double.parseDouble(xy[0]),
                            Double.parseDouble(xy[1]), new net.minecraft.client.input.MouseButtonInfo(0, 0)), false);
                }
                return false;
            }
            if (texto.equals(GOLPEAR)) {
                golpear(cliente);
                return false;
            }
            if (texto.startsWith(MIRAR)) {
                apuntar(cliente, texto.substring(MIRAR.length()).trim());
                return false;
            }
            if (texto.equals(INTERACTUAR)) {
                if (cliente.player != null && cliente.gameMode != null
                        && cliente.hitResult instanceof net.minecraft.world.phys.EntityHitResult e) {
                    cliente.gameMode.interact(cliente.player, e.getEntity(), e, net.minecraft.world.InteractionHand.MAIN_HAND);
                    cliente.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
                }
                return false;
            }
            if (texto.startsWith(FOV)) {
                cliente.options.fov().set(Math.clamp(Integer.parseInt(texto.substring(FOV.length()).trim()), 30, 110));
                return false;
            }
            if (texto.startsWith(COCO_HUD)) {
                CocoDentroHud.pruebaSinPantalla = texto.substring(COCO_HUD.length()).trim().equals("0");
                return false;
            }
            if (texto.startsWith(HUECO)) {
                float[] c = CieloRoto.centroHueco(Integer.parseInt(texto.substring(HUECO.length()).trim()));
                if (c != null && cliente.player != null) {
                    net.minecraft.world.phys.Vec3 ojo = cliente.player.getEyePosition();
                    cliente.player.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES,
                            ojo.add(c[0] * 100, c[1] * 100, c[2] * 100));
                }
                return false;
            }
            if (texto.startsWith(VISTA)) {
                int v = Math.clamp(Integer.parseInt(texto.substring(VISTA.length()).trim()), 0, 2);
                Minecraft.getInstance().options.setCameraType(net.minecraft.client.CameraType.values()[v]);
                return false;
            }
            if (texto.startsWith(USAR)) {
                Minecraft mc = Minecraft.getInstance();
                boolean si = texto.substring(USAR.length()).trim().equals("1");
                mc.options.keyUse.setDown(si);
                if (si && mc.player != null && mc.gameMode != null && !mc.player.isUsingItem()) {
                    mc.gameMode.useItem(mc.player, net.minecraft.world.InteractionHand.MAIN_HAND);
                }
                return false;
            }
            if (texto.startsWith(FPS)) {
                // Para medir el rendimiento: los fotogramas del ultimo segundo, al registro.
                Atalaya.LOGGER.info("FPS {} {}", texto.substring(FPS.length()).trim(), Minecraft.getInstance().getFps());
                return false;
            }
            if (texto.startsWith(DUELO_AUTO)) {
                DueloCantoCliente.auto = texto.substring(DUELO_AUTO.length()).trim().equals("1");
                return false;
            }
            if (!texto.startsWith(PREFIJO)) {
                return true;
            }
            Minecraft mc = Minecraft.getInstance();
            String nombre = texto.substring(PREFIJO.length()).trim().replaceAll("[^A-Za-z0-9_\\-]", "_");
            Screenshot.grab(mc.gameDirectory, nombre + ".png", mc.gameRenderer.mainRenderTarget(), 1, c -> {
            });
            return false;
        });
    }

    /** Si el chat no se ve (mientras se filma la Ruleta, antes de su aviso). */
    public static boolean ocultaChat() {
        return filmando && filmT < RuletaCliente.T_AVISO;
    }

    /** La pelicula de la Ruleta: foto del fotograma pintado con el tiempo de ahora y al siguiente. */
    private static void filmar(Minecraft mc) {
        if (!filmando || RuletaHud.pintadoCon != RuletaCliente.pruebaT) {
            return;
        }
        String nombre = filmNombre + "_" + String.format(java.util.Locale.ROOT, "%07.2f", filmT).replace('.', '_');
        Screenshot.grab(mc.gameDirectory, nombre + ".png", mc.gameRenderer.mainRenderTarget(), 1, c -> {
        });
        filmT += filmPaso;
        if (avisoGuardado != null && filmT >= RuletaCliente.T_AVISO) {
            mc.gui.chatListener().handleSystemMessage(avisoGuardado, false);
            avisoGuardado = null;
        }
        if (filmT > filmFin + 1.0E-3F) {
            filmando = false;
            RuletaCliente.pruebaT = -1;
            Atalaya.LOGGER.info("RULETA_FILM {} hecha", filmNombre);
            return;
        }
        RuletaCliente.pruebaT = filmT;
        RuletaHud.pintadoCon = -1;
    }

    private static void apuntar(Minecraft mc, String tipo) {
        if (mc.player == null || mc.level == null) {
            return;
        }
        net.minecraft.world.entity.Entity mejor = null;
        double d = Double.MAX_VALUE;
        for (net.minecraft.world.entity.Entity e : mc.level.entitiesForRendering()) {
            if (e != mc.player && net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).toString().equals(tipo)) {
                double dd = e.distanceToSqr(mc.player);
                if (dd < d) {
                    d = dd;
                    mejor = e;
                }
            }
        }
        if (mejor != null) {
            mc.player.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES,
                    new net.minecraft.world.phys.Vec3(mejor.getX(), mejor.getY() + mejor.getBbHeight() * 0.6, mejor.getZ()));
        }
    }

    private static void golpear(Minecraft mc) {
        if (mc.player == null || mc.gameMode == null || mc.hitResult == null) {
            return;
        }
        if (mc.hitResult instanceof net.minecraft.world.phys.EntityHitResult e) {
            mc.gameMode.attack(mc.player, e.getEntity());
        } else if (mc.hitResult instanceof net.minecraft.world.phys.BlockHitResult b
                && mc.hitResult.getType() == net.minecraft.world.phys.HitResult.Type.BLOCK) {
            mc.gameMode.startDestroyBlock(b.getBlockPos(), b.getDirection());
            mc.gameMode.stopDestroyBlock();
        }
        mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
    }

    /** El Caballero Manda solo: hace las ordenes de verdad (tras un pequeno retraso) y no las trampas. */
    private static void obedecer(Minecraft mc) {
        if (mandaSuelta > 0 && --mandaSuelta == 0) {
            mc.options.keyShift.setDown(false);
            mc.options.keyJump.setDown(false);
        }
        com.atalaya.entity.NovilisEntity n = null;
        for (net.minecraft.world.entity.Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof com.atalaya.entity.NovilisEntity c && c.minijuego() == com.atalaya.entity.MinijuegosNovilis.MANDA) {
                n = c;
            }
        }
        if (n == null) {
            return;
        }
        int info = n.getMiniInfo();
        int numero = com.atalaya.entity.MinijuegosNovilis.numeroManda(info);
        if (numero == mandaVista || numero == 0) {
            return;
        }
        mandaVista = numero;
        mc.player.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES,
                n.puntoMundo(com.atalaya.entity.NovilisGeometria.PECHO));
        if (!com.atalaya.entity.MinijuegosNovilis.deVerdadManda(info)) {
            return;
        }
        switch (com.atalaya.entity.MinijuegosNovilis.ordenManda(info)) {
            case com.atalaya.entity.MinijuegosNovilis.ARRODILLAOS -> {
                mc.options.keyShift.setDown(true);
                mandaSuelta = 30;
            }
            case com.atalaya.entity.MinijuegosNovilis.SALTAD -> {
                mc.options.keyJump.setDown(true);
                mandaSuelta = 8;
            }
            case com.atalaya.entity.MinijuegosNovilis.MIRAD_SOL -> {
                net.minecraft.world.phys.Vec3 sol = n.puntoMundo(com.atalaya.entity.NovilisGeometria.SOL_PROPIO);
                mc.player.lookAt(net.minecraft.commands.arguments.EntityAnchorArgument.Anchor.EYES, sol);
            }
            default -> {
            }
        }
    }

    /** La Forja sola: golpea el yunque que mira justo cuando el aro toca la hoja. */
    private static void forjar(Minecraft mc) {
        if (mandaAuto && mc.level != null && mc.player != null) {
            obedecer(mc);
        }
        if (!forjaAuto || mc.level == null || mc.player == null || mc.gameMode == null) {
            return;
        }
        if (mc.crosshairPickEntity instanceof com.atalaya.entity.YunqueForjaEntity y && !y.forjada()) {
            float r = y.radioAro(mc.level.getGameTime(), 0.0F);
            // El ultimo tick antes de que el aro toque la hoja (el golpe llega al siguiente).
            float paso = (com.atalaya.entity.YunqueForjaEntity.ARO_SALE - com.atalaya.entity.YunqueForjaEntity.ARO_HOJA)
                    / y.periodo();
            if (r > 0.0F && r <= com.atalaya.entity.YunqueForjaEntity.ARO_HOJA + paso + 0.01F) {
                mc.gameMode.attack(mc.player, y);
                mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
            }
        }
    }
}
