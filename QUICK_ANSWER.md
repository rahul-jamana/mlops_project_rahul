# 🎯 Quick Answer: Where New Data Goes & How Retraining Works

## **Simple Answer:**

### **WHERE NEW DATA IS STORED:**
```
1. LOCAL → data/raw/student_scores.csv
2. S3    → s3://mlops-student/data/raw/student_scores.csv
3. BACKUP → S3 keeps old versions automatically
```

### **WHAT HAPPENS TO OLD DATA:**
```
Old Data (27 students)
    ↓
↳ Backed up automatically
    ↓
New Data replaces it (77 students)
    ↓
Old data still in S3 history (versioning)
    ↓
Model trained on NEW data
```

### **HOW RETRAINING WORKS:**

**One Line Summary:**
```
New Data → Upload to S3 → Preprocess → Upload → Retrain → Auto-upload Model
```

**Step by Step:**
```
1. New CSV Data Arrives
   ↓
2. Move to: data/raw/student_scores.csv
   ↓
3. Run: python scripts/upload_raw_data.py
   (Upload to S3)
   ↓
4. Run: python src/data/preprocess.py
   (Process the new data)
   ↓
5. Run: python scripts/upload_processed_data.py
   (Upload processed version to S3)
   ↓
6. Run: python src/model/train.py
   (Train new model, AUTO-uploads to S3)
   ↓
✓ DONE! New model is live in S3
```

### **OR DO IT ALL AT ONCE:**
```bash
python scripts/retrain_pipeline.py
```

---

## **Data Storage Comparison**

| Location | Purpose | Keep How Long | Auto-Delete? |
|----------|---------|---------------|-------------|
| **Local** | Working files | Current only | No backup |
| **S3** | Production + backup | Forever | Keep all versions |
| **Old Model** | Recovery | S3 keeps history | Can restore anytime |

---

## **Real Timeline Example**

```
WEEK 1:
├── Data: 27 students
├── Upload to S3 ✓
└── Model trained ✓

WEEK 2:
├── New: 50 students arrive
├── Total: 77 students
├── Run retrain_pipeline.py
├── New data uploaded to S3 ✓
├── New model trained & uploaded to S3 ✓
└── Old model backed up in S3 ✓

WEEK 3:
├── Data: 77 students (from Week 2)
├── Deploy with latest model ✓
└── Old models still available in S3 for rollback
```

---

## **Three Retraining Scenarios**

### **Scenario A: Weekly Batch Retraining**
```
Monday:   Run python scripts/retrain_pipeline.py
          ↓ All new data from past week processed
Tuesday-Sunday: Use trained model
Next Monday: Repeat
```

### **Scenario B: On-Demand Retraining**
```
New important data arrives
    ↓
Run python scripts/retrain_pipeline.py
    ↓
Immediately get better predictions
```

### **Scenario C: Emergency Model Rollback**
```
New model performs poorly
    ↓
Download old model: python scripts/download_model.py
    ↓
Deploy old model: docker run ...
    ↓
Investigate what went wrong
```

---

## **Key Facts**

✅ **Old data is NEVER deleted** - Always backed up in S3
✅ **Models are VERSIONED** - Can revert to old models
✅ **Process is AUTOMATED** - One command does everything
✅ **Safe for production** - Backups prevent data loss
✅ **Scalable** - Works with any size dataset

---

## **Commands Cheat Sheet**

```bash
# Check what's in S3
python scripts/verify_s3_files.py

# Handle new data
python scripts/handle_new_data.py --mode replace --file new_data.csv

# Complete retraining
python scripts/retrain_pipeline.py

# Upload everything
python scripts/upload_all.py

# Download everything
python scripts/download_all.py

# Train only
python src/model/train.py
```

