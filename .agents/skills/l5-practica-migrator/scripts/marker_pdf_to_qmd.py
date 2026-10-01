#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


def ensure_module(module_name: str) -> None:
    try:
        __import__(module_name)
    except Exception as e:
        raise RuntimeError(
            f"Falta módulo requerido: {module_name}. "
            "No se instalará automáticamente desde el script. "
            "Instalar dependencias con Pixi (env marker)."
        ) from e


def run_marker(input_pdf: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)

    cli = shutil.which("marker_single") or shutil.which("marker")
    if not cli:
        raise RuntimeError(
            "No se encontró marker en PATH. Ejecuta con pixi en el environment marker:\n"
            "  pixi run -e marker python .agents/skills/l5-practica-migrator/scripts/marker_pdf_to_qmd.py ..."
        )

    ensure_module("packaging")

    # En algunos entornos Windows marker intenta usar backend con Docker.
    # Probamos variantes que fuerzan camino liviano (fast/disable_ocr) antes del modo por defecto.
    common = [
        cli,
        "--output_format",
        "markdown",
        "--output_dir",
        str(out_dir.resolve()),
    ]
    fpath = str(input_pdf.resolve())

    cmd_variants = [
        # 1) PDFs con texto embebido: evita OCR/modelos pesados
        common + ["--mode", "fast", "--disable_ocr", fpath],
        # 2) OCR selectivo, sin modo balanceado
        common + ["--mode", "fast", fpath],
        # 3) fallback estándar
        common + [fpath],
    ]

    last_cmd = None
    last_stdout = ""
    last_stderr = ""
    for cmd in cmd_variants:
        try:
            proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if proc.stdout:
                print(proc.stdout)
            if proc.stderr:
                print(proc.stderr)
            last_cmd = cmd
            last_stdout = proc.stdout or ""
            last_stderr = proc.stderr or ""
            break
        except subprocess.CalledProcessError as e:
            last_cmd = cmd
            last_stdout = e.stdout or ""
            last_stderr = e.stderr or ""
            continue
    else:
        extra = ""
        if "docker" in last_stderr.lower() or "docker" in last_stdout.lower():
            extra = (
                "\n\nDetectado error de Docker/vLLM en marker. "
                "Este script ya probó '--mode fast' y '--disable_ocr'. "
                "Si persiste, revisar configuración de marker/surya en Windows o usar ejecución en entorno Linux con soporte adecuado."
            )
        raise RuntimeError(
            "marker falló durante la conversión tras probar variantes compatibles.\n"
            f"CMD: {' '.join(last_cmd or [])}\n"
            f"STDERR:\n{(last_stderr or '').strip() or '<vacío>'}\n"
            f"STDOUT:\n{(last_stdout or '').strip() or '<vacío>'}"
            f"{extra}"
        )

    md_files = sorted(out_dir.rglob("*.md"), key=lambda p: p.stat().st_size, reverse=True)
    if md_files:
        return md_files[0]

    # Fallback: algunas versiones escriben junto al PDF
    sibling_candidates = sorted(
        input_pdf.parent.glob(f"{input_pdf.stem}*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if sibling_candidates:
        src = sibling_candidates[0]
        dst = out_dir / src.name
        dst.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        return dst

    raise RuntimeError(
        "marker no generó archivos markdown (.md) en output_dir ni junto al PDF."
    )


def slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").strip().title()


def move_images_and_rewrite_markdown(extracted_md: str, conv_dir: Path, slug: str, assets_root: Path) -> str:
    assets_dir = assets_root / slug
    assets_dir.mkdir(parents=True, exist_ok=True)

    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
    images = [p for p in conv_dir.rglob("*") if p.is_file() and p.suffix.lower() in image_exts]

    # Copiar imágenes y mapear por nombre base
    name_map: dict[str, str] = {}
    used = set()
    for img in images:
        base = img.name
        target = assets_dir / base
        if target.name in used:
            stem = img.stem
            suffix = img.suffix
            i = 2
            while (assets_dir / f"{stem}-{i}{suffix}").exists():
                i += 1
            target = assets_dir / f"{stem}-{i}{suffix}"
        shutil.copy2(img, target)
        used.add(target.name)
        name_map[img.name] = f"assets/{slug}/{target.name}"

    # Reescribir markdown image refs por nombre de archivo
    for old_name, new_path in name_map.items():
        extracted_md = re.sub(
            rf"(!\[[^\]]*\]\()([^\)]*{re.escape(old_name)})(\))",
            rf"\g<1>{new_path}\g<3>",
            extracted_md,
        )
        extracted_md = re.sub(
            rf"(src=[\"'])([^\"']*{re.escape(old_name)})([\"'])",
            rf"\g<1>{new_path}\g<3>",
            extracted_md,
        )

    return extracted_md


def cleanup_temp(conv_dir: Path, work_dir: Path, slug: str) -> None:
    if conv_dir.exists():
        shutil.rmtree(conv_dir, ignore_errors=True)
    for txt in work_dir.glob(f"{slug}*.txt"):
        try:
            txt.unlink()
        except Exception:
            pass


def build_qmd(title: str, extracted_md: str, source_ref: str) -> str:
    return f'''---
title: "{title}"
---

## Resumen

> Borrador inicial generado desde PDF con marker-pdf. Revisar y editar para fidelidad conceptual.

## Objetivos de aprendizaje

- (Completar con base fiel en la guía)
- (Completar con base fiel en la guía)
- (Completar con base fiel en la guía)

## Desarrollo conceptual del fenómeno

{extracted_md}

> Nota de revisión: validar manualmente ecuaciones, bloques matemáticos y notación física luego de la conversión automática.

## Ejes de exploración experimental

- (Revisar y reformular evitando formato receta)
- (Revisar y reformular evitando formato receta)
- (Revisar y reformular evitando formato receta)

## Preguntas orientadoras

- ¿(Completar)?
- ¿(Completar)?
- ¿(Completar)?

## Seguridad específica

- (Agregar normas y enlaces pertinentes)

## Recursos y referencias

- Texto de práctica: {source_ref}

## Fuente original

- Conversión automática con marker-pdf (requiere revisión de sintaxis/formato).
- Fuente principal: {source_ref}
'''


def main() -> None:
    ap = argparse.ArgumentParser(description="Convierte PDF a markdown con marker y crea borrador QMD.")
    ap.add_argument("--input", required=True, help="Ruta local al PDF")
    ap.add_argument("--slug", required=True, help="Slug de página en experimentos/, p.ej. conteo-fotones")
    ap.add_argument("--work-dir", default=".agents/skills/l5-practica-migrator/work/marker", help="Directorio de trabajo")
    ap.add_argument("--source-ref", default="(completar URL guía)", help="Referencia de fuente para incrustar en QMD")
    ap.add_argument("--assets-root", default="experimentos/assets", help="Directorio raíz para imágenes por experimento")
    ap.add_argument("--apply", action="store_true", help="Si se indica, sobrescribe experimentos/<slug>.qmd")
    ap.add_argument("--keep-temp", action="store_true", help="Conservar archivos temporales de conversión")
    args = ap.parse_args()

    input_pdf = Path(args.input)
    if not input_pdf.exists():
        raise SystemExit(f"PDF no encontrado: {input_pdf}")

    work_dir = Path(args.work_dir)
    conv_dir = work_dir / args.slug
    md_path = run_marker(input_pdf, conv_dir)

    extracted = md_path.read_text(encoding="utf-8", errors="ignore")
    extracted = move_images_and_rewrite_markdown(
        extracted_md=extracted,
        conv_dir=conv_dir,
        slug=args.slug,
        assets_root=Path(args.assets_root),
    )
    title = slug_to_title(args.slug)
    qmd = build_qmd(title=title, extracted_md=extracted, source_ref=args.source_ref)

    draft_out = work_dir / f"{args.slug}.draft.qmd"
    draft_out.parent.mkdir(parents=True, exist_ok=True)
    draft_out.write_text(qmd, encoding="utf-8")

    print(f"Markdown extraído: {md_path}")
    print(f"Borrador QMD: {draft_out}")

    if args.apply:
        target = Path("experimentos") / f"{args.slug}.qmd"
        target.write_text(qmd, encoding="utf-8")
        print(f"Aplicado en: {target}")

    if not args.keep_temp:
        cleanup_temp(conv_dir=conv_dir, work_dir=work_dir, slug=args.slug)
        print("Temporales eliminados (usar --keep-temp para conservarlos).")


if __name__ == "__main__":
    main()
