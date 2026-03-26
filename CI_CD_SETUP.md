# CI/CD Pipeline Setup Guide

## Complete Workflow: Git → Docker → ECR → EC2

This CI/CD pipeline automatically:
1. ✅ Tests and lints your code
2. ✅ Builds Docker image
3. ✅ Pushes to AWS ECR
4. ✅ Deploys to EC2 and runs container

---

## Required GitHub Secrets

Add these secrets to: **Settings → Secrets and variables → Actions**

### 1. AWS Credentials
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION (default: us-east-1)
```

### 2. ECR Configuration
```
ECR_REPOSITORY_NAME     # e.g., student-mlops-app
ECR_REGISTRY_URL        # e.g., 123456789.dkr.ecr.us-east-1.amazonaws.com
```

### 3. EC2 Configuration
```
EC2_HOST                # e.g., ec2-54-123-45-67.compute-1.amazonaws.com
EC2_USER                # e.g., ec2-user or ubuntu
EC2_SSH_KEY             # Private SSH key (paste full key content)
```

---

## Pipeline Stages

### Stage 1: 🧪 Test & Lint (Always Runs)
- Checkout code
- Install dependencies
- Lint with flake8
- Format check with black
- Run pytest

✅ Runs on: **Push to main/develop + Pull requests**

### Stage 2: 🐳 Build Docker Image (After Tests Pass)
- Configure AWS credentials
- Login to ECR
- Build Docker image with SHA tag
- Push to ECR (both specific tag and `latest`)

✅ Runs on: **Push to main/develop** (only after tests pass)

### Stage 3: 🚀 Deploy to EC2 (After Build Succeeds)
- Pull image from ECR on EC2
- Stop old container
- Start new container
- Verify container is running

✅ Runs on: **Push to main branch only**

---

## How to Set Up

### Step 1: Create ECR Repository
```bash
aws ecr create-repository --repository-name student-mlops-app --region us-east-1
```

### Step 2: Get ECR Details
```bash
aws ecr describe-repositories --repository-names student-mlops-app --region us-east-1
```
Copy: `repositoryUri` (this is ECR_REGISTRY_URL)

### Step 3: Create EC2 SSH Key Pair
```bash
aws ec2 create-key-pair --key-name student-mlops-deploy --region us-east-1 --query 'KeyMaterial' --output text > student-mlops-deploy.pem
chmod 400 student-mlops-deploy.pem
```

### Step 4: Add GitHub Secrets
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add all 7 secrets (see above)
3. For `EC2_SSH_KEY`: paste the entire content of `student-mlops-deploy.pem`

### Step 5: Install Docker on EC2
```bash
# SSH into EC2
ssh -i student-mlops-deploy.pem ec2-user@your-ec2-host

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Logout and login again
exit
```

### Step 6: Configure AWS Credentials on EC2
```bash
aws configure
# Enter: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region
```

---

## Workflow Triggers

| Event | Stages Run |
|-------|-----------|
| **Push to main** | Test → Build → Deploy |
| **Push to develop** | Test → Build (no deploy) |
| **Pull Request** | Test only |
| **Manual trigger** (later) | Any stage |

---

## Monitoring Pipeline

### View CI/CD Status
1. Go to: https://github.com/yourusername/repo/actions
2. Click on the latest workflow run
3. See each stage: Test → Build → Deploy

### Check EC2 Container Status
```bash
ssh -i student-mlops-deploy.pem ec2-user@your-ec2-host
docker ps | grep student-mlops-app
docker logs student-mlops-app
```

### Access Running Application
```
http://your-ec2-host:8000/docs
```

---

## Troubleshooting

### Docker Image Not Building
- Check Dockerfile syntax
- Ensure requirements.txt is valid
- Check Docker build logs in GitHub Actions

### ECR Push Failed
- Verify AWS credentials are correct
- Verify ECR repository exists
- Check IAM permissions

### EC2 Deployment Failed
- Verify EC2 security group allows port 8000
- Check SSH key is correct (matches EC2 key pair)
- Verify EC2 has Docker installed
- Check EC2 has AWS IAM role to pull from ECR

### Container Won't Start
```bash
# SSH into EC2 and check logs
ssh -i student-mlops-deploy.pem ec2-user@your-ec2-host
docker logs student-mlops-app
```

---

## Security Best Practices

1. ✅ Never commit `.pem` files to git
2. ✅ Use GitHub Secrets for all credentials
3. ✅ Rotate SSH keys regularly
4. ✅ Use IAM roles instead of access keys (if possible)
5. ✅ Restrict EC2 security group to your IP
6. ✅ Use least privilege IAM policies

---

## Architecture Diagram

```
GitHub Repository
       ↓
[Test & Lint Job]
       ↓
   (if main/develop)
       ↓
[Build Docker Image]
   Build → Tag → Push to ECR
       ↓
   (if main only)
       ↓
[Deploy to EC2]
   Pull from ECR → Stop old → Start new
       ↓
Running Application on EC2:8000
```

---

## Commands to Deploy Manually (if needed)

```bash
# SSH into EC2
ssh -i student-mlops-deploy.pem ec2-user@your-ec2-host

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [ECR_REGISTRY_URL]

# Pull latest image
docker pull [ECR_REGISTRY_URL]/student-mlops-app:latest

# Stop and remove old container
docker stop student-mlops-app 2>/dev/null || true
docker rm student-mlops-app 2>/dev/null || true

# Start new container
docker run -d \
  --name student-mlops-app \
  -p 8000:8000 \
  [ECR_REGISTRY_URL]/student-mlops-app:latest

# Check status
docker ps | grep student-mlops-app
```
