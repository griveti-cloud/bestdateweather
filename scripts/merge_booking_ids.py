#!/usr/bin/env python3
"""
merge_booking_ids.py
====================
Merges extracted Booking.com dest_ids into destinations.csv.

Usage:
    python3 scripts/merge_booking_ids.py booking_ids.csv

Input CSV format (from browser script output):
    slug_fr,booking_dest_id,dest_type,label

Backs up destinations.csv before modifying.
"""
import csv, os, sys, shutil

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(DIR, 'data', 'destinations.csv')

if len(sys.argv) < 2:
    print("Usage: python3 scripts/merge_booking_ids.py <booking_ids.csv>")
    sys.exit(1)

# Read new IDs
new_ids = {}
with open(sys.argv[1], encoding='utf-8') as f:
    for row in csv.DictReader(f):
        slug = row['slug_fr'].strip()
        dest_id = row['booking_dest_id'].strip()
        if slug and dest_id:
            new_ids[slug] = dest_id

print(f"📥 {len(new_ids)} dest_ids à merger")

# Backup
backup = CSV_PATH + '.bak'
shutil.copy2(CSV_PATH, backup)
print(f"💾 Backup: {backup}")

# Read and update
with open(CSV_PATH, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

updated = 0
already = 0
for row in rows:
    slug = row['slug_fr']
    if slug in new_ids:
        if row.get('booking_dest_id', '').strip():
            already += 1
        else:
            row['booking_dest_id'] = new_ids[slug]
            updated += 1

# Write back
with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ {updated} dest_ids ajoutés")
if already:
    print(f"⏭️  {already} déjà présents (non écrasés)")
print(f"📊 Total avec dest_id: {sum(1 for r in rows if r.get('booking_dest_id','').strip())}/{len(rows)}")
