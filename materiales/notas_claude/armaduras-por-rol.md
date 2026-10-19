---
name: armaduras-por-rol
description: "Diseño aprobado (2026-10-06) de las armaduras y armas elementales por rol (tanque, sanador, soporte, DPS) y cómo equilibrarlas para 60 jugadores"
metadata:
  node_type: memory
  type: project
  originSessionId: 04c72911-117c-483d-8550-53112d80af90
  modified: 2026-10-07T04:14:20.298Z
---

Cada elemento tiene un rol, y su armadura una pasiva y una activa: tecla R con el conjunto entero, recarga de 120 s y 30 s de duración. Cada arma es acorde a su rol. Por ahora solo se consiguen en creativo. Diseño final del usuario (2026-10-06):

**Tierra / tanque (jade, Rajang)**
- Protección 4/9/7/4.
- Pasiva *Guardián*: los aliados a 4 bloques reciben un 5 % menos de daño (no se acumula).
- Activa *Muralla de Jade*:
  - Los ataques de un solo objetivo del jefe van al tanque si está a su alcance. Después, el jefe no se puede atraer de nuevo durante 15 s.
  - Protege a sus 2 aliados más cercanos: recibe el 30 % del daño que les llega, reducido por su propia armadura.
  - El tanque recibe un 20 % menos de daño mientras dura.
- *Martillo de Jade*: 9 de daño, lento. El golpe cargado aturde 1 s a un monstruo normal y hace que le ataque (ni minijefes ni jefes).

**Agua / sanador (mareas, Nerea)**
- Protección de netherita y 1 corazón más.
- Pasiva *Marea Viva*: cada 5 s cura medio corazón al aliado más herido a 6 bloques. Como mucho medio corazón cada 5 s por jugador, haya los sanadores que haya.
- Activa *Manantial*:
  - Al activarse, quita los efectos negativos de los 3 aliados más heridos.
  - Cada 3 s cura medio corazón a los 3 más heridos a 8 bloques. Como mucho medio corazón cada 3 s por jugador.
- *Tridente de las Mareas*: 9 de daño, se lanza y vuelve. Cada 8 s, un golpe cura medio corazón al aliado más herido.

**Viento / soporte (vendaval, Aeralis)**
- Protección de netherita.
- Pasiva *Viento a Favor*: +10 % de velocidad a los aliados a 6 bloques (no se acumula) y −25 % de daño de caída para el que la lleva.
- Activa *Corriente Ascendente*:
  - Él y sus 4 aliados más cercanos reciben Velocidad I durante 30 s y 2 corazones dorados.
  - Una ráfaga aleja a los monstruos normales de su alrededor (solo de él, no de los aliados).
  - Quien ya la tiene no puede recibirla de otro soporte.
- *Arco del Vendaval*:
  - Daño como Poder III; admite Poder V encima (en total, como «Poder 8»). Flechas un 20 % más rápidas.
  - Una flecha que da a un aliado le da Velocidad I 3 s y +5 % de velocidad, una vez cada 20 s por jugador.

**Fuego / DPS (solar, Novilis)**
- Protección de netherita.
- Pasiva *Corazón de Brasa*: +10 % de daño.
- Activa *Furia Solar*: +20 % de daño. Sus 3 aliados más cercanos hacen un 5 % más de daño, una vez cada 20 s por jugador (no se acumula). Lo interpreté como un bonus para ellos, no como daño extra que reciben.
- *Gran Espada Solar*: 10 de daño; prende fuego a los monstruos normales.

**Estado (2026-10-07):** construido, probado en el juego y entregado en atalaya-1.1.6.jar (creativo; tecla R o `/atalaya habilidad`).
- La parte que absorbe el tanque va como daño propio `atalaya:muralla_jade` (con armadura, sin empuje y sin gastar su invulnerabilidad), y solo si el golpe es de un enemigo.
- El Arco descuenta su +20 % de velocidad del daño, para que pegue exactamente como Poder III (o VIII con Poder V).
- Las auras de las activas solo las ven los demás jugadores: al que la lleva le taparían la vista en primera persona.
- Pruebas: `PruebaAliados` (con run/atalaya_fotos.flag) crea aliados falsos que reciben daño y usan armas.

**Why:** el usuario lo ajustó en tres rondas.
- Primero, nada debía romperse con 60 jugadores del mismo rol.
- Después: «algo de ventaja sí, pero no tanto».
- Por último: «cada rol debe cumplir su rol» (el tanque protege a los demás, no a sí mismo).

**How to apply:**
- Al diseñar habilidades de grupo:
  - nada se acumula;
  - poner un tope por receptor (curas cada X s por jugador) y por número de aliados afectados;
  - las mecánicas letales y cooperativas de los jefes nunca se ven afectadas (Mirada, Rugido de Jade, meteorito directo, Juicio);
  - el fuego y las provocaciones de las armas no afectan a jefes ni minijefes.
- Ver [[danos-letales-por-fase]] y [[jefes-rapidos-e-imponentes]].
