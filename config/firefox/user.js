// Solux OS — Perfil de Firefox endurecido pero usable para el día a día
// © 2026 Pollocrudo Company
//
// Equilibrio: privacidad y seguridad fuertes SIN romper la navegación normal
// (compras, banca, vídeo). Se instala en el perfil por defecto vía autoconfig.

/* ---------- Telemetría y datos: desactivar todo ---------- */
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.archive.enabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("app.normandy.enabled", false);
user_pref("browser.discovery.enabled", false);
user_pref("browser.newtabpage.activity-stream.feeds.telemetry", false);
user_pref("browser.ping-centre.telemetry", false);

/* ---------- Privacidad de red ---------- */
// DNS over HTTPS (modo 2: DoH con respaldo). Cloudflare por defecto.
user_pref("network.trr.mode", 2);
user_pref("network.trr.uri", "https://mozilla.cloudflare-dns.com/dns-query");
// No prelanzar conexiones a resultados sugeridos.
user_pref("network.prefetch-next", false);
user_pref("network.dns.disablePrefetch", true);
user_pref("network.predictor.enabled", false);
user_pref("network.http.referer.XOriginPolicy", 2);
user_pref("network.http.referer.XOriginTrimmingPolicy", 2);

/* ---------- Protección contra rastreo (estricta pero compatible) ---------- */
user_pref("browser.contentblocking.category", "strict");
user_pref("privacy.trackingprotection.enabled", true);
user_pref("privacy.trackingprotection.socialtracking.enabled", true);
user_pref("privacy.partition.network_state.ocsp_cache", true);
// Aislamiento total de cookies por sitio (First-Party Isolation vía dFPI).
user_pref("privacy.firstparty.isolate", false); // dFPI (Total Cookie Protection) ya activo en estricto
user_pref("privacy.resistFingerprinting", false); // dejar OFF: rompe zoom/tema; el usuario puede activarlo

/* ---------- Cookies y sesión ---------- */
user_pref("network.cookie.cookieBehavior", 5); // dFPI
// No borrar al cerrar por defecto (usabilidad); el usuario puede activarlo.
user_pref("privacy.sanitize.sanitizeOnShutdown", false);

/* ---------- Seguridad HTTPS ---------- */
user_pref("dom.security.https_only_mode", true);
user_pref("dom.security.https_only_mode_ever_enabled", true);
user_pref("security.ssl.require_safe_negotiation", true);
user_pref("security.tls.enable_0rtt_data", false);
user_pref("security.OCSP.enabled", 1);
user_pref("security.cert_pinning.enforcement_level", 2);

/* ---------- Endurecer contenido activo ---------- */
user_pref("media.peerconnection.enabled", true); // WebRTC ON para videollamadas
user_pref("media.peerconnection.ice.default_address_only", true); // pero sin fugar IP local
user_pref("dom.event.clipboardevents.enabled", true);
user_pref("pdfjs.enableScripting", false);

/* ---------- Búsqueda y sugerencias ---------- */
user_pref("browser.search.suggest.enabled", true);
user_pref("browser.urlbar.suggest.searches", true);
user_pref("keyword.enabled", true);

/* ---------- Descargas y actualizaciones ---------- */
user_pref("browser.download.always_ask_before_handling_new_types", true);
user_pref("browser.safebrowsing.downloads.remote.enabled", false);
user_pref("app.update.auto", true);

/* ---------- Interfaz ---------- */
user_pref("browser.startup.homepage", "about:home");
user_pref("browser.newtabpage.activity-stream.showSponsored", false);
user_pref("browser.newtabpage.activity-stream.showSponsoredTopSites", false);
user_pref("extensions.pocket.enabled", false);
user_pref("browser.aboutConfig.showWarning", false);
user_pref("browser.uidensity", 1);
