package com.atalaya;

import com.atalaya.client.AturdimientoHud;
import com.atalaya.client.AturdimientoTeclado;
import com.atalaya.client.AvisoTrajeHud;
import com.atalaya.client.EstrellaParticula;
import com.atalaya.particula.AtalayaParticulas;
import net.fabricmc.fabric.api.client.particle.v1.ParticleProviderRegistry;
import com.atalaya.client.FrioHud;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import com.atalaya.client.FulminanteModel;
import com.atalaya.client.FulminanteRenderer;
import com.atalaya.client.VigiaModel;
import com.atalaya.client.RayoVigiaModel;
import com.atalaya.client.RayoVigiaRenderer;
import com.atalaya.client.VigiaParticula;
import net.minecraft.core.particles.SimpleParticleType;
import com.atalaya.client.VigiaRenderer;
import com.atalaya.entity.AtalayaEntities;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;
import com.atalaya.client.HidratacionHud;
import com.atalaya.client.VinetaHud;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.hud.HudElementRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.hud.VanillaHudElements;
import net.minecraft.resources.Identifier;

/**
 * Punto de entrada del CLIENTE.
 *
 * Aqui va todo lo que solo existe en el cliente: renderizado, HUD, modelos.
 * Es justo lo que un plugin no podia tocar.
 */
public class AtalayaClient implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        // Aviso de traje sin filtro. Se dibuja despues de la hotbar para que
        // quede por encima y no lo tape.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aviso_traje"),
                new AvisoTrajeHud());

        // Los dos medidores van enganchados a la HOTBAR, no al numero de
        // experiencia.
        //
        // Al numero de experiencia era lo natural —esta justo debajo— pero
        // vanilla solo lo dibuja cuando tienes nivel, y con nivel 0 los dos
        // medidores desaparecian con el. Costo encontrarlo porque en las
        // pruebas siempre habia experiencia de por medio y parecia que iba.
        //
        // La hotbar se dibuja SIEMPRE, y ademas es donde ya cuelgan el aviso del
        // traje y la vineta, que nunca han fallado.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "hidratacion"),
                new HidratacionHud());

        // El copo de frio, en el mismo sitio que la gota. La separacion, cuando
        // hace falta, la pone el propio elemento.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "frio"),
                new FrioHud());

        // El halo va ANTES de la hotbar, al contrario que los otros: es un velo
        // a pantalla completa, asi que tiene que quedar por DEBAJO de todo lo
        // demas del HUD. Si no, tenirria los corazones y la barra de
        // experiencia de naranja o de azul.
        //
        // Uno solo para el calor y el frio, para que no se sumen las opacidades
        // si algun dia coinciden los dos efectos.
        HudElementRegistry.attachElementBefore(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "vineta"),
                new VinetaHud());

        // El fulminante: su capa de modelo y quien lo pinta. Las animaciones
        // salen de heredar el modelo del creeper, asi que aqui no hay nada
        // sobre eso.
        ModelLayerRegistry.registerModelLayer(FulminanteModel.CAPA, FulminanteModel::crear);
        EntityRendererRegistry.register(AtalayaEntities.FULMINANTE, FulminanteRenderer::new);

        // El Vigia: malla y animaciones propias, nada heredado.
        ModelLayerRegistry.registerModelLayer(VigiaModel.CAPA, VigiaModel::crear);
        EntityRendererRegistry.register(AtalayaEntities.VIGIA, VigiaRenderer::new);
        // Y su rayo: malla propia apuntada al vuelo, como una flecha de luz.
        ModelLayerRegistry.registerModelLayer(RayoVigiaModel.CAPA, RayoVigiaModel::crear);
        EntityRendererRegistry.register(AtalayaEntities.RAYO_VIGIA, RayoVigiaRenderer::new);

        // El aviso de la tecla va DESPUES de la hotbar para quedar por encima:
        // es una instruccion, y taparla con cualquier cosa la haria inutil.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aturdimiento"),
                new AturdimientoHud());

        // Y quien cuenta las pulsaciones mientras dura.
        //
        // START y no END: aqui tambien se tragan las teclas que abren el
        // inventario, y para eso hay que llegar ANTES de que el juego las mire.
        ClientTickEvents.START_CLIENT_TICK.register(AturdimientoTeclado::tick);

        // Quien sabe dibujar la estrellita del aturdimiento.
        ParticleProviderRegistry.getInstance().register(
                AtalayaParticulas.ESTRELLA, EstrellaParticula.Fabrica::new);

        // Las ocho del Vigia: una clase, un comportamiento por tipo.
        particula(AtalayaParticulas.VIGIA_CHISPA, VigiaParticula.Tipo.CHISPA);
        particula(AtalayaParticulas.VIGIA_RAYO, VigiaParticula.Tipo.RAYO);
        particula(AtalayaParticulas.VIGIA_MALDICION, VigiaParticula.Tipo.MALDICION);
        particula(AtalayaParticulas.VIGIA_MARCA, VigiaParticula.Tipo.MARCA);
        particula(AtalayaParticulas.VIGIA_ZARPA, VigiaParticula.Tipo.ZARPA);
        particula(AtalayaParticulas.VIGIA_ESQUIRLA, VigiaParticula.Tipo.ESQUIRLA);
        particula(AtalayaParticulas.VIGIA_HUMO, VigiaParticula.Tipo.HUMO);
        particula(AtalayaParticulas.VIGIA_ALMA, VigiaParticula.Tipo.ALMA);

        Atalaya.LOGGER.info("Atalaya (cliente) iniciado.");
    }

    private static void particula(SimpleParticleType tipo, VigiaParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new VigiaParticula.Fabrica(sprites, comportamiento));
    }
}
