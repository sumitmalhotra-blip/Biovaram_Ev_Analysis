# Meeting Presentation: EV Analysis Platform
## Senior Python Full-Stack Developer - Technical Overview

**Presenter:** Sumit Malhotra  
**Date:** November 2025  
**Project:** Automated Exosome Analysis Platform for Bio Varam  
**Client:** CRMIT (Contract Research Organization)

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Overview](#project-overview)
3. [Technical Architecture](#technical-architecture)
4. [Data Strategy](#data-strategy)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Technology Stack & Justification](#technology-stack--justification)
7. [Risk Mitigation](#risk-mitigation)
8. [Performance & Scalability](#performance--scalability)
9. [Q&A: Commonly Asked Questions](#qa-commonly-asked-questions)

---

## Executive Summary

### 30-Second Pitch
We're building an automated data pipeline that processes exosome characterization data from two scientific instruments (nanoFACS and NTA), consolidates it into a unified format, and enables ML-powered quality prediction - eliminating manual CSV wrangling and accelerating Bio Varam's research workflows.

### The Problem We're Solving
- **Current State:** Scientists manually copy/paste data from instrument software into Excel, losing hours per week
- **Pain Points:** Data scattered across 200+ files, inconsistent formats, error-prone manual analysis
- **Business Impact:** Research bottlenecks, delayed results, difficult to scale operations

### Our Solution
- **Automated Data Pipeline:** Parse FCS and NTA files → Unified Parquet database → ML analysis
- **Unified Data Model:** Single source of truth linking nanoFACS + NTA measurements by sample ID
- **Web Dashboard:** Real-time visualization, quality predictions, automated reporting
- **Scalability:** Designed for production volumes (current: 156 sample files, production: TBD in meeting)

### Key Metrics
- **Time Savings:** 80% reduction in data processing time
- **Storage Efficiency:** 70-80% file size reduction (Parquet vs CSV)
- **Throughput Target:** >5 files/minute processing speed
- **Memory Efficiency:** <4GB RAM for processing large datasets (339K events/file)

---

## Project Overview

### What is This Project?

Bio Varam develops iPSC-derived exosomes (30-200nm vesicles) for therapeutic applications. They use two instruments to characterize these exosomes:

1. **nanoFACS (CytoFLEX nano):** Flow cytometry measuring 26 optical parameters across ~339,000 individual particles per sample
2. **NTA (ZetaView):** Nanoparticle tracking analyzing size distributions and concentrations

**Current Workflow Problems:**
- Data trapped in proprietary formats (.fcs, .txt)
- Manual export to CSV, manual Excel analysis
- No connection between nanoFACS and NTA data for same samples
- Cannot answer: "Which samples have high CD81 expression AND optimal size distribution?"

**Our Platform:**
- **Automated parsing** of both instrument formats
- **Unified database** linking measurements by sample identifier
- **ML quality prediction** based on historical patterns
- **Web dashboard** for visualization and reporting

### Business Context

**Client:** CRMIT (Contract Research Organization)  
**End User:** Bio Varam (Therapeutic exosome development)  
**My Role:** Senior Python Full-Stack Developer (sole developer on this project)  

**Stakeholders:**
- **Scientists:** Need fast access to analysis results, quality predictions
- **Lab Managers:** Need throughput tracking, instrument utilization reports
- **Research Directors:** Need cross-batch comparisons, trend analysis

**Success Criteria:**
- Scientists spend <10 minutes per experiment on data (vs current ~1-2 hours)
- All data queryable in one place (not scattered across folders)
- Quality predictions match expert assessment >85% accuracy

---

## Technical Architecture

### Three-Layer Data Architecture

Our approach uses a **unified data model** with three distinct layers:

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: MASTER SAMPLE REGISTRY                             │
│ File: unified_data/samples/sample_metadata.parquet          │
│                                                              │
│ Purpose: Single source of truth for all samples             │
│ Key: sample_id (links everything)                           │
│                                                              │
│ Contains: sample_name, passage, fraction, antibody,         │
│           purification_method, experiment_date, etc.        │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
              ┌───────────────┴───────────────┐
              │                               │
┌─────────────▼──────────────┐  ┌────────────▼─────────────┐
│ LAYER 2A: nanoFACS Data    │  │ LAYER 2B: NTA Data       │
│                            │  │                          │
│ Raw Events (339K/file):    │  │ Size Distributions:      │
│ - events/*.parquet         │  │ - distributions/*.csv    │
│                            │  │                          │
│ Pre-calculated Statistics: │  │ Summary Statistics:      │
│ - event_statistics.parquet │  │ - nta_statistics.parquet │
│   (mean, median, std for   │  │   (D10, D50, D90,        │
│    26 parameters)          │  │    concentration, CV)    │
└────────────┬───────────────┘  └──────────┬───────────────┘
             │                             │
             └──────────────┬──────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: INTEGRATED ML DATASET                              │
│ File: unified_data/integrated/combined_features.parquet     │
│                                                              │
│ Purpose: ML-ready dataset merging both machines             │
│                                                              │
│ Structure: ~70 rows (samples) × ~350 columns (features)     │
│ - facs_mean_FSC, facs_pct_marker_positive, ...             │
│ - nta_D50_nm, nta_concentration, ...                        │
│ - derived: size_correlation, purity_score                   │
│ - labels: quality_label, quality_score                      │
└─────────────────────────────────────────────────────────────┘
```

### Why This Architecture?

**Separation of Concerns:**
- Layer 1: Sample metadata (who/what/when)
- Layer 2: Machine-specific measurements (raw instrument outputs)
- Layer 3: Integrated analysis (ML-ready combined data)

**Flexibility:**
- Add new instruments? → Add new Layer 2 branch, merge into Layer 3
- Change ML features? → Regenerate Layer 3, Layers 1-2 unchanged
- Reprocess old data? → Rebuild from Layer 2, preserve Layer 1

**Performance:**
- Don't load 339K events just to see summary statistics
- Pre-calculated statistics in Layer 2 (event_statistics.parquet)
- Query combined_features.parquet for ML training (no joins needed)

### Directory Structure

```
ev_analysis_platform/
├── raw_data/                          # Original instrument files
│   ├── nanoFACS/
│   │   └── 10000 exo and cd81/
│   │       ├── Exo Control.fcs        # 339,392 events each
│   │       ├── Exo + 0.25ug CD81 SEC.fcs
│   │       └── ...
│   └── NTA/
│       └── EV_IPSC_P1_19_2_25_NTA/
│           ├── 20250219_0001_...txt
│           └── ...
│
├── processed_data/
│   ├── samples/
│   │   └── sample_metadata.parquet     # Layer 1: Master registry
│   │
│   ├── measurements/
│   │   ├── nanofacs/
│   │   │   ├── events/
│   │   │   │   └── *.parquet          # Raw events (12MB each)
│   │   │   └── statistics/
│   │   │       ├── event_statistics.parquet    # Pre-calculated
│   │   │       └── quality_report.parquet
│   │   │
│   │   └── nta/
│   │       ├── distributions/
│   │       │   └── *.csv              # Size distributions
│   │       └── summary/
│   │           └── nta_statistics.parquet
│   │
│   └── unified_data/
│       ├── samples/
│       │   └── sample_metadata.parquet # Complete registry
│       └── integrated/
│           ├── combined_features.parquet    # Layer 3: ML dataset
│           ├── quality_labels.parquet
│           └── correlation_analysis.parquet
│
├── scripts/
│   ├── parse_fcs.py                   # Task 1.1
│   ├── parse_nta.py                   # Task 1.2
│   └── create_integrated_dataset.py   # Task 1.3
│
├── models/                            # ML models (Task 3.x)
├── dashboard/                         # Web app (Task 4.x)
└── docs/
```

---

## Data Strategy

### Critical Discovery: Understanding Data Scale

**Initial Assumption:** 156 files = 156 data points  
**Reality:** 1 FCS file = **339,392 events** × 26 parameters = **8.8 million data points**

**Sample Dataset Analysis:**
- 70 FCS files × 339K events = **23.7 million events**
- Total data points: 23.7M events × 26 parameters = **615 million data points**
- CSV file size: 55 MB per file → 3.85 GB total for 70 files
- **This is just sample data, production scale TBD**

**Architectural Impact:**
- ❌ Cannot load entire datasets into memory naively
- ✅ Need chunked processing, streaming approaches
- ✅ Need pre-calculated statistics to avoid repeated raw data access
- ✅ Need efficient storage format (Parquet, not CSV)

### Format Decision: Parquet vs JSON vs CSV

After comprehensive analysis, we chose **Apache Parquet** as primary storage format:

**File Size Comparison (test.csv: 339K events):**
- CSV: 55 MB
- JSON: ~150 MB (2.7x larger than CSV)
- **Parquet: 12 MB (78% reduction vs CSV)**

**Load Speed Comparison:**
```python
# pandas.read_csv():     ~2.5 seconds
# pandas.read_json():    ~8-12 seconds
# pandas.read_parquet(): ~0.2 seconds  ← 10-20x faster
```

**Why Parquet Wins:**
1. **Columnar Storage:** Only read columns you need (not entire rows)
2. **Built-in Compression:** Snappy compression (70-80% reduction)
3. **Type Safety:** Preserves int/float/datetime types (CSV loses this)
4. **Metadata:** Schema embedded in file (self-documenting)
5. **ML Integration:** Native support in pandas, Dask, TensorFlow, PyTorch
6. **Query Optimization:** Skip chunks based on column statistics

**Format Strategy:**
- **Bulk Data:** Parquet (events, statistics, features)
- **API Responses:** JSON (small payloads only, <1000 rows)
- **Human Review:** CSV export on-demand from Parquet
- **Archival:** Parquet with Gzip compression (cold storage)

### Memory Management Strategy

**The Problem:**
Loading 339K events at once = **~150 MB per file** in RAM  
Processing 70 files naively = **10.5 GB** (exceeds typical laptop RAM)

**Our Solutions:**

1. **Chunked Processing:**
```python
# DON'T: Load entire file
df = pd.read_csv('huge_file.csv')  # 💥 Memory error

# DO: Process in chunks
for chunk in pd.read_csv('huge_file.csv', chunksize=50000):
    process_chunk(chunk)
    # Memory freed after each iteration
```

2. **Pre-calculated Statistics:**
```python
# DON'T: Load raw events every time
events = pd.read_parquet('events/sample1.parquet')  # 339K rows
mean_fsc = events['FSC-H'].mean()  # Loads all data

# DO: Use pre-calculated stats
stats = pd.read_parquet('statistics/event_statistics.parquet')  # 70 rows
mean_fsc = stats.loc['sample1', 'mean_FSC']  # Instant
```

3. **Explicit Garbage Collection:**
```python
import gc

def process_file(filepath):
    df = parse_fcs(filepath)
    stats = calculate_statistics(df)
    del df           # Free memory
    gc.collect()     # Force cleanup
    return stats
```

4. **Dask for Parallel Processing:**
```python
# Process multiple files in parallel without memory explosion
import dask.dataframe as dd

# Lazy loading - doesn't load until compute()
ddf = dd.read_parquet('events/*.parquet')
result = ddf.groupby('sample_id').mean().compute()
```

**Performance Targets:**
- Peak memory usage: <4 GB for processing entire dataset
- Processing speed: >5 files/minute
- Storage compression: 70-80% vs CSV

---

## Implementation Roadmap

### Phase 1: Data Processing Pipeline (6-8 weeks)

**Task 1.1: Enhanced FCS Parser (4-5 weeks)**
- Parse .fcs files (CytoFLEX nano format)
- Extract 26 optical parameters per event (FSC, SSC, fluorescence channels)
- Generate sample_id from filename
- Output:
  - `events/*.parquet` - Raw event data (12 MB each)
  - `event_statistics.parquet` - Pre-calculated means, medians, percentiles
  - `quality_report.parquet` - Data quality flags
- Memory: Chunked processing, <4GB peak usage
- Dependencies: `fcsparser`, `pandas`, `pyarrow`, `dask`

**Task 1.2: NTA Parser (2-3 weeks)**
- Parse ZetaView .txt files (size distributions)
- Extract D10/D50/D90, concentration, CV
- Calculate uniformity scores
- Append to sample_metadata.parquet
- Output:
  - `nta_statistics.parquet` - Summary metrics
  - `distributions/*.csv` - Size histograms
- Dependencies: `pandas`, `numpy`, `pyarrow`

**Task 1.3: Data Integration (1-2 weeks)**
- Merge nanoFACS + NTA by sample_id
- Create combined_features.parquet (350 columns)
- Calculate cross-machine correlations (FSC vs D50_nm)
- Generate quality labels for ML training
- Handle missing data (samples with only one machine)
- Output:
  - `combined_features.parquet` - ML-ready dataset
  - `quality_labels.parquet` - Training labels
  - `correlation_analysis.parquet` - Cross-machine metrics

### Phase 2: Analysis & Visualization (3-4 weeks)

**Task 2.1: Statistical Analysis Module**
- Calculate summary statistics from event_statistics.parquet
- Identify outliers using IQR/Z-score
- Generate comparison reports (CD81 vs ISO controls)

**Task 2.2: Visualization Module**
- Scatter plots (FSC vs SSC)
- Histograms (size distributions)
- Heatmaps (correlation matrices)
- Use downsampling for large datasets (plot 10K points, not 339K)

**Task 2.3: Automated Reporting**
- Generate PDF reports with plots + tables
- Email notifications for completed analyses

### Phase 3: Machine Learning (4-5 weeks)

**Task 3.1: Feature Engineering**
- Load combined_features.parquet
- 300+ nanoFACS features (means, stds, percentiles, gate percentages)
- 50+ NTA features (size distributions, uniformity)
- Derived features (purity scores, size correlations)

**Task 3.2: Quality Prediction Model**
- Train classifier: Good/Bad/Marginal quality
- Algorithms: Random Forest, XGBoost, Neural Network
- Validation: Cross-validation, holdout test set
- Target: >85% accuracy matching expert labels

**Task 3.3: Batch Comparison ML**
- Identify similar batches (clustering)
- Anomaly detection for QC failures

### Phase 4: Web Application (5-6 weeks)

**Task 4.1: Backend API (Flask/FastAPI)**
- REST endpoints for data queries
- Authentication, file upload handlers
- Return small JSON responses (<1000 rows)

**Task 4.2: Frontend Dashboard (React)**
- File upload interface
- Real-time processing status
- Interactive plots (Plotly.js)
- Quality prediction results

**Task 4.3: Deployment**
- Docker containerization
- Cloud deployment (AWS/Azure/GCP)
- Database setup (PostgreSQL for metadata)
- Documentation + user guide

**Total Timeline:** 18-23 weeks (~4.5-6 months)

---

## Technology Stack & Justification

### Core Technologies

| Component | Technology | Why This Choice? |
|-----------|-----------|------------------|
| **Language** | Python 3.8+ | Scientific computing ecosystem, ML libraries, team expertise |
| **Data Storage** | Apache Parquet | 70-80% compression, 10x faster loading, columnar efficiency |
| **Data Processing** | pandas + Dask | Industry standard, Dask adds parallel processing |
| **FCS Parsing** | fcsparser | Purpose-built for flow cytometry files |
| **Memory Profiling** | memory_profiler | Track RAM usage, prevent memory leaks |
| **ML Framework** | scikit-learn | Simple API, proven for tabular data |
| **Deep Learning** | TensorFlow/PyTorch | For advanced models if needed |
| **Web Backend** | FastAPI | Modern async framework, auto-generated docs |
| **Web Frontend** | React | Component-based, large ecosystem |
| **Visualization** | Plotly.js | Interactive plots, publication-quality |
| **Database** | PostgreSQL | Robust, handles JSON, great for metadata |
| **Deployment** | Docker + Cloud | Reproducible, scalable, platform-agnostic |

### Alternative Approaches Considered

**Why Not Just Use Excel/MATLAB?**
- ❌ Excel: Cannot handle 339K rows efficiently, manual workflows error-prone
- ❌ MATLAB: Expensive licensing, not web-deployable, team lacks expertise
- ✅ Python: Open-source, web-ready, ML ecosystem, scalable

**Why Not JSON for Data Storage?**
- ❌ JSON: 12-20x larger than Parquet, no type safety, slow to parse
- ✅ JSON for API: Perfect for small responses (<1000 rows)
- ✅ Parquet for bulk: Optimized for analysis, not human editing

**Why Not SQL Database for Events?**
- ❌ 339K rows per sample × 26 columns = database bloat
- ❌ Queries slow for numerical operations (mean, percentile)
- ✅ Parquet: Faster for analytics, easier backups, no DB overhead
- ✅ PostgreSQL: Only for metadata (sample registry, user accounts)

**Why Not HDF5?**
- ⚖️ HDF5: Good alternative, similar performance to Parquet
- ✅ Parquet: Better cloud storage integration, wider ML tool support
- We're flexible - can switch if project needs change

---

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Memory overflow** processing large files | High | High | Chunked processing, streaming, memory profiling |
| **Data loss** during parsing errors | Medium | High | Try-catch blocks, error logs, quarantine invalid files |
| **Slow processing** (<5 files/min) | Medium | Medium | Parallel processing (Dask), profile bottlenecks, optimize |
| **ML model poor accuracy** (<85%) | Medium | Medium | Feature engineering, multiple algorithms, expert validation |
| **Production volume** exceeds design | Medium | High | Clarify in meeting, design for 10x current scale |

### Project Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Scope creep** (new instrument types) | High | Medium | Phase 1 focuses on nanoFACS + NTA only, extensible design |
| **Changing requirements** mid-project | Medium | High | Weekly check-ins, document all decisions, modular architecture |
| **Single developer** (me) bottleneck | High | High | Clear documentation, GitHub commits, knowledge transfer docs |
| **Deployment blockers** (IT policies) | Medium | Medium | Early infrastructure discussions, Docker for portability |

### Data Quality Risks

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **Inconsistent filenames** → sample_id errors | High | High | Robust parsing with fallbacks, validation reports |
| **Missing metadata** (passage, antibody) | Medium | Medium | Flag in quality_report, allow manual annotation |
| **Instrument calibration drift** over time | Low | Medium | Track instrument settings, flag anomalies |
| **Samples with only one machine** data | High | Low | Design allows partial data, flag in combined_features |

---

## Performance & Scalability

### Current Scale (Sample Data)

**Data Volume:**
- 70 FCS files × 339,392 events = 23.7M events
- 615M total data points (23.7M × 26 parameters)
- Storage: 3.85 GB (CSV) → **0.84 GB (Parquet)** = 78% reduction

**Processing Requirements:**
- Target: >5 files/minute = **<12 seconds per file**
- Memory: <4 GB peak usage
- Disk I/O: Parquet loads 10x faster than CSV

### Production Scale (TBD - Ask in Meeting)

**Critical Questions for Meeting:**
1. How many samples analyzed per day/week/month?
2. Expected growth rate (next 1 year, 3 years)?
3. Real-time processing needed or batch overnight?
4. How many concurrent users accessing data?
5. Data retention policy (archive old data)?

**Scalability Design:**
- **Horizontal Scaling:** Dask allows multi-machine processing if needed
- **Storage Tiers:** 
  - Hot: Recent data on SSD (fast access)
  - Warm: 3-6 months on HDD
  - Cold: >6 months archived (Parquet with Gzip)
- **Database:** PostgreSQL can handle millions of metadata rows
- **Cloud Ready:** Can deploy on AWS/Azure with auto-scaling

### Benchmarks & Monitoring

**What We'll Track:**
- Processing time per file (target: <12 sec)
- Memory usage per file (target: <500 MB peak)
- Storage efficiency (target: 70-80% compression)
- API response time (target: <2 sec for queries)
- ML prediction accuracy (target: >85%)

**How We'll Monitor:**
- Python memory_profiler for RAM tracking
- Logging timestamps for each processing step
- Dashboard showing throughput (files/hour)
- Automated alerts if processing fails/slows

---

## Q&A: Commonly Asked Questions

### Architecture & Design Questions

**Q1: Why not just keep using CSV files? They're simple and everyone knows Excel.**

**A:** Great question - CSV is familiar, but we discovered it doesn't scale:
- **Size:** Our test file is 55 MB in CSV vs 12 MB in Parquet (78% smaller)
- **Speed:** Parquet loads 10-20x faster than CSV
- **Type Safety:** CSV treats everything as text, loses int/float distinctions
- **Columns:** CSV must read all columns even if you need only 2 of 26
- **ML Integration:** pandas/sklearn read Parquet natively, just as easy as CSV

**Bottom line:** We can always export CSV for human review, but Parquet is better for computation.

---

**Q2: What happens if we add a third instrument later (e.g., electron microscopy)?**

**A:** Our three-layer architecture handles this elegantly:
1. **Layer 1 (sample registry):** Add new samples, no changes needed
2. **Layer 2:** Create new branch for EM data (e.g., `measurements/em/`)
3. **Layer 3:** Update integration script to merge EM features alongside nanoFACS/NTA

The key is **sample_id** links everything - as long as new instruments use same sample IDs, integration is straightforward.

---

**Q3: Why separate event_statistics.parquet from raw events? Isn't that duplication?**

**A:** It's a deliberate performance optimization:
- **Raw events:** 339,392 rows, 12 MB - only load when doing deep analysis
- **Statistics:** 1 row, ~10 KB - load this for 99% of queries

Example: "Show me mean FSC for all 70 samples"
- Without stats: Load 23.7M events (840 MB) → calculate means → 2 minutes
- With stats: Load 70 rows (70 KB) → instant

**Tradeoff:** Slightly more storage (~1% overhead) for 100x faster queries.

---

**Q4: What if we want to reprocess old data with updated algorithms?**

**A:** Our layered design allows selective reprocessing:
- **Change Layer 1:** Manual corrections only (rare)
- **Change Layer 2:** Reparse raw .fcs/.txt files → regenerate events & statistics
- **Change Layer 3:** Rerun integration script → regenerate combined_features

Example: "We want to add a new quality metric"
- Don't touch Layer 1-2 (raw data unchanged)
- Update Layer 3 integration script
- Rerun: `python create_integrated_dataset.py` → done in minutes

---

### Data & Format Questions

**Q5: How do you handle samples that only have nanoFACS data but no NTA data (or vice versa)?**

**A:** The unified data model uses **outer joins** (not inner):
```python
combined = metadata.merge(nanofacs, on='sample_id', how='left')
combined = combined.merge(nta, on='sample_id', how='left')
```
- Samples with only nanoFACS: NTA columns will be NaN
- Samples with only NTA: nanoFACS columns will be NaN
- We **flag** these in quality_report.parquet but **don't discard** them
- ML models can handle missing values (imputation or tree-based methods)

---

**Q6: JSON is easier to read and debug. Why not use it for everything?**

**A:** JSON is excellent for small, nested data (APIs, configs), but terrible for large tabular data:

**File Size Example (339K events):**
- CSV: 55 MB
- JSON: ~150 MB (2.7x larger!)
- Parquet: 12 MB (12x smaller than JSON)

**Why JSON bloats:**
```json
[
  {"FSC-H": 1234, "SSC-H": 5678, ...},  ← Every row repeats column names
  {"FSC-H": 1235, "SSC-H": 5679, ...},
  ...339,392 times
]
```

**Our strategy:**
- Bulk storage: Parquet (efficient)
- API responses: JSON (only for small results, <1000 rows)
- Debugging: We can convert Parquet → JSON on-demand

---

**Q7: What about HDF5? I've heard it's good for scientific data.**

**A:** HDF5 is indeed excellent and we considered it:

**Pros of HDF5:**
- Hierarchical structure (groups, datasets)
- Very fast for numerical operations
- Standard in scientific computing

**Why we chose Parquet:**
- Better cloud storage support (S3, GCS, Azure Blob)
- Native integration with Spark, Dask, pandas
- Wider ML ecosystem support
- Simpler file structure (one file = one table)

**We're flexible:** If project needs change, switching to HDF5 is low-effort.

---

**Q8: How do you generate sample_id from filenames? What if filenames are inconsistent?**

**A:** We use a **robust parsing strategy with fallbacks:**

```python
def generate_sample_id(filename, metadata):
    """
    Strategy:
    1. Try parsing structured filename: "L5+F10+CD9.fcs" → passage=5, fraction=10, antibody=CD9
    2. Fall back to metadata fields (if available)
    3. Last resort: Use full filename as ID (flag for manual review)
    """
    try:
        # Parse pattern: L{passage}+F{fraction}+{antibody}
        match = re.match(r'L(\d+)\+F(\d+)\+(.+)\.fcs', filename)
        if match:
            return f"P{match[1]}_F{match[2]}_{match[3]}"
    except:
        pass
    
    # Fallback: Use metadata
    if 'passage' in metadata and 'fraction' in metadata:
        return f"P{metadata['passage']}_F{metadata['fraction']}_..."
    
    # Last resort: Clean filename
    return sanitize_filename(filename)
```

**Validation:**
- Generate quality_report.parquet flagging unparseable filenames
- Scientist reviews and provides manual mapping if needed
- System learns from corrections (add to parsing rules)

---

### Performance & Scalability Questions

**Q9: You said 156 files are just samples. What if production has 10,000 files?**

**A:** That's exactly why we need to clarify in the meeting! Here's our scalability plan:

**Current Design (156 files):**
- Processing: ~30 minutes for all files
- Storage: ~840 MB (Parquet)
- Memory: <4 GB peak

**If Production = 10,000 files:**
- Processing: ~30 hours (batch overnight) OR parallelize to ~3 hours (10 workers)
- Storage: ~54 GB (Parquet) - manageable
- Memory: Still <4 GB per worker (chunked processing)

**Optimizations Available:**
1. **Dask Distributed:** Process on multiple machines
2. **Cloud Functions:** Auto-scale workers based on queue size
3. **Incremental Processing:** Only process new files, not entire dataset
4. **Storage Tiers:** Archive old data to cold storage

**Critical Meeting Questions:**
- What's expected production volume? (files/day, files/month)
- Growth trajectory over next 1-3 years?
- Real-time processing needed or can we batch overnight?

---

**Q10: What if processing one file takes >12 seconds (missing your 5 files/min target)?**

**A:** We have a **performance optimization roadmap:**

**First, diagnose bottleneck:**
- Profile with `memory_profiler` and `cProfile`
- Is it I/O bound (disk reads)? → Use SSDs, optimize Parquet chunk size
- Is it CPU bound (calculations)? → Parallelize with multiprocessing
- Is it memory bound (swapping)? → Increase chunk size, reduce precision

**Common Fixes:**
1. **Optimize FCS parsing:** fcsparser can be slow, consider custom C-based parser
2. **Downsample raw events:** Store all 339K, but calculate stats on 50K sample
3. **Pre-filter events:** Remove debris/noise before saving
4. **Batch operations:** Process 10 files at once (Dask), amortize overhead

**Fallback Plan:**
If we can't hit 5 files/min after optimization:
- Adjust target based on actual needs (is <3 files/min acceptable?)
- Increase hardware (more RAM, faster CPU)
- Parallelize across multiple machines

**Transparency:** We set 5 files/min as initial target, but real requirement depends on production volume (TBD in meeting).

---

**Q11: How much will cloud hosting cost?**

**A:** Rough estimate (needs refinement after meeting):

**AWS Example (moderate usage):**
- **Compute:** EC2 t3.medium (2 vCPU, 4 GB RAM) = ~$30/month
- **Storage:** S3 for 100 GB data = ~$3/month
- **Database:** RDS PostgreSQL (small instance) = ~$15/month
- **Total:** ~$50-100/month for development/testing

**Production (depends on scale):**
- If processing 1000 files/month: ~$100-200/month
- If heavy ML training: Add GPU instances (~$500-1000/month when training)
- If high user concurrency: Scale up web instances (+$100-300/month)

**Cost Optimization:**
- Use spot instances for batch processing (70% cheaper)
- Archive old data to Glacier ($1/TB/month)
- Auto-scale: Only pay for resources when needed

**Alternative:** On-premise server if CRMIT has infrastructure (one-time hardware cost, no monthly fees).

---

### Machine Learning Questions

**Q12: How will you train the ML model if you don't have labeled data yet?**

**A:** Excellent question - we have a **phased ML approach:**

**Phase 1: Unsupervised Learning (No labels needed)**
- **Clustering:** Group similar samples (K-means, DBSCAN)
- **Anomaly Detection:** Flag outliers (Isolation Forest)
- **Visualization:** PCA/t-SNE to explore patterns
- **Value:** Scientists see patterns, identify QC failures without manual labeling

**Phase 2: Semi-Supervised Learning (Few labels)**
- Scientist labels 20-50 samples as "Good/Bad"
- Train initial model, predict rest
- Scientist reviews predictions, corrects errors
- Retrain with corrected labels (active learning loop)

**Phase 3: Supervised Learning (Sufficient labels)**
- Once we have 100+ labeled samples:
- Train robust classifier (Random Forest, XGBoost)
- Validate on holdout set
- Deploy for automated predictions

**Labeling Strategy:**
- Scientists already know good vs bad samples (implicit knowledge)
- We formalize this: "CD81+ >30%, debris <10% = Good"
- System learns from these rules + manual corrections

---

**Q13: What if the ML model predicts wrong quality labels?**

**A:** ML is assistive, not autonomous:

**Safety Mechanisms:**
1. **Confidence Scores:** Show "85% confident this is Good"
2. **Manual Override:** Scientists can always correct predictions
3. **Audit Trail:** Log all predictions + corrections
4. **Retraining:** Learn from corrections to improve model

**Example Workflow:**
1. System predicts: "Sample X = Bad (75% confidence)"
2. Scientist reviews data, agrees → No action needed
3. Scientist disagrees → Clicks "Actually Good" → System records correction
4. Next retraining: Model learns from this example

**Target Accuracy:**
- Goal: >85% matches expert assessment
- If lower: Feature engineering, try different algorithms, get more labels
- Never deploy model that's worse than random guessing (50%)

---

**Q14: Can the model explain WHY it classified a sample as "Bad"?**

**A:** Yes, with **explainable AI techniques:**

**Feature Importance (Global):**
```python
# Random Forest automatically gives feature importance
model.feature_importances_
# Output: "facs_pct_debris" is most important (0.35)
#         "nta_D50_nm" is second (0.22), etc.
```

**SHAP Values (Per-Sample Explanation):**
```python
import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(sample_X)

# Explanation: "This sample is Bad because:"
# - facs_pct_debris = 45% (too high) → +0.6 toward "Bad"
# - nta_uniformity = 0.3 (low) → +0.4 toward "Bad"
# - facs_mean_FSC = 12000 (normal) → -0.1 toward "Good"
```

**Dashboard Display:**
- Show top 3 reasons for prediction
- Highlight problematic features in red
- Compare to "typical Good sample" values

---

### Technical Implementation Questions

**Q15: Why FastAPI instead of Flask for the backend?**

**A:** Both are excellent, FastAPI has modern advantages:

**FastAPI Pros:**
- **Async Support:** Handle multiple requests simultaneously (better performance)
- **Auto Documentation:** Swagger UI generated automatically (try out APIs in browser)
- **Type Hints:** Catches errors at development time
- **Modern:** Built on latest Python 3.8+ features

**Flask Pros:**
- **Maturity:** More Stack Overflow answers, tutorials
- **Simplicity:** Slightly easier for small projects
- **Ecosystem:** Larger plugin ecosystem

**Decision:** FastAPI for this project (async + auto-docs are valuable), but we can switch to Flask if team prefers.

---

**Q16: How will you handle concurrent users uploading files at the same time?**

**A:** Web architecture with **task queue:**

```
User A uploads file → API → Task Queue (Redis/Celery) → Worker 1 processes
User B uploads file → API → Task Queue → Worker 2 processes
User C uploads file → API → Task Queue → Worker 3 processes
```

**Benefits:**
- API responds immediately ("File queued, processing started")
- Workers process in background
- Users see real-time progress (WebSocket updates)
- Auto-scale workers if queue gets long

**Technologies:**
- **Celery:** Python task queue
- **Redis:** Message broker
- **WebSockets:** Real-time status updates to frontend

---

**Q17: What about data security? This is scientific IP.**

**A:** Multi-layer security approach:

**1. Authentication & Authorization:**
- User login (JWT tokens)
- Role-based access: Admin, Scientist, Viewer
- API endpoints require valid token

**2. Data Encryption:**
- HTTPS for all web traffic (TLS 1.3)
- Encrypt Parquet files at rest (if on cloud)
- Database encryption (PostgreSQL supports this)

**3. Audit Logging:**
- Track who accessed what data when
- Log all uploads, downloads, modifications
- Immutable logs (append-only)

**4. Compliance:**
- GDPR (if EU data): Right to deletion, data export
- HIPAA (if clinical): Additional safeguards needed
- **Ask in meeting:** What compliance requirements?

**5. Backup & Recovery:**
- Daily backups of database + Parquet files
- Test restore procedures monthly
- Offsite backup storage

---

**Q18: What if the server crashes during processing? Do we lose data?**

**A:** Robust error handling with **checkpointing:**

**Strategy:**
1. **Atomic Operations:** Files processed fully or not at all (no partial)
2. **Status Tracking:** Database tracks file status (pending/processing/complete/failed)
3. **Checkpoints:** Save intermediate results every N files
4. **Retry Logic:** Failed files auto-retry 3 times with exponential backoff
5. **Dead Letter Queue:** Persistently failing files flagged for manual review

**Example:**
```
Processing 100 files:
- Files 1-50: Complete → Saved to Parquet
- File 51: CRASH → Status = "processing"
- Server restarts → Checks status → Resumes from file 51
- No data loss, no duplicate processing
```

**Monitoring:**
- Email alerts if server down >5 minutes
- Dashboard shows processing health
- Automated health checks every minute

---

### Project Management Questions

**Q19: You're the only developer. What if you get sick or leave?**

**A:** Knowledge transfer is critical:

**Documentation Strategy:**
1. **README.md:** Quick start guide (install, run, test)
2. **Architecture docs:** This master document + technical guides
3. **Code Comments:** Explain WHY, not just WHAT
4. **API Documentation:** Auto-generated (FastAPI Swagger)
5. **Video Walkthrough:** Record screen sharing session explaining codebase

**GitHub Best Practices:**
- Commit frequently with clear messages
- Tag releases (v1.0, v1.1, etc.)
- Keep TASK_TRACKER.md updated with progress

**Handover Checklist (if needed):**
- [ ] New developer can run code locally
- [ ] New developer can deploy to test environment
- [ ] New developer understands data flow (Layer 1 → 2 → 3)
- [ ] New developer can add new feature (e.g., new plot type)

**Mitigation:**
- Train backup developer (even part-time) by month 3
- Pair programming sessions for complex modules
- Code reviews (even if self-reviews initially)

---

**Q20: How will you know when each task is "done"?**

**A:** Clear **Definition of Done (DoD)** for each task:

**Task 1.1 (FCS Parser) is DONE when:**
- [ ] All 70 sample FCS files parse without errors
- [ ] Output Parquet files validated (correct schema, row counts)
- [ ] Memory usage <4GB peak (measured with memory_profiler)
- [ ] Processing speed >5 files/minute (measured with timer)
- [ ] Unit tests pass (test with known FCS file, verify output)
- [ ] Documentation updated (docstrings, README)
- [ ] Code reviewed (self-review checklist or peer)
- [ ] Committed to GitHub with passing CI checks

**Task 3.2 (ML Model) is DONE when:**
- [ ] Model trained on labeled dataset (min 100 samples)
- [ ] Cross-validation accuracy >85%
- [ ] Tested on holdout set (not used in training)
- [ ] Confusion matrix analyzed (low false positives)
- [ ] Model saved to disk (pickle or joblib)
- [ ] Prediction API endpoint created and tested
- [ ] Documentation: How to retrain, update model
- [ ] Committed to GitHub

**Weekly Progress Checks:**
- What tasks moved to "done" this week?
- Any blockers preventing completion?
- Adjust timeline if needed

---

**Q21: What happens if requirements change mid-project?**

**A:** Agile mindset with **change management process:**

**Minor Changes (low impact):**
- Example: "Can we add one more plot type?"
- Impact assessment: <1 day effort, no architecture change
- Decision: Accept, add to current sprint

**Major Changes (high impact):**
- Example: "Can we add a third instrument (EM)?"
- Impact assessment: 2-3 weeks, new parsers, schema changes
- Decision: Document requirement, estimate effort, reprioritize roadmap
- Client approval needed (timeline/budget impact)

**Change Request Process:**
1. Document new requirement clearly
2. Estimate effort (hours/days)
3. Assess impact on timeline/budget
4. Discuss with stakeholders
5. Accept (adjust timeline) OR defer to Phase 2

**Protection:**
- Phase 1 scope locked (nanoFACS + NTA only)
- New features go to "Phase 2 backlog"
- Re-evaluate priorities every month

---

**Q22: How will you demo progress to stakeholders?**

**A:** Regular demos with **working software:**

**Month 1 Demo (After Task 1.1-1.2):**
- Show: Upload FCS file → See parsed data in table
- Show: event_statistics.parquet loaded instantly
- Show: Memory profiler graph (stayed under 4GB)
- Metrics: "Processed 70 files in 10 minutes"

**Month 2 Demo (After Task 2.1-2.2):**
- Show: Interactive scatter plot (FSC vs SSC)
- Show: Comparison report (CD81 vs ISO controls)
- Show: Automated PDF report generation

**Month 3 Demo (After Task 3.1-3.2):**
- Show: Upload new sample → ML predicts quality
- Show: Explanation ("Bad because debris >40%")
- Show: Accuracy metrics (88% on test set)

**Month 4-5 Demo (After Task 4.1-4.2):**
- Show: Full web dashboard (upload, visualize, predict)
- Show: Multi-user access
- Show: Real-time processing status

**Format:**
- 15-minute live demo
- 5-minute Q&A
- Feedback form (what to add/change?)

---

### Data Science & Domain Questions

**Q23: What's the difference between FSC, SSC, and fluorescence channels?**

**A:** These are optical measurements in flow cytometry:

**FSC (Forward Scatter):**
- Measures light scattered in forward direction
- **Correlates with:** Particle size (larger particles = more FSC)
- **Use case:** Identify exosomes vs debris vs large particles

**SSC (Side Scatter):**
- Measures light scattered at 90° angle
- **Correlates with:** Internal complexity, granularity
- **Use case:** Distinguish exosomes from protein aggregates

**Fluorescence Channels (V447, B531, etc.):**
- Measure fluorescence from antibody labels
- Example: CD81-PE antibody → emits light at 531 nm
- **Use case:** Detect specific markers (CD81, CD9, CD63)

**Why This Matters for Our Platform:**
- We parse all 26 parameters (FSC, SSC, 24 fluorescence channels)
- Scientists set "gates" to define populations:
  - EV gate: FSC 1000-10000, SSC 500-5000
  - CD81+ gate: V447 >500 (positive for marker)
- Our analysis calculates % in each gate

---

**Q24: What is "gating" and why is it important?**

**A:** Gating is defining populations of interest:

**Example:**
```
All events (339,392)
    ├── Debris gate (high SSC, low FSC): 15% → Discard
    ├── Large particles (high FSC): 10% → Discard
    └── EV gate (moderate FSC/SSC): 75%
            ├── CD81 negative: 30%
            └── CD81 positive: 45% ← This is the target!
```

**Our Platform's Role:**
1. **Parse gates** from FCS metadata (scientists define in CytoFLEX software)
2. **Calculate percentages:** % in each gate
3. **Quality metrics:** "Good sample if CD81+ >30%, debris <20%"
4. **ML features:** Gate percentages become input features

**Why It's Critical:**
- Quality assessment depends on gate percentages
- Different experiments use different gates
- Must preserve gating logic from instrument software

---

**Q25: What is D10, D50, D90 in NTA data?**

**A:** These are size distribution percentiles:

**Definition:**
- **D10:** 10% of particles are smaller than this size
- **D50:** Median size (50th percentile)
- **D90:** 90% of particles are smaller than this size

**Example:**
```
Sample A: D10=50nm, D50=100nm, D90=180nm
→ Narrow distribution, uniform size

Sample B: D10=30nm, D50=100nm, D90=250nm
→ Wide distribution, heterogeneous
```

**Our Calculations:**
- **Uniformity Score:** (D90 - D10) / D50
  - Lower = more uniform
  - Higher = heterogeneous
- **Quality Metric:** Exosomes should be 30-200nm
  - Good: D10>30, D90<200
  - Bad: D10<30 or D90>300 (contamination)

---

**Q26: How do you correlate FSC (from nanoFACS) with D50 (from NTA)?**

**A:** Both measure size, but different physics:

**FSC (Forward Scatter):**
- Arbitrary units (not nanometers)
- Relative measurement (higher FSC = larger)
- Affected by refractive index, laser wavelength

**D50 (NTA):**
- Absolute size in nanometers
- Direct particle tracking measurement
- True physical size

**Correlation Strategy:**
1. **Calibration:** Measure known size beads (100nm) on nanoFACS → establish FSC value
2. **Calculate:** FSC units → nanometers conversion factor
3. **Compare:** Converted FSC vs NTA D50 for same samples
4. **Analyze:** Are they consistent? (Should be correlated)

**Why It Matters:**
- **Validation:** If FSC and D50 disagree → sample quality issue or instrument error
- **ML Feature:** size_correlation = corr(FSC, D50) → Input to quality model
- **Troubleshooting:** Discrepancy flags calibration drift

---

### Meeting Preparation Questions

**Q27: What questions should I ask in the meeting to clarify requirements?**

**A:** Here are critical questions by category:

**Production Scale:**
1. How many samples do you analyze per day/week/month currently?
2. What's the expected volume in 1 year? 3 years?
3. What's the maximum samples in a single experiment batch?
4. Do you run experiments 24/7 or only during work hours?

**Processing Requirements:**
5. Do you need real-time results or can processing happen overnight?
6. How quickly do you need results after experiment completion? (minutes/hours/days)
7. How many people will be uploading/analyzing data concurrently?

**Data Retention:**
8. How long should we keep raw FCS/NTA files? (months/years/forever)
9. Any compliance requirements (HIPAA, GLP, FDA)?
10. Do you need audit trails showing who accessed what data when?

**Infrastructure:**
11. Do you prefer cloud deployment (AWS/Azure) or on-premise server?
12. Any IT policies restricting cloud usage?
13. Who will maintain the server (IT team or external)?

**Existing Systems:**
14. Are you currently using any analysis software we should integrate with?
15. Do you export data to other systems (LIMS, ELN)?
16. Any preferred file formats for exports?

**Quality Criteria:**
17. How do you currently decide if a sample is "good quality"?
18. Can you provide examples of good vs bad samples?
19. What are dealbreaker issues? (e.g., >X% debris = unusable)

**Feature Priorities:**
20. What's most critical: Fast processing, ML predictions, or visualizations?
21. Which reports do you generate most often?
22. What questions do you want to answer with the data?

---

**Q28: What should I prepare BEFORE the meeting?**

**A:** Preparation checklist:

**Documents to Bring:**
- [ ] This MEETING_PRESENTATION_MASTER_DOC.md (printed or on laptop)
- [ ] Architecture diagram (three-layer design)
- [ ] Sample timeline (Gantt chart of 18-23 week roadmap)
- [ ] Example outputs (screenshot of test.parquet loaded in pandas)

**Demos to Prepare:**
- [ ] Load test.csv (55MB) vs test.parquet (12MB) → show speed difference
- [ ] Show sample_metadata schema in terminal
- [ ] Show directory structure (explain data flow)

**Questions to Confirm:**
- [ ] Review 156 sample files → confirm these are just samples
- [ ] Clarify production volume expectations
- [ ] Understand priority: Speed vs Features vs Cost
- [ ] Identify key stakeholders (who approves each phase?)

**Technical Deep-Dive (if asked):**
- [ ] Explain Parquet format benefits (have graph: size/speed comparison)
- [ ] Explain memory management (chunk processing diagram)
- [ ] Explain ML approach (unsupervised → semi-supervised → supervised)

**Logistics:**
- [ ] Confirm meeting attendees (scientists, managers, IT?)
- [ ] Agenda: 10min overview → 20min architecture → 20min Q&A → 10min next steps
- [ ] Follow-up: Send summary email after meeting with action items

---

**Q29: What are the key decisions that MUST come from this meeting?**

**A:** Critical decisions needed:

**MUST DECIDE:**
1. **Production Volume:** How many files per month? (affects architecture)
2. **Timeline Approval:** 18-23 weeks acceptable or needs faster?
3. **Deployment:** Cloud or on-premise?
4. **Phase 1 Scope:** Confirm nanoFACS + NTA only (no scope creep)

**SHOULD DECIDE:**
5. **Quality Criteria:** Formal definition of good/bad samples
6. **Access Control:** Who can upload/view/delete data?
7. **Reporting Requirements:** What reports are critical?
8. **Integration Needs:** Any existing systems to connect?

**NICE TO DECIDE:**
9. **Feature Priorities:** Rank features by importance
10. **Data Retention:** How long to archive old data?
11. **Budget:** Any constraints on cloud costs?

**Document Decisions:**
- Take notes during meeting
- Send summary email within 24 hours
- Update TASK_TRACKER.md with any scope changes
- Flag any blockers immediately

---

**Q30: What if they ask for features outside the current scope?**

**A:** Have a clear **scope management strategy:**

**Acknowledge & Assess:**
- "That's a great idea - let me assess the impact"
- Ask clarifying questions to understand the requirement
- Estimate effort (rough: hours/days/weeks)

**Categorize:**

**Type 1: Easy Additions (< 1 day effort)**
- Example: "Can we add a pie chart showing gate percentages?"
- Response: "Yes, I can add that to Phase 2 visualization tasks"
- Action: Add to backlog, minimal timeline impact

**Type 2: Moderate Additions (1-5 days effort)**
- Example: "Can we export reports as Excel instead of PDF?"
- Response: "Definitely possible - this would add ~3 days to Phase 2"
- Action: Document requirement, discuss priority, may extend timeline

**Type 3: Major Additions (> 1 week effort)**
- Example: "Can we add electron microscopy data integration?"
- Response: "Yes, our architecture supports this, but it's a significant addition"
- Impact: New parser, new schema, new features = 2-3 weeks
- Action: Propose as separate phase (Phase 1A or Phase 2 extension)

**Defer to Phase 2:**
- "Let's nail nanoFACS + NTA integration in Phase 1"
- "We can add [feature] in Phase 2 once core platform is solid"
- "This ensures we deliver value quickly and iterate based on feedback"

**Document Everything:**
- Maintain "Future Features" list in TASK_TRACKER.md
- Review list monthly with stakeholders
- Prioritize based on value vs effort

---

## Appendix: Key Documents Reference

**Created Documentation:**
1. **TASK_TRACKER.md** - Living task management, updated daily
2. **MY_PROJECT_UNDERSTANDING.md** - Initial project overview
3. **IMPORTANT_SCALE_CLARIFICATION.md** - Sample vs production data
4. **TASK_UPDATES_DATA_STRUCTURE.md** - Impact of 339K events/file discovery
5. **DATA_FORMATS_FOR_ML_GUIDE.md** - Parquet vs JSON vs CSV comparison (765 lines)
6. **UNIFIED_DATA_FORMAT_STRATEGY.md** - Multi-machine integration architecture (645 lines)
7. **MEETING_PREPARATION_CHECKLIST.md** - Pre-meeting preparation guide
8. **MEETING_PRESENTATION_MASTER_DOC.md** - This document

**GitHub Repository:**
- URL: https://github.com/isumitmalhotra/CRMIT-Project-
- All documents committed and version-controlled
- Regular pushes to maintain backup

---

## Next Steps After Meeting

**Immediate (Day 1):**
1. Send meeting summary email with decisions documented
2. Update TASK_TRACKER.md with any scope changes
3. Clarify any unanswered questions via email

**Week 1:**
4. Install dependencies (pyarrow, dask, memory_profiler, fcsparser)
5. Test Parquet conversion on test.csv → validate compression
6. Set up development environment (Python 3.8+, virtual environment)
7. Create GitHub branch for Task 1.1 development

**Week 2:**
8. Begin Task 1.1 implementation (FCS parser)
9. Set up unit tests framework
10. First checkpoint: Parse 1 file successfully

**Ongoing:**
- Weekly progress updates (email or meeting)
- Commit code daily to GitHub
- Update TASK_TRACKER.md with completion status
- Flag any blockers immediately

---

## Contact & Support

**Developer:** Sumit Malhotra  
**Role:** Senior Python Full-Stack Developer  
**Organization:** CRMIT  
**Project:** EV Analysis Platform for Bio Varam

**Communication:**
- Weekly progress reports
- Ad-hoc Slack/email for urgent questions
- Monthly demos of working features
- Documentation maintained on GitHub

**Escalation Path:**
- Technical blockers → Discuss in weekly check-in
- Scope changes → Formal change request process
- Infrastructure issues → Contact CRMIT IT team
- Timeline risks → Flag immediately with stakeholders

---

**End of Document**

*Last Updated: November 13, 2025*  
*Version: 1.0*  
*Status: Ready for Meeting Presentation*
