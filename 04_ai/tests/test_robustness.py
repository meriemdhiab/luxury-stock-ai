import pandas as pd

from pipeline import clean_sales


def test_quality_fixture_is_quarantined_under_stress(quality_fixture, products):
    stressed = pd.concat([quality_fixture] * 5, ignore_index=True)
    clean, quarantine, report = clean_sales(stressed, products)
    # Après duplication, seules les lignes valides du premier exemplaire restent.
    assert len(clean) == len(quality_fixture) - 5
    assert report["quarantine_rows"] == len(quarantine) == len(stressed) - len(clean)
