package com.atalaya.mixin.client;

import net.minecraft.client.model.geom.ModelPart;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

import java.util.List;
import java.util.Map;

/** Para sacar de un modelo solo los cubos que brillan (SoloLoQueBrilla). */
@Mixin(ModelPart.class)
public interface ModelPartAccesor {

    @Accessor("cubes")
    List<ModelPart.Cube> atalaya$cubos();

    @Accessor("children")
    Map<String, ModelPart> atalaya$hijos();
}
