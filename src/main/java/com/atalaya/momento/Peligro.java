package com.atalaya.momento;

import com.atalaya.Atalaya;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.monster.Creeper;

import java.util.ArrayList;
import java.util.List;

/** Lo que comparten los momentos del catalogo: los danos, los avisos de la barra y los creepers de un corazon. */
final class Peligro {

    /** El dano de un momento (el gas, el rayo, el meteorito...): atraviesa la armadura, un totem si salva. */
    static final ResourceKey<DamageType> DANO = ResourceKey.create(Registries.DAMAGE_TYPE,
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "momento_peligro"));

    private Peligro() {
    }

    /** Los que cuentan (vivos, ni en creativo ni espectadores). */
    static List<ServerPlayer> jugadores(MinecraftServer s) {
        List<ServerPlayer> out = new ArrayList<>();
        for (ServerPlayer p : s.getPlayerList().getPlayers()) {
            if (Suceso.cuenta(p)) {
                out.add(p);
            }
        }
        return out;
    }

    static void danar(ServerPlayer p, float cantidad) {
        ServerLevel nivel = p.level();
        DamageSource fuente = new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE).getOrThrow(DANO));
        p.hurtServer(nivel, fuente, cantidad);
    }

    /** La fractura: mata aunque haya totems (la de la prueba de la tierra). */
    static void fractura(ServerPlayer p) {
        ServerLevel nivel = p.level();
        DamageSource fuente = new DamageSource(nivel.registryAccess().lookupOrThrow(Registries.DAMAGE_TYPE)
                .getOrThrow(MomentoMaldicion.DANO));
        p.hurtServer(nivel, fuente, 1.0E6F);
    }

    /** Un aviso en la barra de encima de los objetos (rojo si es un peligro, verde si ya esta a salvo). */
    static void barra(ServerPlayer p, String texto, boolean bien) {
        p.sendOverlayMessage(Component.literal(texto).withStyle(st -> st.withColor(bien ? 0x8AE07A : 0xFF6A5A)));
    }

    /** Un aviso en el chat para todos (un paso de un momento encadenado, una oleada...). */
    static void chat(MinecraftServer s, String texto) {
        s.getPlayerList().broadcastSystemMessage(Component.literal(texto).withStyle(st -> st.withColor(0xF04A40)), false);
    }

    /** Un creeper cargado de un corazon junto a ese jugador. */
    static void creeper(ServerPlayer p) {
        ServerLevel nivel = p.level();
        RandomSource r = nivel.getRandom();
        for (int intento = 0; intento < 8; intento++) {
            double a = r.nextDouble() * Mth.TWO_PI;
            BlockPos pos = BlockPos.containing(p.getX() + Math.cos(a) * 2.0, p.getY(), p.getZ() + Math.sin(a) * 2.0);
            if (nivel.getBlockState(pos).getCollisionShape(nivel, pos).isEmpty()
                    && nivel.getBlockState(pos.above()).getCollisionShape(nivel, pos.above()).isEmpty()) {
                Creeper c = EntityTypes.CREEPER.spawn(nivel, pos, EntitySpawnReason.EVENT);
                if (c != null) {
                    com.atalaya.cambios.EquipoMobs.cargar(c, true);
                    c.setHealth(1.0F);
                    c.setTarget(p);
                }
                return;
            }
        }
    }
}
