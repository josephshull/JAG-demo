#!/usr/bin/env python3
"""Generate a fictional resume in Markdown.

Usage:
    python3 generate_resume.py --role "Senior Software Engineer" --seed 42
    python3 generate_resume.py --name "Jane Doe" --role "Product Manager" --years 8 -o output/jane.md
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field, asdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
TEMPLATES = ROOT / "templates"

FIRST_NAMES = [
    "Avery", "Jordan", "Sam", "Riley", "Taylor", "Morgan", "Casey", "Quinn",
    "Reese", "Skylar", "Devon", "Emerson", "Hayden", "Parker", "Rowan", "Sage",
    "Blair", "Drew", "Finley", "Harper", "Indigo", "Jamie", "Kai", "Lennox",
]
LAST_NAMES = [
    "Okafor", "Nakamura", "Vasquez", "Bergman", "Petrov", "Kowalski", "Singh",
    "Almeida", "Chen", "Rivera", "Holloway", "Marchetti", "Adeyemi", "Lindqvist",
    "Bouchard", "Castellanos", "Yamamoto", "Patel", "Andersen", "Delacroix",
]
CITIES = [
    ("Austin", "TX"), ("Brooklyn", "NY"), ("Seattle", "WA"), ("Denver", "CO"),
    ("Portland", "OR"), ("Boston", "MA"), ("Chicago", "IL"), ("Oakland", "CA"),
    ("Atlanta", "GA"), ("Minneapolis", "MN"), ("Pittsburgh", "PA"),
]
COMPANIES = [
    "Lumen Loop", "Northwind Labs", "Halcyon Systems", "Brightline Robotics",
    "Outpost Analytics", "Meridian Cloud", "Ferrous Studio", "Quanta Health",
    "Saltwater Software", "Riverstone AI", "Pinecone Logistics", "Foglamp Media",
    "Tessellate", "Ironwood Bio", "Catkin Networks", "Polaris Foundry",
]
SCHOOLS = [
    "Carnegie Mellon University", "University of Michigan", "Georgia Tech",
    "UT Austin", "UC Berkeley", "Northeastern University", "Purdue University",
    "University of Washington", "University of Illinois Urbana-Champaign",
    "Rutgers University", "Arizona State University", "Boston University",
]

ROLE_PROFILES: dict[str, dict] = {
    "software engineer": {
        "skills": [
            "Python", "Go", "TypeScript", "React", "PostgreSQL", "Kubernetes",
            "AWS", "Docker", "gRPC", "Redis", "CI/CD", "system design",
        ],
        "bullets": [
            "Built {feature} serving {n}M requests/day with p99 under {ms}ms",
            "Reduced {service} infrastructure cost by {pct}% via {tactic}",
            "Migrated {n} services from {old} to {new} with zero downtime",
            "Led design of {feature} adopted by {n} downstream teams",
            "Cut {pipeline} runtime from {hr}h to {min}m by parallelizing {step}",
            "Authored RFC for {feature}; shipped MVP in {weeks} weeks",
        ],
        "summary": (
            "{years}+ years building distributed systems and developer tooling. "
            "Comfortable across the stack with a strong bias toward reliability "
            "and clean APIs. Recent focus: {focus}."
        ),
        "summary_focus": [
            "platform abstractions for ML inference",
            "incremental migration of monoliths to event-driven services",
            "cost-aware autoscaling on Kubernetes",
            "developer-experience tooling for backend teams",
        ],
        "certs": ["AWS Solutions Architect", "CKAD", "Google Cloud Professional Engineer"],
    },
    "product manager": {
        "skills": [
            "roadmapping", "user research", "SQL", "experimentation", "Figma",
            "OKRs", "stakeholder alignment", "B2B SaaS", "growth", "Jira",
        ],
        "bullets": [
            "Shipped {feature} driving {pct}% lift in {metric} across {n} segments",
            "Ran {n} user interviews shaping the {area} roadmap for FY{year}",
            "Defined success metrics for {feature}; A/B test reached significance in {weeks} weeks",
            "Aligned engineering, design, and GTM on {area} relaunch",
            "Cut {feature} time-to-value from {hr}h to {min}m through onboarding redesign",
        ],
        "summary": (
            "{years}+ years in product, most recently leading {area} for "
            "{segment} customers. Data-driven generalist who pairs qualitative "
            "research with experimentation. Recent focus: {focus}."
        ),
        "summary_focus": [
            "AI-assisted workflows in vertical SaaS",
            "self-serve onboarding and PLG motions",
            "platform pricing and packaging",
            "trust & safety tooling for marketplaces",
        ],
        "certs": ["Pragmatic Institute Level III", "Reforge: Mastering Product Management"],
    },
    "data scientist": {
        "skills": [
            "Python", "SQL", "PyTorch", "scikit-learn", "Spark", "dbt",
            "experimentation", "causal inference", "Airflow", "Looker",
        ],
        "bullets": [
            "Built {model} model improving {metric} by {pct}% in production",
            "Designed offline + online evaluation for {feature}; flagged {n} regressions pre-launch",
            "Productionized {pipeline} pipeline processing {n}M events/day",
            "Partnered with {team} to define KPIs for {area}",
            "Authored internal {topic} guide adopted by {n} analysts",
        ],
        "summary": (
            "{years}+ years applying ML and causal inference to business problems. "
            "Equally comfortable in a notebook and a production pipeline. "
            "Recent focus: {focus}."
        ),
        "summary_focus": [
            "uplift modeling for retention",
            "LLM evaluation harnesses",
            "forecasting with hierarchical models",
            "experiment platform tooling",
        ],
        "certs": ["Coursera: Causal Inference Specialization"],
    },
    "designer": {
        "skills": [
            "Figma", "design systems", "prototyping", "user research",
            "interaction design", "accessibility", "motion", "FigJam", "HTML/CSS",
        ],
        "bullets": [
            "Led design of {feature} adopted by {n}K monthly users",
            "Owned {area} design system; reduced component variance by {pct}%",
            "Ran {n} usability tests informing {area} redesign",
            "Partnered with engineering on {feature}, shipped in {weeks} weeks",
            "Established accessibility audit cadence; raised score from {old} to {new}",
        ],
        "summary": (
            "{years}+ years designing for {segment} products. Systems thinker "
            "who likes to ship. Recent focus: {focus}."
        ),
        "summary_focus": [
            "AI-native interaction patterns",
            "design system governance at scale",
            "onboarding and activation flows",
            "data-dense dashboards for operators",
        ],
        "certs": ["NN/g UX Certification"],
    },
}

DEFAULT_PROFILE_KEY = "software engineer"


@dataclass
class Job:
    title: str
    company: str
    start: str
    end: str
    location: str
    bullets: list[str] = field(default_factory=list)


@dataclass
class Education:
    degree: str
    school: str
    year: int


@dataclass
class Resume:
    name: str
    role: str
    city: str
    state: str
    email: str
    phone: str
    website: str
    summary: str
    experience: list[Job]
    skills: list[str]
    education: list[Education]
    certifications: list[str]


def pick_profile(role: str) -> tuple[str, dict]:
    role_l = role.lower()
    for key, profile in ROLE_PROFILES.items():
        if key in role_l:
            return key, profile
    return DEFAULT_PROFILE_KEY, ROLE_PROFILES[DEFAULT_PROFILE_KEY]


def fill_bullet(template: str, rng: random.Random) -> str:
    fillers = {
        "feature": rng.choice([
            "the unified search API", "the billing pipeline", "the events ingestion service",
            "the customer dashboard", "the realtime sync layer", "the onboarding wizard",
        ]),
        "service": rng.choice(["payments", "search", "auth", "ingest", "notifications"]),
        "old": rng.choice(["Heroku", "EC2", "monolith", "Django", "MySQL"]),
        "new": rng.choice(["EKS", "Lambda", "microservices", "FastAPI", "Postgres"]),
        "tactic": rng.choice([
            "right-sizing instances", "spot fleet adoption", "cache layer rework",
            "query optimization", "tier consolidation",
        ]),
        "pipeline": rng.choice(["nightly ETL", "feature backfill", "training", "build"]),
        "step": rng.choice(["transform", "validation", "feature extraction", "test suite"]),
        "metric": rng.choice(["retention", "activation", "conversion", "DAU", "NPS"]),
        "area": rng.choice([
            "self-serve", "enterprise", "platform", "growth", "billing", "search",
        ]),
        "segment": rng.choice(["SMB", "mid-market", "enterprise", "prosumer"]),
        "team": rng.choice(["growth", "platform", "trust & safety", "GTM", "finance"]),
        "topic": rng.choice(["A/B testing", "causal inference", "feature engineering"]),
        "model": rng.choice(["ranking", "churn", "fraud", "recommendation", "demand"]),
        "n": rng.choice([3, 5, 8, 12, 20, 50, 120]),
        "pct": rng.choice([12, 18, 24, 30, 40, 55]),
        "ms": rng.choice([40, 80, 120, 200]),
        "hr": rng.choice([2, 4, 6, 9]),
        "min": rng.choice([8, 15, 30, 45]),
        "weeks": rng.choice([3, 6, 8, 10]),
        "year": rng.choice([24, 25, 26]),
        "old_score": 62,
        "new_score": 94,
    }
    fillers["old"] = fillers.get("old", "v1")
    fillers["new"] = fillers.get("new", "v2")
    try:
        return template.format(**fillers)
    except KeyError:
        return template


def build_resume(
    name: str,
    role: str,
    years: int,
    rng: random.Random,
) -> Resume:
    _key, profile = pick_profile(role)
    city, state = rng.choice(CITIES)
    handle = name.lower().replace(" ", ".")
    email = f"{handle}@example.com"
    phone = f"({rng.randint(200, 989)}) {rng.randint(200, 989)}-{rng.randint(1000, 9999)}"
    website = f"{handle.replace('.', '')}.dev"

    summary = profile["summary"].format(
        years=years,
        area=rng.choice(["platform", "growth", "search", "ML"]),
        segment=rng.choice(["B2B SaaS", "consumer", "enterprise", "developer tools"]),
        focus=rng.choice(profile["summary_focus"]),
    )

    n_jobs = max(2, min(4, years // 3 + 1))
    experience: list[Job] = []
    current_year = 2026
    # Career progression: most recent (i=0) is most senior; oldest (i=n-1) is most junior.
    progression = ["", "Senior ", "Staff ", "Lead "] if years > 8 else ["", "Senior "]
    for i in range(n_jobs):
        end_year = current_year if i == 0 else current_year - rng.randint(1, 2)
        start_year = end_year - rng.randint(1, 3)
        current_year = start_year
        # Reverse so highest seniority lands on the most recent job.
        rank = min(n_jobs - 1 - i, len(progression) - 1)
        title_prefix = progression[rank]
        # Strip an existing seniority word from the role so we don't get "Senior Senior X".
        base_role = role
        for prefix in ("Senior ", "Staff ", "Lead ", "Principal ", "Junior "):
            if base_role.startswith(prefix):
                base_role = base_role[len(prefix):]
                break
        job = Job(
            title=f"{title_prefix}{base_role}".strip(),
            company=rng.choice(COMPANIES),
            start=f"{start_year}",
            end="Present" if i == 0 else f"{end_year}",
            location=rng.choice([f"{c}, {s}" for c, s in CITIES] + ["Remote"]),
            bullets=[fill_bullet(b, rng) for b in rng.sample(profile["bullets"], k=min(4, len(profile["bullets"])))],
        )
        experience.append(job)

    skills = rng.sample(profile["skills"], k=min(8, len(profile["skills"])))

    edu_year = 2026 - years - rng.randint(0, 2)
    education = [Education(
        degree=rng.choice(["B.S. Computer Science", "B.A. Cognitive Science", "B.S. Math", "B.S. Information Systems"]),
        school=rng.choice(SCHOOLS),
        year=edu_year,
    )]

    certs = rng.sample(profile["certs"], k=min(rng.randint(0, 2), len(profile["certs"])))

    return Resume(
        name=name,
        role=role,
        city=city,
        state=state,
        email=email,
        phone=phone,
        website=website,
        summary=summary,
        experience=experience,
        skills=skills,
        education=education,
        certifications=certs,
    )


def render_markdown(resume: Resume) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(disabled_extensions=("md", "j2")),
        trim_blocks=False,
        lstrip_blocks=False,
        keep_trailing_newline=True,
    )
    template = env.get_template("resume.md.j2")
    return template.render(**asdict(resume))


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace(".", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a fictional resume.")
    parser.add_argument("--name", help="Full name (default: random)")
    parser.add_argument("--role", default="Software Engineer", help="Job role/title")
    parser.add_argument("--years", type=int, default=None, help="Years of experience (default: random 3-15)")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    parser.add_argument("-o", "--output", help="Output path (default: output/<slug>.md)")
    parser.add_argument("--json", action="store_true", help="Also write a .json sidecar with structured data")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    name = args.name or f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
    years = args.years if args.years is not None else rng.randint(3, 15)

    resume = build_resume(name=name, role=args.role, years=years, rng=rng)
    md = render_markdown(resume)

    out_path = Path(args.output) if args.output else ROOT / "output" / f"{slugify(name)}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"wrote {out_path}")

    if args.json:
        json_path = out_path.with_suffix(".json")
        json_path.write_text(json.dumps(asdict(resume), indent=2))
        print(f"wrote {json_path}")


if __name__ == "__main__":
    main()
