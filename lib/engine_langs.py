"""
Textes du moteur par dates et de la page « toute l'année » pour l'espagnol (es),
l'allemand (de) et l'anglais américain (en-us, °F et miles).

Fusionnés dans lib/date_engine.I18N, lib/annual_engine.A18N et
generate_moteur_mois.TEXTS / ANNUAL_TEXTS. Les pages de ces langues restent en
noindex (apply_indexation.py) ; elles servent les visiteurs redirigés par pays.

Dates des raccourcis : jours fériés fixes ou calculés (Pâques 2027 = 28 mars),
jamais des vacances scolaires régionales (elles varient selon la région).
"""
import copy

# ── Format des nombres et des dates (aussi pour fr et en, voir date_engine) ──
#   ni : index du nom dans les données (0 fr, 1 en, 2 es, 3 de)
#   imp : 1 = °F et miles
NF = {
    'fr': {'ni': 0, 'imp': 0, 'dec': ',', 'th': '\u202f', 'h': '{h} h {mm}', 'h0': '{h} h', 'date': '{wd} {d} {m} {y}', 'first': '1er',
           'rs': 'du {a} au {b} {m}', 'rd': 'du {a} {ma} au {b} {mb}', 'hl': 'fr'},
    'en': {'ni': 1, 'imp': 0, 'dec': '.', 'th': ',', 'h': '{h}h{mm}', 'h0': '{h}h', 'date': '{wd} {d} {m} {y}', 'first': '',
           'rs': 'from {a} to {b} {m}', 'rd': 'from {a} {ma} to {b} {mb}', 'hl': 'en'},
    'en-us': {'ni': 1, 'imp': 1, 'dec': '.', 'th': ',', 'h': '{h}h{mm}', 'h0': '{h}h', 'date': '{wd}, {m} {d}, {y}', 'first': '',
              'rs': 'from {m} {a} to {b}', 'rd': 'from {ma} {a} to {mb} {b}', 'hl': 'en-US'},
    'es': {'ni': 2, 'imp': 0, 'dec': ',', 'th': '.', 'h': '{h} h {mm}', 'h0': '{h} h', 'date': '{wd} {d} de {m} de {y}', 'first': '',
           'rs': 'del {a} al {b} de {m}', 'rd': 'del {a} de {ma} al {b} de {mb}', 'hl': 'es'},
    'de': {'ni': 3, 'imp': 0, 'dec': ',', 'th': '.', 'h': '{h}:{mm} Std.', 'h0': '{h} Std.', 'date': '{wd}, {d}. {m} {y}', 'first': '',
           'rs': 'vom {a}. bis {b}. {m}', 'rd': 'vom {a}. {ma} bis {b}. {mb}', 'hl': 'de'},
}


def _us_text(s):
    """Texte anglais britannique → américain, °C → °F (les valeurs sont converties par le rendu)."""
    if not isinstance(s, str):
        return s
    for a, b in (('°C', '°F'), ('analysed', 'analyzed'), ('favourable', 'favorable')):
        s = s.replace(a, b)
    return s


def _us_dict(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, str):
            out[k] = _us_text(v)
        elif isinstance(v, list):
            out[k] = [_us_text(x) for x in v]
        else:
            out[k] = copy.deepcopy(v)
    return out


# ── I18N du moteur par dates (lib/date_engine) ──────────────────────────────

