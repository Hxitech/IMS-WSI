FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
COPY requirements.txt /app/requirements.txt

# If uv.lock exists we use uv, else fallback to pip (dev friendliness)
RUN pip install --no-cache-dir uv || true
# NOTE: avoid bash process substitution (<(...)) because default shell is /bin/sh
RUN if [ -f uv.lock ]; then uv export --format requirements-txt --output-file /tmp/requirements.txt && uv pip install --system -r /tmp/requirements.txt; else pip install --no-cache-dir -r requirements.txt; fi

COPY . /app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
