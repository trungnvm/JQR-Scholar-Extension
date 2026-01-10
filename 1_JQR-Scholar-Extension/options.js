// Cross-browser compatibility wrapper
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

// List of all checkbox IDs
const checkboxIds = [
    'on', 'turbo', 'fieldClassification', 'impactFactor', 'autoExpand',
    'ABDC', 'AJG', 'DAEN', 'CCF', 'CoNRS', 'CORE', 'FNEGE', 'FT50', 'HCERE', 'SJR', 'VHB', 'VHB4'
];

// List of ranking checkboxes (a subset of checkboxIds)
const rankingIds = [
    'ABDC', 'AJG', 'DAEN', 'CCF', 'CoNRS', 'CORE', 'FNEGE', 'FT50', 'HCERE', 'SJR', 'VHB', 'VHB4'
];

/**
 * Saves options to storage
 */
function save_options() {
    browserAPI.storage.local.get(null, function(items) {
        const newSettings = { ...items };

        // Save standard checkboxes
        checkboxIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                // Map 'on' to 'ext_on'
                const key = (id === 'on') ? 'ext_on' : id;
                newSettings[key] = element.checked;
            }
        });

        // Save 'Enable All' state (not used by extension logic, but good for UI consistency)
        const enableAllEl = document.getElementById('enableAll');
        if (enableAllEl) {
            newSettings['enableAll'] = enableAllEl.checked;
        }

        browserAPI.storage.local.set(newSettings, function() {
            if (newSettings.ext_on === false) {
                if (browserAPI.action && browserAPI.action.setBadgeText) {
                    browserAPI.action.setBadgeText({ text: 'OFF' });
                } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                    browserAPI.browserAction.setBadgeText({ text: 'OFF' });
                }
            } else {
                if (browserAPI.action && browserAPI.action.setBadgeText) {
                    browserAPI.action.setBadgeText({ text: '' });
                } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                    browserAPI.browserAction.setBadgeText({ text: '' });
                }
            }
        });
    });
}

/**
 * Restores state using the preferences stored in storage
 */
function restore_options() {
    // Default values
    const defaults = {
        ext_on: true,
        turbo: true,
        fieldClassification: true,
        impactFactor: true,
        autoExpand: true,
        ABDC: true,
        AJG: true,
        DAEN: true,
        CCF: true,
        CoNRS: true,
        CORE: true,
        FNEGE: true,
        FT50: true,
        HCERE: true,
        SJR: true,
        VHB: true,
        VHB4: true
    };

    browserAPI.storage.local.get(defaults, function(items) {
        checkboxIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                // Map 'on' to 'ext_on'
                const key = (id === 'on') ? 'ext_on' : id;
                if (items[key] !== undefined) {
                    element.checked = items[key];
                }
            }
        });

        // Restore 'Enable All' toggle
        const enableAllEl = document.getElementById('enableAll');
        if (enableAllEl && items['enableAll'] !== undefined) {
            enableAllEl.checked = items['enableAll'];
        }

        // Update badge initially too
        if (items.ext_on === false) {
             if (browserAPI.action && browserAPI.action.setBadgeText) {
                browserAPI.action.setBadgeText({ text: 'OFF' });
            } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                browserAPI.browserAction.setBadgeText({ text: 'OFF' });
            }
        } else {
             if (browserAPI.action && browserAPI.action.setBadgeText) {
                browserAPI.action.setBadgeText({ text: '' });
            } else if (browserAPI.browserAction && browserAPI.browserAction.setBadgeText) {
                browserAPI.browserAction.setBadgeText({ text: '' });
            }
        }
    });
}

// Add event listeners
document.addEventListener('DOMContentLoaded', restore_options);
checkboxIds.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        element.addEventListener('change', () => {
            // If any ranking checkbox is unchecked manually, uncheck "Enable All"
            if (rankingIds.includes(id) && !element.checked) {
                const enableAllEl = document.getElementById('enableAll');
                if (enableAllEl) enableAllEl.checked = false;
            }
            save_options();
        });
    }
});

// "Enable All" logic
const enableAllEl = document.getElementById('enableAll');
if (enableAllEl) {
    enableAllEl.addEventListener('change', function() {
        const isChecked = this.checked;
        rankingIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.checked = isChecked;
            }
        });
        save_options();
    });
}

/* ############# Journal Search Function ############# */

