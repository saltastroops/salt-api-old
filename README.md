# SALT API

An API for the Southern African Large Telescope (SALT).

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
