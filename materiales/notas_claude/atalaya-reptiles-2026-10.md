---
name: atalaya-reptiles-2026-10
description: "Los 7 reptiles del DEDsafío con dibujo (carteles D2 y D4); 1.ª «un chiste», 2.ª «puede mejorar», 3.ª pieza a pieza; 4.ª (20-10) lo fino en láminas; 5.ª manos, 4 dientes, ojos de línea; 6.ª raptor con anatomía de referencia; 7.ª (20-10) pelo pegado a la piel, manos hacia dentro, raptor adulto; Dáctylo ELIMINADO"
metadata:
  node_type: memory
  type: project
  originSessionId: 8b154ffb-6f8b-471a-ab02-bedda2001893
  modified: 2026-10-20T01:52:14.886Z
---

El 19-10-2026 Juan pidió «hagamos los reptiles entonces» (la siguiente familia del catálogo, después de los phantoms).

**Con dibujo**, en los carteles del día 2 (tuit 2102850513389621451) y del día 4 (2103569518706483435): siete mobs y cinco cuerpos. El Dáctylo se descartó el 20-10, así que quedan seis.
- `reptisaurio_salvaje` y `reptisaurio_guerrero`: el mismo esqueleto, con parámetros por mob.
- `dromoraptor_rojo` y `dromoraptor_azul`: el mismo raptor en dos colores.
- `plumosaurio`.
- `dactylo_bebe`.
- `reptisaurio_cavador`: el cartel del D4 lo llama también «Reptisaurio Salvaje». El nombre es provisional, pendiente de que lo confirme Juan.

**Sin dibujo** (solo texto de fans), así que no se recrean: Dromoraptor Verde, Reptisaurio Arquero y con Lanza, Dáctylo Adulto, Fluviosaurus y Mastodino.

**1.ª vuelta, rechazada:** «no son nada parecidos, parecen un chiste al lado de los originales, sé que puedes hacerlo mejor».
- Eran cajas lisas con degradados limpios.
- Las medidas estaban a ojo y salían pequeños y flacos.
- Piezas inventadas: la cabeza negra del Dáctylo, los cuernos de diablo, una cresta en peine.

**2.ª vuelta** (enseñada en `scratchpad/reptiles_v5/reptiles.html`):
- **Medidas:** en los iconos a 4K, un píxel de textura son unos 4 píxeles del cartel. Todo se midió así.
  - Salen grandes: 2,3 bloques de alto, y el raptor 2,8 de largo.
  - Le pregunté a Juan si los quiere más pequeños.
- **Paleta:** sale del cartel con `scratchpad/paleta_rep.py`.
- **Silueta:** se compara con el contorno del original encima (`sup_rep.py`) y en grande junto a él (`cerca_rep.py`).
- **Texturas** (`pix`): de 4 o 5 tonos al píxel, con grano y dibujo: escamas, anillos, manchas o mechones.
- **Plumas de los raptores** (`gajos`): plumas en huso, azules, con el canto naranja por fuera en las de cada lado y el cañón en la del medio.
- **Crestas:** manojos de púas sueltas de varios tonos (`penacho`). La del Guerrero es una valla de llamas planas.

**3.ª vuelta** («ahora sí, pero puede mejorar incluso; tómate tu tiempo»), en `scratchpad/reptiles_v6/reptiles.html`:
- Cada pieza se repasó al lado del original muy ampliada, con `scratchpad/detalle_rep.py` (la cara, las manos, las plumas, las crestas).
- También se revisaron las vistas de frente, de lado y por detrás.
- No se añadieron piezas: solo fidelidad y acabado.
- Lo que más cambió:
  - en los reptisaurios, la cabeza por encima de los hombros, la ceja y los ojos de cada uno, y la cresta del Guerrero, una valla de llamas en punta;
  - en los raptores, la cabeza escalonada con el cubo sobre el hocico y las plumas más vivas;
  - en el Plumosaurio, el cuello en interrogación y el plumón de hebras;
  - en el Dáctylo, la cara de gafas con cejas de enfado y las alas más grandes;
  - en el Cavador, los bultos negros y los colmillos.

