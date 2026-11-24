"""Site adapters: how to build a search URL and how to read result / detail pages.

Add a site: add an entry to SITES with a url() builder, a `list` config for js/extract_list.js and an
optional `detail` config (selectors) for js/extract_detail.js. Prefer stable hooks (data attributes,
URL patterns of listing links) over CSS class names, which change often.
"""
from __future__ import annotations

from urllib.parse import quote, quote_plus

# willhaben areaId per Austrian state
AT_AREAS = {
    "burgenland": 1, "kaernten": 2, "kärnten": 2, "niederoesterreich": 3, "niederösterreich": 3,
    "oberoesterreich": 4, "oberösterreich": 4, "salzburg": 5, "steiermark": 6, "tirol": 7,
    "vorarlberg": 8, "wien": 9,
}


def _price_int(p):
    return str(int(p)) if p else ""


def url_willhaben(q, o):
    u = "https://www.willhaben.at/iad/kaufen-und-verkaufen/marktplatz?keyword=" + quote(q) + "&rows=90"
    area = o.get("at_area")
    if area:
        aid = area if str(area).isdigit() else AT_AREAS.get(str(area).lower())
        if aid:
            u += f"&areaId={aid}"
    if o.get("max_price"):
        u += "&PRICE_TO=" + _price_int(o["max_price"])
    return u


def url_kleinanzeigen(q, o):
    slug = quote(q.strip().lower().replace(" ", "-"))
    price = f"preis::{_price_int(o['max_price'])}/" if o.get("max_price") else ""
    if o.get("de_town_id"):
        town = o.get("de_town_slug") or "ort"
        return (f"https://www.kleinanzeigen.de/s-{town}/{price}{slug}/"
                f"k0l{o['de_town_id']}r{int(o.get('radius') or 50)}")
    return f"https://www.kleinanzeigen.de/s-{price}{slug}/k0"


def url_ricardo(q, o):
    return "https://www.ricardo.ch/de/s/" + quote(q)


def url_tutti(q, o):
    return "https://www.tutti.ch/de/q/suche?query=" + quote(q)


def _ebay(domain):
    def build(q, o):
        u = f"https://www.{domain}/sch/i.html?_nkw={quote_plus(q)}&_sop=15"
        if o.get("max_price"):
            u += "&_udhi=" + _price_int(o["max_price"])
        if o.get("ebay_zip"):
            u += f"&_stpos={quote_plus(str(o['ebay_zip']))}&_sadis={int(o.get('radius') or 50)}&_fspt=1"
        return u
    return build


EBAY_DETAIL = {"title": '[data-testid="x-item-title"]', "price": '[data-testid="x-price-primary"]',
                   "shipping": '[data-testid="d-shipping-minview"]', "details": '[data-testid="x-about-this-item"]',
                   "description_url": 'src:iframe#desc_ifr'}

SITES = {
    "willhaben": {
        "country": "AT", "currency": "EUR", "url": url_willhaben,
        "list": {"mode": "willhaben", "link": 'a[href*="/iad/kaufen-und-verkaufen/d/"]', "closest": "article,div[id^=search-result-entry]"},
        "detail": {"title": '[data-testid="ad-detail-header"]', "price": '[data-testid="contact-box-price-box-price-value"]',
                   "location": '[data-testid="top-contact-box-address-box"]', "details": '[data-testid="attribute-group"]',
                   "text": '[data-testid="ad-description-Beschreibung"]'},
    },
    "kleinanzeigen": {
        "country": "DE", "currency": "EUR", "url": url_kleinanzeigen,
        "list": {"mode": "cards", "card": "article[data-adid]", "hrefAttr": "data-href", "link": 'a[href*="/s-anzeige/"]'},
        "detail": {"title": "#viewad-title", "price": "#viewad-price", "location": "#viewad-locality",
                   "details": "#viewad-details", "text": "#viewad-description-text"},
    },
    "ricardo": {
        "country": "CH", "currency": "CHF", "url": url_ricardo,
        "list": {"mode": "links", "link": 'a[href*="/de/a/"]'},
        "detail": None,
    },
    "tutti": {
        "country": "CH", "currency": "CHF", "url": url_tutti,
        "list": {"mode": "links", "link": 'a[href*="/vi/"]', "closest": "article,div[data-private-srp-listing-item-id]"},
        "detail": None,
    },
    "ebay.de": {
        "country": "DE", "currency": "EUR", "url": _ebay("ebay.de"),
        "list": {"mode": "links", "link": 'a[href*="/itm/"]', "closest": "li"},
        "detail": EBAY_DETAIL,
    },
    "ebay.at": {
        "country": "AT", "currency": "EUR", "url": _ebay("ebay.at"),
        "list": {"mode": "links", "link": 'a[href*="/itm/"]', "closest": "li"},
        "detail": EBAY_DETAIL,
    },
}


def site_for_url(url: str):
    for key in SITES:
        dom = key if "." in key else key + "."
        if dom in url:
            return key
    return None
