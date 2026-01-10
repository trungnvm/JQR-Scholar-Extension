/**
 * FieldDetector Quick Test Script
 *
 * Copy and paste this entire script into your browser console to test fieldDetector.js
 * Make sure fieldDetector.js is already loaded on the page.
 *
 * Usage:
 * 1. Open fieldDetector_example.html in browser
 * 2. Open Developer Console (F12)
 * 3. Paste this script and press Enter
 * 4. Or just type: runQuickTest()
 */

function runQuickTest() {
  console.clear();
  console.log('%c=== FieldDetector Quick Test ===', 'color: #4CAF50; font-size: 18px; font-weight: bold');
  console.log('');

  // Check if FieldDetector is available
  if (typeof FieldDetector === 'undefined') {
    console.error('❌ FieldDetector is not loaded!');
    console.log('Make sure fieldDetector.js is loaded before running this test.');
    return;
  }

  // Initialize detector
  const detector = new FieldDetector();
  console.log('✅ FieldDetector initialized');
  console.log('');

  // Test cases with expected results
  const tests = [
    {
      name: 'Nature Physics',
      issn: '1745-2473',
      expected: 'natural_sciences.physics',
      description: 'High-impact physics journal'
    },
    {
      name: 'Journal of the American Chemical Society',
      issn: '0002-7863',
      expected: 'natural_sciences.chemistry',
      description: 'Top chemistry journal'
    },
    {
      name: 'Cell',
      issn: '0092-8674',
      expected: 'natural_sciences.biology',
      description: 'Top biology journal'
    },
    {
      name: 'IEEE Transactions on Software Engineering',
      issn: '',
      expected: 'engineering.computer_science',
      description: 'Software engineering journal'
    },
    {
      name: 'Annals of Mathematics',
      issn: '',
      expected: 'natural_sciences.mathematics',
      description: 'Top math journal'
    },
    {
      name: 'The Lancet',
      issn: '0140-6736',
      expected: 'medical.clinical',
      description: 'Top medical journal'
    },
    {
      name: 'American Economic Review',
      issn: '',
      expected: 'social_sciences.economics',
      description: 'Top economics journal'
    },
    {
      name: 'Quantum Information Processing',
      issn: '',
      expected: 'natural_sciences.physics',
      description: 'Quantum computing journal'
    }
  ];

  let passed = 0;
  let failed = 0;

  // Run tests
  console.log('%c--- Running Tests ---', 'color: #2196F3; font-weight: bold');
  console.log('');

  tests.forEach((test, index) => {
    const result = detector.detectField(test.name, test.issn);
    const isPass = result.primary_field === test.expected;

    if (isPass) {
      passed++;
      console.log(`%c✓ Test ${index + 1}: ${test.name}`, 'color: #4CAF50');
    } else {
      failed++;
      console.log(`%c✗ Test ${index + 1}: ${test.name}`, 'color: #f44336');
    }

    console.log(`  Description: ${test.description}`);
    if (test.issn) {
      console.log(`  ISSN: ${test.issn}`);
    }
    console.log(`  Expected: ${test.expected}`);
    console.log(`  Got: ${result.primary_field}`);
    console.log(`  Confidence: ${(result.confidence * 100).toFixed(1)}%`);
    console.log(`  Method: ${result.method}`);

    if (!isPass) {
      console.log(`  All matches:`, result.all_matches);
    }

    console.log('');
  });

  // Summary
  console.log('%c--- Test Summary ---', 'color: #2196F3; font-weight: bold');
  console.log(`Total Tests: ${tests.length}`);
  console.log(`%cPassed: ${passed}`, 'color: #4CAF50; font-weight: bold');
  if (failed > 0) {
    console.log(`%cFailed: ${failed}`, 'color: #f44336; font-weight: bold');
  }
  console.log(`Success Rate: ${((passed / tests.length) * 100).toFixed(1)}%`);
  console.log('');

  // Feature tests
  console.log('%c--- Feature Tests ---', 'color: #2196F3; font-weight: bold');
  console.log('');

  // Test 1: Normalization
  console.log('Test: Name Normalization');
  const normalized = detector.normalizeName('Zeitschrift für Physik & Chemie');
  console.log(`  Input: "Zeitschrift für Physik & Chemie"`);
  console.log(`  Output: "${normalized}"`);
  console.log(`  Expected: "ZEITSCHRIFT FUR PHYSIK CHEMIE"`);
  console.log(`  %c${normalized === 'ZEITSCHRIFT FUR PHYSIK CHEMIE' ? '✓ Pass' : '✗ Fail'}`,
    normalized === 'ZEITSCHRIFT FUR PHYSIK CHEMIE' ? 'color: #4CAF50' : 'color: #f44336');
  console.log('');

  // Test 2: Keyword Extraction
  console.log('Test: Keyword Extraction');
  const keywords = detector.extractKeywords('Journal of Applied Physics and Engineering');
  console.log(`  Input: "Journal of Applied Physics and Engineering"`);
  console.log(`  Keywords:`, keywords);
  console.log(`  Expected: Contains "APPLIED", "PHYSICS", "ENGINEERING"`);
  const hasExpected = keywords.includes('APPLIED') && keywords.includes('PHYSICS') && keywords.includes('ENGINEERING');
  console.log(`  %c${hasExpected ? '✓ Pass' : '✗ Fail'}`, hasExpected ? 'color: #4CAF50' : 'color: #f44336');
  console.log('');

  // Test 3: ISSN Classification
  console.log('Test: ISSN Classification (with hyphen)');
  const issnResult1 = detector.classifyByISSN('1745-2473');
  console.log(`  Input: "1745-2473" (with hyphen)`);
  console.log(`  Result:`, issnResult1 ? issnResult1.primary_field : 'Not found');
  console.log('');

  console.log('Test: ISSN Classification (without hyphen)');
  const issnResult2 = detector.classifyByISSN('17452473');
  console.log(`  Input: "17452473" (without hyphen)`);
  console.log(`  Result:`, issnResult2 ? issnResult2.primary_field : 'Not found');
  console.log('');

  // Test 4: Pattern Matching
  console.log('Test: Pattern Matching');
  const patternResult = detector.classifyByName('Quantum Computing Today');
  console.log(`  Input: "Quantum Computing Today"`);
  console.log(`  Primary Field: ${patternResult.primary_field}`);
  console.log(`  Confidence: ${(patternResult.confidence * 100).toFixed(1)}%`);
  console.log(`  All Matches:`, patternResult.all_matches.slice(0, 3));
  console.log('');

  // Test 5: Utility Methods
  console.log('Test: Utility Methods');
  const fields = detector.getSupportedFields();
  console.log(`  Supported Fields: ${fields.length} fields`);
  console.log(`  Sample:`, fields.slice(0, 5));
  console.log('');

  const hierarchy = detector.getCategoryHierarchy();
  console.log(`  Category Hierarchy:`, Object.keys(hierarchy));
  console.log('');

  const isValid = detector.isValidField('natural_sciences.physics');
  console.log(`  Is "natural_sciences.physics" valid? ${isValid ? '✓ Yes' : '✗ No'}`);
  console.log('');

  // Performance test
  console.log('%c--- Performance Test ---', 'color: #2196F3; font-weight: bold');
  console.log('');

  const perfTests = [
    'Nature Physics',
    'Journal of Applied Physics',
    'Chemical Reviews',
    'Cell Biology',
    'IEEE Computer'
  ];

  const startTime = performance.now();
  perfTests.forEach(name => {
    detector.detectField(name);
  });
  const endTime = performance.now();

  const avgTime = (endTime - startTime) / perfTests.length;
  console.log(`Tested ${perfTests.length} journals`);
  console.log(`Total time: ${(endTime - startTime).toFixed(2)}ms`);
  console.log(`Average per journal: ${avgTime.toFixed(2)}ms`);
  console.log(`Performance: %c${avgTime < 5 ? '✓ Excellent' : avgTime < 10 ? '✓ Good' : '⚠ Needs optimization'}`,
    avgTime < 5 ? 'color: #4CAF50' : avgTime < 10 ? 'color: #FF9800' : 'color: #f44336');
  console.log('');

  // Final result
  console.log('%c=== Test Complete ===', 'color: #4CAF50; font-size: 18px; font-weight: bold');
  if (failed === 0) {
    console.log('%c🎉 All tests passed!', 'color: #4CAF50; font-size: 16px');
  } else {
    console.log(`%c⚠ ${failed} test(s) failed. Review output above.`, 'color: #FF9800; font-size: 16px');
  }
  console.log('');
  console.log('To test custom input, use:');
  console.log('  testField("Your Journal Name", "ISSN-optional")');
  console.log('');
}

