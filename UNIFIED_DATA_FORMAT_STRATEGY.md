# 🔄 Standardized Data Format Strategy: Multi-Machine Integration

**Date:** November 13, 2025  
**Topic:** Should we standardize data from nanoFACS and NTA, or use different formats?

---

## 🎯 **Short Answer: YES - Create ONE Unified Format**

**You MUST create a standardized format that combines both machines' data!**

---

## 🤔 **Why This Question is Critical**

### **Your Current Situation:**

```
Machine 1: nanoFACS (CytoFLEX nano)
├── Output: FCS files (binary)
├── Data: 339K events × 26 parameters
├── Measures: Size, complexity, fluorescence markers
└── Purpose: Marker expression (CD81, CD9, CD63)

Machine 2: NTA (ZetaView)
├── Output: TXT files (text)
├── Data: Size distributions, concentrations
├── Measures: Particle size (nm), count (particles/mL)
└── Purpose: Size distribution, purity assessment
```

**Problem:** Two completely different data structures measuring the SAME samples!

---

## ❌ **Option 1: Keep Them Separate (BAD IDEA)**

### **If you DON'T standardize:**

```
Project Structure (Separate):
├── nanoFACS_data/
│   ├── events/*.parquet          # 26 parameters per event
│   ├── statistics/*.parquet      # nanoFACS-specific stats
│   └── metadata/*.csv            # nanoFACS metadata
│
└── NTA_data/
    ├── distributions/*.parquet   # Size distribution data
    ├── concentrations/*.parquet  # Particle counts
    └── metadata/*.csv            # NTA metadata
    
# Two parallel systems, no connection! ❌
```

### **Problems with Separate Approach:**

❌ **Cannot correlate results**
```python
# How do you compare these?
nanoFACS: "Sample L5+F10 has 85% CD81+ events"
NTA:      "Sample L5+F10 has mean size 120nm"

# They're the same sample but stored separately!
# You'd need to manually match them every time
```

❌ **Duplicate metadata**
```python
# Store same info twice:
nanoFACS metadata: sample_name, passage, fraction, date
NTA metadata:      sample_name, passage, fraction, date
# Same data, two places → inconsistencies!
```

❌ **Complex analysis**
```python
# To analyze one sample, load from TWO places:
fcs_data = load_nanofacs_data('L5+F10')
nta_data = load_nta_data('L5+F10')

# Then manually merge:
combined = merge_somehow(fcs_data, nta_data)  # How?!
```

❌ **ML nightmare**
```python
# Training ML model on BOTH measurements:
features_fcs = extract_features_nanofacs(fcs_data)  # 300 features
features_nta = extract_features_nta(nta_data)       # 50 features

# How to combine for training?
# Different sample IDs? Different timestamps?
# Matching nightmare! 😱
```

❌ **Duplicate work**
- Write two parsers
- Two storage systems
- Two APIs
- Two dashboards
- Two sets of documentation

---

## ✅ **Option 2: Unified Standardized Format (BEST APPROACH)**

### **Create ONE master format that combines both:**

```
Project Structure (Unified):
├── unified_data/
│   ├── samples/
│   │   ├── sample_metadata.parquet        # ← Master sample registry
│   │   └── experimental_conditions.parquet
│   │
│   ├── measurements/
│   │   ├── nanofacs/
│   │   │   ├── events/*.parquet           # Raw nanoFACS events
│   │   │   └── statistics/*.parquet       # Pre-calculated stats
│   │   │
│   │   └── nta/
│   │       ├── distributions/*.parquet    # Size distributions
│   │       └── summary/*.parquet          # Concentration, D50, etc.
│   │
│   └── integrated/
│       ├── combined_features.parquet      # ← Both machines, one file!
│       └── ml_ready_dataset.parquet       # ← Ready for ML training
│
# Everything linked by unique sample_id! ✅
```

---

## 🏗️ **Recommended Unified Data Model**

