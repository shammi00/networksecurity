FROM python:3.10-slim-buster

WORKDIR /app

RUN apt update  && apt install curl awscli -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# the health check
# It checks the endpoint defined in the app.py every 30 seconds
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "app.py"]