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
import com.atalaya.client.BurbujaNereaRenderer;
import com.atalaya.client.GanchoNereaRenderer;
import com.atalaya.client.NereaMalla;
import com.atalaya.client.NereaModel;
import com.atalaya.client.NereaParticula;
import com.atalaya.client.NereaRenderer;
import com.atalaya.client.AeralisMalla;
import com.atalaya.client.AeralisModel;
import com.atalaya.client.AeralisParticula;
import com.atalaya.client.AeralisRenderer;
import com.atalaya.client.PlataformaSelloRenderer;
import com.atalaya.client.FragmentoJadeRenderer;
import com.atalaya.client.PicoTierraRenderer;
import com.atalaya.client.PilarTierraRenderer;
import com.atalaya.client.RajangMalla;
import com.atalaya.client.RajangModel;
import com.atalaya.client.RajangParteRenderer;
import com.atalaya.client.RajangParticula;
import com.atalaya.client.RajangRenderer;
import com.atalaya.client.TotemSelloRenderer;
import com.atalaya.client.NovilisMalla;
import com.atalaya.client.NovilisModel;
import com.atalaya.client.NovilisParticula;
import com.atalaya.client.NovilisRenderer;
import com.atalaya.client.CuchillaVientoRenderer;
import com.atalaya.client.NucleoVientoRenderer;
import com.atalaya.client.RafagaAeralisRenderer;
import com.atalaya.client.TornadoAeralisRenderer;
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

        // Nerea: malla y animaciones generadas desde nerea_juego*.py, y lo
        // suyo alrededor: las burbujas, el ancla (la misma malla que la de su
        // mano), las paredes de agua y los geiseres.
        ModelLayerRegistry.registerModelLayer(NereaModel.CAPA, NereaMalla::crear);
        ModelLayerRegistry.registerModelLayer(NereaModel.CAPA_AURA, NereaMalla::crearAura);
        EntityRendererRegistry.register(AtalayaEntities.NEREA, NereaRenderer::new);
        ModelLayerRegistry.registerModelLayer(BurbujaNereaRenderer.CAPA, BurbujaNereaRenderer.Modelo::crear);
        EntityRendererRegistry.register(AtalayaEntities.BURBUJA_NEREA, BurbujaNereaRenderer::new);
        ModelLayerRegistry.registerModelLayer(GanchoNereaRenderer.CAPA, NereaMalla::crearAncla);
        EntityRendererRegistry.register(AtalayaEntities.GANCHO_NEREA, GanchoNereaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.OLA_NEREA, com.atalaya.client.OlaNereaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.GEISER_NEREA, com.atalaya.client.GeiserNereaRenderer::new);

        // Aeralis: malla y animaciones generadas desde vendaval_juego*.py, y lo
        // suyo: cuchillas, tornados, rafagas y nucleos (dibujados a mano).
        ModelLayerRegistry.registerModelLayer(AeralisModel.CAPA, AeralisMalla::crear);
        ModelLayerRegistry.registerModelLayer(AeralisModel.CAPA_AURA, AeralisMalla::crearAura);
        EntityRendererRegistry.register(AtalayaEntities.AERALIS, AeralisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.CUCHILLA_VIENTO, CuchillaVientoRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.TORNADO_AERALIS, TornadoAeralisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.RAFAGA_AERALIS, RafagaAeralisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.NUCLEO_VIENTO, NucleoVientoRenderer::new);

        // Rajang: malla y animaciones generadas desde rajang_juego*.py, y lo
        // suyo: picos, pilares, totems, plataformas y fragmentos (a mano).
        ModelLayerRegistry.registerModelLayer(RajangModel.CAPA, RajangMalla::crear);
        ModelLayerRegistry.registerModelLayer(RajangModel.CAPA_AURA, RajangMalla::crearAura);
        EntityRendererRegistry.register(AtalayaEntities.RAJANG, RajangRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.RAJANG_PARTE, RajangParteRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.PICO_TIERRA, PicoTierraRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.PILAR_TIERRA, PilarTierraRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.TOTEM_SELLO, TotemSelloRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.PLATAFORMA_SELLO, PlataformaSelloRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.FRAGMENTO_JADE, FragmentoJadeRenderer::new);

        // Novilis: malla y animaciones generadas desde novilis_juego*.py, y lo
        // que lanza (medias lunas, sellos, la onda, los soles, estatuas y fuentes).
        ModelLayerRegistry.registerModelLayer(NovilisModel.CAPA, NovilisMalla::crear);
        EntityRendererRegistry.register(AtalayaEntities.NOVILIS, NovilisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.TAJO_NOVILIS, com.atalaya.client.TajoNovilisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.SELLO_SOL, com.atalaya.client.SelloSolRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.ONDA_FUEGO, com.atalaya.client.OndaFuegoRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.SOL_NOVILIS, com.atalaya.client.SolNovilisRenderer::new);
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.EstatuaNovilisRenderer.CAPA, com.atalaya.client.EstatuaNovilisMalla::crear);
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.EstatuaNovilisRenderer.CAPA_ROTA, com.atalaya.client.EstatuaNovilisMalla::crearRota);
        EntityRendererRegistry.register(AtalayaEntities.ESTATUA_NOVILIS, com.atalaya.client.EstatuaNovilisRenderer::new);
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.FuenteSolarRenderer.CAPA, com.atalaya.client.FuenteSolarMalla::crear);
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.FuenteSolarRenderer.CAPA_ROTA, com.atalaya.client.FuenteSolarMalla::crearRota);
        EntityRendererRegistry.register(AtalayaEntities.FUENTE_SOLAR, com.atalaya.client.FuenteSolarRenderer::new);

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

        // Las armaduras de los jefes, en 3D y con capas (sustituyen a la capa plana).
        com.atalaya.client.ArmaduraJefeRender.registrar();
        // Sus habilidades: la tecla (R), lo que dicen al pasar el raton y lo que lanzan sus armas.
        com.atalaya.client.HabilidadCliente.registrar();
        EntityRendererRegistry.register(AtalayaEntities.TRIDENTE_MAREAS, com.atalaya.client.TridenteMareasRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.FLECHA_VENDAVAL, com.atalaya.client.FlechaVendavalRenderer::new);

        // El tajo de las espadas de los jefes.
        for (SimpleParticleType tajo : new SimpleParticleType[]{AtalayaParticulas.MAREAS_TAJO, AtalayaParticulas.JADE_TAJO,
                AtalayaParticulas.VENDAVAL_TAJO, AtalayaParticulas.SOLAR_TAJO}) {
            ParticleProviderRegistry.getInstance().register(tajo, com.atalaya.client.TajoParticula.Fabrica::new);
        }

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

        // Las diez de Nerea.
        nerea(AtalayaParticulas.NEREA_BURBUJA, NereaParticula.Tipo.BURBUJA);
        nerea(AtalayaParticulas.NEREA_ESPUMA, NereaParticula.Tipo.ESPUMA);
        nerea(AtalayaParticulas.NEREA_GOTA, NereaParticula.Tipo.GOTA);
        nerea(AtalayaParticulas.NEREA_OLA, NereaParticula.Tipo.OLA);
        nerea(AtalayaParticulas.NEREA_REMOLINO, NereaParticula.Tipo.REMOLINO);
        nerea(AtalayaParticulas.NEREA_CHISPA, NereaParticula.Tipo.CHISPA);
        nerea(AtalayaParticulas.NEREA_OJO, NereaParticula.Tipo.OJO);
        nerea(AtalayaParticulas.NEREA_SELLO, NereaParticula.Tipo.SELLO);
        nerea(AtalayaParticulas.NEREA_CORAZON, NereaParticula.Tipo.CORAZON);
        nerea(AtalayaParticulas.NEREA_LUZ, NereaParticula.Tipo.LUZ);
        nerea(AtalayaParticulas.NEREA_ONDA, NereaParticula.Tipo.ONDA);
        nerea(AtalayaParticulas.NEREA_ROCA, NereaParticula.Tipo.ROCA);
        nerea(AtalayaParticulas.NEREA_POLVO, NereaParticula.Tipo.POLVO);

        // Las once de Aeralis.
        aeralis(AtalayaParticulas.AERALIS_VIENTO, AeralisParticula.Tipo.VIENTO);
        aeralis(AtalayaParticulas.AERALIS_ESCAMA, AeralisParticula.Tipo.ESCAMA);
        aeralis(AtalayaParticulas.AERALIS_REMOLINO, AeralisParticula.Tipo.REMOLINO);
        aeralis(AtalayaParticulas.AERALIS_RAYO, AeralisParticula.Tipo.RAYO);
        aeralis(AtalayaParticulas.AERALIS_MARCA, AeralisParticula.Tipo.MARCA);
        aeralis(AtalayaParticulas.AERALIS_LUZ, AeralisParticula.Tipo.LUZ);
        aeralis(AtalayaParticulas.AERALIS_ORO, AeralisParticula.Tipo.ORO);
        aeralis(AtalayaParticulas.AERALIS_ONDA, AeralisParticula.Tipo.ONDA);
        aeralis(AtalayaParticulas.AERALIS_CIRCULO, AeralisParticula.Tipo.CIRCULO);
        aeralis(AtalayaParticulas.AERALIS_POLVO, AeralisParticula.Tipo.POLVO);
        aeralis(AtalayaParticulas.AERALIS_JIRON, AeralisParticula.Tipo.JIRON);

        // Las quince de Rajang.
        rajang(AtalayaParticulas.RAJANG_POLVO, RajangParticula.Tipo.POLVO);
        rajang(AtalayaParticulas.RAJANG_ROCA, RajangParticula.Tipo.ROCA);
        rajang(AtalayaParticulas.RAJANG_JADE, RajangParticula.Tipo.JADE);
        rajang(AtalayaParticulas.RAJANG_CHISPA, RajangParticula.Tipo.CHISPA);
        rajang(AtalayaParticulas.RAJANG_HOJA, RajangParticula.Tipo.HOJA);
        rajang(AtalayaParticulas.RAJANG_ONDA, RajangParticula.Tipo.ONDA);
        rajang(AtalayaParticulas.RAJANG_GRIETA, RajangParticula.Tipo.GRIETA);
        rajang(AtalayaParticulas.RAJANG_AVISO, RajangParticula.Tipo.AVISO);
        rajang(AtalayaParticulas.RAJANG_MARCA, RajangParticula.Tipo.MARCA);
        rajang(AtalayaParticulas.RAJANG_SELLO, RajangParticula.Tipo.SELLO);
        rajang(AtalayaParticulas.RAJANG_RUNA, RajangParticula.Tipo.RUNA);
        rajang(AtalayaParticulas.RAJANG_LLAMA, RajangParticula.Tipo.LLAMA);
        rajang(AtalayaParticulas.RAJANG_LASTRE, RajangParticula.Tipo.LASTRE);
        rajang(AtalayaParticulas.RAJANG_ORO, RajangParticula.Tipo.ORO);
        rajang(AtalayaParticulas.RAJANG_ZARPAZO, RajangParticula.Tipo.ZARPAZO);

        // Las once de Novilis.
        novilis(AtalayaParticulas.NOVILIS_BRASA, NovilisParticula.Tipo.BRASA);
        novilis(AtalayaParticulas.NOVILIS_CHISPA, NovilisParticula.Tipo.CHISPA);
        novilis(AtalayaParticulas.NOVILIS_CENIZA, NovilisParticula.Tipo.CENIZA);
        novilis(AtalayaParticulas.NOVILIS_LLAMA, NovilisParticula.Tipo.LLAMA);
        novilis(AtalayaParticulas.NOVILIS_HUMO, NovilisParticula.Tipo.HUMO);
        novilis(AtalayaParticulas.NOVILIS_ONDA, NovilisParticula.Tipo.ONDA);
        novilis(AtalayaParticulas.NOVILIS_ROCA, NovilisParticula.Tipo.ROCA);
        novilis(AtalayaParticulas.NOVILIS_NOTA, NovilisParticula.Tipo.NOTA);
        novilis(AtalayaParticulas.NOVILIS_LUZ, NovilisParticula.Tipo.LUZ);
        novilis(AtalayaParticulas.NOVILIS_AZUL, NovilisParticula.Tipo.AZUL);
        novilis(AtalayaParticulas.NOVILIS_CARMESI, NovilisParticula.Tipo.CARMESI);

        // La presencia de Nerea: temblor, retumbo y miedo. El miedo va con los
        // velos de camara (calabaza, nieve polvo...): un velo bajo el resto del
        // HUD. NO cuelga de la hotbar como la vineta del calor: en espectador
        // la hotbar no se dibuja, y con ella desaparecia todo lo enganchado.
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.AeralisEfectosCliente::tick);
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.RajangEfectosCliente::tick);
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.NereaEfectosCliente::tick);
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.NovilisEfectosCliente::tick);
        // La Ofrenda al Sol: la secuencia de teclas de quien Novilis tiene en las manos.
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.OfrendaCliente::tick);
        // La musica de cada jefe mientras pelea cerca (y la de vanilla calla: MusicaJefesMixin).
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.MusicaJefes::tick);
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.MISC_OVERLAYS,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "miedo"),
                new com.atalaya.client.MiedoHud());
        // Su barra de jefe, propia: la ola, el marco de prismarina, el corazon de
        // la fase (la calavera mientras mira) y el agua del color de la
        // maldicion. Va con la barra de jefe de vanilla,
        // que se dibuja en cualquier modo de juego (la hotbar no en espectador).
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.BOSS_BAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_nerea"),
                new com.atalaya.client.NereaBarraHud());
        // La de Aeralis, despues: si las dos estan a la vista, va debajo.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_nerea"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_aeralis"),
                new com.atalaya.client.AeralisBarraHud());
        // Y la de Rajang, debajo de las dos.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_aeralis"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_rajang"),
                new com.atalaya.client.RajangBarraHud());
        // Y la de Novilis, debajo de las tres.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_rajang"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_novilis"),
                new com.atalaya.client.NovilisBarraHud());
        // La pantalla de la Ofrenda al Sol (la del atrapado), por encima de la hotbar.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "ofrenda"),
                new com.atalaya.client.OfrendaHud());
        // El icono de la habilidad de la armadura, a la derecha de la hotbar.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "habilidad"),
                new com.atalaya.client.HabilidadHud());
        // La quemadura de Novilis, a la izquierda de los corazones.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "quemadura"),
                new com.atalaya.client.QuemaduraHud());

        // Solo en el entorno de pruebas (con run/atalaya_fotos.flag).
        com.atalaya.client.FotosPrueba.registrar();

        Atalaya.LOGGER.info("Atalaya (cliente) iniciado.");
    }

    private static void nerea(SimpleParticleType tipo, NereaParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new NereaParticula.Fabrica(sprites, comportamiento));
    }

    private static void rajang(SimpleParticleType tipo, RajangParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new RajangParticula.Fabrica(sprites, comportamiento));
    }

    private static void novilis(SimpleParticleType tipo, NovilisParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new NovilisParticula.Fabrica(sprites, comportamiento));
    }

    private static void aeralis(SimpleParticleType tipo, AeralisParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new AeralisParticula.Fabrica(sprites, comportamiento));
    }

    private static void particula(SimpleParticleType tipo, VigiaParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new VigiaParticula.Fabrica(sprites, comportamiento));
    }
}
