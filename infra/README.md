# Trading Simulator Infrastructure (AWS CDK)

This directory contains the AWS infrastructure for the trading simulator,
implemented with **AWS CDK v2 (Python)** and managed with **uv**.

The stack (`SimulatorStack`) provisions:

- VPC (public + private subnets)
- RDS Postgres database
- ElastiCache Redis
- ECS Fargate service for the FastAPI backend (behind an ALB)
- S3 bucket + CloudFront distribution for the Vite React frontend

## Prerequisites

- AWS account and credentials configured locally (e.g. via `aws configure`)
- Node.js and the AWS CDK CLI:

  ```bash
  npm install -g aws-cdk
  ```

- `uv` installed (see the official docs for your platform)

## Setup

From the `infra` directory:

```bash
uv sync
```

This will create a virtual environment and install the dependencies defined in
`pyproject.toml`.

Bootstrap your AWS environment (per account/region) once:

```bash
uv run cdk bootstrap
```

## Build & deploy

1. Build the frontend (from the `frontend` directory):

   ```bash
   npm install     # first time only
   npm run build   # produces ./dist
   ```

2. Deploy the stack (from the `infra` directory):

   ```bash
   uv run cdk deploy SimulatorStack
   ```

   This will:

   - Build and publish the backend Docker image from `../backend`
   - Create / update all AWS resources
   - Upload the built frontend assets to S3 and invalidate CloudFront

The deploy output will include:

- `BackendUrl` – the ALB URL for the FastAPI API
- `FrontendUrl` – the CloudFront URL for the React frontend

## Tear down

When you're done testing or the competition is over, destroy the stack to avoid
charges:

```bash
uv run cdk destroy SimulatorStack
```

This removes all resources defined in `SimulatorStack` (RDS, Redis, ECS, S3,
CloudFront, etc.).


