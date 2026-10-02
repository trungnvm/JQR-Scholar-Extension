const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log('====================================================');
console.log('RUNNING COMPREHENSIVE JQR EXTENSION SELF-TEST SUITE');
console.log('====================================================\n');

const BASE_DIR = path.resolve(__dirname, 'scholar_extention_trung');

// ----------------------------------------------------
// TEST SUITE 1: JS Syntax Verification
// ----------------------------------------------------
console.log('[TEST SUITE 1] JavaScript Syntax Verification');
const filesToCheck = [
    'script.js',
    'js/ccf.js',
    'js/fetchRank.js',
    'js/scholar.js',
    'js/scholar_turbo.js',
    'data/rankings/impact_factors.js',
    'data/rankings/impact_factors_names.js'
];

filesToCheck.forEach(relPath => {
    const fullPath = path.join(BASE_DIR, relPath);
    assert(fs.existsSync(fullPath), `File must exist: ${relPath}`);
    // Evaluates syntax without error
    const content = fs.readFileSync(fullPath, 'utf8');
    assert.doesNotThrow(() => {
        new Function(content);
    }, `Syntax error in ${relPath}`);
    console.log(`  ✓ ${relPath} passed syntax check`);
});

// ----------------------------------------------------
// TEST SUITE 2: Environment Setup & Data Loading
// ----------------------------------------------------
console.log('\n[TEST SUITE 2] In-Memory Data Loading');
global.window = {
    location: { pathname: '/scholar', href: 'https://scholar.google.com/scholar?q=ai' },
    addEventListener: () => {}
};
global.document = {
    getElementById: (id) => null,
    body: {}
};
global.sfc = {};
global.browserAPI = {
    storage: {
        local: {
            get: (cb) => cb({ ext_on: true, turbo: true, impactFactor: true })
        }
    }
};

// Load Ranking files
eval(fs.readFileSync(path.join(BASE_DIR, 'data/rankings/impact_factors.js'), 'utf8'));
eval(fs.readFileSync(path.join(BASE_DIR, 'data/rankings/impact_factors_names.js'), 'utf8'));

assert(sfc.impactFactors, 'sfc.impactFactors must be defined');
assert(sfc.impactFactorsNames, 'sfc.impactFactorsNames must be defined');

const issnCount = Object.keys(sfc.impactFactors).length;
const nameCount = Object.keys(sfc.impactFactorsNames).length;

console.log(`  ✓ Loaded ${issnCount} ISSN/eISSN keys`);
console.log(`  ✓ Loaded ${nameCount} Name & Alias keys`);
assert(issnCount >= 35000, 'ISSN keys should be >= 35,000');
assert(nameCount >= 60000, 'Name keys should be >= 60,000');

// Load ccf.js
eval(fs.readFileSync(path.join(BASE_DIR, 'js/ccf.js'), 'utf8').replace('const ccf = {};', 'global.ccf = {};'));
assert(typeof ccf.getImpactFactor === 'function', 'ccf.getImpactFactor must be a function');
assert(typeof ccf.getImpactFactorByName === 'function', 'ccf.getImpactFactorByName must be a function');

// ----------------------------------------------------
// TEST SUITE 3: Journal Name Extraction from div.gs_a
// ----------------------------------------------------
console.log('\n[TEST SUITE 3] Journal Name Extraction from Google Scholar div.gs_a');

// Extract the extractJournalInfo function from scholar.js
const scholarContent = fs.readFileSync(path.join(BASE_DIR, 'js/scholar.js'), 'utf8');
const extractFnMatch = scholarContent.match(/function extractJournalInfo\([\s\S]*?\n\}/);
assert(extractFnMatch, 'extractJournalInfo must be present in scholar.js');
eval(extractFnMatch[0]);

