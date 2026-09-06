import unittest
from country_catalog import country_catalog, coverage_inventory


class CountryCatalogTests(unittest.TestCase):
    def test_catalog_has_unique_codes_and_distinguishes_extension(self):
        rows = country_catalog()
        by_code = {row["code"]: row for row in rows}
        self.assertEqual(len(by_code), len(rows))
        self.assertEqual(sum(row["code_system"] == "ISO 3166-1" for row in rows), 249)
        self.assertEqual(by_code["XK"]["code_system"], "Application extension")
        for code in ("TW", "CN", "HK", "PS", "VA", "AQ", "US", "DE", "FR"):
            self.assertIn(code, by_code)

    def test_inventory_never_claims_coverage_from_membership(self):
        rows = coverage_inventory()
        self.assertEqual(len(rows), len(country_catalog()))
        self.assertEqual({row["News coverage"] for row in rows}, {"Not verified"})
