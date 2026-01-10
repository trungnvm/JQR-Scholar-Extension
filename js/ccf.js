
/**
 * 03112022
 * MIT License
 *
 * Copyright (c) 2022 Julian R.K. Wichmann building upon
 * Copyright (c) 2025 Trung V.M Nguyen
 *                                            WenyanLiu (https://github.com/WenyanLiu/CCFrank4dblp), Kai Chen (https://github.com/FunClip)
 */

const ccf = {};

// Initialize sfc namespace for Impact Factor data if not already defined
if (typeof sfc === 'undefined') {
    var sfc = {};
}
if (typeof sfc.impactFactors === 'undefined') {
    sfc.impactFactors = {};
}

ccf.getRankInfo = function (refine, type, ISSN1, ISSN2, dblp_venue) {
    let rankInfo = {};
    rankInfo.ranks = [];
    rankInfo.AllRanks = {};
    rankInfo.rank_CORE = "";
    rankInfo.refine_CORE = "";
    rankInfo.only_CORE = 0;
    rankInfo.info = "";
    rankInfo.info2 = "";
    rankInfo.txt = "";
    let rank;
    let hindex;
    let rank_txt;

    refine = refine.replace(/&amp;/g, "&");

    url = refine;
    url = url.toUpperCase();
    url = url.replace(/&AMP;/g, "&");
    url = url.replace(/ AND /g, "");
    url = url.replace(/^THE /g, "");
    url = url.replace(/, THE$/g, "");
    url = url.normalize('NFD');
    url = url.replace(/[^A-Z0-9]/ig, "");
    
    
    if (dblp_venue != undefined && dblp_venue != "") {
        
        dblp_venue = dblp_venue.toUpperCase(); 
        dblp_venue = dblp_venue.replace(/[^A-Z0-9]/ig, "");
    
        let position_start_CORE = ccf.FullRank_Acro.indexOf("X_X" + dblp_venue + "\1/");
       
        if (position_start_CORE == -1) {
            dblp_venue = dblp_venue.replace(/^IEEE/g, ""); 
            position_start_CORE = ccf.FullRank_Acro.indexOf("X_X" + dblp_venue + "\1/");
        }
        
        if (position_start_CORE == -1) {
            dblp_venue = dblp_venue.replace(/^ACM/g, ""); 
            position_start_CORE = ccf.FullRank_Acro.indexOf("X_X" + dblp_venue + "\1/");
        }

        if (position_start_CORE != -1) {
            let sjrq2_pos_s_CORE = ccf.FullRank_Acro.indexOf("\1/", position_start_CORE);
            let sjrq2_pos_e_CORE = ccf.FullRank_Acro.indexOf("\2/", position_start_CORE);
            let sjrq2_CORE = ccf.FullRank_Acro.substring( (sjrq2_pos_s_CORE + 2), sjrq2_pos_e_CORE);
            rankInfo.rank_CORE = sjrq2_CORE; // looks for the V5 rank
            
            sjrq2_pos_s_CORE = ccf.FullRank_Acro.indexOf("\2/", position_start_CORE);
            sjrq2_pos_e_CORE = ccf.FullRank_Acro.indexOf("\3/", position_start_CORE);
            sjrq2_CORE = ccf.FullRank_Acro.substring( (sjrq2_pos_s_CORE + 2), sjrq2_pos_e_CORE);
            rankInfo.refine_CORE = sjrq2_CORE; // looks for the full name of the venue

        } else {
            rankInfo.rank_CORE = "NA";
        }
    } else {
            rankInfo.rank_CORE = "NA";
    }

    if (ISSN1 != undefined && ISSN1 != "") {     
        ISSN1 = ISSN1.toUpperCase();             
        ISSN1 = ISSN1.replace(/[^A-Z0-9]/ig, "");
        issn = ISSN1;    

        // let position_start = ccf.FullRank_ISSNs.indexOf("X_X" + issn + "\1/");
        let position_start = ccf.issnSJR_Q[issn]; // we build the dataset from a csv file so if ANY rating exists there will be at least an entry with NA in all others

        if (ISSN2 != "" && ISSN2 != undefined && position_start === undefined) {
                
            ISSN2 = ISSN2.toUpperCase(); 
            ISSN2 = ISSN2.replace(/[^A-Z0-9]/ig, "");
            issn = ISSN2; 
                
            // position_start = ccf.FullRank_ISSNs.indexOf("X_X" + issn + "\1/");
            position_start = ccf.issnSJR_Q[issn]; 
        }
        if (position_start === undefined && url != "" && url != undefined) {
            position_start = ccf.SJR_Q[url]; // we build the dataset from a csv file so if ANY rating exists there will be at least an entry with NA in all others
            if (position_start !== undefined) { // single undefined check
                sjrq2 = position_start || "NA"; // if the rating is an empty string, we replace it with NA
                rankInfo.AllRanks.SJR_Q2 = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.SJR_Hi[url] || "NA";
                rankInfo.AllRanks.SJR_H = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.VHB[url] || "NA";
                rankInfo.AllRanks.VHB = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.VHB4[url] || "NA";
                rankInfo.AllRanks.VHB4 = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.FNEGE[url] || "NA";
                rankInfo.AllRanks.FNEGE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.CoNRS[url] || "NA";
                rankInfo.AllRanks.CoNRS = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.HCERES[url] || "NA";
                rankInfo.AllRanks.HCERE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.CORE[url] || "NA";
                rankInfo.AllRanks.CORE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.source[url] || "NA";
                rankInfo.AllRanks.CORE_source = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.CORE_c[url] || "NA";
                rankInfo.AllRanks.CORE_Conf = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.CCF[url] || "NA";
                rankInfo.AllRanks.CCF = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = "NA";
                rankInfo.AllRanks.DAEN = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.AJG[url] || "NA";
                rankInfo.AllRanks.AJG = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.JCR[url] || "NA";
                rankInfo.AllRanks.JCR = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.SNIP[url] || "NA";
                rankInfo.AllRanks.SNIP = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.SJR[url] || "NA";
                rankInfo.AllRanks.SJR = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.CiteSc[url] || "NA";
                rankInfo.AllRanks.CiteScore = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.ABDC[url] || "NA";
                rankInfo.AllRanks.ABDC = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.FT50[url] || "NA";
                rankInfo.AllRanks.FT50 = sjrq2;
                rankInfo.ranks.push(sjrq2);

            
            } else {

                rank_txt = "NA";
                rankInfo.info = "No ranking found for '" + refine + "'";
                rankInfo.info2 = "";
            }     

        } else {
 
            if (position_start !== undefined) {                
        
                sjrq2 = position_start || "NA"; // if the rating is an empty string, we replace it with NA
                rankInfo.AllRanks.SJR_Q2 = sjrq2;
                rankInfo.ranks.push(sjrq2);
        
                sjrq2 = ccf.issnSJR_H[issn] || "NA";
                rankInfo.AllRanks.SJR_H = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.issnVHB[issn] || "NA";
                rankInfo.AllRanks.VHB = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnVHB4 && ccf.issnVHB4[issn]) || "NA";
                rankInfo.AllRanks.VHB4 = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnFNEGE && ccf.issnFNEGE[issn]) || "NA";
                rankInfo.AllRanks.FNEGE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnCoNRS && ccf.issnCoNRS[issn]) || "NA";
                rankInfo.AllRanks.CoNRS = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnHCERE && ccf.issnHCERE[issn]) || "NA";
                rankInfo.AllRanks.HCERE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnCORE && ccf.issnCORE[issn]) || "NA";
                rankInfo.AllRanks.CORE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnsourc && ccf.issnsourc[issn]) || (ccf.issnsource && ccf.issnsource[issn]) || "NA";
                rankInfo.AllRanks.CORE_source = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnCORE_c && ccf.issnCORE_c[issn]) || "NA";
                rankInfo.AllRanks.CORE_Conf = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnDAEN && ccf.issnDAEN[issn]) || "NA";
                rankInfo.AllRanks.DAEN = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnAJG && ccf.issnAJG[issn]) || "NA";
                rankInfo.AllRanks.AJG = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnJCR && ccf.issnJCR[issn]) || "NA";
                rankInfo.AllRanks.JCR = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnSNIP && ccf.issnSNIP[issn]) || "NA";
                rankInfo.AllRanks.SNIP = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnSJR && ccf.issnSJR[issn]) || "NA";
                rankInfo.AllRanks.SJR = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnCiteS && ccf.issnCiteS[issn]) || "NA";
                rankInfo.AllRanks.CiteScore = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.issnABDC && ccf.issnABDC[issn]) || "NA";
                rankInfo.AllRanks.ABDC = sjrq2;
                rankInfo.ranks.push(sjrq2);

        
                position_start = (ccf.FT50 && ccf.FT50[url]); // we build the dataset from a csv file so if ANY rating exists there will be at least an entry with NA in all others

                if (position_start !== undefined) {

                    sjrq2 = position_start || "NA"; // if the rating is an empty string, we replace it with NA
                    rankInfo.AllRanks.FT50 = sjrq2;
                    rankInfo.ranks.push(sjrq2);

                    sjrq2 = (ccf.CORE_c && ccf.CORE_c[url]) || (ccf.Core_c && ccf.Core_c[url]) || "NA";
                    rankInfo.AllRanks.CORE_Conf = sjrq2;
                    rankInfo.ranks.push(sjrq2);


                    sjrq2 = (ccf.CCF && ccf.CCF[url]) || "NA";
                    rankInfo.AllRanks.CCF = sjrq2;
                    rankInfo.ranks.push(sjrq2);

                } else {
                    rank = "NA";

                    rankInfo.AllRanks.FT50 = rank;
                    rankInfo.ranks.push(rank);

                    rankInfo.AllRanks.CORE_Conf = rank;
                    rankInfo.ranks.push(rank);

                    rankInfo.AllRanks.CCF = rank;
                    rankInfo.ranks.push(rank);
                }

            }  else {
                rank_txt = "NA";
                rankInfo.info = "No ranking found for '" + refine + "'";
                rankInfo.info2 = "";
            }

        }

    } else if ( (ISSN1 == undefined || ISSN1 == "") && url != "" && url != undefined) {

        let position_start = (ccf.SJR_Q && ccf.SJR_Q[url]);

            if (position_start !== undefined) {

                sjrq2 = position_start || "NA"; // if the rating is an empty string, we replace it with NA
                rankInfo.AllRanks.SJR_Q2 = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.SJR_Hi && ccf.SJR_Hi[url]) || "NA";
                rankInfo.AllRanks.SJR_H = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.VHB && ccf.VHB[url]) || "NA";
                rankInfo.AllRanks.VHB = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.VHB4 && ccf.VHB4[url]) || "NA";
                rankInfo.AllRanks.VHB4 = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.FNEGE && ccf.FNEGE[url]) || "NA";
                rankInfo.AllRanks.FNEGE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.CoNRS && ccf.CoNRS[url]) || "NA";
                rankInfo.AllRanks.CoNRS = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.HCERES && ccf.HCERES[url]) || "NA";
                rankInfo.AllRanks.HCERE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.CORE && ccf.CORE[url]) || "NA";
                rankInfo.AllRanks.CORE = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.source && ccf.source[url]) || "NA";
                rankInfo.AllRanks.CORE_source = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.CORE_c && ccf.CORE_c[url]) || (ccf.Core_c && ccf.Core_c[url]) || "NA";
                rankInfo.AllRanks.CORE_Conf = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = (ccf.CCF && ccf.CCF[url]) || "NA";
                rankInfo.AllRanks.CCF = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = "NA";
                rankInfo.AllRanks.DAEN = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.AJG[url] || "NA";
                rankInfo.AllRanks.AJG = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.JCR[url] || "NA";
                rankInfo.AllRanks.JCR = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.SNIP[url] || "NA";
                rankInfo.AllRanks.SNIP = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.SJR[url] || "NA";
                rankInfo.AllRanks.SJR = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.CiteSc[url] || "NA";
                rankInfo.AllRanks.CiteScore = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.ABDC[url] || "NA";
                rankInfo.AllRanks.ABDC = sjrq2;
                rankInfo.ranks.push(sjrq2);

                sjrq2 = ccf.FT50[url] || "NA";
                rankInfo.AllRanks.FT50 = sjrq2;
                rankInfo.ranks.push(sjrq2);
    
            } else {
                rank_txt = "NA";
                rankInfo.info = "No ranking found for '" + refine + "'";
                rankInfo.info2 = "";
            }       

    }  
    
    if (rankInfo.rank_CORE != "NA" && rankInfo.rank_CORE != undefined) {
        if ( (refine == "" && ISSN1 == "") || (Object.keys(rankInfo.AllRanks).length === 0  && rankInfo.AllRanks.constructor === Object) ) {
            rankInfo.only_CORE = 1; 
        }
// JW 28112022 //        
        if ( rankInfo.AllRanks.CORE_Conf == "NA" || rankInfo.AllRanks.CORE_Conf == undefined) { 
        
        rank = rankInfo.rank_CORE;
        rankInfo.AllRanks.CORE_Conf = rank;
        rankInfo.ranks.push(rank);
        
        }

    }
    
    if (refine == "" && ISSN1 == "" && (rankInfo.rank_CORE == "NA"  || rankInfo.rank_CORE == undefined) ) {
        rank_txt = "NA";
        rankInfo.info = "No journal identifiable";
        rankInfo.info2 = "";
    }
    
    if (refine == "" && ISSN1 == "" && rankInfo.rank_CORE != "NA"  && rankInfo.rank_CORE != undefined) {
        rank_txt = rankInfo.rank_CORE;
        rankInfo.info = refine;
        rankInfo.info += "; H-Index: NA";
        rankInfo.info2 = "";
    }
            
    if ( Object.keys(rankInfo.AllRanks).length !== 0 && rankInfo.AllRanks.constructor === Object ) { 
      if(rankInfo.AllRanks.SJR_H !== undefined) {
        hindex = rankInfo.AllRanks.SJR_H;
        rankInfo.info = refine;
        rankInfo.info += "; H-Index: " + hindex;
      } else {
        rankInfo.info = refine;
        rankInfo.info += "; H-Index: NA";
      }    
    }
    
    return rankInfo;
};