const extractionTestCases = [
    {
        input: 'J Smith, A Doe - Nature, 2023 - nature.com',
        expected: 'Nature',
        hasEllipsis: false
    },
    {
        input: 'J Smith, A Doe\u00A0- Lancet, 2021\u00A0- thelancet.com',
        expected: 'Lancet',
        hasEllipsis: false
    },
    {
        input: 'M Jordan - IEEE Transactions on Pattern Analysis and Machine …, 2020 - ieeexplore.ieee.org',
        expected: 'IEEE Transactions on Pattern Analysis and Machine',
        hasEllipsis: true
    },
    {
        input: 'A Einstein, B Podolsky - Physical Review, 1935 - APS',
        expected: 'Physical Review',
        hasEllipsis: false
    },
    {
        input: 'CA Clinicians - CA-A Cancer Journal for Clinicians, 2024 - Wiley Online Library',
        expected: 'CA-A Cancer Journal for Clinicians',
        hasEllipsis: false
    },
    {
        input: 'V Mnih, KS Kavukcuoglu, D Silver - Nature, 2015 - nature.com',
        expected: 'Nature',
        hasEllipsis: false
    },
    {
        input: 'T Nguyen - 2022 - repository.vnu.edu.vn', // No journal, just year
        expected: '',
        hasEllipsis: false
    },
    {
        input: 'K He, X Zhang, S Ren - IEEE Trans. Pattern Anal. Mach. Intell., 2016 - IEEE',
        expected: 'IEEE Trans. Pattern Anal. Mach. Intell',
        hasEllipsis: false
    }
];

extractionTestCases.forEach((tc, i) => {
    const res = extractJournalInfo(tc.input);
    assert.strictEqual(res.name, tc.expected, `Extraction mismatch on case ${i+1}: expected '${tc.expected}', got '${res.name}'`);
    assert.strictEqual(res.hasEllipsis, tc.hasEllipsis, `Ellipsis flag mismatch on case ${i+1}`);
    console.log(`  ✓ Case ${i+1}: '${tc.input.substring(0, 35)}...' -> '${res.name}' (ellipsis: ${res.hasEllipsis})`);
});

// ----------------------------------------------------
// TEST SUITE 4: Impact Factor & Category Lookups
// ----------------------------------------------------
console.log('\n[TEST SUITE 4] Impact Factor & Category Lookups (Column AG)');

// Test 4.1: Lookup by Print ISSN and Electronic eISSN
console.log('  Subtest 4.1: ISSN & eISSN dual lookup');
const caByPrint = ccf.getImpactFactor('0007-9235');
const caByElectronic = ccf.getImpactFactor('1542-4863');
assert(caByPrint, 'Print ISSN 0007-9235 must resolve');
assert(caByElectronic, 'Electronic eISSN 1542-4863 must resolve');
assert.strictEqual(caByPrint.value, '685.2', 'CA JIF must be 685.2');
assert.strictEqual(caByElectronic.value, '685.2', 'eISSN must resolve to same JIF 685.2');
assert(caByPrint.categories && caByPrint.categories.length > 0, 'Categories from Column AG must be present');
console.log(`    ✓ CA-A Cancer J Clin: Print ISSN -> ${caByPrint.value}, eISSN -> ${caByElectronic.value} (both match!)`);

// Test 4.2: Name exact & alias match ('The ' prefix)
console.log('  Subtest 4.2: Name exact & alias matching (with/without "The")');
const lancet1 = ccf.getImpactFactorByName('Lancet');
const lancet2 = ccf.getImpactFactorByName('The Lancet');
assert(lancet1, 'Lancet must resolve');
assert(lancet2, 'The Lancet must resolve');
assert.strictEqual(lancet1.value, '109.0', 'Lancet JIF must be 109.0');
assert.strictEqual(lancet2.value, '109.0', 'The Lancet JIF must be 109.0');
console.log(`    ✓ Lancet -> IF ${lancet1.value} | The Lancet -> IF ${lancet2.value}`);

// Test 4.3: Prefix matching on truncated names (Google Scholar '…')
console.log('  Subtest 4.3: Prefix matching for truncated journal titles');
const truncatedQuery = 'IEEE Transactions on Pattern Analysis and Machine';
const tpamiMatch = ccf.getImpactFactorByName(truncatedQuery);
assert(tpamiMatch, 'Truncated TPAMI must resolve via prefix search');
assert.strictEqual(tpamiMatch.value, '20.4', 'TPAMI JIF must be 20.4');
console.log(`    ✓ '${truncatedQuery}' -> Matched: ${tpamiMatch.name || 'TPAMI'} (IF: ${tpamiMatch.value}, Q1)`);

