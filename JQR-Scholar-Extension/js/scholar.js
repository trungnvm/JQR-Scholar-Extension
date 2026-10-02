/**
 * MIT License
 *
 * Copyright (c) 2022 Julian R.K. Wichmann building upon
 * Copyright (c) 2025 Trung V.M Nguyen
 *                                            WenyanLiu (https://github.com/WenyanLiu/CCFrank4dblp), Kai Chen (https://github.com/FunClip)
 */


const scholar = {};

// ============================================================================
// FIELD DETECTION INTEGRATION
// ============================================================================
// Global field detector instance (initialized when settings allow)
let fieldDetector = null;
let fieldDetectionEnabled = false;

// Initialize field detector based on user settings
function initializeFieldDetector() {
    // Check if FieldDetector class is available
    if (typeof FieldDetector !== 'undefined') {
        try {
            fieldDetector = new FieldDetector();
            console.log('[Scholar Field Detection] FieldDetector initialized successfully');
        } catch (error) {
            console.warn('[Scholar Field Detection] Failed to initialize FieldDetector:', error);
            fieldDetector = null;
        }
    } else {
        console.warn('[Scholar Field Detection] FieldDetector class not found - field detection disabled');
    }
}

// Load field detection settings from browser storage
function loadFieldDetectionSettings() {
    browserAPI.storage.local.get(['fieldClassification'], function(result) {
        fieldDetectionEnabled = result.fieldClassification === true;

        if (fieldDetectionEnabled) {
            console.log('[Scholar Field Detection] Field-based classification enabled');
            initializeFieldDetector();
        } else {
            console.log('[Scholar Field Detection] Field-based classification disabled in settings');
        }
    });
}

// Helper function to create field badge HTML
function createFieldBadge(field) {
    if (!field || field === 'unknown') {
        return '';
    }

    // Extract display name from field (e.g., "natural_sciences.physics" -> "Physics")
    let displayName = field;
    if (field.includes('.')) {
        displayName = field.split('.').pop();
    }
    displayName = displayName.charAt(0).toUpperCase() + displayName.slice(1).replace(/_/g, ' ');

    // Create badge with subtle styling
    const badge = $('<span class="field-badge ccf-rank"></span>')
        .text('[' + displayName + ']')
        .attr('title', 'Detected field: ' + field)
        .css({
            'background-color': '#e8f4f8',
            'color': '#1a5490',
            'border': '1px solid #b3d9f0',
            'padding': '2px 6px',
            'margin-right': '4px',
            'border-radius': '3px',
            'font-size': '11px',
            'font-weight': 'normal',
            'display': 'inline-block'
        });

    return badge;
}
// ============================================================================

// Helper function to robustly extract journal name from div.gs_a text
function extractJournalInfo(gs_a_text) {
    if (!gs_a_text) return { name: "", hasEllipsis: false };
    // Normalize special whitespaces and non-breaking spaces (\u00A0)
    let cleanText = gs_a_text.replace(/[\u00A0\u1680\u2000-\u200a\u202f\u205f\u3000]/g, " ").trim();
    let parts = cleanText.split(/\s+[-–—]\s+/);
    if (parts.length >= 2) {
        let venuePart = parts[1].trim();
        // If venuePart is just a 4-digit year, there's no venue name
        if (/^\d{4}$/.test(venuePart)) {
            return { name: "", hasEllipsis: false };
        }
        let hasEllipsis = venuePart.includes("…") || venuePart.includes("...");
        let jName = venuePart.replace(/,\s*\d{4}(\s*[-–—].*)?$/, "").replace(/\s+\d{4}$/, "").trim();
        jName = jName.replace(/[…\.]+$/, "").trim();
        return { name: jName, hasEllipsis: hasEllipsis };
    }
    return { name: "", hasEllipsis: false };
}

CircumventCrossRef = function (journal3, node, title, compl, scholar, elid, author, settings) {
    let url;

    url = journal3;

    url = url.toUpperCase();
    url = url.replace(/&AMP;/g, "&");
    url = url.replace(/ AND /g, "");
    url = url.replace(/^THE /g, "");
    url = url.replace(/, THE$/g, "");
    url = url.normalize('NFD');
    url = url.replace(/[^A-Z0-9]/ig, "");

    // ========================================================================
    // FIELD DETECTION: Detect field from journal name
    // ========================================================================
    let detectedField = null;

    if (fieldDetectionEnabled && fieldDetector) {
        try {
            detectedField = fieldDetector.detectField(journal3, null);
            if (detectedField && detectedField !== 'unknown') {
                if (settings && settings.showFieldBadge !== false) {
                    const fieldBadge = createFieldBadge(detectedField);
                    if (fieldBadge) {
                        $(node).append(fieldBadge);
                    }
                }
            }
        } catch (error) {
            detectedField = null;
        }
    }
    // ========================================================================

    // 1. Check Local Dictionaries First (0ms, no network, no rate-limit!)
    let position_start = (typeof ccf.FullRank_Names !== 'undefined') ? ccf.FullRank_Names.indexOf("X_X" + url + "\1/") : -1;
    let ifData = (typeof ccf.getImpactFactorByName === 'function') ? ccf.getImpactFactorByName(journal3) : null;
    let isLocalHit = (position_start != -1) || (ifData && ifData.value);

    if (isLocalHit) {
        let doi = "";
        let issn1 = (ifData && ifData.issn) ? ifData.issn : "";
        for (let getRankSpan of scholar.rankSpanList) {
            $(node).after(getRankSpan(journal3, "full_cap", doi, elid, issn1, "", "", "", settings, detectedField));
        }
        let spinner = document.getElementById(elid);
        if (spinner) spinner.remove();
    } else {
        // Fallback to API search with timeout
        fetchRank(node, title, compl, scholar, elid, author, journal3, settings, detectedField);
    }
};


