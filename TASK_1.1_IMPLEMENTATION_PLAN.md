# Task 1.1: Enhanced FCS Parser - Implementation Plan

**Created:** November 13, 2025  
**Status:** 🎯 READY FOR APPROVAL  
**Complexity:** HIGH  
**Estimated Duration:** 4-5 days (with testing)

---

## 🎯 Executive Summary

**Goal:** Build production-ready FCS parser that processes 70 files (~24M events) efficiently with baseline workflow support, Parquet output, and AWS S3 integration.

**Philosophy (Tech Leader Mindset):**
- **Zuckerberg's "Move Fast":** Iterative development with quick validation cycles
- **Musk's "First Principles":** Break down into smallest testable components
- **Gates's "Measure Twice":** Extensive testing before scaling to all 70 files

**Success Criteria:**
✅ Parse all 70 FCS files successfully  
✅ Memory usage stays <4 GB  
✅ Processing time <15 minutes (entire batch)  
✅ Baseline detection 100% accurate  
✅ Parquet output 70-80% smaller than CSV  
✅ All metadata correctly extracted  
✅ Zero data loss or corruption  

---

## 📋 Implementation Strategy

### Phase 1: Foundation (Day 1) - "First Principles"
**Goal:** Build smallest working prototype with 1 file

### Phase 2: Core Features (Day 2-3) - "Iterate Fast" 
**Goal:** Add all features, test on 3 files (test_data)

### Phase 3: Scale & Optimize (Day 4) - "Measure Performance"
**Goal:** Process all 70 files, optimize bottlenecks

### Phase 4: Production Ready (Day 5) - "Quality & Documentation"
**Goal:** Testing, error handling, documentation

---

## 🔧 Detailed Subtasks

### ✅ Phase 1: Foundation (Day 1)

#### Subtask 1.1.1: Environment Setup & Validation
**Duration:** 30 minutes  
**Priority:** CRITICAL

**Tasks:**
- [ ] Install core dependencies:
  ```bash
  pip install fcsparser pandas numpy pyarrow tqdm
  ```
- [ ] Test fcsparser on 1 sample file:
  ```python
  import fcsparser
  meta, data = fcsparser.parse('test_data/nanofacs/L5+F10+ISO.fcs')
  print(f"Events: {len(data)}, Parameters: {data.shape[1]}")
  ```
- [ ] Verify memory usage with single file (<500 MB)
- [ ] Test Parquet conversion:
  ```python
  data.to_parquet('test_output.parquet', compression='snappy')
  ```

**Validation Criteria:**
✅ fcsparser loads file without errors  
✅ Correct event count (~339K events)  
✅ All 26 parameters present  
✅ Parquet file created and is 70-80% smaller than CSV  

**Blockers/Questions:**
- ⚠️ **QUESTION:** Do we have Python environment set up? (venv activated?)
- ⚠️ **QUESTION:** Can we install packages or is there a restriction?

---

#### Subtask 1.1.2: Filename Parser - Group 2 Pattern (Test Data)
**Duration:** 1.5 hours  
**Priority:** CRITICAL  
**Dependencies:** 1.1.1

**Goal:** Parse test data filenames (`L5+F10+CD9.fcs`, `L5+F10+ISO.fcs`)

**Implementation:**
```python
# File: scripts/parse_fcs.py
import re
from typing import Dict

def parse_filename_group2(filename: str) -> Dict[str, any]:
    """
    Parse Group 2 pattern: L5+F10+CD9.fcs
    
    Returns:
        {
            'biological_sample_id': 'L5_F10',
            'measurement_id': 'L5_F10_CD9',
            'lot': 5,
            'fraction': 10,
            'antibody': 'CD9',
            'is_baseline': False
        }
    """
    pattern = r'L(\d+)\+F(\d+)\+(.+)\.fcs'
    match = re.match(pattern, filename, re.IGNORECASE)
    
    if not match:
        raise ValueError(f"Filename doesn't match Group 2 pattern: {filename}")
    
    lot = match.group(1)
    fraction = match.group(2)
    antibody = match.group(3)
    
    # Baseline detection
    is_baseline = antibody.upper() in ['ISO', 'ISOTYPE']
    
    biological_sample_id = f"L{lot}_F{fraction}"
    measurement_id = f"{biological_sample_id}_{antibody}"
    
    return {
        'biological_sample_id': biological_sample_id,
        'measurement_id': measurement_id,
        'lot': int(lot),
        'fraction': int(fraction),
        'antibody': antibody,
        'is_baseline': is_baseline,
        'pattern_group': 'group_2'
    }
```

