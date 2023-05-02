import validators


def validate(url):
    errors = []
    if url == '':
        errors.extend(['Некорректный URL', 'URL обязателен'])
    elif not validators.url(url):
        errors.append('Некорректный URL')
    return errors
