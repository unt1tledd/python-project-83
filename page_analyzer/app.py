import os
import psycopg2
import psycopg2.extras
from flask import Flask, request, url_for, flash, redirect, render_template
from validator import validate
from dotenv import load_dotenv
from urllib.parse import urlparse


app = Flask(__name__)


load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/urls')
def post_urls():
    url = request.form.get('url')
    errors = validate(url)
    
    if errors:
        for error in errors:
            flash(error)
        return render_template('index.html', url=url, errors=errors), 422

    parse_url = urlparse(url)
    valid_url = parse_url.scheme + '://' + parse_url.netloc
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id FROM urls
                WHERE name = %s""", [valid_url])
            result = cur.fetchone()[0]
            if result:
                flash('Страница ужу существует', 'alert alert-info')
                return redirect(url_for('added_url', id=result))
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            date = datatime.date.today()
            cur.execute("""
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNINIG id""", [valid_url, date]
            result = cur.fetchone()[0]
            conn.commit()
        flash('Страница успешно добавлена', 'alert alert-success')
        return redirect(url_for('added_url', id=result))


@app.get('/urls/<id>')
def added_url(id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
            cur.execute("""
                SELECT name, created_at FROM urls
                WHERE id = %s""", [id])
            url_name, url_created_at = cur.fetchone()
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT request_cod, h1, title, discription, created_at info
                WHERE id = %s ORDER BY DESC""", [id])
            result = fetchall()
        return render_template(
                'page.html',
                url_name=url_name,
                url_id=id,
                url_created_at=url_created_at.date(),
                checks=result)
