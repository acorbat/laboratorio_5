# TODO — Plan de acción para la web de Laboratorio 5

Este plan está orientado a ejecución por agentes de AI.

## FASE 0 — Bootstrap Quarto + GitHub Pages

- [x] Definir Quarto como stack del sitio.
- [x] Crear `_quarto.yml` con navegación base y `output-dir: docs`.
- [x] Crear páginas base `.qmd` (inicio, secciones y experimentos).
- [x] Definir estilos mínimos (`styles.css`) para badges/avisos.
- [x] Crear workflow de despliegue a GitHub Pages.
- [x] Verificar despliegue en GitHub Pages (sin render local obligatorio) y corregir warnings reportados por CI.

---

## FASE 1 — Sitio funcionando (MVP publicable)

### A. Inventario y estado real del contenido
- [x] Consolidar inventario desde manifests (`guias`, `seguridad`, `parciales`).
- [x] Priorizar enlaces externos en la web MVP (por política temporal de no versionar `*.pdf`/`*.zip`).
- [x] Marcar cada recurso con metadata:
  - [x] tipo (`guía`, `manual`, `paper`, `tesis`, `seguridad`, `adicional`)
  - [x] estado (`local`, `externo`, `roto`)
  - [x] experimento asociado
  - [x] criticidad (`obligatorio`, `recomendado`, `avanzado`)
- [x] Generar `content_index.json` único para render del sitio.

**Agente sugerido:** `agent-content-indexer`  
**DoD:** índice completo + conteos por sección + lista de links rotos.

---

### B. Completar páginas mínimas necesarias
- [x] Página `Inicio` con acceso a: Experimentos, Seguridad, Material adicional, Manuales.
- [x] Página índice de `Experimentos` con links.
- [x] Página por experimento (mínimo viable):
  - [x] resumen corto
  - [x] links a guía(s) PDF
  - [x] manuales/equipo
  - [x] papers/tesis (visibles para estudiantes)
  - [x] seguridad relevante
- [x] Página `Seguridad` separada y priorizada.
- [x] Página `Material adicional` separada con indicadores de link roto.
- [x] Página `/docentes` pública, pero **sin enlace en navegación principal**.

**Agente sugerido:** `agent-page-builder`  
**DoD:** rutas navegables sin 404 internos.

---

### C. Integración de enlaces y UX básica
- [x] Agregar badges visuales: `PDF`, `Externo`, `Obligatorio`, `En inglés`, `Roto`.
- [x] Mostrar aviso cuando un recurso está caído + alternativa (si existe).
- [x] Mostrar “Última actualización” por página.
- [x] Agregar bloque “Fuente original” para cada recurso.

**Agente sugerido:** `agent-link-ux`  
**DoD:** metadata homogénea en todas las páginas.

---

### D. QA y publicación de v1
- [x] Validar navegación de estudiante (flujo completo).
- [x] Validar clasificación de material con criterio docente.
- [x] Revisar links rotos críticos (guías/seguridad).
- [x] Preparar despliegue en GitHub Pages:
  - [x] confirmar estructura estática compatible (`index.html`/ruta base),
  - [x] verificar rutas relativas de assets y páginas,
  - [x] definir estrategia de publicación (`main/docs`).
- [x] Agregar workflow de publicación automática (opcional en v1, recomendado).
- [ ] Publicar `v1.0` con changelog inicial.

**Agente sugerido:** `agent-release-qa`  
**DoD:** sitio funcional + checklist QA aprobado + release tag + despliegue en GitHub Pages operativo.

---

## FASE 2 — Migración de PDFs a contenido web (por experimento)

## Estrategia general
- [ ] Prioridad 1: guías troncales + seguridad asociada.
- [ ] Prioridad 2: manuales de uso frecuente.
- [ ] Prioridad 3: papers/tesis (resumen + link completo).

---

### E. Subagentes por experimento (paralelizable)