I18N_ES = {
    'months': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'ms': ['ene.', 'feb.', 'mar.', 'abr.', 'may.', 'jun.', 'jul.', 'ago.', 'sept.', 'oct.', 'nov.', 'dic.'],
    'wd': ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'],
    'uc': {'gen': '☀️ Clima general', 'plage': '🏖️ Playa', 'ski': '⛷️ Esquí', 'rando': '🥾 Senderismo'},
    'uc_t': {'gen': 'Clima general', 'plage': 'Playa y baño', 'ski': 'Montaña y esquí', 'rando': 'Senderismo'},
    'regions': {'eu': 'Europa', 'af-nord': 'Norte de África', 'af': 'África y océano Índico', 'atl': 'Islas atlánticas',
                'am-n': 'América del Norte', 'car': 'Caribe', 'am-s': 'América del Sur', 'as': 'Asia',
                'me': 'Oriente Medio', 'oc': 'Oceanía', 'other': 'Otros países'},
    'secu': {'1': '🟢 Normal', '2': '🟡 Reforzada', '3': '🟠 Desaconsejado', '4': '🔴 No viajar'},
    'budget': {'1': '💚 Económico', '2': '💛 Asequible', '3': '🟡 Moderado', '4': '🟠 Caro', '5': '🔴 Muy caro'},
    'budget_opts': [[5, 'Todos los presupuestos'], [2, 'Hasta 💛 Asequible'], [3, 'Hasta 🟡 Moderado'], [4, 'Hasta 🟠 Caro']],
    'secu_opts': [[4, 'Todos los destinos'], [2, 'Hasta 🟡 Reforzada'], [1, 'Solo 🟢 Normal']],
    'heat_opts': [[-99, 'Da igual'], [16, '16 °C o más'], [20, '20 °C o más'], [24, '24 °C o más']],
    'sorts': {'score': 'Puntuación BestDateWeather', 'dry': 'Las más seguras (menos lluvia)', 'hot': 'Las más cálidas',
              'near': 'Las más cercanas', 'cheap': 'Las más baratas en destino'},
    'deps': [['Madrid', 40.42, -3.70], ['Barcelona', 41.39, 2.17], ['Valencia', 39.47, -0.38], ['Sevilla', 37.39, -5.98],
             ['Málaga', 36.72, -4.42], ['Bilbao', 43.26, -2.93], ['Ciudad de México', 19.43, -99.13], ['Bogotá', 4.71, -74.07],
             ['Lima', -12.05, -77.04], ['Buenos Aires', -34.60, -58.38], ['Santiago de Chile', -33.45, -70.67]],
    'holidays': {
        '9': [{'id': 'pilar', 'chip': 'Puente del Pilar', 'wh': 'puente del Pilar', 'em': 'en el puente del Pilar', 'a': '2026-10-10', 'b': '2026-10-12',
               'note': 'Puente del Pilar: del sábado 10 al lunes 12 de octubre (Fiesta Nacional de España).'}],
        '11': [{'id': 'navidad', 'chip': 'Navidad y Reyes', 'wh': 'Navidad y Reyes', 'em': 'en Navidad', 'a': '2026-12-19', 'b': '2027-01-06',
                'note': 'Navidad y Reyes: del 19 de diciembre al 6 de enero (el calendario escolar varía según la comunidad autónoma).'},
               {'id': 'puente', 'chip': 'Puente de diciembre', 'wh': 'puente de diciembre', 'em': 'en el puente de diciembre', 'a': '2026-12-05', 'b': '2026-12-08',
                'note': 'Puente de la Constitución y la Inmaculada: del sábado 5 al martes 8 de diciembre.'}],
        '2': [{'id': 'semanasanta', 'chip': 'Semana Santa', 'wh': 'Semana Santa', 'em': 'en Semana Santa', 'a': '2027-03-20', 'b': '2027-03-29',
               'note': 'Semana Santa 2027: del sábado 20 al lunes de Pascua 29 de marzo (el calendario escolar varía según la comunidad autónoma).'}],
    },
    'zones': {},
    't': {
        'h1_month': '¿Dónde ir en <em>{m}</em>?', 'h1_other': '¿Dónde ir <em>{x}</em>?', 'h1_dates': '¿Dónde ir <em>{x}</em>?',
        'your_dates': 'en tus fechas', 'when': '<b>Del {a} al {b}</b>: {n} días.', 'n_days': '{n} días',
        'sub_month': 'Ranking calculado día a día sobre 2016-2025 cuando existe el historial diario; si no, con las medias del mes.',
        'sub_dates': 'Ranking calculado para tus fechas exactas.', 'sub_zone': '',
        'all_month': 'Todo {m}', 'zone_chip': 'Zona {z} · {r}',
        'top': 'Top {n} · {uc}{reg} · {where}', 'your_dates_where': 'tus fechas',
        'count': '{k} de los {n} destinos analizados cumplen tus criterios.',
        'count1': '{k} de los {n} destinos analizados cumple tus criterios.',
        'empty': 'Ningún destino coincide. Amplía el tiempo de vuelo o la región, o baja la temperatura pedida.',
        'err_missing': 'Indica una fecha de salida y una de regreso.', 'err_order': 'La fecha de regreso debe ser posterior a la de salida.',
        'err_long': 'Elige una estancia de dos meses como máximo.',
        'f_safe': 'La apuesta más segura', 'f_near': 'La más cercana sin lluvia', 'f_cheap': 'La más barata sin lluvia',
        'f_trap': 'Buen destino, malas fechas', 'f_trap_far': 'Más lejos, la trampa',
        'f_best_ski': 'Mejor puntuación de esquí', 'f_best_rando': 'Mejor puntuación de senderismo', 'f_near_m': 'La más cercana', 'f_cheap_m': 'La más barata',
        'dry_years': 'casi seco {k} años de {n}', 'lt1': 'menos de un día de lluvia de {n}', 'approx_days': '≈ {x} días de lluvia de {n}',
        'fd_safe': '{dry}, {t} °C, ≈ {h} de vuelo.', 'fd_near': '≈ {h} de vuelo desde {dep}, {t} °C, {dry}.',
        'fd_cheap': 'Presupuesto {b}, {t} °C, {dry}.', 'fd_trap': 'Excelente en {bm} ({bs}/10), pero {x} días de lluvia de {n} en estas fechas.',
        'fd_best_m': '{s}/10, de {tn} a {tx} °C, ≈ {h} de vuelo.', 'fd_near_m': '≈ {h} de vuelo desde {dep}, puntuación {s}/10.', 'fd_cheap_m': 'Presupuesto {b}, puntuación {s}/10.',
        'flight': '≈ {h} de vuelo', 'sea': 'Mar {t} °C', 'card': 'Ficha',
        'dry_line': 'Casi seco <b>{k} años de {n}</b> · {x} días de lluvia de {d}', 'approx_line': '{x} (media del mes)',
        'approx_lt1': 'Menos de un día de lluvia de {n}', 'approx_n': '≈ {x} días de lluvia de {n}',
        'ski_line': 'Sol {s} h/día · noches a {tn} °C', 'season_title': '{y}: días de lluvia: {r}',
        'lg_dry': 'Casi seco (como máximo {l} días de lluvia)', 'lg_mid': 'De {a} a {b} días', 'lg_wet': 'Más de {b} días',
        'lg_one_y': 'Una casilla por año (2016 a 2025)', 'lg_one_s': 'Una casilla por temporada (2016-17 a 2024-25)',
        'lg_approx': 'Sin casillas: media del mes (historial diario en recopilación)',
        'mini_rain': '{t} °C · {r} % lluvia', 'see_all': 'Ver todo', 'see': 'Ver', 'none': 'Ningún destino con estos criterios',
        'reg_title': 'Por región · {where}', 'avoid_title': 'Mejor evitar · {where}',
        'avoid_lead': 'Los destinos menos favorables para estas fechas, de los {n} analizados (estaciones de montaña excluidas: ver el ranking de esquí).',
        'fly_any': 'da igual', 'world': 'Todo el mundo', 'err_load': 'No se pudieron cargar los datos. Recarga la página.',
        'other_city': 'Otra ciudad…', 'city_ph': 'Escribe una ciudad (p. ej. Zaragoza, Quito, Montevideo)', 'city_none': 'No se encontró ninguna ciudad.', 'city_err': 'Búsqueda no disponible, inténtalo de nuevo.',
    },
}

