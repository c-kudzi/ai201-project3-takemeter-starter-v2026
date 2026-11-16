"""Turn raw Reddit thread text (copied from a browser) into a pool of posts.

Usage:
    python tools/ingest.py                 # re-parse every file in data/raw/
    python tools/ingest.py --show 01       # print the posts parsed from one file

Each file in data/raw/ is one thread, pasted exactly as copied. The output,
data/collected.csv, has one row per comment: text, source. Comment text is
kept whole -- only the Reddit chrome around it (usernames, "6y ago", vote
counts, "N more replies") is removed. Comments under MIN_WORDS words, deleted
comments, and exact duplicates are dropped and reported.
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "collected.csv"
MIN_WORDS = 3

SCORE = re.compile(r"^-?\d+(\.\d+)?[kK]?$")
MORE = re.compile(r"^\d+ more repl(y|ies)$")
AGO = re.compile(r"^\d+\s*(y|mo|w|d|h|m|min|hr)s?\.? ago$")
AVATAR = re.compile(r"^u/\S+ avatar$")
CHROME = re.compile(r"^(OP|Edited.*|·|Top \d+% Commenter|Promoted)$")


def header_start(lines, bullet):
    """Index of the first header line (avatar/username/OP) before a bullet."""
    j = bullet - 1  # username or OP
    if j >= 0 and lines[j] == "OP":
        j -= 1
    if j - 1 >= 0 and AVATAR.match(lines[j - 1]):
        j -= 1
    return j


def parse(text):
    lines = [l.rstrip() for l in text.splitlines()]
    bullets = [i for i, l in enumerate(lines) if l.strip() == "•"]
    posts = []
    for n, b in enumerate(bullets):
        start = b + 1
        if start < len(lines) and AGO.match(lines[start].strip()):
            start += 1
        end = header_start(lines, bullets[n + 1]) if n + 1 < len(bullets) else len(lines)
        body = lines[start:end]
        # strip trailing vote counts / "more replies" / blanks
        while body and (not body[-1].strip() or SCORE.match(body[-1].strip())
                        or MORE.match(body[-1].strip())):
            body.pop()
        body = [l for l in body if not CHROME.match(l.strip())]
        post = "\n".join(body).strip()
        post = re.sub(r"\n{3,}", "\n\n", post)
        posts.append(post)
    return posts


def main():
    files = sorted(RAW.glob("*.txt"))
    if "--show" in sys.argv:
        key = sys.argv[sys.argv.index("--show") + 1]
        for f in files:
            if f.name.startswith(key):
                for i, p in enumerate(parse(f.read_text()), 1):
                    print(f"[{i}] {p}\n")
        return

    seen, rows = set(), []
    for f in files:
        kept = short = deleted = dup = 0
        for p in parse(f.read_text()):
            if not p or p in ("[deleted]", "[removed]"):
                deleted += 1
            elif len(p.split()) < MIN_WORDS:
                short += 1
            elif p.lower() in seen:
                dup += 1
            else:
                seen.add(p.lower())
                rows.append({"text": p, "source": f.stem})
                kept += 1
        print(f"{f.name}: kept {kept}, dropped {short} short / {deleted} empty / {dup} dup")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["text", "source"])
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows)} posts in {OUT.relative_to(ROOT)}  (target: 200+)")


if __name__ == "__main__":
    main()