ccf.getRankClass = function (ranks) {
    quarts = ["Q1", "Q2", "Q3", "Q4", "A", "B", "C", "D", "I", "II", "III"]
    if(ranks == "A+") {
        return "ccf-Aplus";
    } else if (ranks == "A/B") {
        return "ccf-b";
    } else if (ranks == "B/C") {
        return "ccf-c"; 
    } else if (ranks == "C/D") {
        return "ccf-d";    
    } else {
        for (let rank of quarts) {
            for (let r of ranks) {
                if (r == rank) {
                    return "ccf-" + rank.toLowerCase();
                }
            }
        }
    }        
    return "ccf-none";
};



/**
 * Clean journal name using same logic as Python script
 * Matches reference extension's matching logic exactly.
 * @param {string} str - Journal name
 * @returns {string} Cleaned journal name
 */
ccf.cleanName = function (str) {
    if (!str) return "";
    return str.toLowerCase()
        .replace(/&/g, 'and')
        .replace(/[-–—]/g, ' ')
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9\s]/g, '')
        .replace(/\s+/g, ' ')
        .trim();
};


/**
 * Get Impact Factor data by journal name
 * @param {string} name - Journal name
 * @returns {object|null} Impact Factor data object or null if not found
 */
ccf.getImpactFactorByName = function (name) {
    if (!sfc || !sfc.impactFactorsNames) {
        return null;
    }
    let cleanedName = ccf.cleanName(name);
    return sfc.impactFactorsNames[cleanedName] || null;
};


