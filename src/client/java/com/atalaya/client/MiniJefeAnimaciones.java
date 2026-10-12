package com.atalaya.client;

import net.minecraft.client.animation.AnimationDefinition;

/**
 * Las animaciones de un mini jefe (las genera minijefes_anim.py en
 * &lt;Nombre&gt;Animaciones). Todas se suman a su postura de reposo y acaban en
 * ella, asi que se mezclan sin saltos.
 */
public record MiniJefeAnimaciones(AnimationDefinition reposo, AnimationDefinition andar, AnimationDefinition dormido,
                                  AnimationDefinition despertar, AnimationDefinition normal, AnimationDefinition area,
                                  AnimationDefinition especial, AnimationDefinition muerte) {
}
