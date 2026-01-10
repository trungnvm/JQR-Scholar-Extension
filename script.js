// Cross-browser compatibility wrapper
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

scholar.rankSpanList.push(ccf.getRankSpan);

function loadSettings() {
    return new Promise(function(resolve, reject) {
        browserAPI.storage.local.get(function(items) {
            resolve(items);
         })
    });
};

let settings = {};
loadSettings().then(function(items) {

    settings.SJR = items.SJR;
    settings.VHB = items.VHB;
    settings.VHB4 = items.VHB4;
    settings.FNEGE = items.FNEGE;
    settings.CoNRS = items.CoNRS;
    settings.HCERE = items.HCERE;
    settings.CORE = items.CORE;
    settings.CCF = items.CCF;
    settings.DAEN = items.DAEN;
    settings.AJG = items.AJG;
    settings.ABDC = items.ABDC;
    settings.FT50 = items.FT50;
    settings.turbo = items.turbo;
    settings.ext_on = items.ext_on;
    settings.fieldClassification = items.fieldClassification ?? true;
    settings.impactFactor = items.impactFactor ?? true;

    if(settings.ext_on === true) {
        if(settings.turbo === true) {
                scholar_turbo.run(settings);
        } else {
                scholar.run(settings);
        }
    }
});
