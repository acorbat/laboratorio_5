# TODO — Plan de acción para la web de Laboratorio 5

Este plan está orientado a ejecución por agentes de AI.

## FASE 1 — Sitio funcionando (MVP publicable)

### A. Inventario y estado real del contenido
- [ ] Consolidar inventario desde manifests (`guias`, `seguridad`, `parciales`).
- [ ] Marcar cada recurso con metadata:
  - [ ] tipo (`guía`, `manual`, `paper`, `tesis`, `seguridad`, `adicional`)
  - [ ] estado (`local`, `externo`, `roto`)
  - [ ] experimento asociado
  - [ ] criticidad (`obligatorio`, `recomendado`, `avanzado`)
- [ ] Generar `content_index.json` único para render del sitio.

**Agente sugerido:** `agent-content-indexer`  
**DoD:** índice completo + conteos por sección + lista de links rotos.

---

### B. Completar páginas mínimas necesarias
- [ ] Página `Inicio` con acceso a: Experimentos, Seguridad, Material adicional, Manuales.
- [ ] Página índice de `Experimentos` con cards y links.
- [ ] Página por experimento (mínimo viable):
  - [ ] resumen corto
  - [ ] links a guía(s) PDF
  - [ ] manuales/equipo
  - [ ] papers/tesis (visibles para estudiantes)
  - [ ] seguridad relevante
- [ ] Página `Seguridad` separada y priorizada.
- [ ] Página `Material adicional` separada con indicadores de link roto.
- [ ] Página `/docentes` pública, pero **sin enlace en navegación principal**.

**Agente sugerido:** `agent-page-builder`  
**DoD:** rutas navegables sin 404 internos.

---

### C. Integración de enlaces y UX básica
- [ ] Agregar badges visuales: `PDF`, `Externo`, `Obligatorio`, `En inglés`, `Roto`.
- [ ] Mostrar aviso cuando un recurso está caído + alternativa (si existe).
- [ ] Mostrar “Última actualización” por página.
- [ ] Agregar bloque “Fuente original” para cada recurso.

**Agente sugerido:** `agent-link-ux`  
**DoD:** metadata homogénea en todas las páginas.

---

### D. QA y publicación de v1
- [ ] Validar navegación de estudiante (flujo completo).
- [ ] Validar clasificación de material con criterio docente.
- [ ] Revisar links rotos críticos (guías/seguridad).
- [ ] Publicar `v1.0` con changelog inicial.

**Agente sugerido:** `agent-release-qa`  
**DoD:** sitio funcional + checklist QA aprobado + release tag.

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
1. [ ] Completar **FASE 1** (web operativa v1).
2. [ ] Migración por lotes:
   - [ ] Lote A: Exp 1, 3, 6
   - [ ] Lote B: Exp 4, 7
   - [ ] Lote C: Exp 2, 5
3. [ ] Migrar luego material adicional/manuales extensos.

---

## Plantilla de tarea para agentes
- **Input:** rutas de archivos + URLs + plantilla de página.
- **Output:** página(s) + assets + actualización de índice/manifests.
- **Checks obligatorios:**
  - [ ] links internos OK
  - [ ] links externos chequeados
  - [ ] bloque de seguridad presente
  - [ ] fuentes citadas
- **Cierre:** checklist DoD 100% cumplido.
