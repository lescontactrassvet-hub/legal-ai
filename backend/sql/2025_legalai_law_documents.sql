-- Таблица для хранения текстов законов (независимо от пользовательских документов)

CREATE TABLE IF NOT EXISTS law_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    act_id INTEGER,
    source_id INTEGER,
    external_id TEXT,
    chunk_index INTEGER,
    content_html TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (act_id) REFERENCES legal_acts(id),
    FOREIGN KEY (source_id) REFERENCES law_sources(id)
);

-- Индексы для быстрого доступа
CREATE INDEX IF NOT EXISTS idx_law_documents_act_id ON law_documents(act_id);
CREATE INDEX IF NOT EXISTS idx_law_documents_source_id ON law_documents(source_id);

-- Внешний ID документа (URL или guid) должен быть уникален
CREATE UNIQUE INDEX IF NOT EXISTS idx_law_documents_external_id
    ON law_documents(external_id);

