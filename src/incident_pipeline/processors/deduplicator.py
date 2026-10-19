"""Canonical deduplication and ID generation for incident and research records."""

import hashlib
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalize a URL to its canonical format by stripping tracking parameters,
    trailing slashes, and standardizing common research repositories (like arXiv).
    """
    if not url:
        return ""
    
    url = url.strip()
    
    # Handle arXiv URL canonicalization: convert pdf/abs variants to canonical abs/
    arxiv_match = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]+\.[0-9]+(?:\w+)?)(?:\.pdf)?", url)
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        return f"https://arxiv.org/abs/{arxiv_id}"

    parsed = urlparse(url)
    
    # Standardize scheme and lowercase hostname
    scheme = "https" if parsed.scheme in ("http", "https") else parsed.scheme
    netloc = parsed.netloc.lower()
    
    # Remove tracking query parameters
    tracking_params = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "ref", "source", "fbclid", "gclid"
    }
    query_params = parse_qs(parsed.query, keep_blank_values=False)
    filtered_params = {k: v for k, v in query_params.items() if k.lower() not in tracking_params}
    
    # Sort query parameters for stability
    cleaned_query = urlencode(filtered_params, doseq=True)
    
    # Strip trailing slashes from path
    path = parsed.path.rstrip("/")
    
    canonical_parsed = parsed._replace(
        scheme=scheme,
        netloc=netloc,
        path=path,
        query=cleaned_query,
        fragment=""
    )
    return urlunparse(canonical_parsed)


def normalize_title(title: str) -> str:
    """Normalize title string for robust matching and canonical hashing."""
    if not title:
        return ""
    cleaned = title.strip().lower()
    # Strip punctuation and collapse multiple whitespace
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def generate_record_id(url: str, title: str) -> str:
    """Generate deterministic SHA-256 hash from canonical URL and normalized title."""
    norm_url = normalize_url(url)
    norm_title = normalize_title(title)
    seed = f"{norm_url}::{norm_title}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()
