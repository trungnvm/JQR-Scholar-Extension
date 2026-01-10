/**
 * Field Detection Module for Scholar Field Classifier (SFC)
 *
 * Purpose: Automatically detect academic field/discipline from journal name and ISSN
 * Implements client-side field classification to organize journal rankings by discipline
 *
 * @author Scholar Field Classifier Team
 * @date 2026-01-10
 * @version 1.0.0
 * @license MIT
 *
 * Dependencies:
 * - jQuery 3.5.1+ (for DOM manipulation if needed)
 * - sfc.issnFieldMapping (external data mapping ISSN to fields)
 */

/**
 * FieldDetector class - Main field detection and classification engine
 *
 * This class provides methods to automatically detect the academic field/discipline
 * of a journal based on its name and/or ISSN. It uses a multi-tier detection strategy:
 * 1. ISSN-based lookup (most reliable)
 * 2. Name pattern matching (regex-based)
 * 3. Keyword extraction and analysis (fallback)
 *
 * @class FieldDetector
 * @example
 * const detector = new FieldDetector();
 * const result = detector.detectField("Nature Physics", "1745-2473");
 * console.log(result.primary_field); // "natural_sciences.physics"
 */
class FieldDetector {
    /**
     * Initialize the FieldDetector with pattern definitions and field mappings
     * @constructor
     */
    constructor() {
        /**
         * Field classification patterns using regular expressions
         * Organized by broad category and specific field
         * Patterns are case-insensitive and use word boundaries for accuracy
         *
         * @type {Object}
         * @property {RegExp} pattern - Regular expression for field detection
         * @property {number} weight - Confidence weight for pattern match (0-1)
         */
        this.fieldPatterns = {
            // Natural Sciences
            'natural_sciences.physics': {
                pattern: /\b(PHYSICS|PHYSICAL|QUANTUM|PARTICLE|NUCLEAR|PLASMA|OPTICS|OPTICAL|PHOTONICS|ASTROPHYS|COSMOLOGY|CONDENSED MATTER|SOLID STATE)\b/i,
                weight: 0.9
            },
            'natural_sciences.chemistry': {
                pattern: /\b(CHEMISTRY|CHEMICAL|MOLECULAR|CATALYSIS|ORGANIC|INORGANIC|ANALYTICAL|BIOCHEM|ELECTROCHEMISTRY|POLYMER)\b/i,
                weight: 0.9
            },
            'natural_sciences.biology': {
                pattern: /\b(BIOLOGY|BIOLOGICAL|CELL|CELLULAR|MOLECULAR BIOLOGY|GENETICS|GENOMICS|BIOINFORMATICS|MICROBIOLOGY|ECOLOGY|EVOLUTION|NEUROSCIENCE)\b/i,
                weight: 0.9
            },
            'natural_sciences.mathematics': {
                pattern: /\b(MATHEMATICS|MATHEMATICAL|ALGEBRA|GEOMETRY|TOPOLOGY|CALCULUS|STATISTICS|STATISTICAL|PROBABILITY|NUMBER THEORY|APPLIED MATH)\b/i,
                weight: 0.9
            },
            'natural_sciences.earth_sciences': {
                pattern: /\b(GEOLOGY|GEOLOGICAL|GEOPHYSICS|GEOCHEMISTRY|EARTH|ATMOSPHERIC|OCEANOGRAPHY|CLIMATE|ENVIRONMENTAL|METEOROLOGY|PALEONTOLOGY)\b/i,
                weight: 0.85
            },

            // Engineering and Technology
            'engineering.computer_science': {
                pattern: /\b(COMPUTER|COMPUTING|COMPUTATIONAL|INFORMATION|SOFTWARE|ALGORITHM|ARTIFICIAL INTELLIGENCE|MACHINE LEARNING|DATA SCIENCE|CYBERSECURITY|PROGRAMMING)\b/i,
                weight: 0.9
            },
            'engineering.electrical': {
                pattern: /\b(ELECTRICAL|ELECTRONIC|ELECTRONICS|CIRCUIT|MICROELECTRONICS|SEMICONDUCTOR|SIGNAL PROCESSING|TELECOMMUNICATIONS|WIRELESS)\b/i,
                weight: 0.85
            },
            'engineering.mechanical': {
                pattern: /\b(MECHANICAL|MECHANICS|THERMODYNAMICS|FLUID|ROBOTICS|MANUFACTURING|AEROSPACE|AUTOMOTIVE|TRIBOLOGY)\b/i,
                weight: 0.85
            },
            'engineering.civil': {
                pattern: /\b(CIVIL|STRUCTURAL|CONSTRUCTION|GEOTECHNICAL|TRANSPORTATION|INFRASTRUCTURE|HYDRAULIC)\b/i,
                weight: 0.85
            },
            'engineering.materials': {
                pattern: /\b(MATERIALS|MATERIAL SCIENCE|NANOMATERIAL|BIOMATERIAL|COMPOSITE|METALLURGY|CERAMICS)\b/i,
                weight: 0.85
            },
            'engineering.general': {
                pattern: /\b(ENGINEERING|TECHNICAL|APPLIED)\b/i,
                weight: 0.6  // Lower weight as it's very broad
            },

            // Medical and Health Sciences
            'medical.clinical': {
                pattern: /\b(MEDICINE|MEDICAL|CLINICAL|SURGERY|CARDIOLOGY|ONCOLOGY|NEUROLOGY|PEDIATRICS|RADIOLOGY|PATHOLOGY)\b/i,
                weight: 0.9
            },
            'medical.public_health': {
                pattern: /\b(HEALTH|PUBLIC HEALTH|EPIDEMIOLOGY|HEALTHCARE|NURSING|PHARMACY|PHARMACOLOGY|TOXICOLOGY)\b/i,
                weight: 0.85
            },

            // Social Sciences
            'social_sciences.economics': {
                pattern: /\b(ECONOMICS|ECONOMIC|ECONOMETRICS|FINANCE|FINANCIAL|BUSINESS|MANAGEMENT|MARKETING|ACCOUNTING)\b/i,
                weight: 0.9
            },
            'social_sciences.psychology': {
                pattern: /\b(PSYCHOLOGY|PSYCHOLOGICAL|COGNITIVE|BEHAVIORAL|PSYCHIATRY)\b/i,
                weight: 0.9
            },
            'social_sciences.sociology': {
                pattern: /\b(SOCIOLOGY|SOCIOLOGICAL|SOCIAL|ANTHROPOLOGY|DEMOGRAPHY)\b/i,
                weight: 0.85
            },
            'social_sciences.education': {
                pattern: /\b(EDUCATION|EDUCATIONAL|PEDAGOGY|TEACHING|LEARNING)\b/i,
                weight: 0.85
            },
            'social_sciences.political': {
                pattern: /\b(POLITICAL|POLITICS|POLICY|GOVERNANCE|INTERNATIONAL RELATIONS|PUBLIC ADMINISTRATION)\b/i,
                weight: 0.85
            },

            // Humanities
            'humanities.literature': {
                pattern: /\b(LITERATURE|LITERARY|LINGUISTICS|LANGUAGE|PHILOLOGY)\b/i,
                weight: 0.9
            },
            'humanities.history': {
                pattern: /\b(HISTORY|HISTORICAL|ARCHAEOLOGY|HERITAGE)\b/i,
                weight: 0.9
            },
            'humanities.philosophy': {
                pattern: /\b(PHILOSOPHY|PHILOSOPHICAL|ETHICS|RELIGION|THEOLOGY)\b/i,
                weight: 0.9
            },
            'humanities.arts': {
                pattern: /\b(ARTS|ART|MUSIC|MUSICOLOGY|DESIGN|ARCHITECTURE)\b/i,
                weight: 0.85
            },

            // Multidisciplinary
            'multidisciplinary': {
                pattern: /\b(SCIENCE|NATURE|PROCEEDINGS|ACADEMY|RESEARCH|PLOS|SCIENTIFIC)\b/i,
                weight: 0.3  // Very low weight as these are ambiguous
            }
        };

        /**
         * Mapping of broad categories to their subcategories
         * Used for hierarchical classification
         * @type {Object}
         */
        this.categoryMapping = {
            'natural_sciences': ['physics', 'chemistry', 'biology', 'mathematics', 'earth_sciences'],
            'engineering': ['computer_science', 'electrical', 'mechanical', 'civil', 'materials', 'general'],
            'medical': ['clinical', 'public_health'],
            'social_sciences': ['economics', 'psychology', 'sociology', 'education', 'political'],
            'humanities': ['literature', 'history', 'philosophy', 'arts'],
            'multidisciplinary': []
        };

        /**
         * Reference to external ISSN-to-field mapping
         * This should be populated from sfc.issnFieldMapping if available
         * @type {Object}
         */
        this.issnFieldMapping = (typeof sfc !== 'undefined' && sfc.issnFieldMapping) ? sfc.issnFieldMapping : {};

        /**
         * Stop words to exclude from keyword extraction
         * Common words that don't help with field classification
         * @type {Array<string>}
         */
        this.stopWords = [
            'JOURNAL', 'OF', 'THE', 'AND', 'FOR', 'IN', 'ON', 'WITH',
            'A', 'AN', 'TO', 'FROM', 'BY', 'AT', 'AS', 'OR',
            'INTERNATIONAL', 'AMERICAN', 'EUROPEAN', 'BRITISH', 'ROYAL',
            'SOCIETY', 'ASSOCIATION', 'INSTITUTE', 'REVIEW', 'REVIEWS',
            'LETTERS', 'COMMUNICATIONS', 'TRANSACTIONS', 'PROCEEDINGS',
            'ADVANCES', 'REPORTS', 'BULLETIN', 'ANNALS'
        ];
    }

