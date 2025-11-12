# 📋 Task Structure Updates Based on Data Analysis

**Date:** November 12, 2025  
**Reason:** Analysis revealed that each FCS file contains ~339K events with 26 parameters = ~8.8M data points per file

---

## 🔍 Key Discovery

### **What We Learned:**
- **1 FCS file** = 1 sample = **~339,392 events** (individual particle measurements)
- **Each event** = 26 parameters measured
- **1 FCS file** = ~8.8 million data points (339K × 26)
- **70 FCS files** = ~23.7 million events = **~615 million data points**
- **Sample file** (`test.csv`) = 55.42 MB for just ONE FCS file's event data

### **Production Scale Impact:**
If production generates 100 samples/week:
- **100 files/week** = ~33.9 million events
- **5,200 files/year** = ~1.76 BILLION events
- **Data volume**: ~5.5 GB/week just for event data

---

## ✅ Required Task Updates

### **1. Task 1.1: Enhanced FCS Parser - CRITICAL UPDATES NEEDED**

#### **NEW REQUIREMENTS TO ADD:**

**A. Memory Management (CRITICAL)**
```
Problem: Cannot load 339K events × 26 params × multiple files into memory at once
Solution: Implement chunked processing and streaming
```

**Updates needed:**
- ✅ **Chunked Reading**: Process files in chunks (e.g., 50,000 events at a time)
- ✅ **Streaming Writing**: Write to disk incrementally, not all at once
- ✅ **Memory Monitoring**: Track RAM usage, warn if exceeding threshold
- ✅ **Garbage Collection**: Explicitly clear memory after processing each file

**Code Pattern to Implement:**
```python
# Instead of loading entire file:
# data = fcsparser.parse(file)  # Loads all 339K events!

# Use chunked processing:
for chunk in read_fcs_chunks(file, chunk_size=50000):
    process_chunk(chunk)
    write_chunk_to_parquet(chunk)
    del chunk  # Explicit memory cleanup
```

---

**B. Data Format Optimization (HIGH PRIORITY)**

**Current Problem:**
- CSV format is inefficient for 339K rows
- `test.csv` = 55 MB for ONE file
- 70 files = ~3.85 GB in CSV format
- Slow to read/write

**Required Changes:**

| Aspect | Current (CSV) | Required (Parquet/HDF5) | Benefit |
|--------|---------------|-------------------------|---------|
| File size | 55 MB | ~10-15 MB | 70-80% compression |
| Read speed | Slow | 5-10x faster | Better performance |
| Memory usage | High | Low (lazy loading) | Scalability |
| Type safety | No (strings) | Yes (typed columns) | Data integrity |

**Action Items:**
1. **Primary format**: Apache Parquet (columnar, compressed)
2. **Fallback**: HDF5 for very large files
3. **Export option**: CSV only for small subsets/reports
4. **Add library**: `pyarrow` or `fastparquet`

**Updated Output Structure:**
```
processed_data/
├── fcs/
│   ├── events/                    # Individual event data
│   │   ├── sample_001.parquet     # ← Use Parquet instead of CSV
│   │   ├── sample_002.parquet
│   │   └── ...
│   ├── metadata/
│   │   └── all_metadata.csv       # Metadata is small, CSV is fine
│   └── summary/
│       └── statistics.csv         # Summary stats, not raw events
```

---

**C. Statistical Pre-Processing (NEW ADDITION)**

**Why:** Don't analyze 339K events every time - pre-calculate summaries!

**Add to Task 1.1:**

**Event-Level Statistics to Calculate During Parsing:**
```python
For each FCS file, calculate and save:
1. Total event count
2. Per-parameter statistics:
   - Mean, Median, Std Dev
   - Min, Max, Quartiles (Q1, Q3)
   - Mode (for categorical-like data)
3. Gating statistics:
   - Events in FSC/SSC gate (debris removal)
   - Positive events per marker (CD81+, CD9+)
   - Percentage positive
4. Data quality metrics:
   - Acquisition time
   - Events per second
   - CV (coefficient of variation)
   - Anomaly flags (unusual distributions)
```

