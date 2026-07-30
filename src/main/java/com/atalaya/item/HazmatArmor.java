package com.atalaya.item;

import com.atalaya.Atalaya;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.equipment.ArmorMaterial;
import net.minecraft.world.item.equipment.ArmorMaterials;
import net.minecraft.world.item.equipment.ArmorType;
import net.minecraft.world.item.equipment.EquipmentAsset;
import net.minecraft.world.item.equipment.EquipmentAssets;
import net.minecraft.world.item.equipment.Equippable;

import java.util.EnumMap;
import java.util.Map;

/**
 * Traje anti-radiacion (Hazmat): las cuatro piezas de armadura.
 *
 * Aspecto: el aspecto del traje puesto lo define
 * assets/atalaya/equipment/hazmat.json (dos capas: humanoid y humanoid_leggings).
 * El icono de cada pieza sale de assets/atalaya/items/hazmat_*.json.
 *
 * Solo el casco lleva visor: el cliente dibuja hazmat_visor.png a pantalla
 * completa mientras esta puesto, igual que hace la calabaza tallada.
 */
public final class HazmatArmor {

    /** Enlaza con assets/atalaya/equipment/hazmat.json. */
    public static final ResourceKey<EquipmentAsset> ASSET =
            ResourceKey.create(EquipmentAssets.ROOT_ID, id("hazmat"));

    /** textures/misc/hazmat_visor.png */
    private static final Identifier VISOR = id("misc/hazmat_visor");

    public static final ArmorMaterial MATERIAL = materialDelTraje();

    // La descripcion ya no se guarda aqui: la genera HazmatArmorItem al
    // mostrarla, leyendo los componentes de cada pieza.

    public static Item CASCO;
    public static Item PECHERA;
    public static Item PANTALON;
    public static Item BOTAS;

    private HazmatArmor() {
    }