    /**
     * Main detection method - Detects academic field from journal name and ISSN
     *
     * Uses a tiered approach:
     * 1. First tries ISSN lookup (if ISSN provided)
     * 2. Then tries pattern matching on journal name
     * 3. Falls back to keyword-based classification
     *
     * @param {string} journalName - Name of the journal (e.g., "Nature Physics")
     * @param {string} [issn] - ISSN of the journal (optional, e.g., "1745-2473")
     * @returns {Object} Detection result with field, confidence, and matches
     * @returns {string} returns.primary_field - Primary field classification (e.g., "natural_sciences.physics")
     * @returns {string} returns.broad_category - Broad category (e.g., "natural_sciences")
     * @returns {number} returns.confidence - Confidence score (0-1)
     * @returns {Array<Object>} returns.all_matches - All matched fields with scores
     * @returns {string} returns.method - Detection method used ("issn", "pattern", or "keyword")
     *
     * @example
     * const result = detector.detectField("Journal of the American Chemical Society", "0002-7863");
     * // Returns: {
     * //   primary_field: "natural_sciences.chemistry",
     * //   broad_category: "natural_sciences",
     * //   confidence: 0.95,
     * //   all_matches: [...],
     * //   method: "issn"
     * // }
     */
    detectField(journalName, issn) {
        // Validate inputs
        if (!journalName || typeof journalName !== 'string') {
            return this._createUnknownResult('Invalid journal name');
        }

        // Method 1: ISSN-based lookup (most reliable)
        if (issn) {
            const issnResult = this.classifyByISSN(issn);
            if (issnResult && issnResult.primary_field !== 'unknown') {
                issnResult.method = 'issn';
                return issnResult;
            }
        }

        // Method 2: Pattern-based matching
        const patternResult = this.classifyByName(journalName);
        if (patternResult && patternResult.confidence > 0.5) {
            patternResult.method = 'pattern';
            return patternResult;
        }

        // Method 3: Keyword-based classification (fallback)
        const keywords = this.extractKeywords(journalName);
        const keywordResult = this.classifyByKeywords(keywords);
        keywordResult.method = 'keyword';
        return keywordResult;
    }

