#!/usr/bin/env bash
# Build locally, ship tar + compose to server, load and start (no GHCR).
# Reuses one SSH connection (single password prompt). Use ssh-copy-id for no prompts.
set -euo pipefail

IMAGE_TAG="${1:?Usage: publish-offline.sh <tag>   e.g. v1}"
REMOTE="${DEPLOY_REMOTE:-yg@lenovo}"
REMOTE_DIR="${DEPLOY_DIR:-~/uploads/survivor_soul_rpg}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

IMAGE_NAME="survivor_soul_rpg"
TAR_DIR="${ROOT}/tar"
TAR="${TAR_DIR}/survivor_soul_rpg_${IMAGE_TAG}.tar"

CONTROL_DIR="${TMPDIR:-/tmp}/survivor-deploy-$$"
mkdir -p "${CONTROL_DIR}"
CONTROL_SOCK="${CONTROL_DIR}/master"
SSH_MASTER=(-o ControlMaster=yes -o "ControlPath=${CONTROL_SOCK}" -o ControlPersist=120)
SSH_SLAVE=(-o ControlMaster=no -o "ControlPath=${CONTROL_SOCK}")

cleanup() {
  ssh -O exit "${SSH_SLAVE[@]}" "${REMOTE}" 2>/dev/null || true
  rm -rf "${CONTROL_DIR}"
}
trap cleanup EXIT

mkdir -p "${TAR_DIR}"

echo "Building ${IMAGE_NAME}:${IMAGE_TAG}..."
docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

echo "Saving ${TAR}..."
docker save -o "${TAR}" "${IMAGE_NAME}:${IMAGE_TAG}"

echo "Connecting to ${REMOTE} (one password if keys are not set up)..."
ssh "${SSH_MASTER[@]}" -fN "${REMOTE}"

ssh "${SSH_SLAVE[@]}" "${REMOTE}" "mkdir -p ${REMOTE_DIR}/scripts"

echo "Uploading to ${REMOTE}:${REMOTE_DIR}..."
scp "${SSH_SLAVE[@]}" \
  "${TAR}" docker-compose.yml .env.example app.env.example \
  "${REMOTE}:${REMOTE_DIR}/"

scp "${SSH_SLAVE[@]}" \
  scripts/remote-up.sh "${REMOTE}:${REMOTE_DIR}/scripts/remote-up.sh"

if [[ -f app.env ]]; then
  scp "${SSH_SLAVE[@]}" app.env "${REMOTE}:${REMOTE_DIR}/app.env"
else
  echo "Note: app.env not found locally; ensure it exists on the server."
fi

if [[ -f .env ]]; then
  scp "${SSH_SLAVE[@]}" .env "${REMOTE}:${REMOTE_DIR}/.env"
elif ! ssh "${SSH_SLAVE[@]}" "${REMOTE}" "test -f ${REMOTE_DIR}/.env"; then
  scp "${SSH_SLAVE[@]}" .env.example "${REMOTE}:${REMOTE_DIR}/.env"
fi

ssh "${SSH_SLAVE[@]}" "${REMOTE}" \
  "chmod +x ${REMOTE_DIR}/scripts/remote-up.sh && ${REMOTE_DIR}/scripts/remote-up.sh ${IMAGE_TAG}"

echo "Done. App should be on http://<server>:5001 (or your HOST_PORT in .env)."
