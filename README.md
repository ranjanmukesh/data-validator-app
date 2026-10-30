# Dataset Validator App

Small example project showing:

- Multi-stage Dockerfile
- Build-time data validation (schema + integrity checks)
- Dataset lineage and version tracking via labels
- Non-root user
- Cache mounts
- Reproducible build arguments

## Project layout

```
dataset-validator-app/
├── Dockerfile
├── .dockerignore
├── app.py
├── schema.json
├── requirements.txt
├── requirements-validate.txt
├── data/
│   └── users.json
└── scripts/
    └── validate.py
```

## Build

Compute the checksum of the dataset and pass lineage values as build arguments:

```bash
cd dataset-validator-app

DATASET_CHECKSUM=$(sha256sum data/users.json | awk '{print $1}')

docker build \
  --build-arg DATASET_VERSION="2026.10.27" \
  --build-arg DATASET_SOURCE="local:data/users.json" \
  --build-arg DATASET_CHECKSUM="$DATASET_CHECKSUM" \
  --build-arg DATASET_BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --build-arg GIT_COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo 'local')" \
  -t dataset-validator-app:2026.10.27 \
  .
```

If validation fails (bad schema or data), the build stops.

## Run

```bash
docker run --rm dataset-validator-app:2026.10.27
```

## Inspect lineage metadata

```bash
# Pretty-print all labels
docker inspect --format '{{json .Config.Labels}}' dataset-validator-app:2026.10.27 | jq

# Specific dataset labels
docker inspect --format '{{index .Config.Labels "com.example.dataset.version"}}' dataset-validator-app:2026.10.27
docker inspect --format '{{index .Config.Labels "com.example.dataset.checksum"}}' dataset-validator-app:2026.10.27
docker inspect --format '{{index .Config.Labels "com.example.dataset.lineage"}}' dataset-validator-app:2026.10.27
```

## What this demonstrates

| Practice | Where |
|----------|-------|
| Multi-stage build | Dockerfile stages `validator` and final |
| Build-time validation | `RUN python validate.py` (fails build on error) |
| Schema consistency | `schema.json` + `jsonschema` |
| Integrity checks | Uniqueness + SHA-256 in validation script |
| Dataset version / lineage | `LABEL` instructions driven by `ARG`s |
| Non-root user | `USER appuser` (UID 10001) |
| Cache mounts | `--mount=type=cache` for pip |
| Layer ordering | Dependencies before source where possible |
| Minimal final image | Only validated data + app copied forward |
| Exec-form CMD | Proper signal handling |

## Try breaking it

Edit `data/users.json` (duplicate id, invalid email, missing field) and rebuild. The build should fail in the validator stage.
