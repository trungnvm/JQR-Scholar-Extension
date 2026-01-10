# FieldDetector.js Integration Guide

## Files Created

Three files have been created in `/scholar_extention_trung/js/`:

1. **fieldDetector.js** (19KB)
   - Main module implementing the FieldDetector class
   - 534 lines of code with comprehensive JSDoc documentation
   - No external dependencies except optional sfc.issnFieldMapping

2. **fieldDetector_example.html** (11KB)
   - Interactive test page with 35+ test cases
   - Demonstrates all major features
   - Includes custom input testing

3. **FIELDDETECTOR_README.md** (13KB)
   - Complete API documentation
   - Usage examples
   - Integration instructions

## Quick Integration Steps

### Step 1: Add to manifest.json

Add `fieldDetector.js` to your content_scripts in `manifest.json`:

```json
{
  "content_scripts": [{
    "js": [
      "lib/jquery-3.5.1.min.js",
      "js/fieldDetector.js",        // ADD THIS LINE
      "js/scholar.js",
      "js/scholar_turbo.js",
      "js/ccf.js",
      "js/fetchRank.js"
      // ... rest of your scripts
    ]
  }]
}
```

**Recommended position:** After jQuery, before scholar.js

### Step 2: Initialize in Your Code

In your main extension script (e.g., `scholar.js` or `script.js`):

```javascript
// Initialize the field detector
const fieldDetector = new FieldDetector();

// Example: Detect field when processing a journal
function processJournalEntry(journalName, issn) {
  // Detect the academic field
  const fieldResult = fieldDetector.detectField(journalName, issn);

  console.log(`Journal: ${journalName}`);
  console.log(`Field: ${fieldResult.primary_field}`);
  console.log(`Category: ${fieldResult.broad_category}`);
  console.log(`Confidence: ${(fieldResult.confidence * 100).toFixed(0)}%`);

  // Use field information for custom logic
  if (fieldResult.broad_category === 'natural_sciences') {
    // Handle natural sciences journals
    showNaturalScienceMetrics(journalName, issn);
  } else if (fieldResult.broad_category === 'engineering') {
    // Handle engineering journals
    showEngineeringMetrics(journalName, issn);
  }

  return fieldResult;
}
```

### Step 3: (Optional) Create ISSN-to-Field Mapping Database

For maximum accuracy, create a data file with ISSN mappings:

**File:** `data/fields/issn_field_mapping.js`

```javascript
// ISSN to Field Mapping Database
const sfc = sfc || {};
sfc.issnFieldMapping = {
  // Physics journals
  "17452473": "natural_sciences.physics",  // Nature Physics
  "00319007": "natural_sciences.physics",  // Physical Review Letters
  "00036951": "natural_sciences.physics",  // Applied Physics Letters

  // Chemistry journals
  "00027863": "natural_sciences.chemistry", // JACS
  "14337851": "natural_sciences.chemistry", // Angewandte Chemie

  // Biology journals
  "10614036": "natural_sciences.biology",   // Nature Genetics
  "00928674": "natural_sciences.biology",   // Cell

  // Computer Science journals
  "00010782": "engineering.computer_science", // CACM
  "15337928": "engineering.computer_science", // ACM TOCS

  // Add more mappings here...
};
```

Then load it before `fieldDetector.js` in manifest.json:

```json
"js": [
  "lib/jquery-3.5.1.min.js",
  "data/fields/issn_field_mapping.js",  // Load BEFORE fieldDetector
  "js/fieldDetector.js",
  "js/scholar.js"
]
```

### Step 4: Test the Integration

Open `fieldDetector_example.html` in your browser to test:

```bash
# Navigate to the extension directory
cd "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/scholar_extention_trung/js/"

# Open in default browser (macOS)
open fieldDetector_example.html

# Or specify browser
open -a "Firefox" fieldDetector_example.html
open -a "Google Chrome" fieldDetector_example.html
```

## Integration Examples

### Example 1: Add Field Badge to Google Scholar Results

```javascript
// In your scholar.js or similar file
function addFieldBadge(element, journalName, issn) {
  const fieldDetector = new FieldDetector();
  const result = fieldDetector.detectField(journalName, issn);

  // Create badge element
  const badge = $('<span>')
    .addClass('field-badge')
    .addClass(`field-${result.broad_category}`)
    .text(result.primary_field.split('.')[1])  // Show subfield only
    .attr('title', `Field: ${result.primary_field}\nConfidence: ${(result.confidence * 100).toFixed(0)}%`);

  // Add to element
  $(element).append(badge);
}
```

Add CSS for badges:

```css
.field-badge {
  display: inline-block;
  padding: 2px 6px;
  margin-left: 5px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: bold;
}

.field-natural_sciences { background: #4CAF50; color: white; }
.field-engineering { background: #2196F3; color: white; }
.field-medical { background: #f44336; color: white; }
.field-social_sciences { background: #FF9800; color: white; }
.field-humanities { background: #9C27B0; color: white; }
.field-multidisciplinary { background: #607D8B; color: white; }
```

### Example 2: Filter Rankings by Field

