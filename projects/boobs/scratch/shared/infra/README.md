CI/CD, Deployment Infrastructure for the Imagination Catalog

Overview
- Terraform-based infrastructure to host the imagination catalog on AWS (ECS/Fargate) with a minimal ECS cluster, task definition, and service. Backend uses S3 for state storage.
- CI/CD pipeline is wired via GitHub Actions for automated plan/apply on push to main and a separate plan step on PRs.

Project structure
- scratch/shared/infra/terraform/main.tf
  - Terraform root configuration with AWS provider, ECS cluster, task definition, and ECS service.
- scratch/shared/infra/terraform/modules/iam.tf
  - IAM roles and policies for ECS task execution.
- scratch/shared/infra/ci/.github_workflows_cd.yml
  - GitHub Actions workflow to run Terraform init/plan/apply on push to main.
- scratch/shared/infra/ (credentials and secrets are not stored here)

Prerequisites
- AWS account with permission to create ECS resources, IAM roles, and S3 backend.
- Terraform 1.4+ installed for local bootstrap (or rely on GH Actions runner).
- For CI: GitHub repository secrets configured:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_REGION (e.g., us-east-1)
  - TF_BACKEND_S3_BUCKET (optional if you override backend config externally)

Backend configuration
- Terraform backend configured to use S3 bucket: imaginary-catalog-terraform-state in us-east-1.
- Ensure the bucket exists or create it prior to running terraform init locally.
- Optional: configure a DynamoDB table for state locking (not defined in the current main.tf by default).

Initialization, planning and deployment (local)
1) Ensure backend bucket exists:
   - aws s3 mb s3://imaginary-catalog-terraform-state --region us-east-1
   - (Optional) Create a DynamoDB table for locking if desired.
2) Init:
   - terraform init
3) Plan:
   - terraform plan
4) Apply:
   - terraform apply -auto-approve

CI/CD workflow (GitHub Actions)
- Trigger: push to main, PRs to main
- Actions: Checkout -> Setup Terraform -> terraform init -> terraform plan -> terraform apply (on main)
- Secrets: AWS credentials and region as described in prerequisites

Environment and deployment strategy
- Environments: dev/staging/prod can be modeled via separate Terraform workspaces or separate backend configurations and variable overrides.
- For production, configure a stable container image source (e.g., ECR) and update the ECS task definition to use the production image tag.
- After infrastructure is ready, wire the catalog container image (not embedded here) with image pulling from ECR or a registry.

Security considerations
- Do not store credentials in code repositories.
- Use GitHub Secrets for AWS credentials and prefer role-based access if feasible.
- Apply least privilege in IAM policies to ECS tasks and related resources.

Observability and maintenance
- CloudWatch logs for ECS containers; monitor metrics for CPU/memory, container health.
- Maintain a changelog for infrastructure changes and ensure a proper review process.

Limitations and next steps
- The provided Terraform scripts include placeholder subnets and security groups. Update with real VPC, subnets, and SG IDs in your environment or import existing resources.
- Add a proper VPC module and network configuration for a production-grade deployment.
- Extend CI to include terraform destroy for cleanup in non-prod environments.

Usage note
- This README is intended as a living document. Update as infrastructure changes evolve.
