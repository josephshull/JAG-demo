# JAG-demo

Workshop demo repo. Hosts files generated during an agentic-AI live demo, plus a small resume generator the agent can drive.

## Resume generator

`generate_resume.py` produces a fictional resume in Markdown. It only depends on Jinja2 (already present on the demo box).

### Quickstart

```bash
# Fully random — picks name, city, companies, etc.
python3 generate_resume.py --role "Software Engineer"

# Reproducible — same seed → same resume
python3 generate_resume.py --role "Senior Software Engineer" --seed 42

# Pin specific fields
python3 generate_resume.py \
  --name "Jane Doe" \
  --role "Product Manager" \
  --years 8 \
  -o output/jane.md

# Also emit a structured JSON sidecar (handy for the agent to read back)
python3 generate_resume.py --role "Data Scientist" --seed 5 --json
```

### Options

| Flag | Default | Notes |
| --- | --- | --- |
| `--name` | random | Full name; e.g. `"Avery Chen"` |
| `--role` | `Software Engineer` | Free-form; matches against role profiles below |
| `--years` | random 3–15 | Drives seniority and number of jobs |
| `--seed` | none | Set for reproducible output |
| `-o`, `--output` | `output/<slug>.md` | Output path |
| `--json` | off | Also writes `<output>.json` with structured data |

### Role profiles

The script picks a profile based on substring match in `--role`. Currently shipped:

- `software engineer`
- `product manager`
- `data scientist`
- `designer`

Anything else falls back to the software engineer profile. To add a new role, drop an entry into `ROLE_PROFILES` in `generate_resume.py`.

## Layout

```
generate_resume.py     # CLI entry point
templates/
  resume.md.j2         # Markdown template
samples/               # Committed example outputs
output/                # Ad-hoc generation (gitignored)
```

## Notes for the demo

- All names, companies, and details are fictional. Email addresses use `example.com`.
- Same `--seed` → same output, so demos are reproducible.
- The agent can either invoke this script directly or write resumes from scratch — the script is here to remove typing and keep things consistent across multiple runs.