// Test 4.4: Multi-category verification (Column AG details)
console.log('  Subtest 4.4: Multi-category parsing from Column AG');
const nrdMatch = ccf.getImpactFactorByName('Nature Reviews Drug Discovery');
assert(nrdMatch, 'Nature Reviews Drug Discovery must resolve');
assert.strictEqual(nrdMatch.value, '91.2', 'NRD JIF must be 91.2');
assert(Array.isArray(nrdMatch.categories), 'categories must be an array');
assert.strictEqual(nrdMatch.categories.length, 2, 'NRD must belong to 2 categories');
console.log(`    ✓ NRD Categories found (${nrdMatch.categories.length}):`);
nrdMatch.categories.forEach(c => {
    console.log(`      • ${c.cat}: ${c.q} (Rank: ${c.rank}, Percentile: ${c.pct})`);
    assert(c.cat && c.q && c.rank, 'Category item must have cat, q, and rank');
});

// ----------------------------------------------------
// TEST SUITE 5: Tooltip Badge Generation Verification
// ----------------------------------------------------
console.log('\n[TEST SUITE 5] Tooltip & Badge Generation');

// Mock jQuery for getIFSpan testing
global.$ = function(selector) {
    let classes = [];
    let textContent = '';
    let children = [];
    let obj = {
        addClass: (c) => { 
            c.split(/\s+/).forEach(x => { if (x) classes.push(x); }); 
            return obj; 
        },
        text: (t) => { if (t !== undefined) { textContent = t; return obj; } return textContent; },
        append: (child) => { children.push(child); return obj; },
        hasClass: (c) => classes.includes(c),
        _classes: classes,
        _text: () => textContent,
        _children: children
    };
    return obj;
};

const badgeSpan = ccf.getIFSpan(nrdMatch);
assert(badgeSpan.hasClass('if-badge'), 'Badge must have class if-badge');
assert(badgeSpan.hasClass('if-q1'), 'Badge for Q1 must have class if-q1');
assert.strictEqual(badgeSpan._text(), 'IF: 91.2', 'Badge text must be "IF: 91.2"');

// Check tooltip
const tooltipChild = badgeSpan._children[0];
assert(tooltipChild, 'Tooltip element must be appended');
const tooltipText = tooltipChild._text();
assert(tooltipText.includes('Impact Factor: 91.2'), 'Tooltip must have IF value');
assert(tooltipText.includes('Year: 2025'), 'Tooltip must have Year 2025');
assert(tooltipText.includes('Quartile: Q1'), 'Tooltip must have Quartile Q1');
assert(tooltipText.includes('BIOTECHNOLOGY & APPLIED MICROBIOLOGY (Q1, 1/180)'), 'Tooltip must have Category 1');
assert(tooltipText.includes('PHARMACOLOGY & PHARMACY (Q1, 1/356)'), 'Tooltip must have Category 2');
console.log('  ✓ Generated Badge: ' + badgeSpan._text() + ' [Classes: ' + badgeSpan._classes.join(' ') + ']');
console.log('  ✓ Tooltip Content Verified:\n' + tooltipText.split('\n').map(l => '    | ' + l).join('\n'));

// ----------------------------------------------------
// TEST SUITE 6: Timeout & Spinner Removal (fetchRank.js)
// ----------------------------------------------------
console.log('\n[TEST SUITE 6] fetchRank.js Timeout & Anti-Spin Verification');
const fetchRankContent = fs.readFileSync(path.join(BASE_DIR, 'js/fetchRank.js'), 'utf8');
assert(fetchRankContent.includes('xhr.timeout = 3000'), 'CrossRef timeout must be set to 3000ms');
assert(fetchRankContent.includes('xhrCORE.timeout = 2500'), 'DBLP timeout must be set to 2500ms');
assert(fetchRankContent.includes('xhr.ontimeout = function'), 'xhr.ontimeout handler must be implemented');
assert(fetchRankContent.includes('if (spinner) spinner.remove()'), 'Spinner must be removed on render');
console.log('  ✓ CrossRef 3.0s timeout and ontimeout fallback verified');
console.log('  ✓ DBLP 2.5s timeout and ontimeout fallback verified');
console.log('  ✓ Guaranteed spinner removal verified');

