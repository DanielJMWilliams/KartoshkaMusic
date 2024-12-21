FROM python:alpine3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Set the entrypoint script as executable
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]

CMD gunicorn kmusic.wsgi:application --bind 0.0.0.0:8000

EXPOSE 8000