**Benefit:** 
- Most analyses don't need raw 339K events
- Use pre-calculated summaries (fast)
- Only go to raw events for detailed plots

**New Deliverable:**
- `event_statistics.csv` - One row per file with all summary stats
- Size: ~70 rows × 100 columns = tiny (~50 KB vs 3.85 GB raw data!)

---

**D. Data Validation (ENHANCED)**

**Add validation checks for each file:**

```python
Quality Checks:
1. Event count validation:
   ✓ Minimum: >1,000 events (too few = unreliable)
   ✓ Maximum: <10 million events (sanity check)
   ✓ Warning if <10,000 events
   
2. Parameter validation:
   ✓ All 26 parameters present
   ✓ No entirely NaN columns
   ✓ FSC/SSC values in reasonable range
   
3. Metadata validation:
   ✓ Sample name extracted correctly
   ✓ Date/time stamp present
   ✓ Machine ID matches expected
   
4. Data integrity:
   ✓ No corruption (file size matches event count)
   ✓ Time parameter is monotonic increasing
   ✓ No duplicate events (check Time parameter)
```

**Output:**
- `data_quality_report.csv` - Pass/Warn/Fail for each file
- Auto-flag problematic files for manual review

---

### **2. Task 2.1: Statistical Analysis Engine - UPDATES**

**NEW CONSIDERATIONS:**

**A. Two-Level Analysis Architecture**

Since we now know files have 339K events each, design analysis in two levels:

**Level 1: Summary Statistics (Fast - use pre-calculated)**
```python
# Analyze pre-calculated statistics
summary_df = pd.read_csv('event_statistics.csv')  # 70 rows, instant
compare_groups(summary_df, group_by='antibody_type')
# Fast! No need to load 23 million events
```

**Level 2: Event-Level Analysis (Slow - only when needed)**
```python
# Only load raw events for detailed analysis
for sample in selected_samples:
    events = pd.read_parquet(f'events/{sample}.parquet')  # 339K rows
    plot_scatter(events, x='FSC-H', y='SSC-H')
    # Slower, but necessary for plots
```

**Update Task 2.1 to specify:**
- Default: Use summary statistics
- Optional: Event-level analysis with progress bar
- User choice: "Quick analysis" vs "Detailed analysis"

---

**B. Downsampling Strategy**

**Problem:** Can't plot 339K points (browser crashes, slow rendering)

**Solution:** Smart downsampling for visualizations

**Add to Task 2.2 (Visualization):**

```python
Visualization Strategies:
1. Scatter plots:
   - Downsample to 10,000 events max (random sampling)
   - Or use density plots (hexbin, 2D histogram)
   
2. Histograms:
   - Use binning (already aggregated)
   - No downsampling needed
   
3. Heatmaps:
   - Use summary statistics (mean, median per sample)
   - No raw events needed
   
4. Interactive plots:
   - Show downsampled points by default
   - "Show all events" option for export/detailed view
```

---

### **3. Task 3.1: ML Quality Control - UPDATES**

**NEW FEATURE ENGINEERING:**

**Original Plan:** Use summary statistics as features

**Enhanced Plan:** Add event distribution features

**Feature Categories:**

**A. Summary Features (from pre-calculated stats):**
```python
- Mean FSC-H, SSC-H, FL channels (26 features)
- Median FSC-H, SSC-H, FL channels (26 features)
- Std Dev for all parameters (26 features)
- CV (coefficient of variation) (26 features)
Total: ~100 summary features
```

**B. Distribution Features (NEW - calculate during parsing):**
```python
- Skewness of each parameter (26 features)
- Kurtosis of each parameter (26 features)
- Percentage in each quartile (26 × 4 = 104 features)
- Mode frequency (26 features)
Total: ~180 distribution features
```

