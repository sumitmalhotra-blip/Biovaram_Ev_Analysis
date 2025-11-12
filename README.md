# 🧬 CRMIT Exosome/EV Analysis Project

**Comprehensive Data Analysis Platform for Extracellular Vesicle Characterization**

[![Project Status](https://img.shields.io/badge/Status-Active-success)]()
[![Phase](https://img.shields.io/badge/Phase-1%3A%20Data%20Processing-blue)]()
[![Progress](https://img.shields.io/badge/Progress-5%25-yellow)]()

---

## 📖 Project Overview

This project develops an **end-to-end automated pipeline** for analyzing Extracellular Vesicles (EVs/Exosomes) using:
- **nanoFACS** (nano Flow Cytometry Analysis)
- **NTA** (Nanoparticle Tracking Analysis)

**Client:** Bio Varam via CRMIT  
**Application:** iPSC-derived exosome characterization for therapeutic development

---

## 📁 Repository Structure

```
├── 📄 PROJECT_ANALYSIS.md          # Comprehensive project documentation
├── 📋 TASK_TRACKER.md              # Task tracking and progress monitoring
├── 📚 Literature/                  # Scientific references and standards
│   ├── FCMPASS_Software-Aids-EVs-Light-Scatter-Stand.pdf
│   ├── Mie functions_scattering_Abs-V1.pdf
│   └── Mie functions_scattering_Abs-V2.pdf
├── 🔬 nanoFACS/                    # Flow cytometry data (FCS files)
│   ├── 10000 exo and cd81/         # CD81 antibody titration (21 files)
│   ├── CD9 and exosome lots/       # CD9 testing + lot variability (24 files)
│   └── EXP 6-10-2025/              # Dilution series experiment (25 files)
├── 📊 NTA/                         # Nanoparticle tracking data (TXT files)
│   ├── EV_IPSC_P1_19_2_25_NTA/     # Passage 1 (27 files)
│   ├── EV_IPSC_P2_27_2_25_NTA/     # Passage 2 (28 files)
│   ├── EV_IPSC_P2.1_28_2_25_NTA/   # Passage 2.1 (31 files)
│   └── Dataset 1.xlsx              # Consolidated NTA results
└── 💻 Project IT data/              # Analysis scripts and processed data
    ├── Take path and meta convert to csv.py  # FCS parser (existing)
    ├── metatest.csv                # Sample metadata output
    ├── test.csv                    # Sample event data
    └── Technical documentation/
```

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
Git
```

### Installation
```bash
# Clone the repository
git clone https://github.com/isumitmalhotra/CRMIT-Project-.git
cd CRMIT-Project-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (coming soon)
pip install -r requirements.txt
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md)** | Complete project scope, methodology, and technical details |
| **[TASK_TRACKER.md](TASK_TRACKER.md)** | Real-time task status and progress tracking |
| `docs/` (Coming Soon) | Technical guides, API docs, user manuals |

---

## 🎯 Project Phases

### ✅ Phase 0: Setup & Planning (COMPLETE)
- [x] Repository setup
- [x] Data organization
- [x] Comprehensive documentation

### 🟡 Phase 1: Data Processing (IN PROGRESS - 10%)
- [ ] Enhanced FCS batch parser
- [ ] NTA data parser
- [ ] Data integration pipeline

### ⏳ Phase 2: Analysis & Visualization (NOT STARTED)
- [ ] Exploratory data analysis
- [ ] Interactive dashboard
- [ ] Quality control module

### ⏳ Phase 3: Machine Learning (NOT STARTED)
- [ ] Predictive models
- [ ] Pattern recognition
- [ ] Anomaly detection

### ⏳ Phase 4: Deployment (PLANNING)
- [ ] Automated pipeline
- [ ] Web application & API
- [ ] Production deployment

---

## 📊 Current Data Assets

### Flow Cytometry Data (nanoFACS)
- **70 FCS files** across 3 experimental batches
- **26 parameters** per sample (FSC, SSC, 6 fluorescence channels)
- **Experiments:** CD81/CD9 antibody optimization, method comparison

### Nanoparticle Tracking (NTA)
- **86 TXT files** across 3 passages (P1, P2, P2.1)
- **Size distribution** and **concentration** measurements
- **11-position scanning** for spatial uniformity

---

## 🔬 Key Scientific Questions

1. ❓ What is the optimal antibody concentration for CD81 and CD9?
2. ❓ Which preparation method is better (SEC vs Centrifugation)?
3. ❓ How consistent are EVs across different cell passages?
4. ❓ What are the ideal dilution factors for each assay?
5. ❓ Can we predict EV quality from early measurements?

---

## 🛠️ Technology Stack

**Languages:** Python 3.8+, SQL  
**Data Processing:** pandas, numpy, fcsparser, scipy  
**Visualization:** matplotlib, seaborn, plotly  
**Dashboard:** Dash / Streamlit  
**ML/AI:** scikit-learn, XGBoost  
**Web:** FastAPI / Flask  
**Deployment:** Docker, Git

---

## 📈 Progress Tracking

**Overall Progress:** 5%

| Phase | Progress |
|-------|----------|
| Phase 1: Data Processing | 🟡🟡⚪⚪⚪⚪⚪⚪⚪⚪ 10% |
| Phase 2: Analysis | ⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪ 0% |
| Phase 3: ML & Analytics | ⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪ 0% |
| Phase 4: Deployment | 🟡🟡⚪⚪⚪⚪⚪⚪⚪⚪ 10% |

**Last Updated:** November 12, 2025

For detailed task status, see [TASK_TRACKER.md](TASK_TRACKER.md)

---

## 🤝 Contributing

This is a client project for CRMIT/Bio Varam. For questions or collaboration:
- Review [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md) for technical details
- Check [TASK_TRACKER.md](TASK_TRACKER.md) for current priorities
- Submit issues or pull requests

---

## 📝 Changelog

### [0.2.0] - 2025-11-12
- Added comprehensive PROJECT_ANALYSIS.md
- Added TASK_TRACKER.md for progress monitoring
- Added README.md

### [0.1.0] - 2025-11-12
- Initial repository setup
- Committed all project data (206 files)
- Organized folder structure

---

## 📞 Contact

**Project Repository:** https://github.com/isumitmalhotra/CRMIT-Project-  
**Client:** Bio Varam via CRMIT  
**Data Scientist:** AI Solution Architect

---

## ⚠️ Important Notes

- **Large Files:** Some data files exceed 50MB. Consider Git LFS for future additions.
- **Data Privacy:** Ensure compliance with data handling protocols.
- **Active Development:** This project is under active development.

---

## 📄 License

Proprietary - CRMIT/Bio Varam Client Project

---

**🔗 Quick Links:**
- [📄 Full Project Analysis](PROJECT_ANALYSIS.md)
- [📋 Task Tracker](TASK_TRACKER.md)
- [🔬 Literature](Literature/)
- [📊 nanoFACS Data](nanoFACS/)
- [📈 NTA Data](NTA/)

---

*For the most up-to-date information, always refer to PROJECT_ANALYSIS.md and TASK_TRACKER.md*
