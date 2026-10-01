#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

ROOT = Path("materials")
OUT = ROOT / "_index" / "files_manifest_curated.csv"
SOURCE_MANIFEST = ROOT / "_index" / "sources_manifest.csv"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def classify(name: str, rel: str) -> tuple[str, str]:
    n = name.lower()
    r = rel.lower()
    if "guia" in n or "practica" in n:
        return "guia", "Guía de práctica"
    if "manual" in n or "datasheet" in n or "1p28" in n:
        return "manual", "Manual/hoja técnica de instrumento"
    if "paper" in n:
        return "paper", "Paper de referencia"
    if "tesis" in n:
        return "tesis", "Tesis de referencia"
    if "seguridad" in r or "normas" in n:
        return "seguridad", "Normativa/material de seguridad"
    if n.endswith(".zip"):
        return "dataset/demo", "Archivo comprimido de material adicional"
    return "referencia", "Material complementario"


def section_and_experiment(rel: str) -> tuple[str, str]:
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "materials" and parts[1] == "experiments":
        return "experiments", parts[2]
    if len(parts) >= 2 and parts[0] == "materials":
        return parts[1], ""
    return "", ""


def load_source_rows() -> list[dict[str, str]]:
    if not SOURCE_MANIFEST.exists():
        return []
    with SOURCE_MANIFEST.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_source_url(filename: str, rows: list[dict[str, str]]) -> str:
    key = norm(filename)
    best = ""
    for r in rows:
        url = r.get("url", "")
        base = url.split("/")[-1].split("?")[0]
        if not base:
            continue
        bkey = norm(base)
        if key and (key == bkey or key in bkey or bkey in key):
            best = url
            break
    return best


def main() -> None:
    rows = load_source_rows()
    files = sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and "_index" not in p.parts and not p.name.lower().endswith(".md")
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "section",
            "experiment_folder",
            "relative_path",
            "file_name",
            "file_type",
            "contains",
            "source_url_guess",
        ])
        for p in files:
            rel = str(p).replace("\\", "/")
            section, exp = section_and_experiment(rel)
            ftype, contains = classify(p.name, rel)
            source = find_source_url(p.name, rows)
            w.writerow([section, exp, rel, p.name, ftype, contains, source])

    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
