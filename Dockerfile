FROM python:3.12-slim

EXPOSE 6969

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=1 

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root --no-interaction --no-ansi 

COPY . /app

RUN poetry cache clear --all pypi

RUN chmod +x /app/entrypoint.sh

CMD ["./entrypoint.sh"]