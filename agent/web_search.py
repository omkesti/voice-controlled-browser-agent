"""
Web search for the Voice Browser Agent.

Scraping search-engine result pages (Bing/Google/DuckDuckGo HTML) is
unreliable: they serve CAPTCHA/bot challenges to automated browsers. This
module instead answers queries through keyless APIs that return structured
data, with an optional real search API (Tavily) when a key is configured:

  1. Currency conversion  -> open.er-api.com (keyless)
  2. Topic / definition   -> DuckDuckGo Instant Answer API (keyless)
  3. General web search    -> Tavily API (only if TAVILY_API_KEY is set)

If nothing is found, returns a "no_result" marker so the agent can fall back
to its own knowledge or tell the user it couldn't find an answer.
"""

import re
from typing import Optional

import requests

import config
from utils.logger import (
    log_browser_info,
    log_browser_debug,
    log_browser_warning,
)

_UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
_TIMEOUT = 15

# Currency words -> ISO codes (extend as needed).
_CURRENCY_NAMES = {
    "rupee": "INR", "rupees": "INR", "rs": "INR",
    "dollar": "USD", "dollars": "USD", "usd": "USD", "buck": "USD", "bucks": "USD",
    "euro": "EUR", "euros": "EUR",
    "pound": "GBP", "pounds": "GBP", "sterling": "GBP",
    "yen": "JPY",
    "yuan": "CNY", "renminbi": "CNY",
    "rupiah": "IDR",
    "won": "KRW",
    "dirham": "AED",
    "real": "BRL", "reais": "BRL",
    "peso": "MXN", "pesos": "MXN",
    "franc": "CHF", "francs": "CHF",
    "cad": "CAD", "aud": "AUD",
}
_CURRENCY_CODES = {
    "USD", "INR", "EUR", "GBP", "JPY", "CNY", "IDR", "KRW", "AED",
    "BRL", "MXN", "CHF", "CAD", "AUD", "SGD", "HKD", "NZD", "ZAR", "RUB",
}


def run(query: str) -> str:
    """Answer a query via the best available source; return text for the LLM."""
    q = (query or "").strip()
    if not q:
        return "error: empty query"

    log_browser_info(f"Web search: {q}")

    # 1. Currency conversion (most precise for that intent).
    result = _try_currency(q)
    if result:
        return result

    # 2. Tavily real web search, if a key is configured (best general coverage).
    if getattr(config, "TAVILY_API_KEY", None):
        result = _try_tavily(q)
        if result:
            return result

    # 3. DuckDuckGo Instant Answer API (keyless; good for topics/definitions).
    result = _try_ddg_instant(q)
    if result:
        return result

    log_browser_warning(f"No web answer found for: {q}")
    return (
        "no_result: no live web answer was found for this query. "
        "If you are confident, answer from your own knowledge; otherwise say you could not find it."
    )


def _try_currency(query: str) -> Optional[str]:
    """Detect 'AMOUNT FROM to/in TO' currency queries and convert via FX API."""
    parsed = _parse_currency(query)
    if not parsed:
        return None

    amount, src, dst = parsed
    try:
        resp = requests.get(
            f"https://open.er-api.com/v6/latest/{src}",
            headers=_UA,
            timeout=_TIMEOUT,
        )
        data = resp.json()
    except Exception as e:
        log_browser_warning(f"Currency API failed: {e}")
        return None

    rate = (data.get("rates") or {}).get(dst)
    if not rate:
        return None

    converted = round(amount * rate, 2)
    log_browser_debug(f"Currency: {amount} {src} -> {converted} {dst}")
    return (
        f"{amount:g} {src} = {converted:,.2f} {dst} "
        f"(rate 1 {src} = {rate:.4f} {dst}, source open.er-api.com)."
    )


def _parse_currency(query: str):
    """Return (amount, from_code, to_code) or None."""
    s = query.lower().replace(",", "")

    amt_match = re.search(r"(\d+(?:\.\d+)?)", s)
    if not amt_match:
        return None
    amount = float(amt_match.group(1))

    found = []
    # ISO codes first (preserve order of appearance).
    for token in re.findall(r"\b([a-z]{3})\b", s):
        code = token.upper()
        if code in _CURRENCY_CODES and code not in found:
            found.append(code)
    # Then currency words.
    for word, code in _CURRENCY_NAMES.items():
        if re.search(rf"\b{re.escape(word)}\b", s) and code not in found:
            found.append(code)
    # A leading '$' implies USD as the source if not already present.
    if "$" in query and "USD" not in found:
        found.insert(0, "USD")

    if len(found) >= 2:
        return amount, found[0], found[1]
    return None


def _try_ddg_instant(query: str) -> Optional[str]:
    """Query the DuckDuckGo Instant Answer API for an abstract/answer/definition."""
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
            headers=_UA,
            timeout=_TIMEOUT,
        )
        data = resp.json()
    except Exception as e:
        log_browser_warning(f"DuckDuckGo IA failed: {e}")
        return None

    answer = (data.get("Answer") or "").strip()
    abstract = (data.get("AbstractText") or "").strip()
    definition = (data.get("Definition") or "").strip()
    heading = (data.get("Heading") or "").strip()

    body = answer or abstract or definition
    if not body:
        # Fall back to the first related topics, if any.
        topics = data.get("RelatedTopics") or []
        snippets = [t.get("Text", "") for t in topics if isinstance(t, dict) and t.get("Text")]
        body = " ".join(snippets[:3]).strip()

    if not body:
        return None

    source = (data.get("AbstractURL") or "").strip()
    prefix = f"{heading}: " if heading and not body.startswith(heading) else ""
    text = f"{prefix}{body}"
    if source:
        text += f" (source: {source})"
    return text[: config.MAX_PAGE_CONTENT_LENGTH]


def _try_tavily(query: str) -> Optional[str]:
    """Query the Tavily search API (requires TAVILY_API_KEY)."""
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": config.TAVILY_API_KEY,
                "query": query,
                "max_results": 5,
                "include_answer": True,
                "search_depth": "basic",
            },
            headers=_UA,
            timeout=_TIMEOUT,
        )
        data = resp.json()
    except Exception as e:
        log_browser_warning(f"Tavily search failed: {e}")
        return None

    parts = []
    answer = (data.get("answer") or "").strip()
    if answer:
        parts.append(answer)

    for item in (data.get("results") or [])[:5]:
        title = (item.get("title") or "").strip()
        content = (item.get("content") or "").strip()
        if title or content:
            parts.append(f"- {title}: {content}")

    if not parts:
        return None

    return "\n".join(parts)[: config.MAX_PAGE_CONTENT_LENGTH]
