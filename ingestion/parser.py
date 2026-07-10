"""
ingestion/parser.py
===================
Production-grade document parser supporting local PDF, XLSX/CSV, DOCX, PNG/JPG, and HTML files.
Uses Docling as the primary engine with robust multi-format fallback parsers to ensure zero crashes
even when running offline without heavy OCR dependencies.
"""

import csv
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger("DoclingParser")


class DoclingParser:
    """
    Universal local document parser for industrial plant documents.
    Extracts clean markdown, structured tables, page counts, and OCR status.
    """

    def __init__(self):
        self._converter = None
        self._docling_available = False
        self._init_docling()

    def _init_docling(self) -> None:
        try:
            from docling.document_converter import DocumentConverter
            self._converter = DocumentConverter()
            self._docling_available = True
            logger.info("Docling DocumentConverter initialized successfully.")
        except ImportError as e:
            logger.warning(f"Docling not installed ({e}). Using robust fallback parsers.")
        except Exception as e:
            logger.warning(f"Error initializing Docling ({e}). Using robust fallback parsers.")

    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a document file and return structured content.

        Returns:
            Dict containing:
            - markdown (str): Clean text formatted as markdown.
            - tables (List[Dict]): Extracted tables or structured data.
            - pages (int): Total page count.
            - ocr (bool): Whether optical character recognition was applied.
            - file_type (str): Extension without dot (e.g., 'PDF', 'XLSX').
            - file_name (str): Basename of the file.
            - file_path (str): Absolute file path.
        """
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Cannot parse document: file not found at {path}")

        ext = path.suffix.lower()
        file_type = ext.lstrip(".").upper() or "TXT"

        logger.info(f"Parsing document: {path.name} ({file_type})...")

        # 1. Attempt primary Docling conversion for supported documents
        if self._docling_available and ext in [".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"]:
            try:
                return self._parse_with_docling(path, file_type)
            except Exception as e:
                logger.warning(f"Docling conversion failed for {path.name}: {e}. Attempting fallback.")

        # 2. Robust format-specific fallbacks
        if ext in [".xlsx", ".xls", ".csv"]:
            return self._parse_tabular(path, file_type)
        elif ext == ".json":
            return self._parse_json(path, file_type)
        elif ext == ".pdf":
            return self._parse_pdf_fallback(path, file_type)
        elif ext in [".html", ".htm"]:
            return self._parse_html_fallback(path, file_type)
        else:
            return self._parse_text_fallback(path, file_type)

    def _parse_with_docling(self, path: Path, file_type: str) -> Dict[str, Any]:
        res = self._converter.convert(str(path))
        doc = res.document
        markdown_text = doc.export_to_markdown()

        # Extract tables if available
        tables = []
        if hasattr(doc, "tables"):
            for idx, table in enumerate(doc.tables):
                try:
                    tables.append({
                        "table_id": f"TABLE_{idx+1}",
                        "markdown": table.export_to_markdown() if hasattr(table, "export_to_markdown") else str(table),
                    })
                except Exception:
                    pass

        # Determine page count
        pages = 1
        if hasattr(doc, "pages") and doc.pages:
            pages = len(doc.pages)

        # Check OCR status
        ocr_used = path.suffix.lower() in [".png", ".jpg", ".jpeg"] or (hasattr(res, "ocr_used") and res.ocr_used)

        return {
            "markdown": markdown_text.strip(),
            "tables": tables,
            "pages": pages,
            "ocr": bool(ocr_used),
            "file_type": file_type,
            "file_name": path.name,
            "file_path": str(path),
        }

    def _df_to_markdown(self, df) -> str:
        """Format a pandas DataFrame as a markdown table without requiring tabulate."""
        try:
            return df.to_markdown(index=False)
        except ImportError:
            headers = list(df.columns)
            header_str = "| " + " | ".join(str(h) for h in headers) + " |"
            sep_str = "| " + " | ".join(["---"] * len(headers)) + " |"
            rows_str = []
            for _, row in df.iterrows():
                rows_str.append("| " + " | ".join(str(val) for val in row) + " |")
            return f"{header_str}\n{sep_str}\n" + "\n".join(rows_str)

    def _parse_tabular(self, path: Path, file_type: str) -> Dict[str, Any]:
        """Fallback parser for Excel spreadsheets and CSV files using pandas or standard csv."""
        markdown_lines = [f"# Tabular Data: {path.name}\n"]
        tables = []

        try:
            import pandas as pd
            if file_type == "CSV":
                df = pd.read_csv(path)
                md_table = self._df_to_markdown(df)
                markdown_lines.append(md_table)
                tables.append({"table_id": "TABLE_1", "markdown": md_table, "rows": len(df)})
            else:
                excel = pd.ExcelFile(path)
                for idx, sheet_name in enumerate(excel.sheet_names):
                    df = excel.parse(sheet_name)
                    md_table = self._df_to_markdown(df)
                    markdown_lines.append(f"## Sheet: {sheet_name}\n\n{md_table}\n")
                    tables.append({"table_id": f"SHEET_{idx+1}_{sheet_name}", "markdown": md_table, "rows": len(df)})
        except ImportError:
            logger.debug("pandas not installed. Using standard csv module fallback.")
            if file_type == "CSV":
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if rows:
                        header = "| " + " | ".join(rows[0]) + " |"
                        sep = "| " + " | ".join(["---"] * len(rows[0])) + " |"
                        body = "\n".join(["| " + " | ".join(r) + " |" for r in rows[1:]])
                        md_table = f"{header}\n{sep}\n{body}"
                        markdown_lines.append(md_table)
                        tables.append({"table_id": "TABLE_1", "markdown": md_table, "rows": len(rows)-1})
            else:
                markdown_lines.append(f"*[Excel file {path.name} requires pandas/openpyxl for full table parsing]*")

        return {
            "markdown": "\n".join(markdown_lines).strip(),
            "tables": tables,
            "pages": 1,
            "ocr": False,
            "file_type": file_type,
            "file_name": path.name,
            "file_path": str(path),
        }

    def _parse_json(self, path: Path, file_type: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        if isinstance(data, list):
            md_lines = [f"# Structured Records: {path.name}\n"]
            for idx, item in enumerate(data, 1):
                md_lines.append(f"## Record {idx}\n")
                if isinstance(item, dict):
                    for k, v in item.items():
                        md_lines.append(f"- **{k}**: {v}")
                else:
                    md_lines.append(str(item))
                md_lines.append("")
            markdown_text = "\n".join(md_lines)
        elif isinstance(data, dict):
            md_lines = [f"# Document: {path.name}\n"]
            for k, v in data.items():
                if isinstance(v, (list, dict)):
                    md_lines.append(f"## {k}\n\n```json\n{json.dumps(v, indent=2)}\n```\n")
                else:
                    md_lines.append(f"- **{k}**: {v}")
            markdown_text = "\n".join(md_lines)
        else:
            markdown_text = str(data)

        return {
            "markdown": markdown_text.strip(),
            "tables": [],
            "pages": 1,
            "ocr": False,
            "file_type": file_type,
            "file_name": path.name,
            "file_path": str(path),
        }

    def _parse_pdf_fallback(self, path: Path, file_type: str) -> Dict[str, Any]:
        """Fallback PDF text extractor using pypdf, PyPDF2, or pdfplumber."""
        pages_text = []
        page_count = 1

        try:
            import pypdf
            reader = pypdf.PdfReader(path)
            page_count = len(reader.pages)
            for idx, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                pages_text.append(f"--- Page {idx} ---\n\n{text.strip()}")
        except ImportError:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(path)
                page_count = len(reader.pages)
                for idx, page in enumerate(reader.pages, 1):
                    text = page.extract_text() or ""
                    pages_text.append(f"--- Page {idx} ---\n\n{text.strip()}")
            except ImportError:
                logger.warning("No PDF parser installed (docling/pypdf/PyPDF2). Cannot extract text from PDF.")
                pages_text.append(f"# PDF Document: {path.name}\n\n*[Text extraction requires pypdf or docling]*")

        return {
            "markdown": "\n\n".join(pages_text).strip(),
            "tables": [],
            "pages": page_count,
            "ocr": False,
            "file_type": file_type,
            "file_name": path.name,
            "file_path": str(path),
        }

    def _parse_html_fallback(self, path: Path, file_type: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()

        # Strip HTML tags and decode basic entities
        clean_text = re.sub(r"<style.*?>.*?</style>", "", html_content, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r"<script.*?>.*?</script>", "", clean_text, flags=re.DOTALL | re.IGNORECASE)
        clean_text = re.sub(r"<[^>]+>", " ", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        return {
            "markdown": f"# HTML Document: {path.name}\n\n{clean_text}",
            "tables": [],
            "pages": 1,
            "ocr": False,
            "file_type": file_type,
            "file_name": path.name,
            "file_path": str(path),
        }

    def _parse_text_fallback(self, path: Path, file_type: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        return {
            "markdown": content.strip(),
            "tables": [],
            "pages": 1,
            "ocr": False,
            "file_type": file_type,
            "file_name": path.name,
            "file_path": str(path),
        }
