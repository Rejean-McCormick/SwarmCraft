# JokeGen CI/CD Pipeline

Overview:
- Build: multi-stage Docker image for JokeGen API
- Test: run unit tests and integration tests
- Deploy: push image to registry and deploy to staging/prod environments using a deployment script

Environment:
- Node.js 18 runtime
- Docker daemon available
- Access to container registry (e.g., Docker Hub or AWS ECR)

Files:
- Dockerfile: multi-stage build
- .github/workflows/jokegen.yml: GitHub Actions workflow (if GitHub is used)
- scripts/deploy.sh: deployment helper for staging/production

Variables (ENV):
- PORT
- BASE_URL
- DATABASE_URL
- AUTH_REQUIRED
- JWT_PUBLIC_KEY
- JWT_ISSUER
- ENABLE_CORS
- CORS_ALLOWED_ORIGINS
- JOKEGEN_LOG_LEVEL
