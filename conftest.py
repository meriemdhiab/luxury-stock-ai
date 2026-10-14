from pathlib import Path
import shutil

import pandas as pd
import pytest

from pipeline import run_pipeline

ROOT = Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def project_root(tmp_path_factory) -> Path:
    """Copie isolée des données brutes, passée dans le pipeline : les tests ne modifient pas le dépôt."""
    root = tmp_path_factory.mktemp("project")
    shutil.copytree(ROOT / "data/raw", root / "data/raw")
    run_pipeline(root)
    return root


@pytest.fixture(scope="session")
def products() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data/raw/products.csv")


@pytest.fixture(scope="session")
def quality_fixture() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data/quality/sales_quality_issues.csv")
