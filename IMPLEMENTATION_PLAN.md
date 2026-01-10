# Kế hoạch Nâng cấp Extension Scholar - Phiên bản Modified

**Ngày:** 2026-01-10
**Tác giả:** Claude Opus (Plan Mode)
**Mục tiêu:** Tạo phiên bản modified của extension hiện tại, tổ chức theo ngành, bổ sung journal list đầy đủ (đặc biệt cho ngành tự nhiên), và thêm Impact Factor.

---

## Tổng quan Cấu trúc Hiện tại

Extension hiện tại (Rapid Journal Quality Check) hoạt động như sau:

### 1. **Luồng hoạt động:**
- Quét các kết quả tìm kiếm trên Google Scholar
- Trích xuất tên journal từ metadata
- So khớp với database journal rankings (SJR Q, VHB, CCF, ABDC, AJG, CORE, etc.)
- Hiển thị badge màu sắc cho ranking quality

### 2. **Cấu trúc dữ liệu:**
- **Names database**: `data/names/ccf.{RANKING_NAME}.js` - Lookup theo tên journal (normalized)
- **ISSNs database**: `data/issns/ccf.issn{RANKING_NAME}.js` - Lookup theo ISSN
- **Python scripts**: Xử lý và chuyển đổi raw data thành JS format

### 3. **Rankings hiện có:**
- SJR (Scimago Journal Rank) - Q1-Q4, H-index
- VHB (German Business Research)
- CCF (China Computer Federation)
- ABDC (Australian Business Deans Council)
- AJG (Academic Journal Guide)
- CORE (Computing Research & Education)
- FNEGE, CoNRS, HCERES (French rankings)
- JCR, SNIP, CiteSc

### 4. **Hạn chế đã xác định:**
- Thiếu coverage cho ngành tự nhiên (physics, chemistry, biology, etc.)
- Không có Impact Factor
- Tổ chức theo journal list thay vì theo ngành/field

---

## PHẦN 1: Tạo Phiên Bản Modified với Tổ Chức Theo Ngành

### 1.1 Đổi tên và Branding

**Tên mới:** Scholar Field Classifier (SFC)
**Slogan:** "Field-aware journal quality metrics for Google Scholar"

**Thay đổi:**
- Extension name: "Scholar Field Classifier"
- Extension ID mới
- Icon mới (có thể giữ hoặc điều chỉnh màu sắc)
- Description cập nhật

**Files cần sửa:**
- `manifest.json` - name, description, extension ID
- `popup.html` - branding text
- `README.md` - documentation mới
- `_locales/en/messages.json` - localization strings

### 1.2 Thiết kế Database theo Ngành

**Cấu trúc mới:**

```javascript
// Thay vì chỉ có:
ccf.SJR_Q = {"JOURNAL_NAME": "Q1", ...}

// Sẽ có:
sfc.fields = {
  "natural_sciences": {
    "physics": {
      "journals": {...},
      "rankings": {...},
      "impact_factors": {...}
    },
    "chemistry": {...},
    "biology": {...},
    "mathematics": {...}
  },
  "engineering": {
    "computer_science": {...},
    "electrical": {...},
    "mechanical": {...}
  },
  "social_sciences": {...},
  "humanities": {...}
}
```

**Phân loại ngành chuẩn (Field Classification):**
Sử dụng chuẩn phân loại từ:
1. **OECD Fields of Science** (6 major fields, 42 sub-fields)
2. **Web of Science Categories** (254 categories)
3. **Scopus Subject Areas** (27 major areas, 330+ specific fields)

**Mapping Strategy:**
- Mỗi journal sẽ được tag với 1 hoặc nhiều field categories
- Implement field detection algorithm dựa trên:
  - ISSN lookup → field mapping
  - Journal name pattern matching
  - Crossref API subject classification
  - DOAJ (Directory of Open Access Journals) categories

### 1.3 Cấu trúc Folder Mới