I18N_DE = {
    'months': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
    'ms': ['Jan.', 'Feb.', 'März', 'Apr.', 'Mai', 'Juni', 'Juli', 'Aug.', 'Sept.', 'Okt.', 'Nov.', 'Dez.'],
    'wd': ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'],
    'uc': {'gen': '☀️ Allgemeines Wetter', 'plage': '🏖️ Strand', 'ski': '⛷️ Ski', 'rando': '🥾 Wandern'},
    'uc_t': {'gen': 'Allgemeines Wetter', 'plage': 'Strand und Baden', 'ski': 'Berge und Ski', 'rando': 'Wandern'},
    'regions': {'eu': 'Europa', 'af-nord': 'Nordafrika', 'af': 'Afrika und Indischer Ozean', 'atl': 'Atlantikinseln',
                'am-n': 'Nordamerika', 'car': 'Karibik', 'am-s': 'Südamerika', 'as': 'Asien',
                'me': 'Naher Osten', 'oc': 'Ozeanien', 'other': 'Andere Länder'},
    'secu': {'1': '🟢 Normal', '2': '🟡 Erhöht', '3': '🟠 Nicht empfohlen', '4': '🔴 Dringend abgeraten'},
    'budget': {'1': '💚 Günstig', '2': '💛 Erschwinglich', '3': '🟡 Moderat', '4': '🟠 Teuer', '5': '🔴 Sehr teuer'},
    'budget_opts': [[5, 'Alle Budgets'], [2, 'Bis 💛 Erschwinglich'], [3, 'Bis 🟡 Moderat'], [4, 'Bis 🟠 Teuer']],
    'secu_opts': [[4, 'Alle Reiseziele'], [2, 'Bis 🟡 Erhöht'], [1, 'Nur 🟢 Normal']],
    'heat_opts': [[-99, 'Egal'], [16, '16 °C und mehr'], [20, '20 °C und mehr'], [24, '24 °C und mehr']],
    'sorts': {'score': 'BestDateWeather-Score', 'dry': 'Am sichersten (wenig Regen)', 'hot': 'Am wärmsten',
              'near': 'Am nächsten', 'cheap': 'Am günstigsten vor Ort'},
    'deps': [['Berlin', 52.52, 13.40], ['Hamburg', 53.55, 9.99], ['München', 48.14, 11.58], ['Köln', 50.94, 6.96],
             ['Frankfurt', 50.11, 8.68], ['Stuttgart', 48.78, 9.18], ['Düsseldorf', 51.23, 6.77], ['Leipzig', 51.34, 12.37],
             ['Wien', 48.21, 16.37], ['Zürich', 47.37, 8.54]],
    'holidays': {
        '11': [{'id': 'weihnachten', 'chip': 'Weihnachten und Neujahr', 'wh': 'Weihnachten und Neujahr', 'em': 'über Weihnachten', 'a': '2026-12-19', 'b': '2027-01-03',
                'note': 'Weihnachten und Neujahr: 19. Dezember bis 3. Januar (Schulferien je nach Bundesland bzw. Kanton verschieden).'}],
        '2': [{'id': 'ostern', 'chip': 'Ostern', 'wh': 'Ostern', 'em': 'über Ostern', 'a': '2027-03-26', 'b': '2027-03-29',
               'note': 'Ostern 2027: Karfreitag, 26. März, bis Ostermontag, 29. März.'}],
        '4': [{'id': 'himmelfahrt', 'chip': 'Christi Himmelfahrt', 'wh': 'Christi Himmelfahrt', 'em': 'an Christi Himmelfahrt', 'a': '2027-05-06', 'b': '2027-05-09',
               'note': 'Christi Himmelfahrt 2027: Donnerstag, 6. Mai, bis Sonntag, 9. Mai (mit Brückentag).'},
              {'id': 'pfingsten', 'chip': 'Pfingsten', 'wh': 'Pfingsten', 'em': 'an Pfingsten', 'a': '2027-05-15', 'b': '2027-05-17',
               'note': 'Pfingsten 2027: Samstag, 15. Mai, bis Pfingstmontag, 17. Mai.'}],
    },
    'zones': {},
    't': {
        'h1_month': 'Wohin im <em>{m}</em>?', 'h1_other': 'Wohin <em>{x}</em>?', 'h1_dates': 'Wohin <em>{x}</em>?',
        'your_dates': 'zu Ihren Reisedaten', 'when': '<b>{a} bis {b}</b>, also {n} Tage.', 'n_days': '{n} Tage',
        'sub_month': 'Ranking Tag für Tag über 2016-2025 berechnet, wo Tagesdaten vorliegen, sonst nach Monatsmitteln.',
        'sub_dates': 'Ranking für Ihre genauen Reisedaten berechnet.', 'sub_zone': '',
        'all_month': 'Ganzer {m}', 'zone_chip': 'Zone {z} · {r}',
        'top': 'Top {n} · {uc}{reg} · {where}', 'your_dates_where': 'Ihre Reisedaten',
        'count': '{k} von {n} analysierten Reisezielen erfüllen Ihre Kriterien.',
        'count1': '{k} von {n} analysierten Reisezielen erfüllt Ihre Kriterien.',
        'empty': 'Kein Reiseziel passt. Erhöhen Sie die Flugzeit, erweitern Sie die Region oder senken Sie die gewünschte Temperatur.',
        'err_missing': 'Geben Sie ein Abreise- und ein Rückreisedatum ein.', 'err_order': 'Das Rückreisedatum muss nach dem Abreisedatum liegen.',
        'err_long': 'Wählen Sie einen Aufenthalt von höchstens zwei Monaten.',
        'f_safe': 'Die sicherste Wahl', 'f_near': 'Am nächsten und trocken', 'f_cheap': 'Am günstigsten und trocken',
        'f_trap': 'Gutes Ziel, falsche Daten', 'f_trap_far': 'Weiter weg, die Falle',
        'f_best_ski': 'Bester Ski-Score', 'f_best_rando': 'Bester Wander-Score', 'f_near_m': 'Am nächsten', 'f_cheap_m': 'Am günstigsten',
        'dry_years': 'fast trocken in {k} von {n} Jahren', 'lt1': 'weniger als ein Regentag von {n}', 'approx_days': '≈ {x} Regentage von {n}',
        'fd_safe': '{dry}, {t} °C, ≈ {h} Flug.', 'fd_near': '≈ {h} Flug ab {dep}, {t} °C, {dry}.',
        'fd_cheap': 'Budget {b}, {t} °C, {dry}.', 'fd_trap': 'Hervorragend im {bm} ({bs}/10), aber {x} Regentage von {n} zu diesen Daten.',
        'fd_best_m': '{s}/10, {tn} bis {tx} °C, ≈ {h} Flug.', 'fd_near_m': '≈ {h} Flug ab {dep}, Score {s}/10.', 'fd_cheap_m': 'Budget {b}, Score {s}/10.',
        'flight': '≈ {h} Flug', 'sea': 'Meer {t} °C', 'card': 'Details',
        'dry_line': 'Fast trocken in <b>{k} von {n} Jahren</b> · {x} Regentage von {d}', 'approx_line': '{x} (Monatsmittel)',
        'approx_lt1': 'Weniger als ein Regentag von {n}', 'approx_n': '≈ {x} Regentage von {n}',
        'ski_line': 'Sonne {s} Std./Tag · Nächte bei {tn} °C', 'season_title': '{y}: Regentage: {r}',
        'lg_dry': 'Fast trocken (höchstens {l} Regentage)', 'lg_mid': '{a} bis {b} Tage', 'lg_wet': 'Mehr als {b} Tage',
        'lg_one_y': 'Ein Feld pro Jahr (2016 bis 2025)', 'lg_one_s': 'Ein Feld pro Saison (2016-17 bis 2024-25)',
        'lg_approx': 'Ohne Felder: Monatsmittel (Tagesdaten werden noch erfasst)',
        'mini_rain': '{t} °C · {r} % Regen', 'see_all': 'Alle ansehen', 'see': 'Ansehen', 'none': 'Kein Reiseziel mit diesen Kriterien',
        'reg_title': 'Nach Region · {where}', 'avoid_title': 'Besser meiden · {where}',
        'avoid_lead': 'Die ungünstigsten Reiseziele für diese Daten, von {n} analysierten (Bergorte ausgenommen: siehe Ski-Ranking).',
        'fly_any': 'egal', 'world': 'Weltweit', 'err_load': 'Die Daten konnten nicht geladen werden. Bitte laden Sie die Seite neu.',
        'other_city': 'Andere Stadt…', 'city_ph': 'Stadt eingeben (z. B. Bremen, Graz, Basel)', 'city_none': 'Keine Stadt gefunden.', 'city_err': 'Suche nicht verfügbar, bitte erneut versuchen.',
    },
}