### **Core Concept: Three-Layer Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              LAYER 1: SAMPLE REGISTRY (Master)              │
│                                                             │
│  sample_metadata.parquet                                    │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ sample_id | name      | passage | fraction | lot | ... │ │
│  │ S001      | L5+F10    | P2      | F10      | L5  | ... │ │
│  │ S002      | L5+F16    | P2      | F16      | L5  | ... │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ↓ Links to both machines via sample_id                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         LAYER 2: MACHINE-SPECIFIC MEASUREMENTS              │
│                                                             │
│  nanoFACS Statistics:                                       │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ sample_id | mean_FSC | mean_SSC | pct_CD81+ | ...     │ │
│  │ S001      | 1250.5   | 890.3    | 85.2%     | ...     │ │
│  │ S002      | 1180.2   | 920.1    | 78.5%     | ...     │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  NTA Statistics:                                            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ sample_id | D50_nm | conc_particles_ml | CV%  | ...   │ │
│  │ S001      | 120.5  | 2.5e11            | 12.3 | ...   │ │
│  │ S002      | 115.8  | 3.1e11            | 10.5 | ...   │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            LAYER 3: INTEGRATED ANALYSIS                     │
│                                                             │
│  combined_features.parquet (ML-ready):                      │
│  ┌────────────────────────────────────────────────────────┐│
│  │ sample_id | mean_FSC | pct_CD81+ | D50_nm | conc | ... ││
│  │ S001      | 1250.5   | 85.2%     | 120.5  | 2.5e11| ...││
│  │ S002      | 1180.2   | 78.5%     | 115.8  | 3.1e11| ...││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  ↑ All features from BOTH machines in ONE row per sample!  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 **Detailed Schema Design**

### **Schema 1: Sample Metadata (Master Registry)**

**File:** `unified_data/samples/sample_metadata.parquet`

```python
import pandas as pd

sample_metadata = pd.DataFrame({
    'sample_id': ['S001', 'S002', 'S003', ...],  # Unique ID (PRIMARY KEY)
    'sample_name': ['L5+F10', 'L5+F16', 'Lot1media+cd9', ...],
    'experiment_date': ['2025-10-09', '2025-10-09', ...],
    'passage': ['P2', 'P2', 'P1', ...],
    'fraction': ['F10', 'F16', None, ...],  # None if not applicable
    'lot_number': ['L5', 'L5', 'Lot1', ...],
    'antibody': ['CD81', 'CD81', 'CD9', ...],
    'antibody_conc_ug': [1.0, 1.0, 0.25, ...],
    'purification_method': ['SEC', 'SEC', 'Centri', ...],
    'dilution_factor': [1000, 1000, 1, ...],
    'operator': ['URAT', 'URAT', 'URAT', ...],
    'notes': ['...', '...', '...', ...],
    
    # Machine availability flags
    'has_nanofacs_data': [True, True, False, ...],
    'has_nta_data': [True, True, True, ...],
    
    # Quality flags
    'quality_status': ['Pass', 'Pass', 'Warn', ...],
    'is_control': [False, False, False, ...],
    'control_type': [None, None, None, ...]  # 'blank', 'isotype', 'water'
})
```

**Why this is critical:**
- ✅ **Single source of truth** for sample information
- ✅ **Unique sample_id** links all data
- ✅ **Flags** indicate which machines have data
- ✅ **Quality tracking** in one place

---

### **Schema 2: nanoFACS Statistics**

**File:** `unified_data/measurements/nanofacs/statistics/event_statistics.parquet`

```python
nanofacs_stats = pd.DataFrame({
    'sample_id': ['S001', 'S002', ...],  # FOREIGN KEY → sample_metadata
    'measurement_date': ['2025-10-09 15:37:23', ...],
    'instrument': ['CytoFLEX nano BH46064', ...],
    
    # Event counts
    'total_events': [339392, 285103, ...],
    'acquisition_time_sec': [30.0, 28.5, ...],
    'events_per_second': [11313, 10004, ...],
    
    # FSC/SSC statistics
    'mean_FSC_H': [1250.5, 1180.2, ...],
    'median_FSC_H': [1100.3, 1050.8, ...],
    'std_FSC_H': [850.2, 790.5, ...],
    'mean_SSC_H': [890.3, 920.1, ...],
    'median_SSC_H': [750.5, 780.2, ...],
    
    # Fluorescence markers (all 6 channels)
    'mean_V447_H': [85.2, 78.5, ...],  # FL1
    'mean_B531_H': [65.3, 70.1, ...],  # FL2
    'mean_Y595_H': [78.9, 82.3, ...],  # FL3
    'mean_R670_H': [55.2, 60.8, ...],  # FL4
    'mean_R710_H': [45.8, 50.2, ...],  # FL5
    'mean_R792_H': [38.5, 42.1, ...],  # FL6
    
    # Gating results (calculated during parsing)
    'pct_debris': [15.2, 18.5, ...],
    'pct_ev_gate': [72.3, 68.9, ...],
    'pct_marker_positive': [85.2, 78.5, ...],  # CD81+ or CD9+
    
    # Data quality metrics
    'cv_FSC': [0.68, 0.67, ...],  # Coefficient of variation
    'cv_SSC': [0.52, 0.55, ...],
    'has_anomalies': [False, False, ...],
    'qc_flags': ['', 'Low event count', ...]
})
```

