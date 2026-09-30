#!/usr/bin/env python3
"""
Sync teaching material from Laboratorio 5 website and track link health.

Examples:
  python3 scripts/sync_l5_materials.py --sections guias --download --check-links
  python3 scripts/sync_l5_materials.py --sections guias,seguridad,parciales --download --check-links
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

BASE = "https://asignaturas.df.uba.ar/l5-larotonda/"
SECTION_URLS = {
    "guias": urljoin(BASE, "guias/"),
    "seguridad": urljoin(BASE, "seguridad/"),
    "parciales": urljoin(BASE, "parciales/"),
    "cronograma": urljoin(BASE, "cronograma/"),
    "programa": urljoin(BASE, "programa/"),
}

DOWNLOADABLE_EXTS = {
    ".pdf", ".zip", ".rar", ".7z", ".doc", ".docx", ".ppt", ".pptx",
    ".xls", ".xlsx", ".txt", ".csv", ".jpg", ".jpeg", ".png", ".gif", ".webp",
}

KEYWORDS_TO_EXPERIMENT = [
    ("exp_01_conteo_fotones", ["conteo", "photon", "pmt", "fotomultiplicador", "centellador"]),
    ("exp_02_descarga_glow", ["glow", "descarga"]),
    ("exp_03_fotoelectrico", ["fotoelec", "fotoel"]),
    ("exp_04_espectroscopia", ["espectrosc", "ccs200", "clorofila", "skdav", "edu-ot3", "redpitaya"]),
    ("exp_05_fluidos", ["fluidos", "pinzas", "piv"]),
    ("exp_06_laser", ["laser", "láser", "cavidad", "abcd", "diodos de bombeo"]),
    ("exp_07_nuclear_particulas", ["nuclear", "gamma", "compton", "coincid", "muon", "muón", "cosmic", "radiaci"]),
]


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_a = False
        self._href = ""
        self._text = ""
        self.anchors: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._in_a = True
            self._href = dict(attrs).get("href", "")
            self._text = ""

    def handle_data(self, data):
        if self._in_a:
            self._text += data

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._in_a:
            text = " ".join(self._text.split())
            self.anchors.append((self._href, text))
            self._in_a = False


@dataclass
class LinkRecord:
    section: str
    source_page: str
    link_text: str
    url: str
    downloadable: bool
    experiment: str
    local_path: str
    sha256: str
    status: str
    availability: str
    http_status: str
    content_type: str
    final_url: str


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=40) as response:
        data = response.read()
    return data.decode("utf-8", "ignore")


def fetch_binary(url: str) -> tuple[bytes, int, str, str]:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=90) as response:
        data = response.read()
        return (
            data,
            getattr(response, "status", 200),
            response.headers.get("Content-Type", ""),
            response.geturl(),
        )


def probe_url(url: str) -> tuple[str, str, str, str]:
    """Return (availability, status_code, content_type, final_url)."""
    headers = {"User-Agent": "Mozilla/5.0"}

    # Try HEAD first
    try:
        req = Request(url, headers=headers, method="HEAD")
        with urlopen(req, timeout=30) as response:
            code = str(getattr(response, "status", 200))
            ctype = response.headers.get("Content-Type", "")
            return "ok", code, ctype, response.geturl()
    except HTTPError as e:
        if e.code not in (405, 501):
            if e.code in (401, 403):
                return "restricted", str(e.code), "", url
            if e.code == 404:
                return "broken", "404", "", url
            return "error", str(e.code), "", url
    except (URLError, socket.timeout):
        pass
    except Exception:
        pass

    # Fallback GET
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=45) as response:
            _ = response.read(512)
            code = str(getattr(response, "status", 200))
            ctype = response.headers.get("Content-Type", "")
            return "ok", code, ctype, response.geturl()
    except HTTPError as e:
        if e.code in (401, 403):
            return "restricted", str(e.code), "", url
        if e.code == 404:
            return "broken", "404", "", url
        return "error", str(e.code), "", url
    except (URLError, socket.timeout):
        return "unreachable", "", "", url
    except Exception:
        return "error", "", "", url


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sanitize_filename(name: str) -> str:
    name = unquote(name)
    name = name.strip().replace("/", "_").replace("\\", "_")
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "file"


def classify_experiment(text: str, url: str) -> str:
    hay = f"{text} {unquote(url)}".lower()
    for exp, keys in KEYWORDS_TO_EXPERIMENT:
        if any(k in hay for k in keys):
            return exp
    return "exp_99_por_clasificar"


def is_downloadable(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in DOWNLOADABLE_EXTS)


def collect_section_links(section: str, page_url: str) -> Iterable[tuple[str, str, str]]:
    html = fetch_text(page_url)
    parser = AnchorParser()
    parser.feed(html)
    seen = set()
    for href, text in parser.anchors:
        if not href:
            continue
        full = urldefrag(urljoin(page_url, href))[0]
        if full in seen:
            continue
        seen.add(full)
        yield section, full, text


def link_kind(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host.endswith("asignaturas.df.uba.ar"):
        return "asignaturas"
    if host.endswith("materias.df.uba.ar") or host.endswith("users.df.uba.ar"):
        return "df_uba_external"
    return "external"


def build_summary(rows: list[LinkRecord], output_path: Path, generated_at: str) -> None:
    def crit(r: LinkRecord) -> str:
        t = (r.link_text or "").lower()
        u = r.url.lower()
        if r.section == "seguridad" and r.downloadable:
            return "alta"
        if r.downloadable and any(k in t + " " + u for k in ["guía", "guia", "manual", "norma", "seguridad"]):
            return "alta"
        if r.downloadable:
            return "media"
        if r.availability in {"broken", "unreachable", "error"}:
            return "media"
        return "baja"

    lines: list[str] = []
    lines.append("# Resumen de materiales (Labo 5)")
    lines.append("")
    lines.append(f"Generado: {generated_at}")
    lines.append("")

    sections = sorted(set(r.section for r in rows))
    for section in sections:
        subset = [r for r in rows if r.section == section]
        files = [r for r in subset if r.downloadable]
        external_refs = [r for r in subset if not r.downloadable]
        broken = [r for r in subset if r.availability in {"broken", "unreachable", "error"}]

        lines.append(f"## Sección: {section}")
        lines.append(f"- Total enlaces indexados: {len(subset)}")
        lines.append(f"- Archivos descargables: {len(files)}")
        lines.append(f"- Referencias externas/no archivo: {len(external_refs)}")
        lines.append(f"- Enlaces con problemas: {len(broken)}")
        lines.append("")

        if files:
            lines.append("### Archivos descargables")
            for r in files:
                lt = r.link_text if r.link_text else "(sin texto)"
                lines.append(
                    f"- [{crit(r).upper()}] {lt}  \n"
                    f"  - URL: {r.url}  \n"
                    f"  - Estado: {r.status} | Disponibilidad: {r.availability} ({r.http_status})  \n"
                    f"  - Ruta local: `{r.local_path}`"
                )
            lines.append("")

        if external_refs:
            lines.append("### Referencias externas / páginas")
            for r in external_refs:
                lt = r.link_text if r.link_text else "(sin texto)"
                lines.append(
                    f"- [{crit(r).upper()}] {lt}  \n"
                    f"  - URL: {r.url}  \n"
                    f"  - Disponibilidad: {r.availability} ({r.http_status})"
                )
            lines.append("")

        if broken:
            lines.append("### Enlaces a revisar (rotos/inaccesibles)")
            for r in broken:
                lt = r.link_text if r.link_text else "(sin texto)"
                lines.append(f"- {lt} -> {r.url} [{r.availability} {r.http_status}]")
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sections", default="guias", help="Comma-separated sections to sync. Default: guias")
    ap.add_argument("--root", default="materials", help="Output root folder")
    ap.add_argument("--download", action="store_true", help="Download files")
    ap.add_argument("--check-links", action="store_true", help="Probe all links and mark broken/unreachable")
    args = ap.parse_args()

    sections = [s.strip() for s in args.sections.split(",") if s.strip()]
    bad = [s for s in sections if s not in SECTION_URLS]
    if bad:
        raise SystemExit(f"Unknown sections: {', '.join(bad)}. Valid: {', '.join(SECTION_URLS)}")

    root = Path(args.root)
    exp_root = root / "experiments"
    index_root = root / "_index"
    exp_root.mkdir(parents=True, exist_ok=True)
    index_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    rows: list[LinkRecord] = []

    for section in sections:
        page_url = SECTION_URLS[section]
        for sec, url, text in collect_section_links(section, page_url):
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                continue

            downloadable = is_downloadable(url)
            exp = classify_experiment(text, url) if sec == "guias" else f"section_{sec}"
            local_path = ""
            digest = ""
            status = "indexed"
            availability = "unchecked"
            http_status = ""
            content_type = ""
            final_url = url

            if downloadable:
                filename = sanitize_filename(Path(parsed.path).name)
                if sec == "guias":
                    target_dir = exp_root / exp / "files"
                else:
                    target_dir = root / sec / "files"
                target_dir.mkdir(parents=True, exist_ok=True)
                target = target_dir / filename
                local_path = str(target).replace("\\", "/")

                if args.download:
                    try:
                        data, code, ctype, final = fetch_binary(url)
                        digest = sha256_bytes(data)
                        existed_before = target.exists()
                        if existed_before and target.read_bytes() == data:
                            status = "unchanged"
                        else:
                            target.write_bytes(data)
                            status = "updated" if existed_before else "downloaded"
                        availability = "ok"
                        http_status = str(code)
                        content_type = ctype
                        final_url = final
                    except HTTPError as e:
                        status = f"error_http_{e.code}"
                        availability = "broken" if e.code == 404 else "error"
                        http_status = str(e.code)
                    except Exception as e:  # noqa: BLE001
                        status = f"error: {e}"
                        availability = "unreachable"

                elif args.check_links:
                    availability, http_status, content_type, final_url = probe_url(url)

            else:
                if args.check_links:
                    availability, http_status, content_type, final_url = probe_url(url)

            rows.append(
                LinkRecord(
                    section=sec,
                    source_page=page_url,
                    link_text=text,
                    url=url,
                    downloadable=downloadable,
                    experiment=exp,
                    local_path=local_path,
                    sha256=digest,
                    status=status,
                    availability=availability,
                    http_status=http_status,
                    content_type=content_type,
                    final_url=final_url,
                )
            )

    header = [
        "timestamp_utc",
        "section",
        "source_page",
        "link_text",
        "url",
        "downloadable",
        "experiment",
        "link_kind",
        "local_path",
        "sha256",
        "status",
        "availability",
        "http_status",
        "content_type",
        "final_url",
    ]

    manifest = index_root / "sources_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([
                timestamp,
                r.section,
                r.source_page,
                r.link_text,
                r.url,
                str(r.downloadable).lower(),
                r.experiment,
                link_kind(r.url),
                r.local_path,
                r.sha256,
                r.status,
                r.availability,
                r.http_status,
                r.content_type,
                r.final_url,
            ])

    # Section-specific manifests (for separate tracking, e.g., seguridad/parciales)
    for section in sorted(set(r.section for r in rows)):
        sec_manifest = index_root / f"sources_manifest_{section}.csv"
        with sec_manifest.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            for r in rows:
                if r.section != section:
                    continue
                w.writerow([
                    timestamp,
                    r.section,
                    r.source_page,
                    r.link_text,
                    r.url,
                    str(r.downloadable).lower(),
                    r.experiment,
                    link_kind(r.url),
                    r.local_path,
                    r.sha256,
                    r.status,
                    r.availability,
                    r.http_status,
                    r.content_type,
                    r.final_url,
                ])

    summary_path = index_root / "materials_summary.md"
    build_summary(rows, summary_path, timestamp)

    print(f"Manifest written: {manifest}")
    print(f"Summary written:  {summary_path}")
    print(f"Total links indexed: {len(rows)}")
    print(f"Download enabled: {args.download}")
    print(f"Link check enabled: {args.check_links}")


if __name__ == "__main__":
    main()
