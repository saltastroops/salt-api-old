# SALT API

An API for the Southern African Large Telescope (SALT).

## Prerequisites

Python 3.8 or higher is required for running the server.

## Environment variables

The following environment variables need to be defined, preferably in the `.env` file.

Variable name | Description | Example
--- | --- | ----
DATABASE_URL | DSN for the database. | mysql://username:password@my.database.server:3306/my_database
SECRET_TOKEN_KEY | Secret key used for signing the issued JWT tokens. | 57f0c9fa-5a08-40ec-bd28-fcb097711e7e
STORAGE_SERVICE_URL | URL of the storage service. | https://srorage.service

## Running the server for development

Make sure that [poetry](https://python-poetry.org) is installed on your machine and run the following command.

```shell script
poetry install
```

You can then launch the server as follows.

```shell script
poetry run uvicorn saltapi.app:app --reload
```

The `--reload` flag is optional; it ensures that the server is restarted when files change.
