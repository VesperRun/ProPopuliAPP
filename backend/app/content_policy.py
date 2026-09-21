import re

from fastapi import HTTPException, status

# ProPopuli does not name or echo that platform. Match common spellings.
_BANNED = re.compile(r"sub\s*[-]?\s*reddits?", re.I)


def content_policy_violation(*parts: str) -> bool:
    for part in parts:
        if part and _BANNED.search(part):
            return True
    return False


def assert_content_policy(*parts: str) -> None:
    if content_policy_violation(*parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That wording isn't allowed on ProPopuli. Remove it and try again.",
        )
