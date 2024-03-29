#!/bin/bash
echo "Running black formatter"
poetry run black .
echo "Running Flake8 linter"
poetry run flake8 .
echo "Running Pylint linter"
poetry run pylint ticket