---

### **Schema 3: NTA Statistics**

**File:** `unified_data/measurements/nta/summary/nta_statistics.parquet`

```python
nta_stats = pd.DataFrame({
    'sample_id': ['S001', 'S002', ...],  # FOREIGN KEY → sample_metadata
    'measurement_date': ['2025-02-19', ...],
    'instrument': ['ZetaView 24-1152', ...],
    
    # Size measurements
    'D10_nm': [85.5, 82.3, ...],   # 10th percentile
    'D50_nm': [120.5, 115.8, ...],  # Median (MOST IMPORTANT)
    'D90_nm': [185.2, 178.5, ...],  # 90th percentile
    'mean_size_nm': [125.3, 120.8, ...],
    'mode_size_nm': [110.2, 105.5, ...],
    'std_size_nm': [35.8, 32.5, ...],
    
    # Concentration measurements
    'concentration_particles_ml': [2.5e11, 3.1e11, ...],
    'concentration_std': [2.3e10, 2.8e10, ...],
    'cv_concentration': [0.092, 0.090, ...],
    
    # 11-position uniformity
    'position_count': [11, 11, ...],
    'position_cv': [0.12, 0.10, ...],  # Lower = more uniform
    'uniformity_score': [88.5, 90.2, ...],  # % (higher = better)
    
    # Data quality
    'temperature_C': [25.2, 25.1, ...],
    'pH': [7.4, 7.4, ...],
    'conductivity': [12.5, 12.3, ...],
    'qc_status': ['Pass', 'Pass', ...],
    'qc_flags': ['', '', ...]
})
```

---

### **Schema 4: Integrated Dataset (ML-Ready)**

**File:** `unified_data/integrated/combined_features.parquet`

**This is the GOLD STANDARD file for ML training!**

```python
combined_features = pd.DataFrame({
    # Sample identification (from sample_metadata)
    'sample_id': ['S001', 'S002', ...],
    'sample_name': ['L5+F10', 'L5+F16', ...],
    'passage': ['P2', 'P2', ...],
    'antibody': ['CD81', 'CD81', ...],
    'antibody_conc_ug': [1.0, 1.0, ...],
    'purification_method': ['SEC', 'SEC', ...],
    
    # === nanoFACS Features (300+ features) ===
    # Size/complexity
    'facs_mean_FSC': [1250.5, 1180.2, ...],
    'facs_median_FSC': [1100.3, 1050.8, ...],
    'facs_std_FSC': [850.2, 790.5, ...],
    'facs_mean_SSC': [890.3, 920.1, ...],
    
    # Fluorescence markers
    'facs_mean_V447': [85.2, 78.5, ...],
    'facs_mean_B531': [65.3, 70.1, ...],
    # ... (all 26 parameters × statistics)
    
    # Gating results
    'facs_pct_marker_positive': [85.2, 78.5, ...],
    'facs_pct_ev_gate': [72.3, 68.9, ...],
    
    # === NTA Features (50+ features) ===
    # Size distribution
    'nta_D50_nm': [120.5, 115.8, ...],
    'nta_mean_size': [125.3, 120.8, ...],
    'nta_std_size': [35.8, 32.5, ...],
    
    # Concentration
    'nta_concentration': [2.5e11, 3.1e11, ...],
    'nta_uniformity_score': [88.5, 90.2, ...],
    
    # === Derived/Computed Features ===
    # Cross-machine correlations
    'size_correlation': [0.85, 0.78, ...],  # FSC vs D50 correlation
    'purity_score': [0.92, 0.88, ...],      # Combined metric
    
    # === Labels (for ML) ===
    'quality_label': ['Good', 'Good', 'Bad', ...],  # Classification target
    'quality_score': [0.95, 0.88, 0.45, ...],       # Regression target
})
```

