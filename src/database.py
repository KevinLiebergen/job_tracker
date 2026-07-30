import sqlite3
from datetime import datetime
from config.settings import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            link TEXT,
            date_added TEXT
        )
    """)
    conn.commit()
    conn.close()


def job_exists(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE id=?", (job_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


def save_job(job_id, job):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO jobs (id, title, company, location, link, date_added)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        job["title"],
        job["company"],
        job["location"],
        job["link"],
        datetime.now().strftime("%Y/%m/%d"),
    ))
    conn.commit()
    conn.close()


def get_latest_jobs(limit=10, company=None, location=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ucompany = f"%{str(company)}%" if company else None
    ulocation = f"%{str(location)}%" if location else None
    query_data = (limit,)
    query = f"""
        SELECT title, company, location, link, date_added
        FROM jobs
    """
    if company and location:
        query += """ WHERE company LIKE ? AND location LIKE ?  """
        query_data = (ucompany, ulocation, limit)
    elif company:
        query += """ WHERE company LIKE ?  """
        query_data = (ucompany, limit)
    elif location:
        query += """ WHERE location LIKE ?  """
        query_data = (ulocation, limit)
    query += """
        ORDER BY rowid DESC
        LIMIT ?
    """
    c.execute(query, query_data)
    results = c.fetchall()
    conn.close()
    return results
