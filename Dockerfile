FROM python:3.12-slim

WORKDIR /opt/app

# Install dependencies first so this layer is cached across code changes.
COPY requirements.txt requirements-prod.txt ./
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

EXPOSE 5000

# Run under Gunicorn (production WSGI server), not the Flask dev server.
# `app:app` = the `app` Flask instance in app.py.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--timeout", "120", "app:app"]