**THIS is what you feed to ML models!** ✅

---

## 💡 **Benefits of Unified Approach**

### **1. Easy Correlation Analysis**

```python
import pandas as pd

# Load integrated dataset
df = pd.read_parquet('unified_data/integrated/combined_features.parquet')

# Correlate nanoFACS and NTA measurements
import seaborn as sns

sns.scatterplot(
    data=df, 
    x='facs_mean_FSC',      # nanoFACS size indicator
    y='nta_D50_nm'          # NTA median size
)
plt.title('Do nanoFACS and NTA agree on particle size?')

# Easy! Both in same DataFrame ✅
```

### **2. Simplified ML Training**

```python
from sklearn.ensemble import RandomForestClassifier

# Load integrated dataset
df = pd.read_parquet('unified_data/integrated/combined_features.parquet')

# Select features from BOTH machines
feature_cols = [col for col in df.columns 
                if col.startswith('facs_') or col.startswith('nta_')]

X = df[feature_cols].values  # All features from both machines!
y = df['quality_label'].values

# Train model on combined data
model = RandomForestClassifier()
model.fit(X, y)

# ONE simple workflow! ✅
```

### **3. Comprehensive Quality Control**

```python
# Check which samples have data from BOTH machines
metadata = pd.read_parquet('unified_data/samples/sample_metadata.parquet')

complete_samples = metadata[
    (metadata['has_nanofacs_data'] == True) & 
    (metadata['has_nta_data'] == True)
]

print(f"Complete samples: {len(complete_samples)}")
print(f"Missing NTA: {(~metadata['has_nta_data']).sum()}")
print(f"Missing nanoFACS: {(~metadata['has_nanofacs_data']).sum()}")

# Easy tracking! ✅
```

### **4. Single API Endpoint**

```python
# FastAPI example
@app.get("/api/sample/{sample_id}")
async def get_sample(sample_id: str):
    # Load from ONE integrated dataset
    df = pd.read_parquet('unified_data/integrated/combined_features.parquet')
    sample = df[df['sample_id'] == sample_id].iloc[0]
    
    return {
        "sample_id": sample_id,
        "sample_name": sample['sample_name'],
        
        # nanoFACS data
        "nanofacs": {
            "mean_FSC": sample['facs_mean_FSC'],
            "pct_marker_positive": sample['facs_pct_marker_positive']
        },
        
        # NTA data
        "nta": {
            "median_size_nm": sample['nta_D50_nm'],
            "concentration": sample['nta_concentration']
        },
        
        # Integrated analysis
        "quality": {
            "label": sample['quality_label'],
            "score": sample['quality_score']
        }
    }
    
# Everything from ONE place! ✅
```

---

## 🔧 **Implementation Strategy**

### **Phase 1: Parse Both Machines Separately (Task 1.1 & 1.2)**

```python
# Task 1.1: nanoFACS Parser
def parse_nanofacs_batch():
    for fcs_file in fcs_files:
        # Parse FCS file
        meta, events = fcsparser.parse(fcs_file)
        
        # Extract sample_id from filename/metadata
        sample_id = generate_sample_id(fcs_file, meta)
        
        # Save raw events
        events.to_parquet(f'measurements/nanofacs/events/{sample_id}.parquet')
        
        # Calculate statistics
        stats = calculate_statistics(events)
        stats['sample_id'] = sample_id
        
        # Append to statistics file
        append_to_parquet(stats, 'measurements/nanofacs/statistics/event_statistics.parquet')

# Task 1.2: NTA Parser
def parse_nta_batch():
    for nta_file in nta_files:
        # Parse NTA text file
        data = parse_nta_file(nta_file)
        
        # Extract sample_id
        sample_id = generate_sample_id(nta_file, data)
        
        # Save distribution
        data.to_parquet(f'measurements/nta/distributions/{sample_id}.parquet')
        
        # Calculate statistics
        stats = calculate_nta_statistics(data)
        stats['sample_id'] = sample_id
        
        # Append to statistics file
        append_to_parquet(stats, 'measurements/nta/summary/nta_statistics.parquet')
```

