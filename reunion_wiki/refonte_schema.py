"""Additive storage for private, anonymous DEV proposals."""


def ensure_schema(connection):
    """Create the proposal table without committing the caller's migration."""
    connection.execute("""CREATE TABLE IF NOT EXISTS refonte_proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT NOT NULL UNIQUE,
        nonce TEXT NOT NULL UNIQUE,
        kind TEXT NOT NULL CHECK(kind IN ('site','personality')),
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        url_key TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        category_id INTEGER,
        email TEXT NOT NULL DEFAULT '',
        city_id INTEGER REFERENCES villes(id),
        location_scope TEXT,
        supplied_evidence_url TEXT NOT NULL DEFAULT '',
        reunion_attachment TEXT NOT NULL DEFAULT '',
        private_source_reference TEXT NOT NULL DEFAULT '',
        private_source_url TEXT NOT NULL DEFAULT '',
        private_source_note TEXT NOT NULL DEFAULT '',
        status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','preparation','refused','published','archived')),
        refusal_reason TEXT NOT NULL DEFAULT '',
        site_id INTEGER REFERENCES sites(id) ON DELETE SET NULL,
        talent_id INTEGER REFERENCES talents(id) ON DELETE SET NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(kind,url_key)
    )""")
    columns = {row[1] for row in connection.execute('PRAGMA table_info(refonte_proposals)')}
    for name,definition in [('city_id','INTEGER REFERENCES villes(id)'),('location_scope','TEXT'),('supplied_evidence_url',"TEXT NOT NULL DEFAULT ''")]:
        if name not in columns:
            connection.execute(f'ALTER TABLE refonte_proposals ADD COLUMN {name} {definition}')
    connection.execute("CREATE INDEX IF NOT EXISTS idx_refonte_proposals_status ON refonte_proposals(status,id DESC)")
