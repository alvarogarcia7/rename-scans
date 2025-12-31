# Python Boilerplate

## Getting started - Local python

This project uses [uv](https://docs.astral.sh/uv/) for Python package and virtual environment management.

To set up the project:

```bash
# Install uv (if not already installed)
# See https://docs.astral.sh/uv/getting-started/installation/

# uv will automatically create a virtual environment and install dependencies
uv sync
make test
```

## Getting started - Docker

```bash
make up
make bash
# development
make down
```
