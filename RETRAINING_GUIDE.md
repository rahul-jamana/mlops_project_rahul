# 🔄 Complete Retraining Workflow Guide

## 📊 **Data Flow Architecture**

```
NEW DATA SOURCES
    ├── CSV File Upload
    ├── API Feed
    ├── Database Query
    └── S3 Direct Upload
        ↓
    S3 Raw Data Storage
    (s3://mlops-student/data/raw/)
        ↓
    Local Download
        ↓
    Preprocessing
        ↓
    S3 Processed Storage
    (s3://mlops-student/data/processed/)
        ↓
    Model Training
        ↓
    S3 Model Storage
    (s3://mlops-student/models/model_v1.pkl)
        ↓
    Deploy in Production
```

---

## 🚀 **Scenario: New Student Data Arrives**

### **Week 1: Initial Setup**

**You have:** 27 students in `student_scores.csv`

**Action:**
```bash
# Upload initial data to S3
python scripts/upload_all.py
```

**S3 Contains:**
```
s3://mlops-student/
├── data/
│   ├── raw/
│   │   └── student_scores.csv (27 students)
│   └── processed/
│       └── train.csv (27 records)
└── models/
    └── model_v1.pkl (trained on 27 students)
```

---

### **Week 2: New Students Enroll (50 more students)**

#### **Step 1: Get New Data**

**Option A: Replace All Data**
```
Old: student_scores.csv (27 students)
    → Delete
New: student_scores_updated.csv (77 students total)
    → Upload
```

**Option B: Append New Data**
```
Old: student_scores.csv (27 students)
New: student_scores_new.csv (50 new students)
    → Combine into 77 students
```

#### **Step 2: Handle New Data**

**If REPLACING:** (simplest)
```bash
python scripts/handle_new_data.py --mode replace \
  --file path/to/new_data.csv \
  --output data/raw/student_scores.csv
```

**If APPENDING:** (keeping history)
```bash
python scripts/handle_new_data.py --mode append \
  --file path/to/new_data.csv \
  --output data/raw/student_scores.csv
```

#### **Step 3: Upload New Raw Data to S3**
```bash
python scripts/upload_raw_data.py
```

**S3 Now Contains:**
```
s3://mlops-student/data/raw/
└── student_scores.csv (77 students - UPDATED)
```

#### **Step 4: Preprocess New Data Locally**
```bash
python src/data/preprocess.py
```

**Output:**
```
Local: data/processed/train.csv (77 records)
```

#### **Step 5: Upload Processed Data to S3**
```bash
python scripts/upload_processed_data.py
```

**S3 Now Contains:**
```
s3://mlops-student/data/processed/
└── train.csv (77 records - UPDATED)
```

#### **Step 6: Retrain Model (Auto-uploads)**
```bash
python src/model/train.py
```

**Output:**
```
Local: models/model_v1.pkl (trained on 77 students)
Uploads to S3 automatically
```

**S3 Final State:**
```
s3://mlops-student/
├── data/
│   ├── raw/
│   │   └── student_scores.csv (77 students)
│   └── processed/
│       └── train.csv (77 records)
└── models/
    └── model_v1.pkl (NEW MODEL trained on 77 students)
```

---

## ⚡ **ONE-COMMAND RETRAINING**

Do all steps in one command:

```bash
python scripts/retrain_pipeline.py
```

This automatically:
1. ✅ Uploads raw data to S3
2. ✅ Preprocesses data
3. ✅ Uploads processed data to S3
4. ✅ Retrains model (auto-uploads to S3)
5. ✅ Verifies all files in S3

---

## 📝 **Complete Commands Reference**

### **Scenario 1: First Time Setup**
```bash
# Step 1: Upload everything to S3
python scripts/upload_all.py

# Verify
python scripts/verify_s3_files.py
```

### **Scenario 2: Weekly Retraining with New Data**
```bash
# Step 1: Copy new CSV to data/raw/student_scores.csv
# (Replace old file or keep both)

# Step 2: Handle new data (optional if you manually updated)
python scripts/handle_new_data.py --mode replace --file data/raw/new_data.csv

# Step 3: Run complete pipeline
python scripts/retrain_pipeline.py

# Verify
python scripts/verify_s3_files.py
```

### **Scenario 3: Emergency - Model Failed, Need Old Model**
```bash
# Step 1: Download previous model from S3
python scripts/download_model.py

# Step 2: Restart API server with old model
docker run -p 8000:8000 mlops-app
```

### **Scenario 4: Download Everything from S3 to Local**
```bash
# Download all files
python scripts/download_all.py

# Verify locally
ls -la data/raw/
ls -la data/processed/
ls -la models/
```

---

## 🗂️ **What Gets Stored Where**

### **Local Storage (Your Computer)**
```
C:\ROUGH\student_mlops\
├── data/
│   ├── raw/student_scores.csv (working data)
│   └── processed/train.csv (preprocessed)
└── models/
    └── model_v1.pkl (current model)
```

### **S3 Cloud Storage**
```
s3://mlops-student/
├── data/
│   ├── raw/student_scores.csv (backup + versions)
│   └── processed/train.csv (backup + versions)
└── models/
    └── model_v1.pkl (production model)
```

---

## 🔍 **How Old Data is Replaced**

### **When You Replace Data:**
```
Old student_scores.csv (27 students)
        ↓
Backup created: student_scores.csv.backup_20260325_143000
        ↓
New file replaces old: student_scores.csv (77 students)
        ↓
All downstream processes use NEW data
```

### **When You Append Data:**
```
Old data: [Student 1-27]
New data: [Student 28-77]
        ↓
Combined: [Student 1-77]
        ↓
Duplicates removed
```

---

## 📌 **Key Points**

1. **Old data is backed up** - Never lost
2. **New S3 model replaces old** - Automatic during training
3. **Versioning available** - Check S3 version history
4. **Recovery possible** - Download from S3 backup
5. **Fully automated** - One command does everything

---

## 🎯 **Real-World Example**

**Monday:** 100 students, model trained
**Wednesday:** 20 new students enroll

```bash
# 1. New CSV arrives (120 students)
# 2. Run retraining:
python scripts/retrain_pipeline.py

# 3. Done! New model deployed, old one backed up
```

That's it! Complete, automated, versioned, backed-up retraining!