```
scholar_extention_trung/
├── manifest.json
├── popup.html
├── options.html
├── background.js
├── script.js
├── css/
│   └── style.css
├── js/
│   ├── scholar.js (modified)
│   ├── fetchRank.js (modified)
│   ├── fieldDetector.js (NEW)
│   ├── fieldMatcher.js (NEW)
│   └── ccf.js
├── data/
│   ├── fields/
│   │   ├── natural_sciences/
│   │   │   ├── physics.journals.js
│   │   │   ├── chemistry.journals.js
│   │   │   ├── biology.journals.js
│   │   │   └── mathematics.journals.js
│   │   ├── engineering/
│   │   │   ├── computer_science.journals.js
│   │   │   └── electrical.journals.js
│   │   ├── social_sciences/
│   │   └── humanities/
│   ├── rankings/ (consolidated from all sources)
│   │   ├── sjr_quartiles.js
│   │   ├── impact_factors.js
│   │   ├── field_rankings.js
│   │   └── issn_to_field.js
│   └── legacy/ (keep original structure for backward compatibility)
├── utils/
│   ├── fieldClassifier.py (NEW)
│   ├── impactFactorScraper.py (NEW)
│   ├── journalListAggregator.py (NEW)
│   └── dataConverter.py (modified)
└── icon/
    ├── 16x16.png
    ├── 32x32.png
    └── 128x128.png
```

### 1.4 Implementation Steps cho Phần 1

**Step 1.1:** Copy base extension và rename
**Step 1.2:** Update manifest.json với branding mới
**Step 1.3:** Create field classification schema
**Step 1.4:** Implement fieldDetector.js - logic detect field từ journal name/ISSN
**Step 1.5:** Modify scholar.js để integrate field detection
**Step 1.6:** Test với sample journals từ different fields

---

## PHẦN 2: Tìm và Cập nhật Journal Lists (Đặc biệt cho Natural Sciences)

### 2.1 Nguồn Dữ liệu Mới

#### A. Natural Sciences - Comprehensive Sources

**Physics:**
1. **APS Journals** (American Physical Society)
   - Source: https://journals.aps.org/
   - Coverage: ~14 high-impact physics journals
   - Data: Journal names, ISSNs, impact factors

2. **IOP Publishing**
   - Source: https://publishingsupport.iopscience.iop.org/journals/
   - Coverage: 100+ physics journals
   - Data: Full journal list with ISSNs

3. **Springer Physics Journals**
   - Source: https://www.springer.com/gp/physics/journals
   - Coverage: 100+ journals
   - API: Springer Nature API available

**Chemistry:**
1. **ACS Publications** (American Chemical Society)
   - Source: https://pubs.acs.org/
   - Coverage: 75+ chemistry journals
   - Data: High-quality chemistry journals, impact factors available

2. **RSC Journals** (Royal Society of Chemistry)
   - Source: https://www.rsc.org/journals-books-databases/
   - Coverage: 50+ chemistry journals
   - Data: Complete ISSN list

3. **Elsevier Chemistry Journals**
   - Source: Scopus Subject Area "Chemistry"
   - Coverage: 1000+ journals
   - API: Scopus API with chemistry filter

**Biology & Life Sciences:**
1. **Nature Portfolio**
   - Source: https://www.nature.com/siteindex/
   - Coverage: Nature + Nature sub-journals + Communications
   - Data: High-impact journals

2. **PLOS (Public Library of Science)**
   - Source: https://plos.org/
   - Coverage: 7 open-access journals
   - API: PLOS Search API

3. **BioMed Central**
   - Source: https://www.biomedcentral.com/journals
   - Coverage: 300+ open-access biology journals
   - Data: Full metadata available

**Mathematics:**
1. **Math Journals - zbMATH**
   - Source: https://zbmath.org/journals/
   - Coverage: 3000+ math journals
   - Data: Comprehensive list with classifications

2. **AMS Journals** (American Mathematical Society)
   - Source: https://www.ams.org/publications/journals
   - Coverage: Top-tier math journals
   - Data: Impact factors, SCImago ranks

#### B. Cross-Disciplinary Sources (Covering All Fields)

**1. Scopus Journal List**
- Source: https://www.scopus.com/sources
- Coverage: 40,000+ journals across all fields
- Data: CiteScore, SJR, SNIP, subject areas
- Access: Downloadable title list (CSV format)
- **Priority: HIGH** - Best comprehensive source

