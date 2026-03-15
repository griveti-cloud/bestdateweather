#!/usr/bin/env python3
"""Re-fetch all climate data with P50. Resumable. ~25min."""
import csv,sys,os,time,json,subprocess
PF="data/refetch_progress.json"

def slugs():
  s=[]
  with open("data/destinations.csv",encoding="utf-8-sig") as f:
    for r in csv.DictReader(f): s.append(r["slug_fr"])
  return s

def load():
  if os.path.exists(PF):
    with open(PF) as f: return json.load(f)
  return {"done":[],"errors":[],"phase":"fetch"}

def save(p):
  with open(PF,"w") as f: json.dump(p,f)

