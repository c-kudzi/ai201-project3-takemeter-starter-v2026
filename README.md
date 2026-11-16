# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

TakeMeter sorts comments from **r/soccer**, the general football subreddit,
into four kinds of post: **analysis** (a point backed by a checkable fact),
**hot_take** (a confident opinion with nothing behind it), **reaction**
(feeling, jokes, nostalgia), and **question**. The aim is to tell apart the
comments worth reading for information from the ones that are just noise or
mood, using a small DistilBERT model fine-tuned on hand-checked labels.

---

## Label Taxonomy

> ⚠️ DRAFT taxonomy. Claude proposed these four labels from the first 87
> collected comments; Kudzi to confirm or change them before the cold labels
> are done. Definitions are mirrored in `label_definitions.txt`.

### `analysis`

**Definition:** Uses a specific, checkable fact (a fee, date, stat, record or rule) to make, support or correct a point.

**Example 1:**
> Still the most expensive transfer adjusted to football inflation. We don't have exact stats on football inflation but RM was afaik the richest club by revenue in 2001 and it was 35+% of total yearly revenue of RM. Nobody really came close. For comparison, Neymar transfer was about 25% of PSG's revenue in 2017 and PSG isn't even top 5 in the world in revenue. Idk if Zidane ever can be topped honestly.

**Example 2:**
> Mbappe got screwed of a record because he was loaned by Monaco to PSG in 2017 with a guaranteed transfer fee in 2018 of 145M

### `hot_take`

**Definition:** A confident opinion, judgement or prediction offered without any checkable fact behind it.

**Example 1:**
> Neymar transfer fee Totally fucked up the market ....ever since most players are overpriced

**Example 2:**
> Italian football used to go all out and spend big but paid for it for a while.

### `reaction`

**Definition:** An emotional response, joke or bit of nostalgia, where the point is how the poster feels rather than a claim.

**Example 1:**
> 70m in 2001 holy shit

**Example 2:**
> Something very nostalgic about seeing Ronaldo in that inter kit

### `question`

**Definition:** The post's main move is asking for information, an opinion, or something that is missing, with no declarative claim of its own.

**Example 1:**
> Why was denilson so expensive? Was he insane in Brazil?

**Example 2:**
> Can somebody make a similar table but with highest transfer in each year?

### The hardest boundary

**Which two labels:** `analysis` vs `reaction` — a post that contains a real
number but wraps it in an exclamation ("70m in 2001 holy shit").

**The decision rule I used every time:**
If the post's point is **how the poster feels about the fact** (insane, wild,
absurd, holy shit), it's `reaction`, even when the fact is checkable. It's
`analysis` only when the post **draws a conclusion, comparison or correction
from the fact** — the fact is doing work in an argument, not sitting next to
a feeling.

Two secondary rules:
- **question vs anything:** a post is `question` only if it has no declarative
  claim besides the question. "Kaka missing? Was highest before CR7 was." has
  one, so it's labelled by that claim (`analysis`).
- **analysis vs hot_take:** support has to be checkable. "Due to his injuries"
  or "for what they've delivered" is not a checkable fact, so a post resting on
  it is `hot_take`.

---

## The Dataset

**Where the posts came from:** Public r/soccer comment sections, copied from
the browser and saved unedited in `data/raw/` (one file per thread). Reddit
blocks scripted access, so collection is copy-paste. `tools/ingest.py` strips
usernames, vote counts and "N more replies", keeps each comment whole, and
drops deleted comments, exact duplicates and comments under three words.

So far: 1 thread (world-record transfer fees), 87 comments.
<!-- TODO: more threads — post-match, tactics/stats, transfer/manager news. -->

**How I labelled them:**
- 20 rows, chosen at random (`data/cold_sheet.csv`), labelled cold by me with
  no tools — marked `cold` in the note column. <!-- TODO Kudzi -->
- The rest were pre-labelled by Claude from the definitions above
  (`data/prelabeled.csv`), then read and corrected by me one by one. Each note
  says `pre-labelled (Claude), checked` or `… corrected from <label>`.
- `tools/build_labels.py` assembles `labels.csv` and refuses to until every
  cold row is filled and every pre-label is reviewed.

**Counts per label:** <!-- TODO: final counts from tools/build_labels.py.
Draft pre-labels for the 67 non-cold rows: analysis 20, reaction 19,
question 16, hot_take 12. -->

| Label | Count | Share |
|---|---|---|
| analysis |  |  |
| hot_take |  |  |
| reaction |  |  |
| question |  |  |
| **Total** |  | 100% |

**Three hard cases**

<!-- Flagged by Claude while pre-labelling. Kudzi: keep the ones that made
you pause too, and replace any that didn't with your own. -->

**1.**
> *The post:* "Jesus the jump from Pogba to Neymar is just insane...I guess everyone kinda knew that at the time, but still wild to see how the jump itself was bigger than Pogba’s actual fee!"
>
> *Could have been:* `analysis` or `reaction`
>
> *I chose, because:* `reaction` — it does contain a checkable comparison (the jump is bigger than Pogba's fee), but the point of the post is "insane… wild". Under the hardest-boundary rule, the fact sits next to a feeling rather than supporting a conclusion.

**2.**
> *The post:* "C. Ronaldo was easily the best money spent here. In hindsight, 94 mil was a bargain."
>
> *Could have been:* `analysis` or `hot_take`
>
> *I chose, because:* `hot_take` — 94 mil is a real number, but it's the graphic's own number restated; the claim ("best money spent", "bargain") rests on no checkable fact about what Ronaldo delivered.

**3.**
> *The post:* "Erling Håland | Real Madrid -> Manchester City | €580M 2027"
>
> *Could have been:* `analysis` or `reaction`
>
> *I chose, because:* `reaction` — it's formatted exactly like a fact from the graphic, but it's an invented future transfer: a joke. A fact has to be checkable, and this one can't be. Worth watching: a model that keys on numbers and arrows will probably call this `analysis`.

---

## The Training Run

**Base model:** `distilbert-base-uncased` (the notebook default).

**Settings:** 3 epochs, learning rate 2e-5, batch size 16, max 128 tokens per
post, seed 42. Trained on **mps** (Apple Silicon GPU) — `results.json` records
the device too.

**Anything I changed from the defaults, and why:** Only the label map —
`LABELS = ["analysis", "hot_take", "reaction", "question"]`. No hyperparameters
changed.

**Split sizes:** <!-- TODO: from section 3 of the notebook after the real run. -->

---

## How I Used AI

**Moment 1**

- *What I asked for:* For Claude to collect r/soccer posts by script.
- *What came back:* Reddit refused scripted access, and Claude declined to work
  around it (or to scrape a forum whose robots.txt forbids AI training). It
  wrote `tools/ingest.py` instead, which parses comment sections I copy from
  the browser.
- *What I changed:* Collection became copy-paste, which keeps me reading every
  thread I add.

**Moment 2**

- *What I asked for:* <!-- TODO Kudzi: e.g. the boundary stress-test, or
  how you checked the drafted taxonomy against your own reading. -->
- *What came back:*
- *What I changed:*

**Pre-labelling disclosure:** Claude pre-labelled every non-cold row from the
written definitions. I read and corrected every one, and each row's note says
whether I kept or changed the label. The 20 cold rows were labelled by me alone,
before seeing any pre-labels.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