/**
 * Get Impact Factor data for a given ISSN
 * @param {string} ISSN1 - Primary ISSN
 * @param {string} ISSN2 - Secondary ISSN (optional)
 * @returns {object|null} Impact Factor data object or null if not found
 */
ccf.getImpactFactor = function (ISSN1, ISSN2) {
    if (!sfc || !sfc.impactFactors) {
        console.log("CCF Debug: sfc or sfc.impactFactors is undefined");
        return null;
    }

    let ifData = null;

    // Try primary ISSN
    if (ISSN1 && ISSN1 !== "") {
        let cleanISSN1 = ISSN1.toUpperCase().replace(/[^A-Z0-9]/ig, "");
        ifData = sfc.impactFactors[cleanISSN1];
        console.log("CCF Debug: Looking up IF for ISSN1:", cleanISSN1, "Result:", ifData);
    }

    // Try secondary ISSN if primary not found
    if (!ifData && ISSN2 && ISSN2 !== "") {
        let cleanISSN2 = ISSN2.toUpperCase().replace(/[^A-Z0-9]/ig, "");
        ifData = sfc.impactFactors[cleanISSN2];
        console.log("CCF Debug: Looking up IF for ISSN2:", cleanISSN2, "Result:", ifData);
    }

    return ifData;
};


