"""
BestDateWeather — Configuration centralisée
============================================
IDs partenaires et constantes de configuration.
Importer ce fichier depuis les générateurs plutôt que de dupliquer les valeurs.

Mise à jour des IDs :
  - GetYourGuide  : dashboard.getyourguide.com → Affiliate Program
  - Travelpayouts : travelpayouts.com → Programs → Tools
  - Expedia       : creator.expediagroup.com → Links → Link builder
Les liens eux-mêmes sont construits par lib/affiliates.py (source unique).
  - Booking.com   : CJ Affiliate (PID 101696591) → get link
"""

# ── Affiliés ─────────────────────────────────────────────────────────────────

# GetYourGuide — partner ID (https://partner.getyourguide.com)
GYG_PARTNER_ID = '2MQKL00'

# Travelpayouts — marker / shmarker (https://travelpayouts.com)
TP_MARKER = '708106'

# Travelpayouts → Kiwi.com : identifiant du programme dans les liens de clic
# (c111.travelpayouts.com/click?...&promo_id=3791). Un lien direct vers kiwi.com
# avec affilid=708106 n'est PAS compté : 708106 est le marqueur Travelpayouts,
# pas un identifiant Kiwi (vérifié le 9 oct. 2026 : affilid reçu par Kiwi =
# « travelpayoutsdeeplink__…-708106 » seulement via le lien de clic).
TP_KIWI_PROMO_ID = '3791'

# Expedia Group (programme Travel Creator, via Partnerize) : paramètres du
# « Link builder » du compte. Format officiel :
#   https://www.expedia.com/affiliate?siteid=1&landingPage=<page Expedia>&camref=…&creativeref=…&adref=…
# Vérifié le 9 oct. 2026 : avec une page d'arrivée expedia.fr, redirection 302
# vers expedia.fr avec affcid/afflid/clickref (suivi posé). Un lien direct
# expedia.fr/Hotel-Search?...&camref=… n'est PAS suivi (aucune redirection).
EXPEDIA_CAMREF = '1110lB57J'
EXPEDIA_CREATIVEREF = '1100l68075'
EXPEDIA_ADREF = 'PZqrOrxQe3'

# Booking.com — CJ Affiliate ID (PID 101696591, approbation en attente)
# Remplacer '304142' par l'ID CJ réel une fois approuvé
BOOKING_AID = '304142'

# ── À venir ──────────────────────────────────────────────────────────────────
# Booking.com direct affiliate : à configurer si approbation CJ échoue
# BOOKING_DIRECT_AID = ''
