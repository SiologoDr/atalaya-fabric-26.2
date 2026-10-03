"""
Guion del video de presentacion del Vigia. Cada escena: su frase de voz y lo
que se ve. La duracion de cada toma sale de la duracion real de la voz, asi
que este fichero manda sobre la edicion y sobre el datapack de rodaje.
"""

VOZ = "es-MX-JorgeNeural"
RITMO = "-8%"
TONO = "-6Hz"

ESCENAS = [
    # clave,      etiqueta en pantalla,  frase
    ("vigilar",  None,
     "Cuando cae la noche sobre la atalaya... algo empieza su guardia."),
    ("alerta",   "EL VIGÍA",
     "El Vigía. Si su farol se vuelve rojo... ya te ha visto."),
    ("mirada",   "LA MIRADA",
     "Su ojo se carga... y dispara. Lo que alcanza, queda marcado: brillarás a través de las paredes, y cada monstruo cercano irá a por ti."),
    ("cepo",     "EL CEPO",
     "De cerca, abre los brazos... y se cierra como una trampa."),
    ("espalda",  "PUNTO CIEGO",
     "Pero no puede verlo todo. Golpéalo por la espalda, y perderá el equilibrio."),
    ("buscar",   "SI TE ESCONDES",
     "Escóndete... y te buscará."),
    ("muerte",   "LA ÚLTIMA GUARDIA",
     "Y cuando por fin cae... su luz se apaga para siempre."),
    ("botin",    "OJO DEL VIGÍA",
     "Lo que deja es su ojo. Úsalo, y por un momento, serás tú quien vigila."),
    ("cierre",   None,
     "El Vigía. Lo que mira, lo maldice. Llega a Atalaya... en modo hardcore."),
]