**C. Gating Features (NEW):**
```python
- % events in debris gate
- % events in EV gate (FSC/SSC optimized range)
- % positive for each marker (CD81, CD9, etc.)
- Ratio positive/total
Total: ~10-20 gating features
```

**Total Features:** ~300 features per sample (no need for raw 339K events!)

**Benefit:** 
- ML model trains on 70 samples × 300 features = 21,000 data points
- Fast training, no memory issues
- Still captures full distribution information

---

### **4. Task 4.2: Web Dashboard - UPDATES**

**NEW REQUIREMENTS:**

**A. Data Loading Strategy**

**Problem:** Cannot send 55 MB CSV files to browser!

**Solution:** Server-side aggregation, client receives summaries

**Architecture:**
```
User clicks "View Sample" 
  ↓
Backend loads full 339K events (server-side)
  ↓
Backend calculates plot data (downsampled/aggregated)
  ↓
Send ~10KB JSON to frontend (not 55MB!)
  ↓
Frontend renders plot
```

**Implementation:**
```python
# Backend API endpoint
@app.get("/api/sample/{sample_id}/scatter")
def get_scatter_plot(sample_id, downsample=10000):
    # Load full data (server has enough RAM)
    events = pd.read_parquet(f'events/{sample_id}.parquet')
    
    # Downsample for visualization
    if len(events) > downsample:
        events = events.sample(n=downsample)
    
    # Return only needed columns
    return events[['FSC-H', 'SSC-H']].to_dict('records')
    # ~10KB response vs 55MB file!
```

---

**B. Progressive Loading**

**Add to dashboard:**

```python
Features:
1. Show summary statistics first (instant)
2. Load plots progressively (one at a time)
3. "Show more detail" button → loads full resolution
4. Export raw data → download parquet file (not displayed in browser)
```

---

**C. Performance Optimizations**

**Add to Task 4.2:**

```python
Backend Caching:
- Cache pre-calculated statistics in Redis
- Cache common plot data (last 50 accessed samples)
- Invalidate cache when data updates

Frontend Optimization:
- Virtual scrolling for sample lists
- Lazy load images (only visible plots)
- WebGL for rendering large scatter plots (if needed)
```

---

### **5. NEW TASK: Data Storage Optimization**

**Add as Task 1.4 or append to Task 1.1:**

**Task: Implement Efficient Data Storage Strategy**

**Objectives:**
1. Convert all event data to Parquet format
2. Implement two-tier storage:
   - **Hot storage**: Recent/frequently accessed (SSD)
   - **Cold storage**: Historical/archived (HDD or cloud)
3. Create data catalog (index of all files, metadata, locations)

**Storage Tiers:**

| Tier | Files | Access Pattern | Storage Type | Size |
|------|-------|----------------|--------------|------|
| Hot | Last 3 months | Daily access | SSD (local) | ~50 GB |
| Warm | 3-12 months | Weekly access | HDD (local) | ~200 GB |
| Cold | >12 months | Rare access | Cloud/Archive | Unlimited |

**Automated Archival:**
```python
# Run monthly
move_to_cold_storage(age_days=90)
compress_cold_data()  # Further compress old data
update_catalog()
```

---

## 📊 Updated Task Priority Matrix

### **Phase 1: Data Processing (Weeks 1-4)**

| Task | Original Priority | New Priority | Reason |
|------|-------------------|--------------|--------|
| 1.1: FCS Parser | HIGH | **CRITICAL** | Must handle 339K events efficiently |
| 1.2: NTA Parser | HIGH | HIGH | (No change) |
| 1.3: Data Integration | MEDIUM | HIGH | Need unified format for scale |
| **1.4: Storage Strategy** | **N/A** | **HIGH** | **NEW - Essential for scale** |

### **Technical Debt to Address:**

**Before starting Task 2.1 (Analysis), must complete:**
1. ✅ Parquet conversion (Task 1.1 update)
2. ✅ Event statistics pre-calculation (Task 1.1 update)
3. ✅ Memory-efficient processing (Task 1.1 update)
4. ✅ Data quality validation (Task 1.1 update)