/**
 * Get color class for Impact Factor badge based on IF data
 * @param {object} ifData - Impact Factor data object
 * @returns {string} CSS class name for color coding
 */
ccf.getIFColorClass = function (ifData) {
    if (ifData && ifData.quartile) {
        const q = ifData.quartile.toUpperCase();
        if (q.includes("Q1")) return "if-q1";
        if (q.includes("Q2")) return "if-q2";
        if (q.includes("Q3")) return "if-q3";
        if (q.includes("Q4")) return "if-q4";
    }

    let ifValue = parseFloat(ifData.value);
    if (ifValue >= 10) {
        return "if-excellent";  // Green
    } else if (ifValue >= 3) {
        return "if-verygood";   // Light green
    } else if (ifValue >= 1) {
        return "if-good";       // Yellow
    } else {
        return "if-low";        // Red
    }
};


/**
 * Create Impact Factor badge span element
 * @param {object} ifData - Impact Factor data object
 * @returns {jQuery} Span element with IF badge
 */
ccf.getIFSpan = function (ifData) {
    if (!ifData || !ifData.value) {
        return $("<span>");  // Return empty span if no data
    }

    let ifValue = parseFloat(ifData.value);
    let colorClass = ccf.getIFColorClass(ifData);

    let tooltipText = "Impact Factor: " + ifValue;
    if (ifData.year) {
        tooltipText += "\nYear: " + ifData.year;
    }
    if (ifData.source) {
        tooltipText += "\nSource: " + ifData.source;
    }
    if (ifData.quartile) {
        tooltipText += "\nQuartile: " + ifData.quartile;
    }
    if (ifData.h_index) {
        tooltipText += "\nH-Index: " + ifData.h_index;
    }

    let span = $("<span>")
        .addClass("ccf-rank if-badge")
        .addClass(colorClass)
        .text("IF: " + ifValue.toFixed(1))
        .addClass("ccf-tooltip")
        .append($("<pre>").addClass("ccf-tooltiptext").text(tooltipText));

    return span;
};


