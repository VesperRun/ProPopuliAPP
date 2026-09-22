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


def content_policy_violation(*parts: str) -> bool:
    for part in parts:
        if part and _BANNED_PLATFORM.search(part):
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
