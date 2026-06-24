from app.db.models import Document, DocumentStatus


def test_document_table_shape() -> None:
    cols = {c.name for c in Document.__table__.columns}
    assert {"id", "filename", "file_hash", "status", "num_chunks", "created_at"} <= cols
    assert Document.__tablename__ == "documents"
    assert DocumentStatus.indexed == "indexed"
    assert Document.__table__.c.file_hash.unique is True
