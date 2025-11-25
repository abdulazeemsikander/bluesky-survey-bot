# automation/main.py
import os
import csv
import textwrap
import random
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from .poster import post_to_bluesky

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
TEMPLATE_PATH = ROOT.parent / "templates" / "post.txt"
LOG_DIR = ROOT.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
POST_LOG = LOG_DIR / "post_log.csv"


# ---------- helpers ----------

def load_template() -> str:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def get_survey_link() -> str:
    link = os.getenv("SURVEY_URL", "").strip()
    if not link:
        raise ValueError("SURVEY_URL must be set in .env")
    return link


def write_log(text: str, dry_run: bool, variant_label: str) -> None:
    """Append a row to logs/post_log.csv for later weekly reports."""
    is_new = not POST_LOG.exists()
    with open(POST_LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["utc_time", "dry_run", "variant", "length", "preview"])
        w.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                "true" if dry_run else "false",
                variant_label,
                len(text),
                text.replace("\n", " ")[:140],
            ]
        )


# ---------- content pools (variants + hashtags) ----------

INTRO_VARIANTS = [
    "Short 5–7 min academic survey about ethical decisions in medical emergencies.",
    "Help with a short 5–7 min university study on ethical decisions in medical emergencies.",
    "We’re running a short academic survey on ethical decisions in medical emergencies (5–7 min).",
]

FOOTER_VARIANTS = [
    "18+ only, anonymous under GDPR.",
    "18+ only. Participation is anonymous and handled under GDPR.",
    "Your answers are anonymous (GDPR-compliant). 18+ only.",
]

# Hashtag pools:
# base tags show up very often, extras rotate so posts don't all look identical
BASE_HASHTAGS = [
    "#Research",
    "#Survey",
    "#AcademicChatter",
    "#Academia",
    "#MedicalEthics",
    "#Ethics",
]

EXTRA_HASHTAGS = [
    "#Bioethics",
    "#Science",
    "#SocialScience",
    "#Psychology",
    "#Healthcare",
    "#EmergencyMedicine",
    "#DecisionMaking",
    "#University",
    "#PhDLife",
    "#HigherEd",
    "#StudyRecruitment",
    "#Humanities",
]


def build_hashtags(max_tags: int = 10) -> str:
    """
    Build a hashtag string with a stable core and rotating extras.
    """
    tags = BASE_HASHTAGS.copy()
    extras = EXTRA_HASHTAGS.copy()
    random.shuffle(extras)

    # fill up to max_tags total
    for t in extras:
        if len(tags) >= max_tags:
            break
        tags.append(t)

    # shuffle final order a bit so posts don't look identical
    random.shuffle(tags)
    return " ".join(tags)


def build_post() -> tuple[str, str]:
    """
    Build a single Bluesky post and return (text, variant_label).
    variant_label is written into the logs so we can see which wording worked.
    """
    template = load_template()
    link = get_survey_link()

    intro = random.choice(INTRO_VARIANTS)
    footer = random.choice(FOOTER_VARIANTS)
    hashtags = build_hashtags(max_tags=10)

    variant_label = f"intro#{INTRO_VARIANTS.index(intro)};footer#{FOOTER_VARIANTS.index(footer)}"

    text = template.format(
        INTRO=intro,
        LINK=link,
        FOOTER=footer,
        HASHTAGS=hashtags,
    )

    # Bluesky limit is 300 chars; warn if we go over
    if len(text) > 300:
        print(f"[WARN] Post is {len(text)} characters; consider shortening.")
    return text, variant_label


# ---------- main ----------

def main() -> None:
    # behaviour flags from env
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    max_posts = int(os.getenv("MAX_POSTS", "1"))
    max_posts = max(1, max_posts)  # at least one

    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] Starting Bluesky bot (dry_run={dry_run}, max_posts={max_posts})")

    for idx in range(max_posts):
        if max_posts > 1:
            print(f"\n--- Post {idx + 1}/{max_posts} ---")

        post_text, variant_label = build_post()

        if dry_run:
            print("\n[DRY RUN] Preview:\n")
            print(textwrap.fill(post_text, width=100))
            write_log(post_text, dry_run=True, variant_label=variant_label)
        else:
            print("\n[LIVE] Posting to Bluesky with text:\n")
            print(textwrap.fill(post_text, width=100))
            print("\n[LIVE] Sending post to Bluesky …")
            uri = post_to_bluesky(post_text, dry_run=False)
            print(f"[LIVE] Post created with uri: {uri}")
            write_log(post_text, dry_run=False, variant_label=variant_label)


if __name__ == "__main__":
    main()
