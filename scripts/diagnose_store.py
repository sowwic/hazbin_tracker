"""Diagnose which scraping endpoints a Shopify store exposes.

Usage:
    uv run python scripts/diagnose_store.py https://hazbinhotel.com
"""

import json
import sys
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from curl_cffi import requests


def diagnose_shopify_store(store_url: str):
    """Run a full diagnostic on a Shopify store."""
    report = {"store": store_url}
    ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # 1. products.json availability + get a sample handle
    sample_handle = None
    try:
        resp = requests.get(
            f"{store_url}/products.json?limit=1", impersonate="chrome", timeout=10
        )
        report["products_json"] = resp.status_code
        if resp.status_code == 200:
            data = resp.json()
            report["is_shopify"] = "products" in data
            if data.get("products"):
                sample_handle = data["products"][0]["handle"]
        else:
            report["is_shopify"] = False
    except Exception:
        report["products_json"] = "error"
        report["is_shopify"] = False

    # 2. Catalog size from sitemap (checks all product sub-sitemaps)
    try:
        resp = requests.get(f"{store_url}/sitemap.xml", impersonate="chrome", timeout=10)
        root = ElementTree.fromstring(resp.content)
        total = 0
        for sm in root.findall("ns:sitemap", ns):
            loc = sm.find("ns:loc", ns).text
            if "products" in loc:
                r2 = requests.get(loc, impersonate="chrome", timeout=15)
                r2root = ElementTree.fromstring(r2.content)
                total += sum(
                    1
                    for u in r2root.findall("ns:url", ns)
                    if "/products/" in u.find("ns:loc", ns).text
                )
        report["catalog_size"] = total if total else None
    except Exception:
        report["catalog_size"] = None

    # 3. /products/{handle}.js endpoint
    if sample_handle:
        try:
            r = requests.get(
                f"{store_url}/products/{sample_handle}.js",
                impersonate="chrome",
                timeout=10,
            )
            report["js_endpoint"] = r.status_code == 200
        except Exception:
            report["js_endpoint"] = False

    # 4. /collections.json endpoint
    try:
        r = requests.get(
            f"{store_url}/collections.json?limit=1", impersonate="chrome", timeout=10
        )
        report["collections_json"] = r.status_code == 200 and "collections" in r.json()
    except Exception:
        report["collections_json"] = False

    # 5. JSON-LD on HTML product pages
    if sample_handle:
        try:
            r = requests.get(
                f"{store_url}/products/{sample_handle}", impersonate="chrome", timeout=15
            )
            soup = BeautifulSoup(r.text, "html.parser")
            has_jsonld = False
            for s in soup.find_all("script", type="application/ld+json"):
                try:
                    d = json.loads(s.string)
                    items = d if isinstance(d, list) else [d]
                    for item in items:
                        if item.get("@type") in ("Product", "ProductGroup"):
                            has_jsonld = True
                except Exception:
                    continue
            report["jsonld_on_html"] = has_jsonld
        except Exception:
            report["jsonld_on_html"] = False

    return report


if __name__ == "__main__":
    store = sys.argv[1] if len(sys.argv) > 1 else "https://hazbinhotel.com"
    print(json.dumps(diagnose_shopify_store(store), indent=4))