**2. Web of Science Master Journal List**
- Source: https://mjl.clarivate.com/
- Coverage: 21,000+ journals
- Data: Impact Factor, categories, JCR quartiles
- Access: Public search interface, can be scraped
- **Priority: HIGH** - Essential for Impact Factor

**3. DOAJ (Directory of Open Access Journals)**
- Source: https://doaj.org/
- Coverage: 18,000+ open-access journals
- Data: Subject classification, ISSNs
- Access: Public API + CSV download
- **Priority: MEDIUM** - Good for OA journals

**4. Ulrichsweb Global Serials Directory**
- Source: http://ulrichsweb.serialssolutions.com/
- Coverage: 300,000+ periodicals
- Data: Subject classification, peer-review status
- Access: Subscription required (alternative: use Crossref)
- **Priority: LOW** - Hard to access

### 2.2 Data Collection Strategy

**Approach 1: API-based Collection (Recommended)**

```python
# utils/journalListAggregator.py

class JournalAggregator:
    def __init__(self):
        self.sources = {
            'scopus': ScopusAPI(),
            'crossref': CrossrefAPI(),
            'doaj': DOAJAPI(),
            'pubmed': PubMedAPI(),
            'openalex': OpenAlexAPI()  # NEW: Open alternative to Scopus/WoS
        }

    def fetch_by_field(self, field_name):
        """
        Fetch journals for a specific field from all sources
        Returns: DataFrame with columns [journal_name, issn, field, source]
        """
        pass

    def deduplicate_journals(self, df):
        """
        Merge journals from different sources using ISSN matching
        """
        pass

    def enrich_with_metrics(self, df):
        """
        Add SJR, Impact Factor, CiteScore from various sources
        """
        pass
```

**Key APIs to use:**

1. **OpenAlex API** (FREE, no key required)
   - Endpoint: https://api.openalex.org/venues
   - Coverage: 250,000+ venues (journals + conferences)
   - Data: Impact factor, h-index, subject areas, ISSN
   - Rate limit: 10 req/sec (100,000/day)
   - **BEST FREE OPTION**

2. **Crossref API** (FREE, polite pool with email)
   - Endpoint: https://api.crossref.org/journals
   - Coverage: 150,000+ journals
   - Data: ISSN, publisher, subject classification
   - Rate limit: 50 req/sec with Plus service

3. **Scopus API** (requires institutional access)
   - More comprehensive but requires subscription

4. **Unpaywall API** (FREE for non-commercial)
   - Endpoint: https://api.unpaywall.org/
   - Good for OA status

**Approach 2: Web Scraping (Backup)**

For sources without APIs:
- Use BeautifulSoup/Scrapy for Springer, ACS, RSC websites
- Respect robots.txt and rate limits
- Cache results to avoid repeat requests

### 2.3 Field Mapping Schema

Create comprehensive ISSN → Field mapping:

```python
# utils/fieldMapper.py

FIELD_MAPPING = {
    "01017324": {  # Nature Physics ISSN
        "fields": ["natural_sciences.physics"],
        "primary_field": "physics",
        "sub_fields": ["condensed_matter", "quantum_physics"],
        "broad_category": "natural_sciences"
    },
    "00027863": {  # JACS (J Am Chem Soc)
        "fields": ["natural_sciences.chemistry"],
        "primary_field": "chemistry",
        "sub_fields": ["organic_chemistry", "inorganic_chemistry"],
        "broad_category": "natural_sciences"
    }
}
```

### 2.4 Data Processing Pipeline

**Pipeline Steps:**

```
Raw Data Sources
    ↓
[1. Collection] → APIs + Web Scraping
    ↓
[2. Normalization] → Standardize formats, clean names
    ↓
[3. Deduplication] → Merge based on ISSN (primary) and name (secondary)
    ↓
[4. Field Classification] → Assign fields using:
    - Source-provided categories
    - ML-based classification (optional)
    - Manual curation for ambiguous cases
    ↓
[5. Metrics Enrichment] → Add Impact Factor, SJR, CiteScore
    ↓
[6. Quality Check] → Validate data integrity
    ↓
[7. Export to JS] → Convert to extension-ready format
    ↓
Final Data Files (data/fields/*.js)
```

