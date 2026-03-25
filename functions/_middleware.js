/**
 * Cloudflare Pages Middleware — regex redirects
 * Equivalent de netlify/edge-functions/regex-redirects.js
 */

const FR_MONTHS = 'janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre';
const EN_MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december';

const PATTERN_FR = new RegExp(`^/meilleure-periode-(.+)-en-(${FR_MONTHS})\\.html$`);
const PATTERN_EN = new RegExp(`^/en/best-time-to-visit-(.+)-in-(${EN_MONTHS})\\.html$`);

export async function onRequest(context) {
  const { request, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  const matchFR = path.match(PATTERN_FR);
  if (matchFR) {
    const [, slug, month] = matchFR;
    return Response.redirect(`${url.origin}/${slug}-meteo-${month}.html`, 301);
  }

  const matchEN = path.match(PATTERN_EN);
  if (matchEN) {
    const [, slug, month] = matchEN;
    return Response.redirect(`${url.origin}/en/${slug}-weather-${month}.html`, 301);
  }

  return next();
}