function loadSettings() {
    return new Promise(function(resolve, reject) {
        browserAPI.storage.local.get(function(items) {
            resolve(items);
         })
    });
};

ccf.getRankSpan = function (refine, type, doi, elid, ISSN1, ISSN2, dblp_venue, dblp_doi, settings) {

    // Safety check for settings
    settings = settings || {};

    // Pre-clean name by removing parentheses, years, and commas
    if (refine) {
        refine = refine.replace(/\([^)]*\)/g, '').replace(/[0-9]{1,4}/g, '').replace(/[,]/g, '').trim();
    }

    let allNA = 1;
 
    let rankInfo = ccf.getRankInfo(refine, type, ISSN1, ISSN2, dblp_venue);
 
    let span1 = $("<span>");
    let rank = rankInfo.AllRanks.SJR_Q2;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span1
            .addClass("ccf-rank")
            .addClass("SJR_Q2_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    }      
    
    let span2 = $("<span>");
    rank = rankInfo.AllRanks.VHB;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span2
            .addClass("ccf-rank")
            .addClass("VHB3_" + rank.replace(/[+*/]/g, "plus").toLowerCase() )
            .text(rank); 
    }

    let span3 = $("<span>");
    rank = rankInfo.AllRanks.VHB4;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span3
            .addClass("ccf-rank")
            .addClass("VHB4_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank);
    }
    
    let span4 = $("<span>");
    rank = rankInfo.AllRanks.FNEGE;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span4
            .addClass("ccf-rank")
            .addClass("FNEGE_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
        
    let span5 = $("<span>");
    rank = rankInfo.AllRanks.CoNRS;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span5
            .addClass("ccf-rank")
            .addClass("CoNRS_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
    
    let span6 = $("<span>");
    rank = rankInfo.AllRanks.HCERE;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span6
            .addClass("ccf-rank")
            .addClass("HCERE_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
    
    let span7 = $("<span>");
    rank = rankInfo.AllRanks.CORE;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span7
            .addClass("ccf-rank")
            .addClass("CORE_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
    
    let span8 = $("<span>");
    rank = rankInfo.AllRanks.CORE_Conf;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span8
            .addClass("ccf-rank")
            .addClass("CORE_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
    
    let span9 = $("<span>");
    rank = rankInfo.AllRanks.CCF;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span9
            .addClass("ccf-rank")
            .addClass("CCF_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
    
    let span10 = $("<span>");
    rank = rankInfo.AllRanks.DAEN;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span10
            .addClass("ccf-rank")
            .addClass("DAEN_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
    
    let span11 = $("<span>");
    rank = rankInfo.AllRanks.AJG;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span11
            .addClass("ccf-rank")
            .addClass("AJG_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
        
    let span12 = $("<span>");
    rank = rankInfo.AllRanks.ABDC;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span12
            .addClass("ccf-rank")
            .addClass("ABDC_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank); 
    } 
    
    let span13 = $("<span>");
    rank = rankInfo.AllRanks.FT50;
    if (rank != "NA" && rank != undefined) {
        allNA = allNA + 1;
        span13
            .addClass("ccf-rank")
            .addClass("FT50_" + rank.replace(/[+*]/g, "plus").toLowerCase() )
            .text(rank);
    }

    // Impact Factor badge
    let span14 = $("<span>");
    let ifData = ccf.getImpactFactor(ISSN1, ISSN2);
    if (!ifData || !ifData.value) {
        ifData = ccf.getImpactFactorByName(refine);
    }
    if (ifData && ifData.value) {
        allNA = allNA + 1;
        span14 = ccf.getIFSpan(ifData);
    }


    let elid_er = elid + "_expandrank";
    let elid_ar = elid + "_addrank";
            
    let span123 = $("<span>")
        .addClass("ccf-rank");
    
    let span456 = $("<span style='display:none'>")
        .attr("id", elid_ar)
        .addClass("ccf-rank");

    if (settings.autoExpand !== false) {
        span456.css("display", "");
    }
        
    let popup_text = "" + rankInfo.info + "\n";

    let popup_text_add = "" + rankInfo.info + "\n";
    

    let Ranks_chosen = [];
    let Ranks_additional = [];
    
      if(settings.SJR === true) { 
          span123.append(span1); 
          popup_text += "SJR: " + rankInfo.AllRanks.SJR_Q2 + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.SJR_Q2); 
        } else { 
          span456.append(span1); 
          popup_text_add += "SJR: " + rankInfo.AllRanks.SJR_Q2 + "   ";
          Ranks_additional.push(rankInfo.AllRanks.SJR_Q2); 
        }

      if(settings.VHB === true) { 
          span123.append(span2); 
          popup_text += "VHB3: " + rankInfo.AllRanks.VHB + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.VHB); 
        } else { 
          span456.append(span2); 
          popup_text_add += "VHB3: " + rankInfo.AllRanks.VHB + "   ";
          Ranks_additional.push(rankInfo.AllRanks.VHB); 
        }

      if(settings.VHB4 === true) {
          span123.append(span3);
          popup_text += "VHB4: " + rankInfo.AllRanks.VHB4 + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.VHB4);
        } else {
          span456.append(span3);
          popup_text_add += "VHB4: " + rankInfo.AllRanks.VHB4 + "   ";
          Ranks_additional.push(rankInfo.AllRanks.VHB4);
        }
    
      if(settings.FNEGE === true) { 
          span123.append(span4); 
          popup_text += "FNEGE: " + rankInfo.AllRanks.FNEGE + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.FNEGE); 
      } else { 
          span456.append(span4); 
          popup_text_add += "FNEGE: " + rankInfo.AllRanks.FNEGE + "   ";
          Ranks_additional.push(rankInfo.AllRanks.FNEGE); 
        }

      if(settings.CoNRS === true) { 
          span123.append(span5);
          popup_text += "CoNRS: " + rankInfo.AllRanks.CoNRS + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.CoNRS); 
      } else { 
          span456.append(span5); 
          popup_text_add += "CoNRS: " + rankInfo.AllRanks.CoNRS + "   ";
          Ranks_additional.push(rankInfo.AllRanks.CoNRS); 
        }

      if(settings.HCERE === true) {  
          span123.append(span6);
          popup_text += "HCERE: " + rankInfo.AllRanks.HCERE + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.HCERE); 
      } else { 
          span456.append(span6); 
          popup_text_add += "HCERE: " + rankInfo.AllRanks.HCERE + "   ";
          Ranks_additional.push(rankInfo.AllRanks.HCERE); 
        }
    
    
    let show_only_CORE = 0;
    let show_only_CORE_add = 0;
      if(settings.CORE === true) { 
          span123.append(span7);
          span123.append(span8);
          if(rankInfo.AllRanks.CORE != "NA") { popup_text += "CORE (Jour.): " + rankInfo.AllRanks.CORE + "   "; }
          if(rankInfo.AllRanks.CORE_Conf != "NA") { popup_text += "CORE (Conf.): " + rankInfo.AllRanks.CORE_Conf + " "; }
          if(rankInfo.AllRanks.CORE_Conf == "NA" && rankInfo.AllRanks.CORE == "NA") { popup_text += "CORE: " + rankInfo.AllRanks.CORE_Conf + "   "; }
          if(rankInfo.only_CORE == 1) { 
              popup_text_CORE = rankInfo.refine_CORE + "; H-Index: NA " + "\n" + "CORE (Conf.): " + rankInfo.rank_CORE;
              show_only_CORE = 1; 
          } 
          Ranks_chosen.push(rankInfo.AllRanks.CORE);
          Ranks_chosen.push(rankInfo.AllRanks.CORE_Conf);    
       } else { 
          span456.append(span7);
          span456.append(span8);
          if(rankInfo.AllRanks.CORE != "NA") { popup_text_add += "CORE (Jour.): " + rankInfo.AllRanks.CORE + "   "; }
          if(rankInfo.AllRanks.CORE_Conf != "NA") { popup_text_add += "CORE (Conf.): " + rankInfo.AllRanks.CORE_Conf + " "; }
          if(rankInfo.AllRanks.CORE_Conf == "NA" && rankInfo.AllRanks.CORE == "NA") { popup_text_add += "CORE: " + rankInfo.AllRanks.CORE_Conf + "   "; }
          if(rankInfo.only_CORE == 1) { 
              popup_text_CORE_add = rankInfo.refine_CORE + "; H-Index: NA " + "\n" + "CORE (Conf.): " + rankInfo.rank_CORE;
              show_only_CORE_add = 1; 
          }
          Ranks_additional.push(rankInfo.AllRanks.CORE);
          Ranks_additional.push(rankInfo.AllRanks.CORE_Conf);   
       }
    
      if(settings.CCF === true) { 
          span123.append(span9);
          popup_text += "CCF: " + rankInfo.AllRanks.CCF + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.CCF); 
       } else { 
          span456.append(span9); 
          popup_text_add += "CCF: " + rankInfo.AllRanks.CCF + "   ";
          Ranks_additional.push(rankInfo.AllRanks.CCF); 
        }

      if(settings.DAEN === true) { 
          span123.append(span10); 
          popup_text += "BFI: " + rankInfo.AllRanks.DAEN + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.DAEN); 
      } else { 
          span456.append(span10); 
          popup_text_add += "BFI: " + rankInfo.AllRanks.DAEN + "   ";
          Ranks_additional.push(rankInfo.AllRanks.DAEN); 
        }

      if(settings.AJG === true) { 
          span123.append(span11);
          popup_text += "AJG: " + rankInfo.AllRanks.AJG + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.AJG); 
       } else { 
          span456.append(span11); 
          popup_text_add += "AJG: " + rankInfo.AllRanks.AJG + "   ";
          Ranks_additional.push(rankInfo.AllRanks.AJG); 
        }

      if(settings.ABDC === true) { 
          span123.append(span12);
          popup_text += "ABDC: " + rankInfo.AllRanks.ABDC + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.ABDC); 
       } else { 
          span456.append(span12); 
          popup_text_add += "ABDC: " + rankInfo.AllRanks.ABDC + "   ";
          Ranks_additional.push(rankInfo.AllRanks.ABDC); 
        }
    
      if(settings.FT50 === true) {
          span123.append(span13);
          popup_text += "FT50: " + rankInfo.AllRanks.FT50 + "   ";
          Ranks_chosen.push(rankInfo.AllRanks.FT50);
       } else {
          span456.append(span13);
          popup_text_add += "FT50: " + rankInfo.AllRanks.FT50 + "   ";
          Ranks_additional.push(rankInfo.AllRanks.FT50);
        }

      // Impact Factor setting check (default enabled if not specified)
      if(settings.impactFactor !== false) {
          span123.append(span14);
          if (ifData && ifData.value) {
              popup_text += "IF: " + ifData.value + "   ";
              Ranks_chosen.push(ifData.value.toString());
          }
       } else {
          span456.append(span14);
          if (ifData && ifData.value) {
              popup_text_add += "IF: " + ifData.value + "   ";
              Ranks_additional.push(ifData.value.toString());
          }
        }

