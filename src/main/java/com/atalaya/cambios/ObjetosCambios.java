package com.atalaya.cambios;

import com.atalaya.Atalaya;
import com.atalaya.item.AtalayaItems;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.fabricmc.fabric.api.event.player.UseBlockCallback;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.Consumables;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.ItemEnchantments;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

import java.util.function.Consumer;

/**
 * Los objetos de los cambios de dificultad: la pildora de la plaga y las ayudas (que solo se pueden fabricar con su
 * cambio encendido: sus recetas se llaman cambio_&lt;id del cambio&gt; y las filtra {@link #permiteReceta}).
 *
 * <pre>
 *   Pildora de la Plaga   media hora mas de plaga (LA PLAGA, MORDISCO PUTRIDO); se fabrica siempre, de dos en dos
 *   Bolsa del Vacio       abre tu cofre de ender desde cualquier sitio (BOLSA DEL VACIO)
 *   Yunque Dorado         repara de golpe toda la armadura que llevas; cuatro usos (YUNQUE DORADO)
 *   Fruto del Recuerdo    la proxima vez que mueras conservas el inventario (FRUTO DEL RECUERDO)
 *   Raiz de Agua          quita la fatiga minera (RAIZ DE AGUA)
 * </pre>
 *
 * Y la PIEDRA SABIA, que no es un objeto: con el cambio encendido, usar la piedra de afilar con un objeto encantado en
 * la mano y un libro en la otra pasa los encantamientos al libro, a cambio de niveles.
 */
public final class ObjetosCambios {

    public static Item PILDORA_PLAGA;
    public static Item BOLSA_VACIO;
    public static Item YUNQUE_DORADO;
    public static Item FRUTO_RECUERDO;
    public static Item RAIZ_AGUA;
    public static Item PILDORA_TAMANO;

    private ObjetosCambios() {
    }

    public static void registrar() {
        PILDORA_PLAGA = AtalayaItems.registrar("pildora_plaga", props -> new Pildora(props.stacksTo(16).rarity(Rarity.UNCOMMON)
                .component(DataComponents.CONSUMABLE, Consumables.DEFAULT_FOOD)));
        BOLSA_VACIO = AtalayaItems.registrar("bolsa_vacio", props -> new Bolsa(props.stacksTo(1).rarity(Rarity.RARE)));
        YUNQUE_DORADO = AtalayaItems.registrar("yunque_dorado", props -> new Yunque(props.durability(4).rarity(Rarity.RARE)));
        FRUTO_RECUERDO = AtalayaItems.registrar("fruto_recuerdo", props -> new Fruto(props.stacksTo(4).rarity(Rarity.EPIC)
                .component(DataComponents.CONSUMABLE, Consumables.DEFAULT_FOOD)));
        RAIZ_AGUA = AtalayaItems.registrar("raiz_agua", props -> new Raiz(props.stacksTo(16)
                .component(DataComponents.CONSUMABLE, Consumables.DEFAULT_FOOD)));
        PILDORA_TAMANO = AtalayaItems.registrar("pildora_tamano", props -> new PildoraTamano(props.stacksTo(16).rarity(Rarity.UNCOMMON)
                .component(DataComponents.CONSUMABLE, Consumables.DEFAULT_FOOD)));

        // Fruto del Recuerdo: lo que llevaba el muerto pasa al que reaparece.
        ServerPlayerEvents.COPY_FROM.register((viejo, nuevo, vivo) -> {
            if (!vivo && viejo.entityTags().contains(RECUERDO)) {
                nuevo.getInventory().replaceWith(viejo.getInventory());
                nuevo.removeTag(RECUERDO);
                nuevo.sendSystemMessage(Component.literal("El Fruto del Recuerdo te ha guardado lo que llevabas.")
                        .withStyle(st -> st.withColor(0xD8A6FF)));
            }
        });

        // La Piedra Sabia: la piedra de afilar con un objeto encantado en la mano y un libro en la otra.
        UseBlockCallback.EVENT.register((jugador, mundo, mano, golpe) -> {
            if (mano != InteractionHand.MAIN_HAND || !CambiosDificultad.activo(Cambio.PIEDRA_SABIA)
                    || !mundo.getBlockState(golpe.getBlockPos()).is(Blocks.GRINDSTONE)) {
                return InteractionResult.PASS;
            }
            ItemStack objeto = jugador.getMainHandItem();
            ItemStack libro = jugador.getOffhandItem();
            if (!libro.is(Items.BOOK) || !objeto.isEnchanted()) {
                return InteractionResult.PASS;
            }
            if (mundo.isClientSide()) {
                return InteractionResult.SUCCESS;
            }
            return piedraSabia((ServerPlayer) jugador, objeto, libro);
        });
    }

