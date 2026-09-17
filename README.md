**English** · [中文](README.zh-TW.md)

# Fly Explorer

**The neurons are real. The positions are real. What makes them light up is a simulation running on their real wiring.**

Live: **https://fly-brain-explorer.vercel.app** (best on a phone, held upright. https://fly-explorer-sage.vercel.app serves the same build.)

A 3D site about the MaleCNS male fruit-fly connectome, written for children and teenagers but with the numbers kept honest enough for a specialist. The connectome contains 166,691 neurons across the whole central nervous system, brain and ventral nerve cord. **140,024 of them carry measured 3D soma coordinates, and those are the ones the site draws.** On top of that it replays an escape reflex we simulated ourselves: something looms, the giant fiber fires, and the nerve cells that drive the jump muscle and the wing muscles follow.

Three ways in:

- **Kids** — a scroll-driven story, one step at a time, with quizzes.
- **In depth** — the same path with the full numbers, the source of each one, and the model's limits.
- **Explore freely** — the 3D stage plus 34 cards you can open in any order.

Everything is bilingual (English / 中文). The site defaults to English; add `?lang=zh` for Chinese.

## What is data and what we drew

Nothing on the screen blurs that line, and the legend says so on every screen:

| On screen | Meaning |
|---|---|
| **Green glow** | Real neuron positions, simulated activity |
| **Magenta** | Injected by us, because the model cannot compute it (the looming detector's input), or added by us (the wind-down after 250 ms) |
| **Cool grey line art** | The fly's body, drawn by us. A connectome has no body in it |
| **Amber** | Motor neuron to muscle. Not in the connectome either. Only the timing is real |

Every number on a card carries one of three marks:

- **●** computed from the data by a script in this repo
- **◆** from a paper we read first-hand (the reading is registered in `docs/verification_log.md`)
- **○** secondhand, illustrative, or not verified

The rule behind the colours is in `docs/visual_provenance.md`. It exists because the most tempting thing to do with a connectome is to animate something that looks alive and let the viewer assume it was measured.

## Model limits, stated up front

- The engine is a leaky integrate-and-fire model using the parameters of Shiu et al. 2024. **Chemical synapses only**: no electrical synapses, no neuromodulation, no synaptic plasticity.
- **The model cannot learn.** The weight table is read-only once loaded. The 61,210 Kenyon-cell-to-output-neuron connections that carry olfactory learning in a real fly are present in the data and completely inert here.
- **The visual front end does not carry the signal.** Driving the optic columns gets LC4 to 1.23 Hz and LPLC2 to zero, so the looming step is injected instead. It is drawn in magenta and labelled.
- **PSI, the relay the textbook puts between the giant fiber and the wing depressor, never fires in this scenario.** Zero out its inhibitory inputs and it fires in all three seeds tested, so inhibition is what holds it down. But the wing readout does not change, and in the fly that GF→PSI synapse is a mixed electrical-and-chemical one whose electrical half is the dominant type in this circuit. A connectome records only chemical synapses, so **this model cannot test the textbook route, and its silence is not evidence against the textbook.** Ablation data: `docs/verification_log.md`, section on PSI inhibition.
- **The model never stops.** In 20 runs to 600 ms, not one stopped on its own. Playback ends at 250 ms and the wind-down after that is ours, in magenta.
- Which direction is "straight ahead" in the eye's hex coordinates is **unverified**. The site says so rather than guessing.
- **The English text has not been reviewed by a native speaker.**

## Status

| | |
|---|---|
| 3D point cloud, escape replay, body line art, muscle diagram, voltage meter | done |
| Lab: swap the stimulus set and see results that were really run 20 times each (9 conditions, 4 playable on the stage) | done |
| 34 cards (kids / in depth × en / zh), every number with a source and a mark | done, through four rounds of validity audit |
| Captions and interface in both languages | done. Translation quality not yet reviewed by a native speaker or a second model |
| Deterministic gates (below) | all passing |
| Voice narration | not started |

## Run it

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # dist/
```

A 308 px upright phone is the acceptance target; on a desktop, `?preset=low` takes the phone path.

Deep links: `?track=kid|more|free`, `?lang=en|zh`, `?cap=0` (captions off), `?card=<id>`, `?t=<ms>` (jump to a moment), `?lab=1` (open the lab), `?lab=<condition>&labplay=1` (play one condition on the stage, e.g. `?lab=rand_311&labplay=1`).

## The lab

Open it with `?lab=1`. Nine stimulus conditions, the same protocol as the replay, changing only which neurons get stimulated. **Every cell was actually run 20 times**, and the page shows the median with the range across those runs (`scripts/build_playground.py` → `public/data/playground.json`).

**This is not a live simulation in your browser.** Each cell was computed ahead of time on the full connectome. That choice is deliberate: the edge file shipped to the browser carries excitatory edges only, so simulating with it would ignite instantly and would contradict this project's own finding, since PSI stays silent precisely because its strongest early input is inhibitory.

Four of the conditions also ship playable stage data. When a non-baseline condition plays, the standard captions are swapped out and the spike counter is hidden, because both were written for the baseline run and reusing them elsewhere would be a lie.

You can recompute every median and range from the raw per-run numbers in the repo. You cannot re-run the simulation: the engine and the weighted connectivity file live in a private research repo.

## Gates (run before and after touching content)

```bash
python3 scripts/jargon_lint.py          # jargon banned in the kids layer; first use must be explained on the spot (en+zh)
python3 scripts/audit_numbers.py        # every number in prose must exist in a fact field or under docs/ (en+zh)
python3 scripts/audit_claims.py         # source paths must exist, must not point at the private repo, must not be empty files
python3 scripts/verify_stages.py        # millisecond values in captions must equal the shipped scenario's actual spike times
python3 scripts/retraction_lint.py      # retracted wording must not reappear (content, docs, src, public, dist)
python3 scripts/citation_record_lint.py # every ◆ needs a registered reading with a year/DOI/PMID on the same line
python3 scripts/lang_residue.py         # no Chinese left on 74 English screens (6 main + 34 cards × 2 layers; needs a build + Chrome)
python3 scripts/verify_playground.py    # lab summaries must be recomputable from the runs; seed 1 must equal the shipped scenario
python3 scripts/disclosure_lint.py      # a limit admitted in the in-depth layer may not go unmentioned in a reader-facing layer
python3 scripts/verify_quotes.py        # every "the paper says X" must match the source verbatim (needs one --fetch to cache sources)
```

Each has a `--self-test` that runs **specific** negative cases, for example "source points at a file that does not exist", "lab median edited by hand", "Chinese left on an English page". That proves **those** errors get caught. It does not prove that wrong things in general get caught, and this README used to claim the stronger thing.

On 2026-09-17 a model that had not helped build any of this was asked to attack the gates. It produced 25 obviously wrong strawmen and **all eight gates of the day passed every one of them.** The structural finding: the gates guarded `content/` and part of `docs/`, while `src/`, `public/` and `dist/` were unguarded, so retracted wording could survive by moving into a code string or a build artefact. The retraction scan and the card-count check now cover those directories, and the English-residue sweep went from 6 screens to 74. `audit/va_20260918.md` has the full list, including the holes still open.

## Checking the science, and evaluating the checker

The gates above answer "do the numbers add up, did a retraction propagate, is there Chinese left on the English page". They cannot answer **"this sentence is scientifically wrong but the wording is clean"**. That is a separate lane, and its method and measured results are in `docs/sci_eval.md`:

```bash
python3 scripts/sci_claims.py       # pick the sentences worth checking against literature (73, not the whole site)
python3 scripts/verify_quotes.py    # "the paper says X" must appear verbatim in the fetched source
python3 scripts/disclosure_lint.py  # an admitted model limit may not be dropped on the way to the reader
python3 scripts/sci_eval.py         # blind-test a checker: per-class recall, false-positive rate, two baselines
```

The evaluation does not measure accuracy, because "is this sentence true" has no ground truth. It measures discrimination: take sentences verified as true, inject one specific class of error while keeping the wording clean, and see what a checker catches. It reports **per error class** (any class at zero recall fails the whole evaluation) and always prints two baselines alongside, "flag nothing" and "flag everything", so a recall figure can never be read on its own.

First real run: a fresh-context reviewer with web access to the literature, given 33 sentences and forbidden to read this repo, scored **16/21 recall with 1/13 false positives**; on the items decidable from public literature alone it was **10/10 with no false positives**. A deterministic floor that only applies the candidate filter and does no science at all scores 0.52 / 0.33.

That run also overturned two of our own judgements and one of its own. Both corrections are written up in `docs/sci_eval.md`, because the useful output of an audit is the claim you have to take back.

## Data and provenance

- **Connectome**: MaleCNS v1.0, Berg et al. 2026, CC BY 4.0, https://male-cns.janelia.org . This repo contains derived data only (coordinates, the shipped scenario's spike record). The 1.1 GB weight table is a separate download.
- **Model**: the LIF parameters of Shiu et al. 2024 (Nature 634:210-219, PMID 39358519), read first-hand and registered in `docs/verification_log.md`.
- **The chain behind each number**: `docs/verification_log.md`, `docs/data_facts.md`, `docs/research_context_cards.md`, and the machine-generated claim table in `audit/claims.md`.

## Found something wrong?

Open an issue. Corrections to the science are the most welcome kind, and if you can point at a paper or a line in the data, that is enough. The record of what previous reviews caught, including the times we had to retract our own findings, is in `audit/`.

## Licence

Code MIT (`LICENSE`). Content CC BY 4.0 (`LICENSE-CONTENT.md`). Data CC BY 4.0 (MaleCNS, Berg et al. 2026).
