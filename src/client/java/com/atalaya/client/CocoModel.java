package com.atalaya.client;

import com.atalaya.Atalaya;
import com.atalaya.entity.CocoEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Mth;

/**
 * El Coco: la malla generada (CocoMalla) y como se mueve (Juan, 16-10-2026: «haz el diseño 1 con todas sus animaciones»).
 *
 * - Andando: pesado y bamboleandose, las piernas cortas de lado a lado, los brazos larguisimos que se apoyan en el suelo
 *   a cada paso (con la contraria), la barriga que bota con retraso y la cresta que se mece.
 * - Quieto: respira (el tronco y la barriga), mira a los lados y ladea la cabeza, abre la boca a ratos, le suenan las
 *   tripas (la barriga tiembla) y tamborilea con los dedos en el suelo.
 * - El aviso (el segundo antes de tragarte): alza los dos brazos hacia ti, abre las manos y la cascara de par en par.
 * - Traga: los brazos se cierran hacia la boca, la boca se abre mas, se cierra de golpe y la cabeza traga hacia atras; la
 *   barriga se hincha.
 * - Lleno: la barriga hinchada, con las patadas del de dentro; la cabeza gacha, satisfecha, y de vez en cuando se da
 *   palmadas en la barriga.
 * - El manotazo: el brazo derecho barre de lado a lado.
 *
 * Las animaciones suman a la postura de reposo (las dos manos en el suelo y la boca cerrada). Del boceto a Minecraft
 * el giro en x conserva el signo: xRot positivo abre la boca, baja la cabeza, echa el tronco adelante y cierra los dedos;
 * negativo alza los brazos hacia delante.
 */
public class CocoModel extends EntityModel<CocoRenderState> {

