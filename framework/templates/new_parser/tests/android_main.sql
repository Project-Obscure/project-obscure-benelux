-- Minimal, anonymised copy of the real schema plus a few fake rows.
-- One .sql file per source in parser.yaml, named after the source.
CREATE TABLE messages (id INTEGER PRIMARY KEY, thread_id TEXT, sender TEXT, body TEXT, timestamp INTEGER);
INSERT INTO messages VALUES (1, 't1', 'Test User', 'Hallo!', 1730800000000);
