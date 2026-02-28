CREATE TABLE sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie TEXT NOT NULL,
    nom TEXT NOT NULL,
    ville TEXT,
    lien TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'valide' CHECK (status IN ('valide', 'en_attente', 'refuse')),
    date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
    en_vedette INTEGER DEFAULT 0
, display_order INTEGER DEFAULT 0, click_count INTEGER DEFAULT 0);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE sqlite_stat1(tbl,idx,stat);
CREATE INDEX idx_sites_status ON sites(status);
CREATE INDEX idx_sites_categorie ON sites(categorie);
CREATE INDEX idx_sites_date_ajout ON sites(date_ajout DESC);
CREATE INDEX idx_sites_en_vedette ON sites(en_vedette);
CREATE INDEX idx_sites_status_categorie ON sites(status, categorie);
CREATE INDEX idx_sites_status_vedette ON sites(status, en_vedette);
CREATE TABLE talents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL,
                instagram TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT DEFAULT '',
                image TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'en_attente',
                date_created TEXT NOT NULL DEFAULT (DATETIME('now')),
                date_updated TEXT NOT NULL DEFAULT (DATETIME('now'))
            , display_order INTEGER DEFAULT 0);
CREATE INDEX idx_talents_status ON talents(status);
CREATE INDEX idx_talents_category ON talents(category);
CREATE TABLE categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                slug TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
CREATE TABLE login_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  ip TEXT NOT NULL,
  success INTEGER NOT NULL,
  user_agent TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (DATETIME('now'))
);
CREATE INDEX idx_login_attempts_created_at ON login_attempts(created_at);
CREATE INDEX idx_login_attempts_username ON login_attempts(username);
CREATE TABLE site_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP, ip_address TEXT, user_agent TEXT,
    FOREIGN KEY(site_id) REFERENCES sites(id)
);
