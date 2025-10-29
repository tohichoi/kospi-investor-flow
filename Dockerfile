FROM python:3.11-slim

WORKDIR /app

# Install system deps required for some Python packages (Excel reading, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

# Copy project
COPY . .

# Expose the port used by Fly / platform
EXPOSE 8050

# Use gunicorn to serve the Flask server exposed by Dash (wsgi.app)
ENV PORT 8050
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8050", "--workers", "1"]
