/**
 * MIT License
 *
 * Copyright (c) 2022 Julian R.K. Wichmann building upon 
 *                                            WenyanLiu (https://github.com/WenyanLiu/CCFrank4dblp), Kai Chen (https://github.com/FunClip)
 */


const scholar_turbo = {};

// Helper function to robustly extract journal name from div.gs_a text
function extractJournalInfo(gs_a_text) {
    if (!gs_a_text) return { name: "", hasEllipsis: false };
    let cleanText = gs_a_text.replace(/[\u00A0\u1680\u2000-\u200a\u202f\u205f\u3000]/g, " ").trim();
    let parts = cleanText.split(/\s+[-–—]\s+/);
    if (parts.length >= 2) {
        let venuePart = parts[1].trim();
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
        
    let position_start = (typeof ccf.SJR_Q !== 'undefined') ? ccf.SJR_Q[url] : undefined;
    let ifData = (typeof ccf.getImpactFactorByName === 'function') ? ccf.getImpactFactorByName(journal3) : null;
    let isLocalHit = (position_start !== undefined) || (ifData && ifData.value);
           
    if (isLocalHit) {
        let doi = "";
        let issn1 = (ifData && ifData.issn) ? ifData.issn : "";
        for (let getRankSpan of scholar.rankSpanList) {
            $(node).after(getRankSpan(journal3, "full_cap", doi, elid, issn1, "", "", "", settings));
        }
        let spinner = document.getElementById(elid);
        if (spinner) spinner.remove();
    } else {
        fetchRank(node, title, compl, scholar, elid, author, journal3, settings);
    }
};


scholar.rankSpanList = [];

scholar_turbo.run = function (settings) {
    let url = window.location.pathname;
    let full_url = window.location.href;
    if (url == "/scholar") {
        scholar_turbo.appendRank(full_url, settings);

        // Dynamic observer for infinite scroll / lazy-loaded results
        let debounceTimer = null;
        const triggerUpdate = function () {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(function () {
                scholar_turbo.appendRank(full_url, settings);
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

        window.addEventListener("scroll", triggerUpdate, { passive: true });

    } else if (url == "/citations") {
        scholar_turbo.appendRanks(settings);
        $("#gsc_bpf_more").click( function() {
            setTimeout( function() {
                 scholar_turbo.appendRanks(settings)
            }, 1000);
        });
    }
};


scholar_turbo.appendRank = function (full_url, settings) {
    let elements = $("#gs_res_ccl_mid > div > div.gs_ri");
    elements.each(async function () {
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

scholar_turbo.appendRanks = function (settings) {
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