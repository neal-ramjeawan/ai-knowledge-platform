from app.migrations import split_sql_statements


def test_split_sql_statements_handles_multiple_statements():
    sql = "CREATE TABLE foo (id INTEGER);\nCREATE INDEX idx ON foo (id);"

    statements = split_sql_statements(sql)

    assert statements == [
        "CREATE TABLE foo (id INTEGER)",
        "CREATE INDEX idx ON foo (id)",
    ]
