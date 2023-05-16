import os
import psycopg2
import psycopg2.extras
import datetime
import requests
from flask import Flask, request, url_for, flash, redirect, render_template
from page_analyzer.validator import validate
from requests import ConnectionError, HTTPError
from dotenv import load_dotenv
from urllib.parse import urlparse
from page_analyzer.content_of_page import get_content


app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def post_url():
    url = request.form.get('url')
    errors = validate(url)

    if errors:
        for error in errors:
            flash(error, "alert alert-danger")
        return render_template('index.html', url=url), 422

    parse_url = urlparse(url)
    valid_url = parse_url.scheme + '://' + parse_url.netloc
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id FROM urls
                WHERE name = %s""", [valid_url])
            result = cur.fetchone()
            if result:
                flash('Страница уже существует', 'alert alert-info')
                return redirect(url_for('added_url', id=result.id))
    with get_conn() as conn:
        with conn.cursor() as cur:
            date = datetime.date.today()
            cur.execute("""
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNING id""", [valid_url, date])
            url_id = cur.fetchone()[0]
            conn.commit()
        flash('Страница успешно добавлена', 'alert alert-success')
        return redirect(url_for('added_url', id=url_id))


@app.route('/urls/<id>')
def added_url(id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, created_at FROM urls
                WHERE id = %s""", [id])
            url_name, url_created_at = cur.fetchone()

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s ORDER BY id DESC""", [id])
            checks = cur.fetchall()
    return render_template('page.html',
                           url_name=url_name,
                           url_id=id,
                           url_created_at=url_created_at.date(),
                           checks=checks)


@app.get('/urls')
def get_urls():
    with get_conn() as conn:
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
    return render_template('pages.html', checks=urls)


@app.route('/urls/<id>/checks', methods=['POST'])
def id_check(id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT name
                FROM urls
                WHERE id = %s""", [id])
            result = cur.fetchone()

    url_name = result.name
    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except (ConnectionError, HTTPError):
        flash("Произошла ошибка при проверке", "alert alert-danger")
        return redirect(url_for('added_url', id=id))

    status_code = response.status_code
    h1, title, meta = get_content(response.text)
    with get_conn() as conn:
        with conn.cursor() as cur:
            date = datetime.date.today()
            cur.execute("""
                INSERT INTO url_checks (url_id, created_at, status_code, h1, title, description)
                VALUES (%s, %s, %s, %s, %s, %s)""", [
                id, date, status_code, h1, title, meta])
            conn.commit()
    flash("Страница успешно проверена", "alert alert-success")
    return redirect(url_for('added_url', id=id))
