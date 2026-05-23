#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${DEPLOY_APP_DIR:-/opt/survivor-soul-rpg}"
APP_VERSION="${1:-latest}"
COMPOSE_FILE="${APP_DIR}/docker-compose.prod.yml"

cd "${APP_DIR}"

export APP_VERSION

if [[ -n "${GHCR_TOKEN:-}" ]]; then
  echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USERNAME:-github}" --password-stdin
fi

docker compose -f "${COMPOSE_FILE}" pull
docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

docker image prune -f

echo "Deployed survivor-soul-rpg:${APP_VERSION}"