US_HEAT = [[-99, 'Any'], [15.56, '60 °F and above'], [20, '68 °F and above'], [23.89, '75 °F and above']]
US_DEPS = [['New York', 40.71, -74.01], ['Los Angeles', 34.05, -118.24], ['Chicago', 41.88, -87.63], ['Houston', 29.76, -95.37],
           ['Dallas', 32.78, -96.80], ['Atlanta', 33.75, -84.39], ['Miami', 25.76, -80.19], ['Washington', 38.91, -77.04],
           ['Boston', 42.36, -71.06], ['San Francisco', 37.77, -122.42], ['Seattle', 47.61, -122.33], ['Denver', 39.74, -104.99]]
US_HOLIDAYS = {
    '10': [{'id': 'thanksgiving', 'chip': 'Thanksgiving', 'wh': 'Thanksgiving', 'em': 'for Thanksgiving', 'a': '2026-11-25', 'b': '2026-11-29',
            'note': 'Thanksgiving is Thursday, November 26, 2026: Wednesday to Sunday.'}],
    '11': [{'id': 'christmas', 'chip': 'Christmas and New Year', 'wh': 'Christmas and New Year', 'em': 'for Christmas', 'a': '2026-12-19', 'b': '2027-01-03',
            'note': 'Christmas and New Year: December 19 to January 3 (winter break dates vary by school district).'}],
    '1': [{'id': 'presidents', 'chip': "Presidents' Day weekend", 'wh': "Presidents' Day weekend", 'em': "for Presidents' Day weekend", 'a': '2027-02-13', 'b': '2027-02-15',
           'note': "Presidents' Day is Monday, February 15, 2027: Saturday to Monday."}],
    '4': [{'id': 'memorial', 'chip': 'Memorial Day weekend', 'wh': 'Memorial Day weekend', 'em': 'for Memorial Day weekend', 'a': '2027-05-29', 'b': '2027-05-31',
           'note': 'Memorial Day is Monday, May 31, 2027: Saturday to Monday.'}],
    '6': [{'id': 'july', 'chip': 'Fourth of July weekend', 'wh': 'Fourth of July weekend', 'em': 'for the Fourth of July', 'a': '2027-07-02', 'b': '2027-07-05',
           'note': 'Independence Day falls on Sunday, July 4, 2027 (observed Monday, July 5): Friday to Monday.'}],
    '8': [{'id': 'labor', 'chip': 'Labor Day weekend', 'wh': 'Labor Day weekend', 'em': 'for Labor Day weekend', 'a': '2027-09-04', 'b': '2027-09-06',
           'note': 'Labor Day is Monday, September 6, 2027: Saturday to Monday.'}],
}


