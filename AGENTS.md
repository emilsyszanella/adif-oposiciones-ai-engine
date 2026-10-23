# Arquitectura Multi-Agente: Pipeline de Documentación Legal y Técnica

Este proyecto implementa una arquitectura desacoplada de dos agentes para el procesamiento y análisis exhaustivo de normativas, leyes y documentos técnicos (Adif / Administraciones Públicas).

```
 ┌──────────────────────┐         ┌───────────────────────────┐         ┌──────────────────────────┐
 │      PDFs Fuente     │ ──────> │  Agente 1: Extractor      │ ──────> │   Salida Markdown (.md)  │
 │  (Leyes, Estatutos,  │         │  (pdf_to_md_agent.py)     │         │   - Frontmatter YAML     │
 │   Informes Adif)     │         │  - Lossless layout        │         │   - Tablas GFM           │
 └──────────────────────┘         │  - Trazabilidad de página │         │   - Marcadores de página │
                                  │  - Respaldo OCR           │         │   - manifest.json / INDEX│
                                  └───────────────────────────┘         └────────────┬─────────────┘
                                                                                     │
                                                                                     ▼
                                                                        ┌──────────────────────────┐
                                                                        │  Agente 2: Especialista  │
                                                                        │  (adif_exam_agent.py)    │
                                                                        │  - Herramienta Didáctica │
                                                                        │  - Modo Test Oposición   │
                                                                        │  - Flashcards / Repaso   │
                                                                        │  - Preguntas Falladas    │
                                                                        └──────────────────────────┘
```

---

## 1. Agente 1: Extractor de PDFs a Markdown (`pdf-to-markdown`)

- **Objetivo**: Convertir documentos PDF complejos en archivos Markdown sin perder ni una sola línea de texto, tabla, jerarquía de títulos ni referencia de página.
- **Herramienta**: `pdf_to_md_agent.py` / `run_agent.sh` (alimentado por PyMuPDF, PyMuPDF4LLM y Tesseract OCR).
- **Directorio de salida**: `markdown_output/`
- **Garantías de Calidad**:
  - **Fidelidad**: Comprobación del ratio de caracteres (`lossless_ratio`).
  - **Tablas**: Formato de tabla GitHub Flavored Markdown (`| Columna |`).
  - **Trazabilidad**: Delimitadores `<!-- ================= PAGE X OF Y ================= -->` en cada salto de página original.
  - **Metadatos**: Frontmatter YAML al inicio de cada archivo con título, fecha, autor y Tabla de Contenidos (TOC).

---

## 2. Agente 2: Especialista en Oposiciones Adif (`adif-exam-specialist`)

- **Objetivo**: Crear herramientas didácticas interactivas para opositores de Adif a partir de los 21 temas en Markdown.
- **Herramienta**: `adif_exam_agent.py` / `run_study_tool.sh`.
- **Componentes**:
  1. **Herramienta Web Didáctica (`web_app/`)**:
     - **Modo Test Oposición**: Examen cronometrado con 4 opciones, penalización oficial (-0.33) y explicación razonada con cita exacta al artículo y página del PDF.
     - **Modo Flashcards 3D**: Tarjetas de memoria volteables con atajos de teclado para estudiar en tiempos libres (transporte, descansos).
     - **Modo Preguntas Falladas**: Refuerzo inteligente persistente en `localStorage`.
     - **Explorador del Temario (21 Temas)**: Práctica focalizada tema por tema.
  2. **Simulacros de Examen (`simulacros/`)**:
     - Exámenes completos en formato Markdown imprimibles con plantillas de corrección oficial justificadas.

---

## 3. Instrucciones de Ejecución

### Para ejecutar el Agente 1 (Extractor):
```bash
# Procesar todos los PDFs
./run_agent.sh

# Procesar una carpeta o archivo específico
./run_agent.sh "/ruta/a/la/carpeta" -o "markdown_output"
./run_agent.sh --file "ruta/al/documento.pdf"
```

### Para ejecutar el Agente 2 (Especialista en Estudio de Oposiciones):
```bash
# Iniciar la herramienta didáctica interactiva en el navegador
./run_study_tool.sh

# O mediante Python:
./.venv/bin/python adif_exam_agent.py --serve 8080

# Generar un nuevo simulacro de examen en Markdown
./.venv/bin/python adif_exam_agent.py
```