### 2.5 Implementation Steps cho Phần 2

**Step 2.1:** Setup API access (OpenAlex, Crossref, DOAJ)
**Step 2.2:** Implement journalListAggregator.py
**Step 2.3:** Collect natural sciences journals (target: 5,000+ journals)
**Step 2.4:** Implement field classification algorithm
**Step 2.5:** Generate ISSN → Field mapping database
**Step 2.6:** Quality assurance - manual check sample of 100 journals
**Step 2.7:** Convert to JS format and integrate into extension

---

## PHẦN 3: Thêm Impact Factor

### 3.1 Nguồn Impact Factor

**Official Sources:**

1. **Journal Citation Reports (JCR) - Clarivate**
   - Source: https://jcr.clarivate.com/
   - Coverage: 20,000+ journals
   - Data: Official Impact Factor (IF), 5-year IF
   - Access: **Subscription required**
   - Workaround: Use institutional access or alternatives

2. **Scimago Journal Rank (SJR)**
   - Source: https://www.scimagojr.com/
   - Coverage: 40,000+ journals
   - Data: SJR indicator (free alternative to IF), H-index, Quartiles
   - Access: **FREE** - Can download full CSV
   - **Best free option for Impact Factor alternative**

3. **CiteScore - Scopus**
   - Source: https://www.scopus.com/sources
   - Coverage: 40,000+ journals
   - Data: CiteScore (similar to IF, 3-year window)
   - Access: **FREE** - Public data

4. **OpenAlex Impact Factor**
   - Source: https://docs.openalex.org/api-entities/venues
   - Data: 2-year mean citedness (equivalent to IF)
   - Access: **FREE** - API available

**Secondary Sources (for verification):**

5. **ResearchGate Journal Impact**
   - Crowdsourced impact metrics
   - Less reliable but can fill gaps

6. **Google Scholar Metrics**
   - h5-index and h5-median
   - Good for top journals only (top 100 per category)

### 3.2 Data Collection Strategy

**Recommended Approach:**

Use **multi-source strategy** to maximize coverage:

```python
# utils/impactFactorCollector.py

class ImpactFactorCollector:
    def __init__(self):
        self.sources = {
            'sjr': SJRScraper(),           # Primary: SJR as IF proxy
            'openalex': OpenAlexAPI(),      # Secondary: OpenAlex 2yr citedness
            'citescore': CitescoreAPI(),    # Tertiary: CiteScore
            'google_scholar': GScraper()    # For top journals only
        }

    def get_impact_factor(self, issn):
        """
        Try to get IF from sources in priority order
        Returns: {
            'if_value': 5.23,
            'year': 2023,
            'source': 'sjr',
            'quartile': 'Q1',
            'alternative_metrics': {
                'citescore': 5.8,
                'sjr': 1.45
            }
        }
        """
        # Try SJR first
        if_data = self.sources['sjr'].get_sjr(issn)
        if if_data:
            return if_data

        # Fallback to OpenAlex
        if_data = self.sources['openalex'].get_2yr_mean(issn)
        # ... etc
```

**SJR as Impact Factor Proxy:**

SJR correlates highly with Impact Factor (r ≈ 0.7-0.8), so we can use it as a good proxy:

- Display: "SJR: 1.45 (≈IF)" or "Impact: 1.45 (SJR-based)"
- For journals with official IF available, display both

### 3.3 Integration vào Extension

**UI Changes:**

Current display:
```
[Q1] [H: 45] [CCF: A]
```

New display with IF:
```
[Q1] [IF: 5.2] [H: 45] [CCF: A]
```

**Data Structure:**

```javascript
// data/rankings/impact_factors.js
sfc.impactFactors = {
  "01017324": {  // Nature Physics ISSN
    "value": 19.5,
    "year": 2023,
    "source": "sjr",
    "quartile": "Q1",
    "field_rank": {
      "physics": 3,
      "total_in_field": 450
    },
    "alternative": {
      "citescore": 21.2,
      "sjr_index": 5.67
    }
  }
}
```

**fetchRank.js Modification:**

