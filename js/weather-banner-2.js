/* Reconstructed from weather-banner-2.min.js — source original perdu */
! function() {
  "use strict";
  var e = "bdw_banner_city",
    t = "bdw_recent",
    n = document.documentElement.lang,
    a = "en" === n || "en-US" === n ? "en" : "es" === n ? "es" : "de" === n ? "de" : "fr",
    i = {
      fr: {
        now: "Maint.",
        feels: "Ressenti",
        wind: "Vent",
        uv: "UV",
        chosenCity: "ville choisie",
        changeCity: "Changer de ville",
        approxLabel: "approx.",
        cityTitle: "Ville du bandeau météo",
        typeCity: "Tapez une ville…",
        usePosition: "Utiliser ma position",
        currently: "Actuellement",
        recentTitle: "Recherches récentes",
        clearAll: "Tout effacer",
        rankingTitle: "Où partir ?",
        rankingUrl: "/meilleures-destinations-meteo.html",
        suggestTitle: "Pour vous",
        suggestSub: "même région climatique",
        suggestTitleDynamic: "Meilleurs mois ·",
        lang: "fr",
        geoPrompt: "Où êtes-vous ? Entrez votre ville pour la météo locale",
        geoPlaceholder: "Votre ville…",
        geoAllow: "Autoriser",
        geoSkip: "Plus tard",
        annual: "12 mois",
        date: "date",
        share: "Partager",
        weatherDesc: {
          0: "Ciel dégagé",
          1: "Peu nuageux",
          2: "Partiellement nuageux",
          3: "Couvert",
          45: "Brouillard",
          48: "Brouillard givrant",
          51: "Bruine légère",
          53: "Bruine modérée",
          55: "Bruine forte",
          61: "Pluie légère",
          63: "Pluie modérée",
          65: "Pluie forte",
          71: "Neige légère",
          73: "Neige modérée",
          75: "Neige forte",
          80: "Averses légères",
          81: "Averses modérées",
          82: "Averses fortes",
          95: "Orage",
          96: "Orage + grêle",
          99: "Orage + grêle forte"
        }
      },
      en: {
        now: "Now",
        feels: "Feels",
        wind: "Wind",
        uv: "UV",
        chosenCity: "chosen city",
        changeCity: "Change city",
        approxLabel: "approx.",
        cityTitle: "Banner weather city",
        typeCity: "Type a city…",
        usePosition: "Use my location",
        currently: "Currently",
        recentTitle: "Recent searches",
        clearAll: "Clear all",
        rankingTitle: "Where to go?",
        rankingUrl: "/en/best-weather-destinations.html",
        suggestTitle: "For you",
        suggestSub: "similar climate region",
        suggestTitleDynamic: "Best months ·",
        lang: "en",
        geoPrompt: "Where are you? Enter your city for local weather",
        geoPlaceholder: "Your city…",
        geoAllow: "Allow",
        geoSkip: "Later",
        annual: "12 months",
        date: "date",
        share: "Share",
        weatherDesc: {
          0: "Clear sky",
          1: "Mainly clear",
          2: "Partly cloudy",
          3: "Overcast",
          45: "Foggy",
          48: "Rime fog",
          51: "Light drizzle",
          53: "Drizzle",
          55: "Heavy drizzle",
          61: "Light rain",
          63: "Rain",
          65: "Heavy rain",
          71: "Light snow",
          73: "Snow",
          75: "Heavy snow",
          80: "Light showers",
          81: "Showers",
          82: "Heavy showers",
          95: "Thunderstorm",
          96: "Storm + hail",
          99: "Storm + heavy hail"
        }
      },
      es: {
        now: "Ahora",
        feels: "Sensación",
        wind: "Viento",
        uv: "UV",
        chosenCity: "ciudad elegida",
        changeCity: "Cambiar de ciudad",
        approxLabel: "aprox.",
        cityTitle: "Ciudad del banner meteorológico",
        typeCity: "Escribe una ciudad…",
        usePosition: "Usar mi ubicación",
        currently: "Actualmente",
        recentTitle: "Búsquedas recientes",
        clearAll: "Borrar todo",
        rankingTitle: "¿Dónde ir?",
        rankingUrl: "/es/mejores-destinos-climaticos.html",
        suggestTitle: "Para ti",
        suggestSub: "región climática similar",
        suggestTitleDynamic: "Mejores meses ·",
        lang: "es",
        geoPrompt: "¿Dónde estás? Introduce tu ciudad para el tiempo local",
        geoPlaceholder: "Tu ciudad…",
        geoAllow: "Permitir",
        geoSkip: "Más tarde",
        annual: "12 meses",
        date: "fecha",
        share: "Compartir",
        weatherDesc: {
          0: "Cielo despejado",
          1: "Mayormente despejado",
          2: "Parcialmente nublado",
          3: "Cubierto",
          45: "Niebla",
          48: "Niebla engelante",
          51: "Llovizna ligera",
          53: "Llovizna",
          55: "Llovizna intensa",
          61: "Lluvia ligera",
          63: "Lluvia",
          65: "Lluvia intensa",
          71: "Nieve ligera",
          73: "Nieve",
          75: "Nieve intensa",
          80: "Chubascos ligeros",
          81: "Chubascos",
          82: "Chubascos fuertes",
          95: "Tormenta",
          96: "Tormenta + granizo",
          99: "Tormenta + granizo fuerte"
        }
      },
      de: {
        now: "Jetzt",
        feels: "Gefühlt",
        wind: "Wind",
        uv: "UV",
        chosenCity: "gewählte Stadt",
        changeCity: "Stadt ändern",
        approxLabel: "ca.",
        cityTitle: "Stadt für Wetterbanner",
        typeCity: "Stadt eingeben…",
        usePosition: "Meinen Standort verwenden",
        currently: "Aktuell",
        recentTitle: "Letzte Suchen",
        clearAll: "Alle löschen",
        rankingTitle: "Wohin reisen?",
        rankingUrl: "/de/beste-reiseziele-klima.html",
        suggestTitle: "Für Sie",
        suggestSub: "ähnliche Klimazone",
        suggestTitleDynamic: "Beste Monate ·",
        lang: "de",
        geoPrompt: "Wo sind Sie? Geben Sie Ihre Stadt für das lokale Wetter ein",
        geoPlaceholder: "Ihre Stadt…",
        geoAllow: "Erlauben",
        geoSkip: "Später",
        annual: "12 Monate",
        date: "Datum",
        share: "Teilen",
        weatherDesc: {
          0: "Klarer Himmel",
          1: "Überwiegend klar",
          2: "Teilweise bewölkt",
          3: "Bedeckt",
          45: "Nebel",
          48: "Gefrierender Nebel",
          51: "Leichter Nieselregen",
          53: "Nieselregen",
          55: "Starker Nieselregen",
          61: "Leichter Regen",
          63: "Regen",
          65: "Starker Regen",
          71: "Leichter Schnee",
          73: "Schnee",
          75: "Starker Schnee",
          80: "Leichte Schauer",
          81: "Schauer",
          82: "Starke Schauer",
          95: "Gewitter",
          96: "Gewitter + Hagel",
          99: "Gewitter + starker Hagel"
        }
      }
    } [a];

  function r(e, t) {
    return 0 === e ? t ? "🌙" : "☀️" : e <= 2 ? t ? "🌙" : "⛅" : 3 === e ? "☁️" : e <= 48 ? "🌫️" : e <= 55 ? "🌦️" : e <= 65 ? "🌧️" : e <= 75 ? "❄️" : e <= 82 ? "🌧️" : "⛈️"
  }

  function o(e) {
    return e >= 7 ? "var(--green)" : e >= 4 ? "#b8860b" : "#c0392b"
  }

  function l(e) {
    return e >= 7 ? "var(--green-bg)" : e >= 4 ? "#fff8e1" : "#fde8e8"
  }

  function s(e) {
    try {
      var t = localStorage.getItem(e);
      return t ? JSON.parse(t) : null
    } catch (e) {
      return null
    }
  }

  function c(e, t) {
    try {
      localStorage.setItem(e, JSON.stringify(t))
    } catch (e) {}
  }
  var d = {
    weather: null,
    hourlyOpen: !1,
    cityModalOpen: !1,
    geoState: "init",
    citySource: "geo"
  };

  function u(t, n) {
    fetch("https://nominatim.openstreetmap.org/reverse?lat=" + t + "&lon=" + n + "&format=json&zoom=10&accept-language=" + a).then(function(e) {
      return e.json()
    }).then(function(a) {
      var i = "Ma position";
      a && a.address && (i = a.address.city || a.address.town || a.address.village || a.address.municipality || a.address.county || "Position"), c(e, {
        name: i,
        lat: t,
        lon: n,
        source: "geo"
      }), g(t, n, i, "geo")
    }).catch(function() {
      g(t, n, t.toFixed(2) + ", " + n.toFixed(2), "geo")
    })
  }

  function g(e, t, n, a) {
    fetch("https://api.open-meteo.com/v1/forecast?latitude=" + e + "&longitude=" + t + "&hourly=temperature_2m,weather_code,wind_speed_10m,precipitation_probability,is_day&daily=temperature_2m_max,temperature_2m_min&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,uv_index,relative_humidity_2m,is_day&timezone=auto&forecast_days=1").then(function(e) {
      return e.json()
    }).then(function(e) {
      if (!e || !e.current) throw new Error("No data");
      for (var t = e.current, o = [], l = (new Date).getHours(), s = e.hourly.temperature_2m || [], c = e.hourly.weather_code || [], u = e.hourly.wind_speed_10m || [], g = e.hourly.precipitation_probability || [], h = e.hourly.is_day || [], m = l; m < Math.min(l + 12, s.length); m++) {
        var p = m === l ? i.now : m + "h";
        o.push({
          h: p,
          temp: s[m],
          icon: r(c[m] || 0, h[m] === 0),
          wind: u[m] || 0,
          rain: Math.round(g[m] || 0)
        })
      }
      var w = null,
        v = null;
      e.daily && (e.daily.temperature_2m_max && e.daily.temperature_2m_max.length && (v = e.daily.temperature_2m_max[0]), e.daily.temperature_2m_min && e.daily.temperature_2m_min.length && (w = e.daily.temperature_2m_min[0])), d.weather = {
        city: n,
        temp: t.temperature_2m,
        tMin: w,
        tMax: v,
        feels: t.apparent_temperature,
        wind: t.wind_speed_10m,
        icon: r(t.weather_code, t.is_day === 0),
        desc: i.weatherDesc[t.weather_code] || i.weatherDesc[0],
        humidity: Math.round(t.relative_humidity_2m || 0),
        uv: Math.round(t.uv_index || 0),
        source: a,
        hourly: o
      }, _(), x(), F()
    }).catch(function(e) {
      console.warn("[WB] Fetch error:", e), d.geoState = "denied", k()
    })
  }
  var m = null,
    p = {
      fr: {
        GF: "Guyane française",
        GP: "Guadeloupe",
        MQ: "Martinique",
        RE: "La Réunion",
        PM: "Saint-Pierre-et-Miquelon",
        YT: "Mayotte",
        NC: "Nouvelle-Calédonie",
        PF: "Polynésie française"
      },
      en: {
        GF: "French Guiana",
        GP: "Guadeloupe",
        MQ: "Martinique",
        RE: "Réunion",
        PM: "Saint Pierre and Miquelon",
        YT: "Mayotte",
        NC: "New Caledonia",
        PF: "French Polynesia"
      },
      es: {
        GF: "Guayana Francesa",
        GP: "Guadalupe",
        MQ: "Martinica",
        RE: "Reunión",
        PM: "San Pedro y Miquelón",
        YT: "Mayotte",
        NC: "Nueva Caledonia",
        PF: "Polinesia Francesa"
      },
      de: {
        GF: "Französisch-Guayana",
        GP: "Guadeloupe",
        MQ: "Martinique",
        RE: "Réunion",
        PM: "Saint-Pierre und Miquelon",
        YT: "Mayotte",
        NC: "Neukaledonien",
        PF: "Französisch-Polynesien"
      }
    },
    w = {
      fr: "France",
      en: "France",
      es: "Francia",
      de: "Frankreich"
    },
    v = {
      de: {
        GB: "Vereinigtes Königreich",
        US: "Vereinigte Staaten",
        AU: "Australien",
        NZ: "Neuseeland",
        AE: "Vereinigte Arabische Emirate",
        ZA: "Südafrika",
        MX: "Mexiko",
        AR: "Argentinien",
        CL: "Chile",
        BR: "Brasilien",
        TH: "Thailand",
        VN: "Vietnam",
        PH: "Philippinen",
        JP: "Japan",
        CN: "China",
        IN: "Indien",
        TR: "Türkei",
        EG: "Ägypten",
        MA: "Marokko",
        TZ: "Tansania",
        KE: "Kenia",
        MZ: "Mosambik",
        MU: "Mauritius",
        MV: "Malediven",
        LK: "Sri Lanka",
        CD: "Demokratische Republik Kongo",
        CG: "Republik Kongo"
      }
    };

  function h(e) {
    var t = e.country_code || "",
      n = "en" === a ? "en" : "es" === a ? "es" : "de" === a ? "de" : "fr",
      i = p[n],
      r = !!i[t];
    if ("FR" === t || r) {
      var o = (r ? i[t] : "") || e.admin1 || "";
      return o + (o ? ", " : "") + w[n]
    }
    var l = e.country || "";
    return v[n] && v[n][t] && (l = v[n][t]), (e.admin1 || "") + (e.admin1 && l ? ", " : "") + l
  }

  function f(e, t) {
    m && clearTimeout(m), e.length < 2 ? t([]) : m = setTimeout(function() {
      var n = "https://geocoding-api.open-meteo.com/v1/search?name=" + encodeURIComponent(e) + "&count=10&language=" + a;
      fetch(n).then(function(e) {
        return e.json()
      }).then(function(e) {
        var n = [];
        if (e && e.results) {
          var a = e.results.filter(function(e) {
            return "AIRP" !== e.feature_code && "RSTN" !== e.feature_code
          });
          a.sort(function(e, t) {
            return (t.population || 0) - (e.population || 0)
          });
          for (var i = {}, r = 0; r < a.length; r++) {
            var o = a[r].name.toLowerCase(),
              l = a[r].population || 0;
            (!i[o] || l > i[o]) && (i[o] = l)
          }
          for (var s = {}, c = 0; c < a.length && n.length < 6; c++) {
            var d = a[c],
              u = (d.country_code || "").toUpperCase(),
              g = {
                GF: 1,
                GP: 1,
                MQ: 1,
                RE: 1,
                PM: 1,
                YT: 1,
                NC: 1,
                PF: 1,
                WF: 1,
                MF: 1,
                BL: 1
              },
              m = d.name.toLowerCase();
            if (!(i[m] >= 5e3) || d.population > 0) {
              var p = m + "|" + (g[u] ? u : "FR" === u ? "FR" : u);
              if (!s[p]) {
                s[p] = !0;
                var w = g[u] ? "FR" : u;
                n.push({
                  name: d.name,
                  country: d.country || "",
                  country_code: u,
                  admin1: d.admin1 || "",
                  sub: h(d),
                  flag: w,
                  lat: d.latitude,
                  lon: d.longitude,
                  elevation: d.elevation || null
                })
              }
            }
          }
        }
        t(n)
      }).catch(function() {
        t([])
      })
    }, 300)
  }

  function b() {
    var e = s(t);
    return Array.isArray(e) ? (e.sort(function(e, t) {
      return (t.ts || 0) - (e.ts || 0)
    }), e) : []
  }
  var y = null;

  function M(e) {
    if (!e) return "🌍";
    if (/^[a-zA-Z]{2}$/.test(e)) {
      var t = e.toLowerCase();
      return {
        gf: 1,
        gp: 1,
        mq: 1,
        re: 1,
        pm: 1,
        yt: 1,
        nc: 1,
        pf: 1,
        wf: 1,
        mf: 1,
        bl: 1
      } [t] && (t = "fr"), '<img src="' + (window.BDW_CFG && window.BDW_CFG.flagBase ? window.BDW_CFG.flagBase : "flags/") + t + '.png" width="20" height="15" alt="' + t.toUpperCase() + '" style="vertical-align:middle;border-radius:2px" onerror="this.style.display=\'none\'">'
    }
    return e
  }

  function C(e) {
    if (!y || !e) return "";
    var t = e.replace(/\s*\([^)]*\)\s*$/, "").replace(/,.*$/, "").trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    for (var n in y) {
      var a = y[n],
        i = (a.fr || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""),
        r = (a.en || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""),
        o = (a.es || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      if (i === t || r === t || o === t) return n
    }
    return ""
  }

  function S(e) {
    return y && e && y[e] && y[e].flag || ""
  }

  function L() {
    return document.getElementById("wb-container")
  }

  function T() {
    var e = L();
    e && (e.innerHTML = '<div class="wb-shimmer"><div class="wb-shimmer-line"></div><div class="wb-shimmer-line" style="width:60%"></div></div>')
  }

  function k() {
    var e = L();
    if (e) {
      e.innerHTML = '<div class="wb-geo-prompt" id="wb-geo-prompt"><p>' + i.geoPrompt + '</p><div class="wb-geo-input-wrap"><span style="font-size:14px;opacity:.5">🔍</span><input class="wb-geo-input" id="wb-geo-input" placeholder="' + i.geoPlaceholder + '" autocomplete="off"/></div><div class="wb-geo-results" id="wb-geo-results"></div></div>';
      var t = document.getElementById("wb-geo-input");
      t && (setTimeout(function() {
        t.focus()
      }, 200), t.addEventListener("input", function() {
        f(t.value, function(e) {
          var t = document.getElementById("wb-geo-results");
          if (t)
            if (0 !== e.length) {
              for (var n = "", a = 0; a < e.length; a++) {
                var i = e[a];
                n += '<button class="wb-geo-result" data-lat="' + i.lat + '" data-lon="' + i.lon + '" data-name="' + I(i.name) + '">' + M(i.flag || i.country_code || "") + " " + G(i.name) + '<span style="opacity:.5;font-size:12px;margin-left:6px">' + G(i.sub || i.country) + "</span></button>"
              }
              t.innerHTML = n;
              for (var r = t.querySelectorAll(".wb-geo-result"), o = 0; o < r.length; o++) r[o].addEventListener("click", function() {
                B(this.getAttribute("data-name"), parseFloat(this.getAttribute("data-lat")), parseFloat(this.getAttribute("data-lon")))
              })
            } else t.innerHTML = ""
        })
      })), x(), F()
    }
  }

  function _() {
    var e = L();
    if (e && d.weather) {
      var t, n = d.weather,
        a = n.source === "ip" ? '<span class="wb-badge wb-badge-ip" onclick="event.stopPropagation();wbOpenCityModal()" title="' + (i.changeCity || "Changer") + '">~' + (i.approxLabel || "approx.") + '</span>' : (n.source === "manual" ? '<span class="wb-badge">' + (i.chosenCity || "") + '</span>' : ""),
        r = d.hourlyOpen ? "wb-expand open" : "wb-expand",
        o = '<div class="wb" id="wb-banner" onclick="wbToggleHourly()"><div class="wb-top"><div class="wb-left"><div class="wb-city"><span class="wb-pin">📍</span><button class="wb-city-btn" onclick="event.stopPropagation();wbOpenCityModal()" title="' + i.changeCity + '">' + G(n.city) + '<span class="wb-edit-ico">✎</span></button>' + a + '</div><div class="wb-desc">' + G(n.desc) + '</div></div><div class="wb-right"><span class="wb-icon">' + n.icon + '</span><div class="wb-temps"><span class="wb-temp">' + z(n.temp) + (R() ? "°F" : "°") + "</span>" + (null != n.tMin && null != n.tMax ? '<span class="wb-minmax">' + z(n.tMin) + "° / " + z(n.tMax) + "°</span>" : "") + '</div></div></div><div class="wb-meta"><span class="wb-meta-item">' + i.feels + " " + z(n.feels) + '°</span><span class="wb-meta-dot">·</span><span class="wb-meta-item">' + i.wind + " " + (null == (t = n.wind) ? "-" : R() ? Math.round(.621371 * t) : Math.round(t)) + (R() ? " mph" : " km/h") + '</span><span class="wb-meta-dot">·</span><span class="wb-meta-item">' + i.uv + " " + n.uv + '</span><span class="' + r + '">▼</span></div></div>',
        l = document.getElementById("wb-banner-zone");
      l ? l.innerHTML = o : e.innerHTML = '<div id="wb-banner-zone">' + o + '</div><div id="wb-hourly-zone"></div>', P();
 // Mettre à jour la ligne topbar compacte
 var tbl = document.getElementById('wb-topbar-line');
 if (tbl && d.weather) {
  var w = d.weather;
  var unit = R() ? '°F' : '°';
  var _w=d.weather;var _mm=(null!=_w.tMin&&null!=_w.tMax)?' ('+z(_w.tMin)+'°/'+z(_w.tMax)+'°)':'';var _isDesk=window.innerWidth>=641;var _feels=null!=_w.feels?' · Ressenti '+z(_w.feels)+(R()?'°F':'°'):'';var _wind=null!=_w.wind?' · Vent '+(R()?Math.round(.621371*_w.wind):Math.round(_w.wind))+(R()?' mph':' km/h'):'';tbl.innerHTML=_w.icon+' <button onclick="wbOpenCityModal()" style="background:none;border:none;color:#fff;font-weight:700;cursor:pointer;font-size:inherit;padding:0;font-family:inherit;">'+G(_w.city)+'</button> · '+z(_w.temp)+(R()?'°F':'°')+_mm+' · '+G(_w.desc)+' · UV '+_w.uv+(_isDesk?_feels:'')+(_isDesk?_wind:'');
 }
    }
  }

  function P() {
    var e = document.getElementById("wb-hourly-zone");
    if (e)
      if (d.hourlyOpen && d.weather && d.weather.hourly) {
        for (var t = d.weather.hourly, n = -999, a = 999, i = 0; i < t.length; i++) t[i].temp > n && (n = t[i].temp), t[i].temp < a && (a = t[i].temp);
        for (var r = n - a || 1, o = "", l = 0; l < t.length; l++) {
          var s = t[l],
            c = 8 + (s.temp - a) / r * 32,
            u = s.rain > 10 ? "#6ea8d9" : "var(--gold)",
            g = s.rain > 10 ? '<div class="wb-h-rain">💧' + s.rain + "%</div>" : '<div class="wb-h-rain" style="opacity:0">-</div>';
          o += '<div class="wb-h-col"><div class="wb-h-time">' + G(s.h) + '</div><div class="wb-h-ico">' + s.icon + '</div><div class="wb-h-bar" style="height:' + c + "px;background:" + u + '"></div><div class="wb-h-temp">' + z(s.temp) + "°</div>" + g + "</div>"
        }
        e.innerHTML = '<div class="wb-hourly"><div class="wb-hourly-scroll">' + o + "</div></div>"
      } else e.innerHTML = ""
  }

  function x() {
    var e = document.getElementById("wb-recent-section");
    if (e) {
      var t = b();
      if (0 === t.length) return e.innerHTML = "", void e.classList.add("wb-hidden");
      e.classList.remove("wb-hidden");
      for (var n = t.slice(0, 2), a = "", r = 0; r < n.length; r++) {
        var s = n[r],
          c = s.slug || C(s.name),
          d = M(s.flag || S(c)),
          u = "annual" === s.mode ? " · " + i.annual : " · " + i.date,
          g = o(s.score || 0),
          m = l(s.score || 0);
        a += '<div class="wb-recent" onclick="wbReplay(' + r + ')" style="animation-delay:' + 80 * r + 'ms"><div class="wb-recent-left"><span class="wb-recent-flag">' + d + '</span><div class="wb-recent-info"><span class="wb-recent-name">' + G(s.name) + '</span><span class="wb-recent-date">' + (s.date ? G(s.date) + " · " : "") + u.replace(" · ", "") + "</span></div></div>" + (s.score ? '<div class="wb-score" style="color:' + g + ";background:" + m + '">' + s.score.toFixed(1) + "</div>" : "") + "</div>"
      }
      e.innerHTML = '<div class="wb-section"><div class="wb-section-head"><span class="wb-section-title">' + i.recentTitle + '</span><button class="wb-section-action" onclick="wbClearRecent()">' + i.clearAll + "</button></div>" + a + "</div>"
    }
  }

  function F() {
    var e = document.getElementById("wb-suggest-section");
    if (e) e.innerHTML = '';
  }

  function A() {
    if (d.cityModalOpen) {
      var e = d.weather ? d.weather.city : "",
        t = document.createElement("div");
      t.id = "wb-modal-overlay", t.className = "wb-modal-overlay", t.onclick = function(e) {
        e.target === t && wbCloseCityModal()
      }, t.innerHTML = '<div class="wb-modal"><div class="wb-modal-head"><span class="wb-modal-title">' + i.cityTitle + '</span><button class="wb-modal-close" onclick="wbCloseCityModal()">✕</button></div><div class="wb-modal-inp-wrap"><span style="font-size:14px;opacity:.4">🔍</span><input class="wb-modal-inp" id="wb-modal-input" placeholder="' + i.typeCity + '" autocomplete="off"/></div><button class="wb-modal-geo" onclick="wbSelectGeo()"><span>📍</span><span>' + i.usePosition + '</span></button><div class="wb-modal-results" id="wb-modal-results"></div>' + (e ? '<div class="wb-modal-current">' + i.currently + " : <strong>" + G(e) + "</strong></div>" : "") + "</div>", document.body.appendChild(t), setTimeout(function() {
        var e = document.getElementById("wb-modal-input");
        e && (e.focus(), e.addEventListener("input", function() {
          f(e.value, function(e) {
            var t = document.getElementById("wb-modal-results");
            if (t)
              if (0 !== e.length) {
                for (var n = "", a = 0; a < e.length; a++) {
                  var i = e[a];
                  n += '<button class="wb-modal-result" data-lat="' + i.lat + '" data-lon="' + i.lon + '" data-name="' + I(i.name) + '"><span style="font-weight:600">' + M(i.flag || i.country_code || "") + " " + G(i.name) + '</span><span class="wb-modal-result-sub">' + G(i.sub || i.country) + "</span></button>"
                }
                t.innerHTML = n;
                for (var r = t.querySelectorAll(".wb-modal-result"), o = 0; o < r.length; o++) r[o].addEventListener("click", function() {
                  B(this.getAttribute("data-name"), parseFloat(this.getAttribute("data-lat")), parseFloat(this.getAttribute("data-lon")))
                })
              } else t.innerHTML = ""
          })
        }))
      }, 150)
    } else {
      var n = document.getElementById("wb-modal-overlay");
      n && n.remove()
    }
  }

  function B(t, n, a) {
    c(e, {
      name: t,
      lat: n,
      lon: a,
      source: "manual"
    }), d.citySource = "manual", d.cityModalOpen = !1, d.hourlyOpen = !1, A(), T(), g(n, a, t, "manual")
  }

  function E() {
    var e = document.getElementById("ann-city-name");
    if (e && e.textContent) {
      for (var t = e.textContent.trim(), n = document.getElementById("ann-city"), a = n ? n.value.trim() : t, i = 0, r = 0, o = document.querySelectorAll(".mcard-score"), l = 0; l < o.length; l++) {
        var s = parseFloat(o[l].textContent);
        isNaN(s) || (i += s, r++)
      }
      var c = r > 0 ? Math.round(i / r * 10) / 10 : 0,
        d = C(t),
        u = S(d);
      window.wbAddRecent({
        name: t,
        label: a,
        slug: d,
        flag: u,
        mode: "annual",
        date: "",
        score: c
      })
    }
  }

  function N() {
    var e = document.getElementById("inp-city"),
      t = document.getElementById("inp-date");
    if (e && e.value) {
      var n = document.querySelector(".score-val"),
        a = n ? parseFloat(n.textContent) : 0;
      isNaN(a) && (a = 0);
      var i = e.value.trim(),
        r = i.replace(/\s*\([^)]*\)\s*$/, "").replace(/,.*$/, "").trim(),
        o = C(i),
        l = S(o),
        s = null,
        c = null,
        d = "",
        u = "",
        g = null,
        m = "";
      window.selectedLoc && (s = window.selectedLoc.lat, c = window.selectedLoc.lon, d = window.selectedLoc.country || "", u = window.selectedLoc.region || "", g = window.selectedLoc.elevation || null, m = window.selectedLoc.country_code || "");
      var p = l || m.toLowerCase();
      window.wbAddRecent({
        name: r,
        label: i,
        slug: o,
        flag: p,
        mode: "date",
        date: t ? t.value : "",
        score: a,
        lat: s,
        lon: c,
        country: d,
        country_code: m,
        region: u,
        elevation: g
      })
    }
  }

  function R() {
    return "us" === window._units
  }

  function z(e) {
    return null == e ? "-" : R() ? Math.round(9 * e / 5 + 32) : Math.round(e)
  }

  function G(e) {
    return e ? e.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;") : ""
  }

  function I(e) {
    return G(e).replace(/'/g, "&#39;")
  }

  function H() {
    var t;
    ! function() {
      // 1. Ville sauvegardée manuellement → priorité absolue
      var t = s(e);
      if (t && t.name && t.lat && t.lon) {
        d.citySource = t.source || "manual";
        d.geoState = "granted";
        T();
        return void g(t.lat, t.lon, t.name, t.source || "manual");
      }
      // 2. Géoloc IP silencieuse via Cloudflare — zero permission
      d.geoState = "ip";
      T();
      fetch("/api/geo").then(function(r) { return r.json(); }).then(function(geo) {
        if (geo && geo.lat && geo.lon && geo.city) {
          var cityName = geo.city;
          d.geoState = "ip";
          // Passer approx:true pour afficher le badge "(approx.)"
          g(geo.lat, geo.lon, cityName, "ip");
        } else {
          // Pas de données IP → afficher le prompt discret (pas de popup)
          d.geoState = "denied";
          k();
        }
      }).catch(function() {
        // Fallback: ipapi.co si /api/geo échoue
        fetch('https://ipapi.co/json/').then(function(r){return r.json();}).then(function(geo){
          if(geo&&geo.latitude&&geo.longitude&&geo.city){
            d.geoState='ip';
            g(geo.latitude,geo.longitude,geo.city,'ip');
          } else { d.geoState='denied'; k(); }
        }).catch(function(){ d.geoState='denied'; k(); });
      });
    }(), (t = document.getElementById("wb-ranking-section")) && i.rankingUrl && (t.innerHTML = '<a href="' + i.rankingUrl + '" style="display:block;text-align:center;background:linear-gradient(135deg,var(--gold),var(--gold2));color:white;text-decoration:none;padding:10px 14px;border-radius:var(--r);margin:10px 16px 4px;border:none;font-family:\'DM Sans\',sans-serif;font-size:14px;font-weight:700;">' + i.rankingTitle + "</a>"), fetch("/data/suggestions.json").then(function(e) {
        return e.json()
      }).then(function(e) {
        y = e, window._wbSuggestions = e, x(), F()
      }).catch(function() {}),
      function() {
        var e = new MutationObserver(function(e) {
            for (var t = 0; t < e.length; t++) {
              var n = document.getElementById("ann-city-name");
              if (n && n.textContent) {
                var a = document.getElementById("months-grid");
                a && a.children.length > 0 && !a._wbTracked && (a._wbTracked = !0, E())
              }
            }
          }),
          t = document.querySelector(".wrap");
        t && e.observe(t, {
          childList: !0,
          subtree: !0,
          characterData: !0
        });
        var n = document.getElementById("btn-go");
        n && n.addEventListener("click", function() {
          // Reset le flag _wbTracked pour que l'observer redéclenche E() après runAnnual
          var mg = document.getElementById("months-grid");
          if (mg) mg._wbTracked = false;
          // En mode annuel, E() est déclenché par l'observer quand months-grid se remplit.
          // N() ne doit tourner qu'en mode date, sinon on pollue les recents avec mode:"date" sans date.
          var annWrap = document.getElementById("annual-wrap");
          var isAnnual = annWrap && annWrap.style.display !== "none";
          if (!isAnnual) setTimeout(N, 3e3)
        })
      }()
  }
  window.wbToggleHourly = function() {
    d.hourlyOpen = !d.hourlyOpen, _()
  }, window.wbOpenCityModal = function() {
    d.cityModalOpen = !0, A()
  }, window.wbShare = function() {
    var e = window.location.href,
      t = document.title || "BestDateWeather";
    navigator.share ? navigator.share({
      title: t,
      url: e
    }).catch(function() {}) : navigator.clipboard.writeText(e).then(function() {
      var e = document.querySelector(".wb-share-btn");
      if (e) {
        var t = e.innerHTML;
        e.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>', setTimeout(function() {
          e.innerHTML = t
        }, 1800)
      }
    }).catch(function() {
      window.prompt("Copier le lien :", e)
    })
  }, window.wbCloseCityModal = function() {
    d.cityModalOpen = !1, A()
  }, window.wbSelectGeo = function() {
    d.cityModalOpen = !1, A(), "geolocation" in navigator && (T(), navigator.geolocation.getCurrentPosition(function(t) {
      c(e, null), localStorage.removeItem(e), u(t.coords.latitude, t.coords.longitude)
    }, function() {
      k()
    }, {
      timeout: 3e3
    }))
  }, window.wbGeoAllow = function() {
    "geolocation" in navigator && (d.geoState = "loading", T(), navigator.geolocation.getCurrentPosition(function(e) {
      d.geoState = "granted", u(e.coords.latitude, e.coords.longitude)
    }, function() {
      d.geoState = "denied", k()
    }, {
      timeout: 3e3
    }))
  }, window.wbGeoSkip = function() {
    d.geoState = "denied", k()
  }, window.wbClearRecent = function() {
    c(t, []), x(), F()
  }, window.wbReplay = function(e) {
    var t = b()[e];
    t && function(e) {
      var t = e.name.replace(/\s*\([^)]*\)\s*$/, "").replace(/,.*$/, "").trim();
      if (e.label, null != e.lat && null != e.lon ? window.selectedLoc = {
          lat: e.lat,
          lon: e.lon,
          name: t,
          country: e.country || "",
          country_code: e.country_code || "",
          region: e.region || "",
          elevation: e.elevation || null
        } : window.selectedLoc = null, "annual" === e.mode) {
        switchMode("annual");
        var n = document.getElementById("ann-city");
        if (n) {
          n.value = t;
          var a = document.getElementById("ann-city-clear");
          a && a.classList.add("visible"), null != e.lat && null != e.lon && (window.annSelectedLoc = window.selectedLoc), setTimeout(function() {
            runAnnual()
          }, 300)
        }
      } else {
        switchMode("date");
        var i = document.getElementById("inp-city"),
          r = document.getElementById("inp-date");
        if (i) {
          i.value = t;
          var o = document.getElementById("inp-city-clear");
          o && o.classList.add("visible")
        }
        if (r && e.date) {
          var l = e.date.match(/(\d{2})\/(\d{2})\/(\d{4})/);
          l && (r.value = e.date, r._isoValue = l[3] + "-" + l[2] + "-" + l[1], r.classList.add("has-val"))
        }
        setTimeout(function() {
          run()
        }, 300)
      }
    }(t)
  }, window.wbRefreshUnits = function() {
    _(), P()
  }, window.wbAddRecent = function(e) {
    e.name && (e.name = e.name.split(" — ")[0].split(",")[0].replace(/\s*\([^)]*\)\s*$/, "").trim());
    var n = b();
    n = n.filter(function(t) {
      return !(t.slug === e.slug && t.mode === e.mode)
    }), e.ts = Date.now(), n.unshift(e), n.length > 10 && (n = n.slice(0, 10)), c(t, n), x(), F()
  }, "loading" === document.readyState ? document.addEventListener("DOMContentLoaded", H) : H()
}();