**Test Cases:**
```python
# Test 1: Baseline detection
result = parse_filename_group2('L5+F10+ISO.fcs')
assert result['is_baseline'] == True
assert result['biological_sample_id'] == 'L5_F10'

# Test 2: Test measurement
result = parse_filename_group2('L5+F10+CD9.fcs')
assert result['is_baseline'] == False
assert result['antibody'] == 'CD9'

# Test 3: Same biological sample
iso = parse_filename_group2('L5+F10+ISO.fcs')
cd9 = parse_filename_group2('L5+F10+CD9.fcs')
assert iso['biological_sample_id'] == cd9['biological_sample_id']
```

**Validation Criteria:**
✅ All 3 test files parse correctly  
✅ Baseline detection works (ISO = True, CD9 = False)  
✅ Same biological_sample_id for L5+F10 files  
✅ Unit tests pass  

**Questions:**
- ⚠️ **CONFIRM:** Is baseline detection logic correct? (ISO/ISOTYPE = baseline)
- ⚠️ **CONFIRM:** Should we handle case variations? (iso, ISO, Iso)

---

#### Subtask 1.1.3: Single File Parser - Complete Pipeline
**Duration:** 2 hours  
**Priority:** CRITICAL  
**Dependencies:** 1.1.2

**Goal:** Parse 1 FCS file end-to-end (file → metadata → events → statistics → Parquet)

**Implementation:**
```python
class FCSParser:
    def parse_single_file(self, fcs_path: str, output_dir: str) -> Dict:
        """
        Parse single FCS file and generate all outputs.
        
        Returns:
            {
                'metadata': {...},
                'statistics': {...},
                'events_parquet': 'path/to/events.parquet',
                'status': 'success'
            }
        """
        # 1. Parse filename
        filename = os.path.basename(fcs_path)
        metadata = self.parse_filename(filename, fcs_path)
        
        # 2. Parse FCS file
        fcs_meta, events_df = fcsparser.parse(fcs_path)
        
        # 3. Add metadata to events
        events_df['measurement_id'] = metadata['measurement_id']
        events_df['biological_sample_id'] = metadata['biological_sample_id']
        
        # 4. Calculate statistics
        stats = self.calculate_statistics(events_df, metadata)
        
        # 5. Save events to Parquet
        events_path = os.path.join(output_dir, 'events', f"{metadata['measurement_id']}.parquet")
        events_df.to_parquet(events_path, compression='snappy', index=False)
        
        # 6. Return results
        return {
            'metadata': metadata,
            'statistics': stats,
            'events_parquet': events_path,
            'event_count': len(events_df),
            'file_size_mb': os.path.getsize(events_path) / (1024**2),
            'status': 'success'
        }

    def calculate_statistics(self, events_df: pd.DataFrame, metadata: Dict) -> Dict:
        """Calculate pre-computed statistics for all parameters."""
        stats = {
            'measurement_id': metadata['measurement_id'],
            'biological_sample_id': metadata['biological_sample_id'],
            'is_baseline': metadata['is_baseline'],
            'event_count': len(events_df)
        }
        
        # Calculate mean, median, std for all numeric columns (26 parameters)
        for col in events_df.select_dtypes(include=[np.number]).columns:
            if col not in ['measurement_id', 'biological_sample_id']:
                stats[f'{col}_mean'] = events_df[col].mean()
                stats[f'{col}_median'] = events_df[col].median()
                stats[f'{col}_std'] = events_df[col].std()
                stats[f'{col}_min'] = events_df[col].min()
                stats[f'{col}_max'] = events_df[col].max()
        
        return stats
```