### **Phase 2: Create Unified Registry (Task 1.3)**

```python
# Task 1.3: Data Integration
def create_sample_registry():
    # Scan all processed files
    nanofacs_samples = get_nanofacs_sample_ids()
    nta_samples = get_nta_sample_ids()
    
    # Create master sample list
    all_samples = set(nanofacs_samples + nta_samples)
    
    metadata = []
    for sample_id in all_samples:
        # Extract metadata from filenames/original files
        meta = extract_sample_metadata(sample_id)
        
        # Add flags
        meta['has_nanofacs_data'] = sample_id in nanofacs_samples
        meta['has_nta_data'] = sample_id in nta_samples
        
        metadata.append(meta)
    
    # Save master registry
    df = pd.DataFrame(metadata)
    df.to_parquet('unified_data/samples/sample_metadata.parquet')
```

### **Phase 3: Merge for ML (Task 1.3 continued)**

```python
def create_integrated_dataset():
    # Load all statistics
    metadata = pd.read_parquet('samples/sample_metadata.parquet')
    nanofacs = pd.read_parquet('measurements/nanofacs/statistics/event_statistics.parquet')
    nta = pd.read_parquet('measurements/nta/summary/nta_statistics.parquet')
    
    # Merge on sample_id
    combined = metadata.merge(nanofacs, on='sample_id', how='left', suffixes=('', '_facs'))
    combined = combined.merge(nta, on='sample_id', how='left', suffixes=('', '_nta'))
    
    # Rename columns for clarity
    combined = combined.rename(columns={
        'mean_FSC_H': 'facs_mean_FSC',
        'D50_nm': 'nta_D50_nm',
        # ... rename all columns
    })
    
    # Calculate derived features
    combined['size_correlation'] = calculate_correlation(
        combined['facs_mean_FSC'], 
        combined['nta_D50_nm']
    )
    
    # Add quality labels
    combined['quality_label'] = assign_quality_labels(combined)
    
    # Save ML-ready dataset
    combined.to_parquet('unified_data/integrated/combined_features.parquet')
```

---

## 📊 **File Organization Summary**

### **Complete Directory Structure:**

```
unified_data/
├── samples/
│   ├── sample_metadata.parquet          ← Master registry
│   └── experimental_conditions.parquet
│
├── measurements/
│   ├── nanofacs/
│   │   ├── events/
│   │   │   ├── S001.parquet             ← 339K events each
│   │   │   ├── S002.parquet
│   │   │   └── ...
│   │   └── statistics/
│   │       └── event_statistics.parquet  ← Summary stats
│   │
│   └── nta/
│       ├── distributions/
│       │   ├── S001.parquet             ← Size distribution curves
│       │   ├── S002.parquet
│       │   └── ...
│       └── summary/
│           └── nta_statistics.parquet    ← Summary stats
│
└── integrated/
    ├── combined_features.parquet        ← ML-ready (BOTH machines)
    ├── quality_labels.parquet
    └── correlation_analysis.parquet
```

---

## ✅ **Final Recommendation**

### **DO THIS (Standardized Unified Format):**

1. ✅ **Create master sample registry** with unique `sample_id`
2. ✅ **Parse both machines** to separate folders (machine-specific formats OK initially)
3. ✅ **Extract statistics** from both into standardized Parquet files
4. ✅ **Merge into integrated dataset** using `sample_id` as key
5. ✅ **Use integrated dataset** for ML, dashboards, reports

### **Format Summary:**

| Data Type | Format | Why |
|-----------|--------|-----|
| **Sample metadata** | Parquet | Small, shared across all machines |
| **nanoFACS events** | Parquet | Large (339K rows), machine-specific |
| **nanoFACS statistics** | Parquet | Standardized schema |
| **NTA distributions** | Parquet | Machine-specific format |
| **NTA statistics** | Parquet | Standardized schema |
| **Integrated ML data** | Parquet | **BOTH machines, ONE file** ✅ |

---

## 🎯 **Key Principle:**

> **"Parse machine-specific, Store standardized, Integrate for analysis"**

- Parse each machine in its native format
- Convert to standardized Parquet with common schema
- Link everything via `sample_id`
- Create integrated datasets for ML/analysis

**This gives you flexibility + consistency + power!** 🚀

