"""Vérifie que le dictionnaire de données couvre exactement les colonnes du schéma SQL.

Lancer depuis la racine du dépôt :  pytest -q tests/test_data_dictionary.py
Convention du schéma : une colonne par ligne ; les contraintes de table
commencent par PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK ou CONSTRAINT.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "02_architecture" / "sql" / "001_schema.sql"
DICTIONARY = ROOT / "01_governance" / "data_dictionary.xlsx"
TABLE_KEYWORDS = ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT")


def schema_columns():
    text = SCHEMA.read_text(encoding="utf-8")
    columns = {}
    for name, body in re.findall(r"CREATE TABLE (\w+) \((.*?)\n\);", text, flags=re.S):
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("--") or line.startswith(")"):
                continue
            first = line.split()[0]
            if first.upper() in TABLE_KEYWORDS or first.startswith(("(", "AND", "OR")):
                continue
            columns.setdefault(name, []).append(first)
    return columns


def dictionary_columns():
    openpyxl = pytest.importorskip("openpyxl")
    sheet = openpyxl.load_workbook(DICTIONARY, read_only=True)["Dictionnaire"]
    rows = list(sheet.iter_rows(values_only=True))
    header = rows[0]
    t, c = header.index("Table"), header.index("Colonne")
    found = {}
    for row in rows[1:]:
        if row[t] and row[c]:
            found.setdefault(row[t], []).append(row[c])
    return found


def test_dictionary_covers_schema():
    schema, dictionary = schema_columns(), dictionary_columns()
    assert schema, "aucune table détectée dans le schéma"
    missing = {t: sorted(set(cols) - set(dictionary.get(t, []))) for t, cols in schema.items()}
    missing = {t: c for t, c in missing.items() if c}
    extra = {t: sorted(set(cols) - set(schema.get(t, []))) for t, cols in dictionary.items()}
    extra = {t: c for t, c in extra.items() if c}
    assert not missing, f"colonnes absentes du dictionnaire : {missing}"
    assert not extra, f"colonnes du dictionnaire absentes du schéma : {extra}"


def test_dictionary_has_no_duplicate_rows():
    for table, cols in dictionary_columns().items():
        assert len(cols) == len(set(cols)), f"doublon dans {table}"
