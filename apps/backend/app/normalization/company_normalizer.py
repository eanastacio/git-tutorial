import re
import unicodedata

LEGAL_SUFFIXES = {
    "llc",
    "inc",
    "inc.",
    "corp",
    "corp.",
    "corporation",
    "ltd",
    "ltd.",
    "co",
    "co.",
    "company",
}


def normalize_company_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", normalized).lower()
    parts = [part for part in normalized.split() if part not in LEGAL_SUFFIXES]
    return " ".join(parts).strip()


def display_company_name(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name.strip())
    return normalized.title()
