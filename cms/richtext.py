import re

_BR_BEFORE_MANUAL = re.compile(r"<br\s*/?\s*>(?=\s*(?:\d+\.)+\d+\s)", re.IGNORECASE)
_MANUAL_PREFIX = re.compile(r"^(\s*(?:<[^>]+>)*\s*)(?:\d+\.)+\d+\s+", re.IGNORECASE)
_NESTED_OL_IN_LI = re.compile(
    r"<li([^>]*)>(.*?)(<ol[^>]*>)(.*?)(</ol>)(.*?)</li>",
    re.IGNORECASE | re.DOTALL,
)
_LI_TAG = re.compile(r"<li([^>]*)>(.*?)</li>", re.IGNORECASE | re.DOTALL)


def _strip_manual_number(fragment):
    return _MANUAL_PREFIX.sub(r"\1", (fragment or "").strip(), count=1)


def _promote_nested_ol(match):
    attrs, before, _open_ol, inner, _close_ol, after = match.groups()
    inner_items = re.findall(r"<li[^>]*>.*?</li>", inner, flags=re.IGNORECASE | re.DOTALL)
    if not inner_items:
        return match.group(0)
    parts = []
    if before.strip():
        parts.append(f"<li{attrs}>{before.strip()}</li>")
    parts.extend(inner_items)
    if after.strip():
        parts.append(f"<li{attrs}>{after.strip()}</li>")
    return "".join(parts)


def flatten_nested_ordered_lists(html):
    if not html or "<ol" not in html.lower():
        return html
    previous = None
    current = html
    while previous != current:
        previous = current
        current = _NESTED_OL_IN_LI.sub(_promote_nested_ol, current, count=1)
    return current


def split_manual_sublist_items(html):
    if not html or "<li" not in html.lower():
        return html

    def split_li(match):
        attrs, inner = match.groups()
        segments = _BR_BEFORE_MANUAL.split(inner)
        if len(segments) <= 1:
            return f"<li{attrs}>{_strip_manual_number(inner)}</li>"
        chunks = []
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            chunks.append(f"<li{attrs}>{_strip_manual_number(segment)}</li>")
        return "".join(chunks) if chunks else match.group(0)

    return _LI_TAG.sub(split_li, html)


def normalize_richtext_html(html):
    if not (html or "").strip():
        return html or ""
    normalized = flatten_nested_ordered_lists(html)
    normalized = split_manual_sublist_items(normalized)
    return normalized
