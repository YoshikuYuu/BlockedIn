import re


_UUID_RE = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$", re.IGNORECASE)
_HEX_RE = re.compile(r"^[a-f0-9]{8,}$", re.IGNORECASE)
_LONG_NUM_RE = re.compile(r"^\d{6,}$")
_MIXED_ID_RE = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d_-]{8,}$")
_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)?")

_URL_STOPWORDS = {
    "http", "https", "www", "com", "org", "net", "io", "co", "app",
    "html", "php", "asp", "aspx", "index", "home", "default"
}


def _is_noisy_token(token: str) -> bool:
    if not token:
        return True
    lowered = token.lower()
    if lowered in _URL_STOPWORDS:
        return True
    if len(token) > 32:
        return True
    if _UUID_RE.match(token) or _HEX_RE.match(token) or _LONG_NUM_RE.match(token):
        return True
    if _MIXED_ID_RE.match(token):
        return True
    return False


def _clean_segment(text: str, *, max_tokens: int) -> str:
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return ""

    tokens = []
    for raw in _TOKEN_RE.findall(normalized):
        if _is_noisy_token(raw):
            continue
        tokens.append(raw.lower())
        if len(tokens) >= max_tokens:
            break
    return " ".join(tokens)

def decompose_url(url: str) -> list[str]:
    """
    Decomposes a URL into alphanumeric components for embedding.
    Additionally, it removes common URL-specific tokens and overly long strings.
    """
    url = url.replace("http://", "").replace("https://", "").replace("www.", "")
    components = re.split(r'\W', url)

    # Filter out strings that contain alternating letters and numbers 
    # and strings that are too long
    pattern = r'(?:\d+[a-zA-Z]+\d+|[a-zA-Z]+\d+[a-zA-Z]+)'
    components = [comp for comp in components 
                  if comp
                  and not re.search(pattern, comp)
                  and len(comp) <= 20
                  and comp.lower() not in _URL_STOPWORDS]
    return components


def build_embedding_input(payload: dict, max_tokens: int = 256) -> str:
    segments = [
        payload.get("title", ""),
        payload.get("h1", ""),
        payload.get("metaDescription", ""),
        payload.get("snippet", ""),
        payload.get("headings", ""),
        payload.get("siteName", ""),
        " ".join(decompose_url(payload.get("url", ""))),
    ]

    cleaned_segments: list[str] = []
    seen = set()
    for segment in segments:
        cleaned = _clean_segment(str(segment), max_tokens=max_tokens)
        if not cleaned:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        cleaned_segments.append(cleaned)

    if not cleaned_segments:
        return ""

    merged = " | ".join(cleaned_segments)
    merged_tokens = _TOKEN_RE.findall(merged)
    if len(merged_tokens) <= max_tokens:
        return merged

    return " ".join(merged_tokens[:max_tokens])