**Why:** Tasks 2.x and 3.x depend on efficient data access!

---

## 🛠️ Updated Technology Stack

### **NEW Libraries to Add:**

**Data Processing:**
```python
# Original plan:
pandas, numpy, fcsparser

# UPDATED - Add these:
pyarrow          # Parquet read/write (fast, efficient)
# OR
fastparquet      # Alternative parquet library

tables           # HDF5 support (for very large files)
dask             # Parallel processing for large datasets
```

**Memory Management:**
```python
memory_profiler  # Track memory usage
gc               # Garbage collection (built-in, use explicitly)
```

**Database (for metadata catalog):**
```python
sqlalchemy       # ORM for database operations
# Storage options:
sqlite3          # Small scale (built-in)
postgresql       # Production scale (recommended)
```

---

## 📝 Updated Deliverables Checklist

### **Task 1.1: Enhanced FCS Parser - REVISED**

**Original Deliverables:**
- ✅ batch_fcs_parser.py
- ✅ processed_data/fcs/ directory
- ✅ fcs_processing_log.csv
- ✅ fcs_metadata_consolidated.csv

**ADDED Deliverables:**
- ✅ **event_statistics.csv** - Pre-calculated statistics (one row per file)
- ✅ **data_quality_report.csv** - Validation results for each file
- ✅ **Parquet event files** (instead of CSV)
- ✅ **Memory usage report** - Peak RAM usage per file
- ✅ **Performance benchmarks** - Processing time per file

**File Structure:**
```
processed_data/
├── fcs/
│   ├── events/                         # ← Parquet format
│   │   ├── 0.25ug_ISO_SEC.parquet     # ~10-15 MB (was 55 MB CSV)
│   │   ├── 1ug_ISO_SEC.parquet
│   │   └── ... (70 files)
│   ├── metadata/
│   │   ├── all_metadata.csv           # Combined metadata
│   │   └── individual/                # Individual metadata files
│   ├── statistics/
│   │   ├── event_statistics.csv       # ← NEW: Summary stats
│   │   └── quality_report.csv         # ← NEW: Validation results
│   └── logs/
│       ├── processing_log.csv
│       └── memory_usage.csv           # ← NEW: Resource tracking
```

---

## ⚠️ Critical Warnings for Development

### **1. Memory Management**

**DON'T DO THIS:**
```python
# Loading all files into memory at once
all_data = []
for file in fcs_files:
    data = fcsparser.parse(file)  # 339K events!
    all_data.append(data)         # RAM explosion!
# CRASH when reaching file #10-20
```

**DO THIS:**
```python
# Process one file at a time, save results
for file in fcs_files:
    data = fcsparser.parse(file)
    stats = calculate_statistics(data)
    save_to_parquet(data, output_path)
    save_statistics(stats)
    del data  # Free memory immediately!
    gc.collect()  # Explicit garbage collection
```

---

### **2. Visualization Limits**

**DON'T DO THIS:**
```python
# Plotting 339K points
plt.scatter(data['FSC-H'], data['SSC-H'])  # Browser hangs!
```

**DO THIS:**
```python
# Downsample or use density plots
sampled = data.sample(n=10000)  # Random 10K points
plt.scatter(sampled['FSC-H'], sampled['SSC-H'])
# OR
plt.hexbin(data['FSC-H'], data['SSC-H'], gridsize=100)  # Density plot
```

---

### **3. Database Query Optimization**

**DON'T DO THIS:**
```python
# Loading all events to filter
all_events = pd.read_parquet('all_events.parquet')  # 23M rows!
filtered = all_events[all_events['sample'] == 'Sample1']
```

**DO THIS:**
```python
# Load only needed file
sample_events = pd.read_parquet('events/Sample1.parquet')  # 339K rows
# Much faster, less memory
```

---

## 🎯 Updated Success Metrics

### **Task 1.1 Completion Criteria:**

**Original:**
- ✅ Parses all 70 FCS files without errors