**4.ª vuelta** (20-10), con su lista larga de correcciones por mob, en `scratchpad/reptiles_v7/reptiles.html`:
- Su queja de fondo: «no son bloques». El musgo, las llamas, las garras, los dientes, los ojos, las cejas, los colmillos y la cosa amarilla tenían que ir dibujados. Ahora van en láminas recortadas o en una 2.ª capa (ver [[lo-fino-no-en-bloques]]).
- Pidió «su textura debería ser mejor» en los siete. Ahora `pix` lleva escamas con luz y sombra en cada una, placas en el vientre, bisel en los cantos, moteado en los raptores y hebras en el plumón.
- Salvaje:
  - los ojos estaban bizcos; ahora tienen la pupila centrada y la cara se pinta a 32 por bloque (`_con_cara(..., fino=True)`);
  - el hueso de los hombros es una L.
- Guerrero: las cabezas de vaca de los hombros se rehicieron con cráneo, hocico y cuernos curvos.
- Raptores:
  - cara nueva, con el cráneo largo y el ojo pequeño atrás;
  - la cola a la altura del cuerpo;
  - abanicos de aletas en punta («los nuestros parecen hojas»);
  - piernas y brazos de velociraptor;
  - crestas una detrás de otra («no son orejas»);
  - la cosa amarilla es una vela plana con las esquinas redondas.
- Plumosaurio («parece una llama»):
  - el cuello adelantado, con púas negras cortas detrás;
  - la cabeza seguida de una escalera invertida, una cola fina y la punta morada maciza;
  - el pelo cae en dos masas con un hueco entre ellas;
  - la cola más larga.
- Dáctylo («el peor»):
  - rehecho como un quetzalcoatlus de pie;
  - las alas son los brazos y llevan garras en la mano;
  - dos ojos en bloque y un pico de dos mandíbulas.
- Cavador: el pilar marrón, luego una extremidad fina y luego el cuerpo; ojos, cejas y colmillos sin bloques.
- Miden de 1,8 a 2,5 bloques de alto.
- Le pregunté otra vez por el tamaño y por el nombre del Cavador.

**5.ª vuelta** (20-10), en `scratchpad/reptiles_v8/reptiles.html`. Juan mandó capturas nuestras con su dibujo encima (y pintó la cara del Salvaje como la quería):
- Reptisaurios:
  - las manos son palma ancha y tres dedos, cada uno con su garra;
  - solo 4 dientes (`cuatro_dientes`), dos pequeños en el centro y dos largos en los extremos, finos;
  - los ojos almendrados con una línea negra vertical, a los costados y doblando la esquina (`lado_ojo`);
  - la nariz más junta y menos pelo arriba;
  - la piel nueva `pix(..., patron='piel')`: manchas suaves sin cuadrícula ni bisel, porque las escamas «parecían bloques».
- Guerrero: las llamas de la cabeza en láminas, no en bloques («recuérdalo»), y las calaveras de gris apagado (`GRIS_CALAVERA`).
- Raptores:
  - cuello grande detrás de la cabeza, sin hueco;
  - muslo grande, caña recta y pie hacia delante;
  - brazo en L;
  - aletas de púas largas y curvas con membrana (`puas`);
  - crestas curvas (`cresta_curva`).
- Plumosaurio:
  - cabeza y hocico de una pieza, más corta y alta, con orejas;
  - el cuello plateado por delante;
  - la escalera más grande, unida al cuello;
  - la punta morada doblada hacia abajo;
  - la cola más corta.
- Cavador:
  - 4 colmillos (`colmillos`), dos largos delante y uno corto a cada lado;
  - los pilares con veta de madera («parecían ladrillos»);
  - la cara como el cartel.
- Dáctylo («no se parece en nada; míralo anatómicamente»): rehecho como el icono.
  - Erguido en el aire, con la pelvis ancha y las patas rectas colgando.
  - La cabeza de gafas encima, sin cuello.
  - Las alas salen de los hombros, con el brazo por el canto de delante y la mano con garras en la muñeca.
  - La cola fina con el tridente.
  - Lo de quetzalcoatlus de la 4.ª vuelta no era lo que buscaba.

**6.ª vuelta** (20-10), en `scratchpad/reptiles_v9/reptiles.html`:
- Reptisaurios: Juan pintó otra vez la cara.
  - Ojos casi rectangulares, a los costados, con poco hueco y franja negra gruesa (`cara_ojos`).
  - La nariz justo debajo, en la piel, sin la encía roja.
  - Los colmillos más anchos, bajo cada ojo.
  - Las manos «volteadas hacia dentro»: los dedos en fila de delante atrás y las garras curvadas hacia el cuerpo.
  - Dijo que con eso «quedarían excelentes».