def us_i18n(en):
    d = copy.deepcopy(en)
    d['t'] = _us_dict(en['t'])
    d['t']['city_ph'] = 'Type a city (e.g. Austin, Portland, Toronto)'
    d['heat_opts'] = copy.deepcopy(US_HEAT)
    d['deps'] = copy.deepcopy(US_DEPS)
    d['holidays'] = copy.deepcopy(US_HOLIDAYS)
    d['zones'] = {}
    return d


# ── Textes de page (generate_moteur_mois.TEXTS) ──────────────────────────────

TEXTS_ES = {
    'eyebrow': 'Estudio climático · 10 años de datos · 2026-2027', 'months_label': 'Otros meses', 'criteria': 'Criterios',
    'your_dates': 'Tus fechas', 'dep_date': 'Salida', 'ret_date': 'Regreso', 'shortcuts': 'Atajos:',
    'zone_label': 'Zona', 'trip_type': 'Tipo de viaje', 'region': 'Región', 'from_city': 'Ciudad de salida',
    'max_flight': 'Tiempo de vuelo máximo:', 'heat': 'Temperatura por la tarde', 'budget': 'Presupuesto en destino',
    'budget_help': 'Coste de la vida por país (índice Numbeo 2026). El vuelo no está incluido.',
    'safety': 'Seguridad',
    'safety_help': 'Nivel del país (el más prudente entre los ministerios de Asuntos Exteriores de Francia y de Alemania). Algunas regiones pueden tener un nivel más severo: compruébalo antes de reservar.',
    'key_points': 'Lo esencial', 'sort_by': 'Ordenar por', 'more': 'Mostrar 25 más',
    'projects_title': 'Según tu plan',
    'projects_lead': 'Los mejores destinos para estas fechas, por tipo de viaje (ciudad de salida, vuelo, presupuesto y seguridad incluidos).',
    'regions_lead': 'Los mejores destinos de cada región para estas fechas (presupuesto y seguridad incluidos, sin límite de vuelo).',
    'others_title': 'Otros rankings',
    'method_title': 'Cómo se calcula este ranking',
    'method': [
        'Puntuación BestDateWeather (general, playa, esquí o senderismo): la de los meses del viaje, ponderada por el número de días de tu estancia en cada mes.',
        'Lluvia: cuando existe el historial diario, tus fechas exactas se repiten en cada año de 2016 a 2025 (reanálisis ERA5, umbral ajustado con 318 estaciones meteorológicas). Si no, el cálculo parte de la proporción de días de lluvia del mes.',
        '«Casi seco»: como máximo un día de lluvia por semana de viaje, de media.',
        'Atajos de fechas: festivos nacionales de España; el calendario escolar varía según la comunidad autónoma.',
    ],
    'know_title': 'Lo que conviene saber',
    'know': [
        'Diez temporadas son un historial corto: «8 años de 10» significa «la mayoría de las veces», no «garantizado».',
        'Tiempo de vuelo estimado a partir de la distancia (45 min + distancia a 850 km/h), para un vuelo directo. Con escala, cuenta más.',
        'Temperaturas del reanálisis ERA5: en islas pequeñas, a veces de 1 a 2 °C por debajo de las estaciones costeras.',
    ],
    'holiday_title': '{chip}: ¿dónde ir al sol?',
    'holiday_lead': 'Del {a} al {b}. Las mejores puntuaciones con 20 °C o más y como máximo un 15 % de días de lluvia en estas fechas (seguridad: hasta nivel reforzado).',
    'holiday_cta': 'Ver el ranking completo para estas fechas',
    'zone_h3': 'Zona {z} · {r}', 'see_all_short': 'Ranking', 'zone_list': '{list}.', 'zone_lead': '',
    'title_z': '¿Dónde ir en {m} de {y}? Top 25 destinos por clima', 'desc_z': '', 'faq_a2_zone': 'Zona {z} (del {a} al {b}): {l}.',
    'title_m': '¿Dónde ir en {m} de {y}? Top 25 destinos por clima, día a día',
    'title_h': '¿Dónde ir en {m} de {y} y {em}? Top 25 destinos por clima',
    'desc': 'Ranking de {n} destinos para {m} de {y}{h}: n.º 1 {top} ({s}/10, {t} °C). Cálculo día a día sobre 2016-2025, filtros de fechas, vuelo, presupuesto y seguridad.',
    'desc_h': ' y {em}', 'crumb': 'Dónde ir en {m}',
    'faq_q1': '¿Cuál es el mejor destino en {m}?', 'faq_a1': '{top} encabeza el ranking de {m} con {s}/10 y {t} °C de media por la tarde.',
    'faq_q2': '¿Dónde ir al sol {em}?', 'faq_a2': 'Del {a} al {b}, los mejores destinos con 20 °C o más y poca lluvia son {l}.',
    'prev': '← Dónde ir en {m}', 'next': 'Dónde ir en {m} →', 'world': '🌍 Ranking mundial 2026', 'map': '🗺️ Mapa climático', 'year': '📅 Todo el año',
    'and': ' y ',
}