/**
 * Test a custom journal
 * @param {string} name - Journal name
 * @param {string} issn - Optional ISSN
 */
function testField(name, issn = '') {
  if (typeof FieldDetector === 'undefined') {
    console.error('FieldDetector is not loaded!');
    return;
  }

  const detector = new FieldDetector();
  const result = detector.detectField(name, issn);

  console.clear();
  console.log('%c=== Field Detection Result ===', 'color: #2196F3; font-size: 16px; font-weight: bold');
  console.log('');
  console.log(`Journal Name: ${name}`);
  if (issn) {
    console.log(`ISSN: ${issn}`);
  }
  console.log('');
  console.log(`Primary Field: %c${result.primary_field}`, 'color: #4CAF50; font-weight: bold');
  console.log(`Broad Category: ${result.broad_category}`);
  console.log(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
  console.log(`Detection Method: ${result.method}`);
  console.log('');

  if (result.all_matches && result.all_matches.length > 0) {
    console.log('All Matches:');
    console.table(result.all_matches.map(m => ({
      Field: m.field,
      'Score (%)': (m.score * 100).toFixed(1)
    })));
  }

  if (result.reason) {
    console.log('');
    console.log(`Note: ${result.reason}`);
  }
}

/**
 * Show detector info
 */
function showDetectorInfo() {
  if (typeof FieldDetector === 'undefined') {
    console.error('FieldDetector is not loaded!');
    return;
  }

  const detector = new FieldDetector();

  console.clear();
  console.log('%c=== FieldDetector Information ===', 'color: #2196F3; font-size: 16px; font-weight: bold');
  console.log('');
  console.log('Supported Fields:');

  const hierarchy = detector.getCategoryHierarchy();
  Object.entries(hierarchy).forEach(([category, subcategories]) => {
    console.log(`\n%c${category}`, 'color: #4CAF50; font-weight: bold');
    const fields = detector.getSupportedFields().filter(f => f.startsWith(category));
    fields.forEach(field => {
      console.log(`  • ${field}`);
    });
  });

  console.log('');
  console.log(`Total Fields: ${detector.getSupportedFields().length}`);
}

// Auto-run if in browser console
if (typeof window !== 'undefined') {
  console.log('%c📚 FieldDetector Test Script Loaded', 'color: #2196F3; font-size: 14px; font-weight: bold');
  console.log('');
  console.log('Available commands:');
  console.log('  runQuickTest()           - Run all tests');
  console.log('  testField(name, issn)    - Test a specific journal');
  console.log('  showDetectorInfo()       - Show detector information');
  console.log('');
  console.log('Example:');
  console.log('  testField("Nature Physics", "1745-2473")');
  console.log('');
}