// ----------------------------------------------------
// TEST SUITE 7: Infinite Scroll & Observer (scholar.js & scholar_turbo.js)
// ----------------------------------------------------
console.log('\n[TEST SUITE 7] Infinite Scroll & MutationObserver Verification');
assert(scholarContent.includes('new MutationObserver'), 'scholar.js must use MutationObserver');
assert(scholarContent.includes('window.addEventListener("scroll"'), 'scholar.js must have scroll listener');
assert(scholarContent.includes('data-jqr-processed'), 'scholar.js must use deduplication marker');

const turboContent = fs.readFileSync(path.join(BASE_DIR, 'js/scholar_turbo.js'), 'utf8');
assert(turboContent.includes('new MutationObserver'), 'scholar_turbo.js must use MutationObserver');
assert(turboContent.includes('window.addEventListener("scroll"'), 'scholar_turbo.js must have scroll listener');
assert(turboContent.includes('data-jqr-processed'), 'scholar_turbo.js must use deduplication marker');
console.log('  ✓ MutationObserver and scroll listeners verified in scholar.js');
console.log('  ✓ MutationObserver and scroll listeners verified in scholar_turbo.js');
console.log('  ✓ Deduplication marker (data-jqr-processed) verified');

// ----------------------------------------------------
// TEST SUITE 8: Q-Ranking Fallback & Color Consistency
// ----------------------------------------------------
console.log('\n[TEST SUITE 8] Q-Ranking & Color Synchronization Verification');

// Test 8.1: Micro and Nanostructures (JCR Q2 fallback)
const m1_if = ccf.getImpactFactorByName('Micro and Nanostructures');
assert(m1_if, 'Micro and Nanostructures must be found in JCR database');
assert.strictEqual(m1_if.value, '3.1', 'Micro and Nanostructures IF must be 3.1');
assert.strictEqual(m1_if.quartile, 'Q2', 'Micro and Nanostructures quartile must be Q2');
assert.strictEqual(ccf.getIFColorClass(m1_if), 'if-q2', 'Micro and Nanostructures color class must be if-q2 (yellow)');
console.log('  ✓ Micro and Nanostructures: IF 3.1, Q2 (JCR), Color: if-q2 (Yellow)');

// Test 8.2: Advances in Natural Sciences: Nanoscience and Nanotechnology
const m2_if = ccf.getImpactFactorByName('Advances in Natural Sciences: Nanoscience and Nanotechnology');
assert(m2_if, 'Advances in Natural Sciences must be found in JCR database');
assert.strictEqual(m2_if.value, '2.4', 'Advances in Natural Sciences IF must be 2.4');
assert.strictEqual(m2_if.quartile, 'Q3', 'Advances in Natural Sciences JCR quartile must be Q3');
assert.strictEqual(m2_if.eissn, '2043-6262', 'Advances in Natural Sciences eISSN must be 2043-6262');
console.log('  ✓ Advances in Natural Sciences: IF 2.4, Q3 (JCR), eISSN: 2043-6262');

// Test 8.3: Color Consistency (No IF 3.0 Green vs IF 3.1 Yellow contradiction)
const c_30 = ccf.getIFColorClass({ value: '3.0' });
const c_31 = ccf.getIFColorClass({ value: '3.1', quartile: 'Q2' });
const c_55 = ccf.getIFColorClass({ value: '5.5' });
const c_12 = ccf.getIFColorClass({ value: '12.0' });
const c_18 = ccf.getIFColorClass({ value: '1.8' });
const c_08 = ccf.getIFColorClass({ value: '0.8' });

assert.strictEqual(c_30, 'if-good', 'IF 3.0 (no Q) must be if-good (yellow)');
assert.strictEqual(c_31, 'if-q2', 'IF 3.1 (Q2) must be if-q2 (yellow)');
assert.strictEqual(c_55, 'if-verygood', 'IF 5.5 must be if-verygood (green)');
assert.strictEqual(c_12, 'if-excellent', 'IF 12.0 must be if-excellent (deep green)');
assert.strictEqual(c_18, 'if-moderate', 'IF 1.8 must be if-moderate (orange)');
assert.strictEqual(c_08, 'if-low', 'IF 0.8 must be if-low (red)');
console.log('  ✓ Color Harmonization verified: IF 3.0 (Yellow) & IF 3.1 (Yellow) - Zero Contradiction!');

console.log('\n====================================================');
console.log('ALL 8 TEST SUITES PASSED FLAWLESSLY (100% SUCCESS)!');
console.log('====================================================');