TEXTS_DE = {
    'eyebrow': 'Klimastudie · 10 Jahre Daten · 2026-2027', 'months_label': 'Andere Monate', 'criteria': 'Kriterien',
    'your_dates': 'Ihre Reisedaten', 'dep_date': 'Abreise', 'ret_date': 'Rückreise', 'shortcuts': 'Schnellauswahl:',
    'zone_label': 'Zone', 'trip_type': 'Reiseart', 'region': 'Region', 'from_city': 'Abflugort',
    'max_flight': 'Maximale Flugzeit:', 'heat': 'Temperatur am Nachmittag', 'budget': 'Budget vor Ort',
    'budget_help': 'Lebenshaltungskosten pro Land (Numbeo-Index 2026). Flugkosten nicht enthalten.',
    'safety': 'Sicherheit',
    'safety_help': 'Stufe des Landes (die strengere von französischem Außenministerium und Auswärtigem Amt). Einzelne Regionen können strenger eingestuft sein: Prüfen Sie dies vor der Buchung.',
    'key_points': 'Das Wichtigste', 'sort_by': 'Sortieren nach', 'more': '25 weitere anzeigen',
    'projects_title': 'Je nach Reiseart',
    'projects_lead': 'Die besten Reiseziele für diese Daten, nach Reiseart (Abflugort, Flugzeit, Budget und Sicherheit berücksichtigt).',
    'regions_lead': 'Die besten Reiseziele jeder Region für diese Daten (Budget und Sicherheit berücksichtigt, ohne Flugzeitgrenze).',
    'others_title': 'Weitere Rankings',
    'method_title': 'So wird dieses Ranking berechnet',
    'method': [
        'BestDateWeather-Score (allgemein, Strand, Ski oder Wandern): der Score der betroffenen Monate, gewichtet nach der Zahl Ihrer Reisetage in jedem Monat.',
        'Regen: Wo Tagesdaten vorliegen, werden Ihre genauen Reisedaten in jedem Jahr von 2016 bis 2025 nachgerechnet (ERA5-Reanalyse, Schwelle an 318 Wetterstationen angepasst). Sonst dient der Anteil der Regentage des Monats als Grundlage.',
        '„Fast trocken“: im Schnitt höchstens ein Regentag pro Reisewoche.',
        'Schnellauswahl: gesetzliche Feiertage in Deutschland; Schulferien unterscheiden sich je nach Bundesland bzw. Kanton.',
    ],
    'know_title': 'Gut zu wissen',
    'know': [
        'Zehn Jahre sind eine kurze Datenreihe: „8 von 10 Jahren“ heißt „meistens“, nicht „garantiert“.',
        'Flugzeit aus der Entfernung geschätzt (45 Min. + Strecke bei 850 km/h), für einen Direktflug. Mit Umstieg dauert es länger.',
        'Temperaturen aus der ERA5-Reanalyse: auf kleinen Inseln teils 1 bis 2 °C unter den Werten der Küstenstationen.',
    ],
    'holiday_title': '{chip}: wohin in die Sonne?',
    'holiday_lead': '{a} bis {b}. Die besten Scores bei 20 °C und mehr, mit höchstens 15 % Regentagen zu diesen Daten (Sicherheit: bis Stufe „Erhöht“).',
    'holiday_cta': 'Vollständiges Ranking für diese Daten ansehen',
    'zone_h3': 'Zone {z} · {r}', 'see_all_short': 'Ranking', 'zone_list': '{list}.', 'zone_lead': '',
    'title_z': 'Wohin im {m} {y}? Top 25 Reiseziele nach Wetter', 'desc_z': '', 'faq_a2_zone': 'Zone {z} ({a} bis {b}): {l}.',
    'title_m': 'Wohin im {m} {y}? Top 25 Reiseziele nach Wetter, Tag für Tag',
    'title_h': 'Wohin im {m} {y} und {em}? Top 25 Reiseziele nach Wetter',
    'desc': 'Ranking von {n} Reisezielen für {m} {y}{h}: Nr. 1 {top} ({s}/10, {t} °C). Tag für Tag über 2016-2025 berechnet, mit Filtern für Daten, Flug, Budget und Sicherheit.',
    'desc_h': ' und {em}', 'crumb': 'Wohin im {m}',
    'faq_q1': 'Was ist das beste Reiseziel im {m}?', 'faq_a1': '{top} liegt im {m} vorn, mit {s}/10 und durchschnittlich {t} °C am Nachmittag.',
    'faq_q2': 'Wohin in die Sonne {em}?', 'faq_a2': 'Für {a} bis {b} sind die besten Reiseziele mit 20 °C und mehr und wenig Regen {l}.',
    'prev': '← Wohin im {m}', 'next': 'Wohin im {m} →', 'world': '🌍 Weltranking 2026', 'map': '🗺️ Klimakarte', 'year': '📅 Ganzjährig',
    'and': ' und ',
}


def us_texts(en):
    d = _us_dict(en)
    d['method'] = d['method'] + ['Date shortcuts: US federal holidays; school breaks vary by district.']
    d['know'] = [
        d['know'][0],
        'Flight time estimated from distance (45 min + distance at about 530 mph) for a direct flight. With a stopover, allow longer.',
        'Temperatures come from the ERA5 reanalysis: on small islands they can be 2 to 4 °F below coastal station readings.',
    ]
    d['holiday_lead'] = '{a} to {b}. The best scores at 68 °F and above, with at most 15% rainy days on these dates (safety: up to high vigilance).'
    d['faq_a2'] = 'For {a} to {b}, the best destinations at 68 °F and above with little rain are {l}.'
    return d


# ── Page « toute l'année » : textes de page (ANNUAL_TEXTS) ────────────────────

