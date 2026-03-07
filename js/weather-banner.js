/* ═══════════════════════════════════════════════════
   Weather Banner Module — ES5 compatible
   Geolocation, Open-Meteo forecast, localStorage
   ═══════════════════════════════════════════════════ */
(function(){
  "use strict";

  /* ── CONFIG ── */
  var LS_CITY = "bdw_banner_city";
  var LS_RECENT = "bdw_recent";
  var MAX_RECENT_STORE = 10;
  var MAX_RECENT_SHOW = 3;
  var FORECAST_URL = "https://api.open-meteo.com/v1/forecast";
  var GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search";

  /* ── i18n ── */
  var LANG = document.documentElement.lang === "en" ? "en" : (document.documentElement.lang === "es" ? "es" : "fr");
  var T = {
    fr: {
      now: "Maint.", feels: "Ressenti", wind: "Vent", uv: "UV",
      chosenCity: "ville choisie", changeCity: "Changer de ville",
      cityTitle: "Ville du bandeau météo", typeCity: "Tapez une ville\u2026",
      usePosition: "Utiliser ma position", currently: "Actuellement",
      recentTitle: "Recherches récentes", clearAll: "Tout effacer",
      suggestTitle: "Pour vous", suggestSub: "même région climatique",
      geoPrompt: "Où êtes-vous ? Entrez votre ville pour la météo locale",
      geoPlaceholder: "Votre ville…",
      geoAllow: "Autoriser", geoSkip: "Plus tard",
      annual: "12 mois", date: "date",
      weatherDesc: {
        0: "Ciel dégagé", 1: "Peu nuageux", 2: "Partiellement nuageux", 3: "Couvert",
        45: "Brouillard", 48: "Brouillard givrant",
        51: "Bruine légère", 53: "Bruine modérée", 55: "Bruine forte",
        61: "Pluie légère", 63: "Pluie modérée", 65: "Pluie forte",
        71: "Neige légère", 73: "Neige modérée", 75: "Neige forte",
        80: "Averses légères", 81: "Averses modérées", 82: "Averses fortes",
        95: "Orage", 96: "Orage + grêle", 99: "Orage + grêle forte"
      }
    },
    en: {
      now: "Now", feels: "Feels", wind: "Wind", uv: "UV",
      chosenCity: "chosen city", changeCity: "Change city",
      cityTitle: "Banner weather city", typeCity: "Type a city\u2026",
      usePosition: "Use my location", currently: "Currently",
      recentTitle: "Recent searches", clearAll: "Clear all",
      suggestTitle: "For you", suggestSub: "similar climate region",
      geoPrompt: "Where are you? Enter your city for local weather",
      geoPlaceholder: "Your city…",
      geoAllow: "Allow", geoSkip: "Later",
      annual: "12 months", date: "date",
      weatherDesc: {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Rime fog",
        51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
        61: "Light rain", 63: "Rain", 65: "Heavy rain",
        71: "Light snow", 73: "Snow", 75: "Heavy snow",
        80: "Light showers", 81: "Showers", 82: "Heavy showers",
        95: "Thunderstorm", 96: "Storm + hail", 99: "Storm + heavy hail"
      }
    },
    es: {
      now: "Ahora", feels: "Sensación", wind: "Viento", uv: "UV",
      chosenCity: "ciudad elegida", changeCity: "Cambiar de ciudad",
      cityTitle: "Ciudad del banner meteorológico", typeCity: "Escribe una ciudad\u2026",
      usePosition: "Usar mi ubicación", currently: "Actualmente",
      recentTitle: "Búsquedas recientes", clearAll: "Borrar todo",
      suggestTitle: "Para ti", suggestSub: "región climática similar",
      geoPrompt: "¿Dónde estás? Introduce tu ciudad para el tiempo local",
      geoPlaceholder: "Tu ciudad\u2026",
      geoAllow: "Permitir", geoSkip: "Más tarde",
      annual: "12 meses", date: "fecha",
      weatherDesc: {
        0: "Cielo despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Cubierto",
        45: "Niebla", 48: "Niebla engelante",
        51: "Llovizna ligera", 53: "Llovizna", 55: "Llovizna intensa",
        61: "Lluvia ligera", 63: "Lluvia", 65: "Lluvia intensa",
        71: "Nieve ligera", 73: "Nieve", 75: "Nieve intensa",
        80: "Chubascos ligeros", 81: "Chubascos", 82: "Chubascos fuertes",
        95: "Tormenta", 96: "Tormenta + granizo", 99: "Tormenta + granizo fuerte"
      }
    }
  };
  var t = T[LANG];

  /* ── WEATHER CODE → EMOJI ── */
  function weatherEmoji(code) {
    if (code === 0) return "\u2600\ufe0f";
    if (code <= 2) return "\u26c5";
    if (code === 3) return "\u2601\ufe0f";
    if (code <= 48) return "\ud83c\udf2b\ufe0f";
    if (code <= 55) return "\ud83c\udf26\ufe0f";
    if (code <= 65) return "\ud83c\udf27\ufe0f";
    if (code <= 75) return "\u2744\ufe0f";
    if (code <= 82) return "\ud83c\udf27\ufe0f";
    return "\u26c8\ufe0f";
  }

  /* ── SCORE COLOR ── */
  function scoreColor(s) { return s >= 7 ? "var(--green)" : s >= 4 ? "#b8860b" : "#c0392b"; }
  function scoreBg(s) { return s >= 7 ? "var(--green-bg)" : s >= 4 ? "#fff8e1" : "#fde8e8"; }

  /* ── localStorage HELPERS ── */
  function lsGet(key) {
    try { var v = localStorage.getItem(key); return v ? JSON.parse(v) : null; }
    catch(e) { return null; }
  }
  function lsSet(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch(e) {}
  }

  /* ── STATE ── */
  var state = {
    weather: null,
    hourlyOpen: false,
    cityModalOpen: false,
    geoState: "init", // init | loading | granted | denied | manual
    citySource: "geo"  // geo | manual
  };

  /* ── DOM REFS ── */
  var $banner, $hourly, $recentSection, $suggestSection, $modalOverlay;

  /* ═════════════════════════════════════════════════
     GEOLOCATION + WEATHER FETCH
     ═════════════════════════════════════════════════ */

  function initBanner() {
    // Check if we have a saved city
    var saved = lsGet(LS_CITY);
    if (saved && saved.name && saved.lat && saved.lon) {
      state.citySource = saved.source || "manual";
      state.geoState = "granted";
      renderShimmer();
      fetchWeather(saved.lat, saved.lon, saved.name, saved.source || "manual");
      return;
    }

    // Try geolocation
    if ("geolocation" in navigator) {
      state.geoState = "loading";
      renderShimmer();
      navigator.geolocation.getCurrentPosition(
        function(pos) {
          state.geoState = "granted";
          reverseGeocode(pos.coords.latitude, pos.coords.longitude);
        },
        function(err) {
          state.geoState = "denied";
          renderGeoPrompt();
        },
        { timeout: 3000, maximumAge: 300000 }
      );
    } else {
      state.geoState = "denied";
      renderGeoPrompt();
    }
  }

  function reverseGeocode(lat, lon) {
    // Use Nominatim for reliable reverse geocoding
    var url = "https://nominatim.openstreetmap.org/reverse?lat=" + lat +
              "&lon=" + lon + "&format=json&zoom=10&accept-language=" + LANG;
    fetch(url).then(function(r) { return r.json(); }).then(function(data) {
      var name = "Ma position";
      if (data && data.address) {
        name = data.address.city || data.address.town || data.address.village ||
               data.address.municipality || data.address.county || "Position";
      }
      lsSet(LS_CITY, { name: name, lat: lat, lon: lon, source: "geo" });
      fetchWeather(lat, lon, name, "geo");
    }).catch(function() {
      // Fallback: use coordinates
      fetchWeather(lat, lon, lat.toFixed(2) + ", " + lon.toFixed(2), "geo");
    });
  }

  function fetchWeather(lat, lon, cityName, source) {
    var url = FORECAST_URL +
      "?latitude=" + lat +
      "&longitude=" + lon +
      "&hourly=temperature_2m,weather_code,wind_speed_10m,precipitation_probability" +
      "&daily=temperature_2m_max,temperature_2m_min" +
      "&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,uv_index,relative_humidity_2m" +
      "&timezone=auto&forecast_days=1";

    fetch(url).then(function(r) { return r.json(); }).then(function(data) {
      if (!data || !data.current) throw new Error("No data");
      var c = data.current;

      // Build hourly array (from current hour, next 12h)
      var hourly = [];
      var nowH = new Date().getHours();
      var hTemps = data.hourly.temperature_2m || [];
      var hCodes = data.hourly.weather_code || [];
      var hWinds = data.hourly.wind_speed_10m || [];
      var hRains = data.hourly.precipitation_probability || [];

      for (var i = nowH; i < Math.min(nowH + 12, hTemps.length); i++) {
        var label = (i === nowH) ? t.now : i + "h";
        hourly.push({
          h: label,
          temp: hTemps[i],
          icon: weatherEmoji(hCodes[i] || 0),
          wind: hWinds[i] || 0,
          rain: Math.round(hRains[i] || 0)
        });
      }

      // Daily min/max
      var tMin = null, tMax = null;
      if (data.daily) {
        if (data.daily.temperature_2m_max && data.daily.temperature_2m_max.length) tMax = data.daily.temperature_2m_max[0];
        if (data.daily.temperature_2m_min && data.daily.temperature_2m_min.length) tMin = data.daily.temperature_2m_min[0];
      }

      state.weather = {
        city: cityName,
        temp: c.temperature_2m,
        tMin: tMin,
        tMax: tMax,
        feels: c.apparent_temperature,
        wind: c.wind_speed_10m,
        icon: weatherEmoji(c.weather_code),
        desc: t.weatherDesc[c.weather_code] || t.weatherDesc[0],
        humidity: Math.round(c.relative_humidity_2m || 0),
        uv: Math.round(c.uv_index || 0),
        source: source,
        hourly: hourly
      };

      renderBanner();
      renderRecent();
      renderSuggestions();
    }).catch(function(err) {
      console.warn("[WB] Fetch error:", err);
      state.geoState = "denied";
      renderGeoPrompt();
    });
  }

  /* ═════════════════════════════════════════════════
     CITY SEARCH (GEOCODING API)
     ═════════════════════════════════════════════════ */

  var searchTimeout = null;

  var FR_TERRITORIES = {GF:"Guyane française",GP:"Guadeloupe",MQ:"Martinique",RE:"La Réunion",PM:"Saint-Pierre-et-Miquelon",YT:"Mayotte",NC:"Nouvelle-Calédonie",PF:"Polynésie française"};

  function acSub(r) {
    var cc = r.country_code || "";
    var isFrDom = !!FR_TERRITORIES[cc];
    if (cc === "FR" || isFrDom) {
      var terr = isFrDom ? FR_TERRITORIES[cc] : "";
      var region = terr || r.admin1 || "";
      return region + (region ? ", " : "") + "France";
    }
    return (r.admin1 || "") + (r.admin1 && r.country ? ", " : "") + (r.country || "");
  }

  function searchCities(query, callback) {
    if (searchTimeout) clearTimeout(searchTimeout);
    if (query.length < 2) { callback([]); return; }

    searchTimeout = setTimeout(function() {
      // Request more results to have room after dedup/filtering
      var url = GEOCODING_URL + "?name=" + encodeURIComponent(query) + "&count=10&language=" + LANG;
      fetch(url).then(function(r) { return r.json(); }).then(function(data) {
        var results = [];
        if (data && data.results) {
          // Filter out airports and non-populated places
          var places = data.results.filter(function(r) {
            return r.feature_code !== "AIRP" && r.feature_code !== "RSTN";
          });
          // Sort by population descending
          places.sort(function(a, b) { return (b.population || 0) - (a.population || 0); });
          // Deduplicate: if a name has a high-pop result, skip no-pop homonyms
          var namePop = {}; // track max population per name
          for (var j = 0; j < places.length; j++) {
            var nm = places[j].name.toLowerCase();
            var pop = places[j].population || 0;
            if (!namePop[nm] || pop > namePop[nm]) namePop[nm] = pop;
          }
          var seen = {};
          for (var i = 0; i < places.length && results.length < 6; i++) {
            var r = places[i];
            var cc = (r.country_code || "").toUpperCase();
            var domTom = {GF:1,GP:1,MQ:1,RE:1,PM:1,YT:1,NC:1,PF:1,WF:1,MF:1,BL:1};
            // Skip no-pop homonyms when a significant city exists with same name
            var rName = r.name.toLowerCase();
            if (namePop[rName] >= 5000 && !(r.population > 0)) continue;
            // Also deduplicate exact same name + same territory
            var territory = domTom[cc] ? cc : (cc === "FR" ? "FR" : cc);
            var key = rName + "|" + territory;
            if (seen[key]) continue;
            seen[key] = true;
            var flagCC = domTom[cc] ? "FR" : cc;
            results.push({
              name: r.name,
              country: r.country || "",
              country_code: cc,
              admin1: r.admin1 || "",
              sub: acSub(r),
              flag: flagCC,
              lat: r.latitude,
              lon: r.longitude,
              elevation: r.elevation || null
            });
          }
        }
        callback(results);
      }).catch(function() { callback([]); });
    }, 300);
  }

  /* ═════════════════════════════════════════════════
     RECENT SEARCHES (localStorage integration)
     ═════════════════════════════════════════════════ */

  function getRecent() {
    var arr = lsGet(LS_RECENT);
    if (!Array.isArray(arr)) return [];
    // Sort by timestamp descending
    arr.sort(function(a, b) { return (b.ts || 0) - (a.ts || 0); });
    return arr;
  }

  function clearRecent() {
    lsSet(LS_RECENT, []);
    renderRecent();
  }

  /* ═════════════════════════════════════════════════
     CLIMATE-BASED SUGGESTIONS
     ═════════════════════════════════════════════════ */

  /* ── SUGGESTIONS DATA (loaded from JSON) ── */
  var suggestionsData = null;

  function flagImg(code) {
    if (!code) return "\ud83c\udf0d";
    if (/^[a-zA-Z]{2}$/.test(code)) {
      var lower = code.toLowerCase();
      // DOM-TOM → use France flag
      var domTom = {gf:1,gp:1,mq:1,re:1,pm:1,yt:1,nc:1,pf:1,wf:1,mf:1,bl:1};
      if (domTom[lower]) lower = "fr";
      var base = (window.BDW_CFG && window.BDW_CFG.flagBase) ? window.BDW_CFG.flagBase : "flags/";
      return '<img src="' + base + lower + '.png" width="20" height="15" alt="' + lower.toUpperCase() + '" style="vertical-align:middle;border-radius:2px" onerror="this.style.display=\'none\'">';
    }
    return code;
  }

  function loadSuggestions() {
    var pfx = LANG === "en" ? "../" : "";
    fetch(pfx + "data/suggestions.json")
      .then(function(r) { return r.json(); })
      .then(function(d) {
        suggestionsData = d;
        renderSuggestions();
      })
      .catch(function() {});
  }

  function getSuggestions() {
    if (!suggestionsData) return [];
    var recent = getRecent();
    if (recent.length === 0) return [];

    // Find first recent search that has suggestions data
    var baseDest = null;
    var baseName = "";
    for (var i = 0; i < recent.length; i++) {
      if (recent[i].slug && suggestionsData[recent[i].slug]) {
        baseDest = suggestionsData[recent[i].slug];
        baseName = LANG === "en" ? baseDest.en : baseDest.fr;
        break;
      }
    }
    if (!baseDest || !baseDest.similar || !baseDest.similar.length) return [];

    // Exclude destinations already in recent
    var recentSlugs = {};
    for (var j = 0; j < recent.length; j++) {
      if (recent[j].slug) recentSlugs[recent[j].slug] = true;
    }

    var sims = baseDest.similar;
    var suggestions = [];
    for (var k = 0; k < sims.length; k++) {
      if (!recentSlugs[sims[k].slug]) {
        var sName = LANG === "en" ? sims[k].en : sims[k].fr;
        suggestions.push({
          name: sName,
          flag: sims[k].flag || "",
          slug: sims[k].slug,
          score: sims[k].score_avg || 0,
          reason: (LANG === "en" ? "Climate similar to " : "Climat proche de ") + baseName
        });
      }
      if (suggestions.length >= 2) break;
    }
    return suggestions;
  }

  /* ── SLUG / FLAG LOOKUP ── */
  function findSlugForName(name) {
    if (!suggestionsData || !name) return "";
    // Strip "(Country)" and ", Region" suffixes from autocomplete labels
    // e.g. "Barcelone, Catalogne (Espagne)" → "Barcelone"
    var clean = name.replace(/\s*\([^)]*\)\s*$/, "").replace(/,.*$/, "").trim();
    var lower = clean.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    for (var slug in suggestionsData) {
      var d = suggestionsData[slug];
      var fr = (d.fr || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      var en = (d.en || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      if (fr === lower || en === lower) return slug;
    }
    return "";
  }

  function findFlagForSlug(slug) {
    if (!suggestionsData || !slug || !suggestionsData[slug]) return "";
    return suggestionsData[slug].flag || "";
  }

  /* ═════════════════════════════════════════════════
     RENDER FUNCTIONS
     ═════════════════════════════════════════════════ */

  function getContainer() {
    return document.getElementById("wb-container");
  }

  function renderShimmer() {
    var c = getContainer();
    if (!c) return;
    c.innerHTML =
      '<div class="wb-shimmer">' +
        '<div class="wb-shimmer-line"></div>' +
        '<div class="wb-shimmer-line" style="width:60%"></div>' +
      '</div>';
  }

  function renderGeoPrompt() {
    var c = getContainer();
    if (!c) return;
    c.innerHTML =
      '<div class="wb-geo-prompt" id="wb-geo-prompt">' +
        '<p>' + t.geoPrompt + '</p>' +
        '<div class="wb-geo-input-wrap">' +
          '<span style="font-size:14px;opacity:.5">\ud83d\udd0d</span>' +
          '<input class="wb-geo-input" id="wb-geo-input" placeholder="' + t.geoPlaceholder + '" autocomplete="off"/>' +
        '</div>' +
        '<div class="wb-geo-results" id="wb-geo-results"></div>' +
      '</div>';

    // Bind autocomplete on the input
    var inp = document.getElementById("wb-geo-input");
    if (inp) {
      setTimeout(function() { inp.focus(); }, 200);
      inp.addEventListener("input", function() {
        searchCities(inp.value, function(results) {
          var container = document.getElementById("wb-geo-results");
          if (!container) return;
          if (results.length === 0) { container.innerHTML = ""; return; }
          var html = "";
          for (var i = 0; i < results.length; i++) {
            var r = results[i];
            html +=
              '<button class="wb-geo-result" data-lat="' + r.lat + '" data-lon="' + r.lon + '" data-name="' + escAttr(r.name) + '">' +
                flagImg(r.flag || r.country_code || "") + " " + escHtml(r.name) + '<span style="opacity:.5;font-size:12px;margin-left:6px">' + escHtml(r.sub || r.country) + '</span>' +
              '</button>';
          }
          container.innerHTML = html;
          var btns = container.querySelectorAll(".wb-geo-result");
          for (var j = 0; j < btns.length; j++) {
            btns[j].addEventListener("click", function() {
              var name = this.getAttribute("data-name");
              var lat = parseFloat(this.getAttribute("data-lat"));
              var lon = parseFloat(this.getAttribute("data-lon"));
              selectCity(name, lat, lon);
            });
          }
        });
      });
    }

    renderRecent();
    renderSuggestions();
  }

  function renderBanner() {
    var c = getContainer();
    if (!c || !state.weather) return;
    var w = state.weather;

    var badgeHtml = w.source === "manual"
      ? '<span class="wb-badge">' + t.chosenCity + '</span>'
      : '';

    var expandCls = state.hourlyOpen ? "wb-expand open" : "wb-expand";

    var html =
      '<div class="wb" id="wb-banner" onclick="wbToggleHourly()">' +
        '<div class="wb-top">' +
          '<div class="wb-left">' +
            '<div class="wb-city">' +
              '<span class="wb-pin">\ud83d\udccd</span>' +
              '<button class="wb-city-btn" onclick="event.stopPropagation();wbOpenCityModal()" title="' + t.changeCity + '">' +
                escHtml(w.city) +
                '<span class="wb-edit-ico">\u270e</span>' +
              '</button>' +
              badgeHtml +
            '</div>' +
            '<div class="wb-desc">' + escHtml(w.desc) + '</div>' +
          '</div>' +
          '<div class="wb-right">' +
            '<span class="wb-icon">' + w.icon + '</span>' +
            '<div class="wb-temps">' +
              '<span class="wb-temp">' + fmtT(w.temp) + unitT() + '</span>' +
              (w.tMin != null && w.tMax != null ? '<span class="wb-minmax">' + fmtT(w.tMin) + '\u00b0 / ' + fmtT(w.tMax) + '\u00b0</span>' : '') +
            '</div>' +
          '</div>' +
        '</div>' +
        '<div class="wb-meta">' +
          '<span class="wb-meta-item">' + t.feels + ' ' + fmtT(w.feels) + '\u00b0</span>' +
          '<span class="wb-meta-dot">\u00b7</span>' +
          '<span class="wb-meta-item">' + t.wind + ' ' + fmtW(w.wind) + unitW() + '</span>' +
          '<span class="wb-meta-dot">\u00b7</span>' +
          '<span class="wb-meta-item">' + t.uv + ' ' + w.uv + '</span>' +
          '<span class="' + expandCls + '">\u25bc</span>' +
        '</div>' +
      '</div>';

    // Set banner HTML (keep hourly/modal separate)
    var bannerEl = document.getElementById("wb-banner-zone");
    if (!bannerEl) {
      c.innerHTML = '<div id="wb-banner-zone">' + html + '</div><div id="wb-hourly-zone"></div>';
    } else {
      bannerEl.innerHTML = html;
    }

    renderHourly();
  }

  function renderHourly() {
    var zone = document.getElementById("wb-hourly-zone");
    if (!zone) return;

    if (!state.hourlyOpen || !state.weather || !state.weather.hourly) {
      zone.innerHTML = "";
      return;
    }

    var hourly = state.weather.hourly;
    var maxT = -999, minT = 999;
    for (var i = 0; i < hourly.length; i++) {
      if (hourly[i].temp > maxT) maxT = hourly[i].temp;
      if (hourly[i].temp < minT) minT = hourly[i].temp;
    }
    var range = maxT - minT || 1;

    var cols = "";
    for (var j = 0; j < hourly.length; j++) {
      var h = hourly[j];
      var barH = 8 + ((h.temp - minT) / range) * 32;
      var barColor = h.rain > 10 ? "#6ea8d9" : "var(--gold)";
      var rainHtml = h.rain > 10
        ? '<div class="wb-h-rain">\ud83d\udca7' + h.rain + '%</div>'
        : '<div class="wb-h-rain" style="opacity:0">-</div>';

      cols +=
        '<div class="wb-h-col">' +
          '<div class="wb-h-time">' + escHtml(h.h) + '</div>' +
          '<div class="wb-h-ico">' + h.icon + '</div>' +
          '<div class="wb-h-bar" style="height:' + barH + 'px;background:' + barColor + '"></div>' +
          '<div class="wb-h-temp">' + fmtT(h.temp) + '\u00b0</div>' +
          rainHtml +
        '</div>';
    }

    zone.innerHTML =
      '<div class="wb-hourly">' +
        '<div class="wb-hourly-scroll">' + cols + '</div>' +
      '</div>';
  }

  function renderRecent() {
    var section = document.getElementById("wb-recent-section");
    if (!section) return;

    var recent = getRecent();
    if (recent.length === 0) {
      section.innerHTML = "";
      section.classList.add("wb-hidden");
      return;
    }

    section.classList.remove("wb-hidden");
    var shown = recent.slice(0, MAX_RECENT_SHOW);

    var cards = "";
    for (var i = 0; i < shown.length; i++) {
      var item = shown[i];
      var flag = flagImg(item.flag);
      var modeLabel = item.mode === "annual"
        ? " \u00b7 " + t.annual
        : " \u00b7 " + t.date;
      var sColor = scoreColor(item.score || 0);
      var sBg = scoreBg(item.score || 0);

      cards +=
        '<div class="wb-recent" onclick="wbReplay(' + i + ')" style="animation-delay:' + (i * 80) + 'ms">' +
          '<div class="wb-recent-left">' +
            '<span class="wb-recent-flag">' + flag + '</span>' +
            '<div class="wb-recent-info">' +
              '<div class="wb-recent-name">' + escHtml(item.name) + '</div>' +
              '<div class="wb-recent-date">' +
                escHtml(item.date || "") +
                '<span class="wb-recent-mode">' + modeLabel + '</span>' +
              '</div>' +
            '</div>' +
          '</div>' +
          (item.score ? '<div class="wb-score" style="color:' + sColor + ';background:' + sBg + '">' + item.score.toFixed(1) + '</div>' : '') +
        '</div>';
    }

    section.innerHTML =
      '<div class="wb-section">' +
        '<div class="wb-section-head">' +
          '<span class="wb-section-title">' + t.recentTitle + '</span>' +
          '<button class="wb-section-action" onclick="wbClearRecent()">' + t.clearAll + '</button>' +
        '</div>' +
        cards +
      '</div>';
  }

  function replaySearch(r) {
    var cleanName = r.name.replace(/\s*\([^)]*\)\s*$/, "").replace(/,.*$/, "").trim();
    var inputLabel = r.label || cleanName;

    // Restore selectedLoc so core.js run() doesn't re-geocode
    if (r.lat != null && r.lon != null) {
      window.selectedLoc = {
        lat: r.lat, lon: r.lon,
        name: cleanName,
        country: r.country || "",
        country_code: r.country_code || "",
        region: r.region || "",
        elevation: r.elevation || null
      };
    } else {
      window.selectedLoc = null;
    }

    if (r.mode === "annual") {
      switchMode("annual");
      var annInput = document.getElementById("ann-city");
      if (annInput) {
        annInput.value = r.lat != null ? inputLabel : cleanName;
        if (r.lat != null && r.lon != null) {
          window.annSelectedLoc = window.selectedLoc;
        }
        setTimeout(function() { runAnnual(); }, 300);
      }
    } else {
      switchMode("date");
      var cityInput = document.getElementById("inp-city");
      var dateInput = document.getElementById("inp-date");
      if (cityInput) {
        cityInput.value = r.lat != null ? inputLabel : cleanName;
      }
      if (dateInput && r.date) {
        var parts = r.date.match(/(\d{2})\/(\d{2})\/(\d{4})/);
        if (parts) {
          dateInput.value = r.date;
          dateInput._isoValue = parts[3] + "-" + parts[2] + "-" + parts[1];
          dateInput.classList.add("has-val");
        }
      }
      setTimeout(function() {
        run();
      }, 300);
    }
  }

  function renderSuggestions() {
    var section = document.getElementById("wb-suggest-section");
    if (!section) return;

    var suggestions = getSuggestions();
    if (suggestions.length === 0) {
      section.innerHTML = "";
      section.classList.add("wb-hidden");
      return;
    }

    section.classList.remove("wb-hidden");
    var cards = "";
    for (var i = 0; i < suggestions.length; i++) {
      var s = suggestions[i];
      var href = LANG === "en"
        ? "/en/best-time-to-visit-" + s.slug + ".html"
        : "/meilleure-periode-" + s.slug + ".html";

      cards +=
        '<a href="' + href + '" class="wb-suggest" style="animation-delay:' + ((3 + i) * 80) + 'ms;text-decoration:none">' +
          '<div class="wb-suggest-top">' +
            '<span class="wb-recent-flag">' + flagImg(s.flag) + '</span>' +
            '<span class="wb-suggest-name">' + escHtml(s.name) + '</span>' +
            (s.score ? '<span class="wb-score" style="font-size:12px;padding:2px 8px;color:' + scoreColor(s.score) + ';background:' + scoreBg(s.score) + '">' + s.score.toFixed(1) + '</span>' : '') +
          '</div>' +
          '<div class="wb-suggest-reason">' + escHtml(s.reason) + '</div>' +
        '</a>';
    }

    section.innerHTML =
      '<div class="wb-section">' +
        '<div class="wb-section-head">' +
          '<span class="wb-section-title">' + t.suggestTitle + '</span>' +
          '<span class="wb-section-sub">' + t.suggestSub + '</span>' +
        '</div>' +
        cards +
      '</div>';
  }

  /* ═════════════════════════════════════════════════
     CITY MODAL
     ═════════════════════════════════════════════════ */

  function renderCityModal() {
    if (!state.cityModalOpen) {
      var existing = document.getElementById("wb-modal-overlay");
      if (existing) existing.remove();
      return;
    }

    var currentCity = state.weather ? state.weather.city : "";

    var overlay = document.createElement("div");
    overlay.id = "wb-modal-overlay";
    overlay.className = "wb-modal-overlay";
    overlay.onclick = function(e) { if (e.target === overlay) wbCloseCityModal(); };

    overlay.innerHTML =
      '<div class="wb-modal">' +
        '<div class="wb-modal-head">' +
          '<span class="wb-modal-title">' + t.cityTitle + '</span>' +
          '<button class="wb-modal-close" onclick="wbCloseCityModal()">\u2715</button>' +
        '</div>' +
        '<div class="wb-modal-inp-wrap">' +
          '<span style="font-size:14px;opacity:.4">\ud83d\udd0d</span>' +
          '<input class="wb-modal-inp" id="wb-modal-input" placeholder="' + t.typeCity + '" autocomplete="off"/>' +
        '</div>' +
        '<button class="wb-modal-geo" onclick="wbSelectGeo()">' +
          '<span>\ud83d\udccd</span>' +
          '<span>' + t.usePosition + '</span>' +
        '</button>' +
        '<div class="wb-modal-results" id="wb-modal-results"></div>' +
        (currentCity ? '<div class="wb-modal-current">' + t.currently + ' : <strong>' + escHtml(currentCity) + '</strong></div>' : '') +
      '</div>';

    document.body.appendChild(overlay);

    // Focus input
    setTimeout(function() {
      var inp = document.getElementById("wb-modal-input");
      if (inp) {
        inp.focus();
        inp.addEventListener("input", function() {
          var val = inp.value;
          searchCities(val, function(results) {
            var container = document.getElementById("wb-modal-results");
            if (!container) return;
            if (results.length === 0) { container.innerHTML = ""; return; }

            var html = "";
            for (var i = 0; i < results.length; i++) {
              var r = results[i];
              html +=
                '<button class="wb-modal-result" data-lat="' + r.lat + '" data-lon="' + r.lon + '" data-name="' + escAttr(r.name) + '">' +
                  '<span style="font-weight:600">' + flagImg(r.flag || r.country_code || "") + ' ' + escHtml(r.name) + '</span>' +
                  '<span class="wb-modal-result-sub">' + escHtml(r.sub || r.country) + '</span>' +
                '</button>';
            }
            container.innerHTML = html;

            // Bind clicks
            var btns = container.querySelectorAll(".wb-modal-result");
            for (var j = 0; j < btns.length; j++) {
              btns[j].addEventListener("click", function() {
                var name = this.getAttribute("data-name");
                var lat = parseFloat(this.getAttribute("data-lat"));
                var lon = parseFloat(this.getAttribute("data-lon"));
                selectCity(name, lat, lon);
              });
            }
          });
        });
      }
    }, 150);
  }

  function selectCity(name, lat, lon) {
    lsSet(LS_CITY, { name: name, lat: lat, lon: lon, source: "manual" });
    state.citySource = "manual";
    state.cityModalOpen = false;
    state.hourlyOpen = false;
    renderCityModal();
    renderShimmer();
    fetchWeather(lat, lon, name, "manual");
  }

  /* ═════════════════════════════════════════════════
     GLOBAL HANDLERS (onclick from HTML)
     ═════════════════════════════════════════════════ */

  window.wbToggleHourly = function() {
    state.hourlyOpen = !state.hourlyOpen;
    renderBanner();
  };

  window.wbOpenCityModal = function() {
    state.cityModalOpen = true;
    renderCityModal();
  };

  window.wbCloseCityModal = function() {
    state.cityModalOpen = false;
    renderCityModal();
  };

  window.wbSelectGeo = function() {
    state.cityModalOpen = false;
    renderCityModal();

    if ("geolocation" in navigator) {
      renderShimmer();
      navigator.geolocation.getCurrentPosition(
        function(pos) {
          lsSet(LS_CITY, null);
          localStorage.removeItem(LS_CITY);
          reverseGeocode(pos.coords.latitude, pos.coords.longitude);
        },
        function() {
          renderGeoPrompt();
        },
        { timeout: 3000 }
      );
    }
  };

  window.wbGeoAllow = function() {
    if ("geolocation" in navigator) {
      state.geoState = "loading";
      renderShimmer();
      navigator.geolocation.getCurrentPosition(
        function(pos) {
          state.geoState = "granted";
          reverseGeocode(pos.coords.latitude, pos.coords.longitude);
        },
        function() {
          state.geoState = "denied";
          renderGeoPrompt();
        },
        { timeout: 3000 }
      );
    }
  };

  window.wbGeoSkip = function() {
    state.geoState = "denied";
    renderGeoPrompt();
  };

  window.wbClearRecent = function() {
    clearRecent();
    renderSuggestions();
  };

  window.wbReplay = function(idx) {
    var r = getRecent()[idx];
    if (r) replaySearch(r);
  };

  window.wbRefreshUnits = function() {
    renderBanner();
    renderHourly();
  };

  /* ═════════════════════════════════════════════════
     AUTO-TRACKING — observe search results
     ═════════════════════════════════════════════════ */

  function hookSearchTracking() {
    // Observe mutations on .wrap to detect when results appear
    var observer = new MutationObserver(function(mutations) {
      for (var i = 0; i < mutations.length; i++) {
        // Annual results
        var annCityEl = document.getElementById("ann-city-name");
        if (annCityEl && annCityEl.textContent) {
          var grid = document.getElementById("months-grid");
          if (grid && grid.children.length > 0 && !grid._wbTracked) {
            grid._wbTracked = true;
            trackAnnualResult();
          }
        }
      }
    });
    var wrap = document.querySelector(".wrap");
    if (wrap) observer.observe(wrap, { childList: true, subtree: true, characterData: true });

    // Hook into btn-go for date mode
    var btnGo = document.getElementById("btn-go");
    if (btnGo) {
      btnGo.addEventListener("click", function() {
        setTimeout(trackDateResult, 3000);
      });
    }
  }

  function trackAnnualResult() {
    var nameEl = document.getElementById("ann-city-name");
    if (!nameEl || !nameEl.textContent) return;
    var name = nameEl.textContent.trim();

    // Keep full input label for replay
    var annInput = document.getElementById("ann-city");
    var fullLabel = annInput ? annInput.value.trim() : name;

    // Average score from month cards
    var score = 0, count = 0;
    var cards = document.querySelectorAll(".mcard-score");
    for (var i = 0; i < cards.length; i++) {
      var v = parseFloat(cards[i].textContent);
      if (!isNaN(v)) { score += v; count++; }
    }
    var avgScore = count > 0 ? Math.round((score / count) * 10) / 10 : 0;

    var slug = findSlugForName(name);
    var flag = findFlagForSlug(slug);

    window.wbAddRecent({
      name: name,
      label: fullLabel,
      slug: slug,
      flag: flag,
      mode: "annual",
      date: "",
      score: avgScore,
    });
  }

  function trackDateResult() {
    var cityInput = document.getElementById("inp-city");
    var dateInput = document.getElementById("inp-date");
    if (!cityInput || !cityInput.value) return;

    var scoreEl = document.querySelector(".score-val");
    var score = scoreEl ? parseFloat(scoreEl.textContent) : 0;
    if (isNaN(score)) score = 0;

    var fullLabel = cityInput.value.trim();
    var displayName = fullLabel.replace(/\s*\([^)]*\)\s*$/, "").replace(/,.*$/, "").trim();
    var slug = findSlugForName(fullLabel);
    var flag = findFlagForSlug(slug);

    // Capture coordinates from selectedLoc if available
    var lat = null, lon = null, country = "", region = "", elevation = null, cc = "";
    if (window.selectedLoc) {
      lat = window.selectedLoc.lat;
      lon = window.selectedLoc.lon;
      country = window.selectedLoc.country || "";
      region = window.selectedLoc.region || "";
      elevation = window.selectedLoc.elevation || null;
      cc = window.selectedLoc.country_code || "";
    }

    // Use country_code for flag if slug-based flag is empty
    var flagCode = flag || cc.toLowerCase();

    window.wbAddRecent({
      name: displayName,
      label: fullLabel,
      slug: slug,
      flag: flagCode,
      mode: "date",
      date: dateInput ? dateInput.value : "",
      score: score,
      lat: lat,
      lon: lon,
      country: country,
      country_code: cc,
      region: region,
      elevation: elevation,
    });
  }

  /* ═════════════════════════════════════════════════
     PUBLIC API for integration with main app
     (called by core.js when a search is performed)
     ═════════════════════════════════════════════════ */

  window.wbAddRecent = function(item) {
    // item: { slug, name, flag, mode, date, score }
    // Sanitize name: strip country suffix appended by autocomplete
    if (item.name) {
      item.name = item.name.split(' — ')[0].split(',')[0].replace(/\s*\([^)]*\)\s*$/, '').trim();
    }
    var arr = getRecent();

    // Remove duplicate by slug + mode
    arr = arr.filter(function(r) {
      return !(r.slug === item.slug && r.mode === item.mode);
    });

    item.ts = Date.now();
    arr.unshift(item);

    // Trim to max
    if (arr.length > MAX_RECENT_STORE) arr = arr.slice(0, MAX_RECENT_STORE);

    lsSet(LS_RECENT, arr);
    renderRecent();
    renderSuggestions();
  };

  /* ── UNIT CONVERSION ── */
  function isUS() { return window._units === "us"; }
  function fmtT(c) {
    if (c == null) return "-";
    return isUS() ? Math.round(c * 9/5 + 32) : Math.round(c);
  }
  function fmtW(kmh) {
    if (kmh == null) return "-";
    return isUS() ? Math.round(kmh * 0.621371) : Math.round(kmh);
  }
  function unitT() { return isUS() ? "\u00b0F" : "\u00b0"; }
  function unitW() { return isUS() ? " mph" : " km/h"; }

  /* ── UTILS ── */
  function escHtml(s) {
    if (!s) return "";
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function escAttr(s) {
    return escHtml(s).replace(/'/g, "&#39;");
  }

  /* ═════════════════════════════════════════════════
     INIT
     ═════════════════════════════════════════════════ */

  function initAll() {
    initBanner();
    loadSuggestions();
    hookSearchTracking();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }

})();
