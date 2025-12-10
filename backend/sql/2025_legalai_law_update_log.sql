-- Логи обновления источников законов
-- Эти данные будут выводиться в админ-панели

CREATE TABLE IF NOT EXISTS law_update_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- источник (pravo_rss_all, pravo_rss_president, ...)
    source_id INTEGER NOT NULL,

    -- метки времени
    started_at  TEXT NOT NULL,
    finished_at TEXT,

    -- статус: success / error / partial
    status TEXT NOT NULL,

    -- сколько элементов было в RSS
    total_items      INTEGER DEFAULT 0,

    -- сколько попытались обработать
    processed_items  INTEGER DEFAULT 0,

    -- сколько не удалось (ошибки)
    failed_items     INTEGER DEFAULT 0,

    -- сколько реально вставили в law_documents
    inserted_items   INTEGER DEFAULT 0,

    -- текст ошибки (для последних падений)
    error_message    TEXT,

    FOREIGN KEY (source_id) REFERENCES law_sources(id)
);

CREATE INDEX IF NOT EXISTS idx_law_update_log_source_id
    ON law_update_log(source_id);

CREATE INDEX IF NOT EXISTS idx_law_update_log_started_at
    ON law_update_log(started_at);

