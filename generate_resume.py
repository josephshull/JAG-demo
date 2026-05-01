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
UTAH_CITIES = [
    ("Salt Lake City", "UT"), ("Logan", "UT"), ("Moab", "UT"), ("Cedar City", "UT"),
    ("Vernal", "UT"), ("Price", "UT"), ("Ogden", "UT"), ("Provo", "UT"),
    ("Kanab", "UT"), ("Richfield", "UT"),
]
COMPANIES = [
    "Lumen Loop", "Northwind Labs", "Halcyon Systems", "Brightline Robotics",
    "Outpost Analytics", "Meridian Cloud", "Ferrous Studio", "Quanta Health",
    "Saltwater Software", "Riverstone AI", "Pinecone Logistics", "Foglamp Media",
    "Tessellate", "Ironwood Bio", "Catkin Networks", "Polaris Foundry",
]
CONSERVATION_ORGS = [
    "Great Basin Institute", "American Conservation Experience (ACE)",
    "Conservation Legacy / Southwest Conservation Corps", "Utah Conservation Corps",
    "BLM (seasonal, via Great Basin Institute)", "USFS Manti-La Sal NF (seasonal)",
    "Utah Division of Wildlife Resources (seasonal)", "Grand Canyon Trust",
    "Sageland Collaborative", "Stantec — Ecological Services",
    "SWCA Environmental Consultants", "Bio-West, Inc.",
    "Wild Utah Project", "Capitol Reef Field Station (USU)",
]
SCHOOLS = [
    "Carnegie Mellon University", "University of Michigan", "Georgia Tech",
    "UT Austin", "UC Berkeley", "Northeastern University", "Purdue University",
    "University of Washington", "University of Illinois Urbana-Champaign",
    "Rutgers University", "Arizona State University", "Boston University",
]
CONSERVATION_SCHOOLS = [
    "Utah State University", "University of Utah", "Northern Arizona University",
    "University of Montana", "Colorado State University", "Prescott College",
    "Westminster College (SLC)", "Southern Utah University",
    "University of Wyoming", "Humboldt State University",
]
CONSERVATION_DEGREES = [
    "B.S. Wildlife Biology", "B.S. Rangeland Ecology and Management",
    "B.S. Environmental Science", "B.S. Natural Resource Management",
    "B.S. Conservation Biology", "B.A. Environmental Studies",
    "B.S. Ecology and Evolutionary Biology", "B.S. Forestry",
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
    "conservation": {
        "skills": [
            "vegetation surveys", "GPS/GNSS (Trimble, Garmin)", "ArcGIS Pro",
            "ArcGIS Field Maps", "QGIS", "plant ID (Intermountain flora)",
            "invasive species removal", "herbicide application", "chainsaw (S-212)",
            "wildland fire (S-130/S-190)", "Wilderness First Aid", "ATV/UTV operation",
            "4WD off-road driving", "data collection (Survey123, Collector)",
            "riparian restoration", "wildlife observation", "rangeland monitoring",
            "AIM/MIM protocols", "backcountry navigation", "trail maintenance",
        ],
        "bullets": [
            "Led {n}-person crew conducting {protocol} surveys across {n2} plots in {region}",
            "Treated {acres} acres of {invasive} using {method}; achieved {pct}% mortality on follow-up",
            "Collected vegetation and soil data on {n} AIM plots in {region} for BLM monitoring",
            "Restored {miles} miles of riparian corridor via willow staking and bank stabilization",
            "Operated chainsaw and hand tools to remove {invasive} from {acres} acres of {habitat}",
            "Logged {n} wildlife observations into {database}; supported {species} habitat assessment",
            "Mapped {miles} miles of fenceline using Trimble GPS; submetric accuracy",
            "Trained {n} seasonal techs on plant ID, data protocols, and field safety",
            "Maintained {miles} miles of backcountry trail with hand crew; packed in via {transport}",
            "Wrote daily field notes and uploaded data nightly via {platform}; zero missing records over {weeks} weeks",
            "Coordinated with {agency} biologist on {project} surveys across {acres} acres",
            "Spike-camped for {n}-day hitches in {region}; carried {weight}lb pack in remote terrain",
        ],
        "summary": (
            "{years}+ years of conservation field work across {region_summary}, "
            "with deep experience in {focus}. Comfortable spike-camping for "
            "extended hitches, navigating off-trail, and running data collection "
            "to agency protocol."
        ),
        "summary_focus": [
            "vegetation monitoring and AIM/MIM protocols",
            "invasive species treatment and native plant restoration",
            "rangeland health assessment for BLM and USFS partners",
            "riparian and sage-grouse habitat work",
            "wildlife survey support and habitat assessment",
        ],
        "certs": [
            "S-130/S-190 Wildland Fire",
            "S-212 Wildland Fire Chainsaws",
            "Wilderness First Responder (WFR)",
            "Wilderness First Aid (WFA)",
            "Utah Pesticide Applicator (Non-Commercial)",
            "FAA Part 107 (small UAS)",
        ],
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
        "n2": rng.choice([24, 60, 120, 240]),
        "pct": rng.choice([12, 18, 24, 30, 40, 55, 70, 85]),
        "ms": rng.choice([40, 80, 120, 200]),
        "hr": rng.choice([2, 4, 6, 9]),
        "min": rng.choice([8, 15, 30, 45]),
        "weeks": rng.choice([3, 6, 8, 10]),
        "year": rng.choice([24, 25, 26]),
        "old_score": 62,
        "new_score": 94,
        # Conservation-specific fillers.
        "protocol": rng.choice([
            "AIM (Assessment, Inventory, and Monitoring)", "MIM (Multiple Indicator Monitoring)",
            "line-point intercept", "Daubenmire", "belt transect", "rangeland health",
        ]),
        "region": rng.choice([
            "the Great Basin", "the Colorado Plateau", "the Wasatch Front",
            "the West Desert", "the Uinta Mountains", "southeastern Utah canyon country",
            "the Bear River watershed", "the Henry Mountains",
        ]),
        "region_summary": rng.choice([
            "the Great Basin and Colorado Plateau",
            "Utah's high desert and montane ecosystems",
            "BLM and USFS lands in the Intermountain West",
        ]),
        "invasive": rng.choice([
            "cheatgrass", "Russian olive", "tamarisk (saltcedar)", "Russian knapweed",
            "musk thistle", "leafy spurge", "Dyer's woad", "perennial pepperweed",
        ]),
        "method": rng.choice([
            "cut-stump herbicide treatment", "foliar spray (imazapyr)",
            "mechanical removal", "prescribed grazing", "hand-pulling crews",
        ]),
        "habitat": rng.choice([
            "sagebrush steppe", "pinyon-juniper woodland", "riparian corridor",
            "mixed-conifer forest", "alpine meadow", "salt desert shrubland",
        ]),
        "acres": rng.choice([45, 120, 280, 640, 1200, 3500]),
        "miles": rng.choice([2, 6, 14, 28, 60]),
        "database": rng.choice(["WRI tracker", "AGOL Field Maps", "Survey123", "iNaturalist"]),
        "species": rng.choice([
            "greater sage-grouse", "pronghorn", "mule deer", "Bonneville cutthroat trout",
            "boreal toad", "Utah prairie dog", "pygmy rabbit",
        ]),
        "transport": rng.choice(["mule string", "raft", "ATV", "foot from a 4WD spike camp"]),
        "platform": rng.choice(["AGOL", "Survey123", "Field Maps", "Trimble TerraSync"]),
        "agency": rng.choice([
            "BLM", "USFS", "UDWR", "NPS", "Utah Division of Wildlife Resources",
            "USFWS", "Utah State Parks",
        ]),
        "project": rng.choice([
            "sage-grouse lek", "pinyon-juniper removal", "stream temperature",
            "raptor nest", "fenceline modification", "spring restoration",
        ]),
        "weight": rng.choice([45, 55, 65, 75]),
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
    key, profile = pick_profile(role)
    is_conservation = key == "conservation"

    cities = UTAH_CITIES if is_conservation else CITIES
    orgs = CONSERVATION_ORGS if is_conservation else COMPANIES
    schools = CONSERVATION_SCHOOLS if is_conservation else SCHOOLS
    degrees = CONSERVATION_DEGREES if is_conservation else [
        "B.S. Computer Science", "B.A. Cognitive Science", "B.S. Math", "B.S. Information Systems",
    ]
    job_locations = [f"{c}, {s}" for c, s in cities] + (["Remote"] if not is_conservation else [])

    city, state = rng.choice(cities)
    handle = name.lower().replace(" ", ".")
    email = f"{handle}@example.com"
    phone = f"({rng.randint(200, 989)}) {rng.randint(200, 989)}-{rng.randint(1000, 9999)}"
    website = "" if is_conservation else f"{handle.replace('.', '')}.dev"

    if is_conservation:
        summary = profile["summary"].format(
            years=years,
            region_summary=rng.choice([
                "the Great Basin and Colorado Plateau",
                "Utah's high desert and montane ecosystems",
                "BLM and USFS lands across the Intermountain West",
            ]),
            focus=rng.choice(profile["summary_focus"]),
        )
    else:
        summary = profile["summary"].format(
            years=years,
            area=rng.choice(["platform", "growth", "search", "ML"]),
            segment=rng.choice(["B2B SaaS", "consumer", "enterprise", "developer tools"]),
            focus=rng.choice(profile["summary_focus"]),
        )

    n_jobs = max(2, min(4, years // 3 + 1))
    experience: list[Job] = []
    current_year = 2026

    if is_conservation:
        # Field-work career progression — most recent is most senior.
        senior_titles = ["Crew Lead", "Field Coordinator", "Lead Field Technician"]
        mid_titles = ["Field Technician II", "Senior Field Technician"]
        junior_titles = ["Field Technician", "Seasonal Field Technician", "AmeriCorps Member"]
    for i in range(n_jobs):
        end_year = current_year if i == 0 else current_year - rng.randint(1, 2)
        start_year = end_year - rng.randint(1, 3)
        current_year = start_year

        if is_conservation:
            # Pick title by reversed rank so most recent (i=0) = most senior.
            rank = n_jobs - 1 - i
            if rank == 0:
                title = rng.choice(junior_titles)
            elif rank == 1:
                title = rng.choice(mid_titles)
            else:
                title = rng.choice(senior_titles)
        else:
            progression = ["", "Senior ", "Staff ", "Lead "] if years > 8 else ["", "Senior "]
            rank = min(n_jobs - 1 - i, len(progression) - 1)
            title_prefix = progression[rank]
            base_role = role
            for prefix in ("Senior ", "Staff ", "Lead ", "Principal ", "Junior "):
                if base_role.startswith(prefix):
                    base_role = base_role[len(prefix):]
                    break
            title = f"{title_prefix}{base_role}".strip()

        job = Job(
            title=title,
            company=rng.choice(orgs),
            start=f"{start_year}",
            end="Present" if i == 0 else f"{end_year}",
            location=rng.choice(job_locations),
            bullets=[fill_bullet(b, rng) for b in rng.sample(profile["bullets"], k=min(4, len(profile["bullets"])))],
        )
        experience.append(job)

    skills = rng.sample(profile["skills"], k=min(10 if is_conservation else 8, len(profile["skills"])))

    edu_year = 2026 - years - rng.randint(0, 2)
    education = [Education(
        degree=rng.choice(degrees),
        school=rng.choice(schools),
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
