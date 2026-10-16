package com.atalaya.client;

import com.atalaya.Atalaya;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * El Fogonazo: la malla generada (FogonazoMalla) y como se mueve (Juan, 16-10-2026: «sus animaciones de movimiento y
 * de quieto hay que ponerselas y mejorarlas»).
 *
 * - Andando y corriendo: trota en diagonal (la delantera de un lado con la trasera del otro); cada pata se adelanta
 *   doblando la rodilla, para levantar el pie. El cuerpo sube y baja y se mece, se echa adelante al correr; el farol se
 *   balancea con retraso (cuelga del talle) y las antenas se pliegan hacia atras.
 * - Quieto: tantea con las antenas (cada una a su aire, y de vez en cuando una se levanta de golpe), mira a los lados y
 *   ladea la cabeza, mueve las mandibulas a ratos, respira (el farol late, las placas se abren un poco con el y el cuerpo
 *   sube y baja) y alguna vez da un golpecito con una pata.
 * - Al hincharse (el creeper que se ceba) se abre: levanta las placas del farol y el escudo, abre la quijada y las
 *   mandibulas, levanta las antenas hacia delante y el farol crece. El parpadeo blanco y el hincharse entero son los del
 *   creeper (FogonazoRenderer).
 *
 * Cada uno lleva su fase (FogonazoRenderState.fase): dos Fogonazos juntos no se mueven a la vez.
 */
public class FogonazoModel extends EntityModel<FogonazoRenderState> {

