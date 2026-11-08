from __future__ import annotations

REPLACEMENTS = {
    "unable": "cannot",
    "authenticate": "sign in",
    "password": "passphrase",
    "rotation": "rollover",
    "failed": "did not complete",
    "timeout": "time limit",
    "invoice": "bill",
}


def paraphrase(text: str) -> str:
    words = text.split(" ")
    changed: list[str] = []
    for word in words:
        stem = word.strip(".,").lower()
        replacement = REPLACEMENTS.get(stem)
        if replacement:
            changed.append(replacement)
        else:
            changed.append(word)
    return " ".join(changed)


def rare_wording(text: str) -> str:
    return text.replace("password", "credential churn").replace("Password", "Credential churn")


def boundary(text: str) -> str:
    return " ".join(text.split(" ")[:8])


def missing_context(text: str) -> str:
    return "The workflow failed after the last change and the user cannot continue."


def long_context(text: str, appendix: str) -> str:
    return f"{text} {appendix}"
