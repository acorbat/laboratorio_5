#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path("materials")
INDEX = ROOT / "_index" / "sources_manifest.csv"


def load_rows() -> list[dict[str, str]]:
    if not INDEX.exists():
        return []
    with INDEX.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def score_row(row: dict[str, str], practica: str) -> int:
    text = f"{row.get('link_text','')} {row.get('url','')} {row.get('experiment','')}".lower()
    p = practica.lower()
    score = 0
    if p.replace("-", "_") in text or p.replace("-", " ") in text:
        score += 4
    if any(k in text for k in ["guía", "guia", "práctica", "practica"]):
        score += 5
    if row.get("section") == "guias":
        score += 2
    if row.get("downloadable") == "true":
        score += 1
    return score


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--practica", required=True, help="slug de práctica, p.ej. conteo-fotones")
    ap.add_argument("--limit", type=int, default=20)
    args = ap.parse_args()

    rows = load_rows()
    ranked = sorted(rows, key=lambda r: score_row(r, args.practica), reverse=True)
    ranked = [r for r in ranked if score_row(r, args.practica) > 0][: args.limit]

    local_candidates = []
    if ROOT.exists():
        for p in ROOT.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".pdf", ".doc", ".docx", ".txt", ".md"}:
                name = p.name.lower().replace("_", "-")
                if args.practica.lower() in name:
                    local_candidates.append(str(p).replace("\\", "/"))

    result = {
        "practica": args.practica,
        "manifest_matches": [
            {
                "section": r.get("section"),
                "link_text": r.get("link_text"),
                "url": r.get("url"),
                "availability": r.get("availability"),
                "http_status": r.get("http_status"),
                "experiment": r.get("experiment"),
            }
            for r in ranked
        ],
        "local_candidates": local_candidates,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