- Raptores: su dibujo más dos raptores de referencia de otros mods («mejora su anatomía»).
  - Cuerpo horizontal: pecho hondo y cadera.
  - Cola larga que adelgaza en 4 tramos.
  - Pierna en zigzag: muslo, espinilla atrás, caña oscura y pie delante.
  - Brazo en L con garras en gancho.
  - Las dos aletas de atrás echadas hacia la cola.
- Plumosaurio, «casi listo»:
  - le faltaban las aletas moradas como orejas a los lados de la cabeza (`aleta_oreja`);
  - el hocico, con rayas grises verticales arriba y la mandíbula oscura, sin boca negra.
- Cavador: colmillos «muy delgados y no conectados»; ahora son de 2 px y arrancan sobre el borde de la cara.
- **Dáctylo Bebé ELIMINADO**: «hay que eliminarlo, no lo vamos a hacer». Se quitó del generador; no volver a proponerlo.

**7.ª vuelta** (20-10), en `scratchpad/reptiles_v10/reptiles.html`:
- Reptisaurios:
  - el pelo «sujetado a la piel, no a la nada»: los manojos nacen dentro de la cabeza y del lomo y crecen pegados (inclina −18 en el lomo), sin la masa de musgo que salía hacia atrás;
  - ojos rectángulos de verdad, sin redondear;
  - colmillos enteros y la boca más abierta (30° y 34°), así que caben sobre lo rojo; antes parecían partidos o pintados en la mandíbula;
  - el hueso del hombro alineado con el brazo;
  - las manos planas, con la palma de cara al cuerpo (mandó el dibujo de una persona con los brazos caídos).
- Guerrero: no se veían los dos dientes del centro porque un diente de 1 px centrado entre dos píxeles no pinta ninguno. Ahora van centrados en un píxel.
- Raptores: «parece pequeño, no un adulto».
  - Cuerpo más grande, cola más larga, piernas más largas.
  - Piel `manchas_grandes`.
  - Cabeza de cráneo y hocico.
  - Garras gris oscuro (`GARRA_OSCURA`): 2 en la mano y 3 en el pie.
  - La aleta de los hombros neutral (recta, simétrica, sin curva) y las aletas con la membrana más limpia.
- Plumosaurio: las aletas-oreja abiertas 55° hacia fuera, y la boca solo una raya corta en la punta.

**Después de la 7.ª** (20-10): «en el Dromoraptor déjalo como estaba antes, y solo mejora su textura, haz eso y mételos al juego».
- **Raptor:** vuelve a la forma de la 6.ª vuelta, la del cuerpo, las piernas y la cabeza de una caja. Se quedan:
  - la piel `manchas_grandes`;
  - el ojo de tres píxeles bajo la ceja;
  - las aletas más limpias;
  - las garras gris oscuro (2 en la mano, 3 en el pie);
  - la aleta de los hombros recta.
  Lo «adulto» de la 7.ª no gustó.
- **En el juego:**
  - generador `al_juego` (modelo, huevo, nombres, retrato y partículas);
  - `bestiario_sonidos_reptiles.py`;
  - `mobs/Reptiles.java` y las fichas en `Fichas.java` (grupo REPTILES, sin aparición natural);
  - los rótulos del chat, con `catalogo.py`; reescribe 1321 PNG idénticos, que hay que devolver uno a uno comparando píxeles;
  - la prueba `materiales/pruebas/prueba_reptiles.py`.
- **Mecánicas:**
  - Guerrero: veneno II, 8 s.
  - Raptores: salen de tres en tres (`finalizeSpawn`, salvo REINFORCEMENT), se avisan de la presa y siguen al más antiguo.
  - Plumosaurio: neutral; si le pegas, se revuelve, lanza por los aires y se calma a los 30 s.
  - Cavador: a menos de 4 bloques se entierra (estado 1: solo asoman los prismas; no se le hiere), acecha y sale mordiendo y lanzando; espera 5 s antes de volver a enterrarse.

