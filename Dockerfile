FROM python:3.8-slim

RUN mkdir -p /server
WORKDIR /server

RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock /server/
COPY saltapi /server/saltapi
RUN poetry config virtualenvs.create false
RUN poetry install

EXPOSE 8000

CMD ["uvicorn", "saltapi.app:app", "--host", "0.0.0.0"]