```javascript
// Add IF lookup after ISSN is retrieved
function fetchRank(node, title, compl, site, elid, author, settings) {
    // ... existing CrossRef API call ...

    // NEW: Fetch Impact Factor
    if (ISSN1) {
        let impactFactor = sfc.impactFactors[ISSN1.replace('-', '')];
        if (impactFactor) {
            // Add IF badge to display
            let ifBadge = createIFBadge(impactFactor);
            $(node).append(ifBadge);
        }
    }

    // ... rest of function ...
}

function createIFBadge(ifData) {
    let color = getColorByIF(ifData.value);
    let tooltip = `Impact Factor: ${ifData.value} (${ifData.year})
                   Source: ${ifData.source.toUpperCase()}
                   Quartile: ${ifData.quartile}`;

    return `<span class="if-badge" style="background: ${color}"
                  title="${tooltip}">
                IF: ${ifData.value}
            </span>`;
}

function getColorByIF(value) {
    // Color scheme based on IF ranges
    if (value >= 10) return '#00cc00';      // Green - Excellent
    if (value >= 5) return '#66cc00';       // Light green - Very good
    if (value >= 3) return '#cccc00';       // Yellow - Good
    if (value >= 1) return '#ff9900';       // Orange - Average
    return '#ff6666';                        // Red - Below average
}
```

### 3.4 Impact Factor Display Options

**Option A: Always Show (Recommended)**
- Show IF for all journals that have it
- Show "IF: N/A" if not available
- Consistent display

**Option B: Selective Display**
- Only show IF if value > 1.0
- Reduces clutter for low-impact journals
- May confuse users about missing data

**Option C: Tiered Display**
- Show official IF if available (marked with *)
- Show SJR-based estimate otherwise (marked with ~)
- Example: `IF: 5.2*` vs `IF: 5.2~`

**Recommendation:** Use Option C for transparency

### 3.5 Implementation Steps cho Phần 3

**Step 3.1:** Download complete SJR journal list (CSV from scimagojr.com)
**Step 3.2:** Implement impactFactorCollector.py
**Step 3.3:** Enrich journal database with IF values
**Step 3.4:** Generate impact_factors.js data file
**Step 3.5:** Modify fetchRank.js to display IF badge
**Step 3.6:** Update CSS for IF badge styling
**Step 3.7:** Add IF filter in options page (user can toggle on/off)
**Step 3.8:** Test display on Google Scholar results

---

## PHẦN 4: Technical Implementation Details

### 4.1 Data Size Optimization

**Challenge:** Firefox extension file size limit = 4MB (per file)

**Current sizes:**
- `ccf.ABDC.js` = 1.4MB
- `ccf.issnABDC.js` = 772KB

**With new data (estimated):**
- Natural sciences journals: +3,000 journals
- Impact factors: +20,000 entries
- Field classifications: +40,000 mappings

**Total estimated new data: ~8-10MB** → Exceeds limit!

**Solutions:**

**Option 1: Split by Field (Recommended)**
```
data/fields/physics.js       (1.2MB)
data/fields/chemistry.js     (1.0MB)
data/fields/biology.js       (1.5MB)
... etc
```
- Lazy load only relevant field data
- Load based on field detection

**Option 2: Data Compression**
```javascript
// Use shorter keys, compact format
// Instead of:
{"Journal of Applied Physics": {"sjr": "Q1", "if": 3.2, "field": "physics"}}

// Use:
{"JApplPhys": ["Q1", 3.2, "phy"]}
```
- Can reduce size by 40-50%
- Trade-off: less readable

**Option 3: IndexedDB Storage**
```javascript
// Store large datasets in browser IndexedDB
// Load on extension install
// Access via async queries
```
- Best for very large datasets
- More complex implementation

**Recommended:** Combination of Option 1 + Option 2

### 4.2 Field Detection Algorithm

