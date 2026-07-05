from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.db import get_connection
from app.migrations import initialize_database
from app.repositories.documents import (
    create_document_with_chunks,
    list_document_chunks,
    list_documents,
    search_chunks,
    semantic_search_chunks,
)
from app.text import chunk_text

app = FastAPI(title="AI Knowledge Platform API")

initialize_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    raw_content = await file.read()
    text_content = raw_content.decode("utf-8")
    chunks = chunk_text(text_content)

    with get_connection() as conn:
        document = create_document_with_chunks(
            conn,
            filename=file.filename,
            content_type=file.content_type,
            content=text_content,
            chunks=chunks,
        )

    return {
        "message": "Document saved and chunked successfully",
        "document": document,
        "chunk_count": len(chunks),
    }


@app.get("/documents")
def get_documents():
    with get_connection() as conn:
        documents = list_documents(conn)

    return {"documents": documents}


@app.get("/documents/{document_id}/chunks")
def get_document_chunks(document_id: str):
    with get_connection() as conn:
        chunks = list_document_chunks(conn, document_id)

    return {"chunks": chunks}


@app.get("/search")
def search(q: str):
    with get_connection() as conn:
        results = search_chunks(conn, q)

    return {
        "query": q,
        "results": results,
    }


@app.post("/ask")
def ask_question(request: AskRequest):
    with get_connection() as conn:
        context = semantic_search_chunks(conn, request.question)

    return {
        "question": request.question,
        "answer": "LLM generation is not enabled yet. Returning semantic context only.",
        "context": context,
    }

@app.get("/semantic-search")
def semantic_search(q: str):
    with get_connection() as conn:
        results = semantic_search_chunks(conn, q)

    return {
        "query": q,
        "results": results,
    }