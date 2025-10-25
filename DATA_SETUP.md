# Data Setup Instructions

This repository requires large data files that are not included in version control due to their size.

## Required Files

### 1. Skills Dataset (Required for RAG)
- **File**: `data/skills_exploded (2).csv`
- **Size**: ~46 MB
- **Description**: 3.2M skills database for RAG-based matching
- **Where to get**: Download from your original data source

### 2. Skills Embeddings Cache (Optional - Auto-generated)
- **File**: `skills_embeddings_csv_10000.pkl`
- **Size**: ~45 MB
- **Description**: Cached sentence embeddings for 10,000 skills
- **Note**: This file will be automatically generated on first run if not present (takes ~5-10 seconds)

### 3. Database (Auto-generated)
- **File**: `hiring_platform.db`
- **Description**: SQLite database for platform data
- **Note**: Automatically created on first run by running `python hiring_platform_db.py`

## Setup Steps

1. **Place the skills CSV file**:
   ```bash
   # Create data directory if needed
   mkdir data
   
   # Copy your skills dataset
   # Copy skills_exploded (2).csv to data/
   ```

2. **Initialize the database** (optional - happens automatically):
   ```bash
   python hiring_platform_db.py
   ```

3. **First run will generate embeddings cache**:
   ```bash
   # The first time you run the app, it will create the embeddings cache
   # This takes about 5-10 seconds for 10,000 skills
   streamlit run hiring_platform_app.py
   ```

## Alternative: Run Without RAG

If you don't have the skills dataset, you can disable RAG in `hiring_platform_app.py`:

```python
# Line 23 in hiring_platform_app.py
engine = HiringMatchingEngine(use_rag=False, use_llm=False)
```

This will use only the traditional ATS analysis.