```javascript
// js/fieldDetector.js

class FieldDetector {
    constructor() {
        this.issnToField = sfc.issnFieldMapping;
        this.namePatterns = sfc.fieldPatterns;
    }

    detectField(journalName, issn) {
        // Method 1: ISSN lookup (most reliable)
        if (issn && this.issnToField[issn]) {
            return this.issnToField[issn];
        }

        // Method 2: Name pattern matching
        let normalizedName = this.normalizeName(journalName);
        for (let [pattern, field] of Object.entries(this.namePatterns)) {
            if (normalizedName.match(pattern)) {
                return field;
            }
        }

        // Method 3: Keyword analysis
        let keywords = this.extractKeywords(journalName);
        return this.classifyByKeywords(keywords);
    }

    normalizeName(name) {
        return name.toUpperCase()
                   .normalize('NFD')
                   .replace(/[^A-Z0-9]/g, '');
    }

    extractKeywords(name) {
        const stopWords = ['JOURNAL', 'OF', 'THE', 'AND', 'FOR'];
        return name.toUpperCase()
                   .split(' ')
                   .filter(w => !stopWords.includes(w));
    }

    classifyByKeywords(keywords) {
        // Physics indicators
        const physicsTerms = ['PHYSICS', 'QUANTUM', 'PLASMA', 'OPTICS'];
        if (keywords.some(k => physicsTerms.includes(k))) {
            return 'natural_sciences.physics';
        }

        // Chemistry indicators
        const chemistryTerms = ['CHEMISTRY', 'CHEMICAL', 'MOLECULAR'];
        if (keywords.some(k => chemistryTerms.includes(k))) {
            return 'natural_sciences.chemistry';
        }

        // ... more classifications ...

        return 'unknown';
    }
}
```

### 4.3 Performance Considerations

**Current performance:**
- Lookup time: ~1-5ms per journal (in-memory dictionary)
- Page load impact: ~50-100ms for 10 results

**With new system:**
- Field detection: +2-3ms
- IF lookup: +1-2ms
- **Total: ~5-10ms per journal** → Still acceptable

**Optimization strategies:**
1. **Pre-compute normalized names** - Don't normalize at runtime
2. **Use Map instead of Object** - Faster lookups in JS
3. **Lazy load field data** - Only load when needed
4. **Cache results** - Don't re-lookup same journal

### 4.4 Backward Compatibility

**Keep legacy data structure** in `data/legacy/` folder:
- Ensures old queries still work
- Gradual migration path
- Users can opt-in to new field-based system

**Settings option:**
```javascript
// options.html
<input type="checkbox" id="useFieldBasedSystem">
<label>Use field-based journal classification (Beta)</label>
```

---

## PHẦN 5: Testing & Quality Assurance

### 5.1 Test Cases

**Test Suite 1: Field Detection**
- [ ] Physics journals correctly identified (Nature Physics, PRL, etc.)
- [ ] Chemistry journals correctly identified (JACS, Angew. Chem., etc.)
- [ ] Ambiguous journals handled (Nature → multiple fields)
- [ ] Unknown journals return 'unknown' field

**Test Suite 2: Impact Factor Display**
- [ ] IF shown for journals with data
- [ ] Correct IF value displayed
- [ ] Tooltip shows year and source
- [ ] Color coding accurate
- [ ] Graceful fallback if no IF data

**Test Suite 3: Performance**
- [ ] Page load time < 200ms overhead
- [ ] Lookup time < 10ms per journal
- [ ] Memory usage < 50MB
- [ ] No UI freezing

**Test Suite 4: Data Integrity**
- [ ] No duplicate journals in database
- [ ] All ISSNs valid format
- [ ] Field classifications consistent
- [ ] No broken links in metadata

### 5.2 Manual Testing Checklist

**Test on Google Scholar with these queries:**
1. "quantum computing" → Should show physics/CS journals
2. "organic synthesis" → Should show chemistry journals
3. "CRISPR gene editing" → Should show biology journals
4. "machine learning" → Should show CS journals
5. "climate change" → Should show environmental science journals

**Verify:**
- Field badges appear correctly
- Impact factors displayed
- Rankings still work (Q1-Q4, etc.)
- No performance degradation

---

## PHẦN 6: Deployment & Maintenance

### 6.1 Release Strategy

**Phase 1: Internal Testing (Week 1-2)**
- Deploy to local Firefox only
- Test all features
- Fix critical bugs

**Phase 2: Beta Release (Week 3-4)**
- Release to select users
- Gather feedback
- Iterate on design

**Phase 3: Public Release (Week 5+)**
- Submit to Firefox Add-ons store
- Announce on academic forums
- Monitor for issues