**Test Execution:**
```python
parser = FCSParser()
result = parser.parse_single_file(
    'test_data/nanofacs/L5+F10+ISO.fcs',
    'output/test/'
)

print(f"✅ Events: {result['event_count']}")
print(f"✅ File size: {result['file_size_mb']:.2f} MB")
print(f"✅ Statistics calculated: {len(result['statistics'])} metrics")
```

**Validation Criteria:**
✅ Parses L5+F10+ISO.fcs successfully  
✅ Events Parquet file created  
✅ Statistics calculated (mean, median, std for all 26 params)  
✅ File size 70-80% smaller than CSV equivalent  
✅ No data loss (event count matches original)  

**Questions:**
- ⚠️ **CONFIRM:** Should we store ALL events in Parquet? (339K rows × 26 cols = ~12 MB each)
- ⚠️ **CONFIRM:** Or should we store ONLY statistics and keep raw events separate?
- ⚠️ **QUESTION:** What statistics are most important? (we're calculating 130+ metrics per file)

---

### 🚀 Phase 2: Core Features (Day 2-3)

#### Subtask 1.1.4: Multi-Pattern Filename Parser
**Duration:** 2 hours  
**Priority:** HIGH  
**Dependencies:** 1.1.3

**Goal:** Support all 3 filename patterns (Group 1, 2, 3)

**Implementation:**
```python
def parse_filename(self, filename: str, folder_path: str) -> Dict:
    """
    Auto-detect pattern and parse filename.
    """
    # Detect pattern based on folder or filename structure
    if 'CD9 and exosome lots' in folder_path or re.match(r'L\d+\+F\d+', filename):
        return self.parse_filename_group2(filename)
    
    elif '10000 exo' in folder_path or 'ug' in filename.lower():
        return self.parse_filename_group1(filename)
    
    elif 'EXP' in folder_path:
        return self.parse_filename_group3(filename)
    
    else:
        raise ValueError(f"Unknown filename pattern: {filename}")
```

**Test Coverage:**
- Group 1: `0.25ug ISO SEC.fcs` → EXOSOME_10K
- Group 2: `L5+F10+ISO.fcs` → L5_F10 ✅ (already tested)
- Group 3: `isotype 0.25ug.fcs` → EXP_6_10_2025

**Questions:**
- ⚠️ **QUESTION:** Should we implement all 3 patterns now, or start with Group 2 (test data) and add others later?
- ⚠️ **RECOMMENDATION:** Start with Group 2 (test data available), add others in Phase 3

---

#### Subtask 1.1.5: Batch Processing (3 Files)
**Duration:** 2 hours  
**Priority:** HIGH  
**Dependencies:** 1.1.4

**Goal:** Process all 3 test files, verify baseline grouping

**Implementation:**
```python
def parse_batch(self, file_paths: List[str], output_dir: str) -> pd.DataFrame:
    """
    Parse multiple FCS files and return consolidated statistics.
    """
    results = []
    
    for fcs_path in tqdm(file_paths, desc="Processing FCS files"):
        try:
            result = self.parse_single_file(fcs_path, output_dir)
            results.append(result['statistics'])
        except Exception as e:
            logger.error(f"Failed to parse {fcs_path}: {e}")
            results.append({'status': 'failed', 'error': str(e)})
    
    # Create statistics DataFrame
    stats_df = pd.DataFrame(results)
    
    # Save consolidated statistics
    stats_df.to_parquet(
        os.path.join(output_dir, 'event_statistics.parquet'),
        compression='snappy',
        index=False
    )
    
    return stats_df
```

**Test Execution:**
```python
test_files = [
    'test_data/nanofacs/L5+F10+ISO.fcs',
    'test_data/nanofacs/L5+F10+CD9.fcs',
    'test_data/nanofacs/L5+F10+ONLY EXO.fcs'
]

stats = parser.parse_batch(test_files, 'output/batch_test/')

# Verify baseline grouping
l5_f10_files = stats[stats['biological_sample_id'] == 'L5_F10']
print(f"✅ L5_F10 group has {len(l5_f10_files)} files")
print(f"✅ Baseline: {l5_f10_files[l5_f10_files['is_baseline']]['measurement_id'].values}")
```

**Validation Criteria:**
✅ All 3 test files process successfully  
✅ All have same biological_sample_id (L5_F10)  
✅ 1 baseline detected (ISO)  
✅ Consolidated statistics Parquet created  
✅ Memory usage <500 MB  

---

#### Subtask 1.1.6: Baseline Comparison Calculations
**Duration:** 3 hours  
**Priority:** HIGH  
**Dependencies:** 1.1.5

**Goal:** Calculate deltas between test measurements and baseline

**Implementation:**
```python
def calculate_baseline_comparisons(self, stats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate baseline comparisons for each biological_sample_id group.
    
    For each test measurement:
    - delta = test_value - baseline_value
    - fold_change = test_value / baseline_value
    """
    comparisons = []
    
    # Group by biological_sample_id
    for bio_id, group in stats_df.groupby('biological_sample_id'):
        # Find baseline
        baseline = group[group['is_baseline'] == True]
        
        if len(baseline) == 0:
            logger.warning(f"No baseline found for {bio_id}")
            continue
        
        baseline = baseline.iloc[0]  # Take first if multiple
        
        # Compare each test to baseline
        tests = group[group['is_baseline'] == False]
        
        for _, test in tests.iterrows():
            comparison = {
                'biological_sample_id': bio_id,
                'test_measurement_id': test['measurement_id'],
                'baseline_measurement_id': baseline['measurement_id']
            }
            
            # Calculate deltas for key parameters (example: FSC-A, SSC-A, FL1-A)
            for param in ['FSC-A_mean', 'SSC-A_mean', 'FL1-A_mean']:
                if param in test and param in baseline:
                    test_val = test[param]
                    base_val = baseline[param]
                    
                    comparison[f'{param}_delta'] = test_val - base_val
                    comparison[f'{param}_fold_change'] = test_val / base_val if base_val != 0 else np.nan
                    comparison[f'{param}_pct_change'] = ((test_val - base_val) / base_val * 100) if base_val != 0 else np.nan
            
            comparisons.append(comparison)
    
    return pd.DataFrame(comparisons)
```

**Test Execution:**
```python
# Using stats from previous subtask
baseline_comp = parser.calculate_baseline_comparisons(stats)

print(f"✅ Comparisons calculated: {len(baseline_comp)}")
print(f"✅ Test measurements: {baseline_comp['test_measurement_id'].unique()}")
print(f"✅ Baseline used: {baseline_comp['baseline_measurement_id'].unique()}")

# Example output:
# L5_F10_CD9 vs L5_F10_ISO:
#   FSC-A_mean_delta = +1500
#   FSC-A_mean_fold_change = 1.15
#   FSC-A_mean_pct_change = +15%
```

**Validation Criteria:**
✅ Baseline found for L5_F10  
✅ 2 comparisons created (CD9 vs ISO, ONLY EXO vs ISO)  
✅ Delta, fold_change, pct_change calculated  
✅ No division by zero errors  

**Questions:**
- ⚠️ **QUESTION:** Which parameters should we calculate comparisons for? All 26 or subset?
- ⚠️ **RECOMMENDATION:** Start with key parameters (FSC-A, SSC-A, FL1-A for CD81, FL2-A for CD9), expand later

---

### 📊 Phase 3: Scale & Optimize (Day 4)

#### Subtask 1.1.7: Full Dataset Processing (70 Files)
**Duration:** 2 hours  
**Priority:** CRITICAL  
**Dependencies:** 1.1.6

**Goal:** Process all 70 FCS files across 3 folders

**Implementation:**
```python
# Scan all FCS files
all_fcs_files = []
for folder in ['10000 exo and cd81', 'CD9 and exosome lots', 'EXP 6-10-2025']:
    folder_path = os.path.join('nanoFACS', folder)
    files = glob.glob(os.path.join(folder_path, '*.fcs'))
    all_fcs_files.extend(files)

print(f"Found {len(all_fcs_files)} FCS files")

# Process with progress tracking
stats = parser.parse_batch(all_fcs_files, 'processed_data/')
```

**Monitoring:**
```python
# Track memory usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024**3:.2f} GB")
```

**Validation Criteria:**
✅ All 70 files processed successfully  
✅ Processing time <15 minutes  
✅ Memory usage stays <4 GB  
✅ No crashes or errors  
✅ Output files total ~70 × 12 MB = 840 MB  

**Questions:**
- ⚠️ **QUESTION:** Should we implement parallel processing (multiple files at once) or sequential?
- ⚠️ **RECOMMENDATION:** Start sequential, add parallel only if too slow

---

#### Subtask 1.1.8: Memory Optimization
**Duration:** 2 hours  
**Priority:** MEDIUM  
**Dependencies:** 1.1.7

**Goal:** Ensure memory usage stays under 4 GB

**Techniques:**
```python
# 1. Process files one at a time (already doing this)

# 2. Explicitly delete DataFrames after saving
def parse_single_file(self, fcs_path: str, output_dir: str):
    # ... parsing logic ...
    
    events_df.to_parquet(events_path, ...)
    
    # Free memory immediately
    del events_df
    del fcs_meta
    gc.collect()

# 3. Use chunking if needed (for very large files)
# Currently not needed - 339K events fits in memory
```

**Validation:**
- Monitor memory throughout 70-file batch
- Ensure no memory leaks
- Peak memory <4 GB

---

### ✅ Phase 4: Production Ready (Day 5)

#### Subtask 1.1.9: Error Handling & Validation
**Duration:** 2 hours  
**Priority:** HIGH

**Implementation:**
```python
def validate_fcs_file(self, fcs_path: str) -> Dict:
    """Validate FCS file before processing."""
    validation = {
        'file_exists': os.path.exists(fcs_path),
        'file_readable': os.access(fcs_path, os.R_OK),
        'min_size_kb': os.path.getsize(fcs_path) / 1024 > 100,  # At least 100 KB
        'errors': []
    }
    
    try:
        # Try to parse
        meta, data = fcsparser.parse(fcs_path)
        
        # Validate event count
        if len(data) < 1000:
            validation['errors'].append(f"Low event count: {len(data)}")
        
        # Validate parameters
        if data.shape[1] < 20:
            validation['errors'].append(f"Missing parameters: {data.shape[1]}")
        
        validation['valid'] = len(validation['errors']) == 0
        
    except Exception as e:
        validation['errors'].append(str(e))
        validation['valid'] = False
    
    return validation
```

**Quality Checks:**
- Minimum event count: 1000 events
- Expected parameters: 26 (or close)
- File not corrupted
- Metadata parseable

---

#### Subtask 1.1.10: Unit Tests
**Duration:** 2 hours  
**Priority:** HIGH

**Test Coverage:**
```python
# tests/test_fcs_parser.py

def test_parse_filename_group2():
    """Test filename parsing for Group 2."""
    result = parser.parse_filename_group2('L5+F10+ISO.fcs')
    assert result['biological_sample_id'] == 'L5_F10'
    assert result['is_baseline'] == True

def test_baseline_detection():
    """Test baseline detection."""
    assert parser.is_baseline('ISO') == True
    assert parser.is_baseline('CD9') == False

def test_single_file_parsing():
    """Test complete file parsing."""
    result = parser.parse_single_file('test_data/nanofacs/L5+F10+ISO.fcs', 'output/')
    assert result['status'] == 'success'
    assert result['event_count'] > 1000

def test_batch_processing():
    """Test batch processing."""
    stats = parser.parse_batch(test_files, 'output/')
    assert len(stats) == 3
    
def test_baseline_comparison():
    """Test baseline comparison calculations."""
    comps = parser.calculate_baseline_comparisons(stats)
    assert len(comps) == 2  # 2 tests vs 1 baseline
```

**Run Tests:**
```bash
pytest tests/test_fcs_parser.py -v
```

---

#### Subtask 1.1.11: Documentation
**Duration:** 1 hour  
**Priority:** MEDIUM

**Documents to Create:**
- Code docstrings (already in examples)
- Usage guide: `docs/FCS_PARSER_USAGE.md`
- API reference
- Example scripts

---

## ⚠️ Critical Questions for Approval

Before I start implementing, please confirm:

### 1. **Environment Setup**
- [ ] **CONFIRM:** Python virtual environment is set up and activated?
- [ ] **CONFIRM:** Can I install packages? (`pip install fcsparser pandas pyarrow`)
- [ ] **CONFIRM:** Python version? (Need 3.8+)

### 2. **Data Storage Strategy**
- [ ] **QUESTION:** Should we save ALL 339K events per file to Parquet? (70 files × 12 MB = 840 MB total)
  - **Option A:** Save all events (enables future re-analysis without re-parsing FCS)
  - **Option B:** Save only statistics (smaller footprint, but must re-parse FCS for new analysis)
  - **RECOMMENDATION:** Option A - storage is cheap, re-parsing is expensive

### 3. **Baseline Comparison Parameters**
- [ ] **QUESTION:** Which of the 26 parameters should we calculate baseline comparisons for?
  - **Option A:** All 26 parameters (130+ comparison metrics per test)
  - **Option B:** Key parameters only (FSC-A, SSC-A, FL1-A, FL2-A, FL3-A)
  - **RECOMMENDATION:** Option B initially, expand to Option A if needed

### 4. **Implementation Scope for Week 1**
- [ ] **QUESTION:** Should we implement all 3 filename patterns (Groups 1, 2, 3) or start with Group 2 only?
  - **Option A:** All 3 patterns (full coverage, but longer development)
  - **Option B:** Group 2 only first (faster, can test with available data)
  - **RECOMMENDATION:** Option B - validate approach with test data first

### 5. **AWS S3 Integration**
- [ ] **QUESTION:** Should Task 1.1 include S3 upload/download, or is that separate (Task 1.6)?
  - **Option A:** Include basic S3 upload in Task 1.1
  - **Option B:** Keep Task 1.1 local-only, defer S3 to Task 1.6
  - **RECOMMENDATION:** Option B - keep tasks separate, easier to test

### 6. **Performance vs Features Trade-off**
- [ ] **QUESTION:** Priority: Speed or Features?
  - **Fast approach:** Get basic parsing working, iterate features
  - **Complete approach:** Implement all features upfront, optimize later
  - **RECOMMENDATION:** Fast approach - validate core functionality first

---

## 📊 Development Roadmap (Pending Approval)

### Week 1 (Nov 13-19)
**Days 1-2:** Phase 1 & 2 (Foundation + Core Features with test data)
**Days 3-4:** Phase 3 (Scale to all 70 files)
**Day 5:** Phase 4 (Testing + Documentation)

### Checkpoints
- ✅ **Checkpoint 1 (Day 1 EOD):** Single file parsing works
- ✅ **Checkpoint 2 (Day 2 EOD):** 3 test files process with baseline comparison
- ✅ **Checkpoint 3 (Day 4 EOD):** All 70 files processed successfully
- ✅ **Checkpoint 4 (Day 5 EOD):** Tests pass, documentation complete

---

## 🚀 Next Steps

**Once approved, I will:**

1. **Set up environment** (install dependencies)
2. **Start with Subtask 1.1.1** (validate fcsparser works)
3. **Implement incrementally** (one subtask at a time, validate each)
4. **Show you results** at each checkpoint for feedback
5. **Adjust approach** based on your input

---

## 📝 Questions Summary

Please review and answer these critical questions:

1. ✅ Python environment ready? Can install packages?
2. 🤔 Save all events to Parquet or only statistics?
3. 🤔 Calculate baseline comparisons for all 26 params or subset?
4. 🤔 Implement all 3 filename patterns or Group 2 only first?
5. 🤔 Include S3 in Task 1.1 or keep separate?
6. 🤔 Prefer speed (iterate fast) or completeness (all features upfront)?

**Recommended Answers (for your consideration):**
1. ✅ Yes (will verify)
2. 💾 Save all events (Option A)
3. 📊 Key parameters only initially (Option B)
4. 🎯 Group 2 only first (Option B)
5. 🔄 Keep S3 separate in Task 1.6 (Option B)
6. ⚡ Speed/iteration (Fast approach)

---

**Status:** 🟡 Awaiting your approval and answers to proceed with implementation.

