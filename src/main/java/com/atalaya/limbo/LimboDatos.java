package com.atalaya.limbo;

import com.atalaya.Atalaya;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.GlobalPos;
import net.minecraft.resources.Identifier;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.datafix.DataFixTypes;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.SavedDataType;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Lo que el Limbo recuerda entre sesiones: si el laberinto ya esta hecho (y con que version y semilla), en que celda
 * esta ahora la salida, cuando se movio por ultima vez y a donde vuelve cada desterrado (donde estaba al entrar).
 */
public class LimboDatos extends SavedData {

    private static final Codec<LimboDatos> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.INT.optionalFieldOf("version", 0).forGetter(d -> d.version),
            Codec.LONG.optionalFieldOf("semilla", 0L).forGetter(d -> d.semilla),
            Codec.INT.optionalFieldOf("salida_i", -1).forGetter(d -> d.salidaI),
            Codec.INT.optionalFieldOf("salida_j", -1).forGetter(d -> d.salidaJ),
            Codec.LONG.optionalFieldOf("movida", 0L).forGetter(d -> d.movida),
            Codec.unboundedMap(Codec.STRING, GlobalPos.CODEC).optionalFieldOf("vueltas", Map.of())
                    .forGetter(d -> d.vueltasTexto())
    ).apply(i, LimboDatos::new));

    static final SavedDataType<LimboDatos> TIPO = new SavedDataType<>(
            Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "limbo"), LimboDatos::new, CODEC,
            DataFixTypes.SAVED_DATA_COMMAND_STORAGE);

    /** La version del laberinto construido (0, ninguno): si cambia Laberinto.VERSION, se rehace. */
    int version;
    long semilla;
    int salidaI = -1;
    int salidaJ = -1;
    /** El tick del servidor en que se movio la salida por ultima vez. */
    long movida;
    final Map<UUID, GlobalPos> vueltas = new HashMap<>();

    public LimboDatos() {
    }

    private LimboDatos(int version, long semilla, int salidaI, int salidaJ, long movida, Map<String, GlobalPos> vueltas) {
        this.version = version;
        this.semilla = semilla;
        this.salidaI = salidaI;
        this.salidaJ = salidaJ;
        this.movida = movida;
        vueltas.forEach((k, v) -> {
            try {
                this.vueltas.put(UUID.fromString(k), v);
            } catch (IllegalArgumentException ignorado) {
                // Una clave rota: se pierde esa vuelta y ya esta.
            }
        });
    }

    private Map<String, GlobalPos> vueltasTexto() {
        Map<String, GlobalPos> m = new HashMap<>();
        vueltas.forEach((k, v) -> m.put(k.toString(), v));
        return m;
    }

    static LimboDatos de(MinecraftServer servidor) {
        return servidor.getDataStorage().computeIfAbsent(TIPO);
    }
}
