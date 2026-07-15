"""extract-price — цена товара «Читай-город» по URL."""

import json
import re
import sys

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9",
}
CREDIT_KEYWORDS = ("рассрочк", "долями", "сплит", "частями")
PRICE_KEYS = ("price", "lowPrice", "highPrice")
MIN_PRICE = 10
MAX_PRICE = 200000


def _to_number(raw):
    if raw is None:
        return None
    text = str(raw).replace("\xa0", "").replace(" ", "")
    m = re.search(r"\d+(?:[.,]\d+)?", text)
    if not m:
        return None
    value = float(m.group(0).replace(",", "."))
    return int(value) if value.is_integer() else value


def _valid(p):
    return p is not None and MIN_PRICE <= p <= MAX_PRICE

def _deref(data, ref):
    return data[ref] if isinstance(ref, int) and 0 <= ref < len(data) else ref


def _prices_from_nuxt(html):
    tag = BeautifulSoup(html, "html.parser").find("script", id="__NUXT_DATA__")
    if not tag or not tag.string:
        return None
    data = json.loads(tag.string)

    for node in data:
        if not (isinstance(node, dict) and "price" in node):
            continue
        price_obj = _deref(data, node["price"])
        if not (isinstance(price_obj, dict) and "base" in price_obj and "sale" in price_obj):
            continue

        base = _to_number(_deref(data, price_obj["base"]))
        sale = _to_number(_deref(data, price_obj["sale"]))
        if _valid(base) and _valid(sale):
            return max(base, sale), min(base, sale)
    return None
def _walk(node, prices):
    if isinstance(node, dict):
        for key, val in node.items():
            if key in PRICE_KEYS and isinstance(val, (str, int, float)):
                num = _to_number(val)
                if _valid(num):
                    prices.append(num)
            else:
                _walk(val, prices)
    elif isinstance(node, list):
        for item in node:
            _walk(item, prices)


def _prices_from_jsonld(soup):
    prices = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        _walk(data, prices)
    return prices


def extract_price(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    prices = sorted(set(_prices_from_jsonld(soup)))

    regular_price = None
    sale_price = None
    if len(prices) == 1:
        regular_price = prices[0]
    elif len(prices) >= 2:
        regular_price = prices[-1]
        sale_price = prices[0]

    page_text = soup.get_text().lower()
    has_credit = any(w in page_text for w in CREDIT_KEYWORDS)

    return {"regular_price": regular_price, "sale_price": sale_price, "has_credit": has_credit}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python extract_price.py <URL>")
        sys.exit(1)
    print(json.dumps(extract_price(sys.argv[1]), ensure_ascii=False, indent=2))