    /**
     * Normalize journal name for consistent matching
     * - Converts to uppercase
     * - Removes accents/diacritics (NFD normalization)
     * - Removes special characters except spaces
     *
     * @param {string} name - Raw journal name
     * @returns {string} Normalized journal name
     *
     * @example
     * normalizeName("Zeitschrift für Physik") // Returns: "ZEITSCHRIFT FUR PHYSIK"
     */
    normalizeName(name) {
        if (!name || typeof name !== 'string') {
            return '';
        }

        return name
            .toUpperCase()
            .normalize('NFD')  // Decompose accented characters
            .replace(/[\u0300-\u036f]/g, '')  // Remove diacritics
            .replace(/[^A-Z0-9\s]/g, ' ')  // Keep only alphanumeric and spaces
            .replace(/\s+/g, ' ')  // Collapse multiple spaces
            .trim();
    }

    /**
     * Classify journal by ISSN lookup
     *
     * Looks up the ISSN in the pre-built issnFieldMapping database.
     * ISSNs are normalized (hyphens removed) before lookup.
     *
     * @param {string} issn - Journal ISSN (with or without hyphen)
     * @returns {Object|null} Classification result or null if not found
     *
     * @example
     * classifyByISSN("1745-2473") // Nature Physics ISSN
     * // Returns: {
     * //   primary_field: "natural_sciences.physics",
     * //   broad_category: "natural_sciences",
     * //   confidence: 0.95,
     * //   all_matches: [...]
     * // }
     */
    classifyByISSN(issn) {
        if (!issn || typeof issn !== 'string') {
            return null;
        }

        // Normalize ISSN: remove hyphens and convert to uppercase
        const normalizedISSN = issn.replace(/[^A-Z0-9]/gi, '').toUpperCase();

        if (this.issnFieldMapping && this.issnFieldMapping[normalizedISSN]) {
            const fieldData = this.issnFieldMapping[normalizedISSN];

            // If fieldData is a string (simple mapping)
            if (typeof fieldData === 'string') {
                return this._createResult(fieldData, 0.95, [{field: fieldData, score: 0.95}]);
            }

            // If fieldData is an object with detailed info
            if (typeof fieldData === 'object') {
                return {
                    primary_field: fieldData.primary_field || fieldData.field || 'unknown',
                    broad_category: fieldData.broad_category || this._getBroadCategory(fieldData.primary_field || fieldData.field),
                    confidence: fieldData.confidence || 0.95,
                    all_matches: fieldData.all_fields || [{field: fieldData.primary_field || fieldData.field, score: 0.95}]
                };
            }
        }

        return null;
    }

