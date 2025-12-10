-- Таблица источников законов (конфиг + статус)
CREATE TABLE IF NOT EXISTS law_sources (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 base_url TEXT,
 type TEXT NOT NULL, -- html, api_json, xml, pdf, docx, rtf, file_jsonl, ...
 parser TEXT NOT NULL, -- имя парсера в коде: official_portal, file_jsonl_local, ...
 auth TEXT, -- JSON с auth-конфигом
 config TEXT, -- JSON с доп. настройками (шаблоны URL и пр.)
 is_active INTEGER NOT NULL DEFAULT 1, -- 1 = включен
 schedule_cron TEXT, -- опционально: индивидуальное расписание
 last_success_at TEXT,
 last_error_at TEXT,
 last_error_message TEXT
);

-- Таблица категорий (отраслей)
CREATE TABLE IF NOT EXISTS law_categories (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 code TEXT NOT NULL UNIQUE, -- 'labour', 'criminal', ...
 name_ru TEXT NOT NULL -- 'Трудовое право', ...
);

-- Связь закон ↔ категории (многие-ко-многим)
CREATE TABLE IF NOT EXISTS law_category_links (
 law_id INTEGER NOT NULL,
 category_id INTEGER NOT NULL,
 PRIMARY KEY (law_id, category_id),
 FOREIGN KEY (category_id) REFERENCES law_categories(id)
);

-- Canonical-акты (логические законы вне зависимости от источника)
CREATE TABLE IF NOT EXISTS legal_acts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 canonical_key TEXT NOT NULL UNIQUE, -- jurisdiction|kind|number|date или fallback
 kind TEXT, -- 'federal_law', 'code', 'resolution', ...
 number TEXT, -- номер акта, например '63-ФЗ'
 date_adopted TEXT, -- ISO-дата
 jurisdiction TEXT, -- 'RF', 'RU-MOW', ...
 title TEXT NOT NULL,
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL
);

-- Логи обновлений
CREATE TABLE IF NOT EXISTS law_update_log (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 source_id INTEGER,
 started_at TEXT NOT NULL,
 finished_at TEXT,
 status TEXT NOT NULL, -- 'running', 'success', 'error'
 message TEXT,
 details TEXT,
 FOREIGN KEY (source_id) REFERENCES law_sources(id)
);

-- Расширяем существующую таблицу documents
-- (SQLite не умеет IF NOT EXISTS для ALTER, это одноразовая миграция)
ALTER TABLE documents ADD COLUMN act_id INTEGER;
ALTER TABLE documents ADD COLUMN source_id INTEGER;
ALTER TABLE documents ADD COLUMN external_id TEXT;
ALTER TABLE documents ADD COLUMN chunk_index INTEGER;
ALTER TABLE documents ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1;

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_documents_act_id ON documents(act_id);
CREATE INDEX IF NOT EXISTS idx_documents_source_id ON documents(source_id);
CREATE INDEX IF NOT EXISTS idx_documents_is_active ON documents(is_active);

