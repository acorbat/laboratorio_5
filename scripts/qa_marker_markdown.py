#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    r"\)\(ˆ",
    r"<sup>",
    r"\*TTtI\*",
    r"\*TtI\*",
    r"τ<<",
    r"\[\s*\]",
]

# Targeted fixes for conteo-fotones equations detected in marker output
TARGETED_REPLACEMENTS = [
    (
        r"\)\( ε= ˆ \)\( \*dttIdttp\* \. \(1\)",
        "\\[ p(t)\\,dt = \\epsilon \\hat{I}(t)\\,dt \\tag{1} \\]",
    ),
    (
        r"∫ \+ = ′′ \*Tt t tdtI T TtI\* <sup>ˆ</sup> \)\( <sup>1</sup> <sup>ˆ</sup> \),\( \. \(3\)",
        "\\[ \\hat{I}(t,T)=\\frac{1}{T}\\int_{t}^{t+T} \\hat{I}(t')\\,dt' \\tag{3} \\]",
    ),
    (
        r"\*m m <sup>m</sup> m m TP\* <sup>−</sup> = e ! \)\( \. \(4\)",
        "\\[ P_m(T)=\\frac{\\bar m^m}{m!}e^{-\\bar m} \\tag{4} \\]",
    ),
    (
        r"ε= ˆ\*TIm\* \. \(5\)",
        "\\[ \\bar m = \\epsilon \\hat{I}T \\tag{5} \\]",
    ),
    (
        r"\. \(6\) \*T <sup>c</sup>\* ˆ \),\( = ˆ \*tITtI\* para\)\( τ<<",
        "\\[ \\hat{I}(t,T)\\approx \\hat{I}(t), \\qquad T \\ll \\tau_c \\tag{6} \\]",
    ),
]


def find_suspicious(text: str) -> list[tuple[int, str]]:
    out = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        for pat in SUSPICIOUS_PATTERNS:
            if re.search(pat, line):
                out.append((i, line.strip()))
                break
    return out


def apply_targeted_fixes(text: str) -> str:
    fixed = text
    for pat, repl in TARGETED_REPLACEMENTS:
        fixed = re.sub(pat, lambda _m, r=repl: r, fixed)

    # Cleanup common heading artifacts
    fixed = fixed.replace("#### **eguridad S**", "#### Seguridad")
    fixed = fixed.replace("#### **imental: Propuesta exper**", "#### Propuesta experimental")

    # Replace lingering html superscript tags in math-ish lines
    fixed = fixed.replace("<sup>", "^")
    fixed = fixed.replace("</sup>", "")

    return fixed


def main() -> None:
    ap = argparse.ArgumentParser(description="QA de texto convertido por marker (sintaxis/ecuaciones).")
    ap.add_argument("--input", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    path = Path(args.input)
    text = path.read_text(encoding="utf-8", errors="ignore")

    before = find_suspicious(text)
    fixed = apply_targeted_fixes(text)
    after = find_suspicious(fixed)

    rep = []
    rep.append(f"# QA report: {path}")
    rep.append("")
    rep.append(f"Líneas sospechosas antes: {len(before)}")
    rep.append(f"Líneas sospechosas después: {len(after)}")
    rep.append("")
    if before:
        rep.append("## Ejemplos antes")
        for n, line in before[:30]:
            rep.append(f"- L{n}: `{line[:180]}`")
        rep.append("")
    if after:
        rep.append("## Pendientes de revisión manual")
        for n, line in after[:40]:
            rep.append(f"- L{n}: `{line[:180]}`")
        rep.append("")

    Path(args.report).write_text("\n".join(rep), encoding="utf-8")

    if args.apply:
        path.write_text(fixed, encoding="utf-8")
        print(f"Applied fixes to: {path}")

    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()
