# Impact Factor Data

This directory contains Impact Factor data for journals displayed by the extension.

## File Structure

### impact_factors.js & impact_factors_names.js

- `impact_factors.js`: Contains Impact Factor data indexed by 8-character clean ISSN/eISSN (39,900+ entries).
- `impact_factors_names.js`: Contains Impact Factor data indexed by normalized journal names and aliases (70,200+ entries).
- Data source: Clarivate JCR (Journal Citation Reports) updated with `2026-newJCRimpactfactor.xlsx` (2025 JCR release metrics).
- Regeneration script: `utils/update_jcr_2026.py`

Each entry includes:

```javascript
"ISSN": {
    "value": "109.0",     // Impact Factor value
    "year": 2025,         // JCR Year
    "source": "JCR",      // Source
    "quartile": "Q1",     // Journal quartile
    "name": "LANCET"      // Journal name
}
```

## Color Coding

Impact Factor badges are color-coded based on their value:

- **IF >= 10**: Green (#00cc00) - Excellent
- **IF >= 5**: Light green (#66cc00) - Very Good
- **IF >= 3**: Yellow (#cccc00) - Good
- **IF >= 1**: Orange (#ff9900) - Moderate
- **IF < 1**: Red (#ff6666) - Low

## Adding New Journals

To add Impact Factor data for a new journal:

1. Find the journal's ISSN (remove any hyphens)
2. Add an entry to the `sfc.impactFactors` object in `impact_factors.js`:

```javascript
"12345678": {
    "value": 8.5,
    "year": 2023,
    "source": "JCR",
    "quartile": "Q1",
    "h_index": 120
}
```

## User Settings

Users can enable/disable Impact Factor display via browser settings:
- Setting key: `impactFactor`
- Default: `true` (enabled)

## Backward Compatibility

The extension will work correctly even if:
- The `impact_factors.js` file is missing
- A journal's ISSN is not in the Impact Factor database
- Impact Factor data is incomplete for a journal

In these cases, no Impact Factor badge will be displayed for that journal.
