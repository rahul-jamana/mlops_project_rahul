# 🚀 CI/CD Setup Guide

Follow this guide to configure GitHub Actions CI/CD for the Student MLOps project.

## ✅ Prerequisites

- GitHub repository with this project
- Docker Hub account
- AWS account with S3 access
- (Optional) Slack workspace for notifications
- Your choice of deployment target (EC2, ECS, or Kubernetes)

---

## 📝 Step 1: Add GitHub Secrets

### 1.1 Docker Hub Credentials

1. Go to **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

| Secret Name | Value | Where to Find |
|------------|-------|---------------|
| `DOCKER_USERNAME` | Your Docker Hub username | [Hub.docker.com](https://hub.docker.com) account |
| `DOCKER_PASSWORD` | Docker Hub Personal Access Token | Settings → Security → [Create New Token](https://hub.docker.com/settings/security) |

**How to create Docker Hub token:**
1. Go to [Docker Hub Security](https://hub.docker.com/settings/security)
2. Click **New Access Token**
3. Name it `github-actions`
4. Set permissions: `Read & Write`
5. Copy the token and paste in GitHub Secrets

### 1.2 AWS Credentials

1. Create IAM user in AWS (or use existing)
2. Go to **IAM** → **Users** → Select user → **Security credentials**
3. Click **Create access key**
4. Copy the credentials

Add to GitHub Secrets:

| Secret Name | Value |
|------------|-------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key |
| `AWS_REGION` | AWS Region (e.g., `us-east-1`) |

### 1.3 Slack Webhook (Optional)

For deployment notifications:

1. Go to [Slack API](https://api.slack.com/messaging/webhooks)
2. Click **Create New App** → **From scratch**
3. Name: `GitHub Actions` → Select workspace → **Create App**
4. Go to **Incoming Webhooks** → Toggle **On**
5. Click **Add New Webhook to Workspace**
6. Select channel (e.g., `#deployments`)
7. Copy the webhook URL

Add to GitHub Secrets:

| Secret Name | Value |
|------------|-------|
| `SLACK_WEBHOOK` | Your Slack webhook URL |

---

## 🎯 Step 2: Choose Your Deployment Method

Edit `.github/workflows/ci-cd.yml` in the **Deploy to Production** job and **uncomment** one option:

### Option A: AWS EC2 (SSH)

**Add these secrets first:**

| Secret Name | Value | How to Get |
|------------|-------|-----------|
| `EC2_KEY` | EC2 private key (*.pem) content | Download from AWS → Key pairs |
| `EC2_HOST_PROD` | Production server IP/DNS | AWS → EC2 → Instances |
| `EC2_HOST_STAGING` | Staging server IP/DNS | AWS → EC2 → Instances |

**Uncomment this in the workflow:**

```yaml
- name: Deploy to AWS (EC2)
  run: |
    ssh -i ${{ secrets.EC2_KEY }} \
      ec2-user@${{ secrets.EC2_HOST_PROD }} \
      "docker pull $REGISTRY/$USERNAME/$IMAGE:latest && \
       docker stop mlops-app && \
       docker run -d --name mlops-app -p 8000:8000 \
       -e AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }} \
       -e AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }} \
       $REGISTRY/$USERNAME/$IMAGE:latest"
```

### Option B: AWS ECS

**Add these secrets first:**

| Secret Name | Value | How to Get |
|------------|-------|-----------|
| `ECS_CLUSTER` | ECS Cluster name | AWS → ECS → Clusters |
| `ECS_SERVICE` | ECS Service name | AWS → ECS → Services |

**Uncomment this in the workflow:**

```yaml
- name: Deploy to ECS
  run: |
    aws ecs update-service \
      --cluster ${{ secrets.ECS_CLUSTER }} \
      --service ${{ secrets.ECS_SERVICE }} \
      --force-new-deployment
```

### Option C: Kubernetes (EKS)

**Add these secrets first:**

| Secret Name | Value | How to Get |
|------------|-------|-----------|
| `EKS_CLUSTER_NAME` | EKS Cluster name | AWS → EKS → Clusters |

**Uncomment this in the workflow:**

```yaml
- name: Deploy to Kubernetes
  run: |
    aws eks update-kubeconfig \
      --name ${{ secrets.EKS_CLUSTER_NAME }} \
      --region ${{ secrets.AWS_REGION }}
    kubectl set image deployment/mlops-app \
      mlops-app=${{ env.REGISTRY }}/${{ secrets.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:latest \
      -n production
```

---

## 🧪 Step 3: Configure Tests (Optional)

If you have pytest tests, create a `tests/` directory:

```bash
mkdir tests
touch tests/__init__.py
touch tests/test_api.py
```

Example `tests/test_api.py`:

```python
import pytest
from app.app import app

@pytest.fixture
def client():
    return app.test_client()

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200

def test_predict(client):
    response = client.post('/predict', json={'hours': 5.0})
    assert response.status_code == 200
    assert 'predicted_score' in response.json()
```

---

## 🔄 Step 4: Test the Workflows

### A. Test Code Quality (PR)

1. Create a new branch:
   ```bash
   git checkout -b test-ci
   ```

2. Make a small change and commit:
   ```bash
   git add .
   git commit -m "Test CI pipeline"
   git push -u origin test-ci
   ```

3. Create a Pull Request
4. View the workflow run:
   - Go to **GitHub** → **Actions** tab
   - Watch the **CI/CD Pipeline** run

Expected: ✅ **Test & Lint** job completes

### B. Test Build & Deploy (Merge to Main)

1. If tests pass, merge PR to `main`:
   ```bash
   git checkout main
   git merge test-ci
   git push
   ```

2. Watch the workflow:
   - **Test & Lint** → ✅ Pass
   - **Build & Push Docker** → ✅ Docker image pushed to Hub
   - **Deploy to Production** → ✅ Deployment script runs

3. Verify Docker image:
   ```bash
   docker pull your-username/student-mlops-app:latest
   docker images
   ```

### C. Test Manual Retrain

1. Go to **GitHub** → **Actions**
2. Click **Manual Retrain & Deploy** workflow
3. Click **Run workflow**
4. Select:
   - Environment: `staging` or `production`
   - Retrain Model: `true`
5. Click **Run workflow**

Watch the job execute:
- **Retrain** → Downloads data, trains model, uploads to S3
- **Build** → Builds Docker image
- **Deploy** → Deploys to selected environment

---

## 📊 Monitor Workflows

### View Workflow Runs

1. Go to **GitHub** → **Actions** tab
2. Click on any workflow run to see details
3. Click on a job to see step-by-step output

### Common Workflow Statuses

| Status | Meaning | Action |
|--------|---------|--------|
| 🟢 ✅ Success | All jobs passed | Nothing needed |
| 🔴 ❌ Failure | One or more jobs failed | Check logs, fix issue, re-run |
| 🟡 ⏳ Queued | Waiting to run | Wait or manually trigger |
| 🟣 🔄 In Progress | Currently running | Wait for completion |
| 🟠 ⚪ Skipped | Job was skipped | Check conditional logic |

### Debug Failed Jobs

1. Click on the **failed job**
2. Look for red ❌ step
3. Click the step to expand and see error logs
4. Common errors:
   - **Docker login failed** → Check `DOCKER_USERNAME`/`DOCKER_PASSWORD`
   - **AWS auth failed** → Check AWS credentials
   - **Tests failed** → Check test output, run locally

---

## 🛠️ Troubleshooting

### Docker Image Not Pushing

**Error:** `Error response from daemon: unauthorized`

**Fix:**
1. Verify `DOCKER_USERNAME` is correct
2. Create new token at [Docker Hub Security](https://hub.docker.com/settings/security)
3. Update `DOCKER_PASSWORD` secret with new token
4. Re-run workflow

### Deployment Fails

**Error:** `Timeout waiting for API`

**Fix:**
1. Check if API is running: `curl http://ip:8000/health`
2. Check Docker logs: `docker logs mlops-app`
3. Verify security group allows port 8000
4. Check environment variables in Docker

### Tests Failing

**Error:** `pytest: command not found` or test failures

**Fix:**
1. Ensure `requirements.txt` includes `pytest`
2. Test locally first:
   ```bash
   pip install -r requirements.txt
   pytest tests/ -v
   ```
3. Check workflow logs for specific test failures

### Model Not Updating

**Error:** API still using old model after retraining

**Fix:**
1. Verify S3 upload succeeded:
   ```bash
   python scripts/verify_s3_files.py
   ```
2. Ensure Docker restart happens after deployment
3. Check S3 bucket permissions for user/service

---

## 📋 Checklist: Ready for Production?

- [ ] All secrets added to GitHub
- [ ] Docker Hub credentials working
- [ ] AWS credentials configured
- [ ] Deployment method chosen (EC2/ECS/K8s)
- [ ] Tests passing locally
- [ ] Workflow triggered successfully on PR
- [ ] Docker image pushed to Hub successfully
- [ ] Deployment script tested
- [ ] Health checks passing
- [ ] Slack notifications working (optional)
- [ ] Production environment protection enabled (optional)

---

## 🚨 Production Best Practices

### 1. Enable Branch Protection

1. Go to **Settings** → **Branches**
2. Under **Branch protection rules**, click **Add rule**
3. Apply to branch: `main`
4. Check:
   - ✅ Require PR reviews before merging
   - ✅ Dismiss stale PRs
   - ✅ Require status checks to pass (select CI/CD Pipeline)
   - ✅ Require branches to be up to date

### 2. Create Production Environment

1. Go to **Settings** → **Environments**
2. Click **New environment** → Name: `production`
3. Add:
   - Required reviewers: Your team members
   - Deployment branches: `main` only
   - Environment secrets (optional): Add production-specific secrets

### 3. Monitor Deployments

1. Go to **Deployments** tab
2. Click on a deployment to see:
   - Status (success/failure)
   - Logs
   - Time deployed

### 4. Secure Secrets

- 🚫 Never commit `.env` files
- 🔄 Rotate AWS keys every 90 days
- 🔐 Use IAM roles instead of long-term keys
- 📋 Audit secret access in CloudTrail

---

## 📚 Next Steps

1. **[Read Detailed Workflow Guide](./.github/workflows/README.md)**
2. **[Set up DVC for Model Versioning](https://dvc.org/doc)**
3. **[Configure Monitoring & Alerts](../PRODUCTION_DEPLOYMENT.md)**
4. **[Set up Auto-Scaling](https://docs.aws.amazon.com/autoscaling/)**

---

## ❓ FAQ

**Q: Can I deploy multiple environments?**  
A: Yes! Use the manual retrain workflow to deploy to `staging` or `production`.

**Q: How do I roll back a deployment?**  
A: Redeploy a previous Docker image tag or revert the commit and push.

**Q: Can I skip deployment for certain commits?**  
A: Yes, add `[skip ci]` in commit message: `git commit -m "Minor fix [skip ci]"`

**Q: What if I don't want to use Docker?**  
A: Modify the build job to deploy using other methods (direct Python, zip file, etc.)

**Q: How often does scheduled retraining run?**  
A: Check `.github/workflows/scheduled-tasks.yml` for cron schedule.

---

**Questions?** Check the logs in the **Actions** tab or consult GitHub Actions documentation.

**Last Updated:** March 2026
