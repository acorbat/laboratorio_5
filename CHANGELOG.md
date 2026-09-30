# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.

## [v1.0.1] - 2026-09-30

### Corregido
- Actualizado workflow de GitHub Actions para mitigar warnings por deprecación de Node.js 20:
  - `actions/checkout@v5`
  - `actions/upload-pages-artifact@v4`
  - `actions/deploy-pages@v5`
- Fijado runner de GitHub Actions a Ubuntu 24.04 para evitar cambios inesperados por migración futura de `ubuntu-latest`:
  - `runs-on: ubuntu-24.04` en jobs de build y deploy.

### Agregado
- Logo institucional del Departamento de Física en la configuración del sitio Quarto:
  - `website.logo: assets/logo_df.jpg`

## [v1.0.0] - 2026-09-30

### Agregado
- Estructura base del sitio en Quarto (`_quarto.yml`, páginas `.qmd`, estilos base).
- Secciones MVP:
  - Inicio
  - Experimentos (índice + 7 páginas)
  - Seguridad
  - Material adicional
  - Manuales
  - Estado de materiales
  - Docentes (ruta pública sin enlace en navbar)
- Workflow de publicación automática a GitHub Pages.
- Integración inicial de badges (`PDF`, `Externo`, `Obligatorio`, `En inglés`, `Roto`).

### Documentación
- Definición de contexto operativo para agentes de AI (`AGENTS.md`).
- Plan de trabajo por fases (`TODO.md`).