```javascript
// Modify ccf.getRankInfo to be field-aware
function getFieldAwareRankings(journalName, issn) {
  const fieldDetector = new FieldDetector();
  const fieldResult = fieldDetector.detectField(journalName, issn);

  // Get standard rankings
  const rankInfo = ccf.getRankInfo(journalName, 'journal', issn, '', '');

  // Filter rankings based on field
  if (fieldResult.broad_category === 'natural_sciences') {
    // Prioritize JCR, SJR for natural sciences
    return {
      ...rankInfo,
      field: fieldResult.primary_field,
      preferred_rankings: ['JCR', 'SJR', 'SNIP']
    };
  } else if (fieldResult.broad_category === 'engineering') {
    // Prioritize CCF, CORE for engineering
    return {
      ...rankInfo,
      field: fieldResult.primary_field,
      preferred_rankings: ['CCF', 'CORE', 'SJR']
    };
  }

  return {
    ...rankInfo,
    field: fieldResult.primary_field
  };
}
```

### Example 3: Field-Based Color Coding

```javascript
function getFieldColor(fieldResult) {
  const colorMap = {
    'natural_sciences': {
      'physics': '#1976D2',      // Blue
      'chemistry': '#388E3C',     // Green
      'biology': '#7B1FA2',       // Purple
      'mathematics': '#F57C00',   // Orange
      'earth_sciences': '#5D4037' // Brown
    },
    'engineering': {
      'computer_science': '#0288D1',
      'electrical': '#FBC02D',
      'mechanical': '#455A64',
      'civil': '#6D4C41',
      'materials': '#00796B'
    },
    'medical': '#C62828',         // Red
    'social_sciences': '#F57F17', // Yellow
    'humanities': '#6A1B9A'       // Deep purple
  };

  const category = fieldResult.broad_category;
  const subfield = fieldResult.primary_field.split('.')[1];

  if (colorMap[category] && typeof colorMap[category] === 'object') {
    return colorMap[category][subfield] || '#757575';
  }

  return colorMap[category] || '#757575';
}
```

## Testing Checklist

Before deploying to production:

- [ ] Test with physics journals (Nature Physics, PRL, etc.)
- [ ] Test with chemistry journals (JACS, Angew. Chem., etc.)
- [ ] Test with biology journals (Cell, Nature Genetics, etc.)
- [ ] Test with computer science journals (IEEE, ACM, etc.)
- [ ] Test with multidisciplinary journals (Nature, Science, etc.)
- [ ] Test with unknown/new journals
- [ ] Test ISSN lookup (with and without hyphens)
- [ ] Test name-only detection
- [ ] Verify performance (< 5ms per detection)
- [ ] Check memory usage
- [ ] Test in Firefox and Chrome

## Performance Optimization

The FieldDetector is already optimized, but if you need better performance:

### Option 1: Pre-compute for Known Journals

```javascript
// Cache results for frequently accessed journals
const fieldCache = new Map();

function getFieldWithCache(journalName, issn) {
  const cacheKey = `${journalName}|${issn}`;

  if (fieldCache.has(cacheKey)) {
    return fieldCache.get(cacheKey);
  }

  const result = fieldDetector.detectField(journalName, issn);
  fieldCache.set(cacheKey, result);

  return result;
}
```

### Option 2: Lazy Initialization

```javascript
// Don't create detector until needed
let fieldDetector = null;

function getFieldDetector() {
  if (!fieldDetector) {
    fieldDetector = new FieldDetector();
  }
  return fieldDetector;
}
```

## Troubleshooting

### Issue: "FieldDetector is not defined"

**Solution:** Make sure `fieldDetector.js` is loaded before your code uses it. Check load order in manifest.json.

### Issue: Low confidence scores

**Solution:**
1. Provide ISSN when available (increases confidence to 95%)
2. Create `sfc.issnFieldMapping` database for your journals
3. Check journal name spelling and format

### Issue: Wrong field detected

**Solution:**
1. Check `result.all_matches` to see what else was detected
2. Add journal to ISSN mapping database
3. Improve pattern matching by adding specific keywords

### Issue: Performance problems

**Solution:**
1. Use caching (see Performance Optimization above)
2. Lazy-load the detector
3. Pre-compute fields for top journals

## Next Steps

1. **Test the implementation**
   - Open `fieldDetector_example.html`
   - Run all test cases
   - Try custom inputs

2. **Create ISSN mapping database**
   - Identify top journals in your target fields
   - Create `issn_field_mapping.js`
   - Populate with ISSN → field mappings

3. **Integrate with existing code**
   - Modify `scholar.js` to use field detection
   - Add field badges to UI
   - Filter rankings by field

4. **Customize patterns**
   - Review field patterns in `fieldDetector.js`
   - Add domain-specific keywords
   - Adjust confidence weights

5. **Deploy and monitor**
   - Test with real Google Scholar pages
   - Monitor accuracy
   - Collect feedback
   - Iterate and improve

## Support

For questions or issues:
- Review `FIELDDETECTOR_README.md` for detailed API documentation
- Check `fieldDetector_example.html` for working examples
- Examine test cases in the example file
- Consult the implementation plan in `IMPLEMENTATION_PLAN.md`

## Version Compatibility

- **Manifest Version:** 2 or 3
- **Browser:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **jQuery:** 3.5.1+ (optional, not required for core functionality)
- **Extension Framework:** Compatible with existing ccf.js architecture

## License

MIT License - Same as parent extension (Scholar Field Classifier)

---

**Created:** 2026-01-10
**Version:** 1.0.0
**Author:** Scholar Field Classifier Team