    /** Si una receta del mod se puede usar: las de las ayudas (cambio_&lt;id&gt;), solo con su cambio encendido. */
    public static boolean permiteReceta(Identifier id) {
        if (!Atalaya.MOD_ID.equals(id.getNamespace()) || !id.getPath().startsWith("cambio_")) {
            return true;
        }
        Cambio c = Cambio.porId(id.getPath().substring("cambio_".length()));
        return c == null || CambiosDificultad.activo(c);
    }

    /** La marca del que ha comido el Fruto del Recuerdo (hasta que muera). */
    public static final String RECUERDO = "atalaya_fruto_recuerdo";

    // ------------------------------------------------------------------
    //  Los objetos
    // ------------------------------------------------------------------

    private static final class Pildora extends Item {
        Pildora(Properties p) {
            super(p);
        }

        @Override
        public ItemStack finishUsingItem(ItemStack stack, Level nivel, LivingEntity quien) {
            if (!nivel.isClientSide() && quien instanceof ServerPlayer p) {
                if (Plaga.pildora(p)) {
                    p.sendOverlayMessage(Component.literal("La plaga se aletarga: media hora más.").withStyle(st -> st.withColor(0x7ED35A)));
                } else {
                    p.sendOverlayMessage(Component.literal("No llevas la plaga: la píldora no te hace nada.").withStyle(ChatFormatting.GRAY));
                }
            }
            return super.finishUsingItem(stack, nivel, quien);
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar, Consumer<Component> linea,
                                    TooltipFlag flag) {
            linea.accept(Component.literal("Media hora más de plaga (hasta cuatro horas).").withStyle(ChatFormatting.GRAY));
        }
    }

    private static final class Bolsa extends Item {
        Bolsa(Properties p) {
            super(p);
        }