    /**
     * Classify journal by name using pattern matching
     *
     * Tests the journal name against all defined field patterns.
     * Returns the best matching field(s) with confidence scores.
     *
     * @param {string} name - Journal name
     * @returns {Object} Classification result with matches
     *
     * @example
     * classifyByName("Journal of Applied Physics")
     * // Returns: {
     * //   primary_field: "natural_sciences.physics",
     * //   broad_category: "natural_sciences",
     * //   confidence: 0.9,
     * //   all_matches: [...]
     * // }
     */
    classifyByName(name) {
        const normalizedName = this.normalizeName(name);
        const matches = [];

        // Test against all patterns
        for (const [field, {pattern, weight}] of Object.entries(this.fieldPatterns)) {
            if (pattern.test(normalizedName)) {
                matches.push({
                    field: field,
                    score: weight
                });
            }
        }

        // Sort matches by score (descending)
        matches.sort((a, b) => b.score - a.score);

        // If we have matches, return the best one
        if (matches.length > 0) {
            const bestMatch = matches[0];
            return this._createResult(bestMatch.field, bestMatch.score, matches);
        }

        // No matches found
        return this._createUnknownResult('No pattern matches found');
    }

    /**
     * Extract meaningful keywords from journal name
     *
     * Removes stop words and extracts significant terms that can
     * help identify the field. Preserves multi-word phrases.
     *
     * @param {string} name - Journal name
     * @returns {Array<string>} Array of extracted keywords
     *
     * @example
     * extractKeywords("Journal of Applied Physics")
     * // Returns: ["APPLIED", "PHYSICS"]
     */
    extractKeywords(name) {
        const normalizedName = this.normalizeName(name);
        const words = normalizedName.split(/\s+/);

        // Filter out stop words
        const keywords = words.filter(word =>
            word.length > 2 && !this.stopWords.includes(word)
        );

        return keywords;
    }