    public static final ModelLayerLocation CAPA =
            new ModelLayerLocation(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "fogonazo"), "main");

    private final ModelPart cuerpo;
    private final ModelPart farol;
    private final ModelPart nucleo;
    private final ModelPart[] placas = new ModelPart[4];
    private final ModelPart cabeza;
    private final ModelPart escudo;
    private final ModelPart quijada;
    private final ModelPart mandibulaD;
    private final ModelPart mandibulaI;
    private final ModelPart antenaD;
    private final ModelPart antenaI;
    /** Las patas (delantera derecha, delantera izquierda, trasera derecha, trasera izquierda) y sus canillas. */
    private final ModelPart[] patas = new ModelPart[4];
    private final ModelPart[] canillas = new ModelPart[4];
    /** El trote en diagonal: la delantera derecha va con la trasera izquierda. */
    private static final float[] FASE_PATA = {0.0F, Mth.PI, Mth.PI, 0.0F};

    public FogonazoModel(ModelPart raiz) {
        super(raiz);
        cuerpo = raiz.getChild("cuerpo");
        farol = cuerpo.getChild("farol");
        nucleo = farol.getChild("nucleo");
        for (int i = 0; i < placas.length; i++) {
            placas[i] = farol.getChild("placa" + i);
        }
        cabeza = cuerpo.getChild("cabeza");
        escudo = cabeza.getChild("escudo");
        quijada = cabeza.getChild("quijada");
        mandibulaD = cabeza.getChild("mandibula_d");
        mandibulaI = cabeza.getChild("mandibula_i");
        antenaD = cabeza.getChild("antena_d");
        antenaI = cabeza.getChild("antena_i");
        String[] nombres = {"pata_dd", "pata_di", "pata_td", "pata_ti"};
        for (int i = 0; i < 4; i++) {
            patas[i] = cuerpo.getChild(nombres[i]);
            canillas[i] = patas[i].getChild(nombres[i] + "_canilla");
        }
    }

    /** Un golpe de vez en cuando: casi siempre 0 y, un rato corto cada vuelta de 'x', sube a 1 y baja. */
    private static float aRatos(float x, float dureza) {
        return (float) Math.pow(Math.max(0.0F, Mth.sin(x)), dureza);
    }

    @Override
    public void setupAnim(FogonazoRenderState estado) {
        // Vuelve a la postura de reposo: las animaciones suman.
        super.setupAnim(estado);
        float t = estado.ageInTicks;
        float f = estado.fase;
        float s = Mth.clamp(estado.swelling, 0.0F, 1.0F);
        float anda = Mth.clamp(estado.walkAnimationSpeed * 1.2F, 0.0F, 1.0F);
        float quieto = 1.0F - anda;
        float paso = estado.walkAnimationPos * 0.6662F;

        // Mirar a donde va (lo decide la cabeza del mob).
        cabeza.yRot += estado.yRot * Mth.DEG_TO_RAD * 0.8F;
        cabeza.xRot += estado.xRot * Mth.DEG_TO_RAD * 0.5F;

        // ---- Andar y correr --------------------------------------------------------------------------------------
        for (int i = 0; i < 4; i++) {
            float fase = paso + FASE_PATA[i];
            boolean trasera = i >= 2;
            // La pata va y viene; al adelantarse (cuando el seno es negativo) dobla la rodilla y levanta el pie.
            patas[i].xRot += Mth.cos(fase) * (trasera ? 0.6F : 0.75F) * anda;
            canillas[i].xRot += Math.max(0.0F, -Mth.sin(fase)) * (trasera ? 0.7F : 0.9F) * anda;
        }
        cuerpo.y -= Math.abs(Mth.sin(paso)) * 0.9F * anda;
        cuerpo.zRot += Mth.sin(paso) * 0.05F * anda;
        cuerpo.xRot += 0.07F * anda;
        // El farol cuelga del talle: se balancea con retraso, dos veces por zancada.
        farol.xRot += Mth.sin(paso * 2.0F - 1.0F) * 0.07F * anda;
        farol.zRot -= Mth.sin(paso - 0.6F) * 0.06F * anda;
        cabeza.xRot += Mth.sin(paso * 2.0F + 0.5F) * 0.04F * anda - 0.07F * anda;
        // Las antenas se pliegan hacia atras al correr, y tiemblan.
        antenaD.xRot -= (0.3F + Mth.sin(t * 0.9F) * 0.04F) * anda;
        antenaI.xRot -= (0.3F + Mth.sin(t * 0.9F + 1.7F) * 0.04F) * anda;

        // ---- Quieto ----------------------------------------------------------------------------------------------
        // Tantea con las antenas, cada una a su aire, y de vez en cuando levanta una de golpe.
        antenaD.yRot += (Mth.sin(t * 0.07F + f) * 0.45F + Mth.sin(t * 0.19F + f * 2.0F) * 0.08F) * quieto;
        antenaD.xRot += (Mth.sin(t * 0.09F + f * 1.7F) * 0.25F + aRatos(t * 0.035F + f * 3.0F, 6.0F) * 0.6F) * quieto;
        antenaI.yRot += (Mth.sin(t * 0.075F + f + 2.4F) * 0.45F + Mth.sin(t * 0.17F + f) * 0.08F) * quieto;
        antenaI.xRot += (Mth.sin(t * 0.085F + f * 0.6F + 1.1F) * 0.25F
                + aRatos(t * 0.031F + f * 3.0F + 2.6F, 6.0F) * 0.6F) * quieto;
        // Mira a los lados y ladea la cabeza, curioso.
        cabeza.yRot += Mth.sin(t * 0.035F + f) * 0.45F * quieto;
        cabeza.zRot += Mth.sin(t * 0.045F + f * 1.3F) * 0.12F * quieto;
        // Las mandibulas, a ratos, como si masticara.
        float muerde = aRatos(t * 0.18F + f * 2.0F, 6.0F) * aRatos(t * 0.03F + f, 1.5F);
        mandibulaD.yRot += muerde * 0.35F * quieto;
        mandibulaI.yRot -= muerde * 0.35F * quieto;
        quijada.xRot += muerde * 0.12F * quieto;
        // Respira: el farol late, las placas se abren un poco con el y el cuerpo sube y baja.
        float respira = 0.5F + 0.5F * Mth.sin(t * 0.09F + f);
        for (ModelPart placa : placas) {
            placa.xRot -= 0.09F * respira * quieto;
        }
        cuerpo.y -= respira * 0.4F * quieto;
        farol.xRot += Mth.sin(t * 0.05F + f) * 0.03F * quieto;
        // Alguna vez, un golpecito con una pata.
        int cual = Math.floorMod((int) ((t * 0.04F + f * 5.0F) / Mth.TWO_PI), 4);
        float golpecito = aRatos(t * 0.04F + f * 5.0F, 12.0F) * quieto;
        patas[cual].xRot -= golpecito * 0.25F;
        canillas[cual].xRot += golpecito * 0.6F;

        // ---- Al hincharse: se abre -------------------------------------------------------------------------------
        float late = 1.0F + 0.05F * Mth.sin(t * 0.09F + f) + 0.3F * s;
        nucleo.xScale = late;
        nucleo.yScale = late;
        nucleo.zScale = late;
        farol.xRot -= 0.18F * s;
        for (ModelPart placa : placas) {
            placa.xRot -= 0.4F * s;
        }
        escudo.xRot -= 0.35F * s;
        quijada.xRot += 0.6F * s;
        mandibulaD.yRot += 0.7F * s;
        mandibulaI.yRot -= 0.7F * s;
        antenaD.xRot += 0.3F * s;
        antenaI.xRot += 0.3F * s;
    }
}
