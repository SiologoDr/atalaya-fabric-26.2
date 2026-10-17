"""
El índice visual de las ideas del DEDsafío (17-10-2026). Juan: «hazlo como un index html más visual, porque con texto me
voy a perder; pon todos los cambios, mobs y jefes de cada edición, todo en un index».

Lee materiales/ideas/dedsafio_2.md, dedsafio_3.md, dedsafio_4.md y repertorio.md y escribe materiales/ideas/index.html:
una sola página con cada edición día a día (los cambios con su tipo, su fuente y el cartel), la galería de mobs, los
jefes, las otras mecánicas, lo que falta y el repertorio por mecánica. Se filtra por edición y por tipo y se busca.

Las imágenes son de @dedsafio y de las cuentas de fans: no se copian, se enlazan (pbs.twimg.com). medios.json guarda, por
cada tuit enlazado en los documentos, la URL de su primera imagen; los que falten se piden a api.fxtwitter.com.

Uso: python ideas_index.py <raiz del proyecto> [--sin-red]
"""
import html, json, os, re, sys, time, urllib.request

RAIZ = sys.argv[1] if len(sys.argv) > 1 else '../..'
SIN_RED = '--sin-red' in sys.argv
IDEAS = os.path.join(RAIZ, 'materiales', 'ideas')
MEDIOS = os.path.join(IDEAS, 'medios.json')
# recortes.json: por cada cartel, el recuadro (en %) del dibujo de cada cambio, medido a mano; asi cada cambio y cada mob
# lleva su dibujo sin copiar la imagen (la pagina enseña solo ese trozo del cartel enlazado)
RECORTES = os.path.join(IDEAS, 'recortes.json')
# mobs de la tabla cuyo cambio en el cartel se llama de otra forma (el comienzo del nombre del mob: el del cambio)
ALIAS = {'3': {'creeper electrico': 'creeper mania', 'fantas': 'pandemia fantasma', 'phantoms revuelve': 'adivinen quienes',
               'aranas venenosas': 'fiebre aracnida', 'wardens en las aldeas': 'atte', 'bombas voladoras': 'bombas tacticas',
               'arquimagos': 'elfos magicos', 'piglin': 'feliz ano nuevo'}}
# jefes con su cartel o su foto (el tuit, enlazado en el documento)
# (la clave es una expresión sobre el nombre entero: el REviil del Templo del dragón no es el del encuentro final)
JEFES_IMG = {'3': {r'^hydra': '1845297015648862700', r'^titan': '1847746087500566783', r'^reviil$': '1850221401732472906'}}
TUIT = re.compile(r'https://x\.com/([A-Za-z0-9_]+)/status/(\d+)')

EDICIONES = {
    '2': dict(titulo='DEDsafío 2', anio='2022', fechas='22-07 → 20-08-2022', color='#62c46f',
              resumen='Treinta días con el diario de la nutria Eón: arañas, hormigas y plantas que envenenan, el '
                      'Flashbang que se come las antorchas, las cucharas de la resurrección y el gulag.'),
    '3': dict(titulo='DEDsafío 3', anio='2024', fechas='25-09 → 26-10-2024', color='#ad86ff',
              resumen='La ruleta diaria, los Tikis, la Legión de las Brumas y el Limbo: fantasmas que solo mueren con '
                      'la espada fantasmal, el sapo que te traga, las bombas voladoras y REviil.'),
    '4': dict(titulo='DEDsafío 4', anio='2026', fechas='21-09 → 17-10-2026', color='#ff9a3d',
              resumen='Quiu, Gleba y el Limbo: dinosaurios, cerebros que se te suben a la cabeza, naves Phora, '
                      'creepers de todo tipo, los Momentos Reviil y los jefes Qumara, el Observalador y Ofidia.'),
}
TIPOS = [('nuevo', 'Mob nuevo'), ('cambiado', 'Mob cambiado'), ('jugador', 'Jugador'), ('mundo', 'Mundo y bloques'),
         ('items', 'Objetos'), ('evento', 'Evento'), ('otro', 'Otro')]


