# Conservation Field-Work Resume Demo

Workshop artifact, generated 2026-05-01.

A fictional candidate (**Sage Holloway**) with 6+ years of conservation field work, paired against 10 currently-listed Utah field-work job postings, with a curated resume tailored to each.

## Contents

- [`base/sage-holloway-base.md`](base/sage-holloway-base.md) — base resume (also `.json` for structured access)
- [`jobs/utah-conservation-jobs.md`](jobs/utah-conservation-jobs.md) — list of 10 target postings with sources
- [`curated/`](curated/) — 10 tailored variants, one per posting (see [`curated/README.md`](curated/README.md))

## How it was built

1. Extended `generate_resume.py` with a `conservation` role profile (Utah cities/orgs/schools, AIM/MIM bullets, S-130/WFA cert pool).
2. Generated the base resume with `--seed 21` for reproducibility.
3. Pulled job listings from Conservation Job Board, Indeed, Utah DNR, UFRI / Association for Fire Ecology, and a couple of related sources.
4. Wrote 10 curated variants — same underlying facts (jobs, dates, employers, education are constant), but headline / summary / skill order / cert order / bullet phrasing tuned to each posting.

## Reproducing the base resume

```bash
python3 generate_resume.py \
  --name "Sage Holloway" \
  --role "Conservation Field Technician" \
  --years 6 \
  --seed 21 \
  -o demo/conservation/base/sage-holloway-base.md \
  --json
```
