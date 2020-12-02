FROM python:3.8

# Create the directory for the server
RUN mkdir -p /server
RUN mkdir -p /auth
WORKDIR /server

# Install Poetry and the server
RUN pip install --upgrade pip && pip install poetry
COPY pyproject.toml poetry.lock /server/
COPY saltapi /server/saltapi
RUN poetry config virtualenvs.create false
RUN poetry install

# Set up the RS256 key for signing tokens
RUN openssl genrsa -out /auth/rs256_key 4096
RUN openssl rsa -in /auth/rs256_key -pubout > /auth/rs256_key.pub

EXPOSE 8000

# Launch the server
CMD ["uvicorn", "saltapi.app:app", "--host", "0.0.0.0"]
