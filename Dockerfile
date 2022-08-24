FROM nikolaik/python-nodejs:python3.10-nodejs14-slim

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.0

COPY frontend/src /app/frontend/src
COPY frontend/public /app/frontend/public
COPY frontend/package.json /app/frontend
COPY frontend/package-lock.json /app/frontend
WORKDIR /app/frontend
RUN npm install

COPY backend /app/backend
COPY images /app/images
COPY poetry.lock pyproject.toml entrypoint.sh /app/

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["bash", "entrypoint.sh"]