package com.atalaya.cambios;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentSyncPredicate;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;

/**
 * La plaga (la zombificacion del DEDsafio 3 y 4): una cuenta atras que lleva dentro el jugador. Al llegar a cero, la
 * plaga se cobra un totem (si lo tiene en la mano; y la cuenta vuelve a tres minutos) o la vida. La Pildora de la Plaga
 * le suma media hora (hasta cuatro horas).
 *
 * <pre>
 *   LA PLAGA           todos la llevan siempre (al entrar, al reaparecer: media hora)
 *   MORDISCO PUTRIDO   la contagia el mordisco de un zombi (diez minutos), y se cura con debilidad y una manzana de oro
 * </pre>
 *
 * La cuenta se guarda en el jugador y la ve el suyo (PlagaHud).
 */
public final class Plaga {

    /** Lo que dura al empezar, tras un totem, por mordisco y lo que suma una pildora (ticks). */
    public static final int INICIAL = 30 * 60 * 20;
    public static final int TRAS_TOTEM = 3 * 60 * 20;
    public static final int MORDISCO = 10 * 60 * 20;
    public static final int PILDORA = 30 * 60 * 20;
    public static final int MAXIMO = 4 * 60 * 60 * 20;
    public static final ResourceKey<DamageType> DANO = ResourceKey.create(Registries.DAMAGE_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "cambio_plaga"));

    /** Los ticks que le quedan (-1: sano). */
    public static AttachmentType<Integer> CUENTA;

    private Plaga() {
    }

    static void registrar() {
        CUENTA = AttachmentRegistry.<Integer>builder()
                .persistent(Codec.INT)
                .initializer(() -> -1)
                .syncWith(ByteBufCodecs.VAR_INT, AttachmentSyncPredicate.targetOnly())
                .buildAndRegister(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "plaga"));
        ServerTickEvents.END_SERVER_TICK.register(Plaga::tick);
    }

    public static int de(Player p) {
        return p.getAttachedOrCreate(CUENTA);
    }

    private static void poner(Player p, int ticks) {
        p.setAttached(CUENTA, ticks < 0 ? -1 : Math.min(MAXIMO, ticks));
    }

    static void alEncender(MinecraftServer s) {
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            if (de(p) < 0) {
                poner(p, INICIAL);
            }
        }
    }

    static void alApagar(MinecraftServer s) {
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            poner(p, -1);
        }
    }

    /** Quien entra o reaparece: con LA PLAGA, la lleva (media hora si no la tenia o si acaba de morir). */
    static void alEntrar(ServerPlayer p) {
        if (CambiosDificultad.activo(Cambio.LA_PLAGA)) {
            if (de(p) <= 0) {
                poner(p, INICIAL);
            }
        } else if (!CambiosDificultad.activo(Cambio.MORDISCO_PUTRIDO) || p.isDeadOrDying()) {
            poner(p, -1);
        }
    }

    /** MORDISCO PUTRIDO: el mordisco de un zombi contagia (si no la llevaba ya). */
    static void contagiar(ServerPlayer p) {
        if (de(p) < 0 && !p.isCreative()) {
            poner(p, MORDISCO);
            p.sendSystemMessage(Component.literal("Un zombi te ha contagiado la plaga. Cúrala con una poción de debilidad "
                    + "y una manzana de oro, o alárgala con píldoras.").withStyle(st -> st.withColor(0x7ED35A)));
        }
    }

    /** LA INFECCION (el momento): la plaga a todos con esa cuenta (o menos, si ya la llevaban con menos). */
    public static void infectar(Player p, int ticks) {
        int c = de(p);
        if (!p.isCreative() && (c < 0 || c > ticks)) {
            poner(p, ticks);
        }
        infectadosMomento = true;
    }

    /** Al acabar LA INFECCION: se va la plaga (salvo con LA PLAGA o MORDISCO PUTRIDO encendidos, que siguen solos). */
    public static void curarMomento(Player p) {
        if (!CambiosDificultad.activo(Cambio.LA_PLAGA) && !CambiosDificultad.activo(Cambio.MORDISCO_PUTRIDO)) {
            poner(p, -1);
        }
        infectadosMomento = false;
    }

    /** Si el momento de la infeccion tiene la plaga en marcha (aunque no haya cambio encendido). */
    private static boolean infectadosMomento;

    /** La Pildora: media hora mas. Devuelve si ha hecho algo. */
    public static boolean pildora(Player p) {
        int c = de(p);
        if (c < 0) {
            return false;
        }
        poner(p, c + PILDORA);
        return true;
    }

    /** Comer una manzana de oro con debilidad cura la plaga del mordisco (la de LA PLAGA no se cura). */
    public static void alComerManzana(Player p) {
        if (de(p) >= 0 && p.hasEffect(MobEffects.WEAKNESS) && !CambiosDificultad.activo(Cambio.LA_PLAGA)) {
            poner(p, -1);
            p.removeEffect(MobEffects.WEAKNESS);
            p.sendSystemMessage(Component.literal("La plaga se ha ido.").withStyle(st -> st.withColor(0x7ED35A)));
        }
    }

    private static void tick(MinecraftServer s) {
        if (s.getTickCount() % 20 != 0) {
            return;
        }
        boolean hay = CambiosDificultad.activo(Cambio.LA_PLAGA) || CambiosDificultad.activo(Cambio.MORDISCO_PUTRIDO)
                || infectadosMomento;
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            int c = de(p);
            if (c < 0) {
                continue;
            }
            if (!hay) {
                poner(p, -1);
                continue;
            }
            if (!p.isAlive() || p.isSpectator() || p.isCreative()) {
                continue;
            }
            c -= 20;
            if (c > 0) {
                poner(p, c);
                continue;
            }
            // A cero: se cobra un totem o la vida.
            ServerLevel nivel = p.level();
            DamageSource fuente = new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(DANO));
            poner(p, TRAS_TOTEM);
            p.hurtServer(nivel, fuente, 1.0E6F);
            if (p.isDeadOrDying()) {
                poner(p, -1);
            }
        }
    }
}
