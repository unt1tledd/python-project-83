import psycopg2
import psycopg2.extras
import datetime


def select_id_urls(f, valid_url):
    with f() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id FROM urls
                WHERE name = %s""", [valid_url])
            result = cur.fetchone()
    return result


def insert_into_urls(f, valid_url):
    with f() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            date = datetime.date.today()
            cur.execute("""
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNING id""", [valid_url, date])
            url_id = cur.fetchone().id
    return url_id


def check_url(f, id):
    with f() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, created_at FROM urls
                WHERE id = %s""", [id])
            url_name, url_created_at = cur.fetchone()
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s ORDER BY id DESC""", [id])
            checks = cur.fetchall()
    return url_name, url_created_at, checks


def make_list_of_urls(f):
    with f() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT urls.id, urls.name, url_checks.created_at,
                url_checks.status_code FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                WHERE url_checks.url_id IS NULL OR
                url_checks.id = (SELECT MAX(url_checks.id) FROM url_checks
                WHERE url_checks.url_id = urls.id)
                ORDER BY urls.id DESC""")
            urls = cur.fetchall()
    return urls


def get_name_url(f, id):
    with f() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT name
                FROM urls
                WHERE id = %s""", [id])
            name = cur.fetchone().name
    return name


def insert_into_urls_checks(f, url):
    id, status_code, h1, title, meta = url
    with f() as conn:
        with conn.cursor() as cur:
            date = datetime.date.today()
            cur.execute("""
                INSERT INTO url_checks
                (url_id, created_at, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s, %s)""", [
                id, date, status_code, h1, title, meta])
