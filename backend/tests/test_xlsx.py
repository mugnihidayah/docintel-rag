import io

import openpyxl

from app.ingestion.detector import get_extractor
from app.ingestion.models import ElementType
from app.ingestion.xlsx import extract_xlsx


def _make_xlsx() -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws.append(["Product", "Qty", "Price"])
    ws.append(["Apple", 10, 5])
    ws.append(["Banana", 20, 3])
    ws2 = wb.create_sheet("Notes")
    ws2.append(["Note"])
    ws2.append(["Q1 review"])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_extract_xlsx_sheets_and_rows() -> None:
    result = extract_xlsx("data.xlsx", _make_xlsx())
    assert result.format == "xlsx"
    assert result.num_units == 2

    sales = [e for e in result.elements if e.location.sheet == "Sales"]
    assert sales
    el = sales[0]
    assert el.element_type == ElementType.CELL_BLOCK
    assert "Product | Qty | Price" in el.text  # header repeated
    assert "Apple" in el.text and "Banana" in el.text
    assert el.location.row_start == 2 and el.location.row_end == 3

    assert any(e.location.sheet == "Notes" for e in result.elements)


def test_xlsx_extractor_is_registered() -> None:
    assert get_extractor("xlsx") is extract_xlsx
