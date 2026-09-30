#!/usr/bin/env python3
"""Build a unified JSON index from materials manifests."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

MANIFEST = Path("materials/_index/sources_manifest.csv")
OUT = Path("materials/_index/content_index.json")


def infer_type(row: dict[str, str]) -> str:
    t = (row.get("link_text") or "").lower()
    u = (row.get("url") or "").lower()
    section = row.get("section", "")

    if section == "seguridad" or "seguridad" in t or "norma" in t:
        return "seguridad"
    if "manual" in t or "datasheet" in t or "hoja de datos" in t:
        return "manual"
    if "tesis" in t:
        return "tesis"
    if "paper" in t:
        return "paper"
    if section == "parciales":
        return "adicional"
    if "guía" in t or "guia" in t or "práctica" in t or "practica" in t:
        return "guía"
    if u.endswith(".pdf"):
        return "documento"
    return "referencia"


def infer_criticality(row: dict[str, str]) -> str:
    t = (row.get("link_text") or "").lower()
    if row.get("section") == "seguridad":
        return "obligatorio"
    if any(k in t for k in ["guía", "guia", "norma", "seguridad"]):
        return "obligatorio"
    if any(k in t for k in ["manual", "apunte", "notas", "referencias"]):
        return "recomendado"
    if any(k in t for k in ["paper", "tesis"]):
        return "avanzado"
    return "recomendado"


def infer_state(row: dict[str, str]) -> str:
    availability = row.get("availability", "")
    if availability in {"broken", "error", "unreachable"}:
        return "roto"
    if row.get("downloadable", "false") == "true":
        # Current policy: external links are primary, local files are ignored by git.
        return "externo"
    return "externo"


def main() -> None:
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    resources = []

    for i, r in enumerate(rows, start=1):
        resources.append(
            {
                "id": i,
                "title": r.get("link_text") or "(sin texto)",
                "section": r.get("section"),
                "experiment": r.get("experiment"),
                "resource_type": infer_type(r),
                "criticality": infer_criticality(r),
                "state": infer_state(r),
                "downloadable": r.get("downloadable") == "true",
                "url": r.get("url"),
                "local_path": r.get("local_path") or None,
                "availability": r.get("availability") or "unchecked",
                "http_status": r.get("http_status") or None,
                "content_type": r.get("content_type") or None,
                "last_checked": r.get("timestamp_utc"),
            }
        )

    by_section = Counter(r["section"] for r in resources)
    by_type = Counter(r["resource_type"] for r in resources)
    by_state = Counter(r["state"] for r in resources)
    broken = [r for r in resources if r["state"] == "roto"]

    payload = {
        "generated_from": str(MANIFEST).replace("\\", "/"),
        "generated_at": rows[0]["timestamp_utc"] if rows else None,
        "totals": {
            "resources": len(resources),
            "broken_links": len(broken),
        },
        "counts": {
            "by_section": dict(by_section),
            "by_type": dict(by_type),
            "by_state": dict(by_state),
        },
        "broken_links": [
            {
                "title": r["title"],
                "url": r["url"],
                "section": r["section"],
                "http_status": r["http_status"],
                "availability": r["availability"],
            }
            for r in broken
        ],
        "resources": resources,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
