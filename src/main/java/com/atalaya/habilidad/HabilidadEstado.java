package com.atalaya.habilidad;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

/**
 * Lo que el jugador lleva de su habilidad activa: cuando vuelve a estar lista,
 * hasta cuando dura la que lanzo y de que conjunto era (el ordinal del tema).
 * Va en ticks de juego, asi que sobrevive a salir y entrar (no se recarga
 * reconectando) y el cliente lo usa tal cual para dibujar la recarga.
 */
public record HabilidadEstado(long lista, long hasta, int tema) {

    public static final HabilidadEstado NADA = new HabilidadEstado(0L, 0L, -1);

    public static final Codec<HabilidadEstado> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.LONG.fieldOf("lista").forGetter(HabilidadEstado::lista),
            Codec.LONG.fieldOf("hasta").forGetter(HabilidadEstado::hasta),
            Codec.INT.fieldOf("tema").forGetter(HabilidadEstado::tema)
    ).apply(i, HabilidadEstado::new));

    public static final StreamCodec<ByteBuf, HabilidadEstado> RED = StreamCodec.composite(
            ByteBufCodecs.VAR_LONG, HabilidadEstado::lista,
            ByteBufCodecs.VAR_LONG, HabilidadEstado::hasta,
            ByteBufCodecs.VAR_INT, HabilidadEstado::tema,
            HabilidadEstado::new);

    /** Esta en marcha la activa de ese tema. */
    public boolean activa(long ahora, int tema) {
        return this.tema == tema && ahora < hasta;
    }
}
