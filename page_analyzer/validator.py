def validate(url):
    errors = []
    if url == '':
        errors.extend('Некорректный URl', 'URL обязателен')
    elif not validators.url(url):
        errors.append('Некорректный URL')
    return errors
