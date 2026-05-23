#!/usr/bin/env bash
# GHCR deploy on a server that pulls images from GitHub Container Registry.
set -euo pipefail

APP_DIR="${DEPLOY_APP_DIR:-/opt/survivor-soul-rpg}"
IMAGE_TAG="${1:-latest}"
COMPOSE_FILE="${APP_DIR}/docker-compose.ghcr.yml"

cd "${APP_DIR}"

export IMAGE_TAG
export PULL_POLICY=always

if [[ -n "${GHCR_TOKEN:-}" ]]; then
  echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USERNAME:-github}" --password-stdin
fi

docker compose -f "${COMPOSE_FILE}" pull
docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

docker image prune -f

echo "Deployed ghcr.io image tag ${IMAGE_TAG}"
