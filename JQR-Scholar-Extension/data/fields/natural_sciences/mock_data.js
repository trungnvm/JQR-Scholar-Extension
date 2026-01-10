/**
 * Mock Data for Natural Sciences
 * Used for testing JQR extension
 */

if (typeof sfc === 'undefined') {
    var sfc = {};
}

// Ensure namespace structure exists
if (!sfc.fields) sfc.fields = {};
if (!sfc.fields.natural_sciences) sfc.fields.natural_sciences = {};

// Physics Journals
sfc.fields.natural_sciences.physics = {
    "17452473": { "name": "Nature Physics", "sjr": "Q1", "if": 19.6, "h_index": 250 },
    "00319007": { "name": "Physical Review Letters", "sjr": "Q1", "if": 8.1, "h_index": 700 },
    "00346861": { "name": "Reviews of Modern Physics", "sjr": "Q1", "if": 44.1, "h_index": 350 },
    "00036951": { "name": "Applied Physics Letters", "sjr": "Q1", "if": 4.0, "h_index": 450 },
    "13672630": { "name": "New Journal of Physics", "sjr": "Q1", "if": 3.2, "h_index": 180 }
};

// Chemistry Journals
sfc.fields.natural_sciences.chemistry = {
    "00027863": { "name": "Journal of the American Chemical Society", "sjr": "Q1", "if": 14.4, "h_index": 600 },
    "14337851": { "name": "Angewandte Chemie International Edition", "sjr": "Q1", "if": 16.1, "h_index": 550 },
    "00092665": { "name": "Chemical Reviews", "sjr": "Q1", "if": 62.1, "h_index": 400 },
    "17554330": { "name": "Nature Chemistry", "sjr": "Q1", "if": 21.8, "h_index": 200 },
    "21555435": { "name": "ACS Catalysis", "sjr": "Q1", "if": 11.3, "h_index": 180 }
};

// Biology Journals
sfc.fields.natural_sciences.biology = {
    "00928674": { "name": "Cell", "sjr": "Q1", "if": 64.5, "h_index": 850 },
    "00280836": { "name": "Nature", "sjr": "Q1", "if": 64.8, "h_index": 1300 },
    "00368075": { "name": "Science", "sjr": "Q1", "if": 56.9, "h_index": 1250 },
    "15460897": { "name": "PLOS Biology", "sjr": "Q1", "if": 9.8, "h_index": 280 },
    "09609822": { "name": "Current Biology", "sjr": "Q1", "if": 9.2, "h_index": 350 }
};

// Mathematics Journals
sfc.fields.natural_sciences.mathematics = {
    "0003486X": { "name": "Annals of Mathematics", "sjr": "Q1", "if": 4.9, "h_index": 120 },
    "08940347": { "name": "Journal of the American Mathematical Society", "sjr": "Q1", "if": 3.6, "h_index": 100 },
    "00209910": { "name": "Inventiones Mathematicae", "sjr": "Q1", "if": 2.8, "h_index": 110 },
    "00015962": { "name": "Acta Mathematica", "sjr": "Q1", "if": 2.5, "h_index": 90 }
};

// Populate Impact Factors for these journals
if (sfc.impactFactors) {
    const allJournals = {
        ...sfc.fields.natural_sciences.physics,
        ...sfc.fields.natural_sciences.chemistry,
        ...sfc.fields.natural_sciences.biology,
        ...sfc.fields.natural_sciences.mathematics
    };

    for (const [issn, data] of Object.entries(allJournals)) {
        if (!sfc.impactFactors[issn]) {
            sfc.impactFactors[issn] = {
                "value": data.if,
                "year": 2023,
                "source": "MockData",
                "quartile": data.sjr_q,
                "h_index": data.h_index
            };
        }
    }
}