### 6.2 Data Update Schedule

**Quarterly updates:**
- Impact Factors (when JCR releases new data - usually June)
- Journal list additions (new journals)
- Field classification improvements

**Annual updates:**
- Complete re-scrape of all sources
- Deprecate defunct journals
- Add new ranking systems

### 6.3 Documentation

**Create:**
1. `USER_GUIDE.md` - How to use extension
2. `DATA_SOURCES.md` - List all data sources and licenses
3. `DEVELOPMENT.md` - How to build and contribute
4. `CHANGELOG.md` - Version history
5. `API_DOCS.md` - For data pipeline scripts

---

## PHẦN 7: Timeline & Resource Estimates

### 7.1 Development Timeline

**Assuming full-time development:**

| Phase | Task | Duration |
|-------|------|----------|
| 1 | Setup & Planning | 2 days |
| 2 | Extension Rename & Rebranding | 1 day |
| 3 | Field Classification Schema | 2 days |
| 4 | Data Collection (APIs) | 5 days |
| 5 | Data Processing & Cleaning | 3 days |
| 6 | Impact Factor Integration | 3 days |
| 7 | UI/UX Updates | 2 days |
| 8 | Testing & QA | 3 days |
| 9 | Documentation | 2 days |
| 10 | Deployment | 1 day |
| **TOTAL** | | **24 days (~5 weeks)** |

**Part-time development:** ~8-10 weeks

### 7.2 Required Resources

**Technical:**
- Python 3.8+ (for data scripts)
- Node.js (optional, for build tools)
- Firefox Developer Edition (for testing)
- Git (for version control)

**APIs:**
- OpenAlex API (free, no key)
- Crossref API (free, polite pool)
- ScimagoJR data (free download)

**Optional (for better data):**
- Scopus API (institutional access)
- Web of Science API (institutional access)

**Human Resources:**
- 1 developer (full-stack: Python + JavaScript)
- 1 domain expert (for field classification QA) - optional
- Beta testers (5-10 academic users)

---

## PHẦN 8: Risks & Mitigation

### 8.1 Identified Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data source changes/removal | High | Medium | Use multiple sources, cache data |
| API rate limits exceeded | Medium | Low | Implement backoff, use free APIs |
| Extension size exceeds limits | High | Medium | Data splitting, compression |
| Field classification inaccurate | Medium | Medium | Manual QA, user feedback loop |
| Performance degradation | High | Low | Profiling, optimization |
| User adoption low | Low | Medium | Marketing, academic outreach |

### 8.2 Contingency Plans

**If Scopus API unavailable:**
- Fall back to OpenAlex + Crossref combination
- Supplement with manual curation for top journals

**If file size still too large:**
- Move to IndexedDB storage model
- Use on-demand loading from CDN

**If field classification fails:**
- Fall back to legacy journal-only view
- Implement manual override in settings

---

## PHẦN 9: Success Metrics

### 9.1 Quantitative Metrics

**Data Coverage:**
- Target: 25,000+ journals (up from current ~10,000)
- Natural sciences coverage: 5,000+ journals (currently ~500)
- Impact factor coverage: 15,000+ journals (currently 0)

**Performance:**
- Page load overhead: < 200ms
- Lookup accuracy: > 95%
- Field classification accuracy: > 85%

**Adoption:**
- 1,000+ active users (6 months post-launch)
- 4.0+ star rating on Firefox Add-ons
- 50+ GitHub stars

### 9.2 Qualitative Metrics

**User Feedback:**
- Positive reviews from natural sciences researchers
- Feature requests for additional fields
- Low bug report rate

**Academic Impact:**
- Cited in research papers
- Recommended by university libraries
- Integration requests from other tools

---

## PHẦN 10: Next Steps (Immediate Actions)

### To Start Implementation NOW:

**Priority 1 (Must Do):**
1. ✅ Create `scholar_extention_trung/` folder structure
2. ✅ Copy base extension files
3. ✅ Setup Python virtual environment
4. ✅ Install dependencies: `pandas`, `requests`, `beautifulsoup4`
5. ✅ Register for OpenAlex API access (no key needed, just respect rate limits)
6. ✅ Download SJR journal list CSV from scimagojr.com

