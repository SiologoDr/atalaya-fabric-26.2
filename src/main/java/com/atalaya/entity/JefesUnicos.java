package com.atalaya.entity;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.UUIDUtil;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;
import org.jspecify.annotations.Nullable;

/**
 * Un jefe de cada tipo por mundo (Juan, 07-10-2026: "si pongo una Nerea no se
 * puede poner otra"). Se guarda con el mundo cual es el de cada tipo (su UUID,
 * su dimension y por donde anda).
 *
 * - El huevo (HuevoJefeItem) no lo suelta si ya hay otro: avisa de donde esta.
 * - Por si llega por otro lado (/summon, un dispensador), cada jefe se apunta en
 *   su primer tick de servidor y, si ya habia otro, se va (JefesUnicos.admitir).
 * - Se borra al morir o quitarlo. Mientras muere (la liberacion) ya no cuenta:
 *   se puede poner otro.
 * - Si el apuntado no esta cargado, se da por vivo... salvo que su trozo este
 *   cargado y no aparezca: entonces ya no existe (lo borraron de otra forma).
 */
public class JefesUnicos extends SavedData {

    /** El jefe de un tipo: quien es, en que dimension y por donde anda (se actualiza cada 10 s). */
    public record Registro(UUID uuid, ResourceKey<Level> mundo, BlockPos sitio) {
        static final Codec<Registro> CODEC = RecordCodecBuilder.create(i -> i.group(
                UUIDUtil.CODEC.fieldOf("uuid").forGetter(Registro::uuid),
                ResourceKey.codec(Registries.DIMENSION).fieldOf("mundo").forGetter(Registro::mundo),
                BlockPos.CODEC.fieldOf("sitio").forGetter(Registro::sitio)).apply(i, Registro::new));
    }

    private static final Codec<JefesUnicos> CODEC = Codec.unboundedMap(Codec.STRING, Registro.CODEC)
            .xmap(JefesUnicos::new, j -> j.vivos);

    /** El tipo de datafix no se usa (los datos se escriben siempre en la version actual), pero no puede ser null. */
    private static final SavedDataType<JefesUnicos> TIPO = new SavedDataType<>(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "jefes_unicos"), JefesUnicos::new, CODEC,
            DataFixTypes.SAVED_DATA_COMMAND_STORAGE);

    /** Por tipo de entidad ("atalaya:nerea"), el que hay. */
    private final Map<String, Registro> vivos;

    public JefesUnicos() {
        this(Map.of());
    }

    private JefesUnicos(Map<String, Registro> vivos) {
        this.vivos = new HashMap<>(vivos);
    }

    private static JefesUnicos de(MinecraftServer servidor) {
        return servidor.getDataStorage().computeIfAbsent(TIPO);
    }

    private static String clave(EntityType<?> tipo) {
        return EntityType.getKey(tipo).toString();
    }

    /** El jefe de ese tipo que ya hay en el mundo y sigue ahi (sin contar a "salvo"), o null. */
    public static @Nullable Registro ocupado(MinecraftServer servidor, EntityType<?> tipo, @Nullable UUID salvo) {
        Registro r = de(servidor).vivos.get(clave(tipo));
        if (r == null || r.uuid().equals(salvo)) {
            return null;
        }
        return sigue(servidor, r) ? r : null;
    }

    private static boolean sigue(MinecraftServer servidor, Registro r) {
        ServerLevel nivel = servidor.getLevel(r.mundo());
        if (nivel == null) {
            return false;
        }
        Entity e = nivel.getEntity(r.uuid());
        if (e != null) {
            return !e.isRemoved() && !(e instanceof LivingEntity v && v.isDeadOrDying());
        }
        // Sin cargar: si las entidades de su trozo estan cargadas y no esta, ya no existe.
        return !nivel.areEntitiesLoaded(ChunkPos.pack(r.sitio()));
    }

    /**
     * El jefe empieza a vivir (su primer tick): si no hay otro de su tipo se apunta
     * y devuelve null; si lo hay, devuelve el que hay (y este se tiene que ir).
     */
    public static @Nullable Registro admitir(ServerLevel nivel, Entity jefe) {
        Registro otro = ocupado(nivel.getServer(), jefe.getType(), jefe.getUUID());
        if (otro != null) {
            return otro;
        }
        apuntar(nivel, jefe);
        return null;
    }

    /** Apunta (o pone al dia) por donde anda el jefe de su tipo. */
    public static void apuntar(ServerLevel nivel, Entity jefe) {
        JefesUnicos d = de(nivel.getServer());
        String k = clave(jefe.getType());
        Registro antes = d.vivos.get(k);
        if (antes != null && !antes.uuid().equals(jefe.getUUID()) && sigue(nivel.getServer(), antes)) {
            return;
        }
        Registro ahora = new Registro(jefe.getUUID(), nivel.dimension(), jefe.blockPosition());
        if (!ahora.equals(antes)) {
            d.vivos.put(k, ahora);
            d.setDirty();
        }
    }

    /** Se ha ido del mundo (muerto o quitado): deja libre su tipo. */
    public static void soltar(ServerLevel nivel, Entity jefe) {
        JefesUnicos d = de(nivel.getServer());
        String k = clave(jefe.getType());
        Registro r = d.vivos.get(k);
        if (r != null && r.uuid().equals(jefe.getUUID())) {
            d.vivos.remove(k);
            d.setDirty();
        }
    }

    /** "Solo uno de cada jefe: Nerea ya esta en x, z". */
    public static Component aviso(EntityType<?> tipo, Registro r) {
        return Component.translatable("hud.atalaya.jefe.unico", tipo.getDescription(), r.sitio().getX(), r.sitio().getZ())
                .withStyle(ChatFormatting.RED);
    }

    /** El jefe repetido se va: avisa a los que esten cerca de donde ha intentado salir. */
    public static void avisarRepetido(ServerLevel nivel, Entity jefe, Registro otro) {
        // Todos los de cerca, tambien en espectador (getEntitiesOfClass los deja fuera).
        Component texto = aviso(jefe.getType(), otro);
        for (Player p : nivel.players()) {
            if (p.distanceToSqr(jefe) < 32 * 32) {
                p.sendOverlayMessage(texto);
            }
        }
    }
}
