import re

def decompose_url(url: str) -> list[str]:
    """Decomposes a URL into alphanumeric components for embedding."""
    url = url.replace("http://", "").replace("https://", "")
    components = re.split(r'\W', url)
    return components
