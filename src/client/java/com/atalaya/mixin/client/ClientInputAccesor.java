package com.atalaya.mixin.client;

import net.minecraft.client.player.ClientInput;
import net.minecraft.world.phys.Vec2;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Para dejar quieto al jugador en la presentacion de un jefe (TecladoPresentacionMixin). */
@Mixin(ClientInput.class)
public interface ClientInputAccesor {

    @Accessor("moveVector")
    void atalaya$setMoveVector(Vec2 v);
}
