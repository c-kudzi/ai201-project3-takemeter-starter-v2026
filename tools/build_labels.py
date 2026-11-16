"""Assemble labels.csv from the cold sheet and the reviewed pre-labels.

    python tools/build_labels.py

Refuses to write labels.csv until:
  * every row in data/cold_sheet.csv has a label (filled in by hand, no tools)
  * every row in data/prelabeled.csv has been reviewed -- i.e. its note no
    longer says NOT YET REVIEWED. Change the note to
    "pre-labelled (Claude), checked" if you agreed, or
    "pre-labelled (Claude), corrected from <old_label>" if you changed it.
Then prints per-label counts against the 70% cap.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LABELS = ["analysis", "hot_take", "reaction", "question"]
CAP = 0.70

cold = pd.read_csv(ROOT / "data" / "cold_sheet.csv", keep_default_na=False)
pre = pd.read_csv(ROOT / "data" / "prelabeled.csv", keep_default_na=False)

problems = []
blank = cold[cold["label"].str.strip() == ""]
if len(blank):
    problems.append(f"{len(blank)} cold rows still unlabelled (ids {blank['id'].tolist()})")
unreviewed = pre[pre["note"].str.contains("NOT YET REVIEWED")]
if len(unreviewed):
    problems.append(f"{len(unreviewed)} pre-labelled rows not reviewed yet")

df = pd.concat([cold, pre], ignore_index=True)
df["label"] = df["label"].str.strip()
bad = df[(df["label"] != "") & ~df["label"].isin(LABELS)]
if len(bad):
    problems.append(f"unknown labels {sorted(bad['label'].unique())} (ids {bad['id'].tolist()})")

counts = df[df["label"] != ""]["label"].value_counts()
total = counts.sum()
print(f"{len(df)} rows ({len(cold)} cold, {len(pre)} pre-labelled)\n")
for label in LABELS:
    n = int(counts.get(label, 0))
    share = n / total if total else 0
    flag = "  <-- over 70% cap" if share > CAP else ""
    print(f"  {label:<10} {n:>4}  {share:6.1%}{flag}")

if problems:
    print("\nNot writing labels.csv yet:")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)

df.sort_values("id")[["text", "label", "note"]].to_csv(ROOT / "labels.csv", index=False)
print(f"\nWrote labels.csv: {len(df)} rows")
if len(df) < 200:
    print(f"(The target is 200; {200 - len(df)} more to collect, or explain the stop rule in the README.)")
