package com.atalaya.item;

import com.atalaya.effect.CorrienteAbismalEffect;
import com.atalaya.effect.ParalisisEffect;
import com.atalaya.effect.PesoTierraEffect;
import com.atalaya.entity.AeralisEntity;
import com.atalaya.entity.NereaEntity;
import com.atalaya.entity.RajangEntity;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.SimpleParticleType;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.boss.wither.WitherBoss;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/**
 * La espada de un jefe: la de netherite mejorada (16 de dano, el doble) que al
 * golpear suelta su tajo (una media luna del color del tema). Con un 5 % de
 * suerte en cada golpe, ademas, lo de su jefe:
 *
 * <pre>
 *   mareas    la Corriente Abismal 3 s (te arrastra los pies) y agua que salpica
 *   jade      el Peso de la Tierra 2 s (no salta) y esquirlas de jade
 *   vendaval  una racha que lo echa atras y la Paralisis 1 s
 * </pre>
 *
 * Los efectos son para los bichos normales: a los jefes (los tres elementales,
 * el Wither y el dragon) no les hacen nada; el tajo si se ve.
 *
 * La hoja esta animada (armaduras_jefes.py): agua que corre, vetas que laten,
 * viento que sube.
 */
public class EspadaJefeItem extends Item {

    /** La suerte de que el golpe suelte lo del jefe. */
    public static final float PROBABILIDAD = 0.05F;

    private final ArmadurasJefes.Tema tema;

    public EspadaJefeItem(ArmadurasJefes.Tema tema, Properties props) {
        super(props);
        this.tema = tema;
    }

    @Override
    public void postHurtEnemy(ItemStack stack, LivingEntity blanco, LivingEntity atacante) {
        super.postHurtEnemy(stack, blanco, atacante);
        if (!(atacante.level() instanceof ServerLevel nivel)) {
            return;
        }
        Vec3 mira = atacante.getLookAngle();
        Vec3 tajo = atacante.getEyePosition().add(mira.scale(1.3)).add(0, -0.35, 0);
        Vec3 pecho = blanco.position().add(0, blanco.getBbHeight() * 0.55, 0);
        // El tajo, en cada golpe.
        particulas(nivel, switch (tema) {
            case MAREAS -> AtalayaParticulas.MAREAS_TAJO;
            case JADE -> AtalayaParticulas.JADE_TAJO;
            case VENDAVAL -> AtalayaParticulas.VENDAVAL_TAJO;
        }, tajo, 1, 0.0);
        // Y su clink limpio, en cada golpe.
        nivel.playSound(null, blanco.getX(), blanco.getY() + 1.0, blanco.getZ(), switch (tema) {
            case MAREAS -> AtalayaSonidos.ESPADA_MAREAS_GOLPE;
            case JADE -> AtalayaSonidos.ESPADA_JADE_GOLPE;
            case VENDAVAL -> AtalayaSonidos.ESPADA_VENDAVAL_GOLPE;
        }, SoundSource.PLAYERS, 0.8F, 0.95F + nivel.getRandom().nextFloat() * 0.1F);
        // Lo del jefe: de vez en cuando, y nunca contra un jefe.
        if (esJefe(blanco) || nivel.getRandom().nextFloat() >= PROBABILIDAD) {
            return;
        }
        switch (tema) {
            case MAREAS -> {
                blanco.addEffect(new MobEffectInstance(CorrienteAbismalEffect.CORRIENTE, 60, 0), atacante);
                particulas(nivel, AtalayaParticulas.NEREA_ESPUMA, pecho, 10, 0.12);
                particulas(nivel, AtalayaParticulas.NEREA_GOTA, pecho, 12, 0.3);
                sonido(nivel, blanco, AtalayaSonidos.NEREA_OLA, 1.7F);
            }
            case JADE -> {
                blanco.addEffect(new MobEffectInstance(PesoTierraEffect.PESO, 40, 0), atacante);
                particulas(nivel, AtalayaParticulas.RAJANG_JADE, pecho, 10, 0.25);
                particulas(nivel, AtalayaParticulas.RAJANG_ROCA, pecho, 6, 0.25);
                sonido(nivel, blanco, AtalayaSonidos.RAJANG_PICO, 1.6F);
            }
            case VENDAVAL -> {
                Vec3 fuera = new Vec3(mira.x, 0, mira.z);
                fuera = fuera.lengthSqr() < 1.0E-4 ? Vec3.ZERO : fuera.normalize();
                blanco.push(fuera.x * 0.8, 0.25, fuera.z * 0.8);
                blanco.hurtMarked = true;
                blanco.addEffect(new MobEffectInstance(ParalisisEffect.PARALISIS, 20, 0), atacante);
                particulas(nivel, AtalayaParticulas.AERALIS_RAYO, pecho, 2, 0.0);
                particulas(nivel, AtalayaParticulas.AERALIS_JIRON, pecho, 8, 0.2);
                sonido(nivel, blanco, AtalayaSonidos.AERALIS_ALETEO, 1.8F);
            }
        }
    }

    /** Los jefes: los tres elementales y los de vanilla. */
    private static boolean esJefe(LivingEntity v) {
        return v instanceof NereaEntity || v instanceof AeralisEntity || v instanceof RajangEntity
                || v instanceof WitherBoss || v instanceof EnderDragon;
    }

    private static void particulas(ServerLevel nivel, SimpleParticleType tipo, Vec3 p, int n, double vel) {
        nivel.sendParticles(tipo, p.x, p.y, p.z, n, n == 1 ? 0.0 : 0.3, n == 1 ? 0.0 : 0.35, n == 1 ? 0.0 : 0.3, vel);
    }

    private static void sonido(ServerLevel nivel, LivingEntity donde, net.minecraft.sounds.SoundEvent s, float tono) {
        nivel.playSound(null, donde.getX(), donde.getY() + 1.0, donde.getZ(), s, SoundSource.PLAYERS, 0.5F,
                tono + nivel.getRandom().nextFloat() * 0.15F);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext contexto, TooltipDisplay mostrar,
                                Consumer<Component> linea, TooltipFlag flag) {
        super.appendHoverText(stack, contexto, mostrar, linea, flag);
        linea.accept(Component.translatable("item.atalaya." + tema.id + "_sword.efecto").withStyle(ChatFormatting.GRAY));
    }
}
