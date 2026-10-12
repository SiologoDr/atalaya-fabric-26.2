package com.atalaya.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.state.level.CameraRenderState;

/**
 * Lo propio de cada mini jefe en el cliente: lo que ondea solo encima de las
 * animaciones (capas, plumas, llamas) y lo grande de sus ataques, que se pinta
 * desde su estado y el tiempo que lleva en el (la ola, el ciclon, los tajos...).
 */
public interface MiniJefeEfectos {

    /** Lo que se mueve solo, encima de las animaciones (con el modelo ya puesto). */
    default void secundario(MiniJefeModel m, MiniJefeRenderState s) {
    }

    /** Lo grande de sus ataques (en el espacio de la entidad: el origen en sus pies). */
    default void submit(MiniJefeRenderState s, PoseStack pose, SubmitNodeCollector c, CameraRenderState camara) {
    }

    /**
     * Cuanto sobresale de su caja (bloques, antes de su escala) lo que pinta andando
     * o dormido: alas, armas, plumas, el aura. Para no dejar de pintarlo si aun asoma.
     */
    default float alcance() {
        return 3.0F;
    }

    /** Si la piel se pinta a plena luz (el fenix es fuego: no se apaga de noche). */
    default boolean plenaLuz() {
        return false;
    }
}
