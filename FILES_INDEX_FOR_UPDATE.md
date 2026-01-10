# 📋 Files Index - Scholar Field Classifier Extension
**Mục đích:** Reference nhanh các file đã tạo/sửa để update sau này
**Lưu ý:** KHÔNG list files trong `data/` vì quá dài (hàng triệu dòng)

---

## 🔴 CORE FILES - CẦN CHÚ Ý KHI UPDATE

### **Extension Configuration**
```
scholar_extention_trung/
├── manifest.json                    # ⚠️ Extension config - đã update name, ID, thêm impact_factors.js
├── popup.html                       # ⚠️ Popup UI - đã đổi branding
├── options.html                     # ⚠️ Settings page - thêm 2 checkboxes mới
└── background.js                    # Không đổi
```

### **JavaScript - Modified Files**
```
scholar_extention_trung/js/
├── scholar.js                       # ⚠️ ĐÃ SỬA - thêm field detection logic
├── fetchRank.js                     # ⚠️ ĐÃ SỬA - thêm detectedField parameter
├── ccf.js                          # ⚠️ ĐÃ SỬA - thêm IF display functions
├── fieldDetector.js                # ✅ MỚI - Client-side field detection
├── fieldDetector_example.html      # ✅ MỚI - Test page cho fieldDetector
└── fieldDetector_test.js           # ✅ MỚI - Browser test script
```

**Chi tiết sửa đổi trong scholar.js:**
- Lines 11-79: Field detection infrastructure
- Lines 94-122: Field detection trong CircumventCrossRef()
- Lines 140-145: Initialize field detection trong scholar.run()

**Chi tiết sửa đổi trong fetchRank.js:**
- Lines 9-18: Thêm detectedField parameter
- Lines 117-118, 206-207: Pass field to getRankSpan

**Chi tiết sửa đổi trong ccf.js:**
- Thêm ccf.getImpactFactor()
- Thêm ccf.getIFColorClass()
- Thêm ccf.getIFSpan()
- Sửa ccf.getRankSpan() để integrate IF badge

### **CSS - Modified Files**
```
scholar_extention_trung/css/
└── style.css                       # ⚠️ ĐÃ SỬA - thêm IF badge styles (.if-badge, color classes)
```

---

## 🟢 PYTHON SCRIPTS - Backend Data Processing

### **Core Modules (utils/)**
```
scholar_extention_trung/utils/
├── journalListAggregator.py        # ✅ MỚI - Fetch journals từ OpenAlex/Crossref
├── fieldClassifier.py              # ✅ MỚI - OECD field classification
├── impactFactorCollector.py        # ✅ MỚI - Collect Impact Factor từ SJR/OpenAlex
├── collect_natural_sciences_data.py # ✅ MỚI - Orchestrator cho Natural Sciences
├── convert_to_js.py                # ✅ MỚI - Convert CSV → JavaScript
├── download_sjr_data.py            # ✅ MỚI - Helper download SJR data
└── quickstart.sh                   # ✅ MỚI - Bash convenience script
```

**Chức năng:**
- `journalListAggregator.py`: OpenAlexAPI, CrossrefAPI, JournalAggregator classes (644 lines)
- `fieldClassifier.py`: FieldClassifier class, OECD schema, 600+ keywords (822 lines)
- `impactFactorCollector.py`: SJRDataLoader, OpenAlexMetrics, ImpactFactorCollector (1,696 lines)
- `collect_natural_sciences_data.py`: Main orchestrator, collects Physics/Chem/Bio/Math journals
- `convert_to_js.py`: Đọc CSV → export JS format cho extension
- `download_sjr_data.py`: Check/validate SJR CSV file
- `quickstart.sh`: Wrapper commands (verify, test, collect, convert)

### **Test Files (utils/)**
```
scholar_extention_trung/utils/
├── test_journalListAggregator.py   # ✅ Unit tests cho journalListAggregator
├── test_fieldClassifier.py         # ✅ Unit tests cho fieldClassifier (65 tests)
├── test_impactFactorCollector.py   # ✅ Unit tests cho impactFactorCollector
├── example_journal_aggregator.py   # ✅ Usage examples
├── example_fieldClassifier.py      # ✅ Usage examples (10 examples)
├── example_impact_factor_collector.py # ✅ Usage examples
├── example_natural_sciences_collection.py # ✅ Quick test script
└── verify_installation.py          # ✅ Verify Python env setup
```

