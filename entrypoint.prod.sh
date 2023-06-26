#!/bin/sh


if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do

        sleep 1
        echo "Postgress creating in process..."
     
    done

    echo "PostgreSQL started"

fi

# python manage.py flush --no-input
# python manage.py makemigrations
# python manage.py migrate

exec "$@"