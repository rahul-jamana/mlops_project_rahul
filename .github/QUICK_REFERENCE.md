# ⚡ CI/CD Quick Reference

## 🚀 Workflow Files Created

| File | Purpose | Triggers |
|------|---------|----------|
| `.github/workflows/ci-cd.yml` | Main pipeline: test, build, deploy | Push/PR on main, develop |
| `.github/workflows/manual-retrain-deploy.yml` | Manual retrain & deploy | Manual trigger (UI) |
| `.github/workflows/scheduled-tasks.yml` | Daily tasks & checks | Scheduled (2 AM UTC) |
| `.github/SETUP_GUIDE.md` | Detailed setup instructions | Reference |
| `.github/workflows/README.md` | Workflow documentation | Reference |

---

## 📝 Required Secrets

```bash
# Docker Hub
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_hub_token

# AWS
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Deployment (choose one)
# EC2 Option:
EC2_KEY=private_key_content
EC2_HOST_PROD=prod.example.com
EC2_HOST_STAGING=staging.example.com

# ECS Option:
ECS_CLUSTER=your_cluster_name
ECS_SERVICE=your_service_name

# Kubernetes Option:
EKS_CLUSTER_NAME=your_cluster_name

# Optional
SLACK_WEBHOOK=https://hooks.slack.com/services/...
```

---

## 🔧 Common Tasks

### Run CI/CD on PR
```bash
git checkout -b feature-branch
# Make changes
git commit -m "Add feature"
git push -u origin feature-branch
# Create PR on GitHub
```

### Deploy to Main
```bash
git checkout main
git merge feature-branch
git push origin main
# Workflow triggers automatically
```

### Manual Retrain & Deploy
1. Go to **Actions** tab
2. Click **Manual Retrain & Deploy**
3. Click **Run workflow**
4. Select environment & retrain option
5. Monitor progress

### View Workflow Logs
- Go to **Actions** tab
- Click workflow run
- Click job
- View step logs

### Force Re-run
1. Go to **Actions** tab
2. Click failed workflow
3. Click **Re-run failed jobs**

### Rollback Deployment
```bash
# Redeploy previous version
git revert HEAD
git push origin main
```

---

## 🐛 Quick Fixes

### Docker Login Failed
1. Update `DOCKER_PASSWORD` secret
2. Use new token from [Docker Hub](https://hub.docker.com/settings/security)
3. Re-run workflow

### AWS Auth Failed
1. Verify `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`
2. Check IAM user has permissions
3. Re-run workflow

### Tests Failed
```bash
# Run locally to debug
pytest tests/ -v
```

### Health Check Timeout
1. Check API is running: `curl http://ip:8000/health`
2. Check firewall/security group allows port 8000
3. Check Docker logs: `docker logs mlops-app`

### Secrets Not Found
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Verify secret name matches exactly in workflow
3. Add missing secret if needed

---

## 📊 Workflow Status Codes

| Status | Icon | Meaning |
|--------|------|---------|
| Success | ✅ 🟢 | All jobs passed |
| Failure | ❌ 🔴 | One or more jobs failed |
| Skipped | ⚪ | Job was skipped (conditional) |
| Timeout | ⏱️ | Job exceeded time limit |
| Cancelled | ❌ | User cancelled the workflow |

---

## 🎯 Workflow Execution Rules

### CI/CD Pipeline (ci-cd.yml)

**Always runs:**
- Test & Lint (all pushes & PRs)

**Only runs on success + push to main/develop:**
- Build & Push Docker

**Only runs on success + push to main only:**
- Deploy to Production

### Manual Retrain (manual-retrain-deploy.yml)

**Triggered from Actions UI with options:**
- Environment: staging or production
- Retrain: true or false

### Scheduled Tasks (scheduled-tasks.yml)

**Runs on schedule:**
- Code quality: Weekly (Monday 10 AM)
- Daily retrain: Daily (2 AM UTC)
- Dependency check: Every scheduled event
- Security checks: Every scheduled event
- Health check: Every scheduled event

---

## 🔐 Security Settings

### Add Branch Protection (Production)
1. **Settings** → **Branches** → **Add rule**
2. Branch: `main`
3. Require:
   - ✅ PR reviews
   - ✅ Status checks pass
   - ✅ Branches up to date

### Create Production Environment
1. **Settings** → **Environments** → **New**
2. Name: `production`
3. Required reviewers: Select team members
4. Deployment branches: `main` only

---

## 📌 File Locations

```
.github/
├── workflows/
│   ├── ci-cd.yml                    (Main pipeline)
│   ├── manual-retrain-deploy.yml    (Manual retrain)
│   ├── scheduled-tasks.yml          (Scheduled jobs)
│   └── README.md                    (Detailed docs)
└── SETUP_GUIDE.md                   (Setup instructions)
```

---

## 🚦 Typical Deployment Flow

### On PR
```
PR Created
  ↓
Test & Lint ✅
  ↓
Status: Ready to merge
```

### On Merge to Main
```
Push to main
  ↓
Test & Lint ✅
  ↓
Build & Push Docker ✅
  ↓
Deploy to Production ✅
  ↓
Health Check ✅
  ↓
Status: LIVE
```

### Manual Retrain
```
Trigger workflow
  ↓
Retrain (optional)
  ↓
Build
  ↓
Deploy to [staging/prod]
  ↓
Health Check
  ↓
Notify Slack
```

---

## ✅ Setup Checklist

- [ ] Add `DOCKER_USERNAME` & `DOCKER_PASSWORD`
- [ ] Add `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- [ ] Choose deployment method (EC2/ECS/K8s)
- [ ] Add deployment secrets
- [ ] (Optional) Add `SLACK_WEBHOOK`
- [ ] Test PR to develop
- [ ] Test merge to main
- [ ] Verify Docker image in Hub
- [ ] Verify deployment
- [ ] Enable branch protection for main

---

## 📚 Documentation Links

- [Main Documentation](./.github/workflows/README.md)
- [Setup Guide](./.github/SETUP_GUIDE.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Hub Guide](https://docs.docker.com/docker-hub/)

---

## 🆘 Emergency Contacts

- **Workflow Failed?** Check **Actions** → Failed job logs
- **Deployment Issue?** SSH to server & check `docker logs`
- **AWS Issue?** Check CloudWatch logs
- **Docker Issue?** Pull image locally & test: `docker run -it image:tag`

---

**Last Updated:** March 2026  
**Version:** 1.0