# ----------------------------------------------------------------------
#  Las imágenes
# ----------------------------------------------------------------------
def cargar_medios(textos):
    medios = json.load(open(MEDIOS, encoding='utf-8')) if os.path.exists(MEDIOS) else {}
    faltan = sorted({(u, i) for t in textos for u, i in TUIT.findall(t) if i not in medios}, key=lambda x: x[1])
    if faltan and not SIN_RED:
        print('pidiendo', len(faltan), 'tuits a fxtwitter', flush=True)
        for usuario, i in faltan:
            try:
                d = json.load(urllib.request.urlopen(urllib.request.Request(
                    'https://api.fxtwitter.com/%s/status/%s' % (usuario, i), headers={'User-Agent': 'Mozilla/5.0'}),
                    timeout=30))
                m = (d.get('tweet') or {}).get('media') or {}
                img = m['photos'][0]['url'].split('?')[0] if m.get('photos') else (
                    m['videos'][0].get('thumbnail_url') if m.get('videos') else None)
                medios[i] = {'img': img, 'usuario': usuario}
            except Exception as e:
                print('  err', usuario, i, e)
            time.sleep(0.3)
        with open(MEDIOS, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(medios, fh, ensure_ascii=False, indent=1)
    return {k: v.get('img') for k, v in medios.items() if v.get('img')}


# ----------------------------------------------------------------------
#  De markdown a HTML (lo justo)
# ----------------------------------------------------------------------
def en_linea(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'(?<!href=")(?<!">)(https?://[^\s<)]+)', lambda m: '<a href="%s" target="_blank" rel="noopener">↗</a>'
               % m.group(1).rstrip('.,;'), t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t


def limpio(t):
    """El texto sin marcas (para buscar y para los nombres)."""
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    return re.sub(r'[*`]', '', t).strip()


def tipos_de(texto):
    t = texto.lower()
    out = []
    for clave, palabras in (('nuevo', ('mob nuevo', 'nuevo mob', 'facción')), ('cambiado', ('mob cambiado', 'mob/', '/mob')),
                            ('jugador', ('jugador',)), ('mundo', ('mundo', 'bloques', 'spawn')),
                            ('items', ('ítems', 'items', 'comida', 'comercio', 'rol', 'transporte', 'ayuda')),
                            ('evento', ('evento',))):
        if any(p in t for p in palabras):
            out.append(clave)
    return out or ['otro']


FUENTE = re.compile(r'\[((?:C|C-texto|O|F|F-chat|Mill|Addon|addon|fans|VOD|TikTok|prensa|mod de fans|O, recuperado|'
                    r'Vídeo|X: @|Títulos|TwitchLatam|Eufonia|clip Twitch|clips Twitch|YouTube)'
                    r'[^\]]*)\](?!\()')


def entrada(texto):
    """Un punto de un día: (nombre, tipos, descripción, fuentes, tuits) o None si es una nota."""
    t = texto.strip()
    cab = re.match(r'^((?:\[[^\]]+\]\s*)*)(?:\*\*(.+?)\*\*|\*\((.+?)\)\*)', t)
    if not cab:
        return None
    nombre = limpio(cab.group(2) or '(%s)' % cab.group(3))
    resto = t[cab.end():]
    tipos_txt = ''
    for patron in (r'^\s*\(((?:`[^`]+`(?:,\s*)?)+)\)', r'^\s*(?:\([^)]*\)\s*)?·\s*\*([^*]+)\*', r'^\s*\[([^\]]+)\](?!\()'):
        m = re.match(patron, resto)
        if m:
            tipos_txt = m.group(1)
            resto = resto[m.end():]
            break
    if not tipos_txt:
        m = re.search(r'\(`([^`]+)`', resto[:40])
        tipos_txt = m.group(1) if m else ''
    resto = re.sub(r'^\s*[:,·.]\s*', '', resto)
    fuentes = [f for f in FUENTE.findall(cab.group(1) + ' ' + resto)]
    resto = re.sub(r'\s{2,}', ' ', FUENTE.sub('', resto)).strip()
    return dict(nombre=nombre, tipos=tipos_de(tipos_txt + ' ' + nombre if tipos_txt else nombre),
                desc=resto.strip(), fuentes=sorted(set(fuentes)), tuits=[i for _, i in TUIT.findall(t)])


# ----------------------------------------------------------------------
#  Cada edición
# ----------------------------------------------------------------------
def secciones(md):
    """{titulo de '## ': [lineas]}, en orden."""
    out, actual = [], None
    for linea in md.split('\n'):
        if linea.startswith('## '):
            actual = [linea[3:].strip(), []]
            out.append(actual)
        elif actual is not None:
            actual[1].append(linea)
    return out


def leer_dias(lineas):
    dias, semana, dia, ultimo, bajo_nota = [], None, None, None, False
    for linea in lineas:
        if re.match(r'^###\s+Semana', linea):
            semana = limpio(linea.lstrip('#').strip())
            continue
        m = re.match(r'^#{3,4}\s+(Días?\b.*)$', linea)
        if m:
            cab = m.group(1)
            num = re.search(r'\d+', cab)
            enlaces = TUIT.findall(cab)
            dia = dict(titulo=en_linea(re.sub(r'\s*·?\s*\[(?:cartel|tuit)\]\([^)]+\)', '', cab)),
                       num=int(num.group()) if num else 0, semana=semana, cartel=None, extra=[], entradas=[], notas=[])
            etiquetas = re.findall(r'\[([^\]]+)\]\((https://x\.com/[^)]+)\)', cab)
            for etiqueta, url in etiquetas:
                i = TUIT.search(url).group(2)
                if etiqueta in ('cartel', 'tuit') and not dia['cartel']:
                    dia['cartel'] = i
                else:
                    dia['extra'].append(i)
            if not dia['cartel'] and enlaces and not etiquetas:
                dia['extra'] += [i for _, i in enlaces]
            dias.append(dia)
            ultimo, bajo_nota = None, False
            continue
        if dia is None:
            continue
        if linea.startswith('Cartel:'):
            m = TUIT.search(linea)
            if m:
                dia['cartel'] = m.group(2)
            nota = re.sub(r'^Cartel:\s*https?://\S+\s*', '', linea).strip()
            if nota:
                dia['notas'].append(en_linea(nota))
            continue
        if linea.startswith('- '):
            e = entrada(linea[2:])
            if e:
                e['html'] = en_linea(e['desc']) if e['desc'].strip(' .') else ''
                dia['entradas'].append(e)
                ultimo, bajo_nota = e, False
            else:
                dia['notas'].append(en_linea(linea[2:]))
                ultimo, bajo_nota = None, True
            continue
        # subpuntos, pasos numerados y párrafos sangrados: van con el cambio de encima; bajo una nota, un subpunto
        # con su nombre en negrita es un cambio más (los que salen de leer un directo entero)
        sub = re.match(r'^\s{2,}- (.*)$', linea) or re.match(r'^\s*(\d+\.\s.*)$', linea) \
            or (re.match(r'^\s{2,}\S', linea) and ultimo is not None and re.match(r'^\s*(.*)$', linea))
        if sub:
            texto = sub.group(1).strip()
            if (ultimo is None or bajo_nota) and linea.lstrip().startswith('- '):
                e = entrada(texto)
                if e:
                    e['html'] = en_linea(e['desc']) if e['desc'].strip(' .') else ''
                    dia['entradas'].append(e)
                    ultimo = e
                    continue
                if bajo_nota:
                    ultimo = None
            if ultimo is not None:
                ultimo['fuentes'] = sorted(set(ultimo['fuentes'] + FUENTE.findall(texto)))
                texto = re.sub(r'\s{2,}', ' ', FUENTE.sub('', texto)).strip()
                ultimo['html'] += ('<br>' if ultimo['html'] else '') + '<span class="sub">' + en_linea(texto) + '</span>'
                ultimo['desc'] += ' ' + texto
                ultimo['tuits'] += [i for _, i in TUIT.findall(texto)]
            else:
                dia['notas'].append(en_linea(texto))
            continue
        if linea.strip() and not linea.startswith('#') and not linea.startswith('---'):
            dia['notas'].append(en_linea(linea.strip()))
            ultimo, bajo_nota = None, True
    return dias


def leer_tablas(lineas):
    """Las tablas de markdown: [(cabecera, filas)]."""
    tablas, actual = [], None
    for linea in lineas:
        if linea.startswith('|'):
            celdas = [c.strip() for c in linea.strip().strip('|').split('|')]
            if actual is None:
                actual = (celdas, [])
                tablas.append(actual)
            elif not all(re.match(r'^:?-+:?$', c) for c in celdas):
                actual[1].append(celdas)
        else:
            actual = None
    return tablas


def leer_puntos(lineas, saltar_tablas=True):
    """Los puntos y párrafos sueltos (fuera de las tablas), con los subpuntos dentro."""
    out = []
    for linea in lineas:
        if linea.startswith('|') or not linea.strip() or linea.startswith('---'):
            continue
        if linea.startswith('### '):
            out.append(('titulo', en_linea(linea[4:].strip())))
        elif linea.startswith('- '):
            out.append(('punto', en_linea(linea[2:])))
        elif re.match(r'^\s{2,}- ', linea) and out and out[-1][0] == 'punto':
            out[-1] = ('punto', out[-1][1] + '<br><span class="sub">' + en_linea(linea.strip()[2:]) + '</span>')
        else:
            out.append(('parrafo', en_linea(linea.strip())))
    return out


def leer_detalles(lineas):
    """Los jefes vistos en los directos: [{nombre, enlace, puntos}], de líneas «**Nombre** · [VOD…](url)» y sus puntos."""
    out = []
    for linea in lineas:
        m = re.match(r'^\*\*(.+?)\*\*(.*)$', linea)
        if m:
            u = re.search(r'\]\((https?://[^)\s]+)\)', m.group(2))
            out.append(dict(nombre=limpio(m.group(1)), enlace=u.group(1) if u else None, puntos=[]))
        elif out and linea.startswith('- '):
            out[-1]['puntos'].append(en_linea(linea[2:]))
        elif out and re.match(r'^\s{2,}- ', linea) and out[-1]['puntos']:
            out[-1]['puntos'][-1] += '<br><span class="sub">' + en_linea(linea.strip()[2:]) + '</span>'
    return out


def norma(t):
    """El nombre para comparar: en minusculas, sin tildes ni signos."""
    t = limpio(t).lower()
    for a, b in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ü', 'u'), ('ñ', 'n')):
        t = t.replace(a, b)
    return ' '.join(re.findall(r'[a-z0-9]+', t))


def edicion(clave, md, imgs, recortes):
    secs = secciones(md)
    intro = md.split('## ')[0].split('\n', 1)[1]
    dias, mobs, otras, falta, detalles = [], [], [], [], []
    for titulo, lineas in secs:
        tl = titulo.lower()
        if tl.startswith('1.'):
            dias = leer_dias(lineas)
        elif 'mobs' in tl or 'jefes' in tl:
            # «Los tres jefes vistos en los directos»: cada jefe en negrita con sus puntos debajo; va a su ficha
            vistos = [k for k, l in enumerate(lineas) if re.match(r'^###\s.*vistos en los directos', l)]
            if vistos:
                fin = next((k for k in range(vistos[0] + 1, len(lineas)) if lineas[k].startswith('### ')), len(lineas))
                detalles = leer_detalles(lineas[vistos[0] + 1:fin])
                lineas = lineas[:vistos[0]] + lineas[fin:]
            for cab, filas in leer_tablas(lineas):
                es_jefes = cab[0].lower().startswith('jefe')
                for f in filas:
                    f = f + [''] * (4 - len(f))
                    jefe = es_jefes or bool(re.search(r'\([^)]*\b(jefe|jefa|villano)\b[^)]*\)', f[0], re.I))
                    nombre = limpio(re.sub(r'\s*\((jefe|jefa|jefe final)\)', '', f[0], flags=re.I))
                    mobs.append(dict(nombre=nombre, donde=en_linea(f[1]), que=en_linea(f[2]), fuente=en_linea(f[3]),
                                     jefe=jefe, tuits=[i for _, i in TUIT.findall(' '.join(f))],
                                     texto=limpio(' '.join(f[1:3])), donde_txt=f[1], fuente_txt=f[3]))
            otras += leer_puntos(lineas)
        elif 'falta' in tl:
            falta = leer_puntos(lineas)
        else:
            otras += [('titulo', en_linea(titulo.split('.', 1)[-1].strip()))] + leer_puntos(lineas)
    # las imágenes
    for d in dias:
        d['img'] = imgs.get(d['cartel']) if d['cartel'] else None
        d['img_tuit'] = d['cartel']
        d['extras'] = [(i, imgs[i]) for i in d['extra'] if i in imgs]
        if not d['img'] and d['extras']:
            d['img_tuit'], d['img'] = d['extras'][0]
            d['extras'] = d['extras'][1:]
        libres = [[norma(n), caja] for n, caja in recortes.get(d['cartel'] or '', [])]
        for e in d['entradas']:
            propias = [i for i in e['tuits'] if i != d['cartel'] and i in imgs]
            e['img'] = imgs[propias[0]] if propias else None
            e['img_tuit'] = propias[0] if propias else None
            e['tuit'] = e['tuits'][0] if e['tuits'] else None
            e['recorte'] = None
            en = norma(e['nombre'])
            for k, (n, caja) in enumerate(libres):
                if en == n or en.startswith(n + ' ') or n.startswith(en + ' '):
                    e['recorte'] = dict(img=d['img'], tuit=d['cartel'], caja=caja)
                    libres.pop(k)
                    break
    por_num = {d['num']: d for d in dias}
    for mob in mobs:
        primera = norma(mob['nombre']).split(' ')[0]
        mob['detalle'] = next((dt for dt in detalles if norma(dt['nombre']).split(' ')[0] == primera), None)

    for mob in mobs:
        mob['img'], mob['img_tuit'], mob['cartel'], mob['recorte'] = None, None, None, None
        propias = [i for i in mob['tuits'] if i in imgs]
        nombre = norma(re.sub(r'\(.*?\)', '', mob['nombre']))
        for inicio, otro in ALIAS.get(clave, {}).items():
            if nombre.startswith(inicio):
                nombre = otro
        for patron, i in JEFES_IMG.get(clave, {}).items():
            if re.search(patron, norma(mob['nombre'])) and i in imgs:
                propias = [i]
        if propias:
            mob['img_tuit'], mob['img'] = propias[0], imgs[propias[0]]
            continue
        # el cambio del día que lleva su nombre: su dibujo en el cartel o, si no, su captura
        m = re.search(r'\bD(\d+)\b', mob['donde_txt'] + ' ' + mob['fuente_txt'])
        preferido = int(m.group(1)) if m else None
        candidatos = []
        for d in dias:
            for e in d['entradas']:
                en = norma(e['nombre'])
                if nombre and (en == nombre or en.startswith(nombre + ' ') or nombre.startswith(en + ' ')):
                    candidatos.append((d['num'] != preferido, e['recorte'] is None, e))
        candidatos = [c for c in candidatos if c[2]['recorte'] or c[2]['img']]
        if candidatos:
            e = sorted(candidatos, key=lambda c: (c[0], c[1]))[0][2]
            if e['recorte']:
                mob['recorte'] = e['recorte']
            else:
                mob['img'], mob['img_tuit'] = e['img'], e['img_tuit']
            continue
        # si no, el día en que salió: su ficha (en el DEDsafío 2) o el enlace a su cartel
        num = None
        m = re.search(r'\bD(\d+)\b', mob['donde_txt'] + ' ' + mob['fuente_txt'])
        if m:
            num = int(m.group(1))
        if num is None:
            m = re.search(r'd[íi]a (\d+)', mob['donde_txt'], re.I)
            num = int(m.group(1)) if m else None
        if num is None:
            m = re.search(r'(\d\d-\d\d)', mob['donde_txt'])
            if m:
                for d in dias:
                    if m.group(1) in limpio(d['titulo']):
                        num = d['num']
                        break
        d = por_num.get(num)
        if d:
            if 'ficha' in mob['fuente_txt'] and d['extras']:
                mob['img_tuit'], mob['img'] = d['extras'][0]
            else:
                mob['cartel'] = d['img_tuit']
    E = EDICIONES[clave]
    return dict(clave=clave, **E, intro=[en_linea(p.strip()) for p in intro.strip().split('\n\n') if p.strip()],
                dias=dias, mobs=mobs, otras=otras, falta=falta)


def repertorio(md):
    secs = []
    intro = md.split('## ')[0].split('\n', 1)[1]
    for titulo, lineas in secciones(md):
        tablas = leer_tablas(lineas)
        puntos = leer_puntos(lineas)
        secs.append(dict(titulo=re.sub(r'^\d+\.\s*', '', titulo), num=(re.match(r'^(\d+)', titulo) or [0, '0'])[1],
                         tablas=[dict(cab=[en_linea(c) for c in cab], filas=[[en_linea(c) for c in f] for f in filas])
                                 for cab, filas in tablas],
                         puntos=puntos))
    return dict(intro=[en_linea(p.strip()) for p in intro.strip().split('\n\n') if p.strip()], secciones=secs)


# ----------------------------------------------------------------------
#  La página
# ----------------------------------------------------------------------
PAGINA = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ideas_index.html'), encoding='utf-8').read()


def main():
    textos = {k: open(os.path.join(IDEAS, 'dedsafio_%s.md' % k), encoding='utf-8').read() for k in EDICIONES}
    rep = open(os.path.join(IDEAS, 'repertorio.md'), encoding='utf-8').read()
    imgs = cargar_medios(list(textos.values()) + [rep])
    recortes = json.load(open(RECORTES, encoding='utf-8')) if os.path.exists(RECORTES) else {}
    datos = dict(ediciones=[edicion(k, textos[k], imgs, recortes) for k in EDICIONES], tipos=TIPOS,
                 repertorio=repertorio(rep))
    for e in datos['ediciones']:
        n_ent = sum(len(d['entradas']) for d in e['dias'])
        print('DEDsafío', e['clave'], len(e['dias']), 'días,', n_ent, 'cambios,', len(e['mobs']), 'mobs y jefes,',
              sum(1 for d in e['dias'] if d['img']), 'días con imagen,',
              sum(1 for d in e['dias'] for x in d['entradas'] if x['recorte']), 'cambios con dibujo,',
              sum(1 for m in e['mobs'] if m['img'] or m['recorte']), 'mobs con imagen')
    js = json.dumps(datos, ensure_ascii=False).replace('</', '<\\/')
    salida = os.path.join(IDEAS, 'index.html')
    with open(salida, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(PAGINA.replace('/*DATOS*/null', js))
    print('ok', salida)


if __name__ == '__main__':
    main()