Crear subagentes:
- [ ] `agent-exp01-conteo-fotones`
- [ ] `agent-exp02-glow`
- [ ] `agent-exp03-fotoelectrico`
- [ ] `agent-exp04-espectroscopia`
- [ ] `agent-exp05-fluidos`
- [ ] `agent-exp06-laser`
- [ ] `agent-exp07-nuclear-particulas`

Cada subagente debe:
- [ ] Tomar PDFs del experimento.
- [ ] Extraer y limpiar texto.
- [ ] Crear páginas con estructura estándar:
  1. Objetivos
  2. Fundamento teórico
  3. Montaje / Instrumental
  4. Procedimiento
  5. Adquisición y análisis
  6. Preguntas guía
  7. Seguridad específica
  8. Referencias
- [ ] Extraer imágenes/figuras relevantes e insertarlas con caption.
- [ ] Mantener link al PDF original (`versión fuente`).
- [ ] Vincular manuales y referencias externas del experimento.
- [ ] Vincular material de seguridad pertinente.

**DoD por subagente:** página migrada + imágenes + referencias + bloque seguridad + revisión básica.

---

### F. Normalización editorial post-migración
- [ ] Unificar estilo (español principal; inglés permitido en fuentes).
- [ ] Corregir símbolos, unidades y notación.
- [ ] Estandarizar nombres de secciones/tablas.
- [ ] Marcar contenido como “adaptado desde PDF”.

**Agente sugerido:** `agent-editor-cientifico`  
**DoD:** consistencia transversal entre experimentos.

---

### G. QA académico final de migración
- [ ] Revisar exactitud física por experimento.
- [ ] Verificar figuras y referencias.
- [ ] Verificar advertencias de seguridad críticas.
- [ ] Cerrar migración por lotes.

**Agente sugerido:** `agent-academic-review`  
**DoD:** aprobación docente por experimento.

---

## Priorización recomendada
1. [x] Completar **FASE 1** (web operativa v1).
2. [ ] Migración por lotes:
   - [x] Lote A: Exp 1, 3, 6
   - [ ] Lote B: Exp 4, 7
   - [ ] Lote C: Exp 2, 5
3. [ ] Migrar luego material adicional/manuales extensos.

### Avance Fase 2 (ejecutado)
- [x] Conteo de fotones migrado con corrección inicial de ecuaciones y anexo de transcripción completa.
- [x] Migración automática de guías para: glow, fotoeléctrico, espectroscopia difractiva, fluidos, láser, muones y nuclear (con anexo de transcripción automática por práctica).
- [x] Prácticas sin guía específica resueltas en versión simple: Zeeman y Faraday.
- [x] Lista de preguntas de revisión interactiva generada en `materials/_index/migration_questions.md`.
- [ ] Pendiente QA académico fino de contenido migrado.
- [ ] Pendiente corrección manual de ecuaciones/sintaxis OCR en anexos automáticos.
- [x] Manifiesto curado de archivos generado con nombres actuales y contenido (`materials/_index/files_manifest_curated.csv`).
- [x] Registro de migración por skill (búsqueda por práctica) generado en `.agents/skills/l5-practica-migrator/work/matches/`.
- [x] Re-migración de experimentos (excepto conteo-fotones como referencia) ejecutada con flujo del skill y transcripción automática asociada.

---

## Plantilla de tarea para agentes
- **Input:** rutas de archivos + URLs + plantilla de página.
- **Output:** página(s) + assets + actualización de índice/manifests.
- **Checks obligatorios:**
  - [ ] links internos OK
  - [ ] links externos chequeados
  - [ ] bloque de seguridad presente
  - [ ] fuentes citadas
  - [ ] compatibilidad con GitHub Pages (rutas/enlaces estáticos)
- **Cierre:** checklist DoD 100% cumplido.

## Nota operativa (Git)
- [ ] Registrar cada avance en commits chicos y descriptivos.
- [ ] Mantener trazabilidad entre tarea del TODO y commit asociado.
- [ ] Evitar cambios no relacionados en el mismo commit.
- [ ] Mantener `*.pdf` y `*.zip` fuera del repo (salvo cambio explícito de política).
