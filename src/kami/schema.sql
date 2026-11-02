PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    series_type TEXT NOT NULL 
        CHECK (series_type IN (
                'Manga', 
                'Manhwa', 
                'Manhua', 
                'Novel', 
                'Webtoon', 
                'Comic')
        ),
    author TEXT,
    status TEXT NOT NULL DEFAULT 'Reading' 
        CHECK (status IN (
                'Reading', 
                'Completed', 
                'On Hold', 
                'Dropped')
        ),
    started_at TEXT,
    
    UNIQUE (title, series_type)
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS series_tags (
    series_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    PRIMARY KEY (series_id, tag_id),

    FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY,
    series_id INTEGER NOT NULL,
    chapter TEXT NOT NULL,
    read_date TEXT,

    UNIQUE (series_id, chapter)
);

CREATE INDEX IF NOT EXISTS idx_chapters_series ON chapters(series_id);
CREATE INDEX IF NOT EXISTS idx_chapters_read_date ON chapters(read_date);
CREATE INDEX IF NOT EXISTS idx_series_status ON series(status);
CREATE INDEX IF NOT EXISTS idx_series_type ON series(series_type);
