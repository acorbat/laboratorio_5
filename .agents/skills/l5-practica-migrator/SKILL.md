---
name: l5-practica-migrator
description: Migra material de prácticas de Laboratorio 5 a páginas Quarto. Úsalo cuando debas crear o actualizar una página de experimento desde material en materials/, priorizando guías PDF.
---

# Skill: Migración de prácticas L5 (PDF/guía -> página)

Este skill define el flujo obligatorio para construir páginas de prácticas.

## Objetivo operativo del skill

1. Usar **marker** para convertir **todo el PDF de la guía** a markdown.
2. Usar ese markdown como base de migración completa de contenido.
3. Luego, el agente de AI debe revisar y corregir sintaxis/formato (incluyendo ecuaciones), y terminar de migrar el contenido a la página Quarto correspondiente.

## Regla pedagógica principal (obligatoria)

1. **Si existe guía de práctica, su migración textual completa y fiel tiene prioridad.**
2. No redactar páginas como receta de instrucciones para estudiantes.
3. La página debe describir fenómeno, contexto experimental, objetivos de aprendizaje y preguntas orientadoras que fomenten diseño experimental por parte del estudiante.

## Flujo de trabajo

### Paso 1: Buscar material en `materials/`

- Ejecutar `scripts/find_materials.py --practica <slug>`.
- Revisar candidatos en:
  - archivos locales (si existen)
  - links en manifests (`materials/_index/*.csv`)

### Paso 2: Decidir fuente principal

- Si hay guía (`guía`, `guia`, `práctica`, `practica`), marcarla como fuente principal.
- Si no hay guía:
  - detener migración completa,
  - hacer flujo interactivo con usuario para pedir material o criterio alternativo.

### Paso 3: Convertir la guía completa PDF a Markdown con marker-pdf (Pixi)

Usar el environment específico `marker`:

- `pixi run -e marker python scripts/marker_pdf_to_qmd.py --input <ruta_pdf_local> --slug <slug-practica> --source-ref <url_guia>`

El script maneja variantes de CLI entre versiones de marker (`marker_single`) para el parámetro de salida.
Además intenta, en este orden: `--mode fast --disable_ocr`, `--mode fast`, y modo estándar para reducir fallos por backends que requieren Docker/vLLM en Windows.

Resultado esperado:

- markdown de la guía completa extraído por marker,
- borrador `.qmd` generado,
- imágenes movidas a `experimentos/assets/<slug>/`.

> Revisión obligatoria posterior por el agente:
> - corregir sintaxis markdown/quarto,
> - corregir ecuaciones y notación matemática,
> - corregir estructura de secciones,
> - completar la migración final en `experimentos/<slug>.qmd`.
>
> Si aparece `ModuleNotFoundError: No module named 'packaging'`, resolver dependencias con Pixi:
> `pixi install -e marker`
>
> No instalar dependencias desde el script; el entorno lo gestiona Pixi.

Fallback si marker falla:

- `scripts/extract_pdf_text.py --input <ruta_o_url> --output <archivo_txt>`
- registrar que la migración queda parcial hasta resolver conversión completa con marker.

### Paso 3.1: Orden y limpieza de archivos

- Mantener imágenes de la práctica en `experimentos/assets/<slug>/`.
- Eliminar temporales de extracción/conversión al finalizar (salvo debug con `--keep-temp`).
### Paso 4: Revisar markdown convertido y terminar migración en Quarto

- Tomar el markdown completo generado por marker como base principal.
- Corregir sintaxis, ecuaciones y bloques incompatibles con Quarto.
- Integrar el contenido en `experimentos/<slug>.qmd` usando `templates/practica-template.qmd`.
- Mantener esta estructura:
  1. Resumen
  2. Objetivos de aprendizaje
  3. Desarrollo conceptual del fenómeno (desde guía)
  4. Ejes de exploración experimental (no receta)
  5. Preguntas orientadoras
  6. Seguridad específica
  7. Recursos y referencias
  8. Fuente original

### Paso 5: Validación mínima

- Verificar que:
  - se cita la guía fuente,
  - se migró el contenido completo de la guía (o se declara explícitamente qué faltó),
  - no hay texto imperativo tipo checklist para alumnos,
  - se agregan links de seguridad pertinentes,
  - ecuaciones/sintaxis fueron revisadas manualmente,
  - se indica claramente si la migración fue parcial por limitaciones de extracción.

## Modo interactivo cuando no hay guía

Si no hay guía, preguntar explícitamente:

1. ¿Deseas proporcionar PDF/URL alternativo?
2. ¿Deseas construir página en estado "en construcción"?
3. ¿Deseas usar solo referencias/manuales para versión parcial?

No continuar con migración completa sin una decisión del usuario.

## Archivos de soporte

- Plantilla: `templates/practica-template.qmd`
- Búsqueda de material: `scripts/find_materials.py`
- Conversión PDF→Markdown con marker: `scripts/marker_pdf_to_qmd.py`
- Extracción fallback PDF→texto: `scripts/extract_pdf_text.py`
- Checklist: `references/checklist-migracion.md`
