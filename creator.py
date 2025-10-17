import os
import sqlite3


def table_creator(file: str):
    conn = sqlite3.connect(file)
    cur = conn.cursor()

    # Wrap schema creation in one transaction
    cur.executescript("""
    BEGIN;

    CREATE TABLE IF NOT EXISTS news_articles (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        published_date DATETIME,
        scraped_at DATETIME NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_news_articles_source
        ON news_articles (source);

    CREATE INDEX IF NOT EXISTS idx_news_articles_published_date
        ON news_articles (published_date);

    CREATE INDEX IF NOT EXISTS idx_news_articles_scraped_at
        ON news_articles (scraped_at);

    CREATE INDEX IF NOT EXISTS idx_news_articles_source_pubdate
        ON news_articles (source, published_date);

    COMMIT;
    """)

    conn.close()


if __name__ == '__main__':
    for filename in os.listdir('./databases'):
        table_creator(f'./databases/{filename}')
