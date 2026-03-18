/**
 * Netlify Edge Function — regex redirects
 *
 * Handles 2 patterns not supported by _redirects syntax:
 *
 * 1. FR: /meilleure-periode-{slug}-en-{month}.html → /{slug}-meteo-{month}.html
 * 2. EN: /en/best-time-to-visit-{slug}-in-{month}.html → /en/{slug}-weather-{month}.html
 *
 * These are legacy SEO URLs from old site structure, kept for 301 coverage.
 */

const FR_MONTHS = 'janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre';
const EN_MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december';

const PATTERN_FR = new RegExp(`^/meilleure-periode-(.+)-en-(${FR_MONTHS})\\.html$`);
const PATTERN_EN = new RegExp(`^/en/best-time-to-visit-(.+)-in-(${EN_MONTHS})\\.html$`);

export default async function handler(request, context) {
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

  return context.next();
}

export const config = {
  path: ['/:path*'],
};
