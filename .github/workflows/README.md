# 🚀 GitHub Actions CI/CD Workflows

This document explains the automated CI/CD pipelines configured for the Student MLOps project using GitHub Actions.

## 📋 Overview

Three main workflows are configured:

1. **CI/CD Pipeline** (`ci-cd.yml`) - Automatic testing and deployment
2. **Manual Retrain & Deploy** (`manual-retrain-deploy.yml`) - Manual model retraining
3. Workflow status notifications via Slack

---

## 🔄 Workflows

### 1. CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- ✅ Push to `main` or `develop` branches
- ✅ Pull requests to `main` or `develop`

**Jobs:**

#### A. Test & Lint
- ✅ Runs on all push and PR events
- Installs dependencies from `requirements.txt`
- Runs code quality checks:
  - **flake8**: Python linting
  - **black**: Code formatting
  - **pytest**: Unit testing
- Uploads coverage reports to Codecov

**Key Steps:**
```bash
# Lint Python code
flake8 app/ src/ scripts/ --max-line-length=127

# Format check
black --check app/ src/ scripts/

# Run tests with coverage
pytest tests/ -v --cov=app --cov=src
```

#### B. Build & Push Docker Image
- ⚙️ Runs **only on successful tests** AND **only on push to main/develop**
- Automatically builds Docker image from `docker/Dockerfile`
- Pushes image to Docker Hub
- Tags with:
  - Branch name (e.g., `main`, `develop`)
  - Git SHA (e.g., `main-abc123def`)
  - `latest` (only for main branch)

**Requires Secrets:**
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub access token

#### C. Deploy to Production
- 🚀 Runs **only on successful build** AND **only on push to main branch**
- Configures AWS credentials
- Deploys container to production environment
- Performs health checks
- Runs smoke tests

**Requires Secrets:**
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (e.g., `us-east-1`)

**Deployment Options:**
Choose one of the options in the `Deploy to Production` step:

**Option 1: SSH to EC2**
```bash
ssh -i $KEY ec2-user@$HOST "docker pull ... && docker run ..."
```
Requires: `EC2_KEY`, `EC2_HOST`

**Option 2: AWS ECS**
```bash
aws ecs update-service --cluster $CLUSTER --service $SERVICE
```
Requires: `ECS_CLUSTER`, `ECS_SERVICE`

**Option 3: Kubernetes (EKS)**
```bash
kubectl set image deployment/mlops-app ...
```
Requires: `EKS_CLUSTER_NAME`

#### D. Notifications
- 📢 Runs after all other jobs (always)
- Sends Slack notification with pipeline status

**Requires Secrets:**
- `SLACK_WEBHOOK`: Slack incoming webhook URL (optional)

---

### 2. Manual Retrain & Deploy (`manual-retrain-deploy.yml`)

**Triggers:**
- 🎯 Manual trigger from GitHub Actions UI (workflow_dispatch)

**Options:**
- **Environment**: `staging` or `production` (default: staging)
- **Retrain Model**: `true` or `false` (default: false)

**Jobs:**

#### A. Retrain (Optional)
- Downloads raw data from S3
- Runs DVC pipeline (`dvc repro`)
- Preprocesses and trains model
- Uploads updated model to S3
- Saves model artifact

**Requires Secrets:**
- All AWS credentials (same as CI/CD)

#### B. Build Docker Image
- Builds and pushes Docker image tagged with environment
- Double tags: `environment` and `environment-sha`

#### C. Deploy to Staging/Production
- Deploys to selected environment
- Runs health checks
- Runs smoke tests (test_api.py)

#### D. Notify
- Sends deployment status to Slack

---

## 🔐 Required Secrets Setup

Add these secrets to your GitHub repository:

