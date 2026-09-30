# AGENTS.md — Contexto para agentes de AI (Laboratorio 5)

## 1) Propósito del proyecto
Centralizar y mantener el material de la materia **Laboratorio 5 (Física, UBA)** en un repositorio/web:
- guías de experimentos,
- manuales de equipamiento,
- material de seguridad,
- material adicional,
- referencias externas.

Se busca trazabilidad de cambios y control de enlaces (incluyendo links rotos).

---

## 2) Estado actual
Ya existe una primera etapa de ingesta de materiales:
- Script de sync: `scripts/sync_l5_materials.py`
- Descargas organizadas en:
  - `materials/experiments/...`
  - `materials/seguridad/files/`
  - `materials/parciales/files/`
- Índices y reportes:
  - `materials/_index/sources_manifest.csv`
  - `materials/_index/sources_manifest_guias.csv`
  - `materials/_index/sources_manifest_seguridad.csv`
  - `materials/_index/sources_manifest_parciales.csv`
  - `materials/_index/materials_summary.md`

El esqueleto de la web ya está armado y se puede producir una v1 funcional.

---

## 3) Decisiones de producto (confirmadas)
1. **Tesis y papers** deben estar visibles para estudiantes.
2. Se aceptan recursos críticos externos aunque no estén replicados localmente (por ahora).
3. Sección `/docentes` pública, pero **sin enlace accesible desde navegación de estudiantes**.
4. Idioma principal: **español**. Inglés permitido en fuentes y contenido original.

---

## 4) Objetivo de ejecución por fases

### Fase 1 (MVP): web funcional
- Navegación completa.
- Páginas por experimento con links a recursos.
- Seguridad y material adicional separados.
- Badges y estado de enlaces.

### Fase 2: migración PDF → texto web
- Subagente por experimento.
- Extraer texto e imágenes necesarias.
- Integrar referencias y seguridad en cada página.
- Mantener PDF fuente enlazado.

---

## 5) Estructura de contenido esperada (alto nivel)
- `Inicio`
- `Experimentos` (índice + páginas por experimento)
- `Seguridad`
- `Material adicional`
- `Manuales`
- `/docentes` (pública, no enlazada en menú estudiantil)
- `Estado de materiales` (salud de enlaces)

---

## 6) Convenciones para agentes
- Priorizar español en títulos, UI y redacción.
- Mantener trazabilidad de cada recurso:
  - URL origen,
  - copia local (si existe),
  - estado del link,
  - fecha de verificación.
- No eliminar referencias externas solo por estar en inglés.
- Si un enlace está roto: marcarlo explícitamente y proponer alternativa.
- En migración de PDF, no perder tablas, fórmulas, figuras ni advertencias de seguridad.

---

## 7) Definición de “hecho” (DoD) para tareas típicas
Una tarea se considera completa si:
- contenido integrado en la página correspondiente,
- links internos y externos verificados,
- bloque de seguridad presente cuando aplica,
- fuente original citada,
- cambios reflejados en índices/manifests.

---

## 8) Riesgos y atención especial
- Muchos enlaces dependen de sitios externos históricos (`materias`, `users`, nubes compartidas).
- Hay enlaces rotos en material adicional; deben permanecer listados con estado.
- PDFs heterogéneos: algunos requerirán limpieza manual y/o OCR.

---

## 9) Prioridad operativa recomendada
1. Cerrar Fase 1 (sitio usable de punta a punta).
2. Migrar PDFs por experimento en paralelo con subagentes.
3. Normalizar estilo editorial y control académico final.

---

## 10) Referencias internas clave
- Plan de trabajo detallado: `TODO.md`
- Inventario/estado técnico de materiales: `materials/_index/`
- Script de sincronización: `scripts/sync_l5_materials.py`