        @Override
        public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
            if (!nivel.isClientSide()) {
                jugador.openMenu(new SimpleMenuProvider((id, inv, quien) -> ChestMenu.threeRows(id, inv, quien.getEnderChestInventory()),
                        Component.literal("Bolsa del Vacío")));
                nivel.playSound(null, jugador.blockPosition(), SoundEvents.ENDER_CHEST_OPEN, SoundSource.PLAYERS, 0.6F, 1.2F);
            }
            return InteractionResult.SUCCESS;
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar, Consumer<Component> linea,
                                    TooltipFlag flag) {
            linea.accept(Component.literal("Abre tu cofre de ender desde cualquier sitio.").withStyle(ChatFormatting.GRAY));
        }
    }

    private static final class Yunque extends Item {
        Yunque(Properties p) {
            super(p);
        }

        @Override
        public InteractionResult use(Level nivel, Player jugador, InteractionHand mano) {
            ItemStack yunque = jugador.getItemInHand(mano);
            boolean algo = false;
            for (EquipmentSlot s : new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET}) {
                ItemStack pieza = jugador.getItemBySlot(s);
                if (pieza.isDamaged()) {
                    algo = true;
                    if (!nivel.isClientSide()) {
                        pieza.setDamageValue(0);
                    }
                }
            }
            if (!algo) {
                return InteractionResult.PASS;
            }
            if (nivel instanceof ServerLevel servidor) {
                servidor.playSound(null, jugador.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 0.7F, 1.3F);
                servidor.sendParticles(ParticleTypes.WAX_ON, jugador.getX(), jugador.getY() + 1.0, jugador.getZ(), 20, 0.4, 0.6, 0.4, 0.1);
                yunque.hurtAndBreak(1, jugador, mano == InteractionHand.MAIN_HAND ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);
            }
            return InteractionResult.SUCCESS;
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar, Consumer<Component> linea,
                                    TooltipFlag flag) {
            linea.accept(Component.literal("Repara de golpe toda la armadura que llevas puesta.").withStyle(ChatFormatting.GRAY));
        }
    }

    private static final class Fruto extends Item {
        Fruto(Properties p) {
            super(p);
        }

        @Override
        public ItemStack finishUsingItem(ItemStack stack, Level nivel, LivingEntity quien) {
            if (!nivel.isClientSide() && quien instanceof ServerPlayer p) {
                p.addTag(RECUERDO);
                p.sendOverlayMessage(Component.literal("Si mueres, conservarás lo que llevas.").withStyle(st -> st.withColor(0xD8A6FF)));
            }
            return super.finishUsingItem(stack, nivel, quien);
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar, Consumer<Component> linea,
                                    TooltipFlag flag) {
            linea.accept(Component.literal("La próxima vez que mueras, conservas el inventario.").withStyle(ChatFormatting.GRAY));
        }
    }

    private static final class Raiz extends Item {
        Raiz(Properties p) {
            super(p);
        }

        @Override
        public ItemStack finishUsingItem(ItemStack stack, Level nivel, LivingEntity quien) {
            if (!nivel.isClientSide()) {
                quien.removeEffect(MobEffects.MINING_FATIGUE);
            }
            return super.finishUsingItem(stack, nivel, quien);
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar, Consumer<Component> linea,
                                    TooltipFlag flag) {
            linea.accept(Component.literal("Quita la fatiga minera.").withStyle(ChatFormatting.GRAY));
        }
    }

    /** La Pildora del Tamano (el momento TODOS DIMINUTOS): te devuelve a tu altura. */
    private static final class PildoraTamano extends Item {
        PildoraTamano(Properties p) {
            super(p);
        }

        @Override
        public ItemStack finishUsingItem(ItemStack stack, Level nivel, LivingEntity quien) {
            if (!nivel.isClientSide() && quien instanceof ServerPlayer p) {
                if (com.atalaya.momento.Momentos.pildoraTamano(p)) {
                    p.sendOverlayMessage(Component.literal("Vuelves a tu altura.").withStyle(st -> st.withColor(0x8AE07A)));
                } else {
                    p.sendOverlayMessage(Component.literal("Ya estás a tu altura: la píldora no te hace nada.").withStyle(ChatFormatting.GRAY));
                }
            }
            return super.finishUsingItem(stack, nivel, quien);
        }

        @Override
        public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar, Consumer<Component> linea,
                                    TooltipFlag flag) {
            linea.accept(Component.literal("Te devuelve a tu altura si estás diminuto.").withStyle(ChatFormatting.GRAY));
        }
    }

    /** La Piedra Sabia: los encantamientos del objeto pasan al libro (3 niveles por cada nivel de encantamiento). */
    private static InteractionResult piedraSabia(ServerPlayer p, ItemStack objeto, ItemStack libro) {
        ItemEnchantments encantos = objeto.getOrDefault(DataComponents.ENCHANTMENTS, ItemEnchantments.EMPTY);
        int coste = 0;
        for (var e : encantos.entrySet()) {
            coste += 3 * e.getIntValue();
        }
        if (coste == 0) {
            return InteractionResult.PASS;
        }
        if (!p.isCreative() && p.experienceLevel < coste) {
            p.sendOverlayMessage(Component.literal("La piedra pide " + coste + " niveles.").withStyle(ChatFormatting.RED));
            return InteractionResult.FAIL;
        }
        ItemStack encantado = new ItemStack(Items.ENCHANTED_BOOK);
        encantado.set(DataComponents.STORED_ENCHANTMENTS, encantos);
        EnchantmentHelper.setEnchantments(objeto, ItemEnchantments.EMPTY);
        libro.shrink(1);
        if (!p.getInventory().add(encantado)) {
            p.drop(encantado, false);
        }
        if (!p.isCreative()) {
            p.giveExperienceLevels(-coste);
        }
        ServerLevel nivel = p.level();
        nivel.playSound(null, p.blockPosition(), SoundEvents.GRINDSTONE_USE, SoundSource.BLOCKS, 1.0F, 0.8F);
        nivel.playSound(null, p.blockPosition(), SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.BLOCKS, 0.8F, 1.0F);
        return InteractionResult.SUCCESS;
    }
}
