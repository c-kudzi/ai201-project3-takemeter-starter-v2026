"""Label the cold sheet and review the pre-labels, one keypress per post.

    .venv/bin/python tools/label_session.py

Part 1 -- cold: the 20 rows in data/cold_sheet.csv. No suggestion shown.
Part 2 -- review: the rows in data/prelabeled.csv. Enter keeps the suggested
label; a letter changes it.

Keys:  a = analysis   h = hot_take   r = reaction   q = question
       d = show the definitions again   s = save and stop (resume later)

Progress is saved after every post, so you can quit and come back.
"""
import sys
import textwrap
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COLD = ROOT / "data" / "cold_sheet.csv"
PRE = ROOT / "data" / "prelabeled.csv"
KEYS = {"a": "analysis", "h": "hot_take", "r": "reaction", "q": "question"}


def definitions():
    lines = (ROOT / "label_definitions.txt").read_text().splitlines()
    return "\n".join("  " + l for l in lines if l and not l.startswith("#"))


def show(i, n, text, header):
    print("\n" + "─" * 72)
    print(f"{header}  [{i}/{n}]\n")
    for para in str(text).split("\n"):
        print(textwrap.fill(para, 72) if para.strip() else "")
    print()


def ask(prompt, allow_enter):
    while True:
        k = input(prompt).strip().lower()
        if k == "" and allow_enter:
            return ""
        if k in KEYS or k == "s":
            return k
        if k == "d":
            print(definitions())
            continue
        print("  a / h / r / q" + (" / Enter to keep" if allow_enter else "") + "  (d = definitions, s = stop)")


def cold_pass():
    df = pd.read_csv(COLD, keep_default_na=False)
    todo = df.index[df["label"].str.strip() == ""].tolist()
    if not todo:
        print("Cold sheet: already done.")
        return True
    print("\nPART 1 — COLD. Just you and the definitions. No suggestions.\n")
    print(definitions())
    for n, idx in enumerate(todo, 1):
        show(n, len(todo), df.at[idx, "text"], "COLD")
        k = ask("label (a/h/r/q): ", allow_enter=False)
        if k == "s":
            return False
        df.at[idx, "label"] = KEYS[k]
        df.to_csv(COLD, index=False)
    return True


def review_pass():
    df = pd.read_csv(PRE, keep_default_na=False)
    todo = df.index[df["note"].str.contains("NOT YET REVIEWED")].tolist()
    if not todo:
        print("Review: already done.")
        return True
    print("\nPART 2 — REVIEW. Read every one. Enter keeps the suggestion.\n")
    changed = 0
    for n, idx in enumerate(todo, 1):
        old = df.at[idx, "label"]
        show(n, len(todo), df.at[idx, "text"], "REVIEW")
        k = ask(f"suggested: {old}   keep [Enter] or change (a/h/r/q): ", allow_enter=True)
        if k == "s":
            return False
        if k == "" or KEYS[k] == old:
            df.at[idx, "note"] = "pre-labelled (Claude), checked"
        else:
            df.at[idx, "label"] = KEYS[k]
            df.at[idx, "note"] = f"pre-labelled (Claude), corrected from {old}"
            changed += 1
        df.to_csv(PRE, index=False)
    print(f"\nReview done — you changed {changed} of {len(todo)}.")
    return True


if __name__ == "__main__":
    try:
        if cold_pass() and review_pass():
            print("\nAll labelled. Next: .venv/bin/python tools/build_labels.py")
        else:
            print("\nSaved. Run this again to pick up where you stopped.")
    except (KeyboardInterrupt, EOFError):
        print("\nSaved. Run this again to pick up where you stopped.")
        sys.exit(0)
