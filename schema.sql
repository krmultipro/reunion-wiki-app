DROP TABLE IF EXISTS sites;

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
);