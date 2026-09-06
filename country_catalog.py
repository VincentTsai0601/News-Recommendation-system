"""Country/territory inventory; membership never asserts news coverage."""
import pycountry


def country_catalog():
    rows = [{"code": c.alpha_2, "name": c.name, "code_system": "ISO 3166-1"}
            for c in pycountry.countries]
    # Common application extension; explicitly separate from assigned ISO codes.
    rows.append({"code": "XK", "name": "Kosovo", "code_system": "Application extension"})
    return sorted(rows, key=lambda row: row["name"].casefold())


def coverage_inventory():
    """No country relevance audit has been performed yet."""
    return [{"Country / territory": row["name"], "Code": row["code"],
             "Code system": row["code_system"], "News coverage": "Not verified"}
            for row in country_catalog()]
