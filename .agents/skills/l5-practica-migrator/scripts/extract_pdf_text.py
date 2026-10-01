#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import zlib
from pathlib import Path
from urllib.request import Request, urlopen


def read_input(src: str) -> bytes:
    if src.startswith("http://") or src.startswith("https://"):
        req = Request(src, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=60) as r:
            return r.read()
    return Path(src).read_bytes()


def extract_text_from_pdf_bytes(data: bytes) -> str:
    # Fallback extractor (no dependencia externa): recupera strings de streams flate.
    chunks: list[str] = []
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        stream = m.group(1)
        decompressed = None
        for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS):
            try:
                decompressed = zlib.decompress(stream, wbits)
                break
            except Exception:
                continue
        if not decompressed or b"BT" not in decompressed:
            continue

        # Tj
        for token in re.findall(rb"\(([^\)]{2,500})\)\s*Tj", decompressed):
            chunks.append(token.decode("latin1", "ignore"))

        # TJ arrays
        for arr in re.findall(rb"\[(.*?)\]\s*TJ", decompressed, re.S):
            for token in re.findall(rb"\(([^\)]{1,500})\)", arr):
                chunks.append(token.decode("latin1", "ignore"))

    def unescape_pdf_text(s: str) -> str:
        s = re.sub(r"\\([0-7]{1,3})", lambda m: chr(int(m.group(1), 8)), s)
        s = s.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
        s = re.sub(r"\s+", " ", s).strip()
        return s

    cleaned: list[str] = []
    seen = set()
    for c in chunks:
        text = unescape_pdf_text(c)
        if len(text) < 20:
            continue
        if text in seen:
            continue
        seen.add(text)
        cleaned.append(text)

    return "\n".join(cleaned)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="ruta local o URL a PDF")
    ap.add_argument("--output", required=True, help="archivo .txt de salida")
    args = ap.parse_args()

    raw = read_input(args.input)
    text = extract_text_from_pdf_bytes(raw)
    Path(args.output).write_text(text, encoding="utf-8")

    print(f"Texto extraído en: {args.output}")
    if len(text.strip()) < 1000:
        print("ADVERTENCIA: extracción corta; revisar manualmente o usar OCR/herramienta PDF dedicada.")


if __name__ == "__main__":
    main()
