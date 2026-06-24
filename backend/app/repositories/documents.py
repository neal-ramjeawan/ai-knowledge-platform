from psycopg.rows import dict_row


def create_document_with_chunks(conn, filename: str, content_type: str | None, content: str, chunks: list[str]):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO documents (filename, content_type, content)
            VALUES (%s, %s, %s)
            RETURNING id, filename, content_type, created_at;
            """,
            (filename, content_type, content),
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

    return document


def list_documents(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, filename, content_type, created_at
            FROM documents
            ORDER BY created_at DESC;
            """
        )
        return cur.fetchall()


def list_document_chunks(conn, document_id: str):
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
        return cur.fetchall()


def search_chunks(conn, query: str, limit: int = 5):
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
            LIMIT %s;
            """,
            (query, query, limit),
        )
        return cur.fetchall()