ANNUAL_TEXTS_ES = {
    'eyebrow': 'Estudio climático · 10 años de datos · 12 meses', 'h1': '¿Dónde ir al sol <em>todo el año</em>?',
    'sub': 'Ranking según la media de los 12 meses y el número de buenos meses (puntuación de 7,6 sobre 10 o más). La franja muestra cada mes de un vistazo.',
    'months_label': 'Meses', 'all_year': 'Todo el año', 'dates_q': '¿Ya tienes fechas?',
    'dates_a': 'Elige arriba el mes de tu salida: cada página mensual calcula tu viaje al día, festivos incluidos.',
    'good_months': 'Buenos meses en el año',
    'by_month_title': 'Mes a mes', 'by_month_lead': 'Los 3 mejores destinos de cada mes (presupuesto y seguridad incluidos). Cada mes tiene su página detallada.',
    'regions_title': 'Por región', 'regions_lead': 'Las mejores puntuaciones anuales de cada región (presupuesto y seguridad incluidos, sin límite de vuelo).',
    'projects_lead': 'Los mejores destinos del año por tipo de viaje. Esquí y senderismo: puntuación del mejor mes.',
    'method': [
        'Puntuación anual: media de las puntuaciones BestDateWeather de los 12 meses (esquí y senderismo: puntuación del mejor mes).',
        'Buen mes: puntuación de 7,6 sobre 10 o más, el nivel «Muy bien» del mapa.',
        'Temperaturas: la más baja y la más alta de las máximas mensuales; lluvia: proporción media de días de lluvia en el año.',
        'Datos: reanálisis ERA5 2016-2025, días de lluvia e insolación ajustados con estaciones meteorológicas.',
    ],
    'title': '¿Dónde ir al sol todo el año? Top 25 destinos por clima en 12 meses',
    'desc': 'Ranking de {n} destinos en los 12 meses: puntuación anual, número de buenos meses y franja mes a mes. N.º 1 {top} ({s}/10, {g} buenos meses de 12). Filtros de vuelo, presupuesto y seguridad.',
    'crumb': 'Todo el año',
    'know': [
        'Una puntuación anual suaviza las estaciones: mira la franja de los 12 meses antes de elegir tus fechas.',
        'Tiempo de vuelo estimado a partir de la distancia (45 min + distancia a 850 km/h), para un vuelo directo. Con escala, cuenta más.',
        'Temperaturas del reanálisis ERA5: en islas pequeñas, a veces de 1 a 2 °C por debajo de las estaciones costeras.',
    ],
    'faq_q1': '¿Qué destino tiene el mejor clima todo el año?', 'faq_a1': '{top}: puntuación anual de {s}/10 y {g} buenos meses de 12.',
    'faq_q2': '¿Dónde ir al sol todo el año en Europa?', 'faq_a2': '{top}: {g} buenos meses de 12, con máximas de {t1} a {t2} °C según el mes.',
    'nomads': '💻 Ranking nómadas digitales', 'world': '🌍 Ranking mundial 2026', 'map': '🗺️ Mapa climático',
}

ANNUAL_TEXTS_DE = {
    'eyebrow': 'Klimastudie · 10 Jahre Daten · 12 Monate', 'h1': 'Wohin das <em>ganze Jahr</em> in die Sonne?',
    'sub': 'Ranking nach dem Mittel der 12 Monate und der Zahl guter Monate (Score ab 7,6 von 10). Die Leiste zeigt jeden Monat auf einen Blick.',
    'months_label': 'Monate', 'all_year': 'Ganzjährig', 'dates_q': 'Sie haben schon Reisedaten?',
    'dates_a': 'Wählen Sie oben Ihren Abreisemonat: Jede Monatsseite berechnet Ihre Reise tagesgenau, Feiertage inklusive.',
    'good_months': 'Gute Monate im Jahr',
    'by_month_title': 'Monat für Monat', 'by_month_lead': 'Die 3 besten Reiseziele jedes Monats (Budget und Sicherheit berücksichtigt). Jeder Monat hat seine eigene Seite.',
    'regions_title': 'Nach Region', 'regions_lead': 'Die besten Jahres-Scores jeder Region (Budget und Sicherheit berücksichtigt, ohne Flugzeitgrenze).',
    'projects_lead': 'Die besten Reiseziele übers Jahr nach Reiseart. Ski und Wandern: Score des besten Monats.',
    'method': [
        'Jahres-Score: Mittel der BestDateWeather-Scores der 12 Monate (Ski und Wandern: Score des besten Monats).',
        'Guter Monat: Score ab 7,6 von 10, die Stufe „Sehr gut“ der Karte.',
        'Temperaturen: niedrigstes und höchstes monatliches Tagesmaximum; Regen: mittlerer Anteil der Regentage im Jahr.',
        'Daten: ERA5-Reanalyse 2016-2025, Regentage und Sonnenstunden an Wetterstationen angepasst.',
    ],
    'title': 'Wohin das ganze Jahr in die Sonne? Top 25 Reiseziele nach Wetter über 12 Monate',
    'desc': 'Ranking von {n} Reisezielen über 12 Monate: Jahres-Score, Zahl guter Monate und Monatsleiste. Nr. 1 {top} ({s}/10, {g} gute Monate von 12). Filter für Flug, Budget und Sicherheit.',
    'crumb': 'Ganzjährig',
    'know': [
        'Ein Jahres-Score glättet die Jahreszeiten: Prüfen Sie die Leiste der 12 Monate, bevor Sie Ihre Reisedaten wählen.',
        'Flugzeit aus der Entfernung geschätzt (45 Min. + Strecke bei 850 km/h), für einen Direktflug. Mit Umstieg dauert es länger.',
        'Temperaturen aus der ERA5-Reanalyse: auf kleinen Inseln teils 1 bis 2 °C unter den Werten der Küstenstationen.',
    ],
    'faq_q1': 'Welches Reiseziel hat das ganze Jahr das beste Wetter?', 'faq_a1': '{top}: Jahres-Score {s}/10 und {g} gute Monate von 12.',
    'faq_q2': 'Wohin das ganze Jahr in die Sonne in Europa?', 'faq_a2': '{top}: {g} gute Monate von 12, mit Höchstwerten von {t1} bis {t2} °C je nach Monat.',
    'nomads': '💻 Ranking digitale Nomaden', 'world': '🌍 Weltranking 2026', 'map': '🗺️ Klimakarte',
}


def us_annual_texts(en):
    d = _us_dict(en)
    d['know'] = [
        d['know'][0],
        'Flight time estimated from distance (45 min + distance at about 530 mph) for a direct flight. With a stopover, allow longer.',
        'Temperatures come from the ERA5 reanalysis: on small islands they can be 2 to 4 °F below coastal station readings.',
    ]
    return d


# ── Page « toute l'année » : textes du calcul (lib/annual_engine.A18N) ────────

