"""Private proposal persistence; public views must never receive these rows."""
from ..db import get_db_connection


FIELDS = ('name', 'url', 'url_key', 'description', 'category_id', 'email', 'city_id', 'location_scope', 'supplied_evidence_url',
          'reunion_attachment', 'private_source_reference', 'private_source_url', 'private_source_note')


def get(proposal_id):
    """Read a proposal for authenticated moderation."""
    connection = get_db_connection()
    try:
        return connection.execute('SELECT * FROM refonte_proposals WHERE id=?', (proposal_id,)).fetchone()
    finally:
        connection.close()


def get_by_nonce(nonce):
    """Find the result of an already accepted submission."""
    connection = get_db_connection()
    try:
        return connection.execute('SELECT * FROM refonte_proposals WHERE nonce=?', (nonce,)).fetchone()
    finally:
        connection.close()


def find_duplicate(kind, key, exclude_proposal_id=None):
    """Find a previously stored URL without exposing its private state."""
    connection = get_db_connection()
    try:
        return connection.execute('SELECT id FROM refonte_proposals WHERE kind=? AND url_key=? AND (? IS NULL OR id!=?)', (kind, key, exclude_proposal_id, exclude_proposal_id)).fetchone()
    finally:
        connection.close()


def list_all(status=None):
    """List the moderation queue with a bounded number of private records."""
    connection = get_db_connection()
    try:
        return connection.execute(
            'SELECT * FROM refonte_proposals WHERE (? IS NULL OR status=?) ORDER BY id DESC LIMIT 200',
            (status, status)).fetchall()
    finally:
        connection.close()


def list_talent_urls():
    """Read only identity/link columns needed to detect exact official links."""
    connection = get_db_connection()
    try:
        return connection.execute('SELECT id,slug,status,instagram_url,youtube_url,tiktok_url,facebook_url,website_url FROM talents').fetchall()
    finally:
        connection.close()


def insert(connection, data, token, nonce, site_id=None):
    """Insert one pending proposal inside the caller's transaction."""
    columns = ','.join(FIELDS)
    marks = ','.join('?' for _ in FIELDS)
    cursor = connection.execute(
        f'INSERT INTO refonte_proposals ({columns},kind,token,nonce,site_id) VALUES ({marks},?,?,?,?)',
        tuple(data.get(field, '') for field in FIELDS) + (data['kind'], token, nonce, site_id))
    return cursor.lastrowid


def insert_pending_site(connection, data):
    """Insert the validated site in the same transaction as its proposal."""
    cursor = connection.execute('''INSERT INTO sites
        (nom,lien,description,category_id,ville_id,location_scope,status,date_ajout,submitted_at,updated_at,en_vedette)
        VALUES (?,?,?,?,?,?,'en_attente',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,0)''',
        (data['name'],data['url'],data['description'],data['category_id'],data['city_id'],data['location_scope']))
    return cursor.lastrowid


def update(proposal_id, data):
    """Update validated private editorial values without changing type/state."""
    connection = get_db_connection()
    try:
        assignments = ','.join(field+'=?' for field in FIELDS)
        connection.execute(f'UPDATE refonte_proposals SET {assignments},updated_at=CURRENT_TIMESTAMP WHERE id=?',
                           tuple(data.get(field, '') for field in FIELDS)+(proposal_id,))
        connection.commit()
    finally:
        connection.close()


def set_state(proposal_id, status, talent_id=None, refusal_reason=''):
    """Persist the outcome of a successful administrative operation."""
    connection = get_db_connection()
    try:
        connection.execute('''UPDATE refonte_proposals SET status=?,talent_id=COALESCE(?,talent_id),
            refusal_reason=?,updated_at=CURRENT_TIMESTAMP WHERE id=?''',
            (status,talent_id,refusal_reason,proposal_id))
        connection.commit()
    finally:
        connection.close()


def get_site_record(site_id):
    """Read the linked stored site including optional location identifiers."""
    connection = get_db_connection()
    try:
        return connection.execute('SELECT * FROM sites WHERE id=?',(site_id,)).fetchone()
    finally:
        connection.close()