let chosen = 0;
let additional = 0;


    const isundef = (currentValue) => (currentValue === undefined || currentValue === "" || currentValue === "NA");
   
    if ( (!Ranks_chosen.every(isundef)) ) {   
        
        chosen = 1;

        if(show_only_CORE == 0) {
            span123
                .addClass("ccf-tooltip")
                .append($("<pre>").addClass("ccf-tooltiptext").text(popup_text));        
        } else {
            span123
                .addClass("ccf-tooltip")
                .append($("<pre>").addClass("ccf-tooltiptext").text(popup_text_CORE));   
        }
    } else if ( (refine == "" && ISSN1 == "") || (Ranks_chosen.every(isundef)) ) {
        
        chosen = 0;

        span123 = $("<span>")
            .addClass("ccf-rank")
            .text("NA")
            .addClass("ccf-none")
            .addClass("ccf-tooltip")
            .append($("<pre>").addClass("ccf-tooltiptext").text(rankInfo.info));       
    } 

    if  ( (!Ranks_additional.every(isundef)) ) {   
        
        additional = 1;
 
        if(show_only_CORE_add == 0) {
           span456  
                .addClass("ccf-tooltip")
                .append($("<pre>").addClass("ccf-tooltiptext").text(popup_text_add));
         } else {
           span456  
                .addClass("ccf-tooltip")
                .append($("<pre>").addClass("ccf-tooltiptext").text(popup_text_CORE_add));    
        }
    } else if ( (Ranks_additional.every(isundef)) ) {   
        
        additional = 0;

        span456 = $("<span id='add_rank'>")
            .addClass("ccf-rank")
            .addClass("ccf-none") 
            .text("NA")
            .addClass("ccf-tooltip")
            .append($("<pre>").addClass("ccf-tooltiptext").text(rankInfo.info)); 
    }   
    
    link_text = "https://doi.org/" + doi; 
    
    expand_rank = $("<span title='Click to see additional rankings' style='margin:0 auto'>")
        .attr("id", elid_er)
        .addClass("ccf-rank closed")
        .text("+")
        .on("click", function(){ $(document.getElementById(elid_ar)).toggle({direction: "right"},3000); $(document.getElementById(elid_er)).toggleClass( "open closed" ); if ($(this).hasClass("open")) { $(this).text("-"); } else { $(this).text("+"); } });

    if (settings.autoExpand !== false) {
        expand_rank.removeClass("closed").addClass("open").text("-");
    }   
    
    if(doi != "") { 
        span_link = $('<a href="" target="_blank">')
            .attr("href", link_text)
            .append(span123);
            
        if(additional === 1) {
            span_link
                .append(span456);
        }
        
        span_span_link = $('<span>')
            .append(span_link);
   
    } else if (rankInfo.rank_CORE != "NA" && rankInfo.rank_CORE != undefined && show_only_CORE == 1) {
        span_link = $('<a href="" target="_blank">')
            .attr("href", "https://doi.org/" + dblp_doi)
            .append(span123);
            
        if(additional === 1) {
            span_link
                .append(span456);
        }   

        span_span_link = $('<span>')
            .append(span_link);
 
    }

    if(doi != "") { 
        span = span_span_link;
        if(additional === 1) {
            span
                .append(expand_rank);
        }
    } else if(doi === "" || doi === undefined) { 
        span = $('<span>')
            .append(span123)
        if(additional === 1) {
        span
            .append(span456)
            .append(expand_rank);
        }
    } else if (rankInfo.rank_CORE != "NA" && rankInfo.rank_CORE != undefined && show_only_CORE == 1) {
        span = span_span_link;
        if(additional === 1) {
            span
                .append(span456)
                .append(expand_rank);
        }    
    } else {
        span = $('<span>')
            .append(span123);
        
        if(additional === 1) {
            span
                .append(span456)
                .append(expand_rank);
        }     
    } 
        
    document.getElementById(elid).remove();
    return span; 
    
};
