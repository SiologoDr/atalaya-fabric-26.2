# Ideas

Un repertorio de ideas para Atalaya, sacado de lo que hicieron otros. Juan, 17-10-2026: «saca todos los cambios de
dificultad y todos los mobs que añadieron en el DEDsafío 2, 3 y 4, el actual, para ver qué cosas hacen y así tener un
repertorio de ideas».

## Qué hay

- **`index.html`**: todo lo de abajo en una página, para verlo sin perderse. Ábrela en el navegador. Tiene los días de
  cada edición con el dibujo de cada cambio sacado de su cartel, las fichas de mobs y jefes, las otras mecánicas y el
  repertorio por mecánica, con un buscador. **Es por donde empezar.** Se rehace con
  `python ideas_index.py ../..` desde `materiales/generadores/`, que lee los `.md` de esta carpeta: si cambias un
  documento, vuelve a generarla.
- **`repertorio.md`**: lo de las tres ediciones junto y ordenado por lo que hace. Están los mobs que te atrapan, los que
  te ciegan o te quitan algo, los creepers y bombas, los que salen cuando haces algo, los cambios al jugador y al mundo,
  los objetos, los «Momentos» y los jefes. En cada idea se apunta qué tenemos ya en Atalaya.
- **`dedsafio_2.md`**: el DEDsafío 2 (del 22-07 al 20-08-2022), día a día, con sus mobs y jefes.
- **`dedsafio_3.md`**: el DEDsafío 3 (del 25-09 al 26-10-2024).
- **`dedsafio_4.md`**: el DEDsafío 4 (del 21-09 al 17-10-2026). El final contra Reviil fue el mismo 17-10, así que no
  está.
- **`medios.json`** y **`recortes.json`**: los datos de la página. El primero guarda la imagen de cada tuit enlazado
  (solo la dirección); el segundo, dónde está el dibujo de cada cambio dentro de su cartel.

## De dónde sale

- **Los carteles oficiales** «Cambios de dificultad» de @dedsafio en X. Se leen desde aquí con
  `https://api.fxtwitter.com/dedsafio/status/<id>`, porque X no se abre directo. Cada día de los documentos lleva el
  enlace a su cartel.
- **Lo que no tiene cartel** sale de las cuentas de fans que contaban los cambios en directo, y va marcado:
  - @DedsafioMuertes en el D2;
  - @Cracksterss en el D4;
  - en el D3, los textos de los clips de muertes que publicaba el propio @dedsafio.
- **Los directos** (segunda pasada): los avisos del juego y el chat, leídos en fotogramas de los vídeos guardados. Son
  los de Kick en el D4, los destacados de Twitch de los participantes en el D3, y los episodios de YouTube en el D2. Van
  marcados con el canal y el minuto (por ejemplo, `[VOD: elded, 01-10, 2:21:57]`).
- **Lo que sale solo de mods de fans** también va marcado.
- **Los huecos** están dichos en cada documento, al final.
- **Las imágenes no se copian aquí** (son suyas). Solo van los enlaces, como en las fichas de jefes; la página las
  carga de X al abrirla, así que sin internet salen vacías.

## Ojo

- Son ideas para inspirarse, no para copiar. Lo que hagamos tiene que ser nuestro y con nuestro toque (ver
  `fichas/COMO_HACEMOS_LOS_MONSTRUOS.md`).
- Algunos mobs se atribuyen a veces a la edición que no es. Por ejemplo, el Creeper de Pasto, el Creeper Nuclear, la
  Bomba Negra, el Fantasma Farola, el Narval y los Cerebros son del DEDsafío 4, no del 3.
