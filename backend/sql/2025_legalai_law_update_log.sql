-- Логи обновления источников законов для админ-панели

CREATE TABLE IF NOT EXISTS law_update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    source_id   INTEGER NOT NULL,

    started_at  TEXT NOT NULL,
    finished_at TEXT,

    -- статус: running / success / partial / error
    status      TEXT NOT NULL,

    -- краткое сообщение (например "OK", "fetch error", "partial")
    message     TEXT,

    -- дополнительные детали / текст ошибки / stacktrace
    details     TEXT,

    -- статистика по источнику (для админ-панели)
    total_items     INTEGER DEFAULT 0,
    processed_items INTEGER DEFAULT 0,
    failed_items    INTEGER DEFAULT 0,
    inserted_items  INTEGER DEFAULT 0,

    FOREIGN KEY (source_id) REFERENCES law_sources(id)
);

CREATE INDEX IF NOT EXISTS idx_law_update_log_source_id
    ON law_update_log(source_id);

CREATE INDEX IF NOT EXISTS idx_law_update_log_started_at
    ON law_update_log(started_at);