A18N_ES = {
    'mi': ['E', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
    'sorts': {'score': 'Puntuación anual', 'regular': 'Regularidad (buenos meses)', 'near': 'Las más cercanas', 'cheap': 'Las más baratas en destino'},
    'good_opts': [[0, 'Da igual'], [6, '6 meses o más'], [9, '9 meses o más'], [12, 'Los 12 meses']],
    't': {
        'top': 'Top {n} · {uc}{reg} · todo el año',
        'count': '{k} de los {n} destinos analizados cumplen tus criterios.',
        'count1': '{k} de los {n} destinos analizados cumple tus criterios.',
        'empty': 'Ningún destino coincide. Amplía el tiempo de vuelo o la región, o pide menos buenos meses.',
        'f_regular': 'La más regular', 'f_near': 'La más cercana todo el año', 'f_cheap': 'La más barata todo el año',
        'f_europe': 'La mejor en Europa (islas incluidas)', 'f_best': 'La mejor puntuación', 'f_near_m': 'La más cercana', 'f_cheap_m': 'La más barata',
        'fd_regular': '{g} buenos meses de 12, puntuación anual {s}/10, ≈ {h} de vuelo.',
        'fd_near': '≈ {h} de vuelo desde {dep}, {g} buenos meses de 12.',
        'fd_cheap': 'Presupuesto {b}, {g} buenos meses de 12.',
        'fd_europe': '{g} buenos meses de 12, máximas de {t1} a {t2} °C.',
        'fd_best': 'Mejor mes: {bm} ({s}/10), ≈ {h} de vuelo.',
        'good_line': '<b>{g} buenos meses de 12</b> · mejores: {bm}',
        'temps': 'Máximas de {t1} a {t2} °C', 'rain': '≈ {r} % de días de lluvia en el año',
        'score_year': '{s}/10', 'score_best': '{s}/10 en el mejor mes',
        'cell': '{m}: {s}/10', 'flight': '≈ {h} de vuelo', 'card': 'Ficha',
        'lg': ['8,6 o más', '7,6 a 8,5', '6,3 a 7,5', '5 a 6,2', '3,5 a 4,9', 'menos de 3,5'],
        'lg_lead': 'Puntuación del mes:', 'see_all': 'Ver todo', 'see': 'Ver', 'none': 'Ningún destino con estos criterios',
        'month_more': 'Ranking completo', 'fly_any': 'da igual', 'world': 'Todo el mundo', 'err_load': 'No se pudieron cargar los datos. Recarga la página.',
        'other_city': 'Otra ciudad…', 'city_ph': 'Escribe una ciudad (p. ej. Zaragoza, Quito, Montevideo)', 'city_none': 'No se encontró ninguna ciudad.', 'city_err': 'Búsqueda no disponible, inténtalo de nuevo.',
        'mini': '{g}/12 buenos meses',
    },
}

A18N_DE = {
    'mi': ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
    'sorts': {'score': 'Jahres-Score', 'regular': 'Beständigkeit (gute Monate)', 'near': 'Am nächsten', 'cheap': 'Am günstigsten vor Ort'},
    'good_opts': [[0, 'Egal'], [6, '6 Monate und mehr'], [9, '9 Monate und mehr'], [12, 'Alle 12 Monate']],
    't': {
        'top': 'Top {n} · {uc}{reg} · ganzjährig',
        'count': '{k} von {n} analysierten Reisezielen erfüllen Ihre Kriterien.',
        'count1': '{k} von {n} analysierten Reisezielen erfüllt Ihre Kriterien.',
        'empty': 'Kein Reiseziel passt. Erhöhen Sie die Flugzeit, erweitern Sie die Region oder verlangen Sie weniger gute Monate.',
        'f_regular': 'Am beständigsten', 'f_near': 'Am nächsten, ganzjährig', 'f_cheap': 'Am günstigsten, ganzjährig',
        'f_europe': 'Am besten in Europa (inkl. Inseln)', 'f_best': 'Bester Score', 'f_near_m': 'Am nächsten', 'f_cheap_m': 'Am günstigsten',
        'fd_regular': '{g} gute Monate von 12, Jahres-Score {s}/10, ≈ {h} Flug.',
        'fd_near': '≈ {h} Flug ab {dep}, {g} gute Monate von 12.',
        'fd_cheap': 'Budget {b}, {g} gute Monate von 12.',
        'fd_europe': '{g} gute Monate von 12, Höchstwerte von {t1} bis {t2} °C.',
        'fd_best': 'Bester Monat: {bm} ({s}/10), ≈ {h} Flug.',
        'good_line': '<b>{g} gute Monate von 12</b> · am besten: {bm}',
        'temps': 'Höchstwerte von {t1} bis {t2} °C', 'rain': '≈ {r} % Regentage im Jahr',
        'score_year': '{s}/10', 'score_best': '{s}/10 im besten Monat',
        'cell': '{m}: {s}/10', 'flight': '≈ {h} Flug', 'card': 'Details',
        'lg': ['8,6 und mehr', '7,6 bis 8,5', '6,3 bis 7,5', '5 bis 6,2', '3,5 bis 4,9', 'unter 3,5'],
        'lg_lead': 'Score des Monats:', 'see_all': 'Alle ansehen', 'see': 'Ansehen', 'none': 'Kein Reiseziel mit diesen Kriterien',
        'month_more': 'Vollständiges Ranking', 'fly_any': 'egal', 'world': 'Weltweit', 'err_load': 'Die Daten konnten nicht geladen werden. Bitte laden Sie die Seite neu.',
        'other_city': 'Andere Stadt…', 'city_ph': 'Stadt eingeben (z. B. Bremen, Graz, Basel)', 'city_none': 'Keine Stadt gefunden.', 'city_err': 'Suche nicht verfügbar, bitte erneut versuchen.',
        'mini': '{g}/12 gute Monate',
    },
}


def us_a18n(en):
    d = copy.deepcopy(en)
    d['t'] = _us_dict(en['t'])
    d['t']['city_ph'] = 'Type a city (e.g. Austin, Portland, Toronto)'
    return d
