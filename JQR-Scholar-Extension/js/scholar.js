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

    // Only perform field detection if enabled and FieldDetector is available
    if (fieldDetectionEnabled && fieldDetector) {
        try {
            // Call FieldDetector to identify the field based on journal name
            // ISSN is not available at this stage (only journal name from metadata)
            detectedField = fieldDetector.detectField(journal3, null);

            if (detectedField && detectedField !== 'unknown') {
                console.log('[Scholar Field Detection] Detected field for "' + journal3 + '": ' + detectedField);

                // Display field badge before ranking badges (optional feature)
                if (settings && settings.showFieldBadge !== false) {
                    const fieldBadge = createFieldBadge(detectedField);
                    if (fieldBadge) {
                        $(node).append(fieldBadge);
                    }
                }
            }
        } catch (error) {
            console.warn('[Scholar Field Detection] Error detecting field:', error);
            detectedField = null;
        }
    }
    // ========================================================================

    let position_start = ccf.FullRank_Names.indexOf("X_X" + url + "\1/");

    if (position_start != -1) {
        for (let getRankSpan of scholar.rankSpanList) {
                let doi = "";
                // Pass detected field to getRankSpan function for field-aware ranking
                $(node).after(getRankSpan(journal3, "full_cap", doi, elid, "", "", "", "", settings, detectedField)); }
    } else {
        fetchRank(node, title, compl, scholar, elid, author, settings, detectedField);
        }
};


scholar.rankSpanList = [];

scholar.run = function (settings) {
    // ========================================================================
    // FIELD DETECTION: Load settings at startup
    // ========================================================================
    // Initialize field detection based on user settings
    loadFieldDetectionSettings();
    // ========================================================================

    let url = window.location.pathname;
    let full_url = window.location.href;
    if (url == "/scholar") {
        scholar.appendRank(full_url, settings);
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
        let elid_id = elid;
        elid += "_wait_surr";
        let span_wait = $('<span title="Fetching results from CrossRef API..." id="waiting" class="ccf-waiting">');
        let span_wait_surr = $('<span id="id" class="ccf-waiting_surr ccf-rank">')
            .append(span_wait)
            .attr("id",elid);
        node
            .append(span_wait_surr);
            
                    
        let journal = $(this)
            .find("div.gs_a")
            .text();

        let r1 = journal.indexOf(String.fromCharCode(160) + "- ");
        let journal2 = journal.substring(r1+3);
        let r2 = journal2.indexOf(" - ");

        journal3 = journal.substring(r1+3, r1+3+r2); 
        journal3 = journal3.replace(/, \d\d\d\d/, "");
                
        full_url = "https://scholar.google.com/scholar"
        let cite_link = full_url + "?q=info:" + elid_id + ":scholar.google.com/&output=cite&scirp=8&hl=de";
  
        let r3 = journal3.indexOf("…");
           
        if(r3 == -1) {
            CircumventCrossRef(journal3, node, title, compl, scholar, elid, author, settings);

        } else {
                    fetchRank(node, title, compl, scholar, elid, author, journal3, settings);
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