    public static final ModelLayerLocation CAPA =
            new ModelLayerLocation(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "coco"), "main");

    private final ModelPart cuerpo;
    private final ModelPart tronco;
    private final ModelPart barriga;
    private final ModelPart cabeza;
    private final ModelPart quijada;
    private final ModelPart cresta;
    /** Los dos lados: 0 el izquierdo (x>0), 1 el derecho. */
    private final ModelPart[] brazo = new ModelPart[2];
    private final ModelPart[] antebrazo = new ModelPart[2];
    private final ModelPart[] mano = new ModelPart[2];
    private final ModelPart[][] dedo = new ModelPart[2][4];
    private final ModelPart[][] falange = new ModelPart[2][4];
    private final ModelPart[] pierna = new ModelPart[2];
    private final ModelPart[] canilla = new ModelPart[2];
    private final ModelPart[] pie = new ModelPart[2];

    public CocoModel(ModelPart raiz) {
        super(raiz);
        cuerpo = raiz.getChild("cuerpo");
        tronco = cuerpo.getChild("tronco");
        barriga = cuerpo.getChild("barriga");
        cabeza = cuerpo.getChild("cabeza");
        quijada = cabeza.getChild("quijada");
        cresta = cabeza.getChild("cresta");
        String[] lados = {"i", "d"};
        for (int l = 0; l < 2; l++) {
            String s = lados[l];
            brazo[l] = tronco.getChild("brazo_" + s);
            antebrazo[l] = brazo[l].getChild("antebrazo_" + s);
            mano[l] = antebrazo[l].getChild("mano_" + s);
            for (int k = 0; k < 4; k++) {
                dedo[l][k] = mano[l].getChild("mano_" + s + "_dedo" + k);
                falange[l][k] = dedo[l][k].getChild("mano_" + s + "_dedo" + k + "b");
            }
            pierna[l] = cuerpo.getChild("pierna_" + s);
            canilla[l] = pierna[l].getChild("canilla_" + s);
            pie[l] = canilla[l].getChild("pie_" + s);
        }
    }

    /** Un golpe de vez en cuando: casi siempre 0 y, un rato corto cada vuelta de 'x', sube a 1 y baja. */
    private static float aRatos(float x, float dureza) {
        return (float) Math.pow(Math.max(0.0F, Mth.sin(x)), dureza);
    }

    /** Suave de 0 a 1 entre a y b. */
    private static float entre(float x, float a, float b) {
        float k = Mth.clamp((x - a) / (b - a), 0.0F, 1.0F);
        return k * k * (3.0F - 2.0F * k);
    }

    /** Una curva de claves (t, valor), suave entre una y otra. */
    private static float claves(float t, float... tv) {
        if (t <= tv[0]) {
            return tv[1];
        }
        for (int i = 2; i < tv.length; i += 2) {
            if (t <= tv[i]) {
                return Mth.lerp(entre(t, tv[i - 2], tv[i]), tv[i - 1], tv[i + 1]);
            }
        }
        return tv[tv.length - 1];
    }

    private void abrirManos(float k) {
        for (int l = 0; l < 2; l++) {
            for (int j = 0; j < 4; j++) {
                dedo[l][j].xRot -= 0.75F * k;
                falange[l][j].xRot -= 0.55F * k;
            }
        }
    }

    @Override
    public void setupAnim(CocoRenderState s) {
        // Vuelve a la postura de reposo: las animaciones suman.
        super.setupAnim(s);
        float t = s.ageInTicks;
        float f = s.fase;
        boolean libre = s.estado == CocoEntity.LIBRE;
        boolean lleno = s.estado == CocoEntity.LLENO || s.estado == CocoEntity.TRAGANDO;
        float anda = libre ? Mth.clamp(s.walkAnimationSpeed * 1.4F, 0.0F, 1.0F) : 0.0F;
        float quieto = 1.0F - anda;
        float paso = s.walkAnimationPos * 0.5F;

        // Mirar a donde va (lo decide la cabeza del mob).
        cabeza.yRot += s.yRot * Mth.DEG_TO_RAD * 0.85F;
        cabeza.xRot += s.xRot * Mth.DEG_TO_RAD * 0.6F;

        // ---- Andar: pesado, bamboleandose ---------------------------------------------------------------------
        if (anda > 0.0F) {
            for (int l = 0; l < 2; l++) {
                float fase = paso + (l == 0 ? 0.0F : Mth.PI);
                pierna[l].xRot += Mth.cos(fase) * 0.55F * anda;
                float alza = Math.max(0.0F, -Mth.sin(fase));
                canilla[l].xRot += alza * 0.65F * anda;
                pie[l].xRot -= alza * 0.35F * anda;
                // El brazo va con la pierna contraria y se apoya en el suelo al llegar delante.
                brazo[l].xRot += Mth.cos(fase + Mth.PI) * 0.42F * anda;
                antebrazo[l].xRot += Math.max(0.0F, Mth.sin(fase + Mth.PI)) * 0.3F * anda;
            }
            cuerpo.y -= Math.abs(Mth.sin(paso)) * 1.1F * anda;
            cuerpo.zRot += Mth.sin(paso) * 0.075F * anda;
            cuerpo.yRot += Mth.sin(paso) * 0.05F * anda;
            tronco.xRot += 0.08F * anda;
            // La barriga bota con retraso, y la cresta se mece.
            float bote = Mth.sin(paso * 2.0F - 0.8F);
            barriga.y += bote * 0.6F * anda;
            barriga.yScale += bote * 0.03F * anda;
            cabeza.xRot += Mth.sin(paso * 2.0F + 0.4F) * 0.05F * anda;
            cresta.xRot += Mth.sin(paso * 2.0F - 1.2F) * 0.15F * anda;
        }

        // ---- Respirar, siempre ----------------------------------------------------------------------------------
        float lento = lleno ? 0.05F : 0.07F;
        float respira = 0.5F + 0.5F * Mth.sin(t * lento + f);
        tronco.xRot -= 0.03F * respira;
        barriga.xScale += 0.02F * respira;
        barriga.zScale += 0.025F * respira;
        cresta.zRot += Mth.sin(t * 0.05F + f) * 0.06F;
        cresta.xRot += Mth.sin(t * 0.07F + f * 0.5F) * 0.04F;

        // ---- Quieto y libre: mira, abre la boca, le suenan las tripas y tamborilea --------------------------------
        if (libre && quieto > 0.0F) {
            cabeza.yRot += Mth.sin(t * 0.025F + f) * 0.35F * quieto;
            cabeza.zRot += Mth.sin(t * 0.04F + f * 1.3F) * 0.08F * quieto;
            quijada.xRot += 0.14F * aRatos(t * 0.045F + f, 8.0F) * quieto;
            float tripas = aRatos(t * 0.031F + f * 2.0F, 14.0F) * quieto;
            barriga.xScale += 0.035F * tripas * Mth.sin(t * 1.3F);
            barriga.yScale -= 0.02F * tripas;
            float ganas = aRatos(t * 0.02F + f, 2.0F);
            for (int l = 0; l < 2; l++) {
                for (int j = 0; j < 4; j++) {
                    dedo[l][j].xRot -= 0.3F * aRatos(t * 0.28F - j * 0.7F + l * 1.9F + f, 6.0F) * ganas * quieto;
                }
            }
        }

        // ---- El aviso: alza los brazos, abre las manos y la cascara ---------------------------------------------
        float k = 0.0F;
        if (s.estado == CocoEntity.AVISANDO && s.aviso >= 0.0F) {
            k = entre(s.aviso, 0.0F, CocoEntity.AVISO * 0.7F);
        }
        if (k > 0.0F) {
            for (int l = 0; l < 2; l++) {
                float fuera = l == 0 ? -1.0F : 1.0F;
                brazo[l].xRot -= 1.25F * k;
                brazo[l].zRot += fuera * 0.45F * k;
                antebrazo[l].xRot -= 0.5F * k;
                mano[l].xRot -= 0.5F * k;
            }
            abrirManos(k);
            quijada.xRot += (0.85F + Mth.sin(t * 1.6F) * 0.03F) * k;
            cabeza.xRot -= 0.2F * k;
            tronco.xRot -= 0.1F * k;
        }

        // ---- Traga ------------------------------------------------------------------------------------------------
        float hincha = lleno ? 1.0F : 0.0F;
        if (s.estado == CocoEntity.TRAGANDO && s.traga >= 0.0F) {
            float u = Mth.clamp(s.traga / CocoEntity.TRAGA, 0.0F, 1.0F);
            float alza = claves(u, 0.0F, 1.25F, 0.35F, 1.6F, 1.0F, 0.0F);
            float cierra = claves(u, 0.0F, -0.45F, 0.35F, 0.25F, 1.0F, 0.0F);
            for (int l = 0; l < 2; l++) {
                float fuera = l == 0 ? -1.0F : 1.0F;
                brazo[l].xRot -= alza;
                brazo[l].zRot -= fuera * cierra;
                antebrazo[l].xRot -= alza * 0.4F;
            }
            abrirManos(claves(u, 0.0F, 1.0F, 0.35F, 0.0F));
            quijada.xRot += claves(u, 0.0F, 0.85F, 0.25F, 1.1F, 0.45F, 0.0F, 0.6F, 0.15F, 1.0F, 0.05F);
            cabeza.xRot += claves(u, 0.0F, -0.2F, 0.3F, -0.45F, 0.6F, 0.15F, 1.0F, 0.1F);
            hincha = claves(u, 0.0F, 0.0F, 0.35F, 0.0F, 0.65F, 1.25F, 1.0F, 1.0F);
        }

        // ---- Lleno: la barriga hinchada, con las patadas del de dentro ---------------------------------------------
        if (lleno) {
            barriga.xScale += 0.12F * hincha;
            barriga.yScale += 0.1F * hincha;
            barriga.zScale += 0.14F * hincha;
            if (s.estado == CocoEntity.LLENO) {
                float patada = aRatos(t * 0.23F + f, 10.0F) * aRatos(t * 0.047F + f * 2.0F, 1.5F);
                barriga.xScale += 0.06F * patada;
                barriga.zScale += 0.05F * patada;
                barriga.zRot += 0.06F * patada * Mth.sin(t * 0.7F);
                barriga.xRot -= 0.04F * patada;
                cabeza.xRot += 0.12F;
                quijada.xRot += 0.06F + 0.1F * aRatos(t * 0.06F + f, 6.0F);
                // De vez en cuando, palmadas en la barriga con la mano izquierda.
                float palmada = aRatos(t * 0.055F + f, 4.0F);
                float golpe = 0.5F + 0.5F * Mth.sin(t * 0.9F);
                brazo[0].xRot -= (0.75F + 0.12F * golpe) * palmada;
                brazo[0].zRot += 0.4F * palmada;
                antebrazo[0].xRot -= 0.55F * palmada;
            }
        }

        // ---- El manotazo: el brazo derecho barre de lado a lado ---------------------------------------------------
        if (s.manotazo >= 0.0F && s.manotazo < 12.0F) {
            float u = Mth.clamp(s.manotazo / 10.0F, 0.0F, 1.0F);
            float arco = Mth.sin(u * Mth.PI);
            brazo[1].xRot -= 1.45F * arco;
            brazo[1].yRot += 0.7F - 1.4F * entre(u, 0.15F, 0.75F);
            tronco.yRot -= 0.3F * arco;
            for (int j = 0; j < 4; j++) {
                dedo[1][j].xRot -= 0.6F * arco;
            }
        }
    }
}
