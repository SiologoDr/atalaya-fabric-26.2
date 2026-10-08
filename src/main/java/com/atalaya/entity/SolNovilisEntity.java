package com.atalaya.entity;

import com.atalaya.effect.QuemaduraEffect;
import com.atalaya.particula.AtalayaParticulas;
import com.atalaya.sonido.AtalayaSonidos;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import org.joml.Vector3fc;
import org.jspecify.annotations.Nullable;

/**
 * Un sol pequeno que Novilis lanza.
 *
 * <ul>
 *   <li>SOL (Sol x3): vuela en arco hasta su sello (que se ve desde que lo
 *       lanza) y revienta en fuego y lava. A quien este dentro del sello: el
 *       golpe, dos niveles de quemadura y fuego. Deja un charco de lava 5 s que
 *       prende a quien lo pisa.</li>
 *   <li>DIOS (Dios de la Guerra): cae en una de las tres zonas y la llena de
 *       explosiones en cadena (cinco en algo mas de un segundo). A quien tiene
 *       quemadura grave lo mata salvo totem.</li>
 *   <li>SUPERNOVA (el cuarto del Sol Abrasador, 08-10-2026): mas grande y mas
 *       lento; su sello mide 12 bloques. Revienta en grande (dos niveles de
 *       quemadura) y deja un charco de lava mas ancho.</li>
 * </ul>
 *
 * Como las olas de Nerea, la entidad se queda donde nacio: el arco sale de la
 * edad, de donde sale y de donde va (sincronizados), igual en los dos lados.
 */
public class SolNovilisEntity extends Entity {

    public static final int SOL = 0;
    public static final int DIOS = 1;
    public static final int SUPERNOVA = 2;
    /** El charco de lava del Sol y el de la Supernova (radio). */
    public static final float CHARCO_SOL = 2.8F;
    public static final float CHARCO_NOVA = 6.0F;
    /** Lo que sube el arco por encima de la recta. */
    private static final float ARCO = 7.0F;
    /** Lo que dura el charco de lava del Sol. */
    public static final int CHARCO = 100;
    /** Las explosiones en cadena del Dios: cada cuantos ticks y cuantas. */
    private static final int CADA_EXPLOSION = 6;
    private static final int EXPLOSIONES = 5;

