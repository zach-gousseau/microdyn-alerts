#!/bin/bash

DB_FILE="alerts.db"
CONTENT_TABLE="content"
METADATA_TABLE="metadata"

# create db if it doesn't exist and define the schema
sqlite3 $DB_FILE <<EOF
-- Create $CONTENT_TABLE table
CREATE TABLE IF NOT EXISTS $CONTENT_TABLE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    text TEXT NOT NULL,
    url TEXT,
    summary TEXT,
    keywords TEXT,
    is_update BOOLEAN NOT NULL CHECK (is_update IN (0, 1)),
    manual_check_required BOOLEAN NOT NULL CHECK (manual_check_required IN (0, 1))
);

-- Create $METADATA_TABLE table
CREATE TABLE IF NOT EXISTS $METADATA_TABLE (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    FOREIGN KEY (content_id) REFERENCES $CONTENT_TABLE(id) ON DELETE CASCADE
);

-- Verify the structure
PRAGMA table_info($CONTENT_TABLE);
PRAGMA table_info($METADATA_TABLE);
EOF

# Output success message
echo "SQLite database '$DB_FILE' created successfully with tables '$CONTENT_TABLE' and '$METADATA_TABLE'."
