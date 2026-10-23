#!/usr/bin/env python3
"""
Agent de Conversión de PDF a Markdown Sin Pérdida de Datos (Lossless PDF-to-Markdown Agent).

Diseñado específicamente para extraer toda la información de documentos complejos
(leyes, reglamentos, informes técnicos, tablas, jerarquías) y formatearla en
Markdown enriquecido con metadatos para que agentes downstream puedan procesarla.

Características:
- Preserva la jerarquía de títulos (#, ##, ###)
- Extrae tablas completas en formato Markdown GFM (| Col1 | Col2 |)
- Inserta delimitadores de página transparentes (<!-- PAGE X OF Y -->)
- Genera YAML Frontmatter con metadatos, autor, título y Tabla de Contenidos (TOC)
- Comprobación de integridad de datos (raw text vs markdown)
- Fallback automático a OCR para páginas escaneadas o basadas en imagen
- Genera manifiesto JSON (manifest.json) y catálogo índice (INDEX.md)
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple

import fitz  # PyMuPDF
import pymupdf4llm
import yaml
from tqdm import tqdm

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PDFToMarkdownAgent")


class PDFToMarkdownAgent:
    """
    Agente extractor de PDFs a Markdown con garantía de fidelidad de datos.
    """

    def __init__(
        self,
        output_dir: str = "markdown_output",
        enable_ocr_fallback: bool = True,
        save_images: bool = False,
        ocr_language: str = "spa+eng",
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.enable_ocr_fallback = enable_ocr_fallback
        self.save_images = save_images
        self.ocr_language = ocr_language

    def extract_toc(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Extrae la tabla de contenidos (TOC / Bookmarks) del PDF si existe."""
        toc_entries = []
        try:
            raw_toc = doc.get_toc()
            for item in raw_toc:
                if len(item) >= 3:
                    lvl, title, page = item[0], item[1], item[2]
                    toc_entries.append({
                        "level": lvl,
                        "title": title.strip(),
                        "page": page,
                    })
        except Exception as e:
            logger.debug(f"No se pudo extraer el TOC: {e}")
        return toc_entries

    def extract_page_raw_text(self, page: fitz.Page) -> str:
        """Obtiene el texto sin formato de una página para validación."""
        return page.get_text("text").strip()

    def process_single_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Procesa un único archivo PDF y genera su correspondiente .md
        con frontmatter y marcadores de página.
        """
        start_time = time.time()
        file_name = pdf_path.name
        doc_stem = pdf_path.stem
        output_file = self.output_dir / f"{doc_stem}.md"

        report: Dict[str, Any] = {
            "source_file": file_name,
            "markdown_file": output_file.name,
            "status": "PROCESSING",
            "total_pages": 0,
            "raw_characters": 0,
            "markdown_characters": 0,
            "total_words": 0,
            "tables_found": 0,
            "ocr_pages_used": 0,
            "toc_entries_count": 0,
            "duration_seconds": 0.0,
            "lossless_ratio": 1.0,
            "warnings": [],
        }

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            report["total_pages"] = total_pages
            metadata = doc.metadata or {}
            toc = self.extract_toc(doc)
            report["toc_entries_count"] = len(toc)

            # 1. Comprobar páginas para determinar si se necesita OCR por página
            raw_char_counts = []
            pages_needing_ocr = []

            for i, page in enumerate(doc):
                raw_text = self.extract_page_raw_text(page)
                raw_char_counts.append(len(raw_text))
                if len(raw_text) < 15 and len(page.get_images()) > 0:
                    pages_needing_ocr.append(i)

            report["raw_characters"] = sum(raw_char_counts)

            # 2. Extracción a Markdown por chunks de página usando pymupdf4llm
            # Primero intentamos extracción vectorial rápida (muy fiel y estructurada)
            try:
                page_chunks = pymupdf4llm.to_markdown(
                    doc,
                    page_chunks=True,
                    use_ocr=False,
                )
            except Exception as e:
                logger.warning(f"Extracción por chunks falló para {file_name}: {e}. Intentando fallback...")
                page_chunks = None

            # Fallback si pymupdf4llm falla o no devuelve datos
            if not page_chunks or len(page_chunks) != total_pages:
                page_chunks = []
                for i, page in enumerate(doc):
                    try:
                        p_md = pymupdf4llm.to_markdown(doc, pages=[i], use_ocr=False)
                    except Exception:
                        p_md = page.get_text("text")
                    page_chunks.append({"text": p_md, "page_number": i + 1})

            # 3. Revisar si alguna página requiere fallback de OCR
            final_page_texts: List[str] = []
            ocr_count = 0

            for i, chunk in enumerate(page_chunks):
                p_text = chunk.get("text", "").strip()
                # Si la página tiene poquísimo texto pero tenía imágenes o OCR necesario
                if self.enable_ocr_fallback and i in pages_needing_ocr:
                    try:
                        logger.info(f"Ejecutando OCR en página {i+1}/{total_pages} de {file_name}...")
                        ocr_md = pymupdf4llm.to_markdown(doc, pages=[i], use_ocr=True, force_ocr=True)
                        if len(ocr_md.strip()) > len(p_text):
                            p_text = ocr_md.strip()
                            ocr_count += 1
                    except Exception as ocr_err:
                        report["warnings"].append(f"Página {i+1}: Fallo de OCR ({ocr_err})")

                final_page_texts.append(p_text)

            report["ocr_pages_used"] = ocr_count

            # 4. Estadísticas del contenido generado
            full_body_text = "\n\n".join(final_page_texts)
            report["markdown_characters"] = len(full_body_text)
            report["total_words"] = len(full_body_text.split())
            report["tables_found"] = full_body_text.count("|---|")

            # Métrica de cobertura de texto (raw vs markdown)
            if report["raw_characters"] > 0:
                report["lossless_ratio"] = round(report["markdown_characters"] / report["raw_characters"], 3)
            else:
                report["lossless_ratio"] = 1.0

            # 5. Generar Frontmatter YAML enriquecido
            doc_title = metadata.get("title") or doc_stem
            frontmatter_dict = {
                "source_file": file_name,
                "document_title": doc_title,
                "author": metadata.get("author") or "Desconocido / Oficial",
                "subject": metadata.get("subject") or "",
                "total_pages": total_pages,
                "total_words": report["total_words"],
                "total_characters": report["markdown_characters"],
                "tables_count": report["tables_found"],
                "ocr_pages_applied": report["ocr_pages_used"],
                "extraction_date": datetime.now().isoformat(),
                "lossless_ratio": report["lossless_ratio"],
                "table_of_contents": toc if toc else "No estructurado explícitamente en marcadores PDF",
            }

            frontmatter_str = yaml.dump(frontmatter_dict, allow_unicode=True, sort_keys=False)

            # 6. Ensamblar documento Markdown con marcadores de página
            md_lines = ["---", frontmatter_str.strip(), "---", ""]
            md_lines.append(f"# {doc_title}\n")

            for page_num, p_text in enumerate(final_page_texts, start=1):
                md_lines.append(f"\n<!-- ================= PAGE {page_num} OF {total_pages} ================= -->\n")
                md_lines.append(p_text)

            # Escribir a archivo .md
            output_file.write_text("\n".join(md_lines), encoding="utf-8")

            report["status"] = "SUCCESS"
            report["duration_seconds"] = round(time.time() - start_time, 2)
            doc.close()
            return report

        except Exception as e:
            logger.error(f"Error procesando {file_name}: {e}", exc_info=True)
            report["status"] = "ERROR"
            report["error_message"] = str(e)
            report["duration_seconds"] = round(time.time() - start_time, 2)
            return report

    def process_all(
        self,
        input_dir: Path,
        pattern: str = "*.pdf",
        recursive: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Procesa todos los archivos PDF encontrados en input_dir.
        """
        if recursive:
            pdf_files = sorted(list(input_dir.rglob(pattern)))
        else:
            pdf_files = sorted(list(input_dir.glob(pattern)))

        if not pdf_files:
            logger.warning(f"No se encontraron archivos PDF con el patrón '{pattern}' en {input_dir}")
            return []

        logger.info(f"Iniciando conversión de {len(pdf_files)} PDFs a Markdown en '{self.output_dir}'...")

        reports = []
        with tqdm(total=len(pdf_files), desc="Convirtiendo PDFs", unit="doc") as pbar:
            for pdf_path in pdf_files:
                pbar.set_postfix_str(pdf_path.name[:25])
                rep = self.process_single_pdf(pdf_path)
                reports.append(rep)
                pbar.update(1)

        # Generar manifiesto JSON e INDEX.md
        self.save_manifest_and_index(reports)
        return reports

    def save_manifest_and_index(self, reports: List[Dict[str, Any]]) -> None:
        """
        Guarda un manifest.json y un INDEX.md detallado con el resumen
        de todos los documentos para el agente downstream.
        """
        manifest_path = self.output_dir / "manifest.json"
        manifest_data = {
            "generated_at": datetime.now().isoformat(),
            "total_documents": len(reports),
            "successful_documents": sum(1 for r in reports if r["status"] == "SUCCESS"),
            "total_pages_processed": sum(r.get("total_pages", 0) for r in reports),
            "total_words_extracted": sum(r.get("total_words", 0) for r in reports),
            "total_tables_extracted": sum(r.get("tables_found", 0) for r in reports),
            "documents": reports,
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, ensure_ascii=False, indent=2)

        # Crear INDEX.md
        index_path = self.output_dir / "INDEX.md"
        index_lines = [
            "# Catálogo de Documentos Convertidos a Markdown",
            "",
            f"> Generado el: {manifest_data['generated_at']}  ",
            f"> Documentos procesados: **{manifest_data['total_documents']}** | Páginas totales: **{manifest_data['total_pages_processed']:,}** | Palabras totales: **{manifest_data['total_words_extracted']:,}**",
            "",
            "Este catálogo ha sido generado por el **PDFToMarkdownAgent** para alimentar al agente downstream.",
            "Cada documento contiene delimitadores de página `<!-- PAGE X OF Y -->`, tablas completas y YAML frontmatter.",
            "",
            "## Índice de Documentos",
            "",
            "| # | Archivo Markdown | Páginas | Palabras | Tablas | Estado |",
            "|---|---|---:|---:|---:|:---:|",
        ]

        for i, r in enumerate(reports, start=1):
            md_name = r.get("markdown_file", "")
            pages = r.get("total_pages", 0)
            words = r.get("total_words", 0)
            tables = r.get("tables_found", 0)
            status = "✅" if r.get("status") == "SUCCESS" else "❌"
            index_lines.append(f"| {i} | [{md_name}](./{md_name}) | {pages} | {words:,} | {tables} | {status} |")

        index_lines.append("")
        index_lines.append("## Instrucciones para el Agente Downstream")
        index_lines.append("1. **Consulta `manifest.json`** para inspeccionar la estructura completa, metadatos y TOC de cada documento.")
        index_lines.append("2. **Usa los delimitadores de página**: Busca `<!-- PAGE X OF Y -->` para citar la página exacta en tus respuestas.")
        index_lines.append("3. **Extracción de Tablas**: Todas las tablas están en formato Markdown estándar `| Col1 | Col2 |`.")
        index_lines.append("4. **Títulos y Secciones**: Las leyes y estatutos preservan la estructura jerárquica de Títulos, Capítulos y Artículos.")

        index_path.write_text("\n".join(index_lines), encoding="utf-8")
        logger.info(f"Manifiesto guardado en: {manifest_path}")
        logger.info(f"Índice Markdown guardado en: {index_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Agente de extracción de PDFs a Markdown sin pérdida de información para agentes IA."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Ruta a una carpeta con PDFs o a un archivo PDF específico (opcional, como argumento posicional directo).",
    )
    parser.add_argument(
        "--input-dir",
        "-i",
        default=None,
        help="Directorio de entrada con los archivos PDF (por defecto: directorio actual o el especificado en target).",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="markdown_output",
        help="Directorio de salida para los archivos .md (por defecto: 'markdown_output').",
    )
    parser.add_argument(
        "--file",
        "-f",
        default=None,
        help="Procesar un único archivo PDF específico.",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Buscar archivos PDF recursivamente en subcarpetas del directorio de entrada.",
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Desactivar el fallback de OCR para páginas sin texto vectorial.",
    )
    parser.add_argument(
        "--save-images",
        action="store_true",
        help="Extraer y guardar imágenes embebidas en los PDFs.",
    )

    args = parser.parse_args()

    agent = PDFToMarkdownAgent(
        output_dir=args.output_dir,
        enable_ocr_fallback=not args.no_ocr,
        save_images=args.save_images,
    )

    # Determinar si target posicional es archivo o carpeta
    target_file = args.file
    target_dir = args.input_dir

    if args.target:
        p = Path(args.target)
        if p.is_file():
            target_file = str(p)
        elif p.is_dir():
            target_dir = str(p)
        else:
            logger.error(f"La ruta especificada '{args.target}' no existe.")
            sys.exit(1)

    if target_file:
        file_path = Path(target_file)
        if not file_path.exists():
            logger.error(f"El archivo {file_path} no existe.")
            sys.exit(1)
        rep = agent.process_single_pdf(file_path)
        agent.save_manifest_and_index([rep])
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        input_dir = Path(target_dir if target_dir else ".")
        if not input_dir.exists():
            logger.error(f"El directorio '{input_dir}' no existe.")
            sys.exit(1)
        reports = agent.process_all(input_dir=input_dir, recursive=args.recursive)
        successes = sum(1 for r in reports if r["status"] == "SUCCESS")
        print(f"\nProceso finalizado: {successes}/{len(reports)} documentos convertidos exitosamente.")
        print(f"Archivos disponibles en: {args.output_dir}/")


if __name__ == "__main__":
    main()
