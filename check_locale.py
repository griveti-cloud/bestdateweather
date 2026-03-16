#!/usr/bin/env python3
"""
check_locale.py — Validation de la structure des fichiers locales/*.json

Vérifie :
1. Toutes les locales ont les mêmes clés dans labels{} et monthly{}
2. Les clés lbl_* (non-lbl_m_*) utilisées dans generate_pages.py existent dans labels{}
3. Alerte si une clé lbl_* est à la racine du JSON (devrait être dans labels{})
4. temp_unit doit être à la racine (lu par page_config.py)
"""

import json, re, sys
from pathlib import Path

LOCALE_DIR = Path("locales")
LOCALES = ["fr", "en", "en-us", "de", "es"]
GEN_FILE = "generate_pages.py"

errors = []
warnings = []

data = {}
for lang in LOCALES:
    with open(LOCALE_DIR / f"{lang}.json") as f:
        data[lang] = json.load(f)

# 1. Cohérence labels{} entre locales
fr_labels = set(data["fr"].get("labels", {}).keys())
for lang in LOCALES[1:]:
    missing = fr_labels - set(data[lang].get("labels", {}).keys())
    if missing:
        errors.append(f"[{lang}] labels manquantes vs fr: {sorted(missing)[:8]}")

# 2. Cohérence monthly{} entre locales
fr_monthly = set(data["fr"].get("monthly", {}).keys())
for lang in LOCALES[1:]:
    missing = fr_monthly - set(data[lang].get("monthly", {}).keys())
    if missing:
        errors.append(f"[{lang}] monthly manquantes vs fr: {sorted(missing)[:8]}")

# 3. Clés lbl_* (non lbl_m_*) utilisées dans generate_pages.py → doivent être dans labels{}
with open(GEN_FILE) as f:
    gen = f.read()

# Trouver C['lbl_X'] et C.get('lbl_X') mais PAS lbl_m_
used = set(re.findall(r"(?:C|cfg)(?:\['|.get\(')lbl_(?!m_)(\w+)(?:'\]|'[,)])", gen))
fr_labels_keys = set(data["fr"]["labels"].keys())
orphans = {k for k in used if k not in fr_labels_keys and k not in ("temp_unit",)}
if orphans:
    warnings.append(f"[fr] lbl_* absentes de labels{{}}: {sorted(orphans)[:8]}")

# 4. Clés lbl_* à la racine (erreur structurelle)
for lang in LOCALES:
    bad = [k for k in data[lang] if k.startswith("lbl_")]
    if bad:
        errors.append(f"[{lang}] lbl_* à la RACINE (mettre dans labels{{}}): {bad[:5]}")

# 5. temp_unit doit être à la racine
for lang in LOCALES:
    if "temp_unit" not in data[lang]:
        errors.append(f"[{lang}] temp_unit manquant à la racine")

if errors:
    print("❌ ERREURS:")
    for e in errors: print(f"  {e}")
if warnings:
    print("⚠️  AVERTISSEMENTS:")
    for w in warnings: print(f"  {w}")
if not errors and not warnings:
    print("✅ Toutes les locales sont cohérentes")

sys.exit(1 if errors else 0)