function toUnicodeVariant(str, variant, flags) {
    const offsets = {
        m: [0x1d670, 0x1d7f6],
        b: [0x1d400, 0x1d7ce],
        i: [0x1d434, 0x00030],
        bi: [0x1d468, 0x00030],
        c: [0x1d49c, 0x00030],
        bc: [0x1d4d0, 0x00030],
        g: [0x1d504, 0x00030],
        d: [0x1d538, 0x1d7d8],
        bg: [0x1d56c, 0x00030],
        s: [0x1d5a0, 0x1d7e2],
        bs: [0x1d5d4, 0x1d7ec],
        is: [0x1d608, 0x00030],
        bis: [0x1d63c, 0x00030],
        o: [0x24B6, 0x2460],
        p: [0x249C, 0x2474],
        w: [0xff21, 0xff10],
        u: [0x2090, 0xff10]
    }

    const variantOffsets = {
        'monospace': 'm',
        'bold': 'b',
        'italic': 'i',
        'bold italic': 'bi',
        'script': 'c',
        'bold script': 'bc',
        'gothic': 'g',
        'gothic bold': 'bg',
        'doublestruck': 'd',
        'sans': 's',
        'bold sans': 'bs',
        'italic sans': 'is',
        'bold italic sans': 'bis',
        'parenthesis': 'p',
        'circled': 'o',
        'fullwidth': 'w'
    }

    var special = {
        m: { ' ': 0x2000, '-': 0x2013 },
        i: { 'h': 0x210e },
        g: { 'C': 0x212d, 'H': 0x210c, 'I': 0x2111, 'R': 0x211c, 'Z': 0x2128 },
        o: { '0': 0x24EA, '1': 0x2460, '2': 0x2461, '3': 0x2462, '4': 0x2463, '5': 0x2464, '6': 0x2465, '7': 0x2466, '8': 0x2467, '9': 0x2468 },
        p: {}, w: {}
    }
    for (var i = 97; i <= 122; i++) { special.p[String.fromCharCode(i)] = 0x249C + (i - 97) }
    for (var i = 97; i <= 122; i++) { special.w[String.fromCharCode(i)] = 0xff41 + (i - 97) }

    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';

    var getType = function (variant) {
        if (variantOffsets[variant]) return variantOffsets[variant]
        if (offsets[variant]) return variant;
        return 'm';
    }
    var getFlag = function (flag, flags) {
        if (!flags) return false
        return flags.split(',').indexOf(flag) > -1
    }

    var type = getType(variant);
    var underline = getFlag('underline', flags);
    var strike = getFlag('strike', flags);
    var result = '';

    for (var k of str) {
        let index
        let c = k
        if (special[type] && special[type][c]) c = String.fromCodePoint(special[type][c])
        if (type && (index = chars.indexOf(c)) > -1) {
            result += String.fromCodePoint(index + offsets[type][0])
        } else if (type && (index = numbers.indexOf(c)) > -1) {
            result += String.fromCodePoint(index + offsets[type][1])
        } else {
            result += c
        }
        if (underline) result += '\u0332'
        if (strike) result += '\u0336'
    }
    return result
}

function joursearch_func() {
    const input = document.getElementById("journal_query").value;
    if (!input) return;

    let query = input.toUpperCase();
    query = query.replace(/&AMP;/g, "&");
    query = query.replace(/ AND /g, "");
    query = query.replace(/^THE /g, "");
    query = query.replace(/, THE$/g, "");
    query = query.normalize('NFD');
    query = query.replace(/[^A-Z0-9]/ig, "");

    browserAPI.storage.local.get(null, function(settings) {
        browserAPI.runtime.sendMessage({
            action: "searchJournal",
            query: query,
            settings: settings
        }, function(response) {
            if (response && response.found) {
                displayResults(input, response.results);
            } else {
                alert("Journal not found, please check the spelling.");
            }
        });
    });
}

function displayResults(input, results) {
    let text2 = "";
    let i = 0;
    while (i < 14 && results[i] !== undefined) {
        text2 += results[i].name + ": " + toUnicodeVariant(results[i].value, 'bold') + ";       "
        i++;
    }
    alert(toUnicodeVariant(input, 'bold italic') + ": \n" + text2);
}

const searchForm = document.getElementById("joursearch_form");
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        joursearch_func();
    });
}
