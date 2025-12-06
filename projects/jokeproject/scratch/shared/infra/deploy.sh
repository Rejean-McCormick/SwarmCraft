#!/usr/bin/env bash
set -euo pipefail

# Deploy JokeGen to environment (stage|prod)
ENV=${1:-stage}
if [[ "$ENV" != "stage" && "$ENV" != "prod" ]]; then
  echo "Usage: deploy.sh [stage|prod]"; exit 1
fi

IMAGE_TAG=${IMAGE_TAG:-latest}
REGISTRY=${REGISTRY:-docker.io}
REPO=${REPO:-jokegen}

echo "Deploying JokeGen to $ENV with image tag ${IMAGE_TAG}..."

# Push image (assumes docker login and local tag Jokegen:tag naming)
docker tag jokegen:latest ${REGISTRY}/${REPO}:${IMAGE_TAG}
docker push ${REGISTRY}/${REPO}:${IMAGE_TAG}

# Update Kubernetes/Orchestrator (placeholder: user should fill with actual k8s/helm commands)
if which kubectl >/dev/null 2>&1; then
  kubectl set image deployment/jokegen-deployment jokegen=${REGISTRY}/${REPO}:${IMAGE_TAG} -n jokegen-$ENV
fi

echo "Deployment request submitted."