    /**
     * Classify journal by keywords extracted from name
     *
     * Uses keyword matching as a fallback when pattern matching fails.
     * Lower confidence than pattern matching.
     *
     * @param {Array<string>} keywords - Extracted keywords
     * @returns {Object} Classification result
     *
     * @example
     * classifyByKeywords(["QUANTUM", "COMPUTING"])
     * // Returns: {
     * //   primary_field: "natural_sciences.physics",
     * //   broad_category: "natural_sciences",
     * //   confidence: 0.7,
     * //   all_matches: [...]
     * // }
     */
    classifyByKeywords(keywords) {
        if (!keywords || keywords.length === 0) {
            return this._createUnknownResult('No keywords available');
        }

        const fieldScores = {};

        // Score each field based on keyword matches
        for (const keyword of keywords) {
            for (const [field, {pattern, weight}] of Object.entries(this.fieldPatterns)) {
                if (pattern.test(keyword)) {
                    fieldScores[field] = (fieldScores[field] || 0) + weight;
                }
            }
        }

        // Convert to matches array
        const matches = Object.entries(fieldScores).map(([field, score]) => ({
            field: field,
            score: Math.min(score / keywords.length, 0.85)  // Normalize and cap at 0.85
        }));

        // Sort by score
        matches.sort((a, b) => b.score - a.score);

        if (matches.length > 0) {
            const bestMatch = matches[0];
            return this._createResult(bestMatch.field, bestMatch.score * 0.8, matches);  // Reduce confidence for keyword matching
        }

        return this._createUnknownResult('No keyword matches found');
    }

    /**
     * Helper: Create a formatted result object
     *
     * @private
     * @param {string} field - Primary field classification
     * @param {number} confidence - Confidence score (0-1)
     * @param {Array<Object>} allMatches - All matched fields
     * @returns {Object} Formatted result object
     */
    _createResult(field, confidence, allMatches) {
        return {
            primary_field: field,
            broad_category: this._getBroadCategory(field),
            confidence: Math.min(Math.max(confidence, 0), 1),  // Clamp to [0, 1]
            all_matches: allMatches || []
        };
    }

    /**
     * Helper: Create an "unknown" result when classification fails
     *
     * @private
     * @param {string} reason - Reason for unknown classification
     * @returns {Object} Unknown result object
     */
    _createUnknownResult(reason) {
        return {
            primary_field: 'unknown',
            broad_category: 'unknown',
            confidence: 0,
            all_matches: [],
            reason: reason
        };
    }

    /**
     * Helper: Extract broad category from full field name
     *
     * @private
     * @param {string} field - Full field name (e.g., "natural_sciences.physics")
     * @returns {string} Broad category (e.g., "natural_sciences")
     */
    _getBroadCategory(field) {
        if (!field || typeof field !== 'string') {
            return 'unknown';
        }

        // Split by dot and take first part
        const parts = field.split('.');
        return parts[0] || 'unknown';
    }

    /**
     * Get all supported fields
     *
     * @returns {Array<string>} Array of all supported field names
     */
    getSupportedFields() {
        return Object.keys(this.fieldPatterns);
    }

    /**
     * Get category hierarchy
     *
     * @returns {Object} Category to subcategories mapping
     */
    getCategoryHierarchy() {
        return this.categoryMapping;
    }

    /**
     * Check if a field is valid
     *
     * @param {string} field - Field name to validate
     * @returns {boolean} True if field is valid
     */
    isValidField(field) {
        return this.fieldPatterns.hasOwnProperty(field);
    }
}

/**
 * Export for use in extension
 * Creates a global instance if needed
 */
if (typeof window !== 'undefined') {
    window.FieldDetector = FieldDetector;
}

/**
 * Compatibility with CommonJS/Node.js
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FieldDetector;
}