**UPDATED - Add these:**
- ✅ Parses all 70 FCS files without errors
- ✅ **Memory usage < 4 GB** during entire batch process
- ✅ **Processing speed**: >5 files/minute (70 files in <15 minutes)
- ✅ **Data compression**: Parquet files 70-80% smaller than CSV
- ✅ **Quality validation**: Auto-flags files with <10K events or other issues
- ✅ **Statistics generation**: event_statistics.csv contains all 70 samples

---

## 📋 Immediate Action Items

### **Before Starting Task 1.1 Development:**

**Week 1 Preparation:**
1. ✅ Install required libraries:
   ```bash
   pip install pyarrow dask memory_profiler
   ```

2. ✅ Test memory limits:
   ```python
   # Test: Can you load one FCS file comfortably?
   import fcsparser
   import psutil
   
   before = psutil.Process().memory_info().rss / 1024**2
   data = fcsparser.parse('test.fcs')
   after = psutil.Process().memory_info().rss / 1024**2
   
   print(f"Memory used: {after - before:.2f} MB")
   # Should be <500 MB for one file
   ```

3. ✅ Benchmark Parquet vs CSV:
   ```python
   # Test: Save test.csv as parquet
   import pandas as pd
   df = pd.read_csv('test.csv')
   df.to_parquet('test.parquet', compression='snappy')
   
   # Compare sizes:
   # CSV: 55 MB
   # Parquet: ~10-15 MB (70% smaller!)
   ```

4. ✅ Plan chunk size:
   ```python
   # Determine optimal chunk size for your system
   # Test with: 10K, 50K, 100K events per chunk
   # Measure: Processing time vs memory usage
   ```

---

## 📚 Updated Documentation Needs

### **Add to DEVELOPER_ONBOARDING_GUIDE.md:**

**Section: "Understanding the Data Structure"**
```markdown
### Event-Level Data vs Summary Data

**Critical Concept:**
- ONE FCS file ≠ ONE data point
- ONE FCS file = 339,392 events (individual particles)
- Each event = 26 parameters

**Memory Implications:**
- Cannot load all 70 files into RAM at once (would need ~50+ GB!)
- Must use chunked processing, Parquet format, and pre-calculated summaries

**Analysis Strategy:**
- 90% of analyses: Use event_statistics.csv (summary data)
- 10% of analyses: Load raw events.parquet (for detailed plots)
```

---

## ✅ Summary of Changes

### **What Changes:**

| Aspect | Before | After |
|--------|--------|-------|
| **Data format** | CSV | Parquet (primary) |
| **File size** | 55 MB/file | ~12 MB/file |
| **Memory strategy** | Load all | Chunked processing |
| **Analysis approach** | Raw events | Two-tier (summary + raw) |
| **Storage** | Single tier | Multi-tier (hot/cold) |
| **Validation** | Basic | Comprehensive QC |

### **New Tasks:**
- ✅ Task 1.4: Storage Strategy (NEW)
- ✅ Event statistics pre-calculation (added to 1.1)
- ✅ Data quality validation (added to 1.1)
- ✅ Memory profiling (added to all tasks)

### **Updated Priorities:**
- Task 1.1: HIGH → **CRITICAL** (must handle scale)
- Task 1.3: MEDIUM → **HIGH** (need unified format)

### **What Stays the Same:**
- Overall project phases (4 phases)
- Timeline (11-13 weeks)
- Core objectives (automation, ML, dashboard)
- Technology choices (Python, pandas, ML)

---

## 🚀 Ready to Start?

**Pre-Development Checklist:**

Before writing code for Task 1.1:
- [ ] Read this document completely
- [ ] Install new dependencies (pyarrow, dask)
- [ ] Test memory limits on your machine
- [ ] Understand chunked processing concept
- [ ] Benchmark Parquet vs CSV with test.csv
- [ ] Review updated deliverables list
- [ ] Clarify production data volumes in tech lead meeting

**Then proceed with Task 1.1 development!** 🎯

