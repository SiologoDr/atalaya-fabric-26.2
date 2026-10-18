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
import com.atalaya.client.AltarIdoloRenderer;
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
                oculto(new AvisoTrajeHud()));

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
                oculto(new HidratacionHud()));

        // El copo de frio, en el mismo sitio que la gota. La separacion, cuando
        // hace falta, la pone el propio elemento.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "frio"),
                oculto(new FrioHud()));

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
                oculto(new VinetaHud()));

        // El fulminante: su capa de modelo y quien lo pinta. Las animaciones
        // salen de heredar el modelo del creeper, asi que aqui no hay nada
        // sobre eso.
        ModelLayerRegistry.registerModelLayer(FulminanteModel.CAPA, FulminanteModel::crear);
        EntityRendererRegistry.register(AtalayaEntities.FULMINANTE, FulminanteRenderer::new);

        // El Fogonazo: la malla generada por fogonazo_juego.py, que anima FogonazoModel; lo que brilla y, cuando te
        // estalla cerca, la pantalla en blanco (DeslumbreHud, por encima de todo el HUD).
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.FogonazoModel.CAPA, com.atalaya.client.FogonazoMalla::crear);
        EntityRendererRegistry.register(AtalayaEntities.FOGONAZO, com.atalaya.client.FogonazoRenderer::new);
        HudElementRegistry.addLast(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "deslumbre"),
                new com.atalaya.client.DeslumbreHud());
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.DeslumbreHud::tick);
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking.registerGlobalReceiver(
                com.atalaya.net.AtalayaRed.Deslumbre.TIPO,
                (carga, contexto) -> com.atalaya.client.DeslumbreHud.recibir(carga));
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents.DISCONNECT.register(
                (manejador, cliente) -> com.atalaya.client.DeslumbreHud.olvidar());

        // El Coco: la malla generada por coco_juego.py, que anima CocoModel; lo que brilla, el aviso de encima cuando
        // tiene a alguien dentro (CocoRenderer) y, para el de dentro, la pantalla roja con el latido (por debajo de la
        // barra y los corazones, para que vea como se le va la vida).
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.CocoModel.CAPA, com.atalaya.client.CocoMalla::crear);
        EntityRendererRegistry.register(AtalayaEntities.COCO, com.atalaya.client.CocoRenderer::new);
        HudElementRegistry.attachElementBefore(VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "coco_dentro"), new com.atalaya.client.CocoDentroHud());
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.CocoDentroHud::tick);

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
        EntityRendererRegistry.register(AtalayaEntities.CADENA_NEREA, com.atalaya.client.CadenaNereaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.REFUGIO_NEREA, com.atalaya.client.RefugioNereaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.REMOLINO_LADRON, com.atalaya.client.RemolinoLadronRenderer::new);
        // Los minijuegos de Aeralis
        EntityRendererRegistry.register(AtalayaEntities.VELETA_AERALIS, com.atalaya.client.VeletaAeralisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.CIRCULO_RAYO, com.atalaya.client.CirculoRayoRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.CHISPA_AERALIS, com.atalaya.client.ChispaAeralisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.REMOLINO_CHISPA, com.atalaya.client.RemolinoChispaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.SOL_CENIT, com.atalaya.client.SolCenitRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.EGIDA_NOVILIS, com.atalaya.client.EgidaNovilisRenderer::new);
        // Los minijuegos de Novilis
        EntityRendererRegistry.register(AtalayaEntities.YUNQUE_FORJA, com.atalaya.client.YunqueForjaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.BRASA_ENTERRADA, com.atalaya.client.BrasaEnterradaRenderer::new);
        // Los minijuegos de Nerea
        EntityRendererRegistry.register(AtalayaEntities.POZA_ABISMO, com.atalaya.client.PozaAbismoRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.CORCHO_ABISMO, com.atalaya.client.CorchoAbismoRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.PERLA_LANZADA, com.atalaya.client.PerlaLanzadaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.MORENA_NEREA, com.atalaya.client.MorenaNereaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.MORENA_SALTO, com.atalaya.client.MorenaSaltoRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.CANON_NAUFRAGIO, com.atalaya.client.CanonNaufragioRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.PILA_BALAS, com.atalaya.client.PilaBalasRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.BALA_CANON, com.atalaya.client.BalaCanonRenderer::new);

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
        EntityRendererRegistry.register(AtalayaEntities.ALTAR_IDOLO, AltarIdoloRenderer::new);
        // Los minijuegos de Rajang: la luz del prisma, las trampas de oro, las columnas de los glifos y las losas.
        EntityRendererRegistry.register(AtalayaEntities.LUZ_PRISMA, com.atalaya.client.LuzPrismaRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.TRAMPA_ORO, com.atalaya.client.TrampaOroRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.GLIFO_TEMPLO, com.atalaya.client.GlifoTemploRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.LOSA_JADE, com.atalaya.client.LosaJadeRenderer::new);

        // Novilis: malla y animaciones generadas desde novilis_juego*.py, y lo
        // que lanza (medias lunas, sellos, la onda, los soles, las estatuas, el camino de
        // llamas y las grietas).
        ModelLayerRegistry.registerModelLayer(NovilisModel.CAPA, NovilisMalla::crear);
        EntityRendererRegistry.register(AtalayaEntities.NOVILIS, NovilisRenderer::new);

        // Los cuatro mini jefes: su malla (minijefes_juego.py), sus animaciones (minijefes_anim.py) y
        // lo grande de sus ataques. Escala: lo que mide su boceto en el mundo (en su Geometria, que
        // genera minijefes_anim.py); la sombra crece con lo que han crecido (K).
        EntityRendererRegistry.register(AtalayaEntities.MOCTEZUMA, ctx -> new com.atalaya.client.MiniJefeRenderer<>(ctx, "moctezuma",
                com.atalaya.client.MoctezumaAnimaciones.JUEGO, new com.atalaya.client.MoctezumaEfectos(),
                com.atalaya.entity.MoctezumaGeometria.ESCALA, 0.07F, 1.4F * com.atalaya.entity.MoctezumaEntity.K));
        EntityRendererRegistry.register(AtalayaEntities.YIATZO, ctx -> new com.atalaya.client.MiniJefeRenderer<>(ctx, "yiatzo",
                com.atalaya.client.YiatzoAnimaciones.JUEGO, new com.atalaya.client.YiatzoEfectos(),
                com.atalaya.entity.YiatzoGeometria.ESCALA, 0.08F, 1.2F * com.atalaya.entity.YiatzoEntity.K));
        EntityRendererRegistry.register(AtalayaEntities.ATLAHUA, ctx -> new com.atalaya.client.MiniJefeRenderer<>(ctx, "atlahua",
                com.atalaya.client.AtlahuaAnimaciones.JUEGO, new com.atalaya.client.AtlahuaEfectos(),
                com.atalaya.entity.AtlahuaGeometria.ESCALA, 0.05F, 1.5F * com.atalaya.entity.AtlahuaEntity.K));
        EntityRendererRegistry.register(AtalayaEntities.XIUHQUETZAL, ctx -> new com.atalaya.client.MiniJefeRenderer<>(ctx,
                "xiuhquetzal", com.atalaya.client.XiuhquetzalAnimaciones.JUEGO, new com.atalaya.client.XiuhquetzalEfectos(),
                com.atalaya.entity.XiuhquetzalGeometria.ESCALA, 0.12F, 1.8F * com.atalaya.entity.XiuhquetzalEntity.K));
        EntityRendererRegistry.register(AtalayaEntities.TAJO_NOVILIS, com.atalaya.client.TajoNovilisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.SELLO_SOL, com.atalaya.client.SelloSolRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.ONDA_FUEGO, com.atalaya.client.OndaFuegoRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.SOL_NOVILIS, com.atalaya.client.SolNovilisRenderer::new);
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.EstatuaNovilisRenderer.CAPA, com.atalaya.client.EstatuaNovilisMalla::crear);
        ModelLayerRegistry.registerModelLayer(com.atalaya.client.EstatuaNovilisRenderer.CAPA_ROTA, com.atalaya.client.EstatuaNovilisMalla::crearRota);
        EntityRendererRegistry.register(AtalayaEntities.ESTATUA_NOVILIS, com.atalaya.client.EstatuaNovilisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.CAMINO_LLAMAS, com.atalaya.client.CaminoLlamasRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.GRIETA_NOVILIS, com.atalaya.client.GrietaNovilisRenderer::new);
        EntityRendererRegistry.register(AtalayaEntities.ESTRADO_NOVILIS, com.atalaya.client.EstradoNovilisRenderer::new);

        // El aviso de la tecla va DESPUES de la hotbar para quedar por encima:
        // es una instruccion, y taparla con cualquier cosa la haria inutil.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aturdimiento"),
                oculto(new AturdimientoHud()));

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
        nerea(AtalayaParticulas.NEREA_NOTA, NereaParticula.Tipo.NOTA);
        nerea(AtalayaParticulas.NEREA_HUMO, NereaParticula.Tipo.HUMO);
        nerea(AtalayaParticulas.NEREA_FOGONAZO, NereaParticula.Tipo.FOGONAZO);

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
        rajang(AtalayaParticulas.RAJANG_HUELLA, RajangParticula.Tipo.HUELLA);

        // Las once de Novilis.
        novilis(AtalayaParticulas.NOVILIS_BRASA, NovilisParticula.Tipo.BRASA);
        novilis(AtalayaParticulas.NOVILIS_CHISPA, NovilisParticula.Tipo.CHISPA);
        novilis(AtalayaParticulas.NOVILIS_CENIZA, NovilisParticula.Tipo.CENIZA);
        // Las del mundo maldito (Momento Maldicion): con el andar de la luz de Nerea y de la ceniza de Novilis.
        nerea(AtalayaParticulas.MALDICION_MOTA, NereaParticula.Tipo.LUZ);
        novilis(AtalayaParticulas.MALDICION_CENIZA, NovilisParticula.Tipo.CENIZA);
        novilis(AtalayaParticulas.NOVILIS_LLAMA, NovilisParticula.Tipo.LLAMA);
        novilis(AtalayaParticulas.NOVILIS_HUMO, NovilisParticula.Tipo.HUMO);
        novilis(AtalayaParticulas.NOVILIS_ONDA, NovilisParticula.Tipo.ONDA);
        novilis(AtalayaParticulas.NOVILIS_ROCA, NovilisParticula.Tipo.ROCA);
        novilis(AtalayaParticulas.NOVILIS_NOTA, NovilisParticula.Tipo.NOTA);
        novilis(AtalayaParticulas.NOVILIS_LUZ, NovilisParticula.Tipo.LUZ);
        novilis(AtalayaParticulas.NOVILIS_AZUL, NovilisParticula.Tipo.AZUL);
        novilis(AtalayaParticulas.NOVILIS_CARMESI, NovilisParticula.Tipo.CARMESI);
        novilis(AtalayaParticulas.NOVILIS_PIEDRA, NovilisParticula.Tipo.ICONO);
        novilis(AtalayaParticulas.NOVILIS_PAPEL, NovilisParticula.Tipo.ICONO);
        novilis(AtalayaParticulas.NOVILIS_TIJERA, NovilisParticula.Tipo.ICONO);

        // Las de los mini jefes.
        miniJefe(AtalayaParticulas.MJ_JADE, com.atalaya.client.MiniJefeParticula.Tipo.JADE);
        miniJefe(AtalayaParticulas.MJ_OBSIDIANA, com.atalaya.client.MiniJefeParticula.Tipo.OBSIDIANA);
        miniJefe(AtalayaParticulas.MJ_POLVO, com.atalaya.client.MiniJefeParticula.Tipo.POLVO);
        miniJefe(AtalayaParticulas.MJ_PLUMA, com.atalaya.client.MiniJefeParticula.Tipo.PLUMA);
        miniJefe(AtalayaParticulas.MJ_FRAGMENTO, com.atalaya.client.MiniJefeParticula.Tipo.FRAGMENTO);
        miniJefe(AtalayaParticulas.MJ_MARCA, com.atalaya.client.MiniJefeParticula.Tipo.MARCA);
        miniJefe(AtalayaParticulas.MJ_ONDA, com.atalaya.client.MiniJefeParticula.Tipo.ONDA);
        miniJefe(AtalayaParticulas.MJ_VIENTO, com.atalaya.client.MiniJefeParticula.Tipo.VIENTO);
        miniJefe(AtalayaParticulas.MJ_RUNA, com.atalaya.client.MiniJefeParticula.Tipo.RUNA);
        miniJefe(AtalayaParticulas.MJ_GOTA, com.atalaya.client.MiniJefeParticula.Tipo.GOTA);
        miniJefe(AtalayaParticulas.MJ_ESPUMA, com.atalaya.client.MiniJefeParticula.Tipo.ESPUMA);
        miniJefe(AtalayaParticulas.MJ_BURBUJA, com.atalaya.client.MiniJefeParticula.Tipo.BURBUJA);
        miniJefe(AtalayaParticulas.MJ_BRASA, com.atalaya.client.MiniJefeParticula.Tipo.BRASA);
        miniJefe(AtalayaParticulas.MJ_LLAMA, com.atalaya.client.MiniJefeParticula.Tipo.LLAMA);
        miniJefe(AtalayaParticulas.MJ_PLUMA_FUEGO, com.atalaya.client.MiniJefeParticula.Tipo.PLUMA_FUEGO);
        miniJefe(AtalayaParticulas.MJ_CENIZA, com.atalaya.client.MiniJefeParticula.Tipo.CENIZA);
        miniJefe(AtalayaParticulas.MJ_DESTELLO, com.atalaya.client.MiniJefeParticula.Tipo.DESTELLO);
        miniJefe(AtalayaParticulas.MJ_GRIETA, com.atalaya.client.MiniJefeParticula.Tipo.GRIETA);

        // La presencia de Nerea: temblor, retumbo y miedo. El miedo va con los
        // velos de camara (calabaza, nieve polvo...): un velo bajo el resto del
        // HUD. NO cuelga de la hotbar como la vineta del calor: en espectador
        // la hotbar no se dibuja, y con ella desaparecia todo lo enganchado.
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.AeralisEfectosCliente::tick);
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.RajangEfectosCliente::tick);
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.NereaEfectosCliente::tick);
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.NovilisEfectosCliente::tick);
        // El cielo del jefe con el que se pelea (CieloJefesMixin lo mezcla en lo que ve la camara).
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.CieloJefes::tick);
        // La Ofrenda al Sol: la secuencia de teclas de quien Novilis tiene en las manos.
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.OfrendaCliente::tick);
        // El Duelo de Canto de Nerea: las notas de quien ha elegido.
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.DueloCantoCliente::tick);
        // La musica de cada jefe mientras pelea cerca (y la de vanilla calla: MusicaJefesMixin).
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.MusicaJefes::tick);
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.MISC_OVERLAYS,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "miedo"),
                oculto(new com.atalaya.client.MiedoHud()));
        // Su barra de jefe, propia: la ola, el marco de prismarina, el corazon de
        // la fase (la calavera mientras mira) y el agua del color de la
        // maldicion. Va con la barra de jefe de vanilla,
        // que se dibuja en cualquier modo de juego (la hotbar no en espectador).
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.BOSS_BAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_nerea"),
                oculto(new com.atalaya.client.NereaBarraHud()));
        // La de Aeralis, despues: si las dos estan a la vista, va debajo.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_nerea"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_aeralis"),
                oculto(new com.atalaya.client.AeralisBarraHud()));
        // Y la de Rajang, debajo de las dos.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_aeralis"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_rajang"),
                oculto(new com.atalaya.client.RajangBarraHud()));
        // Glifos del Templo: los tres glifos buenos, solo para el Vidente.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_rajang"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "glifos_vidente"),
                oculto(new com.atalaya.client.GlifosVidenteHud()));
        // Y la de Novilis, debajo de las tres.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_rajang"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_novilis"),
                oculto(new com.atalaya.client.NovilisBarraHud()));
        // Y las de los mini jefes, mas bajas, debajo de las de los jefes.
        HudElementRegistry.attachElementAfter(
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_novilis"),
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "barra_minijefes"),
                oculto(new com.atalaya.client.MiniJefeBarraHud()));
        // Los minijuegos de Aeralis: el ojo de los Ocelos y la cuenta de la Chispa.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "aeralis_minijuegos"),
                oculto(new com.atalaya.client.AeralisMinijuegosHud()));
        // Los minijuegos de Novilis: el estandarte del Caballero Manda, la cuenta de
        // Piedra, Papel o Tijera y el termometro de Frio o Caliente.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "novilis_minijuegos"),
                oculto(new com.atalaya.client.NovilisMinijuegosHud()));
        // La pantalla de la Ofrenda al Sol (la del atrapado), por encima de la hotbar.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "ofrenda"),
                oculto(new com.atalaya.client.OfrendaHud()));
        // El catalejo del Canon del Naufragio: en lugar de la cruz mientras se va subido.
        HudElementRegistry.replaceElement(VanillaHudElements.CROSSHAIR, vanilla -> (g, tiempo) -> {
            if (com.atalaya.client.CanonMira.activo()) {
                com.atalaya.client.CanonMiraHud.dibujar(g, tiempo);
            } else {
                com.atalaya.client.CanonMiraHud.bajado();
                vanilla.extractRenderState(g, tiempo);
            }
        });
        // Subido al canon solo se ve el catalejo (Juan: "no deberia aparecer el inventario, ese HUD"): fuera la
        // barra de objetos, los corazones, la comida, la armadura, la experiencia y los efectos.
        for (Identifier hud : new Identifier[]{VanillaHudElements.HOTBAR, VanillaHudElements.ARMOR_BAR,
                VanillaHudElements.HEALTH_BAR, VanillaHudElements.FOOD_BAR, VanillaHudElements.AIR_BAR,
                VanillaHudElements.MOUNT_HEALTH, VanillaHudElements.INFO_BAR, VanillaHudElements.EXPERIENCE_LEVEL,
                VanillaHudElements.HELD_ITEM_TOOLTIP, VanillaHudElements.MOB_EFFECTS}) {
            HudElementRegistry.replaceElement(hud, vanilla -> (g, tiempo) -> {
                net.minecraft.client.Minecraft mc = net.minecraft.client.Minecraft.getInstance();
                if (mc.player == null || !(mc.player.getVehicle() instanceof com.atalaya.entity.CanonNaufragioEntity)) {
                    vanilla.extractRenderState(g, tiempo);
                }
            });
        }
        // La Bala de canon en brazos, vista desde fuera (los brazos: BalaBrazosMixin).
        net.fabricmc.fabric.api.client.rendering.v1.LivingEntityRenderLayerRegistrationCallback.EVENT.register(
                (tipo, renderer, ayudante, contexto) -> {
                    if (renderer instanceof net.minecraft.client.renderer.entity.player.AvatarRenderer<?> avatar) {
                        ayudante.register(new com.atalaya.client.BalaEnBrazosLayer(avatar));
                        // El aura de la habilidad de la armadura mientras esta activa.
                        ayudante.register(new com.atalaya.client.HabilidadAuraLayer(avatar));
                    }
                });
        // La pantalla del Duelo de Canto de Nerea (la del elegido), a la izquierda.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "duelo_canto"),
                oculto(new com.atalaya.client.DueloCantoHud()));
        // El icono de la habilidad de la armadura, a la derecha de la hotbar.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "habilidad"),
                oculto(new com.atalaya.client.HabilidadHud()));
        // La quemadura de Novilis, a la izquierda de los corazones.
        HudElementRegistry.attachElementAfter(
                VanillaHudElements.HOTBAR,
                Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "quemadura"),
                oculto(new com.atalaya.client.QuemaduraHud()));

        // Solo en el entorno de pruebas (con run/atalaya_fotos.flag).
        com.atalaya.client.FotosPrueba.registrar();

        Atalaya.LOGGER.info("Atalaya (cliente) iniciado.");

        // La presentacion de los jefes al despertar: la camara de cine (en sus
        // mixins), las bandas y el cartel por encima de todo, y mientras la camara
        // esta fuera, el resto del HUD escondido.
        net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents.START_CLIENT_TICK.register(
                com.atalaya.client.PresentacionJefe::tick);
        // En combate con un jefe, los corazones del jugador son los suyos (CorazonesJefe).
        net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents.START_CLIENT_TICK.register(
                com.atalaya.client.CorazonesJefe::tick);
        HudElementRegistry.addLast(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "presentacion"),
                new com.atalaya.client.PresentacionHud());
        // El Momento Maldicion (/atalaya momento_maldicion): por debajo del HUD, que no se esconde, para que se pueda
        // seguir jugando mientras sale (Juan, 16-10-2026). Lo manda el servidor (el unico paquete que va hacia el
        // cliente); al salir del mundo se olvida.
        HudElementRegistry.addFirst(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "momento_maldicion"),
                new com.atalaya.client.MomentoMaldicionHud());
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.MomentoMaldicionCliente::tick);
        // Y el cielo que se rompe (las grietas de luz en el cielo de verdad).
        com.atalaya.client.CieloRoto.registrar();
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking.registerGlobalReceiver(
                com.atalaya.net.AtalayaRed.Momento.TIPO,
                (carga, contexto) -> com.atalaya.client.MomentoMaldicionCliente.recibir(carga));
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents.DISCONNECT.register(
                (manejador, cliente) -> com.atalaya.client.MomentoMaldicionCliente.olvidar());
        // La Ruleta (/atalaya ruleta): la tragaperras de los cambios de dificultad, por encima de todo el HUD. La tira el
        // servidor; al salir del mundo se olvida.
        HudElementRegistry.addLast(Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "ruleta"),
                new com.atalaya.client.RuletaHud());
        ClientTickEvents.END_CLIENT_TICK.register(com.atalaya.client.RuletaCliente::tick);
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking.registerGlobalReceiver(
                com.atalaya.net.AtalayaRed.Ruleta.TIPO,
                (carga, contexto) -> com.atalaya.client.RuletaCliente.recibir(carga));
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents.DISCONNECT.register(
                (manejador, cliente) -> com.atalaya.client.RuletaCliente.olvidar());
        // Los menus de los cambios de dificultad y de las dimensiones (/atalaya menu cambios | dimensiones): pantallas
        // propias que abre y pone al dia el servidor.
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking.registerGlobalReceiver(
                com.atalaya.net.AtalayaRed.MenuCambios.TIPO,
                (carga, contexto) -> com.atalaya.client.MenusCliente.recibirCambios(carga));
        net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking.registerGlobalReceiver(
                com.atalaya.net.AtalayaRed.MenuDimensiones.TIPO,
                (carga, contexto) -> com.atalaya.client.MenusCliente.recibirDimensiones(carga));
        java.util.List<Identifier> escondidos = new java.util.ArrayList<>(java.util.List.of(
                VanillaHudElements.CROSSHAIR, VanillaHudElements.HOTBAR, VanillaHudElements.ARMOR_BAR,
                VanillaHudElements.HEALTH_BAR, VanillaHudElements.FOOD_BAR, VanillaHudElements.AIR_BAR,
                VanillaHudElements.MOUNT_HEALTH, VanillaHudElements.INFO_BAR, VanillaHudElements.EXPERIENCE_LEVEL,
                VanillaHudElements.HELD_ITEM_TOOLTIP, VanillaHudElements.MOB_EFFECTS, VanillaHudElements.BOSS_BAR,
                VanillaHudElements.SCOREBOARD, VanillaHudElements.OVERLAY_MESSAGE, VanillaHudElements.CHAT));
        for (Identifier id : escondidos) {
            boolean chat = id.equals(VanillaHudElements.CHAT);
            HudElementRegistry.replaceElement(id, original -> (g, delta) -> {
                if (!com.atalaya.client.PresentacionJefe.ocultaHud() && !(chat && com.atalaya.client.FotosPrueba.ocultaChat())) {
                    original.extractRenderState(g, delta);
                }
            });
        }
    }

    /** Un elemento del HUD propio que se esconde mientras la camara de la presentacion de un jefe esta fuera. */
    private static net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement oculto(
            net.fabricmc.fabric.api.client.rendering.v1.hud.HudElement e) {
        return (g, delta) -> {
            if (!com.atalaya.client.PresentacionJefe.ocultaHud()) {
                e.extractRenderState(g, delta);
            }
        };
    }

    private static void nerea(SimpleParticleType tipo, NereaParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new NereaParticula.Fabrica(sprites, comportamiento));
    }

    private static void miniJefe(SimpleParticleType tipo, com.atalaya.client.MiniJefeParticula.Tipo comportamiento) {
        ParticleProviderRegistry.getInstance().register(tipo,
                sprites -> new com.atalaya.client.MiniJefeParticula.Fabrica(sprites, comportamiento));
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