### **Original Python Files (giữ nguyên)**
```
scholar_extention_trung/utils/
├── __init__.py                     # Không đổi
├── read_vhb_ranks.py               # Không đổi (original)
└── save_file.py                    # Không đổi (original)
```

---

## 🟡 DOCUMENTATION FILES

### **Main Documentation**
```
scholar_extention_trung/
├── IMPLEMENTATION_PLAN.md          # ✅ MỚI - Kế hoạch chi tiết ban đầu (Opus plan)
├── IMPLEMENTATION_COMPLETE.md      # ✅ MỚI - Summary hoàn thành
├── FILES_INDEX_FOR_UPDATE.md       # ✅ MỚI - File này
├── README_DEVELOPMENT.md           # ✅ MỚI - Dev setup guide
├── requirements.txt                # ✅ MỚI - Python dependencies
└── .gitignore                      # ✅ MỚI - Git ignore rules
```

### **Module Documentation (utils/)**
```
scholar_extention_trung/utils/
├── README_journalListAggregator.md           # ✅ API docs cho journalListAggregator
├── README_fieldClassifier.md                 # ✅ API docs cho fieldClassifier (814 lines)
├── README_impactFactorCollector.md           # ✅ API docs cho impactFactorCollector
├── README_NATURAL_SCIENCES.md                # ✅ Natural sciences collection guide
├── QUICK_REFERENCE.txt                       # ✅ Quick reference card
├── QUICK_REFERENCE_impactFactorCollector.txt # ✅ Quick reference cho IF collector
├── ARCHITECTURE_DIAGRAM.txt                  # ✅ System architecture
├── ARCHITECTURE_DIAGRAM_impactFactorCollector.txt # ✅ IF collector architecture
├── IMPLEMENTATION_SUMMARY.md                 # ✅ Implementation summary
├── IMPLEMENTATION_SUMMARY_impactFactorCollector.md # ✅ IF implementation summary
├── IMPLEMENTATION_CHECKLIST.md               # ✅ Task checklist
└── FILE_INDEX_impactFactorCollector.txt      # ✅ File navigation
```

### **JavaScript Documentation (js/)**
```
scholar_extention_trung/js/
├── FIELDDETECTOR_README.md         # ✅ FieldDetector API reference
├── FIELDDETECTOR_INTEGRATION.md    # ✅ Integration guide
├── FIELDDETECTOR_SUMMARY.md        # ✅ Implementation summary
├── IMPACT_FACTOR_IMPLEMENTATION.md # ✅ IF implementation details
├── IMPACT_FACTOR_VISUAL_GUIDE.md   # ✅ Visual guide cho IF display
└── TESTING_GUIDE.md                # ✅ Testing instructions
```

---

## 🔵 DATA FILES - CẤU TRÚC (KHÔNG LIST NỘI DUNG)

### **Data Structure (QUAN TRỌNG)**
```
scholar_extention_trung/data/
├── fields/                         # ✅ MỚI - Field-organized data (empty, ready for data)
│   ├── natural_sciences/           # Sẽ chứa physics.js, chemistry.js, biology.js, math.js
│   ├── engineering/                # Reserved for future
│   ├── social_sciences/            # Reserved for future
│   └── humanities/                 # Reserved for future
├── rankings/                       # ✅ MỚI - Ranking data
│   ├── impact_factors.js           # ✅ MỚI - IF data (10 sample journals)
│   └── README.md                   # ✅ MỚI - IF data documentation
├── raw/                            # ✅ MỚI - Raw data storage (for CSV downloads)
│   └── (put scimagojr.csv here)
├── processed/                      # ✅ MỚI - Processed CSV files (output from Python scripts)
│   └── (physics_journals.csv, chemistry_journals.csv, etc.)
├── legacy/                         # ✅ MỚI - Original data (copied from base extension)
│   ├── names/                      # Original ccf.*.js files
│   └── issns/                      # Original ccf.issn*.js files
├── names/                          # Giữ nguyên (original extension data)
│   └── ccf.*.js                    # ⚠️ KHÔNG ĐỌC - quá lớn (1.4MB/file)
├── issns/                          # Giữ nguyên (original extension data)
│   └── ccf.issn*.js                # ⚠️ KHÔNG ĐỌC - quá lớn (770KB/file)
└── ccf.FullRank_Acro.js            # Giữ nguyên (original)
```

