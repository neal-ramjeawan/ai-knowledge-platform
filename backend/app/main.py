from fastapi import FastAPI, UploadFile, File
from app.db import get_connection
from psycopg.rows import dict_row
from app.text import chunk_text
from pydantic import BaseModel

app = FastAPI(title="AI Knowledge Platform API")

class AskRequest(BaseModel):
    question: str

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db/health")
def database_health_check():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()

    return {
        "status": "ok",
        "database": "connected",
        "result": result[0],
    }

@app.get("/documents")
def list_documents():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, filename, content_type, created_at
                FROM documents
                ORDER BY created_at DESC;
                """
            )
            documents = cur.fetchall()

    return {"documents": documents}

@app.get("/documents/{document_id}/chunks")
def list_document_chunks(document_id: str):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT id, document_id, chunk_index, content, created_at
                FROM document_chunks
                WHERE document_id = %s
                ORDER BY chunk_index ASC;
                """,
                (document_id,),
            )
            chunks = cur.fetchall()

    return {"chunks": chunks}

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    raw_content = await file.read()
    text_content = raw_content.decode("utf-8")
    chunks = chunk_text(text_content)

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO documents (filename, content_type, content)
                VALUES (%s, %s, %s)
                RETURNING id, filename, content_type, created_at;
                """,
                (file.filename, file.content_type, text_content),
            )
            document = cur.fetchone()

            for index, chunk in enumerate(chunks):
                cur.execute(
                    """
                    INSERT INTO document_chunks (document_id, chunk_index, content)
                    VALUES (%s, %s, %s);
                    """,
                    (document["id"], index, chunk),
                )

    return {
        "message": "Document saved and chunked successfully",
        "document": document,
        "chunk_count": len(chunks),
    }

@app.get("/search")
def search_chunks(q: str):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    dc.id,
                    dc.document_id,
                    d.filename,
                    dc.chunk_index,
                    dc.content,
                    ts_rank(
                        to_tsvector('english', dc.content),
                        plainto_tsquery('english', %s)
                    ) AS rank
                FROM document_chunks dc
                JOIN documents d ON d.id = dc.document_id
                WHERE to_tsvector('english', dc.content) @@ plainto_tsquery('english', %s)
                ORDER BY rank DESC
                LIMIT 5;
                """,
                (q, q),
            )
            results = cur.fetchall()

    return {
        "query": q,
        "results": results,
    }

@app.post("/ask")
def ask_question(request: AskRequest):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT
                    dc.id,
                    dc.document_id,
                    d.filename,
                    dc.chunk_index,
                    dc.content,
                    ts_rank(
                        to_tsvector('english', dc.content),
                        plainto_tsquery('english', %s)
                    ) AS rank
                FROM document_chunks dc
                JOIN documents d ON d.id = dc.document_id
                WHERE to_tsvector('english', dc.content) @@ plainto_tsquery('english', %s)
                ORDER BY rank DESC
                LIMIT 5;
                """,
                (request.question, request.question),
            )
            context = cur.fetchall()

    return {
        "question": request.question,
        "answer": "LLM generation is not enabled yet. Returning retrieved context only.",
        "context": context,
    }