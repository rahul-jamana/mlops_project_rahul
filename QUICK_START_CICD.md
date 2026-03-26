# 🚀 CI/CD Pipeline - Quick Start Checklist

## What's Been Set Up
✅ Complete CI/CD pipeline with 3 stages:
1. **TEST & LINT** - Runs tests, flake8, black
2. **BUILD DOCKER** - Builds Docker image, pushes to ECR
3. **DEPLOY TO EC2** - Pulls from ECR, runs container on EC2

---

## What You Need to Do (7 Steps)

### Step 1: Create AWS ECR Repository
```bash
aws ecr create-repository \
  --repository-name student-mlops-app \
  --region us-east-1
```

### Step 2: Get ECR Registry URL
```bash
aws ecr describe-repositories \
  --repository-names student-mlops-app \
  --region us-east-1 \
  --query 'repositories[0].repositoryUri' \
  --output text
```
Copy this value - you'll need it.

### Step 3: Create EC2 Key Pair
```bash
aws ec2 create-key-pair \
  --key-name student-mlops-deploy \
  --region us-east-1 \
  --query 'KeyMaterial' \
  --output text > student-mlops-deploy.pem

chmod 400 student-mlops-deploy.pem
```

### Step 4: Launch EC2 Instance
- AMI: Ubuntu 22.04 LTS (or Amazon Linux 2)
- Instance Type: t2.micro (free tier) or t2.small
- Security Group: Allow port 8000 and 22 (SSH)
- Key Pair: student-mlops-deploy

Get the public IP address.

### Step 5: Install Docker on EC2
```bash
# SSH into EC2
ssh -i student-mlops-deploy.pem ubuntu@your-ec2-ip

# Install Docker (Ubuntu)
sudo apt update && sudo apt install docker.io -y
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Configure AWS credentials
aws configure
# Enter: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region

# Logout then login again
exit
```

### Step 6: Add GitHub Secrets
Go to: **GitHub → Your Repo → Settings → Secrets and variables → Actions**

Click "New repository secret" and add these 7 secrets:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
| `AWS_REGION` | `us-east-1` |
| `ECR_REPOSITORY_NAME` | `student-mlops-app` |
| `ECR_REGISTRY_URL` | From Step 2 (without the image name) |
| `EC2_HOST` | Your EC2 public IP or hostname |
| `EC2_USER` | `ubuntu` (or `ec2-user` for Amazon Linux) |
| `EC2_SSH_KEY` | Contents of `student-mlops-deploy.pem` file |

### Step 7: Test the Pipeline
```bash
# Push a commit to main
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```

Go to: **GitHub → Your Repo → Actions** and watch it run!

---

## What Happens When You Push to Main

```
1. Tests & Linting ✅ (2-3 minutes)
   ↓
2. Build Docker Image ✅ (3-5 minutes)
   ↓
3. Push to ECR ✅ (1-2 minutes)
   ↓
4. Deploy to EC2 ✅ (1-2 minutes)
   ↓
5. Application Running! 🎉
```

Your app will be accessible at: `http://your-ec2-ip:8000/docs`

---

## Monitoring & Testing

### View Pipeline Status
https://github.com/yourusername/mlops_project_rahul/actions

### SSH into EC2 and Check Container
```bash
ssh -i student-mlops-deploy.pem ubuntu@your-ec2-ip
docker ps
docker logs student-mlops-app
```

### Access Your Application
```
API Docs: http://your-ec2-ip:8000/docs
Health Check: http://your-ec2-ip:8000/health
```

---

## Troubleshooting Quick Fixes

### Docker build fails
→ Check Dockerfile syntax and requirements.txt

### ECR push fails
→ Verify AWS credentials in GitHub Secrets

### EC2 deployment fails
→ Check EC2 has Docker installed and AWS configured

### Container won't start
→ SSH to EC2 and check: `docker logs student-mlops-app`

### Port 8000 not accessible
→ Check EC2 Security Group allows inbound on 8000

---

## File Structure
```
.github/
  └── workflows/
      └── test.yml              ← Your CI/CD pipeline
CI_CD_SETUP.md                 ← Detailed setup guide
student-mlops-deploy.pem       ← SSH key (DO NOT COMMIT!)
```

---

## Next Steps (Optional Enhancements)

- [ ] Add environment variables in GitHub Secrets
- [ ] Setup CloudWatch monitoring
- [ ] Configure Docker health checks
- [ ] Add RDS database for persistence
- [ ] Setup load balancer for multiple EC2 instances
- [ ] Configure auto-scaling group
- [ ] Add Slack notifications on deployment

---

## 🎯 You're Done!

Your CI/CD pipeline is ready. Every push to `main` will:
1. Run tests ✅
2. Build Docker image ✅
3. Push to ECR ✅
4. Deploy to EC2 ✅
5. Run your application ✅

**Good luck! 🚀**
