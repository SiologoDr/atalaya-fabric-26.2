package com.atalaya.mixin;

import net.minecraft.world.entity.monster.Creeper;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/**
 * Abre la mecha y el radio del creeper, que son campos privados.
 *
 * El fulminante hereda de Creeper para quedarse con toda su IA, pero esos dos
 * numeros viven en campos sin acceso, asi que no hay forma de tocarlos desde la
 * subclase. Un accesor es la via mas corta y no cambia nada de vanilla: solo
 * anade dos metodos.
 */
@Mixin(Creeper.class)
public interface CreeperAccessor {

    /** Ticks que tarda en reventar desde que se ceba. En vanilla, 30. */
    @Accessor("maxSwell")
    void atalaya$ponerMecha(int ticks);

    /** Radio de la explosion. En vanilla, 3. */
    @Accessor("explosionRadius")
    void atalaya$ponerRadio(int radio);
}