**Tamaños** (20-10, Juan): «el plumosaurio hazlo más grande, por lo menos 6 bloques; los Dromoraptor, 3 bloques; el Reptisaurio Cavador, 1 bloque; los Reptisaurio, un poco más grandes».
- Quedan así: Plumosaurio 6,3; Dromoraptores 3,1; Cavador 1,0; Salvaje 2,9; Guerrero 2,6.
- Se hace con `TAM` y `agrandar(m, k)` en el generador: escala las cajas, los pivotes y los movimientos de las animaciones, y el paso se divide por k.
- El píxel sigue a 16 por bloque: no se usa la `escala` del render, que lo agrandaría (Juan, 18-10: «en mc ya hay un determinado tamaño para un píxel»). La textura sale con más o menos píxeles.
- Las caras dibujadas píxel a píxel (`cara_reptil`, `lado_ojo(k)`, `mapas_plumosaurio(k)`, `CARA_CAVADOR_CHICO`) se generan ya al tamaño final, para que no salgan píxeles desiguales.
- Las cajas de choque de `Fichas.java` se ajustaron a los tamaños nuevos.
- Ya no hace falta preguntarle por el tamaño.

**Animaciones** (20-10). Juan dijo: «las del plumosaurio están raras (los pies, y al ver un enemigo gira bruscamente entre izquierda y derecha); mejorar las de los dromoraptor y el cavador; los reptisaurio, brazos en V y les faltan animaciones».
- **Brazos en V:** se lo pregunté y contestó «brazos en V». Bajan de los hombros cerrándose hacia el centro, con las manos delante y de cara una a la otra.
- **Reptisaurios:**
  - partes `tronco` (aparte de la cadera), `espinilla` (rodilla) y `antebrazo` (codo);
  - reposo, andar y correr; la rodilla solo se dobla al adelantar la pierna (con la base fija parecía arrodillarse);
  - zarpazo y `especial` = rugido al ver presa (sonido `rugido`).
- **Raptores:** `cana` (rodilla) y `cola2`; reposo con la cabeza a tirones de pájaro, andar y correr, mordisco y `especial` = la llamada.
- **Plumosaurio:**
  - patas que se levantan (`forma=max(0, v)`) en vez de barrer;
  - `mirar` suave (0,35 y 0,12);
  - en Java, `getMaxHeadYRot` 30 y `getHeadRotSpeed` 4;
  - el ataque se encabrita.
- **Cavador:**
  - pilares que pisan (los mueve en vez de girarlos);
  - `especial` = se hunde en 12 ticks, y luego el estado 1 (en Java, `luego(12, …)`).
- Para comprobar los fotogramas: `scratchpad/tira_anim.py`.

**Nombre del Cavador** (20-10): en el libro del juego del D4 se llama **Molusco Rocoso** (fila del día 4). Sale en la Guarida de Qumara, suelta Hongo Marrón y Fragmento de Netherita, y se entierra si te **alejas** demasiado. Juan dijo que sí: ahora se llama `molusco_rocoso` (clase `Reptiles.Molusco`). Es lento y ataca a quien se acerca a menos de 8 bloques; si te alejas a más de 6, se entierra y te sigue bajo tierra a 2,6 veces su velocidad hasta tenerte a 1,8, y sale mordiendo. Suelta Hongo Marrón y, una vez de cada tres, Fragmento de Netherita. Brazos de los reptisaurios: [[reptisaurios-brazos-en-arco]].

**Estado:**
- Generador: `materiales/generadores/bestiario_reptiles.py` (sin commit). `MOBS[id]()` solo construye y el `main` exporta.
- Las vistas exportan a `scratchpad/raiz_reptiles`, así que no tocan el repo.
- `scratchpad/luz_mc.py` ilumina las vistas como el juego, por la normal y sin darle la vuelta. Sin eso, las membranas vistas desde abajo salen negras.
- Ya están en el juego (20-10), sin commit. La prueba `prueba_reptiles.py` dio 11 de 11 OK, con fotos en `run/screenshots/reptiles_*`. Falta que Juan los pruebe. Después vienen la mejora, el Java, los sonidos y la prueba en el juego.

**Why:** es la familia que sigue en el catálogo del DEDsafío ([[catalogo-dedsafio]]).

**How to apply:** con cualquier mob de un cartel, medir al píxel, sacar la paleta y comparar con el original encima desde el principio. A ojo sale «un chiste». Sigue el método de [[recrear-primero-luego-mejorar]].
