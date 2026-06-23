"""Ingestion package: importing it registers all format extractors."""

from app.ingestion import csv_txt, docx, pdf, pptx, xlsx  # noqa: F401
