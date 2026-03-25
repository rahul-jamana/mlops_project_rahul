# AWS S3 Setup Guide

## 🔧 Prerequisites
- AWS Account
- S3 Bucket created (default: `mlops-student`)
- AWS Access Key ID and Secret Access Key

## 📋 Step-by-Step Setup

### 1. Create AWS Credentials

**Option A: Using AWS Console**
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **IAM** → **Users**
3. Click **Add Users** and create a user with `AmazonS3FullAccess` policy
4. Generate **Access Key ID** and **Secret Access Key**

**Option B: Using Existing Credentials**
- If you already have credentials, skip to Step 2

### 2. Configure AWS Credentials Locally

Run this command:
```bash
aws configure
```

When prompted, enter:
```
AWS Access Key ID: <your-access-key>
AWS Secret Access Key: <your-secret-key>
Default region: us-east-1
Default output format: json
```

This creates `~/.aws/credentials` file automatically.

### 3. Verify AWS Setup

Test your connection:
```bash
python -c "import boto3; s3 = boto3.client('s3'); print('✓ AWS configured successfully')"
```

### 4. Update S3 Configuration

Edit `src/utils/s3_config.py` and change the bucket name if needed:
```python
S3_BUCKET = os.getenv("S3_BUCKET", "your-bucket-name")
```

Or set environment variable:
```bash
set S3_BUCKET=your-bucket-name
# or on Linux/Mac:
export S3_BUCKET=your-bucket-name
```

## 📤 Upload Commands

### Upload Raw Data
```bash
python scripts/upload_raw_data.py
```

### Upload Processed Data
```bash
python scripts/upload_processed_data.py
```

### Upload Model (happens automatically during training)
```bash
python src/model/train.py
```

### Upload Everything at Once
```bash
python scripts/upload_all.py
```

## 📥 Download Commands

### Download Raw Data
```bash
python scripts/download_raw_data.py
```

### Download Processed Data
```bash
python scripts/download_processed_data.py
```

### Download Model
```bash
python scripts/download_model.py
```

### Download Everything
```bash
python scripts/download_all.py
```

## 🔄 Workflow: Upload → Process → Deploy

### Complete Pipeline
```bash
# 1. Upload raw data to S3
python scripts/upload_raw_data.py

# 2. Run preprocessing and training
dvc repro

# 3. Model is automatically uploaded to S3 (during training)

# 4. Deploy with Docker
docker run -p 8000:8000 mlops-app
```

### Recovery: Download from S3 → Re-train
```bash
# 1. Download from S3
python scripts/download_raw_data.py
python scripts/download_processed_data.py

# 2. Re-train the model (uploads to S3)
python src/model/train.py

# 3. Check S3 for updated model
# The updated model is now in S3 bucket
```

## 📊 S3 File Structure

Your S3 bucket will have this structure:
```
mlops-student/
├── data/
│   ├── raw/
│   │   └── student_scores.csv
│   └── processed/
│       └── train.csv
└── models/
    └── model_v1.pkl
```

## 🧪 Test S3 Connection

```bash
python -c "
from src.utils.s3_utils import get_s3_client
s3 = get_s3_client()
response = s3.list_buckets()
print('Available buckets:')
for bucket in response['Buckets']:
    print(f'  - {bucket[\"Name\"]}')
"
```

## ❌ Troubleshooting

### Error: "Unable to locate credentials"
- Run `aws configure` again
- Check if `~/.aws/credentials` exists

### Error: "Access Denied"
- Verify IAM user has `s3:*` permissions
- Check bucket name spelling

### Error: "Bucket doesn't exist"
- Create S3 bucket in AWS Console
- Update `S3_BUCKET` in `src/utils/s3_config.py`

## 🔐 Security Notes

- ✅ Never commit `.aws/credentials` to git
- ✅ Use environment variables for sensitive data
- ✅ Rotate access keys regularly
- ✅ Use IAM roles in production (not access keys)