    private static Identifier id(String ruta) {
        return Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, ruta);
    }

    /**
     * Etiqueta VACIA a proposito: el traje no se repara en yunque.
     *
     * El cartucho se cambia con click derecho usando un filtro (ver
     * FiltroCarbonItem). El yunque queda descartado porque encarece cada
     * reparacion y a los 40 niveles se planta con "Demasiado caro", lo que
     * dejaria inservible un traje pensado para repararse de continuo.
     *
     * La etiqueta existe porque ArmorMaterial exige una; si algun dia se quiere
     * volver al yunque, basta con meter el filtro en el JSON.
     */
    public static final TagKey<Item> REPARA_HAZMAT = TagKey.create(
            Registries.ITEM, Identifier.fromNamespaceAndPath(Atalaya.MOD_ID, "repara_hazmat"));

    /**
     * Parte del hierro y sube la proteccion a 17 puntos.
     *
     * Se arranca del material vanilla en vez de escribir todos los valores a
     * mano: asi la dureza, la encantabilidad y el sonido siguen a Mojang si los
     * cambia, y solo queda explicito lo que de verdad decidimos nosotros.
     *
     * El reparto de los 17 puntos sube el torso y las piernas y deja casco y
     * botas como el hierro. Es donde un traje sellado lleva mas material, y de
     * paso el pantalon queda igual que el de diamante (6) y la pechera a medio
     * camino entre hierro (6) y diamante (8).
     *
     * OJO: estos puntos NO protegen de la radiacion. El dano de radiacion es de
     * tipo magico, que en vanilla esta en la etiqueta bypasses_armor, asi que
     * ignora la armadura entera. Contra la radiacion solo cuenta cuantas piezas
     * llevas puestas (ver REDUCCION por pieza en RadiacionEffect). Esta
     * proteccion es para los golpes normales.
     *
     * Tres cosas se sustituyen a proposito:
     *   - el ingrediente de reparacion (etiqueta vacia: no se repara en yunque)
     *   - la proteccion, repartida arriba
     *   - la durabilidad, que se iguala luego por pieza a {@link #DURABILIDAD};
     *     el valor que va aqui deja de usarse.
     */
    private static ArmorMaterial materialDelTraje() {
        ArmorMaterial hierro = ArmorMaterials.IRON;

        // Copia del reparto del hierro (2/6/5/2 y el valor de montura) y se
        // retocan solo las dos ranuras que suben. Copiar en vez de construir de
        // cero deja intactas las ranuras que no nos interesan, y si Mojang anade
        // alguna nueva la heredamos sola.
        Map<ArmorType, Integer> defensa = new EnumMap<>(hierro.defense());
        defensa.put(ArmorType.CHESTPLATE, 7);
        defensa.put(ArmorType.LEGGINGS, 6);

        return new ArmorMaterial(
                hierro.durability(),
                Map.copyOf(defensa),
                hierro.enchantmentValue(),
                hierro.equipSound(),
                hierro.toughness(),
                hierro.knockbackResistance(),
                REPARA_HAZMAT,
                ASSET
        );
    }

    public static void registrar() {
        CASCO = pieza("hazmat_helmet", ArmorType.HELMET, true);
        PECHERA = pieza("hazmat_chestplate", ArmorType.CHESTPLATE, false);
        PANTALON = pieza("hazmat_leggings", ArmorType.LEGGINGS, false);
        BOTAS = pieza("hazmat_boots", ArmorType.BOOTS, false);
    }

    private static Item pieza(String nombre, ArmorType tipo, boolean conVisor) {
        ResourceKey<Item> clave = ResourceKey.create(Registries.ITEM, id(nombre));

        Item.Properties props = new Item.Properties()
                .setId(clave)
                .humanoidArmor(MATERIAL, tipo)
                // humanoidArmor() reparte la durabilidad del material por ranura
                // (x11 casco, x16 pechera, x15 pantalon, x13 botas), de ahi los
                // 165/240/225/195 del hierro. Aqui la igualamos a proposito:
                // asi un filtro vale lo mismo en cualquier pieza y las cuentas
                // salen redondas. Va DESPUES para que gane sobre el material.
                .durability(DURABILIDAD);

        if (conVisor) {
            // humanoidArmor() ya deja puesto un componente equippable; lo
            // reemplazamos por uno igual pero con la textura del visor.
            props.component(DataComponents.EQUIPPABLE,
                    Equippable.builder(tipo.getSlot())
                            .setAsset(ASSET)
                            .setEquipSound(MATERIAL.equipSound())
                            .setCameraOverlay(VISOR)
                            .setDamageOnHurt(true)
                            .build());
        }

        return Registry.register(BuiltInRegistries.ITEM, clave, new HazmatArmorItem(props));
    }

    // ------------------------------------------------------------------
    //  Visor excelente (cristal pulido en la mesa de herreria)
    // ------------------------------------------------------------------

    /**
     * El casco mejorado no lleva textura de visor en su componente equippable,
     * asi que no oscurece la pantalla. Eso lo define la receta de herreria
     * (data/atalaya/recipe/visor_hazmat_helmet.json), no el codigo: la
     * herreria copia los componentes de la pieza base sobre el resultado, y ahi
     * es donde se sustituye el equippable por uno sin camera_overlay.
     *
     * La linea de la descripcion la pone HazmatArmorItem al dibujar el
     * tooltip, mirando este componente.
     */
    public static boolean tieneVisorExcelente(ItemStack casco) {
        return AtalayaComponents.VISOR_EXCELENTE != null
                && Boolean.TRUE.equals(casco.get(AtalayaComponents.VISOR_EXCELENTE));
    }

    // ------------------------------------------------------------------
    //  Mejora antiveneno (colmillo venenoso en la mesa de herreria)
    // ------------------------------------------------------------------

    /** Fraccion del dano del veneno que anula CADA pieza mejorada. */
    public static final float REDUCCION_VENENO = 0.25f;

    public static boolean esAntiveneno(ItemStack pieza) {
        return AtalayaComponents.ANTIVENENO != null
                && Boolean.TRUE.equals(pieza.get(AtalayaComponents.ANTIVENENO));
    }

    /**
     * Cuantas piezas con colmillo lleva puestas (0 a 4).
     *
     * Se acumulan: cada una quita un 25% del dano del veneno, asi que las
     * cuatro lo dejan en cero. Como el colmillo cae al 5% y solo si mata un
     * jugador, tener el traje entero mejorado es un objetivo de largo plazo.
     */
    public static int piezasAntiveneno(LivingEntity entidad) {
        int n = 0;
        for (EquipmentSlot slot : RANURAS_ARMADURA) {
            ItemStack pieza = entidad.getItemBySlot(slot);
            if (esPieza(pieza.getItem()) && esAntiveneno(pieza)) {
                n++;
            }
        }
        return n;
    }

    /** Factor por el que se multiplica el dano del veneno (0 = inmune). */
    public static float factorVeneno(LivingEntity entidad) {
        return Math.max(0f, 1f - REDUCCION_VENENO * piezasAntiveneno(entidad));
    }

    // ------------------------------------------------------------------
    //  Amortiguacion (pata ligera en la mesa de herreria)
    // ------------------------------------------------------------------

    /** Fraccion de la LENTITUD de la radiacion que anula CADA pieza montada. */
    public static final float REDUCCION_LENTITUD = 0.25f;

    public static boolean esAmortiguada(ItemStack pieza) {
        return AtalayaComponents.AMORTIGUACION != null
                && Boolean.TRUE.equals(pieza.get(AtalayaComponents.AMORTIGUACION));
    }

    /**
     * Cuantas piezas con pata ligera lleva puestas (0 a 4).
     *
     * Se acumulan igual que el colmillo: cada una recorta un cuarto de la
     * lentitud, asi que el traje entero te deja moverte a velocidad normal
     * dentro de la geoda. No quita el dano: sigues necesitando el traje sano.
     */
    public static int piezasAmortiguadas(LivingEntity entidad) {
        int n = 0;
        for (EquipmentSlot slot : RANURAS_ARMADURA) {
            ItemStack pieza = entidad.getItemBySlot(slot);
            if (esPieza(pieza.getItem()) && esAmortiguada(pieza)) {
                n++;
            }
        }
        return n;
    }

    /** Las cuatro piezas, en orden de cabeza a pies. */
    public static Item[] todas() {
        return new Item[]{CASCO, PECHERA, PANTALON, BOTAS};
    }

    /**
     * true si el item es una pieza del traje.
     *
     * Comparacion por referencia: los Item son singletons del registro, asi que
     * son cuatro comparaciones de puntero. Se usa desde el mixin del crafteo,
     * donde conviene no tocar el registro.
     */
    public static boolean esPieza(Item item) {
        return item == CASCO || item == PECHERA || item == PANTALON || item == BOTAS;
    }

    /**
     * Durabilidad de CADA pieza, igual para las cuatro.
     *
     * Queda entre el casco de hierro (165) y la pechera (240), y bien por debajo
     * del diamante (363 a 528): el traje clona casi la proteccion del hierro, no
     * tendria sentido que aguantase mas que el diamante.
     *
     * Y cuadra con el filtro: desde el umbral en que la pieza deja de proteger
     * lleva 200 puntos de dano encima, asi que DOS filtros de 100 la dejan
     * exactamente nueva sin desperdiciar nada.
     */
    public static final int DURABILIDAD = 250;

    /** Por debajo de esta fraccion de durabilidad, la pieza deja de proteger. */
    public static final float UMBRAL_PROTECCION = 0.20f;

    /**
     * Desde aqui el aviso pasa a ROJO: es el ultimo margen antes de que la
     * pieza deje de filtrar. La banda 21.5% -> 20% son 3 puntos de durabilidad,
     * o sea unos 6 segundos en el borde de la geoda y 1,5 pegado a la amatista.
     * Es corto a proposito: avisa de que va a pasar YA, no de que pasara.
     */
    public static final float UMBRAL_CRITICO = 0.215f;

    /** A partir de aqui el HUD empieza a avisar de que el filtro se agota. */
    public static final float UMBRAL_AVISO = 0.30f;

    /** Fraccion de durabilidad que le queda a una pieza (1.0 = intacta). */
    public static float durabilidadRestante(ItemStack pieza) {
        int max = pieza.getMaxDamage();
        if (max <= 0) {
            return 1f;
        }
        return (max - pieza.getDamageValue()) / (float) max;
    }

    /** true si la pieza es del traje y aun conserva su capacidad de filtrar. */
    public static boolean protege(ItemStack pieza) {
        return esPieza(pieza.getItem()) && durabilidadRestante(pieza) >= UMBRAL_PROTECCION;
    }

    /**
     * Cuantas piezas del traje protegen ahora mismo (0 a 4).
     *
     * Se cuenta por SLOT, no por inventario: llevar cuatro cascos en la mochila
     * no protege de nada. Y una pieza por debajo del umbral no cuenta aunque
     * siga puesta: es la "brecha" del traje.
     */
    public static int piezasQueProtegen(LivingEntity entidad) {
        int n = 0;
        for (EquipmentSlot slot : RANURAS_ARMADURA) {
            if (protege(entidad.getItemBySlot(slot))) {
                n++;
            }
        }
        return n;
    }

    /**
     * Gasta durabilidad del traje y devuelve cuantas piezas siguen protegiendo.
     *
     * Las dos cosas van en el MISMO recorrido de ranuras porque siempre se
     * necesitan juntas, y este metodo corre con cada golpe de radiacion: hasta
     * dos veces por segundo por jugador que este dentro de una geoda.
     *
     * El desgaste se aplica aunque el traje completo te haga inmune: se degrada
     * precisamente por absorber la radiacion, y sin eso los filtros no tendrian
     * sentido. Y se cuenta DESPUES de gastar, para que una pieza que caiga bajo
     * el umbral con este mismo golpe deje de proteger ya.
     */
    public static int desgastarYContarProtectoras(LivingEntity entidad, int desgaste) {
        int protegen = 0;
        for (EquipmentSlot slot : RANURAS_ARMADURA) {
            ItemStack pieza = entidad.getItemBySlot(slot);
            if (!esPieza(pieza.getItem())) {
                continue;
            }
            pieza.hurtAndBreak(desgaste, entidad, slot);
            if (protege(pieza)) {
                protegen++;
            }
        }
        return protegen;
    }

    private static final EquipmentSlot[] RANURAS_ARMADURA = {
            EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET
    };
}
