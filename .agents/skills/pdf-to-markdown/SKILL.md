---
name: pdf-to-markdown
description: "Agente extractor y conversor de PDFs a Markdown de alta fidelidad (lossless) para alimentar a otros agentes IA con textos legales, tablas, jerarquías y referencias de página."
---

# PDF to Markdown Agent (Lossless Ingestion)

Este agente se encarga de convertir documentos PDF complejos (leyes consolidadas, reglamentos, informes de gestión, especificaciones técnicas) a archivos Markdown estructurados (`.md`), garantizando que **no se pierda ningún dato ni tabla** y que cada fragmento quede trazable mediante metadatos y delimitadores de página.

## Capacidades

1. **Extracción Fiel sin Pérdidas**:
   - Conserva el texto íntegro, articulado, disposiciones y anexos.
   - Jerarquía clara de títulos (`#`, `##`, `###`).
   - Listas numeradas y con viñetas intactas.
2. **Tablas Complejas**:
   - Convierte todas las tablas a formato GitHub Flavored Markdown (`| Col1 | Col2 |`).
3. **Trazabilidad por Páginas**:
   - Cada página del PDF original se delimita con:
     `<!-- ================= PAGE X OF Y ================= -->`
   - Permite que el agente posterior cite con precisión milimétrica la página fuente de cualquier afirmación.
4. **Frontmatter YAML Enriquecido**:
   - Cada archivo `.md` incluye metadatos: título oficial, organismo/autor, total de páginas, recuento de palabras, caracteres, conteo de tablas y la Tabla de Contenidos (TOC) extraída de los marcadores del PDF.
5. **Catálogo para Agentes Downstream**:
   - Genera automáticamente `manifest.json` e `INDEX.md` en el directorio de salida.

## Modo de Uso

### 1. Ejecución por Lote en una Carpeta
```bash
# Procesar todos los PDFs de una carpeta específica
./run_agent.sh "/ruta/a/tu/carpeta"

# O especificando carpeta de entrada y carpeta de salida personalizada
./run_agent.sh -i "/ruta/a/tu/carpeta" -o "/ruta/de/salida"

# Buscar recursivamente en todas las subcarpetas
./run_agent.sh "/ruta/a/tu/carpeta" --recursive -o "/ruta/de/salida"
```

### 2. Conversión de un Archivo Específico
```bash
./run_agent.sh "02 Ley 53_1984, Incompatibilidades del personal al servicio de las AAPP.pdf"
# o con la bandera -f:
./run_agent.sh -f "ruta/al/documento.pdf" -o "markdown_output"
```

### 3. Opciones Disponibles
- `target`: Ruta directa a una carpeta o archivo PDF (argumento posicional).
- `--input-dir`, `-i`: Carpeta con los PDFs fuente.
- `--output-dir`, `-o`: Carpeta destino de los `.md` (por defecto: `markdown_output`).
- `--file`, `-f`: Ruta a un único PDF a procesar.
- `--recursive`, `-r`: Escanea recursivamente subcarpetas dentro del directorio indicado.
- `--no-ocr`: Desactiva el fallback OCR (acelera si todos los PDFs tienen texto digital).
- `--save-images`: Guarda las imágenes y figuras extraídas.

## Estructura de Salida para el Agente Downstream

Los archivos generados se guardan en `markdown_output/`:
- `*.md`: Un archivo Markdown por cada PDF con el mismo nombre base.
- `manifest.json`: Índice estructurado en JSON con metadatos, recuentos de palabras/caracteres/tablas y TOC de cada documento.
- `INDEX.md`: Tabla de contenidos global con enlaces a cada documento y sus estadísticas.

## Protocolo de Lectura para el Segundo Agente
1. El segundo agente debe leer primero `markdown_output/INDEX.md` o `markdown_output/manifest.json` para localizar el documento relevante.
2. Al procesar el archivo `.md`, puede buscar los marcadores `<!-- PAGE X OF Y -->` para indexar chunks exactos o citar páginas concretas.
3. El Frontmatter YAML al inicio de cada archivo contiene el título legal consolidado y la tabla de materias.
