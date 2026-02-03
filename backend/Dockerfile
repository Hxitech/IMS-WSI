FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# If uv.lock exists we use uv, else fallback to pip (dev friendliness)
RUN pip install --no-cache-dir uv || true
RUN if [ -f uv.lock ]; then uv pip install --system -r <(uv export --format requirements-txt); else pip install --no-cache-dir -e .; fi

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
