from app.ingestion.csv_txt import extract_csv, extract_txt
from app.ingestion.detector import get_extractor
from app.ingestion.models import ElementType


def test_extract_csv() -> None:
    result = extract_csv("people.csv", b"name,age\nAlice,30\nBob,25\n")
    assert result.format == "csv"
    el = result.elements[0]
    assert el.element_type == ElementType.CELL_BLOCK
    assert "name | age" in el.text
    assert "Alice" in el.text and "Bob" in el.text
    assert el.location.row_start == 2 and el.location.row_end == 3


def test_extract_txt() -> None:
    result = extract_txt("notes.txt", b"line one\nline two\nline three\n")
    assert result.format == "txt"
    el = result.elements[0]
    assert el.element_type == ElementType.PARAGRAPH
    assert "line three" in el.text
    assert el.location.row_start == 1 and el.location.row_end == 3


def test_txt_utf8_indonesian() -> None:
    result = extract_txt("x.txt", "Prosedur audit — café, ©2025".encode())
    assert "café" in result.elements[0].text


def test_csv_txt_registered() -> None:
    assert get_extractor("csv") is extract_csv
    assert get_extractor("txt") is extract_txt
