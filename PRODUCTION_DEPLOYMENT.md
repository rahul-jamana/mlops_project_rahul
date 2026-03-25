# 🚀 Production Deployment Workflow

## **Complete Flow: Train → Upload → Deploy**

```
Step 1: New Data Arrives
    ↓
Step 2: Run Retraining
    └── python scripts/retrain_pipeline.py
    ↓
Step 3: Model Auto-uploaded to S3
    └── s3://mlops-student/models/model_v1.pkl
    ↓
Step 4: Restart API Server
    └── docker stop mlops-app
    └── docker run -p 8000:8000 mlops-app
    ↓
Step 5: API Downloads Latest Model from S3
    └── Automatically on startup
    ↓
Step 6: API Uses New Model for Predictions
    └── All requests use NEW model
    ↓
SUCCESS: New model is live!
```

---

## **Workflow in Detail**

### **1. Train & Upload (Automatic)**
```bash
# Run retraining
python scripts/retrain_pipeline.py

# Output:
# - New model trained
# - Automatically uploaded to S3
# - Old model backed up in S3
```

**S3 State After Training:**
```
s3://mlops-student/
├── data/
│   ├── raw/student_scores.csv (NEW)
│   └── processed/train.csv (NEW)
└── models/
    └── model_v1.pkl (NEW - uploaded automatically)
```

---

### **2. Deploy Updated API**

**Stop old container:**
```bash
docker stop mlops-app
```

**Start new container:**
```bash
docker run -p 8000:8000 mlops-app
```

**On Startup, the API:**
```
1. Starts Docker container
2. Loads app.py
3. Executes: load_model()
4. Attempts to download from S3
5. Download successful → Uses NEW model
6. API ready for predictions
```

---

### **3. API Uses New Model**

**Old Way (Manual):**
- Manual update of model file
- Docker restart needed
- API uses local file

**New Way (Automatic via S3):**
- Script uploads to S3
- Docker restart triggers S3 download
- API uses latest model automatically

---

## **Timeline Example**

### **Week 1: Initial Deployment**
```
Monday 9:00 AM
│
├─ Data: 27 students
├─ Train model
├─ Upload to S3
├─ docker run -p 8000:8000 mlops-app
│  └─ API downloads model from S3
├─ API online with model
│
└─ Predictions use Week 1 model
```

### **Week 2: New Students, Retraining**
```
Monday 9:00 AM (Next Week)
│
├─ Data: 77 students (50 new)
├─ python scripts/retrain_pipeline.py
│  ├─ Preprocess
│  ├─ Train
│  └─ Upload to S3 ✓ (NEW MODEL)
├─ docker stop mlops-app (old container)
├─ docker run -p 8000:8000 mlops-app (new container)
│  └─ API downloads NEW model from S3 ✓
├─ API online with new model
│
└─ Predictions use Week 2 model (trained on 77 students)
```

---

## **What Happens Behind the Scenes**

### **API Startup Sequence:**

```python
# app.py startup

print("[INFO] Starting API...")

# 1. Try S3 first
try:
    download_file(S3_BUCKET, MODEL_KEY, MODEL_PATH)
    print("[OK] Latest model downloaded from S3")
except:
    print("[WARNING] S3 download failed, using local file")

# 2. Load model
model = joblib.load(MODEL_PATH)
print("[OK] Model loaded")

# 3. Ready for predictions
print("[OK] API Ready!")

# When request arrives → Use this model
@app.post("/predict")
def predict(hours: float):
    return model.predict(data)  # Uses latest model
```

---

## **Benefits of This Workflow**

| Aspect | Benefit |
|--------|---------|
| **Automation** | No manual model copying needed |
| **Reliability** | S3 backup ensures model safety |
| **Scalability** | Easy to update model for 1 or 100 servers |
| **Versioning** | Old models kept in S3 for rollback |
| **Consistency** | All API instances get same model |

---

## **Complete Command Sequence**

### **To Deploy New Model (One-Time Setup):**

```bash
# 1. Prepare new data
# (Copy new CSV to data/raw/student_scores.csv)

# 2. Retrain and upload
python scripts/retrain_pipeline.py

# 3. Verify upload
python scripts/verify_s3_files.py
# Should show: Model - [OK]

# 4. Restart API (will download new model)
docker stop mlops-app
docker run -p 8000:8000 mlops-app

# 5. Test predictions
curl -X POST "http://localhost:8000/predict?hours=5"
```

### **To Rollback to Old Model:**

```bash
# 1. Stop current API
docker stop mlops-app

# 2. Download old model from S3
# (Check S3 version history, download specific version)

# 3. Restart API
docker run -p 8000:8000 mlops-app
# API will download from S3
```

---

## **Monitoring**

### **Check if API is using latest model:**

```bash
# Test prediction
curl -X POST "http://localhost:8000/predict?hours=5"

# Response should use NEW model
{"score": <new_score>}

# Compare with old model to confirm
```

### **Check API health:**
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "model": "loaded"}
```

---

## **Summary**

✅ **New model in S3** → API downloads it automatically on restart
✅ **No manual file copying** needed
✅ **Safe backup in S3** for all versions
✅ **Quick rollback** if needed
✅ **Fully automated** retraining pipeline

**The workflow is now production-ready!**
