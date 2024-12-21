#!/bin/sh

# Export environment variables
export DEBUG=${DEBUG:-False}
export ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost}
export DJANGO_SECRET=${DJANGO_SECRET}


# Run collectstatic command
python manage.py collectstatic --noinput --verbosity 3

# Start the application
exec "$@"
