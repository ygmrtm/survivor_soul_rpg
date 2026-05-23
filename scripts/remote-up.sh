#!/usr/bin/env bash
# Run on the server after copying the tar (e.g. ~/uploads/survivor_soul_rpg).
set -euo pipefail

IMAGE_TAG="${1:?Usage: remote-up.sh <tag>   e.g. v1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

TAR="${ROOT}/survivor_soul_rpg_${IMAGE_TAG}.tar"
if [[ ! -f "${TAR}" ]]; then
  TAR="${ROOT}/tar/survivor_soul_rpg_${IMAGE_TAG}.tar"
fi
if [[ ! -f "${TAR}" ]]; then
  echo "Missing image archive: survivor_soul_rpg_${IMAGE_TAG}.tar" >&2
  exit 1
fi

if [[ ! -f app.env ]]; then
  echo "Missing app.env (Notion/Redis secrets). Copy from app.env.example" >&2
  exit 1
fi

echo "Loading ${TAR}..."
docker load -i "${TAR}"

export IMAGE_NAME="${IMAGE_NAME:-survivor_soul_rpg}"
export IMAGE_TAG="${IMAGE_TAG}"
export PULL_POLICY=never

docker compose up -d --remove-orphans

echo "Running ${IMAGE_NAME}:${IMAGE_TAG} on http://localhost:${HOST_PORT:-5001}"
