/**
 * MIT License
 *
 * Copyright (c) 2022 Julian R.K. Wichmann building upon
 * Copyright (c) 2025 Trung V.M Nguyen
 *                                            WenyanLiu (https://github.com/WenyanLiu/CCFrank4dblp), Kai Chen (https://github.com/FunClip)
 */


// ============================================================================
// FIELD DETECTION INTEGRATION: Added detectedField parameter
// This parameter is passed through to getRankSpan functions for field-aware
// ranking display. It's optional and backward compatible (defaults to null).
// ============================================================================
function fetchRank(node, title, compl, site, elid, author, journal_hint, settings, detectedField) {
    // Set default value for backward compatibility
    if (typeof detectedField === 'undefined') {
        detectedField = null;
    }

    // Handle argument shifting if journal_hint is missing (backward compatibility)
    // If journal_hint is passed as an object, it is likely the settings object
    if (typeof journal_hint === 'object' && journal_hint !== null) {
        if (typeof settings === 'undefined') {
            settings = journal_hint;
            journal_hint = "";
        }
    }

    // Helper function to proceed with DBLP search and rendering
    // This unifies the rendering logic for both API success and Local Fallback
    function proceedWithRendering(journalName, doi, issn1, issn2) {
        var dblp_venue = "";
        var dblp_doi = "";
        var xhrCORE = new XMLHttpRequest();
        var api_format2 = "https://dblp.org/search/publ/api?q=" + encodeURIComponent(title + " " + author) + "&format=json&h=1";

        xhrCORE.open("GET", api_format2, true);
        xhrCORE.onreadystatechange = function () {
           if (xhrCORE.readyState == 4) {
                try {
                    if (xhrCORE.status === 200) {
                        var resp = JSON.parse(xhrCORE.responseText).result.hits;
                        if (resp["@total"] >= 1) {
                            dblp_venue = resp.hit[0].info.venue;
                            dblp_doi = resp.hit[0].info.doi;
                        }
                    }
                } catch (e) {
                    // Ignore DBLP errors
                }

                for (let getRankSpan of site.rankSpanList) {
                    // FIELD DETECTION: Pass detectedField to getRankSpan for field-aware ranking
                    $(node).after(getRankSpan(journalName, "full_cap", doi, elid, issn1, issn2, dblp_venue, dblp_doi, settings, detectedField));
                }
            }
        };
        xhrCORE.send();
    }

    // Fallback to local 2025 Data (sfc.impactFactorsNames)
    function tryLocalFallback() {
        if (journal_hint && typeof sfc !== 'undefined' && sfc.impactFactorsNames) {
            // Clean the hint: remove ellipses, extra spaces, lowercase
            let cleanHint = journal_hint.replace(/[…\.]/g, "").trim().toLowerCase();

            // Safety check to avoid matching empty or very short strings
            if (cleanHint.length < 3) return;

            // Fuzzy/Prefix match
            for (let name in sfc.impactFactorsNames) {
                if (name.startsWith(cleanHint)) {
                    // Found a match!
                    let match = sfc.impactFactorsNames[name];
                    let issn = match.issn || "";

                    // Use the matched full name and ISSN
                    proceedWithRendering(name, "", issn, "");
                    return;
                }
            }
        }

        // If no local match found, continue with the provided hint or title
        // This ensures DBLP search still runs and other rankings (ABDC, CORE) are checked
        // and importantly, the spinner is removed.
        proceedWithRendering(journal_hint || title, "", "", "");
    }

    var xhr = new XMLHttpRequest();
    /* Public API */
    var api_format = "https://api.crossref.org/works?query.bibliographic=" + encodeURIComponent(title + " " + compl) + "&rows=2&select=DOI,container-title,ISSN";

    xhr.open("GET", api_format, true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            // Check for success (200 OK)
            if (xhr.status === 200) {
                try {
                    var resp = JSON.parse(xhr.responseText).message;

                    var url = "";
                    var doi = "";
                    var ISSN1 = "";
                    var ISSN2 = "";

                    if (resp["total-results"] == 0) {
                        // API returned no results -> Try Fallback
                        tryLocalFallback();
                        return;
                    }

                    // Extract data from response (Same logic as before)
                    if (resp["total-results"] == 1 & resp.items[0].hasOwnProperty("container-title")) {
                        url = resp.items[0]["container-title"][0];
                        doi = resp.items[0]["DOI"];
                        if( Array.isArray(resp.items[0]["ISSN"]) ) {
                            ISSN1 = resp.items[0]["ISSN"][0];
                            ISSN2 = resp.items[0]["ISSN"][1];
                        } else {
                            ISSN1 = resp.items[0]["ISSN"];
                        }
                    } else if (resp["total-results"] > 1 & resp.items[0].hasOwnProperty("container-title") & resp.items[1].hasOwnProperty("container-title")) {
                        if( resp.items[0]["container-title"][0] == "SSRN Electronic Journal" ) {
                            url = resp.items[1]["container-title"][0];
                            doi = resp.items[1]["DOI"];
                            if( Array.isArray(resp.items[1]["ISSN"]) ) {
                                ISSN1 = resp.items[1]["ISSN"][0];
                                ISSN2 = resp.items[1]["ISSN"][1];
                            } else {
                                ISSN1 = resp.items[1]["ISSN"];
                            }
                        } else {
                            url = resp.items[0]["container-title"][0];
                            doi = resp.items[0]["DOI"];
                            if( Array.isArray(resp.items[0]["ISSN"]) ) {
                                ISSN1 = resp.items[0]["ISSN"][0];
                                ISSN2 = resp.items[0]["ISSN"][1];
                            } else {
                                ISSN1 = resp.items[0]["ISSN"];
                            }
                        }
                    } else if (resp["total-results"] > 1 & resp.items[0].hasOwnProperty("container-title") & !resp.items[1].hasOwnProperty("container-title")) {
                        url = resp.items[0]["container-title"][0];
                        doi = resp.items[0]["DOI"];
                        if( Array.isArray(resp.items[0]["ISSN"]) ) {
                            ISSN1 = resp.items[0]["ISSN"][0];
                            ISSN2 = resp.items[0]["ISSN"][1];
                        } else {
                            ISSN1 = resp.items[0]["ISSN"];
                        }
                    }

                    // Clean DOI
                    if (doi) doi = doi.replaceAll('\\','');

                    // Proceed
                    proceedWithRendering(url, doi, ISSN1, ISSN2);

                } catch (e) {
                    console.error("Error parsing CrossRef response:", e);
                    tryLocalFallback();
                }
            } else {
                // Handle 429 Too Many Requests or other errors
                console.warn("CrossRef API Error (Status " + xhr.status + "). Falling back to local data.");
                tryLocalFallback();
            }
        }
    };
    xhr.send();
}
