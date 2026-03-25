"""
BestDateWeather — Configuration centralisée
============================================
IDs partenaires et constantes de configuration.
Importer ce fichier depuis les générateurs plutôt que de dupliquer les valeurs.

Mise à jour des IDs :
  - GetYourGuide  : dashboard.getyourguide.com → Affiliate Program
  - Travelpayouts : travelpayouts.com → Programs → Tools
  - Booking.com   : CJ Affiliate (PID 101696591) → get link
"""

# ── Affiliés ─────────────────────────────────────────────────────────────────

# GetYourGuide — partner ID (https://partner.getyourguide.com)
GYG_PARTNER_ID = '2MQKL00'

# Travelpayouts — marker / shmarker (https://travelpayouts.com)
TP_MARKER = '708106'

# Booking.com — CJ Affiliate ID (PID 101696591, approbation en attente)
# Remplacer '304142' par l'ID CJ réel une fois approuvé
BOOKING_AID = '304142'

# ── À venir ──────────────────────────────────────────────────────────────────
# Booking.com direct affiliate : à configurer si approbation CJ échoue
# BOOKING_DIRECT_AID = ''