scholar.rankSpanList = [];

scholar.run = function (settings) {
    loadFieldDetectionSettings();

    let url = window.location.pathname;
    let full_url = window.location.href;

    if (url == "/scholar") {
        scholar.appendRank(full_url, settings);

        // Dynamic observer for infinite scroll / lazy-loaded results
        let debounceTimer = null;
        const triggerUpdate = function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function () {
                scholar.appendRank(full_url, settings);
            }, 250);
        };

        const target = document.getElementById("gs_res_ccl_mid") || document.body;
        if (target) {
            const observer = new MutationObserver(function (mutations) {
                let hasNewNodes = false;
                for (let m of mutations) {
                    if (m.addedNodes && m.addedNodes.length > 0) {
                        hasNewNodes = true;
                        break;
                    }
                }
                if (hasNewNodes) triggerUpdate();
            });
            observer.observe(target, { childList: true, subtree: true });
        }

        // Scroll listener for seamless infinite scroll
        window.addEventListener("scroll", triggerUpdate, { passive: true });

    } else if (url == "/citations") {
        scholar.appendRanks(settings);
        $("#gsc_bpf_more").click( function() {
            setTimeout( function() {
                 scholar.appendRanks(settings)
            }, 1000);
        });
    }
};


function ajax(cite_link) {
 return new Promise(function(resolve, reject) {       
    $.get(cite_link, function(data, status){
        resolve(data);
        reject("");
    }, "text");
});
};


scholar.appendRank = function (full_url, settings) {
    let elements = $("#gs_res_ccl_mid > div > div.gs_ri");
    elements.each( async function () {
        if ($(this).attr("data-jqr-processed") === "true") {
            return;
        }
        $(this).attr("data-jqr-processed", "true");

        let node = $(this).find("h3 > a");
        let title = node.text();
        let compl = $(this)
            .find("div.gs_a")
            .text()
            .replace(/(<([^>]+)>)/gi, "")
            .replace("&nbsp;", "");
        
        let data = $(this)
            .find("div.gs_a")
            .text()
            .replace(/[\,\-\…]/g, "")
            .split(" ");
        let author = data[1];
        
        let elid = $(node).attr("id");
        if (!elid) {
            elid = "jqr_" + Math.random().toString(36).substring(2, 9);
            $(node).attr("id", elid);
        }
        let elid_id = elid;
        elid += "_wait_surr";
        let span_wait = $('<span title="Fetching results from JQR database..." id="waiting" class="ccf-waiting">');
        let span_wait_surr = $('<span id="id" class="ccf-waiting_surr ccf-rank">')
            .append(span_wait)
            .attr("id",elid);
        node.append(span_wait_surr);
            
        let gs_a_text = $(this).find("div.gs_a").text();
        let jInfo = extractJournalInfo(gs_a_text);
        let journal3 = jInfo.name;

        if (journal3 && journal3 !== "") {
            CircumventCrossRef(journal3, node, title, compl, scholar, elid, author, settings);
        } else {
            fetchRank(node, title, compl, scholar, elid, author, "", settings);
        }
    });
};

scholar.appendRanks = function (settings) {
    let elements = $("tr.gsc_a_tr");
    let i = 1;
    elements.each(async function () {
        let node = $(this).find("td.gsc_a_t > a").first();
        if (!node.hasClass("done")) {
            node
                .addClass("done");
            let title = node.text();
            let author = $(this)
                .find("div.gs_gray")
                .text()
                .replace(/[\,\…]/g, "")
                .split(" ")[1];
            let year = $(this).find("td.gsc_a_y").text();
            let compl = $(this)
                .find("div.gs_gray")
                .text()
                .replace(/(<([^>]+)>)/gi, "")
                .replace("&nbsp;", "");
                
            let elid = i;
            elid += "_wait_surr";
            let span_wait = $('<span title="Fetching results from CrossRef API..." id="waiting" class="ccf-waiting">');
            let span_wait_surr = $('<span id="id" class="ccf-waiting_surr ccf-rank">')
                .append(span_wait)
                .attr("id",elid);
            node
                .append(span_wait_surr);
            
                              
        let journal = $(this)
            .find("div.gs_gray").last()
            .text();

        let journal3 = journal.replace(/[^A-Z ]/ig, "");
        journal3 = journal3.replace(/^\s+|\s+$|\s+(?=\s)/g, "");

        let r3 = journal3.indexOf("…");
                
        if(r3 == -1) {
            CircumventCrossRef(journal3, node, title, compl, scholar, elid, author, settings);
        } else {
            fetchRank(node, title, compl, scholar, elid, author, journal3, settings);
        }
        
      }
      i = i+1;
    });
};