1. **Docker Hub**
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Docker Hub Personal Access Token
   - (Generate at: https://hub.docker.com/settings/security)

2. **AWS Credentials**
   - `AWS_ACCESS_KEY_ID`: AWS Access Key
   - `AWS_SECRET_ACCESS_KEY`: AWS Secret Key
   - `AWS_REGION`: AWS Region (e.g., `us-east-1`)

3. **EC2 Deployment** (if using EC2)
   - `EC2_KEY`: EC2 private key content
   - `EC2_HOST_PROD`: Production server DNS/IP
   - `EC2_HOST_STAGING`: Staging server DNS/IP (optional)

4. **ECS Deployment** (if using ECS)
   - `ECS_CLUSTER`: ECS cluster name
   - `ECS_SERVICE`: ECS service name

5. **Kubernetes Deployment** (if using EKS)
   - `EKS_CLUSTER_NAME`: EKS cluster name

6. **Slack Notifications** (optional)
   - `SLACK_WEBHOOK`: Slack incoming webhook URL
   - (Create at: https://api.slack.com/messaging/webhooks)

### How to Add Secrets:

1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Enter secret name and value
4. Click **Add secret**

---

## 📊 Workflow Execution Flow

### On Pull Request:
```
PR Created
    ↓
[Test & Lint] ✓ Linting, formatting, unit tests
    ↓
Result: ✅ Pass or ❌ Fail (blocks merge)
```

### On Push to Develop:
```
Push to develop
    ↓
[Test & Lint] ✓
    ↓
[Build & Push Docker] (only if tests pass)
    ├─ Build image
    └─ Push to Docker Hub (tagged: develop-sha)
    ↓
[Notifications] (Slack message sent)
```

### On Push to Main (Production):
```
Push to main
    ↓
[Test & Lint] ✓
    ↓
[Build & Push Docker] (only if tests pass)
    ├─ Build image
    └─ Push to Docker Hub (tagged: main, main-sha, latest)
    ↓
[Deploy to Production] (only if build succeeds)
    ├─ Pull Docker image
    ├─ Run health checks
    └─ Run smoke tests
    ↓
[Notifications] (Slack message sent)
```

### Manual Retrain:
```
Trigger: Workflow Dispatch with Options
    ↓
[Retrain Model] (optional)
    ├─ Download data from S3
    ├─ Run DVC pipeline
    └─ Upload model to S3
    ↓
[Build Docker Image]
    └─ Tag: environment (staging or production)
    ↓
[Deploy to Environment]
    ├─ Pull Docker image
    ├─ Run health checks
    └─ Run smoke tests
    ↓
[Notifications] (Slack message sent)
```

---

## 🔧 Configuration & Customization

### To Customize Triggers:

Edit `.github/workflows/ci-cd.yml`:
```yaml
on:
  push:
    branches: [ main, develop, staging ]  # Add more branches
  pull_request:
    branches: [ main, develop, staging ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

### To Customize Docker Build:

Edit `.github/workflows/ci-cd.yml` → `docker/build-push-action`:
```yaml
tags: |
  type=ref,event=branch
  type=semver,pattern={{version}}
  type=sha,prefix=latest-
```

### To Enable Different Deployment Methods:

Edit `.github/workflows/ci-cd.yml` → `Deploy to Production` job:

**For EC2:**
```bash
ssh -i ${{ secrets.EC2_KEY }} ec2-user@${{ secrets.EC2_HOST }} \
  "docker pull ... && docker stop mlops-app && docker run ..."
```

**For ECS:**
```bash
aws ecs update-service \
  --cluster ${{ secrets.ECS_CLUSTER }} \
  --service ${{ secrets.ECS_SERVICE }} \
  --force-new-deployment
```

**For Kubernetes:**
```bash
aws eks update-kubeconfig \
  --name ${{ secrets.EKS_CLUSTER_NAME }}
kubectl set image deployment/mlops-app \
  mlops-app=${{ env.REGISTRY }}/...
```

---

## 📝 Debugging Failed Workflows

### View Logs:

1. Go to repository → **Actions** tab
2. Click on the failed workflow run
3. Click on the failed job
4. View the detailed logs

### Common Issues:

**❌ Docker login failed**
- Check `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets
- Verify Docker Hub token has `read:packages` and `write:packages` permissions

**❌ AWS credentials failed**
- Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are correct
- Check IAM user has necessary permissions:
  - `ecs:UpdateService` (for ECS)
  - `ec2:DescribeInstances` (for EC2)
  - `eks:DescribeCluster` (for EKS)

**❌ Tests failed**
- Check the test output in the logs
- Run tests locally: `pytest tests/ -v`
- Ensure `requirements.txt` has all dependencies

**❌ Health check timeout**
- Ensure the API is accessible on port 8000
- Check security groups allow incoming traffic
- Verify environment variables are set correctly in Docker

---

## 🎯 Best Practices

### 1. Use Environment Protection
- Go to **Settings** → **Environments** → Create `production` environment
- Require approval before deployment to production
- Add environment-specific secrets

### 2. Use Secrets Management
- 🚫 Never commit credentials to repository
- Use GitHub Secrets for sensitive data
- Rotate AWS keys regularly

### 3. Monitor Workflows
- Set up Slack notifications for failures
- Tag maintainers on failed deployments
- Review logs regularly

### 4. Keep Docker Images Small
- Use Python 3.9 slim image
- Remove build dependencies from final image
- Use multi-stage builds if needed

### 5. Test Before Production
- Always push to `develop` first
- Use staging environment for testing
- Ensure tests pass before merging to `main`

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Action](https://github.com/docker/build-push-action)
- [AWS Configure Credentials Action](https://github.com/aws-actions/configure-aws-credentials)
- [Slack GitHub Action](https://github.com/slackapi/slack-github-action)

---

## ✅ Checklist for Setup

- [ ] Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets
- [ ] Add AWS credentials secrets
- [ ] Choose deployment method (EC2/ECS/Kubernetes)
- [ ] Add deployment-specific secrets
- [ ] (Optional) Add `SLACK_WEBHOOK` for notifications
- [ ] (Optional) Create `production` environment with approval rules
- [ ] Test workflow by pushing to `develop` branch
- [ ] Verify Docker image is pushed to Docker Hub
- [ ] Test manual retrain workflow from Actions UI
- [ ] Review logs and confirm deployments

---

## 🐛 Troubleshooting Deployments

### Model Not Updated After Retraining
```bash
# Ensure S3 upload is working
python scripts/verify_s3_files.py

# Check AWS credentials
aws s3 ls s3://mlops-student/models/
```

### API Still Using Old Model
- Docker container needs restart
- Check if environment variables are set for S3 access
- Verify S3 bucket permissions

### Health Check Failing
```bash
# Test locally
curl http://localhost:8000/health

# Check Docker logs
docker logs mlops-app
```

---

**Last Updated:** March 2026
