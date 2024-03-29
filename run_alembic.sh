#!/bin/bash
if [ -n "$1" ]
then
echo "alembic revision --autogenerate -m \"$1\""
alembic revision --autogenerate -m "$1"
exit 0
else
echo "Add message in the first parameter"
exit 1
fi