**Priority 2 (This Week):**
7. Implement `journalListAggregator.py` to fetch from OpenAlex
8. Implement `fieldClassifier.py` for OECD classification
9. Collect natural sciences journals (physics, chemistry, biology)
10. Generate first version of field mapping database

**Priority 3 (Next Week):**
11. Modify `scholar.js` to integrate field detection
12. Implement Impact Factor display
13. Test on sample Google Scholar queries
14. Iterate based on results

---

## Appendices

### Appendix A: OECD Field Classification

**1. Natural Sciences**
- 1.1 Mathematics
- 1.2 Computer and information sciences
- 1.3 Physical sciences
- 1.4 Chemical sciences
- 1.5 Earth and related environmental sciences
- 1.6 Biological sciences
- 1.7 Other natural sciences

**2. Engineering and Technology**
- 2.1 Civil engineering
- 2.2 Electrical, electronic, information engineering
- 2.3 Mechanical engineering
- 2.4 Chemical engineering
- 2.5 Materials engineering
- 2.6 Medical engineering
- 2.7 Environmental engineering
- 2.8 Environmental biotechnology
- 2.9 Industrial biotechnology
- 2.10 Nano-technology
- 2.11 Other engineering

**3. Medical and Health Sciences**
- 3.1 Basic medicine
- 3.2 Clinical medicine
- 3.3 Health sciences
- 3.4 Medical biotechnology
- 3.5 Other medical sciences

**4. Agricultural Sciences**
- 4.1 Agriculture, forestry, fisheries
- 4.2 Animal and dairy science
- 4.3 Veterinary science
- 4.4 Agricultural biotechnology
- 4.5 Other agricultural sciences

**5. Social Sciences**
- 5.1 Psychology
- 5.2 Economics and business
- 5.3 Educational sciences
- 5.4 Sociology
- 5.5 Law
- 5.6 Political science
- 5.7 Social and economic geography
- 5.8 Media and communications
- 5.9 Other social sciences

**6. Humanities**
- 6.1 History and archaeology
- 6.2 Languages and literature
- 6.3 Philosophy, ethics, religion
- 6.4 Arts
- 6.5 Other humanities

### Appendix B: Useful Data Sources Summary

| Source | Type | Coverage | Access | Priority |
|--------|------|----------|--------|----------|
| OpenAlex | API | 250K+ venues | Free | ⭐⭐⭐⭐⭐ |
| ScimagoJR | CSV | 40K journals | Free | ⭐⭐⭐⭐⭐ |
| Crossref | API | 150K journals | Free | ⭐⭐⭐⭐ |
| DOAJ | API/CSV | 18K OA journals | Free | ⭐⭐⭐ |
| WoS | Web | 21K journals | Paid | ⭐⭐⭐ |
| Scopus | API | 40K journals | Paid | ⭐⭐⭐ |
| PubMed | API | 35K journals | Free | ⭐⭐ |

### Appendix C: File Size Budget

| Component | Current | New | Limit |
|-----------|---------|-----|-------|
| Core JS | 500KB | 600KB | 4MB |
| Data files | 10MB | 25MB | 50MB total |
| Icons/CSS | 100KB | 150KB | 1MB |
| **Total** | ~10.6MB | ~25.75MB | 50MB |

Still within Firefox extension limits ✅

---

## Conclusion

Kế hoạch này cung cấp roadmap đầy đủ để:

1. ✅ Tạo phiên bản modified với tổ chức theo ngành
2. ✅ Bổ sung journal list cho ngành tự nhiên (+15,000 journals)
3. ✅ Thêm Impact Factor display

**Estimated effort:** 5 weeks full-time development
**Data quality:** High (using authoritative sources)
**User impact:** Significant improvement for natural sciences researchers

**Khuyến nghị:** Bắt đầu với MVP (Minimum Viable Product):
- Focus on top 3 natural science fields: Physics, Chemistry, Biology
- Use only free data sources (OpenAlex, SJR, DOAJ)
- Implement core functionality first, optimize later

**Next action:** Please approve this plan or request modifications, sau đó chúng ta sẽ bắt đầu implementation! 🚀