**⚠️ LƯU Ý:**
- KHÔNG đọc/list files trong `data/names/` và `data/issns/` vì mỗi file có hàng triệu columns
- Chỉ cần biết structure, không cần nội dung
- Khi update, dùng Python scripts để generate, KHÔNG edit manual

---

## 🟣 WORKFLOW UPDATE - HƯỚNG DẪN

### **Khi cần update journal data:**

1. **Download SJR data mới:**
   ```bash
   # Manual download từ https://www.scimagojr.com/journalrank.php
   # Save to: scholar_extention_trung/data/raw/scimagojr.csv
   ```

2. **Run data collection:**
   ```bash
   cd scholar_extention_trung/utils
   python collect_natural_sciences_data.py --email your@email.com --sjr-csv ../data/raw/scimagojr.csv
   ```

3. **Convert to JS:**
   ```bash
   python convert_to_js.py
   ```

4. **Update impact_factors.js:**
   - Edit: `data/rankings/impact_factors.js`
   - Add new journals manually hoặc run Python script

### **Khi cần sửa field detection logic:**

1. **Backend (Python):**
   - File: `utils/fieldClassifier.py`
   - Update keywords trong `FIELD_KEYWORDS` dict (lines 50-150)
   - Run tests: `python test_fieldClassifier.py`

2. **Frontend (JavaScript):**
   - File: `js/fieldDetector.js`
   - Update patterns trong `this.fieldPatterns` (lines 50-100)
   - Test: Open `js/fieldDetector_example.html` in browser

### **Khi cần thêm/sửa IF display:**

1. **Data:**
   - File: `data/rankings/impact_factors.js`
   - Format: `sfc.impactFactors = {"ISSN": {value, year, source, quartile, h_index}}`

2. **Display logic:**
   - File: `js/ccf.js`
   - Functions: `ccf.getIFSpan()`, `ccf.getIFColorClass()`

3. **Styling:**
   - File: `css/style.css`
   - Classes: `.if-badge`, `.if-excellent`, `.if-verygood`, etc.

### **Khi cần thêm fields mới:**

1. **Python:**
   - File: `utils/fieldClassifier.py`
   - Thêm field vào `OECD_FIELDS` dict
   - Thêm keywords vào `FIELD_KEYWORDS` dict

2. **JavaScript:**
   - File: `js/fieldDetector.js`
   - Thêm pattern vào `this.fieldPatterns` object

3. **Data structure:**
   - Create folder: `data/fields/new_field_category/`
   - Run collection script với field mới

---

## 📊 FILE SIZE REFERENCE

| File Category | Count | Total Size | Notes |
|--------------|-------|------------|-------|
| **Modified JS** | 3 files | ~50KB | scholar.js, fetchRank.js, ccf.js |
| **New JS** | 3 files | ~40KB | fieldDetector.js + tests |
| **Python Modules** | 7 files | ~100KB | Core processing scripts |
| **Python Tests** | 7 files | ~60KB | Unit tests + examples |
| **Documentation** | 25+ files | ~300KB | READMEs, guides, summaries |
| **Data files** | N/A | ~25MB+ | KHÔNG list vì quá lớn |

---

## 🔍 QUICK FIND - Tìm file theo mục đích

**Muốn update field detection?**
→ `js/fieldDetector.js` (frontend) + `utils/fieldClassifier.py` (backend)

**Muốn update Impact Factor display?**
→ `js/ccf.js` (functions) + `css/style.css` (styling) + `data/rankings/impact_factors.js` (data)

**Muốn collect thêm journals?**
→ `utils/collect_natural_sciences_data.py` (main) + `utils/journalListAggregator.py` (API)

**Muốn update extension branding?**
→ `manifest.json` + `popup.html` + `options.html`

**Muốn test extension?**
→ `js/fieldDetector_example.html` (browser) + `utils/test_*.py` (Python)

**Muốn đọc documentation?**
→ `IMPLEMENTATION_COMPLETE.md` (overview) + `README_*.md` files

---

## ⚠️ CRITICAL FILES - BACKUP BEFORE MODIFYING

```
✋ LUÔN BACKUP TRƯỚC KHI SỬA:
1. manifest.json          # Extension config
2. js/scholar.js          # Core logic
3. js/fetchRank.js        # API calls
4. js/ccf.js              # Ranking display
5. data/rankings/impact_factors.js  # IF data
```

---

## 📝 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-10 | Initial implementation - All features complete |

---

**Last updated:** 2026-01-10
**Maintained by:** Claude (Sonnet + Haiku team)
**Total files:** 60+ (excluding data files)
