import os
import sqlite3


def table_creator(file: str):
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # Wrap schema creation in one transaction
    cur.executescript("""
    BEGIN;

    CREATE TABLE IF NOT EXISTS headlines (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        published_date DATETIME,
        scraped_at DATETIME NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_headlines_source
        ON headlines (source);

    CREATE INDEX IF NOT EXISTS idx_headlines_published_date
        ON headlines (published_date);

    CREATE INDEX IF NOT EXISTS idx_headlines_scraped_at
        ON headlines (scraped_at);

    CREATE INDEX IF NOT EXISTS idx_headlines_source_pubdate
        ON headlines (source, published_date);

    COMMIT;
    """)

    conn.close()


if __name__ == '__main__':
    for filename in os.listdir('./databases'):
        table_creator(f'./databases/{filename}')
