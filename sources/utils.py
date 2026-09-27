import html as _html
import re

_TAG_RX = re.compile(r"<[^>]+>")

def strip_html(s: str) -> str:
    s = _html.unescape(s or "")
    return re.sub(r"\s+", " ", _TAG_RX.sub(" ", s)).strip()

def format_salary(smin, smax):
    if smin and smax:
        return f"${int(smin):,} - ${int(smax):,}"
    return None
