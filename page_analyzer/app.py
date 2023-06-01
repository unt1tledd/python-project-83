import os
import psycopg2
import requests
from page_analyzer import db_actions
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
            flash(error, "danger")
        return render_template('index.html', url=url), 422

    parse_url = urlparse(url)
    valid_url = parse_url.scheme + '://' + parse_url.netloc
    result = db_actions.select_id_urls(get_conn, valid_url)
    if result:
        flash('Страница уже существует', 'info')
        return redirect(url_for('add_url', id=result.id))
    url_id = db_actions.insert_into_urls(get_conn, valid_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('add_url', id=url_id))


@app.route('/urls/<id>')
def add_url(id):
    url_name, url_created_at, checks = db_actions.check_url(get_conn, id)
    return render_template('page.html',
                           url_name=url_name,
                           url_id=id,
                           url_created_at=url_created_at.date(),
                           checks=checks)


@app.get('/urls')
def get_urls():
    urls = db_actions.make_list_of_urls(get_conn)
    return render_template('pages.html', checks=urls)


@app.route('/urls/<id>/checks', methods=['POST'])
def check_id(id):
    url_name = db_actions.get_name_url(get_conn, id)
    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except (ConnectionError, HTTPError):
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for('add_url', id=id))

    status_code = response.status_code
    h1, title, meta = get_content(response.text)
    url = [id, status_code, h1, title, meta]
    db_actions.insert_into_urls_checks(get_conn, url)
    flash("Страница успешно проверена", "success")
    return redirect(url_for('add_url', id=id))
