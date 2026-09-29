import html as _html
import re

_TAG_RX = re.compile(r"<[^>]+>")


from markdownify import markdownify

def html_to_markdown(s: str) -> str:
    s = s or ""
    import html
    s = html.unescape(s)
    try:
        # Convert HTML to markdown, ignoring images and links for clean text
        md = markdownify(s, heading_style="ATX", strip=['img'])
        # clean up multiple empty lines
        import re
        md = re.sub(r'\n\s*\n\s*\n+', '\n\n', md).strip()
        # Still cap length, but safely? Let's cap at 5000 characters
        if len(md) > 8000:
            md = md[:8000] + "..."
        return md
    except Exception:
        return s

def strip_html(s: str) -> str:
    s = _html.unescape(s or "")
    return re.sub(r"\s+", " ", _TAG_RX.sub(" ", s)).strip()

def format_salary(smin, smax):
    if smin and smax:
        return f"${int(smin):,} - ${int(smax):,}"
    return None
