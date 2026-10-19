package com.atalaya.cambios;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.EnderMan;
import net.minecraft.world.entity.monster.Endermite;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;

import static com.atalaya.cambios.Cambio.*;

/**
 * Lo que los cambios de dificultad hacen con el dano: todo pasa por aqui (CambiosDanoMixin, al entrar el golpe en
 * cualquier ser vivo), en este orden:
 *
 * <pre>
 *   al jugador      la caida x3 (PIES DE CRISTAL), el fuego y la lava x10 (BRASAS VORACES), ahogarse x10 (PULMONES DE
 *                   PAPEL), lo que no viene de un monstruo x3 (EL MUNDO CONTRAATACA), el cactus que mata (ESPINAS
 *                   MORTALES) y la perla (PERLAS AFILADAS: 10; SALTOS CAROS: media vida)
 *   de los mobs     los monstruos de siempre x3 (GOLPES TRIPLES), el enderman x4 (LA IRA DEL END) y el enderman y el
 *                   endermite a 100 (CIEN DE UN GOLPE)
 *   a los mobs      un 10 % menos (PIEL MAS GRUESA)
 * </pre>
 */
public final class DanoCambios {

    private DanoCambios() {
    }

    public static float modificar(LivingEntity victima, DamageSource fuente, float cantidad) {
        if (cantidad <= 0.0F || fuente.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) {
            return cantidad;
        }
        Entity atacante = fuente.getEntity();
        if (victima instanceof Player jugador) {
            if (CambiosDificultad.activo(PIES_DE_CRISTAL) && fuente.is(DamageTypes.FALL)) {
                cantidad *= 3.0F;
            }
            if (CambiosDificultad.activo(BRASAS_VORACES) && (fuente.is(DamageTypes.IN_FIRE) || fuente.is(DamageTypes.ON_FIRE)
                    || fuente.is(DamageTypes.LAVA) || fuente.is(DamageTypes.CAMPFIRE))) {
                cantidad *= 10.0F;
            }
            if (CambiosDificultad.activo(PULMONES_DE_PAPEL) && fuente.is(DamageTypes.DROWN)) {
                cantidad *= 10.0F;
            }
            if (CambiosDificultad.activo(EL_MUNDO_CONTRAATACA) && atacante == null) {
                cantidad *= 3.0F;
            }
            if (CambiosDificultad.activo(ESPINAS_MORTALES) && fuente.is(DamageTypes.CACTUS)) {
                cantidad = Math.max(cantidad, 7.777E9F);
            }
            if (fuente.is(DamageTypes.ENDER_PEARL)) {
                if (CambiosDificultad.activo(PERLAS_AFILADAS)) {
                    cantidad = Math.max(cantidad, 10.0F);
                }
                if (CambiosDificultad.activo(SALTOS_CAROS)) {
                    cantidad = Math.max(cantidad, jugador.getHealth() * 0.5F);
                }
            }
            if (atacante instanceof LivingEntity mob && !(atacante instanceof Player)) {
                if (CambiosDificultad.activo(GOLPES_TRIPLES) && esDeSiempre(mob) && mob instanceof Enemy) {
                    cantidad *= 3.0F;
                }
                if (CambiosDificultad.activo(LA_IRA_DEL_END) && mob instanceof EnderMan) {
                    cantidad *= 4.0F;
                }
                if (CambiosDificultad.activo(CIEN_DE_UN_GOLPE) && (mob instanceof EnderMan || mob instanceof Endermite)) {
                    cantidad = Math.max(cantidad, 100.0F);
                }
            }
        } else if (CambiosDificultad.activo(PIEL_MAS_GRUESA)) {
            // "Aguantan un 10 % mas": el mismo golpe les quita lo que les quitaba a 1/1,1.
            cantidad /= 1.1F;
        }
        return cantidad;
    }

    /** Si es un mob de Minecraft (no uno del mod). */
    public static boolean esDeSiempre(Entity e) {
        return "minecraft".equals(BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getNamespace());
    }
}
