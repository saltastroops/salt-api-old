# SALT API

An API for the Southern African Large Telescope (SALT).

## Prerequisites

Python 3.8 or higher is required for running the server.

## Environment variables

The following environment variables need to be defined, preferably in the `.env` file.

Variable name | Description | Example
--- | --- | ----
DATABASE_TIMEZONE | Timezone used by the database | Africa/Johannesburg
DATABASE_URL | DSN for the database. | mysql://username:password@my.database.server:3306/my_database
HS256_SECRET_KEY | Secret key for signing and validating a JWT token using the HS256 algorithm. | 57f0c9fa-5a08-40ec-bd28-fcb097711e7e
RS256_PUBLIC_KEY_FILE | File containing the public key for validating a JWT token using the RS256 algorithm. |
RS256_SECRET_KEY_FILE | File containing the secret key for signing a JWT token using the RS256 algorithm. |
STORAGE_SERVICE_URL | URL of the storage service. | https://srorage.service

You can generate a key pair for the RS256 algorithm by means of the `openssh` command.

```shell script
openssl genrsa -out rs256_key 4096
openssl rsa -in rs256_key -pubout > rs256_key.pub
```

The paths of the generated files `rs256_key` and `rs256_key.pub`must be used as the value of the environment variable `RS256_SECRET_KEY_FILE` and `RS256_PUBLIC_KEY_FILE`, respectively.

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

## Setting up Docker

When running the server with Docker, you should define the environment variables in an `.env` file in the root folder. In addition to the environment variables mentioned above, you need to defining the following variable.

Variable name | Description | Example
PORT | Port on which the server should be listening | 2345

The `RS256_PUBLIC_KEY_FILE` and `RS256_SECRET_KEY_FILE` variables need not be set when using Docker; the container creates its own key pair.
