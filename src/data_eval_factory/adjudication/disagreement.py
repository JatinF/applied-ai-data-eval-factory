from __future__ import annotations


def reviewers_agree(left: str | None, right: str | None) -> bool:
    return left is not None and left == right
