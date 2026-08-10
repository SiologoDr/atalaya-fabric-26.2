package com.atalaya;

import com.atalaya.aturdimiento.Aturdimiento;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.aturdimiento.AturdimientoManager;
import com.atalaya.command.AtalayaCommand;
import com.atalaya.config.LibroRecetas;
import com.atalaya.effect.AturdimientoEffect;
import com.atalaya.net.AtalayaRed;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import com.atalaya.lluvia.LluviaManager;
import com.atalaya.effect.CorrosionEffect;
import com.atalaya.effect.EmpapadoEffect;
import com.atalaya.effect.HipotermiaEffect;
import com.atalaya.effect.InsolacionEffect;
import com.atalaya.effect.RadiacionEffect;
import com.atalaya.entity.AtalayaEntities;
import com.atalaya.frio.Frio;
import com.atalaya.frio.FrioManager;
import com.atalaya.hidratacion.Hidratacion;
import com.atalaya.hidratacion.HidratacionManager;
import com.atalaya.item.AtalayaComponents;
import com.atalaya.item.AtalayaItems;
import com.atalaya.item.HazmatArmor;
import com.atalaya.loot.AtalayaLoot;
import com.atalaya.radiation.GeodeIndex;
import com.atalaya.radiation.RadiationManager;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerChunkEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Items;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Punto de entrada comun del mod (servidor y cliente).
 */
public class Atalaya implements ModInitializer {

    public static final String MOD_ID = "atalaya";
    public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

    /**
     * En 26.2 CreativeModeTabs ya no expone las pestanas como campos publicos,
     * asi que la clave se construye a mano.
     */
    private static final ResourceKey<CreativeModeTab> PESTANA_COMBATE =
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("combat"));

    private static final ResourceKey<CreativeModeTab> PESTANA_INGREDIENTES =
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("ingredients"));

    private static final ResourceKey<CreativeModeTab> PESTANA_HUEVOS =
            ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("spawn_eggs"));


    @Override
    public void onInitialize() {
        // Los componentes van primero: los items los usan al construirse.
        AtalayaComponents.registrar();
        HazmatArmor.registrar();
        AtalayaParticulas.registrar();
        // Las entidades van ANTES que los items: el huevo generador necesita
        // que su tipo de entidad exista cuando se construye.
        AtalayaEntities.registrar();
        AtalayaItems.registrar();
        RadiacionEffect.registrar();
        InsolacionEffect.registrar();
        CorrosionEffect.registrar();
        EmpapadoEffect.registrar();
        HipotermiaEffect.registrar();
        AturdimientoEffect.registrar();
        AtalayaLoot.registrar();
        Hidratacion.registrar();
        Frio.registrar();
        Aturdimiento.registrar();
        AtalayaRed.registrarTipos();
        AtalayaRed.registrarServidor();

        // Indice de geodas: se mantiene al dia con la carga y descarga de chunks.
        // El tercer parametro de CHUNK_LOAD (recien generado o no) no nos importa:
        // hay que escanearlo igual en ambos casos.
        ServerChunkEvents.CHUNK_LOAD.register((nivel, chunk, recienGenerado) ->
                GeodeIndex.alCargarChunk(nivel, chunk));
        ServerChunkEvents.CHUNK_UNLOAD.register(GeodeIndex::alDescargarChunk);
        ServerLifecycleEvents.SERVER_STOPPED.register(servidor -> GeodeIndex.limpiar());

        // Al romper amatista en gemacion hay que sacarla del indice, o quedaria
        // "radiacion fantasma" en un sitio donde ya no hay nada. La colocacion
        // la cubre BlockItemMixin, porque Fabric no expone evento para eso.
        PlayerBlockBreakEvents.AFTER.register((nivel, jugador, pos, estado, bloqueEntidad) -> {
            if (nivel instanceof ServerLevel servidor && GeodeIndex.esFuenteDeRadiacion(estado)) {
                GeodeIndex.quitar(servidor, pos);
            }
        });

        // La radiacion y la hidratacion se aplican desde el tick del servidor.
        ServerTickEvents.END_SERVER_TICK.register(RadiationManager::tick);
        ServerTickEvents.END_SERVER_TICK.register(HidratacionManager::tick);
        // La insolacion va en su propio bucle: se revisa mucho mas seguido que
        // el gasto de agua, porque de ella dependen el dano y el alivio al
        // salir del desierto.
        ServerTickEvents.END_SERVER_TICK.register(HidratacionManager::tickInsolacion);

        // La lluvia corrosiva va en su propio bucle: su intervalo (1 s) ES el
        // ritmo al que muerde la armadura.
        // Un solo bucle para las dos mecanicas de lluvia: comparten condicion.
        ServerTickEvents.END_SERVER_TICK.register(LluviaManager::tick);

        // El frio lleva las dos cosas en un solo bucle: subir, bajar y repartir
        // los castigos. Puede porque su intervalo (1 s) es el ritmo de
        // calentarse, y el de enfriarse sale contando vueltas.
        ServerTickEvents.END_SERVER_TICK.register(FrioManager::tick);

        // El aturdimiento se descuenta en su propio bucle, mas rapido que los
        // demas (5 ticks) porque la cuenta atras tiene que ir fina.
        ServerTickEvents.END_SERVER_TICK.register(AturdimientoManager::tick);

        // Y se pone cuando la explosion de un fulminante hace dano de verdad.
        // Se engancha DESPUES del dano, no antes: asi cubrirse o llevar buena
        // armadura tambien libra de quedarse clavado.
        ServerLivingEntityEvents.AFTER_DAMAGE.register(
                (entidad, fuente, repartido, recibido, bloqueado) ->
                        AturdimientoManager.alRecibirDano(entidad, fuente, recibido));

        // Y lo que no puede hacer mientras dura: usar, pegar, colocar.
        AturdimientoManager.registrarBloqueos();

        // Al conectarse, el libro de recetas tiene que reflejar los interruptores
        // actuales: si el crafteo esta apagado, esas recetas no deben aparecer.
        ServerPlayConnectionEvents.JOIN.register((manejador, emisor, servidor) ->
                LibroRecetas.sincronizar(manejador.getPlayer()));

        // El traje aparece en la pestana de combate, justo detras de las botas de hierro.
        CreativeModeTabEvents.modifyOutputEvent(PESTANA_COMBATE).register(salida ->
                salida.insertAfter(Items.IRON_BOOTS, HazmatArmor.todas()));

        // Carbon activado y filtro van con los materiales, detras del carbon.
        CreativeModeTabEvents.modifyOutputEvent(PESTANA_INGREDIENTES).register(salida ->
                salida.insertAfter(Items.CHARCOAL, AtalayaItems.todos()));

        // El huevo del fulminante va con los demas huevos, detras del de creeper.
        // No cabe en Ingredientes: alli no lo buscaria nadie.
        CreativeModeTabEvents.modifyOutputEvent(PESTANA_HUEVOS).register(salida ->
                salida.insertAfter(Items.CREEPER_SPAWN_EGG, AtalayaItems.HUEVO_FULMINANTE));

        CommandRegistrationCallback.EVENT.register(
                (dispatcher, registryAccess, entorno) -> AtalayaCommand.registrar(dispatcher));

        LOGGER.info("Atalaya iniciado (Minecraft 26.2 / Fabric).");
    }
}
