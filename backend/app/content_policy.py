import re

from fastapi import HTTPException, status

# ProPopuli does not name or echo that platform. Match common spellings.
_BANNED_PLATFORM = re.compile(r"sub\s*[-]?\s*reddits?", re.I)

# Hard reject — not recast; threats, severe harassment (minimal list; operator for edge cases).
_HARD_BLOCK = re.compile(
    r"\b("
    r"kys|kill\s+your\s*self|"
    r"rape|"
    r"n[i1]gg[ae]r|f[a4]gg[o0]t|"
    r"i\s*will\s*(kill|hurt|find)\s*you"
    r")\b",
    re.I,
)

# Subpop names/slugs only — porn, sexual hookup niches, obvious illegal markets.
_HUB_DISALLOWED = re.compile(
    r"("
    r"p[o0]rn|xxx|nsfw|onlyfans|hentai|nude|nudes|gonewild|"
    r"camgirl|camming|stripper|stripclub|"
    r"hookup|hookups|fwb|personals|escort|escorts|sugar[\s-]?daddy|sugar[\s-]?baby|"
    r"kink|bdsm|swinger|swingers|fetish|"
    r"dating[\s-]?sex|singles[\s-]?only|"
    r"cocaine|fentanyl|heroin|methamphetamine|\bmeth\b|"
    r"carding|counterfeit|guns[\s-]?for[\s-]?sale|"
    r"darknet|dark[\s-]?web[\s-]?market"
    r")",
    re.I,
)

HUB_POLICY_MESSAGE = "This subpop name or description is not allowed on ProPopuli."


def _normalize_hub_text(text: str) -> str:
    s = text.lower()
    return s.replace("0", "o").replace("1", "i").replace("3", "e").replace("4", "a")


def content_policy_violation(*parts: str) -> bool:
    for part in parts:
        if part and _BANNED_PLATFORM.search(part):
            return True
    return False


def hub_policy_violation(*parts: str) -> bool:
    for part in parts:
        if not part:
            continue
        if _HUB_DISALLOWED.search(part) or _HUB_DISALLOWED.search(_normalize_hub_text(part)):
            return True
    return False


def hard_block_violation(*parts: str) -> bool:
    for part in parts:
        if part and _HARD_BLOCK.search(part):
            return True
    return False


def assert_content_policy(*parts: str) -> None:
    if hard_block_violation(*parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This content is not allowed on ProPopuli.",
        )
    if content_policy_violation(*parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That wording isn't allowed on ProPopuli. Remove it and try again.",
        )


def assert_hub_policy(*parts: str) -> None:
    assert_content_policy(*parts)
    if hub_policy_violation(*parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=HUB_POLICY_MESSAGE,
        )