    private static final EntityDataAccessor<Vector3fc> DATA_DESTINO =
            SynchedEntityData.defineId(SolNovilisEntity.class, EntityDataSerializers.VECTOR3);
    private static final EntityDataAccessor<Integer> DATA_VUELO =
            SynchedEntityData.defineId(SolNovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_TIPO =
            SynchedEntityData.defineId(SolNovilisEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> DATA_COLOR =
            SynchedEntityData.defineId(SolNovilisEntity.class, EntityDataSerializers.INT);

    private @Nullable NovilisEntity dueno;
    private float dano;

    public SolNovilisEntity(EntityType<? extends SolNovilisEntity> tipo, Level nivel) {
        super(tipo, nivel);
        this.noPhysics = true;
        setNoGravity(true);
    }

    public static SolNovilisEntity lanzar(ServerLevel nivel, NovilisEntity dueno, Vec3 desde, Vec3 destino, int vuelo, int tipo,
                                          float dano, int fase) {
        SolNovilisEntity s = new SolNovilisEntity(AtalayaEntities.SOL_NOVILIS, nivel);
        s.dueno = dueno;
        s.dano = dano;
        s.entityData.set(DATA_DESTINO, new Vector3f((float) (destino.x - desde.x), (float) (destino.y - desde.y),
                (float) (destino.z - desde.z)));
        s.entityData.set(DATA_VUELO, Math.max(1, vuelo));
        s.entityData.set(DATA_TIPO, tipo);
        s.entityData.set(DATA_COLOR, tipo == DIOS ? 4 : dueno.tieneFuria() ? 5 : fase);
        s.setPos(desde.x, desde.y, desde.z);
        nivel.addFreshEntity(s);
        return s;
    }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder datos) {
        datos.define(DATA_DESTINO, new Vector3f());
        datos.define(DATA_VUELO, 28);
        datos.define(DATA_TIPO, SOL);
        datos.define(DATA_COLOR, 1);
    }

    public int getVuelo() {
        return entityData.get(DATA_VUELO);
    }

    public int getTipo() {
        return entityData.get(DATA_TIPO);
    }

    public int getColor() {
        return entityData.get(DATA_COLOR);
    }

    /** Donde cae, relativo a donde nacio. */
    public Vec3 destinoRel() {
        Vector3fc v = entityData.get(DATA_DESTINO);
        return new Vec3(v.x(), v.y(), v.z());
    }

    /** Donde va el sol a la edad dada, relativo a donde nacio. */
    public Vec3 enVuelo(float edad) {
        float k = Math.min(1.0F, edad / getVuelo());
        Vec3 d = destinoRel();
        return new Vec3(d.x * k, d.y * k + ARCO * 4 * k * (1 - k), d.z * k);
    }

    public boolean aterrizado(float edad) {
        return edad >= getVuelo();
    }

    @Override
    public void tick() {
        super.tick();
        int vuelo = getVuelo();
        Vec3 dest = position().add(destinoRel());
        if (level().isClientSide()) {
            if (tickCount < vuelo) {
                Vec3 p = position().add(enVuelo(tickCount));
                level().addParticle(getTipo() == DIOS ? AtalayaParticulas.NOVILIS_CARMESI : AtalayaParticulas.NOVILIS_LLAMA,
                        p.x, p.y, p.z, 0, 0.02, 0);
            } else if (getTipo() != DIOS && tickCount < vuelo + CHARCO && tickCount % (getTipo() == SUPERNOVA ? 2 : 4) == 0) {
                double a = random.nextDouble() * Math.PI * 2;
                double r = random.nextDouble() * (getTipo() == SUPERNOVA ? CHARCO_NOVA : CHARCO_SOL) * 0.93;
                level().addParticle(AtalayaParticulas.NOVILIS_LLAMA, dest.x + Math.cos(a) * r, dest.y + 0.1,
                        dest.z + Math.sin(a) * r, 0, 0.05, 0);
            }
            return;
        }
        if (dueno == null || dueno.isRemoved()) {
            discard();
            return;
        }
        ServerLevel nivel = (ServerLevel) level();
        int dentro = tickCount - vuelo;
        if (getTipo() == SOL || getTipo() == SUPERNOVA) {
            boolean nova = getTipo() == SUPERNOVA;
            if (dentro == 0) {
                explotar(nivel, dest, nova ? NovilisEntity.RADIO_SUPERNOVA : NovilisEntity.RADIO_SOL);
                nivel.playSound(null, dest.x, dest.y, dest.z, AtalayaSonidos.NOVILIS_LAVA, SoundSource.HOSTILE, nova ? 4.0F : 2.5F, 1.0F);
            } else if (dentro > 0 && dentro < CHARCO && dentro % 10 == 0) {
                charco(nivel, dest, nova ? CHARCO_NOVA : CHARCO_SOL);
            }
            if (dentro >= CHARCO) {
                discard();
            }
        } else {
            if (dentro >= 0 && dentro % CADA_EXPLOSION == 0 && dentro / CADA_EXPLOSION < EXPLOSIONES) {
                double a = random.nextDouble() * Math.PI * 2;
                double r = dentro == 0 ? 0 : random.nextDouble() * (NovilisEntity.RADIO_ZONA - 2.0);
                Vec3 p = dest.add(Math.cos(a) * r, 0, Math.sin(a) * r);
                explotar(nivel, p, 3.4F);
            }
            if (dentro >= CADA_EXPLOSION * EXPLOSIONES + 4) {
                discard();
            }
        }
    }

    private void explotar(ServerLevel nivel, Vec3 p, float r) {
        boolean dios = getTipo() == DIOS;
        boolean nova = getTipo() == SUPERNOVA;
        nivel.playSound(null, p.x, p.y, p.z, dios ? AtalayaSonidos.NOVILIS_DIOS_EXPLOSION
                        : nova ? AtalayaSonidos.NOVILIS_SUPERNOVA : AtalayaSonidos.NOVILIS_SOL_EXPLOTA,
                SoundSource.HOSTILE, nova ? 9.0F : 5.0F, 0.9F + random.nextFloat() * 0.2F);
        if (nova) {
            nivel.sendParticles(AtalayaParticulas.NOVILIS_LLAMA, true, true, p.x, p.y + 2.0, p.z, 90, r * 0.35, 2.0, r * 0.35, 0.35);
        }
        nivel.sendParticles(dios ? AtalayaParticulas.NOVILIS_CARMESI : AtalayaParticulas.NOVILIS_LLAMA, true, true, p.x, p.y + 1.0,
                p.z, 50, r * 0.4, 1.0, r * 0.4, 0.25);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_CHISPA, true, true, p.x, p.y + 1.0, p.z, 30, r * 0.3, 0.8, r * 0.3, 0.5);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_HUMO, true, true, p.x, p.y + 1.5, p.z, 14, r * 0.3, 0.8, r * 0.3, 0.03);
        nivel.sendParticles(AtalayaParticulas.NOVILIS_ONDA, true, true, p.x, p.y + 0.12, p.z, 0, dios ? 1.4 : 1.8, r * 2.2, 0.0, 1.0);
        AABB caja = new AABB(p.x - r, p.y - 1.5, p.z - r, p.x + r, p.y + 4, p.z + r);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            double dx = v.getX() - p.x;
            double dz = v.getZ() - p.z;
            if (dx * dx + dz * dz > (r + v.getBbWidth() / 2) * (r + v.getBbWidth() / 2)) {
                continue;
            }
            if (dios && dueno.mataDios(v)) {
                v.hurtServer(nivel, NovilisDanos.fuente(nivel, NovilisDanos.MORTAL, this, dueno), NovilisEntity.MORTAL);
                continue;
            }
            if (dueno.quemar(nivel, v, dios ? NovilisDanos.DIOS : nova ? NovilisDanos.SUPERNOVA : NovilisDanos.SOL, dano,
                    dios ? 1 : 2, this)) {
                v.igniteForSeconds(3.0F);
                Vec3 fuera = new Vec3(dx, 0, dz).lengthSqr() < 1.0E-4 ? new Vec3(1, 0, 0) : new Vec3(dx, 0, dz).normalize();
                v.setDeltaMovement(fuera.x * 0.9, 0.6, fuera.z * 0.9);
                v.hurtMarked = true;
            }
        }
    }

    /** El charco de lava: prende a quien lo pisa. */
    private void charco(ServerLevel nivel, Vec3 p, float radio) {
        AABB caja = new AABB(p.x - radio, p.y - 0.5, p.z - radio, p.x + radio, p.y + 1.5, p.z + radio);
        for (LivingEntity v : nivel.getEntitiesOfClass(LivingEntity.class, caja, x -> dueno != null && dueno.esPresa(x))) {
            double dx = v.getX() - p.x;
            double dz = v.getZ() - p.z;
            if (dx * dx + dz * dz <= radio * radio && v.onGround()) {
                v.igniteForSeconds(3.0F);
                if (QuemaduraEffect.nivel(v) == 0) {
                    QuemaduraEffect.quemar(v, 1);
                }
            }
        }
    }

    @Override
    public boolean isPickable() {
        return false;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    public boolean shouldRenderAtSqrDistance(double distancia) {
        return distancia < 192 * 192;
    }

    @Override
    public boolean hurtServer(ServerLevel nivel, DamageSource fuente, float cantidad) {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(ValueInput entrada) {
    }

    @Override
    protected void addAdditionalSaveData(ValueOutput salida) {
    }
}
