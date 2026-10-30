# syntax=docker/dockerfile:1
ARG DATASET_VERSION=unknown
ARG DATASET_SOURCE=local
ARG DATASET_CHECKSUM=unknown
ARG DATASET_BUILD_DATE
ARG GIT_COMMIT=unknown

FROM python:3.12-slim AS validator

WORKDIR /validate

COPY requirements-validate.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements-validate.txt

COPY schema.json .
COPY data/ ./data/
COPY scripts/validate.py .

RUN python validate.py

FROM python:3.12-slim

ARG DATASET_VERSION
ARG DATASET_SOURCE
ARG DATASET_CHECKSUM
ARG DATASET_BUILD_DATE
ARG GIT_COMMIT

LABEL org.opencontainers.image.created="${DATASET_BUILD_DATE}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.version="${DATASET_VERSION}" \
      org.opencontainers.image.source="${DATASET_SOURCE}" \
      org.opencontainers.image.title="dataset-validator-app" \
      org.opencontainers.image.description="Example app with build-time data validation and lineage" \
      com.example.dataset.version="${DATASET_VERSION}" \
      com.example.dataset.source="${DATASET_SOURCE}" \
      com.example.dataset.checksum="${DATASET_CHECKSUM}" \
      com.example.dataset.schema="schema.json" \
      com.example.dataset.lineage="raw -> schema-validated -> packaged"

WORKDIR /app

RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --shell /sbin/nologin --create-home appuser

COPY --from=validator --chown=appuser:appuser /validate/data ./data

COPY --chown=appuser app.py .

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt


USER appuser

CMD ["python", "app.py"]